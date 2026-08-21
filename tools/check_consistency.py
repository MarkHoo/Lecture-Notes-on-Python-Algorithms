#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一致性检查: 附录B 对照表 <-> 各章"覆盖题号"行 <-> 各章实际 "### N. 题名" 小节。

用法:
    python tools/check_consistency.py

检查项:
1. 附录 B 中标注的章节, 该章节文件里必须存在对应题号的小节标题 (### N.)。
2. 各章"覆盖题号"行里的题号, 该文件里必须存在对应小节 (ch01 为分析样例, 跳过)。
3. 章节里出现的小节题号, 若 <= 400 且不属于数据库/Shell, 附录 B 中必须有一行。
4. 附录 B 中数据库/Shell 题不应出现在任何章节小节里。
"""
import glob
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPENDIX_B = os.path.join(ROOT, "附录B-LeetCode前400题对照表.md")

HEADING_RE = re.compile(r"^### (\d+)\.", re.M)
COVER_RE = re.compile(r"^> 覆盖题号：([^\n]+)", re.M)
ROW_RE = re.compile(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", re.M)
# 扩展阅读小节标题形如 "## 5.8 扩展阅读：302. 题名" 或 "## 7.8 扩展阅读：369 题名"
EXT_RE = re.compile(r"扩展阅读[：:]\s*(\d{1,4})")

DB_SHELL = {"175", "176", "177", "178", "180", "181", "182", "183", "184", "185",
            "192", "193", "194", "195", "196", "197", "262"}


def chapter_files():
    return sorted(glob.glob(os.path.join(ROOT, "ch*.md")))


def headings_of(text):
    """H3 小节题号 (### N.) 与扩展阅读标题中的题号 (## X.8 扩展阅读：N.)"""
    hs = {int(m.group(1)) for m in HEADING_RE.finditer(text)}
    hs |= {int(m.group(1)) for m in EXT_RE.finditer(text)}
    return hs


def cover_line_of(text):
    m = COVER_RE.search(text)
    if not m:
        return None
    return {int(x) for x in re.findall(r"\d+", m.group(1))}


def parse_appendix():
    """返回 {题号: {"title":..., "chapter": 章节单元格文本}}"""
    with open(APPENDIX_B, "r", encoding="utf-8") as f:
        text = f.read()
    rows = {}
    for m in ROW_RE.finditer(text):
        n = int(m.group(1))
        if n < 1 or n > 400:
            continue
        rows[n] = {"title": m.group(2).strip(), "chapter": m.group(5).strip()}
    return rows


def main():
    appendix = parse_appendix()
    errors = []
    infos = []

    # 预收集: 各章实际小节 -> 题号集合
    ch_heading = {}
    ch_cover = {}
    for path in chapter_files():
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        name = os.path.basename(path)
        ch_heading[name] = headings_of(text)
        ch_cover[name] = cover_line_of(text)

    # 检查 1: 附录B 引用的章节必须有对应小节
    for n, info in sorted(appendix.items()):
        cell = info["chapter"]
        if cell in ("数据库题（不展开）", "Shell 题（不展开）", "—"):
            continue
        refs = re.findall(r"ch(\d+)", cell)
        for r in refs:
            fname = "ch%02d" % int(r)
            # 找到对应的章节文件
            matches = [k for k in ch_heading if k.startswith(fname + "-")]
            if not matches:
                errors.append("附录B 题 %d 引用 %s, 但文件不存在" % (n, fname))
                continue
            if n not in ch_heading[matches[0]]:
                errors.append("附录B 题 %d(%s) 引用 %s, 但该章没有 '### %d.' 小节"
                              % (n, info["title"], fname, n))

    # 检查 2: 各章覆盖行里的题号必须有小节 (ch01 除外)
    for name, cover in ch_cover.items():
        if cover is None or name.startswith("ch01"):
            continue
        for n in sorted(cover):
            if n not in ch_heading[name]:
                errors.append("%s 覆盖行含题 %d, 但文件内没有 '### %d.' 小节" % (name, n, n))

    # 检查 3+4: 章节小节 vs 附录B
    for name, heads in ch_heading.items():
        for n in sorted(heads):
            if n > 400:
                infos.append("%s 含超范围扩展题 %d (附录B不收录, 符合预期)" % (name, n))
                continue
            if str(n) in DB_SHELL:
                errors.append("%s 含数据库/Shell 题 %d, 不应展开" % (name, n))
                continue
            if n not in appendix:
                errors.append("%s 含题 %d, 但附录B 无此行" % (name, n))

    print("附录B 行数: %d" % len(appendix))
    print("章节文件: %d 个" % len(chapter_files()))
    print("-" * 60)
    if infos:
        for i in infos:
            print("[提示] " + i)
    if errors:
        print("发现 %d 个不一致:" % len(errors))
        for e in errors:
            print("  [错误] " + e)
        sys.exit(1)
    print("三方一致性检查通过: 附录B <-> 覆盖行 <-> 章节小节 完全对齐!")


if __name__ == "__main__":
    main()
