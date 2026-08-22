---
source_id: algorithm-design-and-analysis-006
course_id: algorithm_design_and_analysis
title: 10-approximation
original_file: "学科资料/算法设计与分析/PPT-英文版/10-approximation.pdf"
document_role: note
year: 
locator_type: page
---

# 10-approximation

<!-- page: 1 -->

Design and Analysis of Algorithms

Approximation Algorithms

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

1

<!-- page: 2 -->

Topics

• Load Balancing
• Center Selection
• Weighted Vertex Cover: Pricing Method
• Weighted Vertex Cover: LP Rounding

2

<!-- page: 3 -->

Load Balancing

Input. 𝑚identical machines; 𝑛jobs, job 𝑗has processing time 𝑡𝑗.
• Job 𝑗must run contiguously on one machine.
• A machine can process at most one job at a time.

Def. Let 𝑆[𝑖] be the subset of jobs assigned to machine 𝑖.
The load of machine 𝑖is  𝐿𝑖= σ𝑗∈𝑆[𝑖] 𝑡𝑗.

Def. The makespan is the maximum load on any machine 𝐿= 𝑚𝑎𝑥𝑖𝐿[𝑖].

Load balancing. Assign each job to a machine to minimize makespan.

3

<!-- page: 4 -->

Load Balancing on 2 Machines

Claim. Load balancing is hard even if 𝑚= 2 machines.

4

<!-- page: 5 -->

Load Balancing: List Scheduling

List-scheduling algorithm.
• Consider 𝑛jobs in some fixed order.
• Assign job 𝑗to machine 𝑖whose load is smallest so far.

List-Scheduling (𝑚, 𝑛, 𝑡1, … , 𝑡𝑛)
------------------------------------------------------------
For 𝑖= 1 to 𝑚

𝐿𝑖= 0.
𝑆𝑖←∅.

For 𝑗= 1 to 𝑛

𝑖←𝑎𝑟𝑔𝑚𝑖𝑛𝑘𝐿[𝑘].
𝑆𝑖←𝑆𝑖∪{𝑗}.
𝐿𝑖←𝐿𝑖+ 𝑡𝑗.

Return 𝑆[1], 𝑆[2], … , 𝑆[𝑚].
5

<!-- page: 6 -->

Load Balancing: List Scheduling Analysis

Theorem. Greedy algorithm is a 2-approximation.
• First worst-case analysis of an approximation algorithm.
• Need to compare resulting solution with optimal makespan 𝐿∗.

Lemma 1. The optimal makespan 𝐿∗≥𝑚𝑎𝑥𝑗𝑡𝑗.
Pf.
Some machine must process the most time-consuming job.

1
𝑚σ𝑗𝑡𝑗.
Pf.
• The total processing time is σ𝑗𝑡𝑗.

Lemma 2. The optimal makespan 𝐿∗≥

• One of 𝑚machines must do at least a
1
𝑚fraction of total work.

6

<!-- page: 7 -->

Load Balancing: List Scheduling Analysis

Theorem. Greedy algorithm is a 2-approximation.
Pf. Consider load 𝐿[𝑖] of bottleneck machine 𝑖.
• Let 𝑗be last job scheduled on machine 𝑖.
• When job 𝑗assigned to machine 𝑖, 𝑖has smallest load.
Its load before assignment is 𝐿𝑖−𝑡𝑗⟹𝐿𝑖−𝑡𝑗≤𝐿[𝑘] for all
1 ≤𝑘≤𝑚.

7

<!-- page: 8 -->

Load Balancing: List Scheduling Analysis

Theorem. Greedy algorithm is a 2-approximation.
Pf. Consider load 𝐿[𝑖] of bottleneck machine 𝑖.
• Let 𝑗be last job scheduled on machine 𝑖.
• When job 𝑗assigned to machine 𝑖, 𝑖has smallest load.
Its load before assignment is 𝐿𝑖−𝑡𝑗⟹𝐿𝑖−𝑡𝑗≤𝐿[𝑘] for all
1 ≤𝑘≤𝑚.
• Sum inequalities over all 𝑘and divide by m:

𝐿𝑖−𝑡𝑗≤1

𝐿𝑘= 1

𝑡𝑗≤𝐿∗

𝑚෍

𝑚෍

𝑘

𝑗

• Now, 𝐿= 𝐿𝑖= 𝐿𝑖−𝑡𝑗+ 𝑡𝑗≤2𝐿∗.

8

<!-- page: 9 -->

Load Balancing: List Scheduling Analysis

Q. Is our analysis tight?
A. Essentially yes.

Ex: 𝑚machines, 𝑚(𝑚−1) jobs length 1, one job of length 𝑚.

9

![image](assets/assets/algorithm-design-and-analysis-006/image-001.png)

<!-- page: 10 -->

Load Balancing: List Scheduling Analysis

Q. Is our analysis tight?
A. Essentially yes.

Ex: 𝑚machines, 𝑚(𝑚−1) jobs length 1, one job of length 𝑚.

10

<!-- page: 11 -->

Load Balancing: LPT Rule

Longest Processing Time (LPT). Sort 𝑛jobs in decreasing order of
processing times; then run list scheduling algorithm.

LPT-List-Scheduling (𝑚, 𝑛, 𝑡1, … , 𝑡𝑛)
--------------------------------------------------------------------
Sort jobs and renumber so that 𝑡1 ≥𝑡2 ≥⋯≥𝑡𝑛.

For 𝑖= 1 to 𝑚

𝐿𝑖= 0.
𝑆𝑖←∅.

For 𝑗= 1 to 𝑛

𝑖←𝑎𝑟𝑔𝑚𝑖𝑛𝑘𝐿[𝑘].
𝑆𝑖←𝑆𝑖∪{𝑗}.
𝐿𝑖←𝐿𝑖+ 𝑡𝑗.

Return 𝑆[1], 𝑆[2], … , 𝑆[𝑚].
11

<!-- page: 12 -->

Load Balancing: LPT Rule

Ex.

LPT-List-Scheduling (𝑚, 𝑛, 𝑡1, … , 𝑡𝑛)
--------------------------------------------------------------------
Sort jobs and renumber so that 𝑡1 ≥𝑡2 ≥⋯≥𝑡𝑛.

For 𝑖= 1 to 𝑚

𝐿𝑖= 0.
𝑆𝑖←∅.

For 𝑗= 1 to 𝑛

𝑖←𝑎𝑟𝑔𝑚𝑖𝑛𝑘𝐿[𝑘].
𝑆𝑖←𝑆𝑖∪{𝑗}.
𝐿𝑖←𝐿𝑖+ 𝑡𝑗.

Return 𝑆[1], 𝑆[2], … , 𝑆[𝑚].
12

<!-- page: 13 -->

Load Balancing: LPT Rule

Ex.

13

<!-- page: 14 -->

Load Balancing: LPT Rule

Observation. If bottleneck machine 𝑖has only 1 job, then optimal.
Pf. Any solution must schedule that job.
Lemma 3. If there are more than 𝑚jobs, 𝐿∗≥2𝑡𝑚+1.
Pf.
• Consider processing times of first 𝑚+ 1 jobs 𝑡1 ≥𝑡2 ≥⋯≥𝑡𝑚+1.
• Each takes at least 𝑡𝑚+1 time.
• There are 𝑚+ 1 jobs and 𝑚machines, so at least one machine
gets two jobs.
Theorem. LPT rule is a 3/2-approximation algorithm.
Pf. [similar to proof for list scheduling]
• Consider load 𝐿[𝑖] of bottleneck machine 𝑖.
• Let 𝑗be the last job scheduled on machine 𝑖.

𝐿= 𝐿𝑖= 𝐿𝑖−𝑡𝑗+ 𝑡𝑗≤3

2 𝐿∗

14

<!-- page: 15 -->

Center Selection Problem

Input. Set of 𝑛sites 𝑠1, 𝑠2, … , 𝑠𝑛and an integer 𝑘> 0.

Center selection problem. Select set of 𝑘centers 𝐶so that
maximum distance 𝑟(𝐶) from a site to nearest center is
minimized.

15

![image](assets/assets/algorithm-design-and-analysis-006/image-002.png)

<!-- page: 16 -->

Center Selection Problem

Input. Set of 𝑛sites 𝑠1, 𝑠2, … , 𝑠𝑛and an integer 𝑘> 0.

Center selection problem. Select set of 𝑘centers 𝐶so that maximum
distance 𝑟(𝐶) from a site to nearest center is minimized.

Notation.
• 𝑑𝑖𝑠𝑡(𝑥, 𝑦) = distance between sites 𝑥and 𝑦.
• 𝑑𝑖𝑠𝑡𝑠𝑖, 𝐶= 𝑚𝑖𝑛𝑐𝑑𝑖𝑠𝑡𝑠𝑖, 𝑐= distance from 𝑠𝑖to closest center.
• 𝑟𝐶= 𝑚𝑎𝑥𝑖𝑑𝑖𝑠𝑡𝑠𝑖, 𝐶= smallest covering radius.

Goal. Find set of centers 𝐶that minimizes 𝑟𝐶, subject to 𝐶= 𝑘.

Distance function properties.
• 𝑑𝑖𝑠𝑡𝑥, 𝑦= 0
[identity]
• 𝑑𝑖𝑠𝑡𝑥, 𝑦= 𝑑𝑖𝑠𝑡(𝑦, 𝑥)
[symmetry]
• 𝑑𝑖𝑠𝑡𝑥, 𝑦≤𝑑𝑖𝑠𝑡𝑥, 𝑧+ 𝑑𝑖𝑠𝑡(𝑧, 𝑦)
[triangle inequality]

16

<!-- page: 17 -->

Center Selection Example

Ex: each site is a point in the plane, a center can be any point in
the plane, 𝑑𝑖𝑠𝑡(𝑥, 𝑦) = Euclidean distance.

Remark: search can be infinite!

17

![image](assets/assets/algorithm-design-and-analysis-006/image-003.png)

<!-- page: 18 -->

Greedy Algorithm: A False Start

Greedy algorithm. Put the first center at the best possible
location for a single center, and then keep adding centers so as to
reduce the covering radius each time by as much as possible.

Remark: arbitrarily bad!

18

<!-- page: 19 -->

Center Selection: Greedy Algorithm

Repeatedly choose next center to be site farthest from any
existing center.

Greedy-Center-Selection (𝑘, 𝑛, 𝑠1, … , 𝑠𝑛)
-------------------------------------------------------------------------
𝐶←∅.
Repeat 𝑘times

Select a site 𝑠𝑖with maximum distance 𝑑𝑖𝑠𝑡(𝑠𝑖, 𝐶).
𝐶←𝐶∪𝑠𝑖.
Return 𝐶.

19

<!-- page: 20 -->

Center Selection: Analysis of Greedy
Algorithm

Lemma. Let 𝐶∗be an optimal set of centers. Then 𝑟(𝐶) ≤2𝑟(𝐶∗).
Pf. [by contradiction] Assume 𝑟(𝐶∗) ≤

1
2 𝑟(𝐶).

• For each site 𝑐𝑖∈𝐶, consider ball of radius
1
2 𝑟(𝐶) around it.
• Exactly one 𝑐𝑖
∗in each ball; let 𝑐𝑖be the site paired with 𝑐𝑖

∗.
• Consider any site 𝑠and its closest center 𝑐𝑖
∗∈𝐶∗.
• 𝑑𝑖𝑠𝑡𝑠, 𝐶≤𝑑𝑖𝑠𝑡𝑠, 𝑐𝑖≤𝑑𝑖𝑠𝑡𝑠, 𝑐𝑖
∗+ 𝑑𝑖𝑠𝑡(𝑐𝑖

∗, 𝑐𝑖) ≤2𝑟(𝐶∗).
• Thus, 𝑟(𝐶) ≤2𝑟(𝐶∗).

20

![image](assets/assets/algorithm-design-and-analysis-006/image-004.png)

<!-- page: 21 -->

Center Selection

Lemma. Let 𝐶∗be an optimal set of centers. Then 𝑟(𝐶) ≤2𝑟(𝐶∗).

Theorem. Greedy algorithm is a 2-approximation for center
selection problem.

Remark. Greedy algorithm always places centers at sites, but is
still within a factor of 2 of best solution that is allowed to place
centers anywhere.

21

<!-- page: 22 -->

Weighted Vertex Cover

Definition. Given a graph 𝐺= (𝑉, 𝐸), a vertex cover is a set of
𝑆⊆𝑉such that each edge in 𝐸has at least one end in 𝑆.

Weighted Vertex cover. Given a graph 𝐺with vertex weights, find
a vertex cover of minimum weight.

22

![image](assets/assets/algorithm-design-and-analysis-006/image-005.png)

<!-- page: 23 -->

Pricing Method

Pricing method. Each edge must be covered by some vertex.
Edge 𝑒= (𝑖, 𝑗) pays price 𝑝𝑒≥0 to use both vertex 𝑖and 𝑗.

Fairness. Edges incident to vertex 𝑖should pay ≤𝑤𝑖in total.

Fairness lemma. For any vertex cover S and any fair prices
𝑝𝑒: σ𝑒∈𝐸𝑝𝑒≤𝑤(𝑆).
Pf. σ𝑒∈𝐸𝑝𝑒≤σ𝑖∈𝑆σ𝑒= 𝑖,𝑗𝑝𝑒≤σ𝑖∈𝑆𝑤𝑖= 𝑤(𝑆).

23

<!-- page: 24 -->

Pricing Method

Set prices and find vertex cover simultaneously.

Weighted-Vertex-Cover (𝐺, 𝑤)
---------------------------------------------------------------------------------------
𝑆←∅.
For each 𝑒∈𝐸

෍

𝑝𝑒= 𝑤𝑖

𝑝𝑒←0.

𝑒= 𝑖,𝑗

While (there exists an edge (𝑖, 𝑗) such that neither 𝑖nor 𝑗is tight)

Select such an edge 𝑒= (𝑖, 𝑗).
Increase 𝑝𝑒as much as possible until 𝑖or 𝑗tight.

𝑆←set of all tight nodes.
Return 𝑆.

24

<!-- page: 25 -->

Pricing Method Example

Ex.

Weighted-Vertex-Cover (𝐺, 𝑤)
---------------------------------------------------------------------------------------
𝑆←∅.
For each 𝑒∈𝐸

𝑝𝑒←0.

While (there exists an edge (𝑖, 𝑗) such that neither 𝑖nor 𝑗is tight)

Select such an edge 𝑒= (𝑖, 𝑗).
Increase 𝑝𝑒as much as possible until 𝑖or 𝑗tight.

𝑆←set of all tight nodes.
Return 𝑆.
25

![image](assets/assets/algorithm-design-and-analysis-006/image-006.png)

<!-- page: 26 -->

Pricing Method Example

Ex.

26

![image](assets/assets/algorithm-design-and-analysis-006/image-007.png)

<!-- page: 27 -->

Pricing Method: Analysis

Theorem. Pricing method is a 2-approximation for Weighted-
Vertex-Cover.
Pf.
• Algorithm terminates since at least one new node becomes
tight after each iteration of “while” loop.

• Let 𝑆= set of all tight nodes upon termination of algorithm.
𝑆is a vertex cover: if some edge (𝑖, 𝑗) is uncovered, then neither 𝑖
or 𝑗is tight. But then “while” loop would not terminate.

• Let 𝑆∗be optimal vertex cover. We show 𝑤(𝑆) ≤2𝑤(𝑆∗).

𝑤𝑆= ෍

𝑤𝑖= ෍

෍

𝑝𝑒≤෍

෍

𝑝𝑒= 2 ෍

𝑝𝑒

𝑖∈𝑆

𝑖∈𝑆

𝑒=(𝑖,𝑗)

𝑖∈𝑉

𝑒∈𝐸

𝑒= 𝑖,𝑗

≤2𝑤(𝑆∗)

27

<!-- page: 28 -->

Weighted Vertex Cover: ILP Formulation

Given a graph 𝐺= (𝑉, 𝐸) with vertex weights 𝑤𝑖≥0, find a min-
weight subset of vertices 𝑆⊆𝑉such that every edge is incident
to at least one vertex in 𝑆.

Integer Linear Programming (ILP) formulation.
• Model inclusion of each vertex 𝑖using a 0/1 variable 𝑥𝑖.

𝑥𝑖= ቊ0, 𝑖𝑓𝑣𝑒𝑟𝑡𝑒𝑥𝑖𝑖𝑠𝑛𝑜𝑡𝑖𝑛𝑣𝑒𝑟𝑡𝑒𝑥𝑐𝑜𝑣𝑒𝑟

1, 𝑖𝑓𝑣𝑒𝑟𝑡𝑒𝑥𝑖𝑖𝑠𝑖𝑛𝑣𝑒𝑟𝑡𝑒𝑥𝑐𝑜𝑣𝑒𝑟
Vertex covers in 1-1 correspondence with 0/1 assignments: 𝑆=
{𝑖∈𝑉: 𝑥𝑖= 1}.
• Objective function: minimize σ𝑖𝑤𝑖𝑥𝑖.
• For every edge (𝑖, 𝑗), take either vertex 𝑖or 𝑗(or both): 𝑥𝑖+
𝑥𝑗≥1.

28

<!-- page: 29 -->

Weighted Vertex Cover: ILP Formulation

Weighted vertex cover. Integer linear programming formulation.

𝐼𝐿𝑃
min σ𝑖∈𝑉𝑤𝑖𝑥𝑖
𝑠. 𝑡. 𝑥𝑖+ 𝑥𝑗≥1
(𝑖, 𝑗) ∈𝐸
𝑥𝑖∈0,1
𝑖∈𝑉

Observation. If 𝑥∗is optimal solution on ILP, then 𝑆= {𝑖∈
𝑉: 𝑥𝑖

∗= 1} is a min-weight vertex cover.

29

<!-- page: 30 -->

Integer Linear Programming

Given integers 𝑎𝑖𝑗, 𝑏𝑖, and 𝑐𝑗, find integers 𝑥𝑗that satisfy:

𝑛
𝑐𝑗𝑥𝑗
𝑠. 𝑡. σ𝑗=1

min 𝑐𝑇𝑥
𝑠. 𝑡. 𝐴𝑥≥𝑏
𝑥≥0
𝑥𝑖𝑛𝑡𝑒𝑔𝑟𝑎𝑙

min σ𝑗=1

𝑛
𝑎𝑖𝑗𝑥𝑗≥𝑏𝑖
1 ≤𝑖≤𝑚
𝑥𝑗≥0
1 ≤𝑗≤𝑛
𝑥𝑗𝑖𝑛𝑡𝑒𝑔𝑟𝑎𝑙
1 ≤𝑗≤𝑛

30

<!-- page: 31 -->

Linear Programming

Given integers 𝑎𝑖𝑗, 𝑏𝑖, and 𝑐𝑗, find real numbers 𝑥𝑗that satisfy:

𝑛
𝑐𝑗𝑥𝑗
𝑠. 𝑡. σ𝑗=1

min 𝑐𝑇𝑥
𝑠. 𝑡. 𝐴𝑥≥𝑏
𝑥≥0

min σ𝑗=1

𝑛
𝑎𝑖𝑗𝑥𝑗≥𝑏𝑖
1 ≤𝑖≤𝑚
𝑥𝑗≥0
1 ≤𝑗≤𝑛

Linear. No 𝑥2, 𝑥𝑦, arccos 𝑥, 𝑥1 −𝑥, etc.

Simplex algorithm. Can solve LP in practice.

31

<!-- page: 32 -->

Weighted Vertex Cover: LP Relaxation

Linear programming relaxation.

𝐿𝑃
min σ𝑖∈𝑉𝑤𝑖𝑥𝑖
𝑠. 𝑡. 𝑥𝑖+ 𝑥𝑗≥1
(𝑖, 𝑗) ∈𝐸
𝑥𝑖≥0
𝑖∈𝑉

Note. LP is not equivalent to weighted vertex cover.

Q. How can solving LP help us find a low-weight vertex cover?
A. Solve LP and round fractional values.

32

<!-- page: 33 -->

Weighted Vertex Cover: LP Rounding
Algorithm

∗≥1/2} is
a vertex cover whose weight is at most twice the min possible weight.

Lemma. If 𝑥∗is optimal solution to LP, then 𝑆= {𝑖∈𝑉: 𝑥𝑖

Pf. [𝑆is a vertex cover]
• Consider an edge (𝑖, 𝑗) ∈𝐸.
• Since 𝑥𝑖
∗+ 𝑥𝑗

∗≥1/2 (or both)  ⟹
(𝑖, 𝑗) covered.

∗≥1, either 𝑥𝑖

∗≥1/2 or 𝑥𝑗

Pf. [𝑆has desired cost]
• Let 𝑆# be optimal vertex cover. Then

∗≥1

෍

𝑤𝑖≥෍

𝑤𝑖𝑥𝑖

2 ෍

𝑤𝑖

𝑖∈𝑆#

𝑖∈𝑆

𝑖∈𝑆

Theorem. The rounding algorithm is a 2-apprimation algorithm.

33
