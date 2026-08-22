---
source_id: algorithm-design-and-analysis-013
course_id: algorithm_design_and_analysis
title: 3-recurrence
original_file: "学科资料/算法设计与分析/PPT-英文版/3-recurrence.pdf"
document_role: note
year: 
locator_type: page
---

# 3-recurrence

<!-- page: 1 -->

Design and Analysis of Algorithms

Recurrence

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

1

<!-- page: 2 -->

Topics

• Induction
• Substitution Method
• Recursion-Tree Method
• Master Method

2

<!-- page: 3 -->

Induction

Induction used to prove that a statement T(n)
holds for all integers n:

•
Base case: prove T(0)
•
Assumption: assume that T(n-1) is true
•
Induction step: prove that T(n-1) implies T(n) for
all n>0

Strong induction: when we assume T(k) is true for
all 𝒌≤𝒏−𝟏and use this in proving T(n)

3

<!-- page: 4 -->

Integer Multiplication

Let 𝑋and 𝑌be n bit integers. 𝑋= 𝐴|𝐵and 𝑌=

𝐶|𝐷where A, B, C, and D are n/2 bit integers.

𝑛

𝑛

Simple Method: 𝑋𝑌= (𝐴2

2 + 𝐵)(𝐶2

2 + 𝐷)

𝑛

= 𝐴𝐶2𝑛+ 𝐴𝐷+ 𝐵𝐶2

2 + 𝐵𝐷

𝑛

Running Time Recurrence: 𝑇𝑛= 4𝑇

2 + 𝑏𝑛

How do we solve it?

4

<!-- page: 5 -->

Induction

The most general strategy:

Guess: the form of the solution.
Verify: by induction.

Ex.  T(n) = 4T(n/2) + bn

Base case T(1) = Q(1).
Guess O(n3) .
Assume that T(k) £ ck3 for k < n .
Prove T(n) £ cn3 by induction.

L2.
5

<!-- page: 6 -->

Induction

𝑛

𝑇𝑛= 4𝑇

2 + 𝑏𝑛

T(k) £ ck3 for k < n

3
+ 𝑏𝑛

𝑛

≤4𝑐

2

𝑐
2 𝑛3 + 𝑏𝑛

=

𝑐
2 𝑛3 −𝑏𝑛

= 𝑐𝑛3 −

≤𝑐𝑛3

𝑐
2 𝑛3 −𝑏𝑛≥0.

For example, if 𝑐≥2𝑏, then

This bound is not tight!

6

<!-- page: 7 -->

Induction

We also try that 𝑇𝑛= 𝑂(𝑛2).

Assume that 𝑇(𝑘) ≤𝑐𝑘2 for 𝑘< 𝑛:

𝑛

𝑇𝑛= 4𝑇

2 + 𝑏𝑛

2
+ 𝑏𝑛

𝑛

≤4𝑐

2

= 𝑐𝑛2 + 𝑏𝑛
≤𝑐𝑛2 X

7

<!-- page: 8 -->

A Tighter Upper Bound

Strengthen the inductive hypothesis.

Subtract a low-order term.
Inductive hypothesis: 𝑇𝑘≤𝑐1𝑘2 −𝑐2𝑘for 𝑘< 𝑛.

𝑛

𝑇𝑛= 4𝑇

2 + 𝑏𝑛

2
−𝑐2

𝑛

𝑛

≤4 𝑐1

2
+ 𝑏𝑛

2

= 𝑐1𝑛2 −2𝑐2𝑛+ 𝑏𝑛
= 𝑐1 𝑛2 −𝑐2𝑛−(𝑐2𝑛−𝑏𝑛)
≤𝑐1𝑛2 −𝑐2𝑛
For example, if 𝑐2 ≥𝑏, then 𝑐2𝑛−𝑏𝑛≥0.

𝑇𝑛=O(𝑛2)

8

<!-- page: 9 -->

Example of Substitution

Use algebraic manipulation to make an unknown
recurrence similar to what you have seenbefore.

Ex. T(n) =2T( 𝑛) + 𝑙𝑜𝑔𝑛

Set m = 𝑙𝑜𝑔𝑛and we have  T(2m) = 2T(2m/2) + m

Set S(m) = T(2m) and we have S(m) = 2S(m/2) + m

→S(m) = O(𝑚𝑙𝑜𝑔𝑚)

As a result, we have  T(n) = O(𝑙𝑜𝑔𝑛𝑙𝑜𝑔𝑙𝑜𝑔𝑛)

9

<!-- page: 10 -->

A Useful Recurrence Relation

• 𝑇𝑛= max number of compares to Merge-Sort a list of
size ≤𝑛
• 𝑇𝑛is monotone nondecreasing.

Merge-Sort recurrence

𝑇(𝑛) ≤ቊ
0,
𝑖𝑓𝑛= 1
𝑇𝑛/2
+ 𝑇𝑛/2
+ 𝑛, 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

Solution. 𝑇𝑛𝑖𝑠𝑂(𝑛𝑙𝑜𝑔𝑛)

Assorted proofs. We describe several ways to solve this
recurrence. Initially we assume n is a power of 2 and
replace “≤” with “=” in the recurrence.
10

<!-- page: 11 -->

Proof by Induction

If 𝑇(𝑛) satisfies the following recurrence, then
𝑇𝑛𝑖𝑠𝑂(𝑛𝑙𝑜𝑔𝑛).

assuming n is a

𝑇𝑛= ቊ
0,
𝑖𝑓𝑛= 1
2𝑇𝑛/2 + 𝑛, 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

power of 2

• Base case: when 𝑛= 1, 𝑇1 = 0 = 𝑛𝑙𝑜𝑔𝑛.
• Inductive hypothesis: assume 𝑇𝑛= 𝑛𝑙𝑜𝑔𝑛.
• Goal: show that 𝑇2𝑛= 2𝑛𝑙𝑜𝑔2𝑛
𝑇2𝑛= 2𝑇𝑛+ 2𝑛

= 2𝑛𝑙𝑜𝑔𝑛+ 2𝑛
= 2𝑛log 2𝑛−1 + 2𝑛
= 2𝑛𝑙𝑜𝑔(2𝑛)

11

<!-- page: 12 -->

Analysis of Merg-Sort Recurrence

If 𝑇(𝑛) satisfies the following recurrence, then
𝑇𝑛
≤𝑛𝑙𝑜𝑔𝑛.

𝑇(𝑛) ≤ቊ
0,
𝑖𝑓𝑛= 1
𝑇𝑛/2
+ 𝑇𝑛/2
+ 𝑛, 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

• Base case: n=1, 𝑇1 = 0.
• Define：𝑛1 = 𝑛/2 and 𝑛2 = 𝑛/2 .
• Induction step: assume true for 1, 2, …, n-1.

12

![image](assets/assets/algorithm-design-and-analysis-013/image-001.png)

<!-- page: 13 -->

Recursion Tree

If 𝑇(𝑛) satisfies the following recurrence, then
𝑇𝑛𝑖𝑠𝑂(𝑛𝑙𝑜𝑔𝑛).

assuming n is a

𝑇𝑛= ቊ
0,
𝑖𝑓𝑛= 1
2𝑇𝑛/2 + 𝑛, 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

power of 2

13

![image](assets/assets/algorithm-design-and-analysis-013/image-002.png)

<!-- page: 14 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2:

L2.
14

<!-- page: 15 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2 :

T(n)

L2.
15

<!-- page: 16 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2 :

n2

T(n/4)
T(n/4)

T(n/4)

L2.
16

<!-- page: 17 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2 :

n2

(𝑛/4)2
(𝑛/4)2
(𝑛/4)2

T(n/16)
T(n/16)
T(n/16)
T(n/16)
T(n/16)
T(n/16)
T(n/16)
T(n/16)
T(n/16)

L2.
17

<!-- page: 18 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2 :

n2

(𝑛/4)2
(𝑛/4)2
(𝑛/4)2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2

Q(1)

L2.
18

<!-- page: 19 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2 :

𝑛2

n2

(𝑛/4)2
(𝑛/4)2
(𝑛/4)2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2

Q(1)

L2.
19

<!-- page: 20 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2 :

𝑛2

n2

3
16 𝑛2

(𝑛/4)2
(𝑛/4)2
(𝑛/4)2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2

Q(1)

L2.
20

<!-- page: 21 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2 :

𝑛2

n2

3
16 𝑛2

(𝑛/4)2
(𝑛/4)2
(𝑛/4)2

9
256 𝑛2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2

Q(1)

L2.
21

<!-- page: 22 -->

Example of Recursion Tree

Solve T(n) = 3T(n/4) + n2 :

𝑛2

n2

3
16 𝑛2

(𝑛/4)2
(𝑛/4)2
(𝑛/4)2

9
256 𝑛2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2 (𝑛/16)2

(𝑛/16)2 (𝑛/16)2 (𝑛/16)2

…

2
+ ⋯
+ 𝑛log4 3

3
16 +
3
16

Total = 𝑛2 1 +

Q(1)

= Θ(𝑛2) geometric series

L2.
22

<!-- page: 23 -->

Geometric Series

23

![image](assets/assets/algorithm-design-and-analysis-013/image-003.png)

<!-- page: 24 -->

Master Method

Goal. Recipe for solving common divide-and-conquer
recurrences:

𝑇𝑛= 𝑎𝑇𝑛

𝑏+ 𝑓(𝑛)

With 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ(1).

Terms.
•
𝑎≥1 is the (integer) number of subproblems.
•
𝑏> 1 is the (integer) factor by which the subproblem size
decreases.
•
𝑓𝑛= work to divide and combine subproblems.

Recursion tree.
•
Number of levels:
•
Number of subproblems at level 𝑖:
•
Size of subproblem at level 𝑖:
•
Number of leaves:

<!-- page: 25 -->

Master Method

Goal. Recipe for solving common divide-and-conquer
recurrences:

𝑇𝑛= 𝑎𝑇𝑛

𝑏+ 𝑓(𝑛)

With 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ(1).

Terms.
•
𝑎≥1 is the (integer) number of subproblems.
•
𝑏> 1 is the (integer) factor by which the subproblem size
decreases.
•
𝑓𝑛= work to divide and combine subproblems.

Recursion tree.
•
Number of levels: 𝑘= log𝑏𝑛.
•
Number of subproblems at level 𝑖: 𝑎𝑖.
•
Size of subproblem at level 𝑖: 𝑛/𝑏𝑖.
•
Number of leaves: 𝑛log𝑏𝑎.

<!-- page: 26 -->

Master Theorem

Master Theorem. Suppose that 𝑇𝑛is a function on the
non-negative integers that satisfies the recurrence:

𝑇𝑛= 𝑎𝑇𝑛

𝑏+ 𝑓(𝑛)

with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏means either ہ

𝑛
/𝑏or 𝑛/𝑏. Then,

ۂ

Case 1. If 𝑓𝑛= 𝑂(𝑛𝑘) for some constant 𝑘< log𝑏𝑎, then
𝑇𝑛= Θ 𝑛log𝑏𝑎.

Ex. 𝑇𝑛= 3𝑇𝑛/2 + 5𝑛
𝑎= 3, 𝑏= 2, 𝑓𝑛= 5𝑛, 𝑘= 1, log𝑏𝑎= 1.58
𝑇𝑛= Θ 𝑛log2 3

<!-- page: 27 -->

Master Theorem

Master Theorem. Suppose that 𝑇𝑛is a function on the
non-negative integers that satisfies the recurrence:

𝑇𝑛= 𝑎𝑇𝑛

𝑏+ 𝑓(𝑛)

with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏means either

𝑛/𝑏or 𝑛/𝑏. Then,

Case 2. If 𝑓𝑛= Θ(𝑛𝑘𝑙𝑜𝑔𝑝𝑛) for 𝑝≥0 and 𝑘= log𝑏𝑎,
then 𝑇𝑛= Θ 𝑛𝑘𝑙𝑜𝑔𝑝+1𝑛.

Ex. 𝑇𝑛= 2𝑇𝑛/2 + 17𝑛log 𝑛
𝑎= 2, 𝑏= 2, 𝑓𝑛= 17𝑛log 𝑛, 𝑘= 1, 𝑝= 1, log𝑏𝑎= 1
𝑇𝑛= Θ 𝑛𝑙𝑜𝑔2 𝑛

<!-- page: 28 -->

Master Theorem

Master Theorem. Suppose that 𝑇𝑛is a function on the non-
negative integers that satisfies the recurrence:

𝑇𝑛= 𝑎𝑇𝑛

𝑏+ 𝑓(𝑛)

with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏means either

𝑛/𝑏or 𝑛/𝑏. Then,

Case 3. If 𝑓𝑛= Ω(𝑛𝑘) for some constant 𝑘> log𝑏𝑎, and if
𝑎𝑓(𝑛/𝑏) ≤𝑐𝑓(𝑛) for some constant 𝑐< 1 and all sufficiently
large 𝑛, then 𝑇𝑛= Θ 𝑓𝑛
.

Ex. 𝑇𝑛= 3𝑇𝑛/2 + 𝑛2

𝑎= 3, 𝑏= 2, 𝑓𝑛= 𝑛2, 𝑘= 2, log𝑏𝑎= 1.58
Regularity condition: 3(𝑛/2)2≤𝑐𝑛2 for 𝑐= 3/4
𝑇𝑛= Θ 𝑛2

<!-- page: 29 -->

Master Theorem

Master Theorem. Suppose that 𝑇𝑛is a function on the non-negative
integers that satisfies the recurrence:

𝑇𝑛= 𝑎𝑇𝑛

𝑏+ 𝑓(𝑛)

with 𝑇0 = 0 𝑎𝑛𝑑𝑇1 = Θ 1 , where 𝑛/𝑏means either 𝑛/𝑏or 𝑛/𝑏.

Case 1. If 𝑓𝑛= 𝑂(𝑛𝑘) for some constant 𝑘< log𝑏𝑎, then 𝑇𝑛= Θ 𝑛log𝑏𝑎.
Case 2. If 𝑓𝑛= Θ(𝑛𝑘𝑙𝑜𝑔𝑝𝑛) for 𝑝≥0 and 𝑘= log𝑏𝑎, then 𝑇𝑛=
Θ 𝑛𝑘𝑙𝑜𝑔𝑝+1𝑛.
Case 3. If 𝑓𝑛= Ω(𝑛𝑘) for some constant 𝑘> log𝑏𝑎, and if 𝑎𝑓(𝑛/𝑏) ≤𝑐𝑓(𝑛)
for some constant 𝑐< 1 and all sufficiently large 𝑛, then 𝑇𝑛= Θ 𝑓𝑛
.

<!-- page: 30 -->

Master Theorem Need Not Apply

Gaps in master theorem
• Number of subproblems must be a constant.
𝑇𝑛= 𝑛𝑇𝑛/2 + 𝑛2

• Number of subproblems must be ≥1.

𝑇𝑛= 1

2 𝑇𝑛/2 + 𝑛2

• Non-polynomial separation between 𝑓(𝑛) and log 𝑛.

𝑇𝑛= 2𝑇𝑛/2 +
𝑛
𝑙𝑜𝑔𝑛
• 𝑓(𝑛) is not positive.
𝑇𝑛= 2𝑇𝑛/2 −𝑛2

• Regularity condition does not hold.
𝑇𝑛= 𝑇𝑛/2 + n(2 −cos 𝑛)
