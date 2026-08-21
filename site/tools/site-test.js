// 网站逻辑真实验证脚本（Node）：渲染全部章节 + 搜索 + 高亮 + 锚点一致性
const fs = require('fs');
const path = require('path');

const SITE = path.join(__dirname, '..');
global.window = global;

// 加载数据
const dataDir = path.join(SITE, 'data');
const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.js'));
files.forEach(f => eval(fs.readFileSync(path.join(dataDir, f), 'utf8')));
const dataCount = Object.keys(global.BOOK_DATA || {}).length;
console.log('数据章节数:', dataCount);

// 加载 JS 模块
eval(fs.readFileSync(path.join(SITE, 'js', 'highlight.js'), 'utf8'));
eval(fs.readFileSync(path.join(SITE, 'js', 'markdown.js'), 'utf8'));
eval(fs.readFileSync(path.join(SITE, 'js', 'search.js'), 'utf8'));

let fail = 0;

// 0) index.html 引用的 data 文件与目录一致
console.log('\n=== index.html 数据引用检查 ===');
const html = fs.readFileSync(path.join(SITE, 'index.html'), 'utf8');
const refs = [...html.matchAll(/src="data\/([^"]+)"/g)].map(m => m[1]).sort();
const onDisk = files.sort();
if (JSON.stringify(refs) !== JSON.stringify(onDisk)) {
  console.log('  ✗ index.html 引用的 data 文件与磁盘不一致');
  console.log('    引用:', refs);
  console.log('    磁盘:', onDisk);
  fail++;
} else {
  console.log('  ✓ index.html 引用 ' + refs.length + ' 个 data 文件，与磁盘一致');
}
if (dataCount !== 32) { console.log('  ✗ 数据章节数应为 32，实际 ' + dataCount); fail++; }

// 1) 渲染全部章节
console.log('\n=== 渲染测试 ===');
for (const k of Object.keys(global.BOOK_DATA)) {
  try {
    const r = global.Markdown.render(global.BOOK_DATA[k]);
    const opens = (r.html.match(/<pre(?:\s|>)/g) || []).length;
    const closes = (r.html.match(/<\/pre>/g) || []).length;
    const tbl = (r.html.match(/<table>/g) || []).length;
    const tblClose = (r.html.match(/<\/table>/g) || []).length;
    if (!r.html.trim()) throw new Error('渲染为空');
    if (opens !== closes) throw new Error('pre 不配对: ' + opens + '/' + closes);
    if (tbl !== tblClose) throw new Error('table 不配对: ' + tbl + '/' + tblClose);
    console.log('  ✓', k, '(' + r.html.length + ' 字符, 小节数=' + r.headings.length + ')');
  } catch (e) {
    fail++;
    console.log('  ✗', k, '→', e.message);
  }
}

// 2) 搜索测试（按本书内容设计关键词 → 预期章节）
console.log('\n=== 搜索测试 ===');
global.Search.buildIndex();
const tests = [
  ['二分', 'ch05'],
  ['滑动窗口', 'ch04'],
  ['KMP', 'ch21'],
  ['背包', 'ch18'],
  ['蓄水池', 'ch26'],
  ['单调栈', 'ch09'],
  ['拓扑排序', 'ch20'],
];
for (const [q, expectKey] of tests) {
  const res = global.Search.search(q);
  const hitExpect = res.some(r => r.key.indexOf(expectKey) === 0);
  console.log('  搜索「' + q + '」→', res.length, '条命中' + (hitExpect ? '（含' + expectKey + ' ✓）' : '（缺预期章节 ✗）'));
  if (!res.length || !hitExpect) fail++;
}
// 多关键词 AND
const multi = global.Search.search('动态规划 背包');
console.log('  搜索「动态规划 背包」→', multi.length, '条命中（AND 语义）');
if (!multi.length) fail++;

// 3) 高亮测试
console.log('\n=== 高亮测试 ===');
const hl = global.Highlighter.highlight('def binary_search(nums, target):  # 注释\n    return mid  # 42', 'python');
console.log('  python 高亮含 span:', hl.includes('<span'));
if (!hl.includes('<span')) fail++;

// 4) 列表渲染测试
console.log('\n=== 列表渲染测试 ===');
function count(html, tag) { return (html.match(new RegExp('<' + tag + '( |>|$)', 'g')) || []).length; }
const nestedMd = '- 一级项 A\n  - 二级项 A1\n  - 二级项 A2\n- 一级项 B\n1. 有序一\n2. 有序二';
const nl = global.Markdown.render(nestedMd).html;
const ulOpen = count(nl, 'ul'), ulClose = count(nl, '/ul');
const liOpen = count(nl, 'li'), liClose = count(nl, '/li');
const olOpen = count(nl, 'ol'), olClose = count(nl, '/ol');
console.log('  嵌套列表 ul:', ulOpen, '/', ulClose, ' ol:', olOpen, '/', olClose, ' li:', liOpen, '/', liClose);
if (ulOpen !== ulClose || olOpen !== olClose || liOpen !== liClose || ulOpen !== 2 || olOpen !== 1 || liOpen !== 6) {
  console.log('  ✗ 列表结构异常:', nl);
  fail++;
} else {
  console.log('  ✓ 列表结构正确');
}
// 真实章节列表检查（ch14 回溯含大量嵌套列表）
const ch14 = global.Markdown.render(global.BOOK_DATA['ch14-回溯算法']).html;
if (count(ch14, 'ul') !== count(ch14, '/ul') || count(ch14, 'li') !== count(ch14, '/li')) {
  console.log('  ✗ ch14 列表不配对');
  fail++;
} else {
  console.log('  ✓ ch14 列表配对正确（ul=' + count(ch14, 'ul') + ', li=' + count(ch14, 'li') + '）');
}

// 5) 锚点一致性测试：渲染各章 h2 id 与 main.js slug 算法对比（跳过代码块内的 ##）
console.log('\n=== 锚点一致性测试 ===');
function slugifyJS(text) {
  return 'sec-' + text.replace(/[^\w\u4e00-\u9fa5]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60);
}
let anchorFail = 0, anchorTotal = 0;
for (const k of Object.keys(global.BOOK_DATA)) {
  const md = global.BOOK_DATA[k];
  const rendered = global.Markdown.render(md);
  const mdNoCode = md.replace(/```[\s\S]*?```/g, '');
  const re = /^##\s+(.+)$/gm;
  let m2;
  while ((m2 = re.exec(mdNoCode)) !== null) {
    anchorTotal++;
    const title = m2[1].replace(/\s*★+.*$/, '').trim();
    const slug = slugifyJS(title);
    if (!rendered.html.includes('id="' + slug + '"')) {
      console.log('  ✗ ' + k + ' 缺锚点: ' + title + ' → ' + slug);
      anchorFail++;
    }
  }
}
console.log('  锚点检查: ' + anchorTotal + ' 个 h2, ' + (anchorFail === 0 ? '全部一致 ✓' : anchorFail + ' 处不一致 ✗'));
if (anchorFail) fail += anchorFail;

// 6) 公式渲染测试
console.log('\n=== 公式渲染测试 ===');
const mathMd = '复杂度为 $O(n \\log n)$，递推式：\n\n$$dp[i] = dp[i-1] + dp[i-2]$$';
const mathHtml = global.Markdown.render(mathMd).html;
const mathCount = (mathHtml.match(/class="math"/g) || []).length;
console.log('  公式 span 数量:', mathCount);
if (mathCount !== 2) { console.log('  ✗ 公式渲染异常:', mathHtml); fail++; }
else console.log('  ✓ 行内公式与块级公式渲染正确');

// 7) Mermaid 块渲染测试：lang=mermaid 的块应输出 <pre class="mermaid">
console.log('\n=== Mermaid 块渲染测试 ===');
const mmd = '## 图\n\n```mermaid\nflowchart TD\n    A --> B\n```\n';
const mmdHtml = global.Markdown.render(mmd).html;
if (mmdHtml.includes('<pre class="mermaid">') && mmdHtml.includes('</pre>')) {
  console.log('  ✓ mermaid 块渲染为 <pre class="mermaid">');
} else {
  console.log('  ✗ mermaid 块渲染异常:', mmdHtml);
  fail++;
}
let mermaidCount = 0;
for (const k of Object.keys(global.BOOK_DATA)) {
  mermaidCount += (global.Markdown.render(global.BOOK_DATA[k]).html.match(/<pre class="mermaid">/g) || []).length;
}
console.log('  全书 mermaid 图数量:', mermaidCount);
if (mermaidCount !== 6) { console.log('  ✗ 应为 6 个 mermaid 图'); fail++; }
else console.log('  ✓ 6 个 mermaid 图全部就位');

console.log('\n' + (fail === 0 ? '✅ 全部测试通过' : '❌ 失败项: ' + fail));
process.exit(fail === 0 ? 0 : 1);
