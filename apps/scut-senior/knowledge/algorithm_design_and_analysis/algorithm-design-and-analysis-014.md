---
source_id: algorithm-design-and-analysis-014
course_id: algorithm_design_and_analysis
title: 3_tutorial
original_file: "学科资料/算法设计与分析/PPT-英文版/3_tutorial.pdf"
document_role: note
year: 
locator_type: page
---

# 3_tutorial

<!-- page: 1 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

<!-- page: 2 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

T(n)

<!-- page: 3 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

n2

T(n/4)
T(n/2)

<!-- page: 4 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

n2

(n/4)2
(n/2)2

T(n/16)
T(n/8)
T(n/8)
T(n/4)

<!-- page: 5 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

n2

(n/4)2
(n/2)2

(n/16)2
(n/8)2
(n/8)2
(n/4)2

Q(1)

<!-- page: 6 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

n2
𝑛2

(n/4)2
(n/2)2

(n/16)2
(n/8)2
(n/8)2
(n/4)2

Q(1)

<!-- page: 7 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

𝑛2

n2

5
16 𝑛2

(n/4)2
(n/2)2

(n/16)2
(n/8)2
(n/8)2
(n/4)2

Q(1)

<!-- page: 8 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

𝑛2

n2

5
16 𝑛2

(n/2)2

(n/4)2

25
256 𝑛2

(n/16)2
(n/8)2
(n/8)2
(n/4)2

…

Q(1)

<!-- page: 9 -->

1. 采用Recursion-Tree方法求解递推式
T(n) = T(n/4) + T(n/2) + n2.

𝑛2

n2

5
16 𝑛2

(n/2)2

(n/4)2

25
256 𝑛2

(n/16)2
(n/8)2
(n/8)2
(n/4)2

…

Q(1)

2
+ ⋯
+ 𝑂(𝑛)

Total = 𝑛2 1 + 5

16 +
5
16

= 𝑂(𝑛2)

geometric series

<!-- page: 10 -->

2. 采用Master Theorem求解下列递推式.

a)T(n) = 4T(n/2) + n

Master Theorem. Suppose that 𝑇𝑛is a
function on the non-negative integers that
satisfies the recurrence:

b)T(n) = 4T(n/2) + n2

𝑇𝑛= 𝑎𝑇𝑛/𝑏+ 𝑓(𝑛)
with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏
means either 𝑛/𝑏or 𝑛/𝑏.

c) T(n) = 4T(n/2) + n3

Case 1. If 𝑓𝑛= 𝑂(𝑛𝑘) for some constant
𝑘< log𝑏𝑎, then 𝑇𝑛= Θ 𝑛log𝑏𝑎.

d) T(n)=3T(n/4)+nlogn

Case 2. If 𝑓𝑛= Θ(𝑛𝑘𝑙𝑜𝑔𝑝𝑛) for 𝑝≥0 and
𝑘= log𝑏𝑎, then 𝑇𝑛= Θ 𝑛𝑘𝑙𝑜𝑔𝑝+1𝑛.

Case 3. If 𝑓𝑛= Ω(𝑛𝑘) for some constant
𝑘> log𝑏𝑎, and if 𝑎𝑓(𝑛/𝑏) ≤𝑐𝑓(𝑛) for
some constant 𝑐< 1 and all sufficiently large
𝑛, then 𝑇𝑛= Θ 𝑓𝑛
.

<!-- page: 11 -->

2. 采用Master Theorem求解下列递推式.

Master Theorem. Suppose that 𝑇𝑛is a
function on the non-negative integers that
satisfies the recurrence:

a)T(n) = 4T(n/2) + n

𝑇𝑛= 𝑎𝑇𝑛/𝑏+ 𝑓(𝑛)
with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏
means either 𝑛/𝑏or 𝑛/𝑏.

a = 4, b = 2,
nlogba= n2; and
f (n) = n = O(n1).
Case 1: 𝑘< 𝑙𝑜𝑔𝑏𝑎,
then T(n) = Θ(n2).

Case 1. If 𝑓𝑛= 𝑂(𝑛𝑘) for some constant
𝑘< log𝑏𝑎, then 𝑇𝑛= Θ 𝑛log𝑏𝑎.

Case 2. If 𝑓𝑛= Θ(𝑛𝑘𝑙𝑜𝑔𝑝𝑛) for 𝑝≥0 and
𝑘= log𝑏𝑎, then 𝑇𝑛= Θ 𝑛𝑘𝑙𝑜𝑔𝑝+1𝑛.

Case 3. If 𝑓𝑛= Ω(𝑛𝑘) for some constant
𝑘> log𝑏𝑎, and if 𝑎𝑓(𝑛/𝑏) ≤𝑐𝑓(𝑛) for
some constant 𝑐< 1 and all sufficiently large
𝑛, then 𝑇𝑛= Θ 𝑓𝑛
.

<!-- page: 12 -->

2. 采用Master Theorem求解下列递推式.

Master Theorem. Suppose that 𝑇𝑛is a
function on the non-negative integers that
satisfies the recurrence:

b) T(n) = 4T(n/2) + n2

𝑇𝑛= 𝑎𝑇𝑛/𝑏+ 𝑓(𝑛)
with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏
means either 𝑛/𝑏or 𝑛/𝑏.

a = 4, b = 2,
nlogba = n2; and
f (n) = n2.
Case 2: f (n) = (n2log0n),
and k = 2,
then T(n) = 𝛩(n2log n).

Case 1. If 𝑓𝑛= 𝑂(𝑛𝑘) for some constant
𝑘< log𝑏𝑎, then 𝑇𝑛= Θ 𝑛log𝑏𝑎.

Case 2. If 𝑓𝑛= Θ(𝑛𝑘𝑙𝑜𝑔𝑝𝑛) for 𝑝≥0 and
𝑘= log𝑏𝑎, then 𝑇𝑛= Θ 𝑛𝑘𝑙𝑜𝑔𝑝+1𝑛.

Case 3. If 𝑓𝑛= Ω(𝑛𝑘) for some constant
𝑘> log𝑏𝑎, and if 𝑎𝑓(𝑛/𝑏) ≤𝑐𝑓(𝑛) for
some constant 𝑐< 1 and all sufficiently large
𝑛, then 𝑇𝑛= Θ 𝑓𝑛
.

<!-- page: 13 -->

2. 采用Master Theorem求解下列递推式.

Master Theorem. Suppose that 𝑇𝑛is a
function on the non-negative integers that
satisfies the recurrence:

c) T(n) = 4T(n/2) + n3

𝑇𝑛= 𝑎𝑇𝑛/𝑏+ 𝑓(𝑛)
with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏
means either 𝑛/𝑏or 𝑛/𝑏.

a = 4, b = 2,
nlogba= n2; and
f (n) = n3.
Case 3: f (n) = 𝛺(n3),
and 4(n/2)3 ≤cn3 (reg.
cond.) for c = ½ ,
then T(n) = 𝛩(n3).

Case 1. If 𝑓𝑛= 𝑂(𝑛𝑘) for some constant
𝑘< log𝑏𝑎, then 𝑇𝑛= Θ 𝑛log𝑏𝑎.

Case 2. If 𝑓𝑛= Θ(𝑛𝑘𝑙𝑜𝑔𝑝𝑛) for 𝑝≥0 and
𝑘= log𝑏𝑎, then 𝑇𝑛= Θ 𝑛𝑘𝑙𝑜𝑔𝑝+1𝑛.

Case 3. If 𝑓𝑛= Ω(𝑛𝑘) for some constant
𝑘> log𝑏𝑎, and if 𝑎𝑓(𝑛/𝑏) ≤𝑐𝑓(𝑛) for
some constant 𝑐< 1 and all sufficiently large
𝑛, then 𝑇𝑛= Θ 𝑓𝑛
.

<!-- page: 14 -->

2. 采用Master Theorem求解下列递推式.

Master Theorem. Suppose that 𝑇𝑛is a
function on the non-negative integers that
satisfies the recurrence:

d) T(n)=3T(n/4)+nlogn

𝑇𝑛= 𝑎𝑇𝑛/𝑏+ 𝑓(𝑛)
with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏
means either 𝑛/𝑏or 𝑛/𝑏.

a = 3, b = 4,
nlogba= n0.793; and
f (n) = nlogn.
Case 3: f (n) = 𝛺(n1),
and 3(n/4)log(n/4) ≤
cnlogn (reg. cond.) for
c = 3/4,
then T(n) = 𝛩(nlogn).

Case 1. If 𝑓𝑛= 𝑂(𝑛𝑘) for some constant
𝑘< log𝑏𝑎, then 𝑇𝑛= Θ 𝑛log𝑏𝑎.

Case 2. If 𝑓𝑛= Θ(𝑛𝑘𝑙𝑜𝑔𝑝𝑛) for 𝑝≥0 and
𝑘= log𝑏𝑎, then 𝑇𝑛= Θ 𝑛𝑘𝑙𝑜𝑔𝑝+1𝑛.

Case 3. If 𝑓𝑛= Ω(𝑛𝑘) for some constant
𝑘> log𝑏𝑎, and if 𝑎𝑓(𝑛/𝑏) ≤𝑐𝑓(𝑛) for
some constant 𝑐< 1 and all sufficiently large
𝑛, then 𝑇𝑛= Θ 𝑓𝑛
.
