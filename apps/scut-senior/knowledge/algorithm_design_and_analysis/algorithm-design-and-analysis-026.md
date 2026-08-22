---
source_id: algorithm-design-and-analysis-026
course_id: algorithm_design_and_analysis
title: 9-networkFlow
original_file: "学科资料/算法设计与分析/PPT-英文版/9-networkFlow-2.pdf"
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

• Image Segmentation
• Bipartite Matching
• Disjoint Paths

2

<!-- page: 3 -->

Image Segmentation

Image segmentation.
• Central problem in image processing.
• Divide image into coherent regions.

Ex. Three people standing in front of complex background scene.
Identify each person as a coherent object.

Semantic segmentation

3

![image](assets/assets/algorithm-design-and-analysis-026/image-001.jpeg)

![image](assets/assets/algorithm-design-and-analysis-026/image-002.jpeg)

<!-- page: 4 -->

Image Segmentation

Foreground/background segmentation.
• Label each pixel in picture as belonging to foreground or
background.
• 𝑉= set of pixels, 𝐸= pairs of neighboring pixels.
• 𝑎𝑖≥0 is likelihood pixel 𝑖in foreground.
• 𝑏𝑖≥0 is likelihood pixel 𝑖in background.
• 𝑝𝑖𝑗≥0 is separation penalty for labeling one of 𝑖and 𝑗as
foreground, and the other as background.

4

<!-- page: 5 -->

Image Segmentation

Foreground/background segmentation.
• Label each pixel in picture as belonging to foreground or
background.
• 𝑉= set of pixels, 𝐸= pairs of neighboring pixels.
• 𝑎𝑖≥0 is likelihood pixel 𝑖in foreground.
• 𝑏𝑖≥0 is likelihood pixel 𝑖in background.
• 𝑝𝑖𝑗≥0 is separation penalty for labeling one of 𝑖and 𝑗as
foreground, and the other as background.
Goals.
• Accuracy: if 𝑎𝑖> 𝑏𝑖in isolation, prefer to label 𝑖in foreground.
• Smoothness: if many neighbors of 𝑖are labeled foreground, we
should be inclined to label 𝑖as foreground.
• Find partition (𝐴, 𝐵) that maximizes:
σ𝑖∈𝐴𝑎𝑖+ σ𝑗∈𝐵𝑏𝑗−σ 𝑖,𝑗∈𝐸, 𝐴∩𝑖,𝑗=1 𝑝𝑖𝑗

5

<!-- page: 6 -->

Image Segmentation

Formulate as min-cut problem.
• Maximization
• No source or sink.
• Undirected graph.

Turn into minimization problem.
• Maximizing σ𝑖∈𝐴𝑎𝑖+ σ𝑗∈𝐵𝑏𝑗−σ 𝑖,𝑗∈𝐸, 𝐴∩𝑖,𝑗=1 𝑝𝑖𝑗

• Is equivalent to minimizing

σ𝑖∈𝑉𝑎𝑖+ σ𝑗∈𝑉𝑏𝑗−σ𝑖∈𝐴𝑎𝑖−σ𝑗∈𝐵𝑏𝑗+ σ 𝑖,𝑗∈𝐸, 𝐴∩𝑖,𝑗=1 𝑝𝑖𝑗

• Or alternatively σ𝑗∈𝐵𝑎𝑗+ σ𝑖∈𝐴𝑏𝑖+ σ 𝑖,𝑗∈𝐸, 𝐴∩𝑖,𝑗=1 𝑝𝑖𝑗

6

<!-- page: 7 -->

Image Segmentation

Formulate as min-cut problem 𝐺′ = (𝑉′, 𝐸′).
• Include node for each pixel.
• Use two antiparallel edges instead of
undirected edge.
• Add source 𝑠to correspond to foreground.
• Add sink 𝑡to correspond to background.

7

![image](assets/assets/algorithm-design-and-analysis-026/image-003.png)

<!-- page: 8 -->

Image Segmentation

Consider min cut (𝐴, 𝐵) in 𝐺′.
• 𝐴= foreground.

𝑐𝑎𝑝𝐴, 𝐵= ෍

𝑎𝑗+ ෍

𝑏𝑖+
෍

𝑝𝑖𝑗

𝑗∈𝐵

𝑖∈𝐴

𝑖,𝑗∈𝐸,𝑖∈𝐴,𝑗∈𝐵

• The quantity we want to minimize.

8

![image](assets/assets/algorithm-design-and-analysis-026/image-004.png)

<!-- page: 9 -->

Image Segmentation

9

![image](assets/assets/algorithm-design-and-analysis-026/image-005.jpeg)

<!-- page: 10 -->

Bipartite Matching

Def. A graph 𝐺is bipartite if the nodes can be partitioned into two
subsets 𝐿and 𝑅such that every edge connects a node in 𝐿to one
in 𝑅.

Bipartite matching. Given a bipartite graph 𝐺= (𝐿∪𝑅, 𝐸), find a
max-cardinality matching.

10

![image](assets/assets/algorithm-design-and-analysis-026/image-006.png)

<!-- page: 11 -->

Bipartite Matching

Def. A graph 𝐺is bipartite if the nodes can be partitioned into two
subsets 𝐿and 𝑅such that every edge connects a node in 𝐿to one in 𝑅.

Bipartite matching. Given a bipartite graph 𝐺= (𝐿∪𝑅, 𝐸), find a max-
cardinality matching.

The Ford-Fulkerson algorithm can be implemented to solve the bipartite
matching problem.

11

![image](assets/assets/algorithm-design-and-analysis-026/image-007.png)

<!-- page: 12 -->

Bipartite Matching: Max-Flow
Formulation
• Create digraph 𝐺′ = (𝐿∪𝑅∪𝑠, 𝑡, 𝐸′).
• Direct all edges from 𝐿to 𝑅, and assign infinite (or unit)
capacity.
• Add source 𝑠, and unit-capacity edges from 𝑠to each node in 𝐿.
• Add sink 𝑡, and unit-capacity edges from each node in 𝑅to 𝑡.

12

![image](assets/assets/algorithm-design-and-analysis-026/image-008.png)

<!-- page: 13 -->

Max-Flow Formulation: Proof of
Correctness
Theorem. Max cardinality of a matching in 𝐺= value of max flow in  𝐺′.
Pf. ≤
• Given a max matching 𝑀of cardinality 𝑘.
• Consider flow 𝑓that sends 1 unit along each of 𝑘paths.
• 𝑓is a flow, and has value 𝑘.

13

![image](assets/assets/algorithm-design-and-analysis-026/image-009.png)

<!-- page: 14 -->

Max-Flow Formulation: Proof of
Correctness
Theorem. Max cardinality of a matching in 𝐺= value of max flow in  𝐺′.
Pf. ≥
•
Let 𝑓be a max flow in 𝐺′ of value 𝑘.
•
Integrality theorem ⟹𝑘is integral and can assume 𝑓is 0-1.
•
Consider 𝑀= set of edges from 𝐿to 𝑅with 𝑓𝑒= 1.
-
Each node in 𝐿and 𝑅participates in at most one edge in 𝑀
-
𝑀= 𝑘: consider cut (𝐿∪𝑠, 𝑅∪{𝑡}).

14

![image](assets/assets/algorithm-design-and-analysis-026/image-010.png)

<!-- page: 15 -->

Bipartite Matching

Bipartite matching. Can solve via reduction to maximum flow.

Flow. During Ford-Fulkerson, all residual capacities and flows are
0-1; flow corresponds to edges in a matching 𝑀.

Residual graph 𝐺𝑀simplifies to:
• If (𝑥, 𝑦) ∉𝑀, then (𝑥, 𝑦) is in 𝐺𝑀.
• If (𝑥, 𝑦) ∈𝑀, then (𝑦, 𝑥) is in 𝐺𝑀.

Augmenting path simplifies to:
• Edge from 𝑠to an unmatched node 𝑥∈𝑋,
• Alternating sequence of unmatched and matched edges,
• Edge from unmatched node 𝑦∈𝑌to 𝑡.

15

<!-- page: 16 -->

Alternating Path

Def. An alternating path 𝑃with respect to a matching 𝑀is an
alternating sequence of unmatched and matched edges, starting
from an unmatched node 𝑥∈𝑋and going to an unmatched node
𝑦∈𝑌.

Key property. Can use 𝑃to increase by one the cardinality of the
matching.

16

![image](assets/assets/algorithm-design-and-analysis-026/image-011.png)

<!-- page: 17 -->

Edge-Disjoint Paths

Def. Two paths are edge-disjoint if they have no edge in common.

Disjoint path problem. Given a digraph 𝐺= (𝑉, 𝐸) and two nodes
𝑠and 𝑡, find the max number of edge-disjoint 𝑠→𝑡paths.

17

![image](assets/assets/algorithm-design-and-analysis-026/image-012.png)

<!-- page: 18 -->

Edge-Disjoint Paths

Def. Two paths are edge-disjoint if they have no edge in common.

Disjoint path problem. Given a digraph 𝐺= (𝑉, 𝐸) and two nodes
𝑠and 𝑡, find the max number of edge-disjoint 𝑠→𝑡paths.

18

![image](assets/assets/algorithm-design-and-analysis-026/image-013.png)

<!-- page: 19 -->

Edge-Disjoint Paths

Max-flow formulation. Assign unit capacity to every edge.

Theorem. Max number of edge-disjoint 𝑠→𝑡paths equals value of max flow.
Pf. ≤
•
Suppose there are 𝑘edge-disjoint 𝑠→𝑡paths 𝑃1, … , 𝑃𝑘.
•
Set 𝑓𝑒= 1 if 𝑒participates in some path 𝑃𝑗, else set 𝑓𝑒= 0.
•
Since paths are edge-disjoint, 𝑓is a flow of value 𝑘.

19

![image](assets/assets/algorithm-design-and-analysis-026/image-014.png)

<!-- page: 20 -->

Edge-Disjoint Paths

Max-flow formulation. Assign unit capacity to every edge.

Theorem. Max number of edge-disjoint 𝑠→𝑡paths equals value of max flow.
Pf. ≥
•
Suppose max flow value is 𝑘.
•
Integrality theorem ⟹there exists 0-1 flow 𝑓of value 𝑘.
•
Consider edge (𝑠, 𝑢) with 𝑓𝑠, 𝑢= 1.
- By flow conservation, there exists an edge (𝑢, 𝑣) with 𝑓𝑢, 𝑣= 1
- Continue until reach 𝑡, always choosing a new edge
•
Produces 𝑘edge-disjoint paths.

20

![image](assets/assets/algorithm-design-and-analysis-026/image-015.png)

<!-- page: 21 -->

Network Connectivity

Def. A set of edges 𝐹⊆𝐸disconnects 𝑡from 𝑠if every 𝑠→𝑡path
uses at least one edge in 𝐹.

Network connectivity. Given a digraph 𝐺= (𝑉, 𝐸) and two nodes
𝑠and 𝑡, find min number of edges whose removal disconnects 𝑡
from 𝑠.

21

![image](assets/assets/algorithm-design-and-analysis-026/image-016.png)

<!-- page: 22 -->

Menger’s Theorem

Theorem. The max number of edge-disjoint 𝑠→𝑡paths equals the min
number of edges whose removal disconnects 𝑡from 𝑠.

Pr. ≤
• Suppose the removal of 𝐹⊆𝐸disconnects 𝑡from 𝑠, and 𝐹= 𝑘.
• Every 𝑠→𝑡path uses at least one edge in 𝐹.
• Hence, the number of edge-disjoint paths is ≤𝑘.

22

![image](assets/assets/algorithm-design-and-analysis-026/image-017.png)

<!-- page: 23 -->

Menger’s Theorem

Theorem. The max number of edge-disjoint 𝑠→𝑡paths equals the min
number of edges whose removal disconnects 𝑡from 𝑠.

Pr. ≥
• Suppose max number of edge-disjoint paths is 𝑘.
• Then value of max flow = 𝑘.
• Max-flow min-cut theorem ⟹there exists a cut (𝐴, 𝐵) of capacity 𝑘.
• Let 𝐹be set of edges going from 𝐴to 𝐵.
•
𝐹= 𝑘and disconnects 𝑡from 𝑠.

23

![image](assets/assets/algorithm-design-and-analysis-026/image-018.png)
