#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""尝试拉取 LeetCode 官方题目列表(题号/题名/难度/是否付费), 用于附录 B 核对。

用法: python tools/fetch_leetcode.py
成功: 保存到 tools/leetcode_problems.json 并打印统计
失败: 打印错误信息
"""
import json
import os
import sys
import urllib.request

URLS = [
    "https://leetcode.com/api/problems/all/",
    "https://leetcode.cn/api/problems/all/",
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leetcode_problems.json")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    for url in URLS:
        try:
            data = fetch(url)
            pairs = data.get("stat_status_pairs", [])
            if not pairs:
                print("FAIL: %s 返回空数据" % url)
                continue
            rows = []
            for p in pairs:
                st = p["stat"]
                rows.append({
                    "id": st["question_id"],
                    "title": st["question__title"],
                    "title_slug": st["question__title_slug"],
                    "difficulty": {1: "简单", 2: "中等", 3: "困难"}.get(p["difficulty"]["level"], "?"),
                    "paid_only": p.get("paid_only", False),
                })
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=1)
            print("OK: %s, 共 %d 题, 已保存 %s" % (url, len(rows), OUT))
            return 0
        except Exception as e:
            print("FAIL: %s -> %s" % (url, e))
    print("全部失败: 网络不可达")
    return 1


if __name__ == "__main__":
    sys.exit(main())
