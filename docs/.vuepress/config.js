import { defaultTheme } from '@vuepress/theme-default'
import { defineUserConfig } from 'vuepress/cli'
import { viteBundler } from '@vuepress/bundler-vite'
import { fs, path } from 'vuepress/utils'

// ========================================================
// Chatwoot 設定（URLが変わったらここだけ更新すればOK）
// ========================================================
const CHATWOOT_BASE_URL = 'https://moviegen.tail954a8f.ts.net'
const CHATWOOT_TOKEN = 'PaDnD4T2wrMmcNM5cx1YWibW'
// ========================================================

export default defineUserConfig({
  lang: 'ja-JP',

  title: 'WEBI',
  description: '胡田昌彦の個人Webサイト',

  head: [
    ['meta', { name: 'theme-color', content: '#3a7bd5' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['script', {}, `(function(d,t) {
      var BASE_URL="${CHATWOOT_BASE_URL}";
      var g=d.createElement(t),s=d.getElementsByTagName(t)[0];
      g.src=BASE_URL+"/packs/js/sdk.js";
      g.async = true;
      s.parentNode.insertBefore(g,s);
      g.onload=function(){
        window.chatwootSDK.run({
          websiteToken: '${CHATWOOT_TOKEN}',
          baseUrl: BASE_URL
        })
      }
    })(document,"script");`],
  ],

  theme: defaultTheme({
    logo: 'https://0.gravatar.com/avatar/6d1b435a74677ddddc346307eed74660e1ba04f2ddaea5cb821e2ae39f413df0?s=80',
    navbar: false,
    contributors: false,
    lastUpdated: false,
  }),

  bundler: viteBundler(),

  plugins: [
    {
      name: 'chatwoot-chat-redirect',
      async onGenerated(app) {
        const chatUrl = `${CHATWOOT_BASE_URL}/widget?website_token=${CHATWOOT_TOKEN}`
        const chatDir = path.join(app.dir.dest(), 'chat')
        fs.mkdirSync(chatDir, { recursive: true })
        fs.writeFileSync(path.join(chatDir, 'index.html'), `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=${chatUrl}">
  <script>window.location.replace('${chatUrl}')</script>
  <title>チャット</title>
</head>
<body></body>
</html>`)
      }
    }
  ],
})
