---
source_id: algorithm-design-and-analysis-018
course_id: algorithm_design_and_analysis
title: 5-greedy
original_file: "学科资料/算法设计与分析/PPT-英文版/5-greedy-2.pdf"
document_role: note
year: 
locator_type: page
---

# 5-greedy

<!-- page: 1 -->

Design and Analysis of Algorithms

Greedy Algorithms

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

<!-- page: 2 -->

Topics

• Dijkstra’s Algorithm
• Minimum Spanning Trees
• Prim’s Algorithm
• Kruskal’s Algorithms

<!-- page: 3 -->

Single-Pair Shortest Path Problem

Problem. Given a digraph 𝐺= 𝑉, 𝐸, edge lengths 𝑙𝑒≥0,
source 𝑠∈𝑉, and destination 𝑡∈𝑉, find a shortest directed path
from 𝑠 to 𝑡.

![image](assets/assets/algorithm-design-and-analysis-018/image-001.png)

<!-- page: 4 -->

Single-Source Shortest Path Problem

Problem. Given a digraph 𝐺= 𝑉, 𝐸, edge lengths 𝑙𝑒≥0,
source 𝑠∈𝑉, find a shortest directed path from 𝑠 to every node.

![image](assets/assets/algorithm-design-and-analysis-018/image-002.png)

<!-- page: 5 -->

Car Navigation

Single-destination shortest paths problem.

![image](assets/assets/algorithm-design-and-analysis-018/image-003.jpeg)

<!-- page: 6 -->

Dijkstra’s Algorithm for Single-
Source Shortest Path Problem

Greedy approach. Maintain a set of explored nodes 𝑆 for which
algorithm has determined 𝑑𝑢= length of a shortest 𝑠→𝑢 path.
• Initialize 𝑆←𝑠, 𝑑𝑠= 0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
add 𝑣 to 𝑆, set 𝑑𝑣= 𝜋𝑣.

The length of a shortest path from 𝒔
to some node 𝒖 in explored part 𝑺,
followed by a single edge 𝒆= 𝒖, 𝒗.

![image](assets/assets/algorithm-design-and-analysis-018/image-004.png)

<!-- page: 7 -->

Dijkstra’s Algorithm for Single-
Source Shortest Path Problem
Greedy approach. Maintain a set of explored nodes 𝑆 for which
algorithm has determined 𝑑𝑢= length of a shortest 𝑠→𝑢 path.
• Initialize 𝑆←𝑠, 𝑑𝑠= 0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
add 𝑣 to 𝑆, set 𝑑𝑣= 𝜋𝑣.

The length of a shortest path from 𝒔
to some node 𝒖 in explored part 𝑺,
followed by a single edge 𝒆= 𝒖, 𝒗.

• To recover path, set 𝑝𝑟𝑒𝑑𝑣←𝑒 that achieves min.

![image](assets/assets/algorithm-design-and-analysis-018/image-005.png)

<!-- page: 8 -->

Dijkstra’s Algorithm: Proof of
Correctness
For each node 𝑢∈𝑆: 𝑑𝑢= length of a shortest 𝑠→𝑢 path.
Pf. By induction on 𝑆
Base case: 𝑆= 1 is easy since 𝑆= {𝑠} and 𝑑𝑠= 0.
Inductive hypothesis: Assume true for 𝑆≥1.
•
Let 𝑣 be next node added to 𝑆, and let (𝑢, 𝑣) be the final edge.
•
A shortest 𝑠→𝑢 path plus (𝑢, 𝑣) is an 𝑠→𝑣 path of length 𝜋𝑣.
•
Consider any other 𝑠→𝑣 path 𝑃. We show that
it is no shorter than 𝜋𝑣.
•
Let 𝑒= (𝑥, 𝑦) be the first edge in 𝑃 that
leaves 𝑆, and let 𝑃′ be the sub-path to 𝑥.
•
The length of 𝑃 is already ≥𝜋𝑣
as soon as it reaches 𝑦:

𝑙𝑃≥𝑙𝑃′ + 𝑙𝑒≥𝑑𝑥+ 𝑙𝑒≥𝜋𝑦≥𝜋𝑣

Dijkstra chose
𝑣instead of 𝑦

Non-negative
lengths

Inductive
hypothesis

Definition of
𝜋𝑦

![image](assets/assets/algorithm-design-and-analysis-018/image-006.png)

<!-- page: 9 -->

Dijkstra’s Algorithm Demo

• Initialize 𝑆←{𝑠} and 𝑑[𝑠] ←0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
Add 𝑣 to 𝑆; set 𝑑[𝑣] ←𝜋𝑣 and 𝑝𝑟𝑒𝑑𝑣← argmin.

The length of a shortest path
from 𝑠to some node u in
explored part 𝑆, followed by
a single edge 𝑒= 𝑢, 𝑣.

![image](assets/assets/algorithm-design-and-analysis-018/image-007.png)

<!-- page: 10 -->

Dijkstra’s Algorithm Demo

• Initialize 𝑆←{𝑠} and 𝑑[𝑠] ←0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
Add 𝑣 to 𝑆; set 𝑑[𝑣] ←𝜋𝑣 and 𝑝𝑟𝑒𝑑𝑣← argmin.

The length of a shortest path
from 𝑠to some node u in
explored part 𝑆, followed by
a single edge 𝑒= 𝑢, 𝑣.

![image](assets/assets/algorithm-design-and-analysis-018/image-008.png)

<!-- page: 11 -->

Dijkstra’s Algorithm Demo

• Initialize 𝑆←{𝑠} and 𝑑[𝑠] ←0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
Add 𝑣 to 𝑆; set 𝑑[𝑣] ←𝜋𝑣 and 𝑝𝑟𝑒𝑑𝑣← argmin.

The length of a shortest path
from 𝑠to some node u in
explored part 𝑆, followed by
a single edge 𝑒= 𝑢, 𝑣.

![image](assets/assets/algorithm-design-and-analysis-018/image-009.png)

<!-- page: 12 -->

Dijkstra’s Algorithm Demo

• Initialize 𝑆←{𝑠} and 𝑑[𝑠] ←0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
Add 𝑣 to 𝑆; set 𝑑[𝑣] ←𝜋𝑣 and 𝑝𝑟𝑒𝑑𝑣← argmin.

The length of a shortest path
from 𝑠to some node u in
explored part 𝑆, followed by
a single edge 𝑒= 𝑢, 𝑣.

![image](assets/assets/algorithm-design-and-analysis-018/image-010.png)

<!-- page: 13 -->

Dijkstra’s Algorithm Demo

• Initialize 𝑆←{𝑠} and 𝑑[𝑠] ←0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
Add 𝑣 to 𝑆; set 𝑑[𝑣] ←𝜋𝑣 and 𝑝𝑟𝑒𝑑𝑣← argmin.

The length of a shortest path
from 𝑠to some node u in
explored part 𝑆, followed by
a single edge 𝑒= 𝑢, 𝑣.

![image](assets/assets/algorithm-design-and-analysis-018/image-011.png)

<!-- page: 14 -->

Dijkstra’s Algorithm Demo

• Initialize 𝑆←{𝑠} and 𝑑[𝑠] ←0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
Add 𝑣 to 𝑆; set 𝑑[𝑣] ←𝜋𝑣 and 𝑝𝑟𝑒𝑑𝑣← argmin.

The length of a shortest path
from 𝑠to some node u in
explored part 𝑆, followed by
a single edge 𝑒= 𝑢, 𝑣.

![image](assets/assets/algorithm-design-and-analysis-018/image-012.png)

<!-- page: 15 -->

Dijkstra’s Algorithm Demo

• Initialize 𝑆←{𝑠} and 𝑑[𝑠] ←0.
• Repeatedly choose unexplored node 𝑣∉𝑆 which minimizes
𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
Add 𝑣 to 𝑆; set 𝑑[𝑣] ←𝜋𝑣 and 𝑝𝑟𝑒𝑑𝑣← argmin.

The length of a shortest path
from 𝑠to some node u in
explored part 𝑆, followed by
a single edge 𝑒= 𝑢, 𝑣.

![image](assets/assets/algorithm-design-and-analysis-018/image-013.png)

<!-- page: 16 -->

Dijkstra’s Algorithm: Efficient
Implementation

Critical optimization 1. For each unexplored node 𝑣∉𝑆: explicitly
maintain 𝜋[𝑣] instead of computing directly from definition

𝜋𝑣=
min
𝑒= 𝑢,𝑣:𝑢∈𝑆𝑑𝑢+ 𝑙𝑒
• For each 𝑣∉𝑆: 𝜋𝑣can only decrease (because 𝑆only
increases).
• More specifically, suppose 𝑢is added to 𝑆and there is an edge
𝑒= (𝑢, 𝑣) leaving 𝑢. Then, it suffices to update:

𝜋[𝑣] ←min{𝜋𝑣, 𝜋𝑢+ 𝑙𝑒}
Recall: for each 𝑢∈𝑆, 𝜋𝑢= 𝑑𝑢=length of shortest 𝑠→𝑢
path.
Critical optimization 2. Use a min-oriented priority queue (PQ) to
choose an unexplored node that minimizes 𝜋[𝑣].

<!-- page: 17 -->

Dijkstra’s Algorithm: Efficient
Implementation

Implementation.
•
Algorithm stores 𝜋[𝑣] for each node 𝑣.
•
Priority Queue (PQ) stores unexplored nodes, using 𝜋[. ] as priorities.
•
Once 𝑢 is deleted from the PQ, 𝜋𝑢= length of a shortest 𝑠→𝑢 path.

Dijkstra (𝑉, 𝐸, 𝑙, 𝑠)
Create an empty priority queue PQ.
for each 𝑣≠𝑠: 𝜋𝑣←∞, 𝑝𝑟𝑒𝑑𝑣←𝑛𝑢𝑙𝑙; 𝜋𝑠←0.
for each 𝑣∈𝑉: Insert (PQ, 𝑣, 𝜋𝑣).
while Is-Not-Empty (PQ)

𝑢← Del-Min (PQ).
for each edge 𝑒= (𝑢, 𝑣) ∈𝐸leaving u:

if 𝜋𝑣> 𝜋𝑢+ 𝑙𝑒

Decrease-Key (PQ, 𝑣, 𝜋𝑢+ 𝑙𝑒).
             𝜋𝑣←𝜋𝑢+ 𝑙𝑒; 𝑝𝑟𝑒𝑑𝑣←𝑒.

<!-- page: 18 -->

Dijkstra’s Algorithm Demo
(Efficient Implementation)

Initialization.
• For all 𝑣≠𝑠: 𝜋[𝑣] ←∞.
• For all 𝑣≠𝑠: 𝑝𝑟𝑒𝑑[𝑣] ←𝑛𝑢𝑙𝑙.
• S ←∅ and 𝜋[𝑠] ←0.

![image](assets/assets/algorithm-design-and-analysis-018/image-014.png)

<!-- page: 19 -->

Dijkstra’s Algorithm Demo
(Efficient Implementation)

Basic step. Choose unexplored node 𝑢≠𝑠with minimum 𝜋[𝑢].
• Add 𝑢to 𝑆.
• For each edge e = (𝑢, 𝑣) leaving 𝑢, if 𝜋𝑣> 𝜋𝑢+ 𝑙𝑒then:
- 𝜋[𝑣] ←𝜋𝑢+ 𝑙𝑒.
- 𝑝𝑟𝑒𝑑[𝑣] ←𝑒.

![image](assets/assets/algorithm-design-and-analysis-018/image-015.png)

<!-- page: 20 -->

Dijkstra’s Algorithm Demo
(Efficient Implementation)

Basic step. Choose unexplored node 𝑢≠𝑠with minimum 𝜋[𝑢].
• Add 𝑢to 𝑆.
• For each edge e = (𝑢, 𝑣) leaving 𝑢, if 𝜋𝑣> 𝜋𝑢+ 𝑙𝑒then:
- 𝜋[𝑣] ←𝜋𝑢+ 𝑙𝑒.
- 𝑝𝑟𝑒𝑑[𝑣] ←𝑒.

![image](assets/assets/algorithm-design-and-analysis-018/image-016.png)

<!-- page: 21 -->

Cycles and Cuts

Def. A path is a sequence of edges which connects a sequence of
nodes.
Def. A cycle is a path with no repeated nodes or edges other than
the starting and ending nodes.

![image](assets/assets/algorithm-design-and-analysis-018/image-017.png)

<!-- page: 22 -->

Cycles and Cuts

Def. A cut is a partition of the nodes into two nonempty subset 𝑆
and 𝑉−𝑆.
Def. The cutset determined by a cut is the set of edges that have
one endpoint in each subset of the partition.

![image](assets/assets/algorithm-design-and-analysis-018/image-018.png)

<!-- page: 23 -->

Cycle-Cut Intersection

Proposition. A cycle and a cutset intersect in an even number of
edges.

![image](assets/assets/algorithm-design-and-analysis-018/image-019.png)

<!-- page: 24 -->

Spanning Tree Definition

Def. Let 𝐻= (𝑉, 𝑇) be a subgraph of an undirected graph 𝐺=
(𝑉, 𝐸). 𝐻 is a spanning tree of 𝐺 if 𝐻 is both acyclic and
connected.

![image](assets/assets/algorithm-design-and-analysis-018/image-020.png)

<!-- page: 25 -->

Spanning Tree Properties

Proposition. Let 𝐻= (𝑉, 𝑇) be a subgraph of an undirected graph 𝐺=
(𝑉, 𝐸). Then, the following are equivalent:
•
𝐻 is a spanning tree of 𝐺.
•
𝐻is acyclic and connected.
•
𝐻is connected and has 𝑛−1 edges.
•
𝐻is acyclic and has 𝑛−1 edges.
•
𝐻is minimally connected: removal of any edge disconnects it.
•
𝐻is maximally acyclic: addition of any edge creates a cycle.

![image](assets/assets/algorithm-design-and-analysis-018/image-021.png)

<!-- page: 26 -->

Minimum Spanning Tree (MST)

Def. Given a connected, undirected graph 𝐺= (𝑉, 𝐸) with edge
costs 𝑐𝑒, a minimum spanning tree (𝑉, 𝑇) is a spanning tree of 𝐺
such that the sum of the edge costs in 𝑇 is minimized.

![image](assets/assets/algorithm-design-and-analysis-018/image-022.png)

<!-- page: 27 -->

Prim’s Algorithm

Initialize 𝑆= any node, 𝑇= ∅.
Repeat 𝑛−1 times:
• Add to 𝑇 a min-weight edge with one endpoint in 𝑆.
• Add new node to 𝑆.

Theorem. Prim’s algorithm computes an MST.

![image](assets/assets/algorithm-design-and-analysis-018/image-023.png)

<!-- page: 28 -->

Prim’s Algorithm: Implementation

Implementation almost identical to Dijkstra’s algorithm.

Prim (𝑉, 𝐸, 𝑐)
Create an empty priority queue 𝑃𝑄.
𝑆←∅, 𝑇←∅.
𝑠← any node in 𝑉.
for each 𝑣≠𝑠: 𝜋𝑣←∞, 𝑝𝑟𝑒𝑑𝑣←𝑛𝑢𝑙𝑙; 𝜋[𝑠] ←0.
for each 𝑣∈𝑉: Insert (𝑃𝑄, 𝑣, 𝜋𝑣),
while Is-Not-Empty (𝑃𝑄)

𝝅𝒗= weight of cheapest
known edge between 𝒗and 𝑺.

𝑢← Del-Min (𝑃𝑄).
𝑆←𝑆∪𝑢, 𝑇←𝑇∪{𝑝𝑟𝑒𝑑[𝑢]}.
for each edge 𝑒= (𝑢, 𝑣) ∈𝐸with 𝑣∉𝑆:

if 𝑐𝑒< 𝜋𝑣

Decrease-Key (𝑃𝑄, 𝑣, 𝑐𝑒).
            𝜋𝑣←𝑐𝑒; 𝑝𝑟𝑒𝑑[𝑣] ←𝑒.

<!-- page: 29 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-024.png)

<!-- page: 30 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

<!-- page: 31 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

<!-- page: 32 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-025.png)

<!-- page: 33 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-026.png)

<!-- page: 34 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-027.png)

<!-- page: 35 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-028.png)

<!-- page: 36 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-029.png)

<!-- page: 37 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-030.png)

<!-- page: 38 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-031.png)

<!-- page: 39 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-032.png)

<!-- page: 40 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-033.png)

<!-- page: 41 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-034.png)

<!-- page: 42 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-035.png)

<!-- page: 43 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-036.png)

<!-- page: 44 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

![image](assets/assets/algorithm-design-and-analysis-018/image-037.png)

<!-- page: 45 -->

Prim’s Algorithm Demo

Initialize S=any node, 𝑇= ∅
Repeat n-1 times:
•
Add to T a min-weight edge with one endpoint in S.
•
Add new node to S.

<!-- page: 46 -->

Kruskal’s Algorithm

Consider edges in ascending order of weight:
• Add to tree unless it would create a cycle.

Theorem. Kruskal’s algorithm computes an MST.

<!-- page: 47 -->

Kruskal’s Algorithm: Implementation

•
Sort edges by weights.
•
Use union-find data structure to dynamically maintain connected
components.

Kruskal (𝑉, 𝐸, 𝑐)
Sort 𝑚 edges by weight so that 𝑐𝑒1 ≤𝑐𝑒1 ≤⋯≤𝑐𝑒𝑚.
𝑇←∅.
for each 𝑣∈𝑉: Make-Set (𝑣).
for 𝑖= 1 to 𝑚

(𝑢, 𝑣) ←𝑒𝑖.
if Find-Set (𝑢) ≠ Find-Set (𝑣)

are 𝑢and 𝑣in
same component?

𝑇←𝑇∪{𝑒𝑖}.
Union (𝑢, 𝑣).
Return 𝑇.

make 𝑢and 𝑣in
same component

<!-- page: 48 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 49 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 50 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 51 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 52 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 53 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 54 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 55 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 56 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 57 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 58 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 59 -->

Kruskal’s Algorithm Demo

Consider edges in ascending order of weight:
•
Add to T unless it would create a cycle.

<!-- page: 60 -->

Proof of Kruskal’s Algorithm

Theorem. After running Kruskal’s algorithm on a connected weight
graph 𝐺, its output 𝑇is a minimum weight spanning tree.

<!-- page: 61 -->

Proof of Kruskal’s Algorithm

Theorem. After running Kruskal’s algorithm on a connected weight
graph 𝐺, its output 𝑇is a minimum weight spanning tree.

Proof. First, 𝑇is a spanning tree. This is because:
•
𝑇is a acyclic.
•
𝑇is spanning.
•
𝑇is connected.

Second, 𝑇is a spanning tree of minimum weight. We can prove
this using induction:
Let 𝑇∗be a minimum-weight spanning tree. If 𝑇= 𝑇∗, then 𝑇is a
minimum weight spanning tree. If 𝑇≠𝑇∗, then there exist an
edge 𝑒∈𝑇∗of minimum weight that is not in 𝑇. Further, 𝑇∪{𝑒}
contains a cycle 𝐶such that:
a.
Every edge in 𝐶has weight less than 𝑤𝑒𝑖𝑔ℎ𝑡(𝑒) . (This follows
from how the algorithm constructed 𝑇.)

<!-- page: 62 -->

Proof of Kruskal’s Algorithm

Theorem. After running Kruskal’s algorithm on a connected weight
graph 𝐺, its output 𝑇is a minimum weight spanning tree.

If 𝑇= 𝑇∗, then there exist an edge 𝑒∈𝑇∗of minimum weight that
is not in 𝑇. Further, 𝑇∪{𝑒} contains a cycle 𝐶such that:
a.
Other edges in 𝐶have weights less than 𝑤𝑒𝑖𝑔ℎ𝑡(𝑒) . (This
follows from how the algorithm constructed 𝑇.)
b.
There is some edge 𝑓in 𝐶that is not in 𝑇∗. (Because 𝑇∗does
not contain the cycle 𝐶.) Consider the tree 𝑇2 = 𝑇∪{𝑒}\{𝑓}:
c.
𝑇2 is a spanning tree.
d.
𝑇2 has more edges in common with 𝑇∗than 𝑇did.
e.
And 𝑤𝑒𝑖𝑔ℎ𝑡(𝑇2) ≥𝑤𝑒𝑖𝑔ℎ𝑡(𝑇). (We exchanged an edge for
one that is no more expensive.)

We can redo the same process with 𝑇2 to find a spanning tree 𝑇3
with more edge in common with 𝑇∗.

<!-- page: 63 -->

Proof of Kruskal’s Algorithm

Theorem. After running Kruskal’s algorithm on a connected weight
graph 𝐺, its output 𝑇is a minimum weight spanning tree.

We can redo the same process with 𝑇2 to find a spanning tree 𝑇3
with more edge in common with 𝑇∗. By induction, we can
continue this process until we reach 𝑇∗, from which we see

𝑤𝑒𝑖𝑔ℎ𝑡𝑇≤𝑤𝑒𝑖𝑔ℎ𝑡𝑇2 ≤𝑤𝑒𝑖𝑔ℎ𝑡𝑇3 ≤⋯≤𝑤𝑒𝑖𝑔ℎ𝑡(𝑇∗)

Since 𝑇∗is a minimum weight spanning tree, then these
inequalities must be equalities and we conclude that 𝑇is a
minimum weight spanning tree.
