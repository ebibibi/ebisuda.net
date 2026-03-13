import { chromium } from 'playwright';
import { mkdir } from 'fs/promises';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outputDir = join(__dirname, '../docs/.vuepress/public/images');

const sites = [
  { url: 'https://www.youtube.com/@ebibibi', name: 'youtube-ebibibi.png' },
  { url: 'https://ebibibi.github.io/yt-channel-navigator/', name: 'yt-channel-navigator.png', clipY: 0, clipHeight: 400 },
  { url: 'https://amzn.to/3PvYqWG', name: 'amazon-book.png' },
  { url: 'https://mvp.microsoft.com/ja-JP/mvp/profile/959007f9-3c9a-e411-93f2-9cb65495d3c4', name: 'mvp.png' },
  { url: 'https://note.com/ebibibi', name: 'note.png' },
  { url: 'https://diary.ebisuda.net', name: 'diary.png' },
  { url: 'https://www.youtube.com/channel/UCgKek_Bu1t_gJ83ABfLBwBQ', name: 'youtube-music.png' },
  { url: 'https://www.youtube.com/channel/UCb2h5Jqh3SWOVwV8AUUgPpw', name: 'youtube-shogi.png' },
  { url: 'https://soundcloud.com/masahiko-ebisuda', name: 'soundcloud.png' },
  { url: 'https://speakerdeck.com/ebibibi', name: 'speakerdeck.png' },
  { url: 'https://github.com/ebibibi/claude-code-discord-bridge', name: 'oss-ccdb.png' },
  { url: 'https://github.com/ebibibi/marp2pptx', name: 'oss-marp2pptx.png' },
  { url: 'https://github.com/ebibibi/process_skyblue', name: 'oss-process-skyblue.png' },
  { url: 'https://github.com/ebibibi/obsidian-cjk-bold-fix', name: 'oss-obsidian-cjk-bold-fix.png' },
  { url: 'https://github.com/ebibibi/ffmpeg-multistream-azure', name: 'oss-ffmpeg-multistream.png' },
  { url: 'https://github.com/ebibibi/restreamer-azure', name: 'oss-restreamer-azure.png' },
  { url: 'https://github.com/ebibibi/ansible-hyperv', name: 'oss-ansible-hyperv.png' },
];

async function takeScreenshots() {
  await mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1200, height: 800 },
    locale: 'ja-JP',
  });

  for (const site of sites) {
    console.log(`Capturing: ${site.url}`);
    const page = await context.newPage();

    try {
      await page.goto(site.url, {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      await page.waitForTimeout(2000);

      // カスタムclip設定がある場合はそれを使う
      const clipY = site.clipY ?? 0;
      const clipHeight = site.clipHeight ?? 640;

      await page.screenshot({
        path: join(outputDir, site.name),
        clip: { x: 0, y: clipY, width: 1200, height: clipHeight },
      });

      console.log(`  ✓ Saved: ${site.name}`);
    } catch (error) {
      console.error(`  ✗ Failed: ${site.name} - ${error.message}`);
    } finally {
      await page.close();
    }
  }

  await browser.close();
  console.log('\nDone!');
}

takeScreenshots();
