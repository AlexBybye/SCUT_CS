---
source_id: algorithm-design-and-analysis-016
course_id: algorithm_design_and_analysis
title: 4-divideConquer
original_file: "学科资料/算法设计与分析/PPT-英文版/4-divideConquer-2.pdf"
document_role: note
year: 
locator_type: page
---

# 4-divideConquer

<!-- page: 1 -->

Design and Analysis ofAlgorithms

Divide-and-Conquer

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

<!-- page: 2 -->

Topics

• Counting Inversions
• Matrix Multiplication
• Randomized Quick-Sort

<!-- page: 3 -->

Counting Inversions

Music site tries to match your song preferences with others.
• You rank n songs.
• Music site consults database to find people with similar tastes.

Similarity metric: number of inversions between two rankings.
• My rank: 1, 2, …, n.
• Your rank: 𝑎1, 𝑎2, … , 𝑎𝑛.
• Songs 𝑖and 𝑗are inverted if 𝑖< 𝑗, but 𝑎𝑖> 𝑎𝑗.

Brute force: check all Θ(𝑛2) pairs.

<!-- page: 4 -->

Counting Inversions: divide-and-conquer

• Divide: separate list into two halves A and B.
• Conquer: ？
• Combine: ？

<!-- page: 5 -->

Counting Inversions: divide-and-conquer

• Divide: separate list into two halves A and B.
• Conquer: recursively count inversions in each list.
• Combine: count inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Return sum of three counts.

<!-- page: 6 -->

Counting Inversions: how to combine two
sub-problems?

Q. How to count inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵?
A. Easy if A and B are sorted!

Algorithm:
•
Sort A and B.
•
For each element 𝑏∈𝐵,
- Binary search in A to find the elements in A greater than b.

<!-- page: 7 -->

Counting Inversions: how to combine two
sub-problems?

Count inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵, assuming A and B
are sorted.
• Scan A and B from left to right.
• Compare 𝑎𝑖and 𝑏𝑗.
• If 𝑎𝑖< 𝑏𝑗, then 𝑎𝑖is not inverted with any element left in B.
• If 𝑎𝑖> 𝑏𝑗, then 𝑏𝑗is inverted with every element left in A.
• Append smaller element to sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-001.png)

<!-- page: 8 -->

Counting Inversions: Merge-and-Count

How about the running time?

![image](assets/assets/algorithm-design-and-analysis-016/image-002.png)

<!-- page: 9 -->

Counting Inversions: algorithm implementation

Input. List L.
Output. Number of inversions in L, and L in sorted order.

Sort-and-Count(L)
----------------------------------------------------
If (list L has one element)

How about the
running time T(n)?

Return (0, L).

Divide the list into two halves A and B.
(𝑟𝐴, 𝐴) ←Sort-and-Count(A).
(𝑟𝐵, 𝐵) ←Sort-and-Count(B).
(𝑟𝐴𝐵, 𝐿) ←Merge-and-Count(A, B).

Return (𝑟𝐴+𝑟𝐵+𝑟𝐴𝐵, L).

<!-- page: 10 -->

Counting Inversions: algorithm analysis

The worst-case running time T(n) satisfies the recurrence:

𝑇𝑛= ？

<!-- page: 11 -->

Counting Inversions: algorithm analysis

The worst-case running time T(n) satisfies the recurrence:

𝑇𝑛= ቊΘ(1),
𝑖𝑓𝑛= 1
𝑇𝑛/2
+ 𝑇𝑛/2
+ Θ(𝑛),
𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

Proposition. The Sort-and-Count algorithm counts the
number of inversions in a permutation of size n in 𝑂(𝑛𝑙𝑜𝑔𝑛)
time.

<!-- page: 12 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-003.png)

<!-- page: 13 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-004.png)

<!-- page: 14 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-005.png)

<!-- page: 15 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-006.png)

<!-- page: 16 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-007.png)

<!-- page: 17 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-008.png)

<!-- page: 18 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-009.png)

<!-- page: 19 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-010.png)

<!-- page: 20 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-011.png)

<!-- page: 21 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-012.png)

<!-- page: 22 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-013.png)

<!-- page: 23 -->

Merge-and-Count Demo

Given two sorted lists A and B,
• Count number of inversions (a, b) with 𝑎∈𝐴and 𝑏∈𝐵.
• Merge A and B into sorted list C.

![image](assets/assets/algorithm-design-and-analysis-016/image-014.png)

<!-- page: 24 -->

Matrix Multiplication

Matrix multiplication. Given two 𝑛-by-𝑛matrices 𝐴and 𝐵,
compute 𝐶= 𝐴𝐵.

𝑛

𝑐𝑖𝑗= ෍

𝑎𝑖𝑘𝑏𝑘𝑗

𝑘=1

<!-- page: 25 -->

Block Matrix Multiplication

![image](assets/assets/algorithm-design-and-analysis-016/image-015.png)

<!-- page: 26 -->

Block Matrix Multiplication: Warmup

To multiply two 𝑛-by-𝑛matrices 𝐴and 𝐵:
• Divide: partition 𝐴and 𝐵into
𝑛

2-by-
𝑛

2 blocks.

• Conquer: multiply 8 pairs of
𝑛

2-by-
𝑛

2 matrices, recursively.
• Combine: add appropriate products using 4 matrix
additions.

8 matrix multiplications

𝑛-by-𝑛matrices

𝑛
2-by-𝑛
2 matrices

4 matrix additions
Running time. 𝑇𝑛= ？

![image](assets/assets/algorithm-design-and-analysis-016/image-016.png)

<!-- page: 27 -->

Block Matrix Multiplication: Warmup

To multiply two 𝑛-by-𝑛matrices 𝐴and 𝐵:
• Divide: partition 𝐴and 𝐵into
𝑛

2-by-
𝑛

2 blocks.

• Conquer: multiply 8 pairs of
𝑛

2-by-
𝑛

2 matrices, recursively.
• Combine: add appropriate products using 4 matrix
additions.

8 matrix multiplications

𝑛-by-𝑛matrices

𝑛
2-by-𝑛
2 matrices

4 matrix additions
Running time. 𝑇𝑛= 8𝑇

𝑛

2 + Θ 𝑛2
⇒
𝑇𝑛=?

![image](assets/assets/algorithm-design-and-analysis-016/image-017.png)

<!-- page: 28 -->

Block Matrix Multiplication: Warmup

To multiply two 𝑛-by-𝑛matrices 𝐴and 𝐵:
• Divide: partition 𝐴and 𝐵into
𝑛

2-by-
𝑛

2 blocks.

• Conquer: multiply 8 pairs of
𝑛

2-by-
𝑛

2 matrices, recursively.
• Combine: add appropriate products using 4 matrix
additions.

8 matrix multiplications

𝑛-by-𝑛matrices

𝑛
2-by-𝑛
2 matrices

4 matrix additions
Running time. Apply Case 1 of the master theorem.

𝑇𝑛= 8𝑇𝑛

2 + Θ 𝑛2
⇒
𝑇𝑛= Θ 𝑛3

![image](assets/assets/algorithm-design-and-analysis-016/image-018.png)

<!-- page: 29 -->

Strassen’s Trick

Key idea. Can multiply two 2-by-2 matrices via 7 scalar
matrix multiplications (plus 11 additions and 7 subtractions).

![image](assets/assets/algorithm-design-and-analysis-016/image-019.png)

<!-- page: 30 -->

Strassen’s Trick

𝑛

2-by-
𝑛

Key idea. Can multiply two n-by-n matrices via 7

2
multiplications (plus 11 additions and 7 subtractions).

![image](assets/assets/algorithm-design-and-analysis-016/image-020.png)

<!-- page: 31 -->

Strassen’s Algorithm

Strassen (𝑛, 𝐴, 𝐵)
If (𝑛= 1)  Return 𝐴× 𝐵.
Partition 𝐴and 𝐵into

𝑛

2-by-
𝑛

2 blocks.
𝑃1 ←Strassen (n/2, 𝐴11, 𝐵12 −𝐵22).
𝑃2 ←Strassen (n/2, 𝐴11 + 𝐴12, 𝐵22).
𝑃3 ←Strassen (n/2, 𝐴21 + 𝐴22, 𝐵11).
𝑃4 ←Strassen (n/2, 𝐴22, 𝐵21 −𝐵11).
𝑃5 ←Strassen (n/2, 𝐴11 + 𝐴22, 𝐵11 + 𝐵22).
𝑃6 ←Strassen (n/2, 𝐴12 −𝐴22, 𝐵21 + 𝐵22).
𝑃7 ←Strassen (n/2, 𝐴11 −𝐴21, 𝐵11 + 𝐵12).
𝐶11 = 𝑃5 + 𝑃4 −𝑃2 + 𝑃6 .
𝐶12 = 𝑃1 + 𝑃1 .
𝐶21 = 𝑃3 + 𝑃4 .
𝐶22 = 𝑃1 + 𝑃5 −𝑃3 −𝑃7 .
Return 𝐶.

<!-- page: 32 -->

Analysis of Strassen’s Algorithm

Theorem. Strassen’s algorithm requires 𝑂(𝑛2.81) arithmetic
operations to multiply two n-by-n matrices.

Pf.
Apply Case 1 of the master theorem to the recurrence:

𝑇𝑛= 7𝑇𝑛

2 + Θ(𝑛2)

⇒𝑇𝑛= Θ(𝑛log2 7)

If n is not a power of 2, could pad matrices with zeros.

<!-- page: 33 -->

Randomized Quick-Sort

3-way partition array so that:
•
Pivot element p is in place.
•
Smaller elements in left subarray L.
•
Equal elements in middle subarray M.
•
Larger elements in right subarray R.

Recur in both left and right subarrays.

Randomized-Quick-Sort (𝐴)
if list 𝐴has zero or one element

Return.
Pick pivot 𝑝∈𝐴uniformly at random.
(𝐿, 𝑀, 𝑅) ←Partition-3-Way (𝐴, 𝑝).
Randomized-Quick-Sort (𝐿).
Randomized-Quick-Sort (𝑅).

3-way partitioning
can be done in-place
(using n compares)

<!-- page: 34 -->

Analysis of Randomized Quick-Sort

Proposition. The expected number of compares to Quick-
Sort an array of n distinct elements is 𝑂(𝑛𝑙𝑜𝑔𝑛).

Randomized-Quick-Sort (𝐴)
if list 𝐴has zero or one element

Return.
Pick pivot 𝑝∈𝐴uniformly at random.
(𝐿, 𝑀, 𝑅) ←Partition-3-Way (𝐴, 𝑝).
Randomized-Quick-Sort (𝐿).
Randomized-Quick-Sort (𝑅).

<!-- page: 35 -->

Analysis of Randomized Quick-Sort

Proposition. The expected number of compares to Quick-
Sort an array of n distinct elements is 𝑂(𝑛𝑙𝑜𝑔𝑛).

Pf. Consider BST representation of partitioning elements.

![image](assets/assets/algorithm-design-and-analysis-016/image-021.png)

<!-- page: 36 -->

Analysis of Randomized Quick-Sort

Proposition. The expected number of compares to Quick-
Sort an array of n distinct elements is 𝑂(𝑛𝑙𝑜𝑔𝑛).

Pf. Consider BST representation of partitioning elements.
• An element is compared with only its ancestors and
descendants.

![image](assets/assets/algorithm-design-and-analysis-016/image-022.png)

<!-- page: 37 -->

Analysis of Randomized Quick-Sort

Proposition. The expected number of compares to Quick-
Sort an array of n distinct elements is 𝑂(𝑛𝑙𝑜𝑔𝑛).

Pf. Consider BST representation of partitioning elements.
• An element is compared with only its ancestors and
descendants.

![image](assets/assets/algorithm-design-and-analysis-016/image-023.png)

<!-- page: 38 -->

Analysis of Randomized Quick-Sort

Proposition. The expected number of compares to Quick-
Sort an array of n distinct elements is 𝑂(𝑛𝑙𝑜𝑔𝑛).

Pf. Consider BST representation of partitioning elements.
• An element is compared with only its ancestors and
descendants.
• Pr[𝑎𝑖and 𝑎𝑗are compared] = 2/(j-i+1), where i<j.

![image](assets/assets/algorithm-design-and-analysis-016/image-024.png)

<!-- page: 39 -->

Analysis of Randomized Quick-Sort

Proposition. The expected number of compares to Quick-
Sort an array of n distinct elements is 𝑂(𝑛𝑙𝑜𝑔𝑛).

Pf. Consider BST representation of partitioning elements.
• An element is compared with only its ancestors and
descendants.
• Pr[𝑎𝑖and 𝑎𝑗are compared] = 2/(j-i+1), where i<j.

𝑛
2
𝑗−𝑖+1
= 2 σ𝑖

• Expected number of compares = σ𝑖
𝑛σ𝑗=𝑖+1

𝑛−𝑖+1 1

𝑛σ𝑗=2

𝑗
≤2𝑛σ𝑗=1

𝑛
1
𝑗
~2𝑛׬𝑥=1

𝑛
1
𝑥𝑑𝑥= 2𝑛𝑙𝑛𝑛
