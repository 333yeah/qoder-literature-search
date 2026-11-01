// LitSeek 前端逻辑
const API = {
  health: () => fetch('/api/health').then(r => r.json()),
  stats: () => fetch('/api/stats').then(r => r.json()),
  documents: (limit = 50) => fetch(`/api/documents?limit=${limit}`).then(r => r.json()),
  search: (body) => fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(r => r.json()),
  addDocument: (body) => fetch('/api/documents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(r => r.json()),
  deleteDocument: (id) => fetch(`/api/documents/${id}`, { method: 'DELETE' }).then(r => r.json()),
};

let currentMode = 'hybrid';

// --- 初始化 ---
document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  loadStats();
  loadDocuments();
  bindEvents();
});

function bindEvents() {
  document.getElementById('searchBtn').addEventListener('click', doSearch);
  document.getElementById('searchInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') doSearch();
  });

  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentMode = btn.dataset.mode;
    });
  });

  document.getElementById('addForm').addEventListener('submit', e => {
    e.preventDefault();
    addDocument();
  });

  document.getElementById('seedBtn').addEventListener('click', seedData);
  document.getElementById('refreshDocs').addEventListener('click', loadDocuments);
}

// --- 健康检查 ---
async function checkHealth() {
  const dot = document.getElementById('healthDot');
  const text = document.getElementById('healthText');
  try {
    const data = await API.health();
    if (data.seekdb === 'connected') {
      dot.className = 'dot connected';
      text.textContent = `已连接 (${data.total} chunks)`;
    } else {
      dot.className = 'dot error';
      text.textContent = '未连接';
    }
  } catch {
    dot.className = 'dot error';
    text.textContent = '连接失败';
  }
}

// --- 统计 ---
async function loadStats() {
  const el = document.getElementById('statsContent');
  try {
    const data = await API.stats();
    const topicSelect = document.getElementById('topicFilter');

    // 更新主题下拉
    const existing = topicSelect.querySelector('option[value=""]');
    topicSelect.innerHTML = '';
    topicSelect.appendChild(existing || createOption('', '全部主题'));
    Object.keys(data.by_topic).sort().forEach(t => {
      topicSelect.appendChild(createOption(t, t));
    });

    // 渲染统计
    let html = `<div class="stats-grid">`;
    html += `<div class="stat-item"><div class="label">总量</div><div class="value">${data.total}</div></div>`;
    for (const [k, v] of Object.entries(data.by_source)) {
      html += `<div class="stat-item"><div class="label">${k}</div><div class="value">${v}</div></div>`;
    }
    html += `</div>`;
    el.innerHTML = html;
  } catch {
    el.innerHTML = '<p class="muted">加载失败</p>';
  }
}

function createOption(value, text) {
  const opt = document.createElement('option');
  opt.value = value;
  opt.textContent = text;
  return opt;
}

// --- 文档列表 ---
async function loadDocuments() {
  const el = document.getElementById('docsList');
  try {
    const data = await API.documents();
    if (!data.length) {
      el.innerHTML = '<p class="muted">暂无数据</p>';
      return;
    }
    el.innerHTML = data.map(d => `
      <div class="doc-item" data-id="${d.id}">
        <span class="doc-title" title="${escHtml(d.title)}">${escHtml(d.title)}</span>
        <span class="doc-tags">
          <span class="doc-tag">${d.source}</span>
          <span class="doc-tag">${d.topic}</span>
        </span>
        <button class="delete-btn" onclick="deleteDoc('${d.id}')" title="删除">×</button>
      </div>
    `).join('');
  } catch {
    el.innerHTML = '<p class="muted">加载失败</p>';
  }
}

// --- 搜索 ---
async function doSearch() {
  const query = document.getElementById('searchInput').value.trim();
  if (!query) {
    showError('请输入检索关键词或问题');
    return;
  }

  const topK = parseInt(document.getElementById('topKSelect').value);
  const topic = document.getElementById('topicFilter').value || null;
  const source = document.getElementById('sourceFilter').value || null;

  const btn = document.getElementById('searchBtn');
  btn.disabled = true;
  btn.textContent = '检索中…';

  try {
    const data = await API.search({ query, mode: currentMode, top_k: topK, topic, source });
    renderResults(data, query);
  } catch (err) {
    showError('检索失败：' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '搜索';
  }
}

function renderResults(data, query) {
  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('errorState').style.display = 'none';
  const header = document.getElementById('resultsHeader');
  header.style.display = 'flex';
  document.getElementById('resultsCount').textContent = `找到 ${data.total} 条结果`;
  document.getElementById('resultsMode').textContent = `模式：${modeLabel(data.mode)}`;

  const list = document.getElementById('resultsList');
  if (!data.results.length) {
    list.innerHTML = '<div class="empty-state"><p>未找到匹配结果</p></div>';
    return;
  }

  list.innerHTML = data.results.map(r => {
    const ranks = [];
    if (r.vector_rank !== null && r.vector_rank !== undefined) {
      ranks.push(`<span class="rank-badge vec">语义 #${r.vector_rank + 1}</span>`);
    }
    if (r.fulltext_rank !== null && r.fulltext_rank !== undefined) {
      ranks.push(`<span class="rank-badge ft">关键词 #${r.fulltext_rank + 1}</span>`);
    }
    if (data.mode === 'hybrid') {
      ranks.push(`<span class="rank-badge rrf">RRF ${r.score?.toFixed(5) || '-'}</span>`);
    }

    let scoreText = '';
    if (r.distance !== null && r.distance !== undefined) {
      scoreText += `余弦距离: ${r.distance.toFixed(4)} `;
    }
    if (r.ft_score !== null && r.ft_score !== undefined) {
      scoreText += `全文得分: ${r.ft_score.toFixed(4)}`;
    }
    if (r.score !== null && data.mode === 'hybrid') {
      scoreText = `RRF 分数: ${r.score.toFixed(5)} ` + scoreText;
    }

    return `
      <div class="result-card">
        <div class="result-header">
          <span class="result-title">${escHtml(r.title)}</span>
          <div class="result-ranks">${ranks.join('')}</div>
        </div>
        <div class="result-tags">
          <span class="tag source">${r.source}</span>
          <span class="tag topic">${r.topic}</span>
        </div>
        <div class="result-text">${highlightText(r.text, query)}</div>
        <div class="result-score">${scoreText}</div>
      </div>
    `;
  }).join('');
}

function showError(msg) {
  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('resultsHeader').style.display = 'none';
  document.getElementById('resultsList').innerHTML = '';
  const err = document.getElementById('errorState');
  err.textContent = msg;
  err.style.display = 'block';
}

function modeLabel(mode) {
  return { hybrid: '混合检索', vector: '语义检索', fulltext: '关键词检索' }[mode] || mode;
}

// --- 新增资料 ---
async function addDocument() {
  const title = document.getElementById('addTitle').value.trim();
  const source = document.getElementById('addSource').value;
  const topic = document.getElementById('addTopic').value;
  const text = document.getElementById('addText').value.trim();
  const resultEl = document.getElementById('addResult');

  try {
    const data = await API.addDocument({ title, source, topic, text });
    resultEl.className = 'form-result success';
    resultEl.textContent = `入库成功：生成 ${data.chunks} 个片段`;
    resultEl.style.display = 'block';
    document.getElementById('addForm').reset();
    loadStats();
    loadDocuments();
    setTimeout(() => { resultEl.style.display = 'none'; }, 3000);
  } catch (err) {
    resultEl.className = 'form-result error';
    resultEl.textContent = '入库失败：' + err.message;
    resultEl.style.display = 'block';
  }
}

// --- 删除 ---
async function deleteDoc(id) {
  if (!confirm('确认删除该条目？')) return;
  try {
    await API.deleteDocument(id);
    loadDocuments();
    loadStats();
  } catch (err) {
    alert('删除失败：' + err.message);
  }
}

// --- 导入示例语料 ---
async function seedData() {
  const btn = document.getElementById('seedBtn');
  btn.disabled = true;
  btn.textContent = '导入中…';

  try {
    const resp = await fetch('/api/documents');
    if (!resp.ok) throw new Error('无法访问 API');

    // 通过后端 seed 等价逻辑：读取 sample_docs.jsonl 并逐条 POST
    // 由于前端无法直接访问文件，这里调用一个专门的 seed 接口
    // 如果不存在，则提示用户用命令行
    const seedResp = await fetch('/api/seed', { method: 'POST' });
    if (seedResp.ok) {
      const data = await seedResp.json();
      alert(`导入成功：${data.imported} 条文档，${data.chunks} 个片段`);
    } else {
      alert('请在命令行运行 python scripts/seed.py 导入示例语料');
    }
    loadStats();
    loadDocuments();
    checkHealth();
  } catch (err) {
    alert('导入失败：' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '导入示例语料';
  }
}

// --- 工具函数 ---
function escHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function highlightText(text, query) {
  if (!query) return escHtml(text);
  const escaped = escHtml(text);
  const terms = query.split(/\s+/).filter(t => t.length > 0);
  let result = escaped;
  terms.forEach(term => {
    const re = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    result = result.replace(re, '<mark>$1</mark>');
  });
  return result;
}
