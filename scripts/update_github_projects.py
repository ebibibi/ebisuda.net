#!/usr/bin/env python3
"""
GitHub プロジェクトページ自動更新スクリプト

github-projects-config.yaml を読み込み、GitHub APIでリポジトリ情報を取得して
docs/github-projects.md を再生成する。新規リポジトリを検出したらDiscordに通知する。

使用方法:
  python3 scripts/update_github_projects.py
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "github-projects-config.yaml"
OUTPUT_PATH = REPO_ROOT / "docs" / "github-projects.md"
DISCORD_API = "http://127.0.0.1:8099/api/notify"
GITHUB_USER = "ebibibi"


def run(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()


def fetch_all_public_repos() -> dict[str, dict]:
    """gh CLI で公開リポジトリ一覧を取得する"""
    raw = run(
        f"gh api /users/{GITHUB_USER}/repos --paginate "
        "-q '.[] | select(.private == false) | "
        "{name: .name, description: .description, "
        "html_url: .html_url, language: .language, "
        "stargazers_count: .stargazers_count, fork: .fork}'"
    )
    repos = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        repos[data["name"]] = data
    return repos


def fetch_repo(name: str) -> dict:
    """単一リポジトリの情報を gh CLI で取得する"""
    raw = run(f"gh api /repos/{GITHUB_USER}/{name}")
    data = json.loads(raw)
    return {
        "name": data["name"],
        "description": data.get("description") or "",
        "html_url": data["html_url"],
        "language": data.get("language") or "",
        "stargazers_count": data.get("stargazers_count", 0),
    }


def star_label(count: int) -> str:
    if count == 0:
        return ""
    return f" ⭐{count}"


def generate_markdown(categories: list[dict], repo_data: dict[str, dict]) -> str:
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "---",
        "title: GitHub プロジェクト一覧",
        "navbar: false",
        "sidebar: false",
        "---",
        "",
        "# GitHub プロジェクト一覧",
        "",
        "胡田昌彦が公開しているGitHubリポジトリです。"
        "主要な自作プロダクト・ツール・スクリプトをまとめています。",
        "",
        f"<small>最終更新: {updated_at}（自動更新）</small>",
        "",
        '<div class="github-projects">',
        "",
    ]

    for category in categories:
        lines.append(f"## {category['name']}")
        lines.append("")
        lines.append("| リポジトリ | 説明 | 言語 |")
        lines.append("|:-----------|:-----|:-----|")
        for repo_name in category["repos"]:
            info = repo_data.get(repo_name)
            if not info:
                print(f"  警告: {repo_name} のデータが取得できませんでした（スキップ）")
                continue
            stars = star_label(info["stargazers_count"])
            desc = info["description"].replace("|", "&#124;") if info["description"] else "（説明なし）"
            lang = info["language"] or "—"
            url = info["html_url"]
            lines.append(f"| [{repo_name}]({url}){stars} | {desc} | {lang} |")
        lines.append("")

    lines += [
        "</div>",
        "",
        "---",
        "",
        '<div class="github-link-section">',
        "",
        f'GitHubプロファイル全体は <a href="https://github.com/{GITHUB_USER}" target="_blank">'
        f"github.com/{GITHUB_USER}</a> でご確認いただけます。",
        "",
        "</div>",
        "",
        "<style>",
        ".github-projects table {",
        "  width: 100%;",
        "  border-collapse: collapse;",
        "  margin-bottom: 1.5rem;",
        "}",
        "",
        ".github-projects th {",
        "  background-color: var(--c-brand);",
        "  color: white;",
        "  padding: 0.6rem 1rem;",
        "  text-align: left;",
        "}",
        "",
        ".github-projects td {",
        "  padding: 0.6rem 1rem;",
        "  border-bottom: 1px solid var(--c-border);",
        "  vertical-align: top;",
        "}",
        "",
        ".github-projects tr:hover td {",
        "  background-color: var(--c-bg-lighter);",
        "}",
        "",
        ".github-projects a {",
        "  font-weight: 600;",
        "}",
        "",
        ".github-link-section {",
        "  margin-top: 2rem;",
        "  padding: 1rem;",
        "  background: var(--c-bg-lighter);",
        "  border-radius: 8px;",
        "  text-align: center;",
        "  font-size: 1.05rem;",
        "}",
        "</style>",
    ]

    return "\n".join(lines) + "\n"


def notify_discord(message: str) -> None:
    payload = json.dumps({"message": message, "title": "GitHub Projects 自動更新"})
    try:
        run(
            f"curl -s -X POST {DISCORD_API} "
            f"-H 'Content-Type: application/json' "
            f"-d '{payload}'"
        )
    except RuntimeError as e:
        print(f"Discord通知に失敗しました（無視して続行）: {e}")


def detect_new_repos(
    all_repos: dict[str, dict],
    curated: set[str],
    ignored: set[str],
) -> list[str]:
    """キュレーション済みでも除外済みでもない = 新規リポジトリ"""
    return [
        name
        for name, info in all_repos.items()
        if name not in curated
        and name not in ignored
        and not info.get("fork", False)
    ]


def main() -> None:
    print("=== GitHub Projects 自動更新 ===")

    # 設定読み込み
    config = yaml.safe_load(CONFIG_PATH.read_text())
    categories = config["categories"]
    ignore_set = set(config.get("ignore", []))
    curated_set = {r for cat in categories for r in cat["repos"]}

    # GitHub API でデータ取得
    print("GitHub API からリポジトリ一覧を取得中...")
    all_repos = fetch_all_public_repos()
    print(f"  公開リポジトリ数: {len(all_repos)}")

    # キュレーション済みリポジトリのデータを取得
    repo_data: dict[str, dict] = {}
    for repo_name in curated_set:
        print(f"  取得中: {repo_name}")
        try:
            repo_data[repo_name] = fetch_repo(repo_name)
        except RuntimeError as e:
            print(f"  エラー: {e}")

    # Markdown 再生成
    print("docs/github-projects.md を再生成中...")
    md = generate_markdown(categories, repo_data)
    OUTPUT_PATH.write_text(md)
    print("  完了")

    # Git commit & push
    print("Git commit & push...")
    run(f"git -C {REPO_ROOT} add docs/github-projects.md")
    diff = subprocess.run(
        f"git -C {REPO_ROOT} diff --cached --quiet",
        shell=True,
    )
    if diff.returncode == 0:
        print("  変更なし（スキップ）")
    else:
        try:
            run(
                f'git -C {REPO_ROOT} commit -m '
                f'"chore: update GitHub projects page ({datetime.now().strftime("%Y-%m")})"'
            )
            run(f"git -C {REPO_ROOT} push origin main")
            print("  プッシュ完了")
        except RuntimeError as e:
            print(f"  Git操作エラー: {e}")
            sys.exit(1)

    # 新規リポジトリの検出 & Discord通知
    new_repos = detect_new_repos(all_repos, curated_set, ignore_set)
    if new_repos:
        names = ", ".join(new_repos)
        msg = (
            f"新しい公開リポジトリを検出しました！\n"
            f"{names}\n\n"
            f"github-projects-config.yaml に追加するか確認してください。"
        )
        print(f"新規リポジトリ検出: {names}")
        notify_discord(msg)
    else:
        print("新規リポジトリなし")

    print("=== 完了 ===")


if __name__ == "__main__":
    main()
