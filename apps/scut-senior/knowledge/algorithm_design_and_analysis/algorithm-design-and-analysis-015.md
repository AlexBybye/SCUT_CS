---
source_id: algorithm-design-and-analysis-015
course_id: algorithm_design_and_analysis
title: 4-divideConquer
original_file: "学科资料/算法设计与分析/PPT-英文版/4-divideConquer-1.pdf"
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

• Divide-and-Conquer Paradigm
• Closest Pair of Points
• Median and Selection Problems

<!-- page: 3 -->

Divide-and-Conquer Paradigm

Divide-and-Conquer.
• Divide problem into several subproblems.
• Solve each subproblem recursively.
• Combine solution to subproblems into overall solution.

Most common usage.
• Divide problem of size n into two subproblems of size n/2
in linear time.
• Solve two subproblems recursively.
• Combine two solutions into overall solution in linear time.

Consequence.
• Brute force: Θ(𝑛2).
• Divide-and-conquer: Θ(𝑛𝑙𝑜𝑔𝑛).

<!-- page: 4 -->

Closest Pair of Points

Closest pair problem. Given n points in the plane, fine a
pair of points with the smallest Euclidean distance between
them.

Fundamental geometric primitive.
• Graphics,
computer
vision,
geographic
information
systems, molecular modeling, air traffic control.
• Special case of nearest neighbor.

<!-- page: 5 -->

Closest Pair of Points

Closest pair problem. Given n points in the plane, fine a
pair of points with the smallest Euclidean distance between
them.

Brute force. Check all pairs with Θ 𝑛2 distance calculations.

1D version. Easy 𝑂(𝑛𝑙𝑜𝑔𝑛) algorithm if points are on a line.

Nondegeneracy assumption. No two points have the same

x-coordinate.

<!-- page: 6 -->

Closest Pair of Points: First Attempt

Sorting solution.
• Sort by x-coordinate and consider nearby points.
• Sort by y-coordinate and consider nearby points.

<!-- page: 7 -->

Closest Pair of Points: First Attempt

Sorting solution.
• Sort by x-coordinate and consider nearby points.
• Sort by y-coordinate and consider nearby points.

<!-- page: 8 -->

Closest Pair of Points: Second Attempt

Divide. Subdivide region into 4 quadrants.

<!-- page: 9 -->

Closest Pair of Points: Second Attempt

Divide. Subdivide region into 4 quadrants.
Obstacle. Impossible to ensure n/4 points in each piece.

![image](assets/assets/algorithm-design-and-analysis-015/image-001.png)

<!-- page: 10 -->

Closest Pair of Points: Divide-and-
Conquer Algorithm

•
Divide: draw vertical line L so that n/2 points on each side.
•
Conquer: find closet pair in each side recursively.
•
Combine: find closet pair with one point in each side.
•
Return best of 3 solutions.

![image](assets/assets/algorithm-design-and-analysis-015/image-002.png)

<!-- page: 11 -->

How to Find Closest Pair with One
Point in Each Side?

Find closest pair with one point in each side, assuming that
distance < 𝛿.
•
Observation: only need to consider points within 𝛿of line L.

![image](assets/assets/algorithm-design-and-analysis-015/image-003.png)

<!-- page: 12 -->

How to Find Closest Pair with One
Point in Each Side?

Find closest pair with one point in each side, assuming that
distance < 𝛿.
•
Observation: only need to consider points within 𝛿of line L.
•
Sort points in 2𝛿-strip by their y-coordinate.
•
Only check distances of those within 15 positions in sorted list.

![image](assets/assets/algorithm-design-and-analysis-015/image-004.png)

<!-- page: 13 -->

How to Find Closest Pair with One
Point in Each Side?

Def. Let 𝑠𝑖be the point in the 2𝛿-strip, with
the i-th smallest y-coordinate.

Claim. If 𝑖−𝑗≥16, then the distance
between 𝑠𝑖and 𝑠𝑗is at least 3

2 𝛿.

Pf.
•
No two points lie in same 1

2 𝛿by 1
2 𝛿box.
•
Two points at least 3 rows apart
•
have distance ≥3(1

2 𝛿).

Note. The value of 15 can be reduced. The
important thing is that it is an absolute constant.

![image](assets/assets/algorithm-design-and-analysis-015/image-005.png)

<!-- page: 14 -->

Closest Pair of Points: Divide-and-
Conquer Algorithm

Closest-Pair (𝑝1, 𝑝2,…, 𝑝𝑛)
• Compute separation line L such that half the
points are on each side of the line.
• 𝛿1 ←Closest-Pair (points in left half).
• 𝛿2 ←Closest-Pair (points in right half).
• 𝛿←min{𝛿1, 𝛿2}.
• Delete all points further than 𝛿from Line L.
• Sort remaining points by y-coordinate.
• Scan points in y-order and compare distance
between each point and next 15 neighbors. If
any of these distances is less than 𝛿, update 𝛿.
Return 𝛿.

𝑻𝒏= ？

<!-- page: 15 -->

Closest Pair of Points: Divide-and-
Conquer Algorithm

Closest-Pair (𝑝1, 𝑝2,…, 𝑝𝑛)
• Compute separation line L such that half the
points are on each side of the line.
• 𝛿1 ←Closest-Pair (points in left half).
• 𝛿2 ←Closest-Pair (points in right half).
• 𝛿←min{𝛿1, 𝛿2}.
• Delete all points further than 𝛿from Line L.
• Sort remaining points by y-coordinate.
• Scan points in y-order and compare distance
between each point and next 15 neighbors. If
any of these distances is less than 𝛿, update 𝛿.
Return 𝛿.

𝑂(𝑛𝑙𝑜𝑔𝑛)

2𝑇(𝑛/2)

𝑂(𝑛)
𝑂(𝑛𝑙𝑜𝑔𝑛)

𝑂(𝑛)

𝑻𝒏= ？

<!-- page: 16 -->

Closest Pair of Points: Analysis

Theorem. The divide-and-conquer algorithm for finding the
closest pair of points in the plane can be implemented in
？time.

𝑇𝑛= ቊ
Θ(1),
𝑖𝑓𝑛= 1
𝑇𝑛/2
+ 𝑇𝑛/2
+ 𝑂(𝑛𝑙𝑜𝑔𝑛), 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

<!-- page: 17 -->

Closest Pair of Points: Analysis

Theorem. The divide-and-conquer algorithm for finding the
closest pair of points in the plane can be implemented in
𝑂(𝑛𝑙𝑜𝑔2𝑛) time.

𝑇𝑛= ቊ
Θ(1),
𝑖𝑓𝑛= 1
𝑇𝑛/2
+ 𝑇𝑛/2
+ 𝑂(𝑛𝑙𝑜𝑔𝑛), 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

Master Theorem - Case 2. If 𝑓𝑛= Θ(𝑛𝑘𝑙𝑜𝑔𝑝𝑛) for 𝑝≥0
and 𝑘= log𝑏𝑎, then 𝑇𝑛= Θ 𝑛𝑘𝑙𝑜𝑔𝑝+1𝑛.

<!-- page: 18 -->

Median and Selection Problems

Selection. Given n elements, find k-th smallest.
• Minimum: 𝑘=1; maximum: 𝑘=n.
• Median: 𝑘= (𝑛+ 1)/2 .
• 𝑂(𝑛) compares for min or max.
• 𝑂(𝑛𝑙𝑜𝑔𝑛) compares by sorting.

Applications. Find the “top k”…

Can we do it with 𝑂(𝑛) compares?

<!-- page: 19 -->

Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray - the one containing the k-th smallest
element.

Quick-Select (𝐴, 𝑘)
Pick pivot 𝑝∈𝐴uniformly at random.
(𝐿, 𝑀, 𝑅) ←Partition-3-Way (𝐴, 𝑝).
if 𝑘≤𝐿
Return Quick-Select (𝐿, 𝑘).
else if 𝑘> 𝐿+ 𝑀
Return Quick-Select (𝑅, 𝑘−𝐿−𝑀).
else Return 𝑝.

3-way partitioning
can be done in-place
(using n-1 compares)

<!-- page: 20 -->

An Example of Quick-Select

Quick-Select (𝐴, 𝑘)
Pick pivot 𝑝∈𝐴uniformly at random.
(𝐿, 𝑀, 𝑅) ←Partition-3-Way (𝐴, 𝑝).
if 𝑘≤𝐿
Return Quick-Select (𝐿, 𝑘).
else if 𝑘> 𝐿+ 𝑀
Return Quick-Select (𝑅, 𝑘−𝐿−𝑀).
else Return 𝑝.

Example: select the 8-th smallest element

<!-- page: 21 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 22 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 23 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 24 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 25 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 26 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 27 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 28 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 29 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 30 -->

An Example of Quick-Select

3-way partition array so that:
• Pivot element p is in place.
• Smaller elements in left subarray L.
• Equal elements in middle subarray M.
• Larger elements in right subarray R.

Recur in one subarray-the one containing the k-th smallest
element.

<!-- page: 31 -->

Quick-Select Analysis

Intuition. Split candy bar uniformly       expected size of
larger piece is ？

<!-- page: 32 -->

Quick-Select Analysis

Intuition. Split candy bar uniformly       expected size of
larger piece is ¾.
𝑇𝑛≤𝑇

3
4 𝑛+ ？

<!-- page: 33 -->

Quick-Select Analysis

Intuition. Split candy bar uniformly       expected size of
larger piece is ¾.
𝑇𝑛≤𝑇

3
4 𝑛+ 𝑛
𝑇(𝑛) ≤？

<!-- page: 34 -->

Quick-Select Analysis

Intuition. Split candy bar uniformly       expected size of
larger piece is ¾.
𝑇𝑛≤𝑇

3
4 𝑛+ 𝑛
𝑇(𝑛) ≤4𝑛

Def. 𝑇𝑛, 𝑘= expected # compares to select k-th smallest
in an array of size ≤𝑛.
Def. 𝑇𝑛= max

𝑘
𝑇(𝑛, 𝑘).

<!-- page: 35 -->

Quick-Select Analysis

Proposition. 𝑇(𝑛) ≤4𝑛
Pf.
• Assume true for 1,2,…,n-1.
• 𝑇(𝑛) satisfies for the following recurrence:

𝑇𝑛≤𝑛+ 2

𝑛[𝑇𝑛

2 + ⋯+ 𝑇𝑛−3 + 𝑇𝑛−2 + 𝑇(𝑛−1)]

<!-- page: 36 -->

Quick-Select Analysis

Proposition. 𝑇(𝑛) ≤4𝑛
Pf.
• Assume true for 1,2,…,n-1.
• 𝑇(𝑛) satisfies for the following recurrence:

𝑇𝑛≤𝑛+ 2

𝑛[𝑇𝑛

2 + ⋯+ 𝑇𝑛−3 + 𝑇𝑛−2 + 𝑇(𝑛−1)]

2
𝑛[

4𝑛
2 + ⋯+ 4 𝑛−3 + 4 𝑛−2 + 4(𝑛−1)]

≤𝑛+

3𝑛
4 )
= 4𝑛.

≤𝑛+ 4(

can assume we always recur on
largest subarray since 𝑇(𝑛) is
monotonic and we are trying to
get an upper bound

<!-- page: 37 -->

Selection in Worst Case (Linear Time)

Goal. Find pivot element 𝑝that divides list of n elements
into two pieces so that each piece is guaranteed to have

7
10 𝑛elements.

≤

How to find approximate median in linear time?

<!-- page: 38 -->

Selection in Worst Case (Linear Time)

Goal. Find pivot element 𝑝that divides list of n elements
into two pieces so that each piece is guaranteed to have

7
10 𝑛elements.

≤

How to find approximate median in linear time?
Recursively compute median of ≤

2
10 𝑛elements.

Θ(1),
𝑖𝑓𝑛= 1

𝑇
7
10 𝑛
+ 𝑇
2
10 𝑛
+ Θ(𝑛), 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

𝑇𝑛= ൞

two sub-problems of
different sizes

<!-- page: 39 -->

Choosing the Pivot Element

• Divide 𝑛elements into 𝑛/5 groups of 5 elements each.

![image](assets/assets/algorithm-design-and-analysis-015/image-006.png)

<!-- page: 40 -->

Choosing the Pivot Element

• Divide 𝑛elements into 𝑛/5 groups of 5 elements each.
• Find median of each group.

![image](assets/assets/algorithm-design-and-analysis-015/image-007.png)

<!-- page: 41 -->

Choosing the Pivot Element

• Divide 𝑛elements into 𝑛/5 groups of 5 elements each.
• Find median of each group.
• Find median of 𝑛/5 medians recursively.
• Use median-of-medians as pivot element.

![image](assets/assets/algorithm-design-and-analysis-015/image-008.png)

<!-- page: 42 -->

Median-of-Medians Selection Algorithm

MoM-Select (𝐴, 𝑘)
----------------------------------------------------------------------------
𝑛←𝐴.
if 𝑛< 50 Return 𝑘-th smallest of element of 𝐴via Merge-
Sort.

Group 𝐴into 𝑛/5 groups of 5 elements each.
𝐵←median of each group of 5.
𝑝←MoM-Select (B, 𝑛/10 ).

median of medians

(𝐿, 𝑀, 𝑅) ←Partition-3-Way (𝐴, 𝑝).
if 𝑘≤𝐿
Return MoM-Select (𝐿, 𝑘).
else if 𝑘> 𝐿+ 𝑀
Return MoM-Select (𝑅, 𝑘−𝐿−𝑀).
else Return 𝑝.

<!-- page: 43 -->

Analysis of Median-of-Medians
Selection Algorithm
• At least half of 5-element medians ≤𝑝.

![image](assets/assets/algorithm-design-and-analysis-015/image-009.png)

<!-- page: 44 -->

Analysis of Median-of-Medians
Selection Algorithm
• At least half of 5-element medians ≤𝑝.
At least 𝑛/5 /2 = 𝑛/10 medians ≤𝑝.

![image](assets/assets/algorithm-design-and-analysis-015/image-010.png)

<!-- page: 45 -->

Analysis of Median-of-Medians
Selection Algorithm
• At least half of 5-element medians ≤𝑝.
At least 𝑛/5 /2 = 𝑛/10 medians ≤𝑝.
At least 3 𝑛/10 elements ≤𝑝.

![image](assets/assets/algorithm-design-and-analysis-015/image-011.png)

<!-- page: 46 -->

Analysis of Median-of-Medians
Selection Algorithm
• At least half of 5-element medians ≥𝑝.

![image](assets/assets/algorithm-design-and-analysis-015/image-012.png)

<!-- page: 47 -->

Analysis of Median-of-Medians
Selection Algorithm
• At least half of 5-element medians ≥𝑝.
Symmetrically, at least 𝑛/10 medians ≥𝑝.

![image](assets/assets/algorithm-design-and-analysis-015/image-013.png)

<!-- page: 48 -->

Analysis of Median-of-Medians
Selection Algorithm
• At least half of 5-element medians ≥𝑝.
Symmetrically, at least 𝑛/10 medians ≥𝑝.
At least 3 𝑛/10 elements ≥𝑝.

![image](assets/assets/algorithm-design-and-analysis-015/image-014.png)

<!-- page: 49 -->

Median-of-Medians Selection
Algorithm Recurrence

Median-of-medians selection algorithm recurrence.
• Select called recursively with 𝑛/5 elements to compute
MoM 𝑝.
• At least 3 𝑛/10 elements ≤𝑝.
• At least 3 𝑛/10 elements ≥𝑝.
• Select called recursively with at most n −3 𝑛/10
elements.

Def. 𝑇𝑛= max # compares on an array of ≤𝑛elements.

6𝑛,
𝑖𝑓𝑛< 50

𝑇
𝑛
5
+ 𝑇𝑛−3
𝑛
10
+ 11

𝑇𝑛≤ቐ

5 𝑛, 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

median of

recursive
select

computing median of 5 (6
compares per group)
partitioning (n compares)

medians

<!-- page: 50 -->

Median-of-Medians Selection
Algorithm Recurrence

6𝑛,
𝑖𝑓𝑛< 50

𝑇
𝑛
5
+ 𝑇𝑛−3
𝑛
10
+ 11

𝑇𝑛≤ቐ

5 𝑛, 𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

Claim. 𝑇𝑛≤44𝑛.
• Base case: 𝑇𝑛≤6𝑛for 𝑛< 50 (Merge-Sort).
• Inductive hypothesis: assume true for 1,2,…, n-1.
• Inductive step: for 𝑛≥50, we have:

𝑇𝑛≤𝑇
𝑛
5
+ 𝑇𝑛−3
𝑛
10
+ 11

5 𝑛

𝑛

𝑛
10
+

11
5 𝑛

≤44

5
+ 44 𝑛−3

𝑛

5 + 44𝑛−44(
𝑛

4) +
11
5 𝑛

≤44

= 44𝑛.

for 𝑛≥50, 3
𝑛
10 ≥𝑛/4
