---
source_id: operating-systems-003
course_id: operating_systems
title: "操作系统模拟考试试卷_题目版"
original_file: "学科资料/操作系统/操作系统模拟考试试卷_题目版.pdf"
document_role: past_exam
year: 
locator_type: page
---

# 操作系统模拟考试试卷_题目版

<!-- page: 1 -->

《操作系统期末考试试卷》

第一部分：选择题（每题2 分，共40 分）

<!-- question: operating-systems-003-Q1 -->

1. 下列哪一项最能体现操作系统的主要目标？
A. 提高系统资源利用率与用户使用便利性
B. 提高编程语言执行速度
C. 减少硬件设备数量
D. 增加指令集长度

<!-- question: operating-systems-003-Q2 -->

2. 以下哪项通常不包含在进程控制块（Process Control Block, PCB）中？
A. 进程状态
B. 寄存器内容
C. 页表基地址
D. 编译器优化信息

<!-- question: operating-systems-003-Q3 -->

3. 下列哪一种调度算法可能造成“饥饿”（Starvation）？
A. 轮转调度（Round Robin）
B. 先来先服务（FCFS）
C. 短作业优先（SJF）
D. 时间片加权轮转

<!-- question: operating-systems-003-Q4 -->

4. 临界区（Critical Section）问题的根本目的是：
A. 提升CPU 利用率
B. 允许同时读写共享数据
C. 避免并发访问共享资源导致冲突
D. 减少内存占用

<!-- question: operating-systems-003-Q5 -->

5. 信号量（Semaphore）主要用于：
A. 线程创建
B. 同步与互斥
C. 进程调度
D. 缓存管理

<!-- question: operating-systems-003-Q6 -->

6. 产生死锁（Deadlock）必须满足四个条件，以下哪一个不是？
A. 互斥
B. 占有并等待
C. 可抢占
D. 循环等待

<!-- question: operating-systems-003-Q7 -->

7. 虚拟内存（Virtual Memory）的主要作用是：
A. 使程序运行速度加倍
B. 使程序地址空间大于物理内存
C. 增加CPU 寄存器数量
D. 提高磁盘容量利用率

<!-- page: 2 -->

<!-- question: operating-systems-003-Q8 -->

8. 页面置换算法中理论缺页率最优的是：
A. OPT
B. FIFO
C. LRU
D. Clock

<!-- question: operating-systems-003-Q9 -->

9. 若页面错误频繁，通常应：
A. 增大时间片
B. 提升物理页面数量
C. 使用更小的页大小
D. 关闭交换空间

<!-- question: operating-systems-003-Q10 -->

10. 文件分配表（File Allocation Table, FAT）属于：
A. 索引式文件系统
B. 连续分配文件系统
C. 链式文件系统
D. 日志文件系统

<!-- question: operating-systems-003-Q11 -->

11. I/O 系统中缓冲区（Buffer）的作用是：
A. 加快CPU 指令执行
B. 减少进程数量
C. 平滑CPU 与设备速度差
D. 增大主存容量

<!-- question: operating-systems-003-Q12 -->

12. 中断（Interrupt）的主要作用是：
A. 切换虚拟内存
B. 优化缓存替换策略
C. 处理异步事件
D. 提高文件访问速度

<!-- question: operating-systems-003-Q13 -->

13. 线程（Thread）相对于进程（Process）的特点是：
A. 独立地址空间
B. 创建开销更大
C. 共享代码段与数据段
D. 不可并发执行

<!-- question: operating-systems-003-Q14 -->

14. 用户态（User Mode）到内核态（Kernel Mode）转换的原因是：
A. 缓存命中
B. 执行系统调用
C. 运行普通指令
D. 切换线程本地变量

<!-- question: operating-systems-003-Q15 -->

15. 以下不属于死锁预防策略的是：
A. 破坏占有并等待
B. 破坏互斥

<!-- page: 3 -->

C. 破坏循环等待
D. 破坏不可抢占

<!-- question: operating-systems-003-Q16 -->

16. 写时复制（Copy-On-Write, COW）的作用是减少：
A. 程序执行时间
B. 进程复制地址空间开销
C. 文件访问延迟
D. CPU 调度成本

<!-- question: operating-systems-003-Q17 -->

17. 关于缓存（Cache），哪项正确：
A. 命中率越高性能越差
B. 缓存属于主存
C. 局部性原理提高命中率
D. 缓存仅用于CPU 不能用于磁盘

<!-- question: operating-systems-003-Q18 -->

18. 文件系统中inode 不包含：
A. 文件权限
B. 文件大小
C. 文件数据内容
D. 指向数据块的指针

<!-- question: operating-systems-003-Q19 -->

19. 生产者–消费者问题典型工具是：
A. 信号量
B. 链表
C. 栈
D. 队列

<!-- question: operating-systems-003-Q20 -->

20. 关于内核，下列正确的是：
A. 单体内核不允许动态模块
B. 微内核将服务移到用户态
C. 微内核一定更快
D. 内核不处理中断

第二部分：判断题（每题1 分，共10 分）

<!-- question: operating-systems-003-Q21 -->

21. 进程状态从运行→等待通常因为时间片耗尽。（）

<!-- question: operating-systems-003-Q22 -->

22. LRU 开销大于FIFO。（）

<!-- question: operating-systems-003-Q23 -->

23. 页面错误一定导致程序崩溃。（）

<!-- question: operating-systems-003-Q24 -->

24. 操作系统使用中断向量表定位中断处理程序。（）

<!-- question: operating-systems-003-Q25 -->

25. PV 操作是信号量实现基础。（）

<!-- question: operating-systems-003-Q26 -->

26. 自旋锁适合长临界区。（）

<!-- question: operating-systems-003-Q27 -->

27. 文件系统中，目录也是文件。（）

<!-- question: operating-systems-003-Q28 -->

28. 银行家算法用于死锁避免。（）

<!-- question: operating-systems-003-Q29 -->

29. 系统调用必须陷入内核态。（）

<!-- question: operating-systems-003-Q30 -->

30. 分段可共享而分页不能共享。（）

<!-- page: 4 -->

第三部分：简答题（每题5 分，共25 分）

<!-- question: operating-systems-003-Q31 -->

31. 简述进程（Process）与线程（Thread）的主要区别。

<!-- question: operating-systems-003-Q32 -->

32. 请说明死锁（Deadlock）的四个必要条件。

<!-- question: operating-systems-003-Q33 -->

33. 简述页面置换算法LRU 与FIFO 的差异。

<!-- question: operating-systems-003-Q34 -->

34. 为什么操作系统需要两级调度（长期调度+ 短期调度）？

<!-- question: operating-systems-003-Q35 -->

35. 简述写时复制（Copy-On-Write, COW）的工作原理。

第四部分：分析题（10 分）

<!-- question: operating-systems-003-Q36 -->

36. 已知系统有三个进程P1、P2、P3，共享同一临界区资源。采用信号量机制
（Semaphore），请写出伪代码并说明其如何避免竞态条件。

第五部分：综合题（15 分）

<!-- question: operating-systems-003-Q37 -->

37. 某系统采用分页（Paging）与请求调页（Demand Paging）。访问序列：
0,1,2,3,2,1,0,3,2；物理帧数=3。请分别计算FIFO 和LRU 的缺页次数，并比较两者原因。

《参考答案》

《操作系统期末考试试卷》
第一部分：选择题（每题2 分，共40 分）
1 A
2 D
3 C
4 C
5 B
6 C
7 B

8 A
9 B
10 C
11 C
12 C
13 C
14 B

15 B
16 B
17 C
18 C
19 A
20 B

第二部分：判断题（每题1 分，共10 分）
21 ×
22 
23 ×
24 
25 

26 ×
27 
28 
29 
30 ×

# **第三部分：简答题（每题5 分，共25 分）参考答案& 评分标准**

<!-- page: 5 -->

**31. 进程（Process）与线程（Thread）的主要区别**
## **参考答案（要点）**

<!-- question: operating-systems-003-Q38 -->

1. **资源占用不同**：进程拥有独立地址空间，线程共享进程地址空间
与资源。

<!-- question: operating-systems-003-Q39 -->

2. **调度粒度不同**：线程是最小调度单位，进程通常作为资源分配单
位。

<!-- question: operating-systems-003-Q40 -->

3. **开销不同**：创建、销毁进程开销大；线程开销更小、切换更快。

<!-- question: operating-systems-003-Q41 -->

4. **隔离性不同**：进程间相互隔离，线程间共享资源更容易出现并发
问题。

<!-- question: operating-systems-003-Q42 -->

5. **通信方式不同**：进程需IPC（管道、消息队列等）；线程可直接
读写共享内存。
### **评分标准（5 分）**
* 资源、调度、开销三点任意两点（2 分）
* 描述隔离性、通信方式中的任意一点（1 分）
* 每写对一个完整要点+1 分（最多5 分）
---

**32. 死锁（Deadlock）的四个必要条件**
### **参考答案**

<!-- question: operating-systems-003-Q43 -->

1. **互斥条件**：资源不可共享。

<!-- question: operating-systems-003-Q44 -->

2. **占有并等待条件**：进程占有部分资源并等待其他资源。

<!-- question: operating-systems-003-Q45 -->

3. **不可抢占条件**：资源不能强制回收。

<!-- question: operating-systems-003-Q46 -->

4. **循环等待条件**：存在进程之间的资源循环等待链。
### **评分标准（5 分）**
* 每写对一个条件1 分，共4 分
* 解释清楚任意一点附加1 分
---

**33. LRU（Least Recently Used）与FIFO（First-In First-Out）差异**
### **参考答案**

<!-- question: operating-systems-003-Q47 -->

1. **策略不同**
* FIFO：最先进入物理内存的页最先淘汰
* LRU：最长时间未被使用的页淘汰

<!-- question: operating-systems-003-Q48 -->

2. **性能差异**：LRU 更贴近程序局部性特征，通常优于FIFO。

<!-- question: operating-systems-003-Q49 -->

3. **异常现象**：FIFO 会出现Belady’s Anomaly（LRU 不会）。

<!-- question: operating-systems-003-Q50 -->

4. **实现开销**：LRU 开销大（需要记录访问时间/链表）；FIFO 实现
简单。

<!-- page: 6 -->

### **评分标准（5 分）**
* 描述策略差异（2 分）
* 描述性能或Belady’s Anomaly（2 分）
* 描述实现开销（1 分）
---
**34. 为什么需要两级调度（长期调度+ 短期调度）？**
### **参考答案**

<!-- question: operating-systems-003-Q51 -->

1. **长期调度**用于控制系统多道程序度，决定哪些作业进入内存成为
进程。

<!-- question: operating-systems-003-Q52 -->

2. **短期调度**用于选择就绪队列中哪个进程获得CPU。

<!-- question: operating-systems-003-Q53 -->

3. **分层调度好处：**
* 控制系统负载、维持CPU / I/O 平衡
* 提高吞吐量与资源利用率
* 避免系统内进程过多导致频繁换页或调度开销过大
### **评分标准（5 分）**
* 长期调度作用（2 分）
* 短期调度作用（2 分）
* 分级调度带来的优势（1 分）
---

**35. 写时复制（Copy-On-Write, COW）的工作原理**

### **参考答案**

<!-- question: operating-systems-003-Q54 -->

1. **多个进程共享相同只读页面（如fork 后的父子进程共享页）。**

<!-- question: operating-systems-003-Q55 -->

2. **当任意进程试图写入共享页时，触发缺页异常。**

<!-- question: operating-systems-003-Q56 -->

3. **系统为写入进程复制该页，此后两个进程使用不同的物理页。**

<!-- question: operating-systems-003-Q57 -->

4. **优点：减少进程复制开销，提高创建速度（尤其是fork+exec ）。
**
### **评分标准（5 分）**
* 共享只读页（1 分）
* 写时触发异常（1 分）
* 创建私有副本（1 分）
* 内核处理流程完整（1 分）
* 优点（1 分）

# **第四部分：分析题（10 分）**

**36. 信号量互斥伪代码& 原理分析**

<!-- page: 7 -->

## **参考答案**
### **伪代码（P/V 操作实现互斥）**
```c
Semaphore mutex = 1;
Process Pi:
while (true) {

P(mutex);
// 进入临界区
critical section;
V(mutex);
// 离开临界区
remainder section;
}
```
### **原理分析**

<!-- question: operating-systems-003-Q58 -->

1. **保证互斥（Mutual Exclusion）**
* 当一个进程执行P(mutex) 后，mutex 变为0，其他进程无法通过
P(mutex)，从而阻塞。

<!-- question: operating-systems-003-Q59 -->

2. **避免竞态条件（Race Condition）**
* 同一时间只有一个进程能进入临界区。

<!-- question: operating-systems-003-Q60 -->

3. **无忙等（若为阻塞型信号量）**

* 阻塞等待，而不是死循环等待。

<!-- question: operating-systems-003-Q61 -->

4. **保证进程离开临界区后释放资源**
* V(mutex) 使其他等待进程被唤醒。

## **评分标准（10 分）**

* 给出正确的P/V 伪代码（4 分）
* 明确说明互斥性产生原因（3 分）
* 解释如何避免竞态条件（2 分）
* 提到阻塞式优势（额外1 分）

# **第五部分：综合题（15 分）**

**37. FIFO / LRU 缺页计算与对比（物理帧数=3）**
访问序列：
**0, 1, 2, 3, 2, 1, 0, 3, 2**

<!-- page: 8 -->

# **①FIFO 计算过程**
| 步骤| 引用页| 内存状态（3 帧）| 缺页？
|
| -- | --- | -------- | ------- |
| 1 | 0 | 0
| ✔
|

| 2 | 1 | 0 1
| ✔
|

| 3 | 2 | 0 1 2
| ✔
|

| 4 | 3 | 1 2 3
| ✔（0 替换）|

| 5 | 2 | 1 2 3
| ✘
|

| 6 | 1 | 1 2 3
| ✘
|

| 7 | 0 | 2 3 0
| ✔（1 替换）|

| 8 | 3 | 2 3 0
| ✘
|

| 9 | 2 | 2 3 0
| ✘
|

## **FIFO 缺页总数= 5**

# **②LRU 计算过程**
| 步骤| 引用页| 内存状态| 缺页？| 淘汰
|
| -- | --- | ----- | --- | ---------- |
| 1 | 0 | 0
| ✔| -
|

| 2 | 1 | 0 1 | ✔| -
|

| 3 | 2 | 0 1 2 | ✔| -
|

| 4 | 3 | 1 2 3 | ✔| 淘汰最久未使用的0 |

| 5 | 2 | 1 2 3 | ✘| -
|

| 6 | 1 | 1 2 3 | ✘| -
|

| 7 | 0 | 2 3 0 | ✔| 淘汰LRU=1 |

| 8 | 3 | 2 3 0 | ✘| -
|

| 9 | 2 | 2 3 0 | ✘| -
|
## **LRU 缺页总数= 5**

<!-- page: 9 -->

# **③两者对比与原理分析**

## **参考答案**

<!-- question: operating-systems-003-Q62 -->

1. 在此访问序列下，两者缺页次数均为**5 次**。

<!-- question: operating-systems-003-Q63 -->

2. FIFO 按进入顺序淘汰，与局部性不匹配时可能性能差。

<!-- question: operating-systems-003-Q64 -->

3. LRU 使用最近最久未使用策略，更贴近实际局部性访问模式。

<!-- question: operating-systems-003-Q65 -->

4. 本序列中局部性特征弱，造成两者缺页次数一致。

<!-- question: operating-systems-003-Q66 -->

5. LRU 不会出现Belady 异常，而FIFO 可能出现。

## **评分标准（15 分）**

* FIFO 过程正确（4 分）
* FIFO 缺页数正确（1 分）
* LRU 过程正确（4 分）
* LRU 缺页数正确（1 分）
* 对比分析正确（3 分）
* 提到局部性/Belady 异常加1 分（额外）
