import { defineClientConfig } from 'vuepress/client'
import { onMounted } from 'vue'

export default defineClientConfig({
  setup() {
    onMounted(() => {
      const details = document.querySelector('.about-me')
      if (!details) return

      const content = details.querySelector('.about-me-content')
      if (!content) return

      // 初期状態を設定
      content.style.maxHeight = '0'
      content.style.opacity = '0'
      content.style.overflow = 'hidden'
      content.style.transition = 'max-height 0.4s ease-out, opacity 0.4s ease-out'

      details.addEventListener('click', (e) => {
        if (e.target.tagName === 'SUMMARY' || e.target.closest('summary')) {
          e.preventDefault()

          if (details.open) {
            // 閉じるアニメーション
            content.style.maxHeight = '0'
            content.style.opacity = '0'
            setTimeout(() => {
              details.open = false
            }, 400)
          } else {
            // 開くアニメーション
            details.open = true
            requestAnimationFrame(() => {
              content.style.maxHeight = content.scrollHeight + 'px'
              content.style.opacity = '1'
            })
          }
        }
      })
    })
  }
})
