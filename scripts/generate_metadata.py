#!/usr/bin/env python3
"""
AI概要・カテゴリ自動生成スクリプト

videos.json の各動画に対して:
- summary: 1-2行の概要文（動画を見なくてもわかる）
- category: 上位カテゴリ
- subcategory: サブカテゴリ
- level: 対象者レベル（beginner/intermediate/advanced）
- targetAudience: 対象者の説明

を自動生成して videos.json を更新する。

Gemini CLI をバッチ処理で使用（コスト効率重視）。
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
VIDEOS_PATH = DATA_DIR / "videos.json"

# カテゴリ定義
CATEGORIES = {
    "azure": {
        "name": "Azure",
        "subcategories": [
            "IaaS（VM・ネットワーク・ストレージ）",
            "PaaS（App Service・Functions・Container Apps）",
            "コンテナ（AKS・Docker）",
            "IaC（Bicep・ARM・Terraform）",
            "Azure Arc・ハイブリッド",
            "Azure Stack HCI / Azure Local",
            "AVD（仮想デスクトップ）",
            "監視・運用（Monitor・Log Analytics）",
            "その他Azure",
        ],
    },
    "m365": {
        "name": "Microsoft 365",
        "subcategories": [
            "Teams",
            "SharePoint・OneDrive",
            "Exchange・メール",
            "M365 Copilot",
            "Office アプリ（Excel・Word・PowerPoint）",
            "Power Platform（PowerApps・PowerAutomate・Power BI）",
            "M365 管理・ライセンス",
            "その他M365",
        ],
    },
    "identity": {
        "name": "ID管理・認証",
        "subcategories": [
            "Microsoft Entra ID（Azure AD）",
            "Active Directory（オンプレミス）",
            "条件付きアクセス",
            "SSO・認証連携",
            "証明書・PKI",
            "その他ID管理",
        ],
    },
    "ai": {
        "name": "AI・生成AI",
        "subcategories": [
            "Azure OpenAI Service",
            "ChatGPT",
            "Claude / Claude Code",
            "ローカルLLM",
            "MCP（Model Context Protocol）",
            "AIエージェント",
            "AIアプリ開発",
            "AI全般・トレンド",
        ],
    },
    "windows": {
        "name": "Windows",
        "subcategories": [
            "Windows 11",
            "Windows 10",
            "Windows Server",
            "Intune・デバイス管理",
            "トラブルシューティング・Tips",
            "その他Windows",
        ],
    },
    "security": {
        "name": "セキュリティ",
        "subcategories": [
            "ゼロトラスト・Defender",
            "ネットワークセキュリティ",
            "パケットキャプチャ",
            "その他セキュリティ",
        ],
    },
    "dev": {
        "name": "開発者向け",
        "subcategories": [
            "PowerShell",
            "Python",
            "自動化・スクリプト",
            "Logic Apps",
            "その他開発",
        ],
    },
    "beginner": {
        "name": "初心者・入門",
        "subcategories": [
            "PC基礎",
            "Azure入門",
            "クラウド入門",
            "その他入門",
        ],
    },
    "news": {
        "name": "ニュース・更新情報",
        "subcategories": [
            "Azure更新情報",
            "M365更新情報",
            "記事紹介・トレンド",
            "Microsoft Build・Ignite",
        ],
    },
    "other": {
        "name": "その他",
        "subcategories": [
            "雑談・振り返り",
            "インタビュー",
            "ツール紹介",
            "キャリア・英語",
            "その他",
        ],
    },
}


def build_category_text() -> str:
    """プロンプト用のカテゴリ一覧テキスト"""
    lines = []
    for key, cat in CATEGORIES.items():
        lines.append(f"- {key}: {cat['name']}")
        for sub in cat["subcategories"]:
            lines.append(f"  - {sub}")
    return "\n".join(lines)


def classify_batch(videos_batch: list[dict]) -> list[dict]:
    """Claude CLI (haiku) でバッチ分類"""
    category_text = build_category_text()

    video_entries = []
    for i, v in enumerate(videos_batch):
        playlists = ", ".join(v.get("playlists", [])) or "なし"
        desc = (v.get("description", "") or "")[:200]
        transcript = (v.get("transcript", "") or "")[:300]
        video_entries.append(
            f"[{i}] タイトル: {v['title']}\n"
            f"    プレイリスト: {playlists}\n"
            f"    説明: {desc}\n"
            f"    文字起こし冒頭: {transcript}"
        )

    videos_text = "\n\n".join(video_entries)

    prompt = f"""以下のYouTube動画リストに対して、各動画のメタデータをJSON配列で返してください。

## カテゴリ定義
{category_text}

## 動画リスト
{videos_text}

## 出力形式
各動画に対して以下のJSONオブジェクトを含む配列を返してください。配列のインデックスは入力の[番号]に対応します。
JSON配列のみを出力してください。説明文やマークダウンのコードブロックマーカーは一切不要です。
[
  {{
    "index": 0,
    "summary": "動画の概要を1-2文で（動画を見なくても内容がわかるように）",
    "category": "カテゴリキー（azure/m365/identity/ai/windows/security/dev/beginner/news/other）",
    "subcategory": "サブカテゴリ名（上のリストから選択）",
    "level": "beginner または intermediate または advanced",
    "targetAudience": "対象者の簡潔な説明（例: Azure初心者、IT管理者、開発者）"
  }}
]

重要:
- summaryは日本語で、具体的に何がわかる/学べるかを書く
- levelはbeginner/intermediate/advancedのいずれか
- 全{len(videos_batch)}件分を返すこと"""

    try:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        result = subprocess.run(
            ["claude", "-p", "--model", "haiku", prompt],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            print(f"  ⚠️ Claude CLIエラー: {result.stderr[:200]}")
            return []

        # JSON配列を抽出
        json_match = output
        if "```json" in output:
            json_match = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            json_match = output.split("```")[1].split("```")[0].strip()

        start = json_match.find("[")
        end = json_match.rfind("]") + 1
        if start >= 0 and end > start:
            json_match = json_match[start:end]

        parsed = json.loads(json_match)
        return parsed

    except subprocess.TimeoutExpired:
        print("  ⚠️ Claudeタイムアウト")
        return []
    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON解析エラー: {e}")
        print(f"  出力先頭: {output[:300]}")
        return []
    except Exception as e:
        print(f"  ⚠️ エラー: {e}")
        return []


def main():
    videos = json.loads(VIDEOS_PATH.read_text(encoding="utf-8"))
    print(f"📊 {len(videos)}本の動画にAIメタデータを生成します\n")

    # 既にsummaryがある動画はスキップ
    todo = [i for i, v in enumerate(videos) if not v.get("summary")]
    print(f"  未処理: {len(todo)}本 / 処理済み: {len(videos) - len(todo)}本\n")

    if not todo:
        print("✅ 全動画処理済み")
        return

    # 20件ずつバッチ処理
    BATCH_SIZE = 20
    processed = 0
    errors = 0

    for batch_start in range(0, len(todo), BATCH_SIZE):
        batch_indices = todo[batch_start : batch_start + BATCH_SIZE]
        batch_videos = [videos[i] for i in batch_indices]

        print(f"🤖 バッチ {batch_start // BATCH_SIZE + 1} ({len(batch_videos)}本)...")

        results = classify_batch(batch_videos)

        if results:
            for item in results:
                idx = item.get("index")
                if idx is not None and 0 <= idx < len(batch_indices):
                    video_idx = batch_indices[idx]
                    videos[video_idx]["summary"] = item.get("summary", "")
                    videos[video_idx]["category"] = item.get("category", "other")
                    videos[video_idx]["subcategory"] = item.get("subcategory", "その他")
                    videos[video_idx]["level"] = item.get("level", "intermediate")
                    videos[video_idx]["targetAudience"] = item.get("targetAudience", "")
                    processed += 1
            print(f"  ✅ {len(results)}件処理完了")
        else:
            errors += len(batch_videos)
            print(f"  ❌ バッチ失敗")

        # 10バッチごとに中間保存
        if (batch_start // BATCH_SIZE + 1) % 10 == 0:
            with open(VIDEOS_PATH, "w", encoding="utf-8") as f:
                json.dump(videos, f, ensure_ascii=False, indent=2)
            print(f"  💾 中間保存 ({processed}件処理済み)")

        # レート制限対策
        time.sleep(1)

    # 最終保存
    with open(VIDEOS_PATH, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完了: {processed}件処理 / {errors}件エラー")
    print(f"💾 {VIDEOS_PATH} を更新しました")

    # カテゴリ別集計
    cat_count = {}
    for v in videos:
        cat = v.get("category", "unknown")
        cat_count[cat] = cat_count.get(cat, 0) + 1
    print(f"\n📊 カテゴリ別集計:")
    for cat, count in sorted(cat_count.items(), key=lambda x: -x[1]):
        name = CATEGORIES.get(cat, {}).get("name", cat)
        print(f"  {name}: {count}本")


if __name__ == "__main__":
    main()
