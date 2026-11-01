// ===== LitSeek 静态演示站点 - 浏览器本地检索 =====

// 18 条示例语料（来自 data/sample_docs.jsonl）
const SAMPLE_DOCS = [
  {"title": "LSM 树与写优化笔记", "source": "note", "topic": "database", "text": "课程笔记：LSM 树把写入先落到内存表和 redo log，后台再把有序片段合并到磁盘，适合写多读少的场景；B+ 树则更适合频繁随机读。"},
  {"title": "事务隔离级别梳理", "source": "note", "topic": "database", "text": "事务隔离级别由低到高是读未提交、读已提交、可重复读、串行化，分别解决脏读、不可重复读和幻读问题；关系型数据库默认级别需要结合业务一致性要求选择。"},
  {"title": "OceanBase 分布式架构要点", "source": "paper", "topic": "database", "text": "OceanBase 是一款分布式关系型数据库，采用多副本 Paxos 复制保证高可用，支持水平扩展与强一致事务，存储层基于 LSM 结构组织数据，适合核心交易系统的在线处理。"},
  {"title": "索引与查询计划实验记录", "source": "lab", "topic": "database", "text": "实验记录：为大表增加合适的二级索引后，等值查询耗时明显下降；但索引会拖慢写入，需要在读写比例之间权衡。本次对比了全表扫描、主键索引和联合索引三种计划。"},
  {"title": "检索增强生成 RAG 综述", "source": "paper", "topic": "rag", "text": "检索增强生成系统先把文档切分成片段，为每个片段生成向量存入向量数据库；用户提问时先做语义检索召回相关上下文，再交给大模型据此生成答案，从而降低幻觉并保留可追溯的出处。"},
  {"title": "RAG 落地踩坑笔记", "source": "note", "topic": "rag", "text": "课程笔记：RAG 效果取决于切片粒度、检索召回质量和上下文拼装方式；切片过长会稀释相关性，过短又会丢失上下文。检索阶段最好同时结合语义相似度和关键词匹配。"},
  {"title": "实验记录：RAG 召回率对比", "source": "lab", "topic": "rag", "text": "实验记录：分别测试纯向量检索、纯关键词检索和混合检索在二十个问题上的召回表现，混合方式在专有名词和口语化提问上都更稳，RRF 融合排序比单路加权更不容易被某一路带偏。"},
  {"title": "知识库问答资料整理", "source": "book", "topic": "rag", "text": "企业知识库问答通常包含文档解析、分段、向量化、索引构建、检索和答案生成几个环节；维护阶段需要处理文档更新、过期片段删除以及新增资料的增量入库。"},
  {"title": "向量相似度检索方法", "source": "paper", "topic": "vector-search", "text": "向量相似度检索先用嵌入模型把文本映射为高维向量，再用余弦距离或欧氏距离衡量相近程度；近似最近邻索引在大规模语料上以少量精度损失换取更快的检索速度。"},
  {"title": "嵌入模型选型笔记", "source": "note", "topic": "vector-search", "text": "课程笔记：嵌入模型决定向量空间的语义表达能力，中英文混合场景要关注模型对中文短语和专业术语的区分度；检索前统一做归一化，能让余弦相似度比较更稳定。"},
  {"title": "实验记录：IVF 与 HNSW 对比", "source": "lab", "topic": "vector-search", "text": "实验记录：IVF_FLAT 通过聚类分桶缩小候选范围，构建快、内存占用低；HNSW 图索引查询更平滑，但构建成本更高。小数据集上两者差距不大，规模增大后召回与延迟差异才明显。"},
  {"title": "倒排索引与全文检索", "source": "book", "topic": "vector-search", "text": "全文检索基于倒排索引，先对文档分词建立词项到文档的映射；查询时把检索词分词后匹配倒排链，再按词频、位置和文档长度计算相关性得分，适合精确术语命中。"},
  {"title": "中文分词与 IK 词典", "source": "note", "topic": "nlp", "text": "中文没有天然空格，全文检索必须先分词；IK 分词器支持细粒度和智能模式，专有名词和领域新词需要补充自定义词典，否则会被错误切分，影响关键词召回。"},
  {"title": "文本向量化原理", "source": "paper", "topic": "nlp", "text": "现代文本嵌入模型基于 Transformer 编码器，经过预训练和对比学习，让语义相近的句子在向量空间中彼此靠近；句向量通常由 token 向量池化得到，并做归一化处理。"},
  {"title": "实验记录：分词错误案例", "source": "lab", "topic": "nlp", "text": "实验记录：观察到若干领域术语被切成无意义单字组合，导致全文检索漏召；补充自定义词典后，术语查询的命中率明显提升，说明分词质量直接决定检索上限。"},
  {"title": "机器学习评估指标笔记", "source": "note", "topic": "machine-learning", "text": "课程笔记：分类问题常用精确率、召回率和 F1 值评估；检索系统可以用召回率、平均倒数排名和命中率衡量，只看排序靠前的几条结果容易高估系统表现。"},
  {"title": "过拟合与正则化资料", "source": "book", "topic": "machine-learning", "text": "模型在训练集上表现好但在新数据上变差称为过拟合；常见缓解手段包括增加数据、正则化、早停、丢弃法和交叉验证，选择模型时应在独立验证集上比较泛化能力。"},
  {"title": "周报与实验记录整理模板", "source": "note", "topic": "workflow", "text": "工作流笔记：周报应汇总本周完成事项、遇到的问题和下周计划；实验记录要写清目的、环境、参数、结果和结论，方便后续回溯；资料分散在聊天记录和文档里时，统一入库检索能显著节省整理时间。"}
];

// 语义模式：主题与同义词/相关词映射（演示用）
const SEMANTIC_GROUPS = {
  "rag": ["检索增强", "RAG", "知识库", "问答", "幻觉", "上下文", "切片", "召回"],
  "vector-search": ["向量", "嵌入", "相似度", "余弦", "距离", "IVF", "HNSW", "索引", "近似", "最近邻"],
  "nlp": ["分词", "IK", "中文", "词典", "Transformer", "token", "向量化", "术语"],
  "database": ["事务", "索引", "LSM", "分布式", "数据库", "Paxos", "OceanBase", "隔离", "查询"],
  "machine-learning": ["机器学习", "评估", "精确率", "召回率", "F1", "过拟合", "正则化", "交叉验证"],
  "workflow": ["周报", "实验记录", "模板", "工作流", "整理"]
};

let currentMode = 'hybrid';
let currentResults = [];

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
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
}

// ===== 搜索 =====
function doSearch() {
  const query = document.getElementById('searchInput').value.trim();
  if (!query) {
    showError('请输入检索关键词或问题');
    return;
  }

  const topK = parseInt(document.getElementById('topKSelect').value);
  const topic = document.getElementById('topicFilter').value || null;
  const source = document.getElementById('sourceFilter').value || null;

  // 过滤
  let docs = SAMPLE_DOCS;
  if (topic) docs = docs.filter(d => d.topic === topic);
  if (source) docs = docs.filter(d => d.source === source);

  let results;
  if (currentMode === 'vector') {
    results = searchVector(query, docs, topK);
  } else if (currentMode === 'fulltext') {
    results = searchFulltext(query, docs, topK);
  } else {
    results = searchHybrid(query, docs, topK);
  }

  renderResults({ mode: currentMode, query, total: results.length, results }, query);
}

// 关键词检索（演示性：按查询词在标题/正文中的出现次数与位置评分）
function searchFulltext(query, docs, topK) {
  const terms = query.split(/\s+/).filter(t => t.length > 0);
  const scored = docs.map(doc => {
    const text = (doc.title + ' ' + doc.text).toLowerCase();
    let score = 0;
    let firstPos = Infinity;
    terms.forEach(term => {
      const lowerTerm = term.toLowerCase();
      const count = (text.match(new RegExp(lowerTerm, 'g')) || []).length;
      score += count * 10;
      const pos = text.indexOf(lowerTerm);
      if (pos >= 0 && pos < firstPos) firstPos = pos;
    });
    // 位置越靠前得分越高
    if (firstPos < Infinity) score += (1000 - firstPos) * 0.1;
    return { ...doc, ft_score: score > 0 ? score : null };
  }).filter(d => d.ft_score > 0);

  scored.sort((a, b) => b.ft_score - a.ft_score);
  return scored.slice(0, topK).map((d, i) => ({
    ...d,
    id: i,
    distance: null,
    vector_rank: null,
    fulltext_rank: i,
    rank: i,
    score: null
  }));
}

// 语义检索（演示性：基于主题与同义词匹配，给出演示距离）
function searchVector(query, docs, topK) {
  const queryLower = query.toLowerCase();
  const scored = docs.map(doc => {
    let matchScore = 0;
    // 检查查询词与主题同义词的匹配
    for (const [topic, synonyms] of Object.entries(SEMANTIC_GROUPS)) {
      if (doc.topic === topic) {
        synonyms.forEach(syn => {
          if (queryLower.includes(syn.toLowerCase()) || syn.toLowerCase().includes(queryLower)) {
            matchScore += 10;
          }
        });
        // 主题直接匹配
        if (queryLower.includes(topic.toLowerCase())) matchScore += 5;
      }
    }
    // 标题/正文中包含查询词
    const text = (doc.title + ' ' + doc.text).toLowerCase();
    const terms = query.split(/\s+/).filter(t => t.length > 0);
    terms.forEach(term => {
      if (text.includes(term.toLowerCase())) matchScore += 3;
    });

    // 演示距离：matchScore 越高，距离越小（0.2 ~ 0.9）
    const distance = matchScore > 0 ? Math.max(0.2, 0.9 - matchScore * 0.05) : 0.85 + Math.random() * 0.1;
    return { ...doc, distance: matchScore > 0 ? distance : null };
  }).filter(d => d.distance !== null);

  scored.sort((a, b) => a.distance - b.distance);
  return scored.slice(0, topK).map((d, i) => ({
    ...d,
    id: i,
    ft_score: null,
    vector_rank: i,
    fulltext_rank: null,
    rank: i,
    score: null
  }));
}

// 混合检索（RRF 融合）
function searchHybrid(query, docs, topK) {
  const candidateK = topK * 3;
  const vecResults = searchVector(query, docs, candidateK);
  const ftResults = searchFulltext(query, docs, candidateK);

  const k = 60;
  const combined = {};

  vecResults.forEach((r, rank) => {
    combined[r.title] = {
      ...r,
      ft_score: null,
      vector_rank: rank,
      fulltext_rank: null,
      rrf: 1.0 / (k + rank + 1)
    };
  });

  ftResults.forEach((r, rank) => {
    if (combined[r.title]) {
      combined[r.title].ft_score = r.ft_score;
      combined[r.title].fulltext_rank = rank;
      combined[r.title].rrf += 1.0 / (k + rank + 1);
    } else {
      combined[r.title] = {
        ...r,
        distance: null,
        vector_rank: null,
        fulltext_rank: rank,
        rrf: 1.0 / (k + rank + 1)
      };
    }
  });

  const sorted = Object.values(combined).sort((a, b) => b.rrf - a.rrf).slice(0, topK);
  return sorted.map((r, i) => ({
    ...r,
    rank: i,
    score: r.rrf
  }));
}

// ===== 渲染结果 =====
function renderResults(data, query) {
  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('errorState').style.display = 'none';
  document.getElementById('demoNotice').style.display = 'block';

  const header = document.getElementById('resultsHeader');
  header.style.display = 'flex';
  document.getElementById('resultsCount').textContent = `找到 ${data.total} 条结果`;
  document.getElementById('resultsMode').textContent = `模式：${modeLabel(data.mode)}（演示）`;

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
    if (data.mode !== 'hybrid') {
      scoreText += '（演示值）';
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
  document.getElementById('demoNotice').style.display = 'none';
  const err = document.getElementById('errorState');
  err.textContent = msg;
  err.style.display = 'block';
}

function modeLabel(mode) {
  return { hybrid: '混合检索', vector: '语义检索', fulltext: '关键词检索' }[mode] || mode;
}

// ===== 工具函数 =====
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
    const re = new RegExp(`(${term.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&')})`, 'gi');
    result = result.replace(re, '<mark>$1</mark>');
  });
  return result;
}
