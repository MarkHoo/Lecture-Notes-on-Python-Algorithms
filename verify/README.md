# 代码验证流水线

本书所有 Python 代码块都经过**实际运行验证**，验证方法：

```text
python verify/verify_book.py                 # 校验根目录全部章节
python verify/verify_book.py ch03-哈希表.md   # 只校验指定章节
```

## 工作原理

1. 扫描指定 Markdown 文件中所有 ```` ```python ```` 围栏的代码块。
2. 块内第一行非空内容以 `# @fragment` 开头的块视为"语法片段"，跳过执行。
3. 其余每个块被提取为独立 `.py` 文件，用 `python` 实际执行（超时 120 秒）。
4. 退出码为 0 才算通过；失败时把错误输出打印出来，临时文件保留在 `verify/_tmp/` 供排查。

## 代码约定（作者必须遵守）

- 每个 python 代码块必须**完整自包含、可独立运行**：包含全部 import 与辅助类定义，
  结尾有 `if __name__ == "__main__":` 演示代码（含 `assert` 断言与成功提示）。
- 只允许 Python 标准库，语法兼容 Python 3.8+。
- 片段类代码必须加 `# @fragment` 标记，且尽量少用。

## 历史验证记录

每次全量验证后，在下方追加一行记录：

| 日期 | 命令 | 结果 |
| --- | --- | --- |
| 写作期 | `python verify/verify_book.py ch01-复杂度分析.md` | 6/6 通过 |
| 写作期 | `python verify/verify_book.py`（骨架全量） | 6/6 通过 |
| 写作期 | `python verify/verify_book.py ch05-二分查找.md` | 首次 9/11，修复 global 声明后复验通过 |
| 完稿 | `python verify/verify_book.py`（全书 26 章全量） | 478/478 通过 |
