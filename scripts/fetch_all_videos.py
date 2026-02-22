#!/usr/bin/env python3
"""
YouTube全動画メタデータ一括取得スクリプト

対象チャンネル: 胡田昌彦 / Windows, Azure, M365, 生成AI (UCn_7IV61pGOfoiC5Lc8nHUw)
出力: ../data/videos.json, ../data/playlists.json

既存の obsidian/scripts/youtube_scraper.py のOAuth認証を再利用する。
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CHANNEL_ID = "UCn_7IV61pGOfoiC5Lc8nHUw"
OBSIDIAN_SCRIPTS = Path("/home/ebi/obsidian/scripts")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OBSIDIAN_VIDEOS_DIR = Path("/home/ebi/obsidian/05_Resources/YouTube動画")

OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def get_youtube_service():
    """OAuth認証でYouTubeサービスを取得（既存トークン再利用）"""
    token_file = OBSIDIAN_SCRIPTS / "token.json"
    credentials = Credentials.from_authorized_user_file(str(token_file), OAUTH_SCOPES)

    if credentials.refresh_token:
        credentials.refresh(Request())
        with open(token_file, "w") as f:
            f.write(credentials.to_json())

    return build("youtube", "v3", credentials=credentials)


def get_api_key_service():
    """APIキー認証のサービス（再生数等の統計取得用）"""
    # .envからAPIキーを読み込む
    env_file = OBSIDIAN_SCRIPTS / ".env"
    api_key = None
    for line in env_file.read_text().splitlines():
        if line.startswith("YOUTUBE_API_KEY="):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not found in .env")
    return build("youtube", "v3", developerKey=api_key)


def parse_duration(iso_duration: str) -> int:
    """ISO 8601 duration (PT1H2M3S) を秒数に変換"""
    if not iso_duration:
        return 0
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
    if not match:
        return 0
    h, m, s = (int(g) if g else 0 for g in match.groups())
    return h * 3600 + m * 60 + s


def format_duration(seconds: int) -> str:
    """秒数を HH:MM:SS or MM:SS に変換"""
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fetch_all_video_ids(yt_oauth) -> list[dict]:
    """OAuth認証で全動画の基本情報を取得（アップロードプレイリスト経由）"""
    # チャンネルのアップロードプレイリストID取得
    ch_resp = yt_oauth.channels().list(
        part="contentDetails,snippet", id=CHANNEL_ID
    ).execute()

    if not ch_resp.get("items"):
        raise ValueError(f"Channel not found: {CHANNEL_ID}")

    channel = ch_resp["items"][0]
    uploads_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    print(f"📺 チャンネル: {channel['snippet']['title']}")
    print(f"📋 アップロードPL: {uploads_id}")

    videos = []
    next_token = None
    while True:
        resp = yt_oauth.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_token,
        ).execute()

        for item in resp.get("items", []):
            vid = item["contentDetails"].get("videoId")
            if not vid:
                continue
            snip = item["snippet"]
            # 他チャンネルの動画をスキップ
            owner_id = snip.get("videoOwnerChannelId", "")
            if owner_id and owner_id != CHANNEL_ID:
                continue

            thumbnails = snip.get("thumbnails", {})
            thumb = (
                thumbnails.get("high", {}).get("url")
                or thumbnails.get("medium", {}).get("url")
                or thumbnails.get("default", {}).get("url", "")
            )

            videos.append({
                "videoId": vid,
                "title": snip.get("title", ""),
                "description": snip.get("description", ""),
                "publishedAt": snip.get("publishedAt", ""),
                "thumbnailUrl": thumb,
            })

        next_token = resp.get("nextPageToken")
        if not next_token:
            break
        print(f"  取得中... {len(videos)}本")

    print(f"✅ 全{len(videos)}本の動画IDを取得")
    return videos


def enrich_with_statistics(yt_api, videos: list[dict]) -> list[dict]:
    """APIキー認証で再生数・いいね数・再生時間等を追加取得（50件ずつバッチ）"""
    print("📊 統計情報を取得中...")
    for i in range(0, len(videos), 50):
        batch = videos[i : i + 50]
        ids = ",".join(v["videoId"] for v in batch)
        resp = yt_api.videos().list(
            part="statistics,contentDetails,status", id=ids
        ).execute()

        stats_map = {}
        for item in resp.get("items", []):
            stats_map[item["id"]] = item

        for v in batch:
            detail = stats_map.get(v["videoId"])
            if not detail:
                v["viewCount"] = 0
                v["likeCount"] = 0
                v["durationSeconds"] = 0
                v["duration"] = "0:00"
                v["privacyStatus"] = "unknown"
                v["tags"] = []
                continue

            stats = detail.get("statistics", {})
            content = detail.get("contentDetails", {})
            status = detail.get("status", {})

            dur_sec = parse_duration(content.get("duration", ""))
            v["viewCount"] = int(stats.get("viewCount", 0))
            v["likeCount"] = int(stats.get("likeCount", 0))
            v["durationSeconds"] = dur_sec
            v["duration"] = format_duration(dur_sec)
            v["privacyStatus"] = status.get("privacyStatus", "unknown")
            v["tags"] = detail.get("snippet", {}).get("tags", [])

        print(f"  {min(i + 50, len(videos))}/{len(videos)}")

    return videos


def fetch_all_playlists(yt_api) -> list[dict]:
    """全プレイリストのメタデータ + 所属動画IDを取得"""
    print("\n📋 プレイリスト情報を取得中...")
    playlists = []
    next_token = None

    while True:
        resp = yt_api.playlists().list(
            part="snippet,contentDetails",
            channelId=CHANNEL_ID,
            maxResults=50,
            pageToken=next_token,
        ).execute()

        for item in resp.get("items", []):
            playlists.append({
                "playlistId": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"].get("description", ""),
                "itemCount": item["contentDetails"]["itemCount"],
                "publishedAt": item["snippet"]["publishedAt"],
                "videoIds": [],
            })

        next_token = resp.get("nextPageToken")
        if not next_token:
            break

    print(f"✅ {len(playlists)}個のプレイリストを取得")

    # 各プレイリスト内の動画IDを取得
    for pl in playlists:
        if pl["itemCount"] == 0:
            continue
        video_ids = []
        next_token = None
        while True:
            resp = yt_api.playlistItems().list(
                part="contentDetails",
                playlistId=pl["playlistId"],
                maxResults=50,
                pageToken=next_token,
            ).execute()
            for item in resp.get("items", []):
                vid = item["contentDetails"].get("videoId")
                if vid:
                    video_ids.append(vid)
            next_token = resp.get("nextPageToken")
            if not next_token:
                break
        pl["videoIds"] = video_ids
        print(f"  [{len(video_ids)}本] {pl['title']}")

    return playlists


def link_obsidian_notes(videos: list[dict]) -> list[dict]:
    """Obsidianの既存ノートからvideoIdを抽出して文字起こしを紐付け"""
    print("\n📝 Obsidianノートを紐付け中...")

    if not OBSIDIAN_VIDEOS_DIR.exists():
        print("  ⚠️ Obsidian YouTube動画ディレクトリが見つかりません")
        return videos

    # ノートからvideoId→文字起こしのマップを構築
    transcript_map = {}
    for note_path in OBSIDIAN_VIDEOS_DIR.glob("*.md"):
        content = note_path.read_text(encoding="utf-8", errors="replace")
        # URLからvideoIdを抽出
        match = re.search(r"youtube\.com/watch\?v=([a-zA-Z0-9_-]+)", content)
        if not match:
            continue
        vid = match.group(1)

        # 文字起こしセクションを抽出
        transcript_match = re.search(
            r"## 文字起こし.*?\n(.*)",
            content,
            re.DOTALL,
        )
        if transcript_match:
            transcript = transcript_match.group(1).strip()
            # 長すぎる場合は切り詰め（概要生成用なので先頭で十分）
            if len(transcript) > 3000:
                transcript = transcript[:3000] + "..."
            transcript_map[vid] = transcript

    # 動画データに紐付け
    linked = 0
    for v in videos:
        transcript = transcript_map.get(v["videoId"])
        if transcript:
            v["transcript"] = transcript
            linked += 1
        else:
            v["transcript"] = ""

    print(f"✅ {linked}/{len(videos)}本の動画に文字起こしを紐付け")
    return videos


def build_reverse_playlist_map(playlists: list[dict]) -> dict:
    """動画ID → 所属プレイリスト名リストの逆引きマップ"""
    reverse = {}
    for pl in playlists:
        for vid in pl["videoIds"]:
            if vid not in reverse:
                reverse[vid] = []
            reverse[vid].append(pl["title"])
    return reverse


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("🚀 全動画メタデータ取得開始\n")

    # 1. OAuth認証で全動画ID+基本情報取得
    yt_oauth = get_youtube_service()
    videos = fetch_all_video_ids(yt_oauth)

    # 2. APIキー認証で統計情報追加
    yt_api = get_api_key_service()
    videos = enrich_with_statistics(yt_api, videos)

    # 3. プレイリスト取得
    playlists = fetch_all_playlists(yt_api)

    # 4. Obsidianノート紐付け
    videos = link_obsidian_notes(videos)

    # 5. プレイリスト逆引きを動画に追加
    reverse_map = build_reverse_playlist_map(playlists)
    for v in videos:
        v["playlists"] = reverse_map.get(v["videoId"], [])

    # 6. 公開日で新しい順にソート
    videos.sort(key=lambda v: v.get("publishedAt", ""), reverse=True)

    # 7. 保存
    videos_path = OUTPUT_DIR / "videos.json"
    with open(videos_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"\n💾 {videos_path} に{len(videos)}本の動画データを保存")

    playlists_path = OUTPUT_DIR / "playlists.json"
    with open(playlists_path, "w", encoding="utf-8") as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)
    print(f"💾 {playlists_path} に{len(playlists)}個のプレイリストデータを保存")

    # サマリー
    total_views = sum(v.get("viewCount", 0) for v in videos)
    total_duration_h = sum(v.get("durationSeconds", 0) for v in videos) / 3600
    with_transcript = sum(1 for v in videos if v.get("transcript"))
    public = sum(1 for v in videos if v.get("privacyStatus") == "public")
    unlisted = sum(1 for v in videos if v.get("privacyStatus") == "unlisted")
    private = sum(1 for v in videos if v.get("privacyStatus") == "private")

    print(f"\n📊 サマリー:")
    print(f"  動画数: {len(videos)}本（公開{public} / 限定{unlisted} / 非公開{private}）")
    print(f"  総再生数: {total_views:,}")
    print(f"  総再生時間: {total_duration_h:.1f}時間")
    print(f"  文字起こし付き: {with_transcript}本")
    print(f"  プレイリスト: {len(playlists)}個")


if __name__ == "__main__":
    main()
