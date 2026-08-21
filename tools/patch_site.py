# -*- coding: utf-8 -*-
"""给 site/js/markdown.js 增加轻量公式支持: $...$ 与 $$...$$ -> <span class="math">"""
import io

path = r"site/js/markdown.js"
with io.open(path, encoding="utf-8") as f:
    text = f.read()

anchor = """    // 加粗 **text**
    s = s.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
    return s;"""

addition = """    // 加粗 **text**
    s = s.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
    // 公式: 块级 $$...$$ 与行内 $...$ (先块级后行内; 输出等宽斜体样式)
    s = s.replace(/\\$\\$([^$]+)\\$\\$/g, '<span class="math">$1</span>');
    s = s.replace(/\\$([^$\\n]+)\\$/g, '<span class="math">$1</span>');
    return s;"""

assert anchor in text, "anchor not found"
text = text.replace(anchor, addition)
with io.open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print("markdown.js 已增加公式支持")

# CSS 补充 .math 样式
css_path = r"site/css/style.css"
with io.open(css_path, encoding="utf-8") as f:
    css = f.read()
css_anchor = "/* 内链锚点 */"
css_addition = """/* 公式 */
.markdown-body .math {
  font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
  font-style: italic; font-size: .92em; color: var(--hl-number);
  background: var(--code-bg); padding: 1px 5px; border-radius: 5px;
  white-space: nowrap;
}
/* 内链锚点 */"""
assert css_anchor in css, "css anchor not found"
css = css.replace(css_anchor, css_addition, 1)
with io.open(css_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(css)
print("style.css 已增加 .math 样式")
