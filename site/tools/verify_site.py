# -*- coding: utf-8 -*-
"""站点完整性自检：文件结构、数据文件、关键引用
用法: python site/tools/verify_site.py   （在项目根目录执行）
"""
import glob
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # site
ROOT = os.path.dirname(BASE)
errors = []

# 1. 必需文件
required = [
    'index.html',
    'css/style.css',
    'js/main.js', 'js/markdown.js', 'js/highlight.js', 'js/search.js',
    'tools/build_site.py', 'tools/site-test.js',
]
for r in required:
    if not os.path.isfile(os.path.join(BASE, r)):
        errors.append('缺少文件: ' + r)

# 2. 数据文件: data/*.js 应等于 32 且与 index.html 引用一致
data_files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(BASE, 'data', '*.js')))
if len(data_files) != 32:
    errors.append('data 文件数应为 32, 实际 %d' % len(data_files))
with open(os.path.join(BASE, 'index.html'), encoding='utf-8') as f:
    html = f.read()
refs = sorted(re.findall(r'src="data/([^"]+)"', html))
if refs != data_files:
    errors.append('index.html 数据引用与磁盘不一致')

# 3. 章节源文件存在（build_site.py 的 CHAPTER_FILES）
with open(os.path.join(BASE, 'tools', 'build_site.py'), encoding='utf-8') as f:
    build_src = f.read()
for m in re.finditer(r"'([\w\u4e00-\u9fa5.-]+\.md)'", build_src):
    if not os.path.isfile(os.path.join(ROOT, m.group(1))):
        errors.append('章节源文件缺失: ' + m.group(1))

# 4. 数据文件必须可被 JS 解析（简单语法检查：window.BOOK_DATA 赋值结构）
for f in data_files:
    with open(os.path.join(BASE, 'data', f), encoding='utf-8') as fh:
        content = fh.read()
    if not content.startswith('window.BOOK_DATA = window.BOOK_DATA || {};'):
        errors.append('数据文件格式异常: ' + f)
    if not content.rstrip().endswith("';"):
        errors.append('数据文件未以引号字符串结尾: ' + f)

if errors:
    print('❌ 站点自检失败 %d 项:' % len(errors))
    for e in errors:
        print('  ' + e)
    sys.exit(1)
print('✅ 站点自检通过: %d 个数据文件, 结构完整' % len(data_files))
