---
source_id: algorithm-design-and-analysis-025
course_id: algorithm_design_and_analysis
title: 9-networkFlow
original_file: "学科资料/算法设计与分析/PPT-英文版/9-networkFlow-1.pdf"
document_role: note
year: 
locator_type: page
---

# 9-networkFlow

<!-- page: 1 -->

Design and Analysis of Algorithms

Network Flow

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

1

<!-- page: 2 -->

Topics

• Max-Flow and Min-Cut Problems
• Ford-Fulkerson Algorithm
• Max-Flow Min-Cut Theorem
• Capacity-Scaling Algorithm
• Shortest Augmenting Paths
• Blocking-Flow Algorithm

2

<!-- page: 3 -->

Flow Network

A flow network is a tuple 𝐺= (𝑉, 𝐸, 𝑠, 𝑡, 𝑐).
• Digraph (𝑉, 𝐸) with source 𝑠∈𝑉and sink 𝑡∈𝑉.
• Non-negative capacity 𝑐(𝑒) for each 𝑒∈𝐸.

Intuition. Material flowing through a transportation network;
material originates at source and is sent to sink.

3

![image](assets/assets/algorithm-design-and-analysis-025/image-001.png)

<!-- page: 4 -->

Minimum-Cut Problem

Def. An 𝑠𝑡-cut (cut) is a partition (𝐴, 𝐵) of the vertices with 𝑠∈𝐴
and 𝑡∈𝐵.
Def. Its capacity is the sum of the capacities of the edges from A
to B.

𝑐𝑎𝑝𝐴, 𝐵=
෍

𝑐(𝑒)

𝑒𝑜𝑢𝑡𝑜𝑓𝐴

4

![image](assets/assets/algorithm-design-and-analysis-025/image-002.png)

<!-- page: 5 -->

Minimum-Cut Problem

Def. An 𝑠𝑡-cut (cut) is a partition (𝐴, 𝐵) of the vertices with 𝑠∈𝐴
and 𝑡∈𝐵.
Def. Its capacity is the sum of the capacities of the edges from A
to B.

𝑐𝑎𝑝𝐴, 𝐵=
෍

𝑐(𝑒)

𝑒𝑜𝑢𝑡𝑜𝑓𝐴

5

![image](assets/assets/algorithm-design-and-analysis-025/image-003.png)

<!-- page: 6 -->

Minimum-Cut Problem

Def. An 𝑠𝑡-cut (cut) is a partition (𝐴, 𝐵) of the vertices with 𝑠∈𝐴
and 𝑡∈𝐵.
Def. Its capacity is the sum of the capacities of the edges from A
to B.

𝑐𝑎𝑝𝐴, 𝐵=
෍

𝑐(𝑒)

𝑒𝑜𝑢𝑡𝑜𝑓𝐴

Min-cut problem.
Find a cut of
minimum capacity.

6

![image](assets/assets/algorithm-design-and-analysis-025/image-004.png)

<!-- page: 7 -->

Minimum-Cut Problem

What is the capacity of the given st-cut?

𝑐𝑎𝑝𝐴, 𝐵= 45 (20 + 25)

7

![image](assets/assets/algorithm-design-and-analysis-025/image-005.png)

<!-- page: 8 -->

Maximum-Flow Problem

Def. An 𝑠𝑡-flow (flow) 𝑓is a function that satisfies:
• For each 𝑒∈𝐸: 0 ≤𝑓(𝑒) ≤𝑐(𝑒) [capacity]
• For each 𝑣∈𝑉−𝑠, 𝑡: σ𝑒𝑖𝑛𝑡𝑜𝑣𝑓𝑒= σ𝑒𝑜𝑢𝑡𝑜𝑓𝑣𝑓(𝑒) [flow
conservation]

8

![image](assets/assets/algorithm-design-and-analysis-025/image-006.png)

<!-- page: 9 -->

Maximum-Flow Problem

Def. An 𝑠𝑡-flow (flow) 𝑓is a function that satisfies:
• For each 𝑒∈𝐸: 0 ≤𝑓(𝑒) ≤𝑐(𝑒) [capacity]
• For each 𝑣∈𝑉−𝑠, 𝑡: σ𝑒𝑖𝑛𝑡𝑜𝑣𝑓𝑒= σ𝑒𝑜𝑢𝑡𝑜𝑓𝑣𝑓(𝑒) [flow
conservation]
Def. The value of a flow 𝑓is: 𝑣𝑎𝑙𝑓= σ𝑒𝑜𝑢𝑡𝑜𝑓𝑠𝑓𝑒−σ𝑒𝑖𝑛𝑡𝑜𝑠𝑓(𝑒)

9

![image](assets/assets/algorithm-design-and-analysis-025/image-007.png)

<!-- page: 10 -->

Maximum-Flow Problem

Def. An 𝑠𝑡-flow (flow) 𝑓is a function that satisfies:
• For each 𝑒∈𝐸: 0 ≤𝑓(𝑒) ≤𝑐(𝑒) [capacity]
• For each 𝑣∈𝑉−𝑠, 𝑡: σ𝑒𝑖𝑛𝑡𝑜𝑣𝑓𝑒= σ𝑒𝑜𝑢𝑡𝑜𝑓𝑣𝑓(𝑒) [flow
conservation]
Def. The value of a flow 𝑓is: 𝑣𝑎𝑙𝑓= σ𝑒𝑜𝑢𝑡𝑜𝑓𝑠𝑓𝑒−σ𝑒𝑖𝑛𝑡𝑜𝑠𝑓(𝑒)
Max-flow problem. Find a flow of maximum value？

10

![image](assets/assets/algorithm-design-and-analysis-025/image-008.png)

<!-- page: 11 -->

Towards a Max-Flow Algorithm

Greedy algorithm.
• Start with 𝑓𝑒= 0 for each edge 𝑒∈𝐸.
• Find an 𝑠→𝑡path P where each edge has 𝑓𝑒≤𝑐(𝑒).
• Augment flow along path P.
• Repeat until get stuck.

11

![image](assets/assets/algorithm-design-and-analysis-025/image-009.png)

<!-- page: 12 -->

Towards a Max-Flow Algorithm

Greedy algorithm.
• Start with 𝑓𝑒= 0 for each edge 𝑒∈𝐸.
• Find an 𝑠→𝑡path P where each edge has 𝑓𝑒≤𝑐(𝑒).
• Augment flow along path P.
• Repeat until get stuck.

12

![image](assets/assets/algorithm-design-and-analysis-025/image-010.png)

<!-- page: 13 -->

Towards a Max-Flow Algorithm

Greedy algorithm.
• Start with 𝑓𝑒= 0 for each edge 𝑒∈𝐸.
• Find an 𝑠→𝑡path P where each edge has 𝑓𝑒≤𝑐(𝑒).
• Augment flow along path P.
• Repeat until get stuck.

13

![image](assets/assets/algorithm-design-and-analysis-025/image-011.png)

<!-- page: 14 -->

Towards a Max-Flow Algorithm

Greedy algorithm.
• Start with 𝑓𝑒= 0 for each edge 𝑒∈𝐸.
• Find an 𝑠→𝑡path P where each edge has 𝑓𝑒≤𝑐(𝑒).
• Augment flow along path P.
• Repeat until get stuck.

14

![image](assets/assets/algorithm-design-and-analysis-025/image-012.png)

<!-- page: 15 -->

Towards a Max-Flow Algorithm

Greedy algorithm.
• Start with 𝑓𝑒= 0 for each edge 𝑒∈𝐸.
• Find an 𝑠→𝑡path P where each edge has 𝑓𝑒≤𝑐(𝑒).
• Augment flow along path P.
• Repeat until get stuck.

15

![image](assets/assets/algorithm-design-and-analysis-025/image-013.png)

<!-- page: 16 -->

Towards a Max-Flow Algorithm

Greedy algorithm.
• Start with 𝑓𝑒= 0 for each edge 𝑒∈𝐸.
• Find an 𝑠→𝑡path P where each edge has 𝑓𝑒≤𝑐(𝑒).
• Augment flow along path P.
• Repeat until get stuck.

Why does the
greedy algorithm fail?

16

![image](assets/assets/algorithm-design-and-analysis-025/image-014.png)

<!-- page: 17 -->

Why the Greedy Algorithm Fails

Q. Why does the greedy algorithm fail?
A. Once greedy algorithm increases flow on an edge, it never
decrease it.

Ex.
• The max flow is unique; flow on edge (𝑣, 𝑤) is zero.
• Greedy algorithm could choose 𝑠→𝑣→𝑤→𝑡for first
augmenting path.

Need some mechanism to “undo” bad decision.
17

<!-- page: 18 -->

Residual Network

Original edge. 𝑒= (𝑢, 𝑣) ∈𝐸.
• Flow 𝑓(𝑒).
• Capacity 𝑐(𝑒).

Reverse edge. 𝑒𝑟𝑒𝑣𝑒𝑟𝑠𝑒= (𝑣, 𝑢).
• “Undo” flow sent.

Residual capacity.

𝑐𝑓𝑒= ቊ𝑐𝑒−𝑓𝑒
𝑖𝑓𝑒∈𝐸
𝑓𝑒
𝑖𝑓𝑒𝑟𝑒𝑣𝑒𝑟𝑠𝑒∈𝐸

Edges with positive
residual capacity

Residual network. 𝐺𝑓= (𝑉, 𝐸𝑓, 𝑠, 𝑡, 𝑐𝑓).
• 𝐸𝑓= 𝑒: 𝑓𝑒< 𝑐𝑒
∪{𝑒𝑟𝑒𝑣𝑒𝑟𝑠𝑒: 𝑓𝑒> 0}.

18

![image](assets/assets/algorithm-design-and-analysis-025/image-015.png)

<!-- page: 19 -->

Flow and Residual Network

Let 𝑓be a flow on 𝐺= (𝑉, 𝐸):

The residual network 𝐺𝑓(𝑉, 𝐸𝑓):

19

![image](assets/assets/algorithm-design-and-analysis-025/image-016.jpeg)

<!-- page: 20 -->

Flow and Residual Network

Let 𝑓be a flow on 𝐺= (𝑉, 𝐸):

The residual network 𝐺𝑓(𝑉, 𝐸𝑓):

20

![image](assets/assets/algorithm-design-and-analysis-025/image-017.jpeg)

![image](assets/assets/algorithm-design-and-analysis-025/image-018.png)

<!-- page: 21 -->

Augmenting Path

Def. An augmenting path is a simple 𝑠→𝑡path in the residual
network 𝐺𝑓.

Def. The bottleneck capacity of an augmenting path 𝑃is the
minimum residual capacity of any edge in 𝑃.

Key property. Let 𝑓be a flow and let 𝑃be an augmenting path
in 𝐺𝑓. Then, after call Augment, the resulting 𝑓′ is a flow and
𝑣𝑎𝑙𝑓′ = 𝑣𝑎𝑙𝑓+ 𝑏𝑜𝑡𝑡𝑙𝑒𝑛𝑒𝑐𝑘(𝐺𝑓, 𝑃).

21

<!-- page: 22 -->

Augmenting Path

Key property. Let 𝑓be a flow and let 𝑃be an augmenting path
in 𝐺𝑓. Then, after call Augment, the resulting 𝑓′ is a flow and
𝑣𝑎𝑙𝑓′ = 𝑣𝑎𝑙𝑓+ 𝑏𝑜𝑡𝑡𝑙𝑒𝑛𝑒𝑐𝑘(𝐺𝑓, 𝑃).

Augment (𝑓, 𝑐, 𝑃)
--------------------------------------------------------
𝑏←bottleneck capacity of path 𝑃.
For each edge 𝑒∈𝑃

If (𝑒∈𝐸)

𝑓𝑒←𝑓𝑒+ 𝑏.
Else

𝑓𝑒𝑟𝑒𝑣𝑒𝑟𝑠𝑒←𝑓𝑒𝑟𝑒𝑣𝑒𝑟𝑠𝑒−𝑏.
Return 𝑓.

22

<!-- page: 23 -->

Augmenting Path

Which is the augmenting path of highest bottleneck capacity?
A. A →F →G →H
B. A →F →B →G →H
C. A →F →B →G →C →D →H

23

![image](assets/assets/algorithm-design-and-analysis-025/image-019.png)

<!-- page: 24 -->

Augmenting Path

Which is the augmenting path of highest bottleneck capacity?
A. A →F →G →H (2)
B. A →F →B →G →H (3)
C. A →F →B →G →C →D →H (4)

24

![image](assets/assets/algorithm-design-and-analysis-025/image-020.png)

<!-- page: 25 -->

Ford-Fulkerson Algorithm

Ford-Fulkerson augmenting path algorithm.
• Start with 𝑓𝑒= 0 for each edge 𝑒∈𝐸.
• Find an 𝑠→𝑡path 𝑃in the residual network 𝐺𝑓.
• Augment flow along path 𝑃.
• Repeat until you get stuck.

Ford-Fulkerson (𝐺)
--------------------------------------------------------------
For each edge 𝑒∈𝐸: 𝑓[𝑒] ←0.
𝐺𝑓←residual network of 𝐺with respect to 𝑓.
While (there exists an 𝑠→𝑡augmenting path 𝑃in 𝐺𝑓

𝑓←Augment(𝑓, 𝑐, 𝑃).

Update 𝐺𝑓.
Return 𝑓.

25

<!-- page: 26 -->

Relationship Between Flows and Cuts

Flow value lemma. Let 𝑓be any flow and let (𝐴, 𝐵) be
any cut. Then, the value of the flow 𝑓equals the net
flow across the cut (𝐴, 𝐵).

𝑣𝑎𝑙𝑓=
෍

𝑓(𝑒) −
෍

𝑓(𝑒)

𝑒𝑜𝑢𝑡𝑜𝑓𝐴

𝑒𝑖𝑛𝑡𝑜𝐴

26

![image](assets/assets/algorithm-design-and-analysis-025/image-021.png)

<!-- page: 27 -->

Relationship Between Flows and Cuts

Flow value lemma. Let 𝑓be any flow and let (𝐴, 𝐵) be
any cut. Then, the value of the flow 𝑓equals the net
flow across the cut (𝐴, 𝐵).

𝑣𝑎𝑙𝑓=
෍

𝑓(𝑒) −
෍

𝑓(𝑒)

𝑒𝑜𝑢𝑡𝑜𝑓𝐴

𝑒𝑖𝑛𝑡𝑜𝐴

27

![image](assets/assets/algorithm-design-and-analysis-025/image-022.png)

<!-- page: 28 -->

Relationship Between Flows and Cuts

Flow value lemma. Let 𝑓be any flow and let (𝐴, 𝐵) be
any cut. Then, the value of the flow 𝑓equals the net
flow across the cut (𝐴, 𝐵).

𝑣𝑎𝑙𝑓=
෍

𝑓(𝑒) −
෍

𝑓(𝑒)

𝑒𝑜𝑢𝑡𝑜𝑓𝐴

𝑒𝑖𝑛𝑡𝑜𝐴

28

![image](assets/assets/algorithm-design-and-analysis-025/image-023.png)

<!-- page: 29 -->

Relationship Between Flows and Cuts

What is the net flow across the given st-cut?

𝑣𝑎𝑙𝑓= 26 (20 + 22 −8 −4 −4)

29

![image](assets/assets/algorithm-design-and-analysis-025/image-024.png)

<!-- page: 30 -->

Relationship Between Flows and Cuts

Flow value lemma. Let 𝑓be any flow and let (𝐴, 𝐵) be
any cut. Then, the value of the flow 𝑓equals the net
flow across the cut (𝐴, 𝐵).

𝑣𝑎𝑙𝑓=
෍

𝑓(𝑒) −
෍

𝑓(𝑒)

𝑒𝑜𝑢𝑡𝑜𝑓𝐴

𝑒𝑖𝑛𝑡𝑜𝐴

Pf.      𝑣𝑎𝑙𝑓= σ𝑒𝑜𝑢𝑡𝑜𝑓𝑠𝑓(𝑒) −σ𝑒𝑖𝑛𝑡𝑜𝑠𝑓(𝑒)

= σ𝑣∈𝐴(σ𝑒𝑜𝑢𝑡𝑜𝑓𝑣𝑓(𝑒) −σ𝑒𝑖𝑛𝑡𝑜𝑣𝑓(𝑒))

= σ𝑒𝑜𝑢𝑡𝑜𝑓𝐴𝑓(𝑒) −σ𝑒𝑖𝑛𝑡𝑜𝐴𝑓(𝑒)
By flow conservation, all
terms except for s are 0

30

<!-- page: 31 -->

Relationship Between Flows and Cuts

Weak duality. Let 𝑓be any flow and (𝐴, 𝐵) be any cut.
Then, 𝑣𝑎𝑙(𝑓) ≤𝑐𝑎𝑝(𝐴, 𝐵).
Pf.        𝑣𝑎𝑙𝑓= σ𝑒𝑜𝑢𝑡𝑜𝑓𝐴𝑓(𝑒) −σ𝑒𝑖𝑛𝑡𝑜𝐴𝑓(𝑒)

≤σ𝑒𝑜𝑢𝑡𝑜𝑓𝐴𝑓(𝑒)
≤σ𝑒𝑜𝑢𝑡𝑜𝑓𝐴𝑐(𝑒)
= 𝑐𝑎𝑝(𝐴, 𝐵)

31

![image](assets/assets/algorithm-design-and-analysis-025/image-025.png)

<!-- page: 32 -->

Certificate of Optimality

Corollary. Let 𝑓be a flow and let (𝐴, 𝐵) be any cut. If 𝑣𝑎𝑙𝑓=
𝑐𝑎𝑝(𝐴, 𝐵), then 𝑓is a max flow and (𝐴, 𝐵) is a min cut.

Pf.
• For any flow 𝑓′: 𝑣𝑎𝑙𝑓′ ≤𝑐𝑎𝑝𝐴, 𝐵= 𝑣𝑎𝑙(𝑓).
• For any cut 𝐴′, 𝐵′ : 𝑐𝑎𝑝𝐴′, 𝐵′ ≥𝑣𝑎𝑙𝑓= 𝑐𝑎𝑝𝐴, 𝐵.

32

![image](assets/assets/algorithm-design-and-analysis-025/image-026.png)

<!-- page: 33 -->

Computing a Minimum Cut from a
Maximum Flow

Theorem. Given any max flow 𝑓, can compute a min cut (𝐴, 𝐵) in
𝑂(𝑚) time.

33

<!-- page: 34 -->

Computing a Minimum Cut from a
Maximum Flow

Theorem. Given any max flow 𝑓, can compute a min cut (𝐴, 𝐵).
Pf. Let 𝐴= set of nodes reachable from 𝑠in residual network 𝐺𝑓.

Capacity of 𝑨, 𝑩= value of flow 𝒇

34

![image](assets/assets/algorithm-design-and-analysis-025/image-027.png)

<!-- page: 35 -->

Max-Flow Min-Cut Theorem

Augmenting path theorem. A flow 𝑓is a max flow iff no
augmenting paths.
Max-flow min-cut theorem. Value of a max flow = capacity of a
min cut.

Pf. The following three conditions are equivalent for any flow 𝑓:
I.
There exists a cut 𝐴, 𝐵such that 𝑐𝑎𝑝𝐴, 𝐵= 𝑣𝑎𝑙(𝑓).
II.
𝑓is a max flow.
III. There is no augmenting path with respect to 𝑓.

[I ⟹II]
• Suppose that 𝐴, 𝐵is a cut such that 𝑐𝑎𝑝𝐴, 𝐵= 𝑣𝑎𝑙(𝑓).
• Then, for any flow𝑓′: 𝑣𝑎𝑙𝑓′ ≤𝑐𝑎𝑝𝐴, 𝐵= 𝑣𝑎𝑙(𝑓).
• Thus, 𝑓is a max flow.

35

<!-- page: 36 -->

Max-Flow Min-Cut Theorem

Augmenting path theorem. A flow 𝑓is a max flow iff no
augmenting paths.
Max-flow min-cut theorem. Value of a max flow = capacity of a
min cut.

Pf. The following three conditions are equivalent for any flow 𝑓:
I.
There exists a cut 𝐴, 𝐵such that 𝑐𝑎𝑝𝐴, 𝐵= 𝑣𝑎𝑙(𝑓).
II.
𝑓is a max flow.
III. There is no augmenting path with respect to 𝑓.

[II ⟹III]   We prove contrapositive: ~III ⟹~II.
• Suppose that there is an augmenting path with respect to 𝑓.
• Can improve flow 𝑓by sending flow along this path.
• Thus, 𝑓is not a max flow.

36

<!-- page: 37 -->

Max-Flow Min-Cut Theorem

[III ⟹I]
• Let 𝑓be a flow with no augmenting paths.
• Let 𝐴be set of nodes reachable from 𝑠in residual network 𝐺𝑓.
• By definition of cut 𝐴: 𝑠∈𝐴.
• By definition of flow 𝑓: 𝑡∉𝐴.

𝑣𝑎𝑙𝑓=
෍

𝑓(𝑒) −
෍

𝑓(𝑒)

𝑒𝑜𝑢𝑡𝑜𝑓𝐴

𝑒𝑖𝑛𝑡𝑜𝐴

= σ𝑒𝑜𝑢𝑡𝑜𝑓𝐴𝑐(𝑒)

= 𝑐𝑎𝑝(𝐴, 𝐵)

37

![image](assets/assets/algorithm-design-and-analysis-025/image-028.png)

<!-- page: 38 -->

Bad Case for Ford-Fulkerson

If max capacity is 𝐶, then algorithm can take ≥𝐶iterations.

38

![image](assets/assets/algorithm-design-and-analysis-025/image-029.png)

<!-- page: 39 -->

Choosing Good Augmenting Paths

Use care when selecting augmenting paths.
•
Some choices lead to exponential algorithms.
•
Clever choices lead to polynomial algorithms.

Pathology. If capacities are irrational, algorithm does not
guarantee to terminate (or converge to correct answer)!

Goal. Choose augmenting paths so that:
•
Can find augmenting paths efficiently.
•
Few iterations.

Choose augmenting paths with:
• Max bottleneck capacity (“fattest”).
• Sufficiency large bottleneck capacity.
• Fewest edges.

39

<!-- page: 40 -->

Capacity-Scaling Algorithm

Intuition. Choose augmenting path with highest bottleneck capacity:
it increases flow by max possible amount in given iteration.
•
Don’t worry about finding exact highest bottleneck path.
•
Maintain scaling parameter Δ.
•
Let 𝐺𝑓(Δ) be the part of the residual network consisting of only
those arcs with capacity ≥Δ.

40

![image](assets/assets/algorithm-design-and-analysis-025/image-030.png)

<!-- page: 41 -->

Capacity-Scaling Algorithm

Capacity-Scaling (𝐺)
---------------------------------------------------------------------------
For each edge 𝑒∈𝐸: 𝑓[𝑒] ←0.
Δ ←largest power of 2 ≤𝐶.

While (Δ ≥1)

𝐺𝑓(Δ) ←Δ -residual network of G with respect to flow 𝑓.

While (there exists an 𝑠→𝑡path P in 𝐺𝑓(Δ)

𝑓←Augment(𝑓, 𝑐, 𝑃).
Update 𝐺𝑓(Δ).
Δ ←Δ/2.

Return 𝑓.

41

<!-- page: 42 -->

Capacity-Scaling Algorithm: Proof of
Correctness
Assumption: All edge capacities are integers between 1
and 𝐶.

Integrality invariant. All flows and residual capacities are
integral.

Theorem. If capacity-scaling algorithm terminates, then f
is a max flow.
Pf.
•
By integrality invariant, when Δ = 1 ⟹𝐺𝑓Δ = 𝐺𝑓.
•
Upon termination of Δ = 1 phase, there are no
augmenting paths.

42

<!-- page: 43 -->

Shortest Augmenting Path

Q. Which augmenting path?
A. The one with the fewest edges (can find via Breadth-First-
Search).

Shortest-Augmenting-Path (𝐺)
---------------------------------------------------------------------------
For each edge 𝑒∈𝐸: 𝑓[𝑒] ←0.

𝐺𝑓←residual network of G with respect to flow 𝑓.

While (there exists an 𝑠→𝑡path in 𝐺𝑓)

𝑃←Breadth-First-Search (𝐺𝑓).
𝑓←Augment (𝑓, 𝑐, 𝑃)
Update 𝐺𝑓.
Return 𝑓.

43

<!-- page: 44 -->

Shortest Augmenting Path: Analysis

Def. Given a digraph 𝐺= (𝑉, 𝐸) with source 𝑠, its level graph is
defined by:
• 𝑙𝑣= number of edges in shortest path from 𝑠to 𝑣.
• 𝐿𝐺= (𝑉, 𝐸𝐺) is the subgraph of 𝐺that contains only those
edge (𝑣, 𝑤) ∈𝐸with 𝑙𝑤= 𝑙𝑣+ 1.

44

![image](assets/assets/algorithm-design-and-analysis-025/image-031.png)

<!-- page: 45 -->

Shortest Augmenting Path: Analysis

Def. Given a digraph 𝐺= (𝑉, 𝐸) with source 𝑠, its level graph is
defined by:
• 𝑙𝑣= number of edges in shortest path from 𝑠to 𝑣.
• 𝐿𝐺= (𝑉, 𝐸𝐺) is the subgraph of 𝐺that contains only those
edge (𝑣, 𝑤) ∈𝐸with 𝑙𝑤= 𝑙𝑣+ 1.

Key property. 𝑃is a shortest path 𝑠→𝑣path in 𝐺iff 𝑃is an 𝑠→𝑣
path in 𝐿𝐺.

45

![image](assets/assets/algorithm-design-and-analysis-025/image-032.png)

<!-- page: 46 -->

Shortest Augmenting Path: Analysis

Lemma 1. The length of a shortest augmenting path never decreases.
•
Let 𝑓and 𝑓′ be flow before and after a shortest-path augmentation.
•
Let 𝐿and 𝐿′ be level graphs of 𝑮𝒇and 𝑮𝒇′.
•
Only back edges added to 𝐺𝑓′.
(any path with a back edge is longer than previous length)

46

![image](assets/assets/algorithm-design-and-analysis-025/image-033.png)

<!-- page: 47 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

47

<!-- page: 48 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

48

![image](assets/assets/algorithm-design-and-analysis-025/image-034.png)

<!-- page: 49 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

49

![image](assets/assets/algorithm-design-and-analysis-025/image-035.png)

<!-- page: 50 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

50

![image](assets/assets/algorithm-design-and-analysis-025/image-036.png)

<!-- page: 51 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

51

![image](assets/assets/algorithm-design-and-analysis-025/image-037.png)

<!-- page: 52 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

52

![image](assets/assets/algorithm-design-and-analysis-025/image-038.png)

<!-- page: 53 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

53

<!-- page: 54 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

54

<!-- page: 55 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

55

<!-- page: 56 -->

Blocking-Flow Algorithm

Two types of augmentations.
• Normal: length of shortest path does not change.
• Special: length of shortest path strictly increases.

Phase of normal augmentations.
• Explicitly maintain level graph 𝐿𝐺.
• Start at 𝑠, advance along an edge in 𝐿𝐺until reach 𝑡or get
stuck.
• If reach 𝑡, augment and update 𝐿𝐺.
• If get stuck, delete node from 𝐿𝐺and go to previous node.

56

<!-- page: 57 -->

Dinitz’ Algorithm

Initialize (𝐺, 𝑓)
----------------------------------
𝐿𝐺←level-graph of 𝐺𝑓.
𝑃←∅.
Goto Advance (𝑠).

Advance (𝑣)
-----------------------------------------
If 𝑣= 𝑡

Augment (𝑃).
Remove saturated edge from 𝐿𝐺.
𝑃←∅.
Goto Advance (𝑠)

Retreat (𝑣)
------------------------------------------------
If 𝑣= 𝑠

If there exists edge (𝑣, 𝑤) ∈𝐿𝐺

Stop.
Else

Add edge (𝑣, 𝑤) to 𝑃.
Goto Advance (𝑤).
Else

Delete 𝑣(and all incident edges) from 𝐿𝐺.
Remove last edge (𝑢, 𝑣) from 𝑃.
Goto Advance (𝑢)

Goto Retreat (𝑣).

57
