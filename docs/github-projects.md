---
title: GitHub プロジェクト一覧
navbar: false
sidebar: false
---

# GitHub プロジェクト一覧

胡田昌彦が公開しているGitHubリポジトリです。主要な自作プロダクト・ツール・スクリプトをまとめています。

<div class="github-projects">

## コミュニティ向け OSS

| リポジトリ | 説明 | 言語 |
|:-----------|:-----|:-----|
| [claude-code-discord-bridge](https://github.com/ebibibi/claude-code-discord-bridge) ⭐9 | Discord × Claude Code OSSフレームワーク。DiscordのスレッドからClaude Codeとチャットできます | Python |
| [obsidian-cjk-bold-fix](https://github.com/ebibibi/obsidian-cjk-bold-fix) ⭐1 | ObsidianのライブプレビューモードでCJK（中国語・日本語・韓国語）の太字・斜体レンダリングを修正するプラグイン | TypeScript |
| [DavinciResolveScripts](https://github.com/ebibibi/DavinciResolveScripts) ⭐3 | DaVinci Resolve用のスクリプト集 | Python |
| [ansible-hyperv](https://github.com/ebibibi/ansible-hyperv) ⭐2 | HyperV上にVMをプロビジョニングするAnsible Playbookサンプル | PowerShell |
| [m365management](https://github.com/ebibibi/m365management) ⭐2 | Microsoft 365管理用スクリプト集 | PowerShell |
| [AzureManagement](https://github.com/ebibibi/AzureManagement) ⭐2 | Azure管理用スクリプト集 | PowerShell |
| [youtubebicep](https://github.com/ebibibi/youtubebicep) ⭐1 | YouTubeで紹介したAzure Bicepテンプレート集 | Bicep |

## Webサービス・アプリ

| リポジトリ | 説明 | 言語 |
|:-----------|:-----|:-----|
| [nearjam](https://github.com/ebibibi/nearjam) | ジャムセッションを探せる・開催できる2サイドプラットフォーム。ミュージシャンと会場をつなぎます | TypeScript |
| [process_skyblue](https://github.com/ebibibi/process_skyblue) | BlueSkyの投稿をX（Twitter）とDiscordにクロスポストするDockerコンテナサービス | Python |
| [ffmpeg-multistream-azure](https://github.com/ebibibi/ffmpeg-multistream-azure) | Azure Container Instances上でffmpegを使いYouTube/Facebook/X/LinkedInへRTMP同時配信 | Shell |
| [restreamer-azure](https://github.com/ebibibi/restreamer-azure) | Azure Container InstancでRestreamerをオンデマンド実行するRTMP再配信環境 | Shell |
| [discord-bot](https://github.com/ebibibi/discord-bot) | 個人用Discord Bot（EbiBot）。Push通知・Watchdog機能を持つ常駐Bot | Python |
| [web-change-line-notifier](https://github.com/ebibibi/web-change-line-notifier) | Webサイトの変更を検知してLINEに通知するツール | Python |
| [ebiyoutubeguide](https://github.com/ebibibi/ebiyoutubeguide) | YouTubeチャンネル向けガイドサイト | TypeScript |
| [diary](https://github.com/ebibibi/diary) | えび日記サイト（[diary.ebisuda.net](https://diary.ebisuda.net)） | HTML |
| [ebisuda.net](https://github.com/ebibibi/ebisuda.net) | このWebサイトのソースコード。VuePress + Azure Static Web Apps | Python |

## ツール・スクリプト

| リポジトリ | 説明 | 言語 |
|:-----------|:-----|:-----|
| [video2srt](https://github.com/ebibibi/video2srt) | 動画ファイルからSRT字幕ファイルを生成するツール | Python |
| [dify-azure-terraform](https://github.com/ebibibi/dify-azure-terraform) | DifyをAzureにデプロイするTerraformテンプレート | HCL |
| [azureguestconfig](https://github.com/ebibibi/azureguestconfig) | Azure Guest Configurationのサンプル集 | PowerShell |
| [InstallBasicToolsToWindows](https://github.com/ebibibi/InstallBasicToolsToWindows) | Windowsクライアント・サーバーに基本ツールをインストールするスクリプト | PowerShell |

## デモ・登壇資料

| リポジトリ | 説明 | 言語 |
|:-----------|:-----|:-----|
| [Demos](https://github.com/ebibibi/Demos) | 各種デモを管理するリポジトリ | Bicep |
| [presentations](https://github.com/ebibibi/presentations) | 登壇・発表で使ったプレゼン資料 | HTML |
| [youtubedemo](https://github.com/ebibibi/youtubedemo) | [YouTubeチャンネル](https://www.youtube.com/@ebibibi)でデモした際に使ったコード集 | Python |

</div>

---

<div class="github-link-section">

GitHubプロファイル全体は <a href="https://github.com/ebibibi" target="_blank">github.com/ebibibi</a> でご確認いただけます。

</div>

<style>
.github-projects table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
}

.github-projects th {
  background-color: var(--c-brand);
  color: white;
  padding: 0.6rem 1rem;
  text-align: left;
}

.github-projects td {
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--c-border);
  vertical-align: top;
}

.github-projects tr:hover td {
  background-color: var(--c-bg-lighter);
}

.github-projects a {
  font-weight: 600;
}

.github-link-section {
  margin-top: 2rem;
  padding: 1rem;
  background: var(--c-bg-lighter);
  border-radius: 8px;
  text-align: center;
  font-size: 1.05rem;
}
</style>
