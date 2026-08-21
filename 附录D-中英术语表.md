# 附录 D：中英术语表

> 面试与刷题时经常遇到英文术语，本表按主题整理本书涉及的核心术语，
> 中文名、英文名、一句话解释与本书对应章节一一对应，方便速查。

## D.1 复杂度与算法分析

| 中文 | English | 一句话解释 | 章节 |
| --- | --- | --- | --- |
| 时间复杂度 | Time Complexity | 运行时间随输入规模的增长趋势 | ch01 |
| 空间复杂度 | Space Complexity | 额外内存随输入规模的增长趋势 | ch01 |
| 大 O 记号 | Big-O Notation | 描述增长上界的记号 | ch01 |
| 常数时间 | Constant Time | $O(1)$，与输入规模无关 | ch01 |
| 对数时间 | Logarithmic Time | $O(\log n)$，如二分查找 | ch01/05 |
| 线性时间 | Linear Time | $O(n)$，如一次遍历 | ch01 |
| 线性对数时间 | Linearithmic Time | $O(n\log n)$，如归并/快排 | ch01/06 |
| 平方时间 | Quadratic Time | $O(n^2)$，如双重循环 | ch01 |
| 指数时间 | Exponential Time | $O(2^n)$，如朴素回溯 | ch01/14 |
| 均摊复杂度 | Amortized Complexity | 多次操作的总代价平均到每次 | ch01 |
| 递归 | Recursion | 函数调用自身 | ch01/10 |
| 递归树 | Recursion Tree | 递归调用的展开树，用于分析复杂度 | ch01 |
| 记忆化 | Memoization | 缓存子问题答案避免重复计算 | ch01/16 |
| 循环不变量 | Loop Invariant | 每轮循环都成立的性质，二分/双指针正确性的根基 | ch05 |
| 主定理 | Master Theorem | 求解 $T(n)=aT(n/b)+O(n^d)$ 的工具 | ch01 |
| 原地算法 | In-place Algorithm | 空间 $O(1)$、直接修改输入的算法 | ch02 |
| 稳定性 | Stability | 排序时相等元素的相对顺序是否保持 | ch06 |
| 哨兵 | Sentinel | 边界处放置的"看守"值，简化代码 | ch09/02 |

## D.2 数据结构

| 中文 | English | 一句话解释 | 章节 |
| --- | --- | --- | --- |
| 数组 | Array | 按下标 $O(1)$ 随机访问的连续存储 | ch02 |
| 链表 | Linked List | 指针串联的节点序列，插入删除快 | ch07 |
| 单向链表 | Singly Linked List | 每个节点只有 next 指针 | ch07 |
| 双向链表 | Doubly Linked List | 节点有 prev/next 两个指针 | ch26 |
| 哑节点 | Dummy Node | 链表头部占位节点，统一边界处理 | ch07 |
| 栈 | Stack | 后进先出（LIFO） | ch08 |
| 队列 | Queue | 先进先出（FIFO） | ch08 |
| 双端队列 | Deque | 两端都可插入删除 | ch08/09 |
| 哈希表 | Hash Table | 键到值的 $O(1)$ 映射 | ch03 |
| 哈希函数 | Hash Function | 键 → 桶号的映射函数 | ch03 |
| 哈希冲突 | Collision | 不同键映射到同一桶 | ch03 |
| 链地址法 | Separate Chaining | 冲突时用链表挂接 | ch03 |
| 开放寻址 | Open Addressing | 冲突时找下一个空位 | ch03 |
| 负载因子 | Load Factor | 已用桶数/总桶数，过高触发扩容 | ch03 |
| 堆 | Heap | 完全二叉树实现的优先队列 | ch13 |
| 二叉堆 | Binary Heap | 用数组存储的堆（下标 $2i+1/2i+2$） | ch13 |
| 上浮 | Sift-up | 新元素向上调整恢复堆序 | ch13 |
| 下沉 | Sift-down | 堆顶向下调整恢复堆序 | ch13 |
| 堆序 | Heap Order | 父 ≤ 子（小顶堆）等性质 | ch13 |
| 二叉树 | Binary Tree | 每个节点至多两个孩子 | ch10 |
| 完全二叉树 | Complete Binary Tree | 除最后一层外全满、最后一层靠左 | ch11/13 |
| 满二叉树 | Full Binary Tree | 每个节点要么是叶子要么有两个孩子 | ch10 |
| 二叉搜索树 | Binary Search Tree (BST) | 左小右大的有序树 | ch12 |
| 平衡二叉树 | Balanced Binary Tree | 左右子树高度差受限的树 | ch10/12 |
| 字典树 | Trie | 按前缀共享字符的多叉树 | ch22 |
| 树状数组 | Fenwick Tree / BIT | 支持单点改+前缀查的 $O(\log n)$ 结构 | ch25 |
| 线段树 | Segment Tree | 支持区间查询/修改的 $O(\log n)$ 结构 | ch25 |
| 并查集 | Union-Find / Disjoint Set | 维护元素分组的森林结构 | ch20 |
| 优先队列 | Priority Queue | 每次取最值的队列，常用堆实现 | ch13 |
| 单调栈 | Monotonic Stack | 栈内元素单调，找"下一个更大/更小" | ch09 |
| 单调队列 | Monotonic Queue | 队列内元素单调，维护窗口最值 | ch09 |
| 有序集合 | Ordered Set | 支持二分查找的有序结构 | ch18/25 |

## D.3 算法与技巧

| 中文 | English | 一句话解释 | 章节 |
| --- | --- | --- | --- |
| 双指针 | Two Pointers | 两个下标协同扫描 | ch02/04 |
| 对撞指针 | Colliding Pointers | 左右向中间夹逼 | ch04 |
| 快慢指针 | Fast & Slow Pointers | 一快一慢找环/中点 | ch07 |
| 滑动窗口 | Sliding Window | 可变长窗口 + 计数维护 | ch04 |
| 二分查找 | Binary Search | 有序空间每次砍半 | ch05 |
| 二分答案 | Binary Search on Answer | 对值域二分，配合判定函数 | ch05 |
| 快速选择 | Quickselect | 快排思想找第 K 大/小 | ch06/13 |
| 排序稳定性 | Stable Sort | 相等元素相对顺序不变 | ch06 |
| 荷兰国旗问题 | Dutch National Flag | 三色数组原地分类 | ch04 |
| 回溯 | Backtracking | 选择-递归-撤销的搜索 | ch14 |
| 剪枝 | Pruning | 提前终止不可能的分支 | ch14 |
| 贪心算法 | Greedy Algorithm | 每步取局部最优 | ch15 |
| 交换论证 | Exchange Argument | 贪心正确性证明方法 | ch15 |
| 动态规划 | Dynamic Programming (DP) | 用子问题答案填表求解 | ch16 |
| 最优子结构 | Optimal Substructure | 大问题最优由子问题最优组成 | ch16 |
| 重叠子问题 | Overlapping Subproblems | 子问题被反复计算 | ch16 |
| 状态 | State | DP 表格中一个格子（子问题） | ch16 |
| 状态转移方程 | Transition | 格子之间的递推关系 | ch16 |
| 初始化 | Initialization | 边界格子的值 | ch16 |
| 滚动数组 | Rolling Array | 只用有限行/列节省空间 | ch16 |
| 记忆化搜索 | Memoized DFS | 自顶向下 + 缓存 | ch16/19 |
| 区间 DP | Interval DP | 状态是区间 $[i,j]$ | ch17 |
| 树形 DP | Tree DP | 在树上做后序 DP | ch11/18 |
| 状态机 DP | State-Machine DP | 用有限状态建模（如股票） | ch18 |
| 背包问题 | Knapsack Problem | 容量约束下的选择问题 | ch18 |
| 0-1 背包 | 0-1 Knapsack | 每件物品选或不选 | ch18 |
| 完全背包 | Unbounded Knapsack | 每件物品可取无限次 | ch18 |
| 最长递增子序列 | LIS | 保持顺序的最长上升子序列 | ch18 |
| 最长公共子序列 | LCS | 两个序列的最长公共子序列 | ch17 |
| 编辑距离 | Edit Distance / Levenshtein | 增删改的最少操作数 | ch17 |
| 广度优先搜索 | BFS | 逐层扩散，无权图最短路径 | ch19 |
| 深度优先搜索 | DFS | 一条路走到底再回头 | ch19 |
| 双向 BFS | Bidirectional BFS | 两端同时扩散的 BFS 优化 | ch19/21 |
| 拓扑排序 | Topological Sort | 有向无环图的线性序 | ch20 |
| 欧拉路径 | Eulerian Path | 一笔画经过所有边 | ch20 |
| 路径压缩 | Path Compression | 并查集 find 时压平树 | ch20 |
| 按秩合并 | Union by Rank | 矮树挂到高树上 | ch20 |
| 字符串匹配 | String Matching | 在文本中找模式串 | ch21 |
| KMP 算法 | Knuth-Morris-Pratt | $O(n+m)$ 匹配，靠前缀函数 | ch21 |
| 前缀函数 | Prefix Function | next 数组：最长相等前后缀 | ch21 |
| 滚动哈希 | Rolling Hash / Rabin-Karp | 滑动窗口哈希匹配 | ch21 |
| 回文 | Palindrome | 正反读相同 | ch21 |
| 中心扩展 | Expand Around Center | 从中心向两边扩找回文 | ch21 |
| Manacher 算法 | Manacher's Algorithm | $O(n)$ 最长回文子串 | ch21 |
| 快速幂 | Fast Exponentiation | $O(\log n)$ 求 $x^n$ | ch24 |
| 埃氏筛 | Sieve of Eratosthenes | 高效求素数表 | ch24 |
| 最大公约数 | Greatest Common Divisor (GCD) | 欧几里得算法 | ch24 |
| 裴蜀定理 | Bézout's Identity | 线性组合可表示 gcd 的倍数 | ch24 |
| 卡特兰数 | Catalan Number | 二叉树数量等组合计数 | ch12 |
| 蓄水池抽样 | Reservoir Sampling | 流式等概率抽样 | ch26 |
| 洗牌算法 | Fisher-Yates Shuffle | 均匀随机打乱 | ch26 |
| 扫描线 | Sweep Line | 事件排序后从左到右扫描 | ch13 |
| 差分数组 | Difference Array | 区间批量加用端点标记 | ch25 |
| 前缀和 | Prefix Sum | 累计和数组，$O(1)$ 区间和 | ch25 |
| 位掩码 | Bitmask | 用整数位表示集合 | ch23 |
| 格雷码 | Gray Code | 相邻数二进制只差一位 | ch23 |
| 投票法 | Boyer-Moore Majority Vote | $O(1)$ 空间找众数 | ch03 |
| 状态压缩 | State Compression (Bitmask DP) | 用位表示子集做 DP | ch23 扩展 |

## D.4 面试与刷题用语

| 中文 | English | 一句话解释 |
| --- | --- | --- |
| 在线判题系统 | Online Judge (OJ) | 提交代码自动评测的平台（如 LeetCode） |
| 通过 | Accepted (AC) | 代码通过全部测试 |
| 超时 | Time Limit Exceeded (TLE) | 运行超过时限 |
| 超内存 | Memory Limit Exceeded (MLE) | 内存超过上限 |
| 边界用例 | Edge Case | 空输入、单元素、极值等特殊输入 |
| 暴力解法 | Brute Force | 直接枚举所有可能的解法 |
| 约束 | Constraints | 题目给出的数据规模限制 |
| 输入规模 | Input Size | 通常用 $n$ 表示 |
| 测试用例 | Test Case | 一组输入 + 期望输出 |
| 示例 | Example | 题目给出的演示用例 |
| 付费题 | Premium / Locked | 需要会员才能查看的题目 |
| 通过率 | Acceptance Rate | 提交中通过的比例 |
| 对标 | Benchmark | 与标准解法对照验证 |
| 随机对拍 | Stress Test / Random Testing | 随机输入下与暴力解对照验证 |

> 用法建议：面试前通读 D.1~D.3，做到"看到英文术语能说出中文与含义"；
> 刷题时遇到不认识的术语回到本表速查。
