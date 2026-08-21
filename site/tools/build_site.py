# -*- coding: utf-8 -*-
"""构建静态网站数据：直接读取项目根目录各章节 Markdown → site/data/*.js
用法: python site/tools/build_site.py   （在项目根目录执行）
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))  # site/tools
SITE = os.path.dirname(BASE)                        # site
BOOK = os.path.dirname(SITE)                        # 项目根目录
DATA_DIR = os.path.join(SITE, 'data')

# 章节文件（顺序即网站目录顺序）：key = 文件名去 .md
CHAPTER_FILES = [
    'README.md',
    '00-导读与使用说明.md',
    'ch01-复杂度分析.md',
    'ch02-数组基础与指针技巧.md',
    'ch03-哈希表.md',
    'ch04-双指针与滑动窗口.md',
    'ch05-二分查找.md',
    'ch06-排序算法.md',
    'ch07-链表.md',
    'ch08-栈与队列.md',
    'ch09-单调栈与单调队列.md',
    'ch10-二叉树基础与遍历.md',
    'ch11-二叉树进阶.md',
    'ch12-二叉搜索树.md',
    'ch13-堆与优先队列.md',
    'ch14-回溯算法.md',
    'ch15-贪心算法.md',
    'ch16-动态规划入门.md',
    'ch17-动态规划进阶-字符串与区间.md',
    'ch18-动态规划进阶-背包序列与股票.md',
    'ch19-图-遍历与连通性.md',
    'ch20-拓扑排序并查集与图进阶.md',
    'ch21-字符串算法.md',
    'ch22-Trie字典树.md',
    'ch23-位运算.md',
    'ch24-数学与数论.md',
    'ch25-前缀和与高级数据结构.md',
    'ch26-设计与数据流与随机化.md',
    '附录A-复杂度速查表.md',
    '附录B-LeetCode前400题对照表.md',
    '附录C-代码验证与运行指南.md',
    '附录D-中英术语表.md',
]


def js_escape(text):
    """转义为 JS 单引号字符串内容"""
    text = text.replace('\\', '\\\\')
    text = text.replace("'", "\\'")
    text = text.replace('\r', '')
    text = text.replace('\n', '\\n')
    text = text.replace('</script>', '<\\/script>')
    return text


def main():
    blocks = []
    for fname in CHAPTER_FILES:
        path = os.path.join(BOOK, fname)
        if not os.path.isfile(path):
            print('缺少章节文件:', fname)
            return 1
        with open(path, encoding='utf-8') as fh:
            blocks.append((fname[:-3], fh.read().strip()))

    # 清空旧数据
    os.makedirs(DATA_DIR, exist_ok=True)
    for f in os.listdir(DATA_DIR):
        if f.endswith('.js'):
            os.remove(os.path.join(DATA_DIR, f))

    for name, block in blocks:
        escaped = js_escape(block)
        js = "window.BOOK_DATA = window.BOOK_DATA || {};\nwindow.BOOK_DATA['%s'] = '%s';\n" % (name, escaped)
        with open(os.path.join(DATA_DIR, name + '.js'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(js)

    print('生成数据文件: %d 个' % len(blocks))
    for name, block in blocks:
        print('  %s (%d 字符)' % (name, len(block)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
