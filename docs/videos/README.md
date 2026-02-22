---
title: 動画ライブラリ
navbar: false
sidebar: false
---

<div id="video-portal">
  <div id="vp-header">
    <h1 id="vp-title">動画ライブラリ</h1>
    <p id="vp-subtitle">855本以上の動画から、あなたに合ったコンテンツを見つけよう</p>
  </div>

  <div id="vp-search-area">
    <input type="text" id="vp-search" placeholder="キーワードで検索（例: Azure VM、Teams、Bicep）">
    <div id="vp-filters">
      <select id="vp-cat-filter">
        <option value="">すべてのカテゴリ</option>
      </select>
      <select id="vp-level-filter">
        <option value="">すべてのレベル</option>
        <option value="beginner">初心者向け</option>
        <option value="intermediate">中級者向け</option>
        <option value="advanced">上級者向け</option>
      </select>
      <select id="vp-sort">
        <option value="date-desc">新しい順</option>
        <option value="date-asc">古い順</option>
        <option value="views-desc">再生数順</option>
        <option value="likes-desc">いいね順</option>
      </select>
    </div>
    <div id="vp-result-count"></div>
  </div>

  <div id="vp-personas"></div>
  <div id="vp-categories"></div>
  <div id="vp-video-grid" class="card-grid"></div>
  <div id="vp-load-more-area"></div>
  <div id="vp-back-link">
    <a href="/">← トップページに戻る</a>
  </div>
</div>

<script>
(function() {
  if (typeof document === 'undefined') return;
  var PAGE_SIZE = 24;
  var currentPage = 0;
  var filteredVideos = [];
  var allVideos = [];
  var categories = [];

  function el(tag, attrs, children) {
    var e = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function(k) {
        if (k === 'className') e.className = attrs[k];
        else if (k === 'textContent') e.textContent = attrs[k];
        else if (k.startsWith('on')) e.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
        else e.setAttribute(k, attrs[k]);
      });
    }
    if (children) {
      children.forEach(function(c) {
        if (typeof c === 'string') e.appendChild(document.createTextNode(c));
        else if (c) e.appendChild(c);
      });
    }
    return e;
  }

  function formatNumber(n) {
    if (n >= 10000) return (n / 10000).toFixed(1) + '万';
    if (n >= 1000) return (n / 1000).toFixed(1) + '千';
    return String(n);
  }

  function getLevelLabel(level) {
    var m = { beginner: '初心者', intermediate: '中級', advanced: '上級' };
    return m[level] || level;
  }

  function getLevelColor(level) {
    var m = { beginner: '#107C10', intermediate: '#0078D4', advanced: '#E81123' };
    return m[level] || '#767676';
  }

  function renderPersonas() {
    var container = document.getElementById('vp-personas');
    if (!container) return;
    container.textContent = '';

    var personas = [
      { icon: '🏢', title: 'IT管理者・インフラ担当', desc: 'Azure, Windows Server, Active Directoryの設計・運用', cats: ['azure', 'windows', 'identity'] },
      { icon: '☁️', title: 'クラウドを学びたい方', desc: 'Azure入門からIaC、コンテナまでステップアップ', cats: ['azure', 'beginner'] },
      { icon: '🤖', title: 'AIに興味がある方', desc: 'ChatGPT, Azure OpenAI, Claude Code, ローカルLLM', cats: ['ai'] },
      { icon: '💼', title: 'M365を活用したい方', desc: 'Teams, SharePoint, Power Platform, Copilot', cats: ['m365'] }
    ];

    var sectionTitle = el('h2', { className: 'vp-section-title', textContent: 'こんな方におすすめ' });
    container.appendChild(sectionTitle);

    var grid = el('div', { className: 'vp-persona-grid' });
    personas.forEach(function(p) {
      var card = el('div', { className: 'vp-persona-card' }, [
        el('div', { className: 'vp-persona-icon', textContent: p.icon }),
        el('div', { className: 'vp-persona-info' }, [
          el('div', { className: 'vp-persona-title', textContent: p.title }),
          el('div', { className: 'vp-persona-desc', textContent: p.desc })
        ])
      ]);
      card.style.cursor = 'pointer';
      card.addEventListener('click', function() {
        var catFilter = document.getElementById('vp-cat-filter');
        if (catFilter && p.cats[0]) {
          catFilter.value = p.cats[0];
          applyFilters();
          document.getElementById('vp-video-grid').scrollIntoView({ behavior: 'smooth' });
        }
      });
      grid.appendChild(card);
    });
    container.appendChild(grid);
  }

  function renderCategories() {
    var container = document.getElementById('vp-categories');
    if (!container) return;
    container.textContent = '';

    var sectionTitle = el('h2', { className: 'vp-section-title', textContent: 'カテゴリ一覧' });
    container.appendChild(sectionTitle);

    var grid = el('div', { className: 'vp-cat-grid' });
    categories.forEach(function(cat) {
      var count = allVideos.filter(function(v) { return v.category === cat.id; }).length;
      var card = el('div', { className: 'vp-cat-card' }, [
        el('div', { className: 'vp-cat-icon', textContent: cat.icon }),
        el('div', { className: 'vp-cat-info' }, [
          el('div', { className: 'vp-cat-name', textContent: cat.name }),
          el('div', { className: 'vp-cat-count', textContent: count + '本' })
        ])
      ]);
      card.style.cursor = 'pointer';
      card.style.borderLeft = '4px solid ' + cat.color;
      card.addEventListener('click', function() {
        var catFilter = document.getElementById('vp-cat-filter');
        if (catFilter) {
          catFilter.value = cat.id;
          applyFilters();
          document.getElementById('vp-video-grid').scrollIntoView({ behavior: 'smooth' });
        }
      });
      grid.appendChild(card);
    });
    container.appendChild(grid);
  }

  function createVideoCard(v) {
    var cat = categories.find(function(c) { return c.id === v.category; });
    var catName = cat ? cat.icon + ' ' + cat.name : '';
    var catColor = cat ? cat.color : '#767676';

    var img = el('img', { alt: v.title, loading: 'lazy' });
    img.src = v.thumbnailUrl || '';

    var badges = el('div', { className: 'vp-card-badges' });

    if (v.category) {
      var catBadge = el('span', { className: 'vp-badge', textContent: catName });
      catBadge.style.background = catColor;
      catBadge.style.color = '#fff';
      badges.appendChild(catBadge);
    }

    if (v.level) {
      var lvBadge = el('span', { className: 'vp-badge', textContent: getLevelLabel(v.level) });
      lvBadge.style.background = getLevelColor(v.level);
      lvBadge.style.color = '#fff';
      badges.appendChild(lvBadge);
    }

    var meta = el('div', { className: 'vp-card-meta' });
    if (v.duration) meta.appendChild(el('span', { textContent: v.duration }));
    if (v.viewCount) meta.appendChild(el('span', { textContent: formatNumber(v.viewCount) + '回再生' }));

    var card = el('a', {
      className: 'card vp-video-card',
      href: 'https://www.youtube.com/watch?v=' + v.videoId,
      target: '_blank',
      rel: 'noopener'
    }, [
      el('div', { className: 'card-thumbnail' }, [img]),
      el('div', { className: 'card-content' }, [
        badges,
        el('h3', { textContent: v.title }),
        v.summary ? el('p', { className: 'vp-card-summary', textContent: v.summary }) : null,
        meta
      ])
    ]);

    return card;
  }

  function renderVideos() {
    var grid = document.getElementById('vp-video-grid');
    if (!grid) return;

    var start = currentPage * PAGE_SIZE;
    var end = start + PAGE_SIZE;
    var batch = filteredVideos.slice(start, end);

    batch.forEach(function(v) {
      grid.appendChild(createVideoCard(v));
    });

    renderLoadMore();
  }

  function renderLoadMore() {
    var area = document.getElementById('vp-load-more-area');
    if (!area) return;
    area.textContent = '';

    var shown = Math.min((currentPage + 1) * PAGE_SIZE, filteredVideos.length);
    var total = filteredVideos.length;

    if (shown < total) {
      var btn = el('button', {
        className: 'vp-load-more-btn',
        textContent: 'もっと見る（残り' + (total - shown) + '本）'
      });
      btn.addEventListener('click', function() {
        currentPage++;
        renderVideos();
      });
      area.appendChild(btn);
    }

    var info = el('div', { className: 'vp-shown-info', textContent: shown + ' / ' + total + '本 表示中' });
    area.appendChild(info);
  }

  function applyFilters() {
    var searchVal = (document.getElementById('vp-search').value || '').toLowerCase();
    var catVal = document.getElementById('vp-cat-filter').value;
    var levelVal = document.getElementById('vp-level-filter').value;
    var sortVal = document.getElementById('vp-sort').value;

    filteredVideos = allVideos.filter(function(v) {
      if (catVal && v.category !== catVal) return false;
      if (levelVal && v.level !== levelVal) return false;
      if (searchVal) {
        var text = ((v.title || '') + ' ' + (v.summary || '') + ' ' + (v.subcategory || '') + ' ' + (v.targetAudience || '')).toLowerCase();
        if (text.indexOf(searchVal) === -1) return false;
      }
      return true;
    });

    if (sortVal === 'date-asc') {
      filteredVideos.sort(function(a, b) { return (a.publishedAt || '').localeCompare(b.publishedAt || ''); });
    } else if (sortVal === 'views-desc') {
      filteredVideos.sort(function(a, b) { return (b.viewCount || 0) - (a.viewCount || 0); });
    } else if (sortVal === 'likes-desc') {
      filteredVideos.sort(function(a, b) { return (b.likeCount || 0) - (a.likeCount || 0); });
    } else {
      filteredVideos.sort(function(a, b) { return (b.publishedAt || '').localeCompare(a.publishedAt || ''); });
    }

    currentPage = 0;
    var grid = document.getElementById('vp-video-grid');
    if (grid) grid.textContent = '';
    renderVideos();

    var countEl = document.getElementById('vp-result-count');
    if (countEl) countEl.textContent = filteredVideos.length + '本の動画が見つかりました';
  }

  function populateCatFilter() {
    var select = document.getElementById('vp-cat-filter');
    if (!select) return;
    categories.forEach(function(cat) {
      var count = allVideos.filter(function(v) { return v.category === cat.id; }).length;
      var opt = el('option', { value: cat.id, textContent: cat.icon + ' ' + cat.name + ' (' + count + ')' });
      select.appendChild(opt);
    });
  }

  function bindEvents() {
    var search = document.getElementById('vp-search');
    var catFilter = document.getElementById('vp-cat-filter');
    var levelFilter = document.getElementById('vp-level-filter');
    var sortSelect = document.getElementById('vp-sort');

    var debounceTimer;
    if (search) {
      search.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(applyFilters, 300);
      });
    }
    if (catFilter) catFilter.addEventListener('change', applyFilters);
    if (levelFilter) levelFilter.addEventListener('change', applyFilters);
    if (sortSelect) sortSelect.addEventListener('change', applyFilters);
  }

  function init() {
    Promise.all([
      fetch('/videos.json').then(function(r) { return r.json(); }),
      fetch('/categories.json').then(function(r) { return r.json(); })
    ]).then(function(results) {
      allVideos = results[0].filter(function(v) { return v.privacyStatus === 'public'; });
      categories = results[1];

      populateCatFilter();
      renderPersonas();
      renderCategories();

      filteredVideos = allVideos.slice();
      renderVideos();

      var countEl = document.getElementById('vp-result-count');
      if (countEl) countEl.textContent = allVideos.length + '本の公開動画';

      bindEvents();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>

<style>
#video-portal {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1rem;
}

#vp-header {
  text-align: center;
  margin-bottom: 2rem;
}

#vp-title {
  font-size: 2rem;
  margin: 0 0 0.5rem;
  border: none;
}

#vp-subtitle {
  color: #64748b;
  font-size: 1.05rem;
  margin: 0;
}

#vp-search-area {
  margin-bottom: 2rem;
}

#vp-search {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  outline: none;
  transition: border-color 0.3s;
  box-sizing: border-box;
  background: #fff;
}

#vp-search:focus {
  border-color: #3a7bd5;
}

#vp-filters {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

#vp-filters select {
  padding: 0.5rem 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  background: #fff;
  cursor: pointer;
  outline: none;
}

#vp-filters select:focus {
  border-color: #3a7bd5;
}

#vp-result-count {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #64748b;
}

/* Persona Section */
.vp-section-title {
  font-size: 1.3rem;
  margin: 0 0 1rem;
  color: #1e293b;
  border: none;
}

.vp-persona-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.vp-persona-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
}

.vp-persona-card:hover {
  border-color: #3a7bd5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(58, 123, 213, 0.15);
}

.vp-persona-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.vp-persona-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.vp-persona-desc {
  font-size: 0.85rem;
  color: #64748b;
}

/* Category Grid */
.vp-cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  margin-bottom: 2.5rem;
}

.vp-cat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.vp-cat-card:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transform: translateY(-1px);
}

.vp-cat-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.vp-cat-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #1e293b;
}

.vp-cat-count {
  font-size: 0.8rem;
  color: #64748b;
}

/* Video Card Extensions */
.vp-card-badges {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.vp-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.vp-card-summary {
  font-size: 0.85rem !important;
  color: #475569 !important;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.vp-card-meta {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #94a3b8;
}

/* Load More */
#vp-load-more-area {
  text-align: center;
  margin: 2rem 0;
}

.vp-load-more-btn {
  padding: 0.75rem 2rem;
  font-size: 1rem;
  background: linear-gradient(135deg, #3a7bd5 0%, #5a9bef 100%);
  color: #fff;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.vp-load-more-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(58, 123, 213, 0.4);
}

.vp-shown-info {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #94a3b8;
}

/* Back Link */
#vp-back-link {
  text-align: center;
  margin: 2rem 0 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

#vp-back-link a {
  color: #3a7bd5;
  text-decoration: none;
  font-size: 0.95rem;
}

#vp-back-link a:hover {
  text-decoration: underline;
}

/* Dark Mode */
html.dark #vp-search {
  background: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

html.dark #vp-filters select {
  background: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

html.dark #vp-subtitle,
html.dark #vp-result-count,
html.dark .vp-persona-desc,
html.dark .vp-cat-count {
  color: #94a3b8;
}

html.dark .vp-section-title,
html.dark .vp-persona-title,
html.dark .vp-cat-name {
  color: #f1f5f9;
}

html.dark .vp-persona-card,
html.dark .vp-cat-card {
  background: #1e293b;
  border-color: #334155;
}

html.dark .vp-persona-card:hover {
  border-color: #5a9bef;
}

html.dark .vp-card-summary {
  color: #94a3b8 !important;
}

html.dark #vp-back-link {
  border-top-color: #334155;
}

/* Responsive */
@media (max-width: 719px) {
  .vp-persona-grid {
    grid-template-columns: 1fr;
  }
  .vp-cat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  #vp-filters {
    flex-direction: column;
  }
  #vp-filters select {
    width: 100%;
  }
}
</style>
