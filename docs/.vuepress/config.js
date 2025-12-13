import { defaultTheme } from '@vuepress/theme-default'
import { defineUserConfig } from 'vuepress/cli'
import { viteBundler } from '@vuepress/bundler-vite'

export default defineUserConfig({
  lang: 'ja-JP',

  title: 'WEBI',
  description: '胡田昌彦の個人Webサイト',

  head: [
    ['meta', { name: 'theme-color', content: '#3a7bd5' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
  ],

  theme: defaultTheme({
    logo: 'https://0.gravatar.com/avatar/6d1b435a74677ddddc346307eed74660e1ba04f2ddaea5cb821e2ae39f413df0?s=80',
    navbar: false,
    contributors: false,
    lastUpdated: false,
  }),

  bundler: viteBundler(),
})
