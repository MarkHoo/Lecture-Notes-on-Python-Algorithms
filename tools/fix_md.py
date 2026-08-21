import re

path = r"ch03-哈希表.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 字面反斜杠+n 出现在代码围栏前的, 替换为真实换行
n1 = text.count("\\n```")
text2 = text.replace("\\n```", "\n```")
n2 = text2.count("\\n```")
# 其余字面 \n (不在围栏前的) 也改为真实换行? 保守起见只处理围栏前的
with open(path, "w", encoding="utf-8") as f:
    f.write(text2)
print(f"replaced: {n1}, remaining literal \\n before fence: {n2}")
