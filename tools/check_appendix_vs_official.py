#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附录 B 与 LeetCode 官方数据(题号/难度/付费)比对。

用法: python tools/check_appendix_vs_official.py
依赖: tools/leetcode_problems.json (由 fetch_leetcode.py 生成)
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPENDIX = os.path.join(ROOT, "附录B-LeetCode前400题对照表.md")
OFFICIAL = os.path.join(ROOT, "tools", "leetcode_problems.json")

ROW_RE = re.compile(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", re.M)


def load_official():
    with open(OFFICIAL, "r", encoding="utf-8") as f:
        rows = json.load(f)
    return {r["id"]: r for r in rows}


def load_appendix():
    with open(APPENDIX, "r", encoding="utf-8") as f:
        text = f.read()
    rows = {}
    for m in ROW_RE.finditer(text):
        n = int(m.group(1))
        if not (1 <= n <= 400):
            continue
        rows[n] = {
            "title": m.group(2).strip(),
            "difficulty": m.group(3).strip(),
            "algo": m.group(4).strip(),
            "chapter": m.group(5).strip(),
        }
    return rows


def main():
    official = load_official()
    appendix = load_appendix()
    missing = [n for n in range(1, 401) if n not in official]
    if missing:
        print("官方数据缺少题号: %s" % missing)

    diff_errors = []
    paid_errors = []
    title_info = []
    for n, row in sorted(appendix.items()):
        off = official.get(n)
        if off is None:
            continue
        # 难度比对
        if row["difficulty"] != off["difficulty"]:
            diff_errors.append("题 %d %s: 附录=%s, 官方=%s" % (
                n, off["title"], row["difficulty"], off["difficulty"]))
        # 付费标记比对: 附录中"(付费)"标记只出现在"核心算法"列
        # (扩展阅读小节里也可能有免费题, 如 241, 因此不能看章节单元格)
        claimed_paid = "付费" in row["algo"]
        if claimed_paid != off["paid_only"]:
            paid_errors.append("题 %d %s: 附录标记付费=%s, 官方付费=%s" % (
                n, off["title"], claimed_paid, off["paid_only"]))
        # 题名差异(仅提示)
        at = row["title"].replace(" ", "")
        ot = off["title"].replace(" ", "")
        if at != ot and at not in ot and ot not in at:
            title_info.append("题 %d: 附录=%s | 官方=%s" % (n, row["title"], off["title"]))

    print("附录B 行数: %d, 官方数据: %d" % (len(appendix), len(official)))
    print("-" * 60)
    if diff_errors:
        print("[难度不一致] %d 处:" % len(diff_errors))
        for e in diff_errors:
            print("   " + e)
    else:
        print("[难度] 全部一致 ✓")
    print("-" * 60)
    if paid_errors:
        print("[付费标记不一致] %d 处:" % len(paid_errors))
        for e in paid_errors:
            print("   " + e)
    else:
        print("[付费标记] 全部一致 ✓")
    print("-" * 60)
    if title_info:
        print("[题名差异-仅供参考] %d 处:" % len(title_info))
        for e in title_info:
            print("   " + e)
    else:
        print("[题名] 全部一致 ✓")

    if diff_errors or paid_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
