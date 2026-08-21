#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验书籍 Markdown 中所有 Python 代码块均可独立运行。

用法:
    python verify/verify_book.py                 # 校验根目录全部章节 md
    python verify/verify_book.py ch03-哈希表.md   # 只校验指定文件

规则:
- 只提取围栏为 ```python 的代码块。
- 块内第一行非空内容若以 "# @fragment" 开头, 视为片段, 跳过执行。
- 其余每个块必须作为独立程序执行成功(退出码 0), 否则报错。
- 警告(不阻断): 块内缺少 if __name__ == "__main__": 的块会被提示。
- 运行结束后生成验证报告 verify/report.md (含每个代码块的耗时)。
"""
import glob
import os
import re
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FENCE_RE = re.compile(r"```python[ \t]*\r?\n(.*?)```", re.S)
FRAGMENT_MARK = "# @fragment"
TIMEOUT = 120  # 单个代码块最长执行秒数
SLOW_WARN = 2.0  # 超过该秒数给出"偏慢"提示

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_tmp")
REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.md")


def iter_blocks(text):
    """逐个产出 (序号, 代码, 是否片段), 片段不执行。"""
    for m in FENCE_RE.finditer(text):
        code = m.group(1)
        first = next((ln for ln in code.splitlines() if ln.strip()), "")
        is_frag = first.strip().startswith(FRAGMENT_MARK)
        yield code, is_frag


def run_block(code, index):
    """把代码块写入临时文件并执行, 返回 (是否通过, 耗时秒, 错误信息)。"""
    os.makedirs(TMP_DIR, exist_ok=True)
    path = os.path.join(TMP_DIR, f"block_{index:04d}.py")
    out_path = path + ".out"
    err_path = path + ".err"
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    t0 = time.time()
    with open(out_path, "w", encoding="utf-8") as fo, open(err_path, "w", encoding="utf-8") as fe:
        try:
            proc = subprocess.run([sys.executable, path], stdout=fo, stderr=fe,
                                  timeout=TIMEOUT, cwd=TMP_DIR)
            ok = proc.returncode == 0
        except subprocess.TimeoutExpired:
            ok = False
            fe.write("TIMEOUT: 执行超过 %d 秒\n" % TIMEOUT)
    elapsed = time.time() - t0
    if not ok:
        with open(err_path, "r", encoding="utf-8", errors="replace") as f:
            err = f.read()[-2000:]
    else:
        err = ""
    return ok, elapsed, err


def verify_file(path):
    """返回 (文件名, 总块数, 片段数, 失败列表, 耗时列表, 缺少main的块列表)"""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    blocks = list(iter_blocks(text))
    total = len(blocks)
    frag_count = sum(1 for _, is_frag in blocks if is_frag)
    failed = []
    times = []
    no_main = []
    for i, (code, is_frag) in enumerate(blocks):
        if is_frag:
            times.append(0.0)
            continue
        ok, elapsed, err = run_block(code, i)
        times.append(elapsed)
        if not ok:
            failed.append((i, err))
        elif "if __name__ == \"__main__\":" not in code:
            no_main.append(i)
    return os.path.basename(path), total, frag_count, failed, times, no_main


def main():
    args = sys.argv[1:]
    if args:
        files = args
    else:
        files = sorted(glob.glob(os.path.join(BASE_DIR, "ch*.md")))
    if not files:
        print("未找到任何章节 md 文件")
        sys.exit(1)

    grand_total = 0
    grand_frag = 0
    grand_failed = 0
    grand_time = 0.0
    report_lines = ["# 代码验证报告\n", "| 文件 | 代码块 | 片段 | 失败 | 总耗时 | 平均耗时 |",
                    "| --- | --- | --- | --- | --- | --- |"]
    for f in files:
        name, total, frag_count, failed, times, no_main = verify_file(f)
        file_time = sum(times)
        avg = file_time / max(1, len(times))
        grand_total += total
        grand_frag += frag_count
        grand_failed += len(failed)
        grand_time += file_time
        status = "通过" if not failed else "失败 %d/%d" % (len(failed), total)
        print("[%s] %s (代码块 %d 个, 片段 %d, 耗时 %.1fs)"
              % (status, name, total, frag_count, file_time))
        report_lines.append("| %s | %d | %d | %d | %.1fs | %.2fs |"
                            % (name, total, frag_count, len(failed), file_time, avg))
        for idx, err in failed:
            print("    block %04d 执行失败:" % idx)
            for line in err.splitlines()[-12:]:
                print("      " + line)
        if no_main:
            print("    [提示] 以下块缺少 if __name__ == \"__main__\": %s" % no_main)
        for idx, t in enumerate(times):
            if t > SLOW_WARN:
                print("    [提示] block %04d 运行偏慢: %.1fs" % (idx, t))

    print("-" * 60)
    print("合计: %d 个代码块(含片段 %d), 失败 %d 个, 总耗时 %.1fs"
          % (grand_total, grand_frag, grand_failed, grand_time))
    report_lines.append("")
    report_lines.append("**合计: %d 个代码块(含片段 %d), 失败 %d 个, 总耗时 %.1fs**"
                        % (grand_total, grand_frag, grand_failed, grand_time))
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print("验证报告已写入 %s" % REPORT)
    if grand_failed:
        print("失败详情见 verify/_tmp/block_*.err")
        sys.exit(1)
    print("全部代码块验证通过!")


if __name__ == "__main__":
    main()
