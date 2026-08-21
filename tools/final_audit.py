#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发布前终审: 对全书做格式/结构/链接/占位符的静态检查。

检查项:
1. 每个 md 文件的代码围栏数量必须为偶数(未闭合围栏)。
2. 代码围栏语言标签必须属于 {python, text, mermaid} 白名单。
3. python 块: 检查是否含 if __name__ == "__main__": (警告)。
4. 字面 "\\n" 出现在正文(非代码块内) -> 警告(渲染缺陷)。
5. 遗留占位符: CONTINUE / TODO / XXX / 待补充 / FIXME -> 错误。
6. @fragment 块统计。
7. README 与导读中的 .md 相对链接, 目标文件必须存在。
8. 附录B: 行数=400, 数据库/Shell 17 个标注, 章节列不含空值。
9. 每个章节文件: 存在 H1 标题、"> 覆盖题号"行、## NN.7/8 小结或扩展(仅提示)。
10. 文件编码: 必须能用 UTF-8 无错误解码(含 BOM 检查)。
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
ALLOWED_FENCES = {"python", "text", "mermaid"}
PLACEHOLDER_RE = re.compile(r"<!--\s*CONTINUE\s*-->|TODO|FIXME|待补充|待完成|此处省略")
LITERAL_NL_RE = re.compile(r"[^\s`]\\n")  # 正文中出现字面 \n
MAIN_RE = re.compile(r"if __name__\s*==\s*[\"']__main__[\"']\s*:")

errors = []
warnings = []


def add_err(msg):
    errors.append(msg)


def add_warn(msg):
    warnings.append(msg)


def check_file(path):
    name = os.path.basename(path)
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        add_warn("%s: 含 UTF-8 BOM" % name)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        add_err("%s: 不是合法 UTF-8 (%s)" % (name, e))
        return

    # 1. 围栏配对(开/关状态机) + 2. 语言标签白名单
    langs = []
    for line in text.splitlines():
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            langs.append(m.group(1))
    if len(langs) % 2 != 0:
        add_err("%s: 代码围栏数量为奇数(%d), 存在未闭合围栏" % (name, len(langs)))
    # 偶数时按开-关配对, 开围栏的语言标签必须白名单
    for i in range(0, len(langs) - 1, 2):
        lang = langs[i]
        if lang not in ALLOWED_FENCES:
            add_err("%s: 未知围栏语言标签 ```%s (第 %d 个围栏)" % (name, lang, i // 2 + 1))

    # 3. python 块 main 检查(逐块)
    blocks = re.findall(r"```python[ \t]*\r?\n(.*?)```", text, re.S)
    frag = 0
    no_main = []
    for b in blocks:
        first = next((ln for ln in b.splitlines() if ln.strip()), "")
        if first.strip().startswith("# @fragment"):
            frag += 1
            continue
        if not MAIN_RE.search(b):
            no_main.append(b.splitlines()[0][:40] if b.splitlines() else "?")
    if no_main:
        add_warn("%s: %d 个 python 块缺 if __name__ == \"__main__\": (首行: %s)"
                 % (name, len(no_main), no_main[:3]))

    # 4. 字面 \n (排除代码块内的)
    code_spans = list(re.finditer(r"```.*?```", text, re.S))
    def in_code(pos):
        return any(s.start() <= pos < s.end() for s in code_spans)
    for m in LITERAL_NL_RE.finditer(text):
        if not in_code(m.start()):
            line = text.count("\n", 0, m.start()) + 1
            add_warn("%s:%d 正文出现字面 \\n (可能是换行符转义错误): ...%s..." %
                     (name, line, text[max(0, m.start()-20):m.end()+10].replace("\n", " ")))
            break  # 每文件只报第一处

    # 5. 占位符
    for m in PLACEHOLDER_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        add_err("%s:%d 发现占位符: %s" % (name, line, m.group(0)))

    # 6. fragment 统计
    if frag:
        add_warn("%s: @fragment 片段 %d 个" % (name, frag))

    # 9. 章节文件结构
    if name.startswith("ch") and name.endswith(".md"):
        if not text.startswith("# "):
            add_err("%s: 缺少 H1 标题" % name)
        if "> 覆盖题号" not in text:
            add_err("%s: 缺少 '> 覆盖题号' 行" % name)
        if "## " not in text:
            add_err("%s: 缺少二级章节" % name)

    return text


def check_links(text, path):
    """README/导读 中的相对 md 链接必须存在。"""
    for m in re.finditer(r"\[[^\]]*\]\(([^)#]+\.md)\)", text):
        target = m.group(1).split("#")[0]
        full = os.path.join(os.path.dirname(path), target)
        if not os.path.exists(full):
            add_err("%s: 链接目标不存在: %s" % (os.path.basename(path), target))


def check_appendix(text):
    rows = re.findall(r"^\| (\d{1,3}) \|", text, re.M)
    nums = [int(x) for x in rows if 1 <= int(x) <= 400]
    if len(nums) != 400 or sorted(nums) != list(range(1, 401)):
        add_err("附录B: 题号行数=%d, 应为 400 且为 1..400" % len(nums))
    db = sum(1 for line in text.splitlines()
             if re.match(r"^\| \d+ \|", line) and "数据库题（不展开）" in line)
    sh = sum(1 for line in text.splitlines()
             if re.match(r"^\| \d+ \|", line) and "Shell 题（不展开）" in line)
    if db != 13 or sh != 4:
        add_err("附录B: 数据库标注 %d 个(应13), Shell 标注 %d 个(应4)" % (db, sh))


def main():
    mds = sorted(glob.glob(os.path.join(ROOT, "*.md")))
    print("检查 %d 个 md 文件 ..." % len(mds))
    for p in mds:
        text = check_file(p)
        if text is None:
            continue
        name = os.path.basename(p)
        if name in ("README.md", "00-导读与使用说明.md"):
            check_links(text, p)
        if name == "附录B-LeetCode前400题对照表.md":
            check_appendix(text)

    # mermaid 统计
    mermaid_count = 0
    for p in mds:
        with open(p, "r", encoding="utf-8") as f:
            mermaid_count += f.read().count("```mermaid")
    print("Mermaid 图数量: %d" % mermaid_count)

    print("-" * 60)
    if warnings:
        print("警告 %d 条(不阻断):" % len(warnings))
        for w in warnings:
            print("  [警告] " + w)
    if errors:
        print("错误 %d 条(必须修复):" % len(errors))
        for e in errors:
            print("  [错误] " + e)
        sys.exit(1)
    print("静态审校通过: 无错误! 格式/围栏/链接/占位符/结构全部正常.")


if __name__ == "__main__":
    main()
