# 第 22 章 Trie 字典树

> 覆盖题号：208, 211, 212, 336

## 22.1 引子：翻词典与输入法联想

回想翻纸质英语词典找 "apple" 的经历：你不会从 A 打头的第一页逐页翻，而是先翻到词典
侧面的 **a 区**，再在 a 区里找 **ap** 开头的小分区，最后在 **appl** 里定位到
"apple"。词典之所以好翻，是因为它把"开头相同的单词"归拢在了一起——找 "apple" 和找
"application"，前三个字母 "app" 的路是**共享**的。手机九宫格输入法、搜索引擎的输入
联想也是同一回事：你刚打出 "app"，输入法就猜出 "apple / application / 预约
（appointment）"——因为它知道"以 app 开头的词"有哪些。这种"**按前缀快速找到所有
候选**"的需求，就是 **Trie（字典树 / 前缀树）** 的用武之地。

LeetCode 第 208 题直接要求手写一个 Trie；第 211、212 题把 Trie 和**回溯（DFS）**结合，
第 336 题则展示了 Trie 与哈希表两种思路的较量。本章把这条主线一次讲透。

## 22.2 核心思想

### 22.2.1 直觉：一棵"长在单词前缀上的树"

Trie 是一棵**多叉树**，它的每条"边"上挂一个字符。从根节点出发，沿着边一路走到底，
把经过的字符按顺序连起来，就是某个**前缀**；在某个节点停下，连起来的就是"以这个
节点结尾的前缀"。为什么叫"字典树"？因为它把一本词典的**字母索引**搬进了程序里：
根节点相当于封面，第一层子节点相当于 a、b、c……各大分区，每一层都进一步细分
"前几个字母相同"的单词，节点上的 `is_end` 标记则相当于词典里的词条。

以插入 `"apple"` 和 `"app"` 为例，手工推演一遍：

1. 插入 `"apple"`：从根开始依次建出 `a → p → p → l → e` 五个节点（都不存在，全部
   新建），并在 `e` 节点上打结束标记；
2. 插入 `"app"`：从根开始走 `a → p → p`，前三个节点**已经存在**，直接复用，只在
   第三个 `p` 节点上打结束标记。

两次插入一共只新建了 5 个节点——`"apple"` 和 `"app"` 共享了 `a p p` 三条边。
这就是 Trie 的灵魂：**共享前缀，按前缀聚合**。下面这段代码把这两步跑给你看，并把树
的结构打印出来（带 `[单词结束]` 标记的节点说明有单词在那里收尾）：

```python
class TrieNode:
    """Trie 的节点: children 字典存子节点, is_end 标记是否有单词在此结束"""
    def __init__(self):
        self.children = {}   # 字符 -> 子节点
        self.is_end = False  # 是否有单词在到达本节点时结束


def build_trie(words):
    """把单词列表插入一棵 Trie, 返回根节点"""
    root = TrieNode()
    for w in words:
        node = root
        for ch in w:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True
    return root


def exists(root, word):
    """判断 word 是否是这棵 Trie 里的完整单词"""
    node = root
    for ch in word:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return node.is_end


def print_trie(node, label="", indent=0):
    """按层级打印 Trie: 每个节点一行, 缩进表示树的深度"""
    mark = " [单词结束]" if node.is_end else ""
    print("  " * indent + label + mark)
    for ch in sorted(node.children):
        print_trie(node.children[ch], ch, indent + 1)


if __name__ == "__main__":
    root = build_trie(["apple", "app"])
    print_trie(root)
    assert exists(root, "apple")
    assert exists(root, "app")
    assert not exists(root, "ap")      # "ap" 只是前缀, 不是完整单词
    assert not exists(root, "apply")   # 从未插入过的单词
    print("apple / app 插入成功, 所有断言通过!")
```

从打印结果可以清楚看到：`p`（第三个字符）节点是 `apple` 路径上的一个"分叉点"，
同时挂着结束标记。`exists(root, "ap")` 返回 False，因为没有任何单词在 `p`（第二个
字符）节点结束；而 `exists(root, "app")` 是 True。**"路径存在"和"单词存在"是两回事**
——这正是 `search` 与 `startsWith` 的本质区别，也是新手最容易踩的坑。

### 22.2.2 定义：节点存什么

一棵 Trie 的每个节点只需要两类信息：

- **子节点**：当前字符的下一跳指向谁。子节点可能有 26 个（甚至更多），最自然的存法
  是一个**字典 `dict`**：键是字符，值是对应的子节点，即 `children: dict[str, TrieNode]`。
  这是 Python 里最简洁的写法——不用为每个字符开定长数组，也没有"空槽位"浪费；
- **结束标记**：`is_end: bool`，表示"是否有单词恰好在这个节点结束"。

节点的完整 Python 定义见 22.3 节的伪代码，只有三行。

### 22.2.3 与哈希表、二叉树的对比

同样是"存一堆字符串"，Trie 和哈希表、二叉搜索树（BST）怎么选？看这张表：

| 能力 | 哈希表（set/dict） | 二叉搜索树 | Trie |
| --- | --- | --- | --- |
| 查找某个完整单词 | 平均 O(1) | O(log n) | O(L)（L 为单词长度） |
| 前缀查询（哪些词以 xx 开头） | 不支持，只能全量扫描 | 需借助"有序区间"技巧 | **天然支持**，沿路径走即可 |
| 单词的字典序遍历 | 不支持 | 中序遍历天然有序 | DFS 按子节点顺序即可 |
| 空间 | 每个单词独立存储 O(NL) | O(N) 个节点 | 共享前缀；但每个节点一个 dict，开销大 |

关键差异在第二行：**哈希表做不了前缀查询**。哈希函数把整个单词打散成一个位置，
"app" 和 "apple" 的哈希值没有任何关系；而 Trie 里它们共享 `a-p-p` 路径，"以 app
开头"就是"从根沿 a-p-p 走一步就能到达的子树"——这就是输入法联想背后的数据结构。
代价是空间：每个字符一个节点、每个节点一个 dict，Python 的 `dict` 开销不小，所以
Trie 通常比"一个 set 存所有单词"更占内存——**用空间换来了前缀能力**。

### 22.2.4 进阶一：Trie 上做回溯（DFS）

Trie 的三种基本操作都是"沿着路径走"，是**确定性**的：下一个字符是啥，就走哪个孩子。
但有些题目要求匹配"不完整的信息"：第 211 题的搜索词里可以出现通配符 `'.'`（匹配任意
一个小写字母），走到这一层我们**不知道**该走哪个孩子；第 212 题的单词由网格里相邻的
格子拼出，每走一步有上、下、左、右四个方向要试。这种"一层多选、全都要试"的匹配，就是**在 Trie 上做回溯（DFS）**：把"匹配一个字符"
从"查一次字典"变成"沿树往下走一层"，走不通就回头（回溯），走通了就继续深入。
211、212 两道题的全部技巧，本质上就是 22.3 伪代码末尾那个 `dfs` 骨架。

### 22.2.5 进阶二：Trie 与哈希的较量（第 336 题）

第 336 题要求找出所有"拼接后是回文"的词对 `(i, j)`。它有两种经典思路：**哈希思路**
把所有单词放进一个 `dict`，枚举每个单词的所有**切分点**，判断两段中哪段是回文、
另一段的逆序是否恰好是某个单词，实现简单直观；**Trie 思路**把所有单词**反转后**
插入 Trie，利用"共享前缀"在查询时一次性把"逆序匹配"和"回文部分"都算出来，
数据量大时更快。两种思路的完整实现与复杂度对比，见 22.6 节第 336 题。

## 22.3 算法流程

Trie 的基本操作可以归纳为"三个走法 + 一个回溯骨架"：

1. **定义节点**：`children` 字典 + `is_end` 标记；
2. **插入 `insert(word)`**：从根开始逐字符走，孩子不存在就新建，走到底打结束标记；
3. **查找 `search(word)`**：从根开始逐字符走，中途断了返回 False，走到底返回 `is_end`；
4. **前缀查找 `startsWith(prefix)`**：和 `search` 一样走，但**不检查** `is_end`；
5. **回溯搜索**：遇到"一层多选"（通配符、多方向）时，用递归把所有分支都试一遍。

伪代码如下：

```text
class TrieNode:
    children: dict   # 字符 -> TrieNode
    is_end: bool

def insert(word):
    node = root
    for ch in word:
        if ch not in node.children:
            node.children[ch] = TrieNode()   # 缺节点就新建
        node = node.children[ch]
    node.is_end = True                        # 打结束标记

def search(word):            # 完整单词查找
    node = root
    for ch in word:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return node.is_end                        # 必须真的有单词结束

def startsWith(prefix):      # 前缀查找
    node = root
    for ch in prefix:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return True                               # 只要求路径存在

def dfs(node, ...):          # Trie 上回溯的骨架
    if 到达终点: 记录或返回
    for 每个可选字符 ch:
        if ch 在 node.children 中:
            dfs(node.children[ch], ...)
            # 若有"占用/标记"类操作, 记得回溯撤销
```

把 `insert` 和 `search` 放在一起看：**只有一行之差**——`insert` 最后一步是
`node.is_end = True`，`search` 最后一步是 `return node.is_end`；`startsWith`
则连 `is_end` 都不看。

## 22.4 复杂度分析

**单次操作**的时间只和**被操作的单词/前缀的长度 L** 有关，与 Trie 里已经存了多少个
单词无关：

| 操作 | 时间复杂度 | 原因 |
| --- | --- | --- |
| insert | O(L) | 沿 L 个字符走，最多新建 L 个节点 |
| search | O(L) | 沿 L 个字符走，读一次 is_end |
| startsWith | O(L) | 沿 L 个字符走，不读 is_end |

**空间复杂度**：每插入一个单词最多产生 L 个新节点，总节点数不超过**所有单词的总
字符数**。但每个节点都带一个 `dict`，Python 字典开销不小，实际内存往往高于"一个
set 存所有单词"；反过来，大量单词共享前缀时（如 "apple / application / apply"），
Trie 又能省下重复存储。哈希查找平均 O(1)，但哈希计算本身也要扫一遍字符串（同样
O(L)），而且哈希表**无法回答前缀问题**——Trie 用"每个字符一个节点"的空间换来了
O(L) 的前缀查询，这是它存在的全部理由。

**组合算法**的复杂度（细节见真题）：211 的通配符 search 最坏遍历整棵子树；
212 建树 O(所有单词总长度)、每个格子最坏 4 个方向递归 L 层，理论最坏 O(m × n × 4^L)，
但 Trie 会在走不通的路径上立即剪枝；336 建结构 O(总长度)，查询阶段每个单词枚举
O(L) 个切分点、每次判回文 O(L)，总时间 O(N × L²)。

## 22.5 Python 实现：完整 Trie 类

下面给出一个完整、可运行的 Trie 类，把 22.3 的三个操作写齐。代码后的"细节"里还会
提到"删除单词"的简化做法——第 212 题"找到单词后从 Trie 里删掉以免重复"正是用它。

```python
class TrieNode:
    """Trie 节点: 每个节点保存子节点字典与"单词是否在此结束"标记"""
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    """字典树: 支持插入、查找完整单词、查找前缀"""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """插入一个单词, 时间 O(len(word))"""
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word):
        """查找完整单词是否存在"""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix):
        """判断是否存在以 prefix 开头的单词"""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True


if __name__ == "__main__":
    t = Trie()
    t.insert("apple")
    t.insert("app")
    assert t.search("apple") is True
    assert t.search("app") is True
    assert t.search("ap") is False           # "ap" 是前缀不是单词
    assert t.starts_with("ap") is True
    assert t.starts_with("appl") is True
    assert t.starts_with("b") is False
    assert t.search("") is False             # 边界: 空串未插入
    t.insert("")
    assert t.search("") is True              # 边界: 插入空串后根节点标记结束
    print("Trie 全部断言通过!")
```

**几个值得注意的细节：**

- `node.children.setdefault(ch, TrieNode())`：一步完成"有就用，没有就新建"，是
  Python 写 Trie 的惯用姿势；
- `search` 与 `starts_with` 的差别只在最后一行：前者要 `is_end`，后者不要；
- 空字符串 `""` 插入后结束标记打在根节点上，所以 `search("")` 返回 True；想"删除"
  一个单词，只需把路径末尾节点的 `is_end` 置回 False（不回收节点）——第 212 题的
  "找到单词后去重"用的正是这个思路。

## 22.6 LeetCode 真题精讲

### 208. 实现 Trie (前缀树)（中等）

**题意**：实现一个 Trie 类，支持 `insert(word)`、`search(word)`（完整单词是否存在）、
`startsWith(prefix)`（是否存在以 prefix 开头的单词）。单词只含小写字母。

**思路**：这就是 22.3 伪代码的照抄：三者共享"沿路径走"的框架，区别只在结尾检查什么。
手工推演：插入 `"apple"` 后，`search("app")` 返回 False——路径 `a→p→p` 存在，但
第三个 `p` 节点上还没有结束标记；`startsWith("app")` 返回 True——它只关心路径在不在；
再插入 `"app"` 后，`search("app")` 才变成 True。

```python
class TrieNode:
    """Trie 节点: 子节点字典 + 结束标记"""
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    """208. 实现 Trie (前缀树)"""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """插入单词: 沿着字符一路建节点, 最后打上结束标记"""
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word):
        """查找完整单词: 路径存在 且 结束标记为 True"""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def startsWith(self, prefix):
        """前缀查找: 只要求路径存在, 不要求结束标记"""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True


if __name__ == "__main__":
    trie = Trie()
    trie.insert("apple")
    assert trie.search("apple") is True        # 完整单词, 命中
    assert trie.search("app") is False         # "app" 只是前缀, 不是单词
    assert trie.startsWith("app") is True      # 前缀查找命中
    trie.insert("app")
    assert trie.search("app") is True          # 插入 "app" 后成为完整单词
    # 边界: 单字符与空 Trie
    t2 = Trie()
    assert t2.search("a") is False
    assert t2.startsWith("a") is False
    t2.insert("a")
    assert t2.search("a") is True
    assert t2.startsWith("") is True           # 空前缀永远存在
    print("208. 实现 Trie 全部断言通过!")
```

**复杂度分析**：三个操作都是 O(L)（L 为单词/前缀长度）；空间 O(总字符数)。

**易错点**：

- `search` 必须检查 `is_end`，否则会把"前缀"当成"单词"（"app" vs "apple" 的经典陷阱）；
- `startsWith` 恰好相反，**不能**检查 `is_end`；
- 空 Trie 的 `search` 返回 False；`startsWith("")` 返回 True 是合法边界，别去特判。

### 211. 添加与搜索单词 - 数据结构设计（中等）

**题意**：实现一个数据结构：`addWord(word)` 添加单词；`search(word)` 查询单词是否
存在，其中 `'.'` 可以匹配任意一个小写字母。

**思路**：`'.'` 通配符让"走哪条路"变得不确定，于是把 `search` 从循环改成**递归 DFS**：
普通字母照常走（有孩子就走，没有就 False）；遇到 `'.'` 则**遍历当前节点的所有子
节点**，只要有一条路能走通就返回 True。手工推演 `search(".ad")`（已插入 bad / dad /
mad）：第一层把根节点的三个孩子 `b、d、m` 全试一遍；走 `b` 的分支时，第二层是 `a`、
第三层是 `d`（命中且是结束标记），返回 True。`search("pad")` 则第一层的 `'p'` 根本
不在根节点的孩子里，直接 False。

```python
class TrieNode:
    """Trie 节点"""
    def __init__(self):
        self.children = {}
        self.is_end = False


class WordDictionary:
    """211. 添加与搜索单词 - 数据结构设计: '.' 可匹配任意一个小写字母"""

    def __init__(self):
        self.root = TrieNode()

    def add_word(self, word):
        """添加单词到字典树"""
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word):
        """搜索单词, '.' 是通配符, 用递归 DFS 处理"""

        def dfs(node, i):
            # 单词字符用完: 只有"走到一个单词结尾"才算找到
            if i == len(word):
                return node.is_end
            ch = word[i]
            if ch == ".":
                # 通配符: 遍历所有子节点, 只要有一条路走得通即可
                for child in node.children.values():
                    if dfs(child, i + 1):
                        return True
                return False
            if ch not in node.children:
                return False
            return dfs(node.children[ch], i + 1)

        return dfs(self.root, 0)


if __name__ == "__main__":
    wd = WordDictionary()
    wd.add_word("bad")
    wd.add_word("dad")
    wd.add_word("mad")
    assert wd.search("pad") is False       # 未添加过
    assert wd.search("bad") is True        # 精确匹配
    assert wd.search(".ad") is True        # '.' 匹配 'b'
    assert wd.search("b..") is True        # 两个通配符匹配 'ad'
    # 边界: 通配符全匹配 / 无匹配 / 单字符
    wd2 = WordDictionary()
    wd2.add_word("a")
    assert wd2.search(".") is True
    assert wd2.search("..") is False       # 长度不同, 不可能匹配
    assert wd2.search("b") is False
    wd2.add_word("")
    assert wd2.search("") is True          # 边界: 空单词
    print("211. 添加与搜索单词 全部断言通过!")
```

**复杂度分析**：`addWord` O(L)。`search` 最坏情况（全是 `'.'`）要遍历整棵子树，
O(节点总数)；没有通配符时仍是 O(L)。

**易错点**：

- 递归出口顺序：先判断 `i == len(word)`，此时返回 `node.is_end`；
- `'.'` 分支必须**遍历全部子节点**，有一个成功立即返回 True；
- 路径存在 ≠ 单词存在：如 `".."` 想匹配长度 1 的 `"a"`，走到第 2 层探不到底，
  靠 `is_end` 兜底返回 False。

### 212. 单词搜索 II（困难）

**题意**：给一个 `m × n` 的字母网格 `board` 和单词列表 `words`，找出所有能由
**相邻格子**（上下左右）连成的单词；同一个格子在一个单词中不能重复使用。

**思路**：暴力是"对每个单词从每个格子 DFS"，复杂度为"单词数 × m × n × 4^L"，
几乎必超时。**Trie 的优化**：把 `words` 全部插入一棵 Trie 共享前缀，然后**只做一轮
网格 DFS**：从每个格子出发，每一步顺着 Trie 往下走——走不通就剪枝返回，走到某个
节点发现"这里是一个单词的结尾"就记录答案。手工推演 `"oath"`：
`o(0,0) → a(0,1) → t(1,1) → h(2,1)` 四步都在 Trie 里，走到 `h` 节点时命中。

两个关键细节：**去重**——同一单词可能被找到多次，记录后把节点里的 `word` 置为
`None`（22.5 节提到的"摘掉结束标记"思路）；**格子不可重复使用**——原地把当前格子
临时改成 `'#'`，递归完四个方向再恢复（回溯）。

```python
class TrieNode:
    """Trie 节点: 这里用 word 字段直接存放完整单词, 方便收集答案"""
    def __init__(self):
        self.children = {}
        self.word = None   # 若某个单词在本节点结束, 存下完整单词; 否则为 None


class Solution:
    """212. 单词搜索 II"""

    def find_words(self, board, words):
        if not board or not board[0]:
            return []
        m, n = len(board), len(board[0])

        # 1. 把所有单词插入 Trie, 公共前缀只存一份
        root = TrieNode()
        for w in words:
            node = root
            for ch in w:
                node = node.children.setdefault(ch, TrieNode())
            node.word = w

        result = []

        def dfs(i, j, node):
            """在网格 (i, j) 处沿 Trie 继续走; node 是走到 board[i][j] 之前的节点"""
            ch = board[i][j]
            child = node.children.get(ch)
            if child is None:
                return                     # Trie 里没有这条路, 剪枝
            if child.word is not None:
                result.append(child.word)
                child.word = None          # 去重: 同一个单词只记录一次
            board[i][j] = "#"              # 原地标记: 本次 DFS 中不可重复使用
            for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and board[ni][nj] != "#":
                    dfs(ni, nj, child)
            board[i][j] = ch               # 回溯: 恢复原字符

        # 2. 从每个格子出发 DFS, 边 DFS 边沿着 Trie 走
        for i in range(m):
            for j in range(n):
                dfs(i, j, root)
        return result


if __name__ == "__main__":
    board = [["o", "a", "a", "n"],
             ["e", "t", "a", "e"],
             ["i", "h", "k", "r"],
             ["i", "f", "l", "v"]]
    words = ["oath", "pea", "eat", "rain"]
    ans = Solution().find_words(board, words)
    assert sorted(ans) == ["eat", "oath"]      # 结果顺序不敏感, 排序后比较
    # 边界: 空棋盘 / 单字符
    assert Solution().find_words([], ["a"]) == []
    assert sorted(Solution().find_words([["a"]], ["a", "b"])) == ["a"]
    board2 = [["a", "b"], ["c", "d"]]
    assert sorted(Solution().find_words(board2, ["ab", "ac", "ba", "dc"])) \
        == ["ab", "ac", "ba", "dc"]
    print("212. 单词搜索 II 全部断言通过!")
```

**复杂度分析**：建 Trie O(所有单词总长度)；DFS 每个格子最多 4 个方向、深度不超过
最长单词 L，理论最坏 O(m × n × 4^L)，但 Trie 剪枝让实际远小于此；空间 O(总长度)。

**易错点**：

- 题目不保证返回顺序，**断言前先排序**（或转 set 比较）；
- 记录答案后要"删除"该单词（`word = None`），否则会被重复统计；
- `'#'` 标记必须在递归返回后**恢复**，否则污染后续搜索；
- 空棋盘直接返回空列表，别让 `board[0][0]` 越界。

### 336. 回文对（困难）

**题意**：给一个不含重复单词的列表 `words`，找出所有下标对 `(i, j)`（`i ≠ j`），
使得 `words[i] + words[j]` 拼接后是回文。

**思路**：先拆解"什么时候两个词拼起来是回文"。设 `w_i = words[i]`、`w_j = words[j]`，
按较长的一边分类只有两种形态：① `w_i` 不短于 `w_j` 时，`w_i = P + reverse(w_j)`，
其中 **P 是回文**（`w_i + w_j = P + reverse(w_j) + w_j` 天然回文）；② `w_j` 长于
`w_i` 时，`w_j = S + reverse(w_i)`，其中 **S 是回文**。手工推演答案里的 `(3, 2)`：
`"s" + "lls" = "slls"` 是回文，较长的是 `"lls" = "ll"`（回文 S）+ `reverse("s")`，
命中形态 ②；而反过来的 `"lls" + "s" = "llss"` **不是**回文，所以没有 `(2, 3)`。

**Trie 法**：把每个单词**反转**后插入 Trie（让"逆序匹配"变成"沿着树走前缀"），查询
`w_i` 时沿 `w_i` 走：**情况 A**——走到某个节点，若它是某个反转词的结尾（记在
`node.index`）且 `w_i` 的**剩余部分是回文**，命中形态 ①；**情况 B**——若 `w_i` 被
完整消费，则所有"**剩余部分是回文**"的单词都能配对（命中形态 ②），建树时把这类单词
的下标预先记在节点的 `pal_suffix` 列表里。

```python
class TrieNode:
    """Trie 节点: index 记录单词下标, pal_suffix 记录"剩余部分是回文"的单词下标"""
    def __init__(self):
        self.children = {}
        self.index = -1       # 有单词在这里结束时存其下标, 否则 -1
        self.pal_suffix = []  # 其余部分是回文的单词下标列表


def is_pal(s):
    """判断字符串 s 是否是回文"""
    return s == s[::-1]


def palindrome_pairs_trie(words):
    """336. 回文对 (Trie 法): 把每个单词反转后插入 Trie, 再逐个查询"""
    root = TrieNode()

    # 1. 插入所有反转单词: 在路径上记录"剩余部分是回文"的单词
    for j, w in enumerate(words):
        node = root
        rev = w[::-1]
        for k, ch in enumerate(rev):
            if is_pal(rev[k + 1:]):
                node.pal_suffix.append(j)
            node = node.children.setdefault(ch, TrieNode())
        node.index = j

    pairs = set()

    # 2. 逐个查询: 走 w_i 的前缀, 分类讨论回文前缀/后缀
    for i, w in enumerate(words):
        if w == "":
            continue
        node = root
        for k, ch in enumerate(w):
            if ch not in node.children:
                break
            node = node.children[ch]
            # 情况 A: 前缀匹配了一个完整反转词, 且 w_i 剩余部分是回文
            if node.index != -1 and node.index != i and is_pal(w[k + 1:]):
                pairs.add((i, node.index))
        else:
            # 情况 B: w_i 被完整消费, 所有"剩余部分是回文"的单词都可配对
            for j in node.pal_suffix:
                if j != i:
                    pairs.add((i, j))

    # 3. 空单词特判: 空串与任何回文单词都能组成两个回文对
    for e, w in enumerate(words):
        if w == "":
            for i, other in enumerate(words):
                if i != e and is_pal(other):
                    pairs.add((i, e))
                    pairs.add((e, i))
            break

    return [list(p) for p in pairs]


if __name__ == "__main__":
    ans = palindrome_pairs_trie(["abcd", "dcba", "lls", "s", "sssll"])
    assert sorted(ans) == sorted([[0, 1], [1, 0], [3, 2], [2, 4]])
    # 边界: 单字符 / 空单词 / 反向词对
    assert palindrome_pairs_trie(["a"]) == []
    assert sorted(palindrome_pairs_trie(["a", ""])) == sorted([[0, 1], [1, 0]])
    assert sorted(palindrome_pairs_trie(["abc", "cba"])) == sorted([[0, 1], [1, 0]])
    print("336. 回文对 (Trie 法) 全部断言通过!")
```

**哈希法**（另一种完整实现）：把所有单词放进 `dict`（单词 → 下标），枚举每个单词的
所有切分点 `j`，把 `w[:j]` 和 `w[j:]` 两段分别套用上面的两种形态，用字典 O(1) 查
"某段逆序在不在 words 里"。注意 `j == len(w)` 时右段为空，情况 2 要跳过，避免与
情况 1 重复计数。

```python
def is_pal(s):
    """判断字符串 s 是否是回文"""
    return s == s[::-1]


def palindrome_pairs_hash(words):
    """336. 回文对 (哈希法): 枚举每个单词的所有切分点, 分类讨论"""
    index = {w: i for i, w in enumerate(words)}
    pairs = set()

    for i, w in enumerate(words):
        n = len(w)
        for j in range(n + 1):
            left, right = w[:j], w[j:]
            # 情况 1: left 是回文, 且 reverse(right) 是一个单词 -> 该词在前, w 在后
            if is_pal(left):
                k = index.get(right[::-1], -1)
                if k != -1 and k != i:
                    pairs.add((k, i))
            # 情况 2: right 是回文, 且 reverse(left) 是一个单词 -> w 在前, 该词在后
            if j != n and is_pal(right):
                k = index.get(left[::-1], -1)
                if k != -1 and k != i:
                    pairs.add((i, k))

    return [list(p) for p in pairs]


if __name__ == "__main__":
    ans = palindrome_pairs_hash(["abcd", "dcba", "lls", "s", "sssll"])
    assert sorted(ans) == sorted([[0, 1], [1, 0], [3, 2], [2, 4]])
    # 边界: 单字符 / 空单词 / 反向词对
    assert palindrome_pairs_hash(["a"]) == []
    assert sorted(palindrome_pairs_hash(["a", ""])) == sorted([[0, 1], [1, 0]])
    assert sorted(palindrome_pairs_hash(["abc", "cba"])) == sorted([[0, 1], [1, 0]])
    print("336. 回文对 (哈希法) 全部断言通过!")
```

两种方法对比如下：

| 方法 | 建结构 | 查询 | 空间 | 特点 |
| --- | --- | --- | --- | --- |
| Trie 法 | O(总长度) | O(N × L²) | O(总长度) | 共享前缀，数据量大时更省 |
| 哈希法 | O(总长度) | O(N × L²) | O(总长度) | 实现直观，容易想到 |

**复杂度分析**：两种方法建结构都是 O(总长度)；查询阶段每个单词枚举 O(L) 个切分点、
每次判回文 O(L)，总时间 O(N × L²)；空间 O(总长度)。

**易错点**：

- 必须排除 `i == j`：同一个单词不能和自己配对；
- **空单词** `""` 是特例：它与任何回文单词 `w` 都能组成 `("", w)` 和 `(w, "")`
  两个回文对；
- 同一对下标可能被重复加入，用 set 去重再转列表；
- 题目不保证返回顺序，断言前排序。

## 22.7 本章小结

### 要点回顾

1. **Trie 是什么**：多叉树，每条边一个字符；节点用 `children: dict` 存子节点、
   `is_end` 标记单词结尾；从根到某个节点的路径就是一个前缀。
2. **三个基本操作**：`insert` 缺节点就建、走到底打标记；`search` 走到底还要
   `is_end`；`startsWith` 只问路径在不在。
3. **灵魂是共享前缀**：前缀查询 O(L)，与已存单词数无关；代价是每节点一个 dict。
4. **Trie + 回溯**：遇到"一层多选"（211 的通配符、212 的四个方向），用递归 DFS
   把所有分支试一遍，走不通就剪枝、走完就回溯。
5. **去重三板斧**：记录后置 `word = None`（212）；set 收集（336）；比较前排序。

### 常见错误

- `search` 忘查 `is_end`：把前缀当单词；`startsWith` 查了 `is_end`：前缀查询莫名失败；
- 212 回溯后忘了恢复 `'#'` 标记：后续搜索被污染；结果不排序就断言；
- 336 忘了 `i != j` 与空单词特判；
- 用 `list` 代替 `dict` 存子节点：插入前要线性查找，把 O(L) 的操作退化。

## 22.8 扩展阅读

Trie 家族和它的近亲远不止本章四题，以下都是超出前 400 题范围、但值得了解的进阶方向：

- **压缩 Trie（Radix Tree / Patricia Tree）**：把"只有一个孩子的连续路径"压缩成一条
  边上的整段字符串，节点数大幅减少。经典应用是路由表（IP 前缀匹配）和 Redis 的
  `Rax`。
- **后缀树 / 后缀数组**：把一个字符串的所有后缀放进一棵压缩 Trie，可以在 O(L) 内
  回答"某个模式串出现了几次、出现在哪"等问题，是理解高级字符串匹配的必经之路。
- **AC 自动机（Aho–Corasick）**：把 KMP 的单模式匹配推广到**多模式**：多个模式串
  建成 Trie 后再补上"失配指针"，扫描一遍文本就能同时找出所有模式串。经典应用是
  敏感词过滤。
- **二进制 Trie（Bitwise Trie）**：Trie 不只装字母。把整数的二进制位当成"字符"
  插入 Trie，可在 O(位数) 内回答"哪个数与 x 异或最大"——第 421 题（数组最大异或，
  超出前 400 题）就是招牌题。
- **带计数的 Trie**：节点上再存一个 `count`，可支持"统计有多少单词以某前缀开头"
  "删除时回收节点"等操作。

