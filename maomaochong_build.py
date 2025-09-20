#!/usr/bin/env python3
from pathlib import Path
import json, markdown
import re

MDFOLDER = Path("mdfiles")
OUTFILE = Path("maomaochong.html")
CHUNK = 100

md = markdown.Markdown(extensions=["extra", "codehilite"])

cards = []
for p in sorted(MDFOLDER.glob("*.md")):
    content = p.read_text(encoding="utf-8")
    html_content = md.convert(content)
    
    # Extract English and Chinese content for better search
    lines = content.strip().split('\n')
    english_text = ""
    chinese_text = ""
    
    for line in lines:
        if line.strip() and not line.startswith("翻译（简体中文）:"):
            english_text += line + " "
        elif line.startswith("翻译（简体中文）:"):
            continue
        elif line.strip() and "翻译（简体中文）:" in content:
            chinese_text += line + " "
    
    # id1：原始文件名（含前导0），id2：无前导0（便于对照）
    id_num = str(int(p.stem)) if p.stem.isdigit() else p.stem
    cards.append({
        "id": p.stem, 
        "id_num": id_num, 
        "html": html_content,
        "english": english_text.strip(),
        "chinese": chinese_text.strip()
    })
    md.reset()

chunks = [cards[i:i+CHUNK] for i in range(0, len(cards), CHUNK)]

html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>毛毛虫词汇卡片</title>
<meta name="description" content="Interactive word cards with English and Chinese translations">
<style>
* {{
  box-sizing: border-box;
}}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  margin: 0;
  background: linear-gradient(135deg, #FFFFFFFF 0%, #E1E1E1FF 100%);
  min-height: 100vh;
  color: #333;
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}}

header {{
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}}

.header-content {{
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem 0;
}}

.title-section {{
  text-align: center;
}}

h1 {{
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}

.subtitle {{
  margin: 0.5rem 0 0;
  color: #666;
  font-size: 1.1rem;
}}

.search-section {{
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}}

.search-container {{
  flex: 1;
  min-width: 300px;
  position: relative;
}}

#search {{
  width: 100%;
  padding: 1rem 1.5rem;
  font-size: 1.1rem;
  border: 2px solid #e1e5e9;
  border-radius: 50px;
  outline: none;
  transition: all 0.3s ease;
  background: white;
}}

#search:focus {{
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}}

.search-buttons {{
  display: flex;
  gap: 0.5rem;
}}

.btn {{
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 25px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}}

.btn-primary {{
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}}

.btn-primary:hover {{
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}}

.btn-secondary {{
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
}}

.btn-secondary:hover {{
  background: #e9ecef;
  transform: translateY(-1px);
}}

.stats {{
  display: flex;
  gap: 2rem;
  justify-content: center;
  margin-top: 1rem;
  flex-wrap: wrap;
}}

.stat {{
  text-align: center;
  padding: 0.5rem 1rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 15px;
  min-width: 100px;
}}

.stat-number {{
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}}

.stat-label {{
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.25rem;
}}

main {{
  padding: 2rem 0;
  min-height: 60vh;
}}

#cards {{
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}}

.card {{
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}}

.card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea, #764ba2);
}}

.card:hover {{
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}}

.card-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f8f9fa;
}}

.card-id {{
  font-size: 1.1rem;
  font-weight: 700;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 15px;
}}

.card-content {{
  line-height: 1.6;
}}

.card-content p {{
  margin: 0 0 1rem;
  font-size: 1.1rem;
}}

.card-content p:last-child {{
  margin-bottom: 0;
}}

.translation {{
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 10px;
  border-left: 4px solid #667eea;
  margin-top: 1rem;
}}

.no-results {{
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}}

.no-results-icon {{
  font-size: 4rem;
  margin-bottom: 1rem;
}}

.no-results h3 {{
  margin: 0 0 1rem;
  font-size: 1.5rem;
  color: #333;
}}

.no-results p {{
  margin: 0;
  font-size: 1.1rem;
}}

.loading {{
  text-align: center;
  padding: 2rem;
  color: #666;
}}

.loading::after {{
  content: '';
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-left: 10px;
}}

@keyframes spin {{
  0% {{ transform: rotate(0deg); }}
  100% {{ transform: rotate(360deg); }}
}}

@media (max-width: 768px) {{
  .container {{
    padding: 0 15px;
  }}
  
  h1 {{
    font-size: 2rem;
  }}
  
  .search-section {{
    flex-direction: column;
  }}
  
  .search-container {{
    min-width: auto;
  }}
  
  #cards {{
    grid-template-columns: 1fr;
  }}
  
  .card {{
    padding: 1.5rem;
  }}
  
  .stats {{
    gap: 1rem;
  }}
  
  .stat {{
    min-width: 80px;
  }}
}}

@media (max-width: 480px) {{
  .header-content {{
    padding: 1rem 0;
  }}
  
  h1 {{
    font-size: 1.8rem;
  }}
  
  .subtitle {{
    font-size: 1rem;
  }}
  
  #search {{
    padding: 0.8rem 1.2rem;
    font-size: 1rem;
  }}
  
  .btn {{
    padding: 0.6rem 1.2rem;
    font-size: 0.8rem;
  }}
}}
</style>
</head>
<body>
<header>
  <div class="container">
    <div class="header-content">
      <div class="title-section">
        <h1>📚 Word Cards</h1>
        <p class="subtitle">毛毛虫词汇卡片 - 英语启蒙助手</p>
      </div>
      
      <div class="search-section">
        <div class="search-container">
          <input id="search" type="text" placeholder="输入编号 (比如: 1936) 或者内容 (比如: 特斯拉)">
        </div>
        <div class="search-buttons">
          <button class="btn btn-primary" onclick="showRandomCard()">🎲 随机卡片</button>
          <button class="btn btn-secondary" onclick="clearSearch()">🗑️ 清空</button>
        </div>
      </div>
      
      <div class="stats">
        <div class="stat">
          <div class="stat-number">{len(cards)}</div>
          <div class="stat-label">总卡片数</div>
        </div>
        <div class="stat">
          <div class="stat-number" id="displayed-count">0</div>
          <div class="stat-label">已显示</div>
        </div>
      </div>
    </div>
  </div>
</header>

<main>
  <div class="container">
    <div id="cards"></div>
    <div id="no-results" class="no-results" style="display: none;">
      <div class="no-results-icon">🔍</div>
      <h3>未找到匹配的卡片</h3>
      <p>请尝试输入不同的数字编号 (比如: 1936) 或者内容 (比如: 特斯拉)，或点击"随机卡片"按钮</p>
    </div>
  </div>
</main>

<script>
const CHUNK_SIZE = {CHUNK};
const CHUNKS = {json.dumps(chunks, ensure_ascii=False, separators=(',',':'))};
const ALL_CARDS = {json.dumps(cards, ensure_ascii=False, separators=(',',':'))};

const main = document.getElementById("cards");
const searchBox = document.getElementById("search");
const noResults = document.getElementById("no-results");
const displayedCount = document.getElementById("displayed-count");
const searchTime = document.getElementById("search-time");

let searchTimeout;

// Initialize
updateDisplayedCount(0);

searchBox.addEventListener("input", function() {{
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(doSearch, 150); // Debounce search
}});

searchBox.addEventListener("keypress", function(e) {{
  if (e.key === 'Enter') {{
    doSearch();
  }}
}});

function doSearch() {{
  const startTime = performance.now();
  const query = searchBox.value.trim();
  
  main.innerHTML = "";
  noResults.style.display = "none";
  
  if (!query) {{
    updateDisplayedCount(0);
    updateSearchTime(0);
    return;
  }}
  
  // Enhanced search: supports both exact ID and partial text search
  const results = searchCards(query);
  
  if (results.length === 0) {{
    noResults.style.display = "block";
    updateDisplayedCount(0);
  }} else {{
    results.forEach(card => render(card));
    updateDisplayedCount(results.length);
  }}
  
  const endTime = performance.now();
  updateSearchTime(Math.round(endTime - startTime));
}}

function searchCards(query) {{
  const results = [];
  const normalizedQuery = query.toLowerCase();
  
  // First try exact ID match
  const exactMatch = ALL_CARDS.find(card => 
    card.id === query || card.id_num === query.replace(/^0+/, '') || query.replace(/^0+/, '') === "0"
  );
  
  if (exactMatch) {{
    return [exactMatch];
  }}
  
  // Then try partial text search
  for (const card of ALL_CARDS) {{
    if (card.english.toLowerCase().includes(normalizedQuery) || 
        card.chinese.toLowerCase().includes(normalizedQuery) ||
        card.id.includes(query) ||
        card.id_num.includes(query)) {{
      results.push(card);
    }}
  }}
  
  return results;
}}

function render(card) {{
  const div = document.createElement("div");
  div.className = "card";
  
  const englishContent = card.html.split('<p>翻译（简体中文）:')[0];
  const chineseContent = card.html.split('<p>翻译（简体中文）:')[1] || '';
  
  div.innerHTML = `
    <div class="card-header">
      <div class="card-id">P` + card.id + `</div>
    </div>
    <div class="card-content">
      ` + englishContent + `
      ` + (chineseContent ? `<div class="translation">` + chineseContent + `</div>` : '') + `
    </div>
  `;
  
  main.appendChild(div);
}}

function showRandomCard() {{
  const randomCard = ALL_CARDS[Math.floor(Math.random() * ALL_CARDS.length)];
  searchBox.value = randomCard.id;
  doSearch();
}}

function clearSearch() {{
  searchBox.value = "";
  doSearch();
}}

function updateDisplayedCount(count) {{
  displayedCount.textContent = count;
}}

function updateSearchTime(time) {{
  searchTime.textContent = time;
}}

// Add some keyboard shortcuts
document.addEventListener('keydown', function(e) {{
  if (e.ctrlKey || e.metaKey) {{
    switch(e.key) {{
      case 'k':
        e.preventDefault();
        searchBox.focus();
        break;
      case 'r':
        e.preventDefault();
        showRandomCard();
        break;
    }}
  }}
}});

// Show welcome message on first load
window.addEventListener('load', function() {{
  if (searchBox.value === '') {{
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'no-results';
    welcomeDiv.innerHTML = `
      <div class="no-results-icon">👋</div>
      <h3>欢迎使用毛毛虫词汇卡片！</h3>
      <p>在搜索框中输入数字编号 (比如: 1936) 或者内容 (比如: 特斯拉) 开始浏览，或点击"随机卡片"按钮探索内容</p>
    `;
    main.appendChild(welcomeDiv);
  }}
}});
</script>
</body></html>
"""

OUTFILE.write_text(html_doc, encoding="utf-8")
print(f"✅ 生成完毕 → {OUTFILE.resolve()}")
print(f"📊 共处理 {len(cards)} 张卡片，分为 {len(chunks)} 个数据块")
