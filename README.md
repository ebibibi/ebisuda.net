# ebisuda.net

胡田昌彦の個人Webサイト [ebisuda.net](https://ebisuda.net) のソースコードです。

## 技術構成

- [VuePress 2.x](https://vuepress.vuejs.org/) - Vue 3ベースの静的サイトジェネレーター
- [Vite](https://vitejs.dev/) - バンドラー
- [Azure Static Web Apps](https://azure.microsoft.com/ja-jp/products/app-service/static) - ホスティング
- GitHub Actions - CI/CD

## ローカル開発

### 必要条件

- Node.js 18以上

### セットアップ

```bash
npm install
```

### 開発サーバーの起動

```bash
npm run docs:dev
```

### ビルド

```bash
npm run build
```

ビルド成果物は `docs/.vuepress/dist` に出力されます。

## デプロイ

`main` ブランチへのpushまたはPull Requestのマージ時に、GitHub ActionsがAzure Static Web Appsへ自動デプロイします。

## ディレクトリ構成

```
.
├── docs/
│   ├── README.md              # サイトのコンテンツ
│   └── .vuepress/
│       └── config.js          # VuePressの設定
├── .github/
│   └── workflows/             # GitHub Actions設定
├── package.json
└── README.md                  # このファイル
```

## ライセンス

MIT
