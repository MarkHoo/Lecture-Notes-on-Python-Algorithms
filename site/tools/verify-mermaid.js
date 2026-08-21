// Mermaid 语法真实验证：用 jsdom + 本地 mermaid.min.js 逐个 parse 书中的 mermaid 块
// 用法: node site/tools/verify-mermaid.js   （需先 npm.cmd install jsdom）
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.join(__dirname, '..', '..');

// jsdom 提供 DOM 环境（mermaid 的 UMD 经 CommonJS 分支 require 加载）
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  pretendToBeVisual: true, url: 'https://localhost/',
});
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.location = dom.window.location;
global.self = dom.window;
global.HTMLElement = dom.window.HTMLElement;
global.SVGElement = dom.window.SVGElement;
global.Element = dom.window.Element;

const mermaid = require(path.join(__dirname, '..', 'js', 'vendor', 'mermaid.min.js'));
mermaid.initialize({ startOnLoad: false, theme: 'neutral' });

const chapters = [
  'ch04-双指针与滑动窗口.md', 'ch10-二叉树基础与遍历.md', 'ch14-回溯算法.md',
  'ch16-动态规划入门.md', 'ch19-图-遍历与连通性.md', 'ch26-设计与数据流与随机化.md',
];
let total = 0, fail = 0;

(async () => {
  for (const fname of chapters) {
    const text = fs.readFileSync(path.join(ROOT, fname), 'utf8');
    const re = /^```mermaid\s*\n([\s\S]*?)```/gm;
    let m, idx = 0;
    while ((m = re.exec(text)) !== null) {
      total++;
      const code = m[1].trim();
      try {
        await mermaid.parse(code);
        console.log('  ✓ ' + fname + ' 第' + (++idx) + '个 mermaid 块 语法正确');
      } catch (e) {
        fail++;
        console.log('  ✗ ' + fname + ' 第' + (++idx) + '个 mermaid 块 语法错误:');
        console.log('    ' + String(e.message || e).split('\n').slice(0, 3).join('\n    '));
      }
    }
  }
  console.log('\n共 ' + total + ' 个 mermaid 块, 失败 ' + fail + ' 个');
  process.exit(fail === 0 ? 0 : 1);
})();
