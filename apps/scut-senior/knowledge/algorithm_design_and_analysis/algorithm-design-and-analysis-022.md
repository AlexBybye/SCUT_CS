---
source_id: algorithm-design-and-analysis-022
course_id: algorithm_design_and_analysis
title: 7-dynamic
original_file: "学科资料/算法设计与分析/PPT-英文版/7-dynamic-2.pdf"
document_role: note
year: 
locator_type: page
---

# 7-dynamic

<!-- page: 1 -->

Design and Analysis of Algorithms

Dynamic Programming

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

1

<!-- page: 2 -->

Topics

• RNA Secondary Structure
• Bellman-Ford Algorithm
• Sequence Alignment

2

<!-- page: 3 -->

RNA Secondary Structure

RNA. String 𝐵= 𝑏1𝑏2 … 𝑏𝑛over alphabet {A, C, G, U}.

Secondary structure. RNA is single-stranded so it tends to loop
back and form base pairs with itself. This structure is essential for
understanding behavior of molecule.

3

![image](assets/assets/algorithm-design-and-analysis-022/image-001.png)

<!-- page: 4 -->

RNA Secondary Structure

Secondary structure. A set of pairs 𝑆= {(𝑏𝑖, 𝑏𝑗)} that satisfy:
• Each pair in 𝑆is a Watson-Crick complement: A-U, U-A, C-G, or
G-C.
• The ends of each pair are separated by at least 4 intervening
bases. If (𝑏𝑖, 𝑏𝑗) ∈𝑆, then 𝑖< 𝑗−4.
• If (𝑏𝑖, 𝑏𝑗) and (𝑏𝑘, 𝑏𝑙) are two pairs in 𝑆, then we cannot have
𝑖< 𝑘< 𝑗< 𝑙.

Free energy. Usual hypothesis is that an RNA molecule will form
the secondary structure with the minimum total free energy.
(approximate by the number of base pairs)

Goal. Given an RNA molecule 𝐵= 𝑏1𝑏2 … 𝑏𝑛, find a secondary
structure 𝑆that maximizes the number of base pairs.
4

<!-- page: 5 -->

RNA Secondary Structure

Examples.

5

![image](assets/assets/algorithm-design-and-analysis-022/image-002.png)

<!-- page: 6 -->

RNA Secondary Structure:
Sub-problems
First attempt. 𝑂𝑃𝑇𝑗= maximum number of base pairs in a
secondary of the substring 𝑏1𝑏2 … 𝑏𝑗.

Goal. 𝑂𝑃𝑇𝑛

Choice. Match bases 𝑏𝑡and 𝑏𝑛.

6

<!-- page: 7 -->

RNA Secondary Structure:
Sub-problems
First attempt. 𝑂𝑃𝑇𝑗= maximum number of base pairs in a
secondary of the substring 𝑏1𝑏2 … 𝑏𝑗.

Goal. 𝑂𝑃𝑇𝑛

Choice. Match bases 𝑏𝑡and 𝑏𝑛.

Difficulty. Results in two sub-problems.
• Find secondary structure in 𝑏1𝑏2 … 𝑏𝑡−1. (𝑂𝑃𝑇𝑡−1 )
• Find secondary structure in 𝑏𝑡+1𝑏2 … 𝑏𝑛−1.  (need more sub-
problems)
7

<!-- page: 8 -->

Dynamic Programming Over Intervals

Notation. 𝑂𝑃𝑇𝑖, 𝑗= maximum number of base pairs in a
secondary of the substring 𝑏𝑖𝑏𝑖+1 … 𝑏𝑗.

Case 1. If 𝑖≥𝑗−4.
• 𝑂𝑃𝑇𝑖, 𝑗= 0 by no-sharp turns condition.

Case 2. Bases 𝑏𝑗is not involved in a pair.
• 𝑂𝑃𝑇𝑖, 𝑗= 𝑂𝑃𝑇(𝑖, 𝑗−1).

Case 3. Bases 𝑏𝑗pairs with 𝑏𝑡for some 𝑖≤𝑡< 𝑗−4.
• Non-crossing constraint decouples resulting sub-problems.
• 𝑂𝑃𝑇𝑖, 𝑗= 1 + max
𝑡{𝑂𝑃𝑇𝑖, 𝑡−1 + 𝑂𝑃𝑇(𝑡+ 1, 𝑗−1)} .

(take max over 𝑡such that 𝑖≤𝑡< 𝑗−4 , 𝑏𝑡and 𝑏𝑗are Watson-
Crick complements)

8

<!-- page: 9 -->

Bottom-Up Dynamic Programming
Over Intervals

Q. In which order to solve the sub-problems?
A. Do shortest intervals first.

RNA-Secondary-Structure (𝑛, 𝑏1, 𝑏2, … , 𝑏𝑛)
--------------------------------------------------------
For 𝑘= 5 To 𝑛−1

For 𝑖= 1 To 𝑛−𝑘

𝑗←𝑖+ 𝑘.
For each 𝑏𝑡(𝑖≤𝑡< 𝑗−4) paired with 𝑏𝑗

𝑇= 1 + 𝑀𝑖, 𝑡−1 + 𝑀𝑡+ 1, 𝑗−1 .
𝑀[𝑖, 𝑗] ←max{𝑀𝑖, 𝑗−1 , 𝑇}.
Return 𝑀[1, 𝑛].

9

<!-- page: 10 -->

RNA Secondary Structure: An Example

RNA sequence. A  C  C G  G U  A  G  U

1    2    3    4    5    6    7   8     9

RNA-Secondary-Structure (𝑛, 𝑏1, 𝑏2, … , 𝑏𝑛)
--------------------------------------------------------
For 𝑘= 5 To 𝑛−1

For 𝑖= 1 To 𝑛−𝑘

𝑗←𝑖+ 𝑘.
For each 𝑏𝑡(𝑖≤𝑡< 𝑗−4) paired with 𝑏𝑗

𝑇= 1 + 𝑀𝑖, 𝑡−1 + 𝑀𝑡+ 1, 𝑗−1 .
𝑀[𝑖, 𝑗] ←max{𝑀𝑖, 𝑗−1 , 𝑇}.
Return 𝑀[1, 𝑛].

10

![image](assets/assets/algorithm-design-and-analysis-022/image-003.png)

<!-- page: 11 -->

1    2    3    4    5    6    7   8     9
𝑖≤𝑡< 𝑗−4
RNA Secondary Structure: An Example

RNA sequence. A  C  C G  G U  A  G  U

11

![image](assets/assets/algorithm-design-and-analysis-022/image-004.png)

<!-- page: 12 -->

Shortest Paths

Shortest-path problem. Given a digraph 𝐺= (𝑉, 𝐸), with arbitrary
edge weights or cost 𝑐𝑣𝑤, find cheapest path from node 𝑠to node
𝑡.

12

![image](assets/assets/algorithm-design-and-analysis-022/image-005.png)

<!-- page: 13 -->

Shortest Paths: Failed Attempts

Dijkstra. May not produce shortest paths when edge weights are
negatives.

Reweighting. Adding a constant to every edge weight does not
necessarily make Dijkstra’s algorithm produce shortest paths.

13

<!-- page: 14 -->

Negative Cycles

Def. A negative cycle is a directed cycle such that sum of its edge
weight is negative.

14

![image](assets/assets/algorithm-design-and-analysis-022/image-006.png)

<!-- page: 15 -->

Shortest Paths and Negative Cycles

Lemma 1. If some path from 𝑣to 𝑡contains a negative cycle, then
there does not exist a cheapest path from 𝑣to 𝑡.

15

<!-- page: 16 -->

Shortest Paths and Negative Cycles

Lemma 1. If some path from 𝑣to 𝑡contains a negative cycle, then
there does not exist a cheapest path from 𝑣to 𝑡.

Pf.
If there exists such a cycle 𝑊, then can build a 𝑣→𝑡path of
arbitrarily negative weight by detouring around cycle as many
times as desired.

16

<!-- page: 17 -->

Shortest Paths and Negative Cycles

Lemma 2. If G has no negative cycles, then there exists a cheapest
path from 𝑣to 𝑡that is simple (i.e. does not repeat nodes), and
hence has at most ≤𝑛−1 edges.

Pf.
• Consider a cheapest 𝑣→𝑡path 𝑃that uses the fewest edges.
• If 𝑃contains a cycle 𝑊, can remove portion of 𝑃corresponding
to 𝑊without increasing the cost.

17

<!-- page: 18 -->

Shortest Paths and Negative-Cycles
Problems
Single-destination shortest-paths problem. Given a digraph G =
(𝑉, 𝐸) with edge weights 𝑐𝑣𝑤, and no negative cycles and a
distinguished note 𝑡, find cheapest 𝑣→𝑡path for each node 𝑣.

Negative-cycle problem. Given a digraph G = (𝑉, 𝐸) with edge
weights 𝑐𝑣𝑤, find a negative cycle (if one exists).

18

![image](assets/assets/algorithm-design-and-analysis-022/image-007.png)

<!-- page: 19 -->

Shortest Paths: Dynamic Programming

Def. 𝑂𝑃𝑇𝑖, 𝑣= cost of shortest 𝑣→𝑡path that uses ≤𝑖edges.

• Case 1: Cheapest 𝑣→𝑡path uses ≤𝑖−1 edges.
‒ 𝑂𝑃𝑇𝑖, 𝑣= 𝑂𝑃𝑇(𝑖−1, 𝑣).

• Case 2: Cheapest 𝑣→𝑡path uses exactly 𝑖edges.
‒ If (𝑣, 𝑤) is the first edge, then 𝑂𝑃𝑇uses (𝑣, 𝑤), and then

selects best 𝑤→𝑡path using ≤𝑖−1 edges.

∞
𝑖𝑓𝑖= 0
min 𝑂𝑃𝑇𝑖−1, 𝑣, min

𝑂𝑃𝑇𝑖, 𝑣= ቐ

𝑣,𝑤∈𝐸𝑂𝑃𝑇𝑖−1, 𝑤+ 𝑐𝑣𝑤
𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒

Observation. If no negative cycles, 𝑂𝑃𝑇𝑛−1, 𝑣= cost of
cheapest 𝑣→𝑡path.

19

<!-- page: 20 -->

Shortest Paths: Implementation

Shortest-Paths (𝑉, 𝐸, 𝑐, 𝑡)
-------------------------------------------------------------------
For each node 𝑣∈𝑉

𝑀[0, 𝑣] ←∞.

𝑀[0, 𝑡] ←0.
For 𝑖= 0 To 𝑛−1

For each node 𝑣∈𝑉

𝑀𝑖, 𝑣←𝑀[𝑖−1, 𝑣].
For each edge (𝑣, 𝑤) ∈𝐸

𝑀𝑖, 𝑣←min{𝑀𝑖, 𝑣, 𝑀𝑖−1, 𝑤+ 𝑐𝑣𝑤}.

20

<!-- page: 21 -->

Shortest Paths: An Example

Ex. Considering the following directed graph, find a
shortest path from each node to 𝑡.

Shortest-Paths (𝑉, 𝐸, 𝑐, 𝑡)
------------------------------------------
For each node 𝑣∈𝑉

𝑀[0, 𝑣] ←∞.
𝑀[0, 𝑡] ←0.
For 𝑖= 0 To 𝑛−1

For each node 𝑣∈𝑉

𝑀𝑖, 𝑣←𝑀[𝑖−1, 𝑣].
For each edge (𝑣, 𝑤) ∈𝐸

𝑀𝑖, 𝑣←min{𝑀𝑖, 𝑣, 𝑀𝑖−1, 𝑤+ 𝑐𝑣𝑤}.
21

![image](assets/assets/algorithm-design-and-analysis-022/image-008.png)

<!-- page: 22 -->

Shortest Paths: An Example

Ex. Considering the following directed graph, find a
shortest path from each node to 𝑡.

Each row corresponds to the shortest path
from a node to 𝑡, as we allow the path to
use an increasing number of edges
22

![image](assets/assets/algorithm-design-and-analysis-022/image-009.png)

![image](assets/assets/algorithm-design-and-analysis-022/image-010.png)

<!-- page: 23 -->

Detecting Negative Cycles

Negative cycle detection problem: Given a digraph
𝐺(𝑉, 𝐸), with edge lengths ℓ𝑣𝑤, find a negative cycle (if
one exists).

23

![image](assets/assets/algorithm-design-and-analysis-022/image-011.png)

<!-- page: 24 -->

Detecting Negative Cycles: Application

Currency conversion: Given 𝑛currencies and exchange
rates between pairs of currencies, is there an arbitrage
opportunity?
Remark. Fastest algorithm very valuable!

24

![image](assets/assets/algorithm-design-and-analysis-022/image-012.jpeg)

<!-- page: 25 -->

Detecting Negative Cycles

Lemma 1. If 𝑂𝑃𝑇𝑛, 𝑣= 𝑂𝑃𝑇(𝑛−1, 𝑣) for every node
𝑣, then no negative cycles.
Pf. The 𝑂𝑃𝑇𝑛, 𝑣values have converged ⟹shortest
𝑣→𝑡path exists.

Lemma 2. If 𝑂𝑃𝑇𝑛, 𝑣< 𝑂𝑃𝑇(𝑛−1, 𝑣) for some node
𝑣, then (any) shortest 𝑣→𝑡path of length ≤𝑛contains
a cycle 𝑊. Moreover 𝑊is a negative cycle.

25

<!-- page: 26 -->

Detecting Negative Cycles

Lemma 2. If 𝑂𝑃𝑇𝑛, 𝑣< 𝑂𝑃𝑇(𝑛−1, 𝑣) for some node
𝑣, then (any) shortest 𝑣→𝑡path of length ≤𝑛contains
a cycle 𝑊. Moreover 𝑊is a negative cycle.

Pf. [by contradiction]
•
Since 𝑂𝑃𝑇𝑛, 𝑣< 𝑂𝑃𝑇(𝑛−1, 𝑣), we know that
shortest 𝑣→𝑡path 𝑃has exactly 𝑛edges.
•
The path 𝑃must contain a repeated note 𝑥.
•
Let 𝑊be any cycle in 𝑃.
•
Deleting 𝑊yields a 𝑣→𝑡path with < 𝑛edges ⟹𝑊
is a negative cycle.

26

<!-- page: 27 -->

String Similarity

Q. How similar are two strings?

Ex. ocurrance & occurrence.

27

![image](assets/assets/algorithm-design-and-analysis-022/image-013.png)

<!-- page: 28 -->

Edit Distance

Edit distance.
•
Gap penalty 𝛿; mismatch penalty 𝛼𝑝𝑔.
•
Cost = sum of gap and mismatch penalties.

Applications. Speech recognition, computational
biology,…
28

<!-- page: 29 -->

Sequence Alignment

Goal. Given two strings 𝑥1𝑥2 … 𝑥𝑚and 𝑦1𝑦2 … 𝑦𝑛find a min-cost
alignment.

Def. An alignment 𝑀is a set of ordered pairs 𝑥𝑖−𝑦𝑗such that
each item occurs in at most one pair and no crossings (𝑥𝑖−𝑦𝑗and
𝑥ℎ−𝑦𝑘cross if 𝑖< ℎ, but 𝑗> 𝑘).

29

![image](assets/assets/algorithm-design-and-analysis-022/image-014.png)

<!-- page: 30 -->

Sequence Alignment

Goal. Given two strings 𝑥1𝑥2 … 𝑥𝑚and 𝑦1𝑦2 … 𝑦𝑛find a min-cost
alignment.

Def. An alignment 𝑀is a set of ordered pairs 𝑥𝑖−𝑦𝑗such that
each item occurs in at most one pair and no crossings (𝑥𝑖−𝑦𝑗and
𝑥ℎ−𝑦𝑘cross if 𝑖< ℎ, but 𝑗> 𝑘).

Def. The cost of an alignment 𝑀is:

𝑐𝑜𝑠𝑡𝑀=
෍

𝛼𝑥𝑖𝑦𝑗+
෍

𝛿+
෍

𝛿

(𝑥𝑖,𝑦𝑗)∈𝑀

𝑖:𝑥𝑖𝑢𝑛𝑚𝑎𝑡𝑐ℎ𝑒𝑑

𝑗:𝑦𝑗𝑢𝑛𝑚𝑎𝑡𝑐ℎ𝑒𝑑

mismatch                                    gap

30

<!-- page: 31 -->

Sequence Alignment: Problem Structure

Def. 𝑂𝑃𝑇𝑖, 𝑗= min cost of aligning prefix strings 𝑥1𝑥2 … 𝑥𝑖and
𝑦1𝑦2 … 𝑦𝑗.
Goal. 𝑂𝑃𝑇𝑚, 𝑛.

Case 1. 𝑂𝑃𝑇𝑖, 𝑗includes 𝑥𝑖−𝑦𝑗.
Pay mismatch for 𝑥𝑖−𝑦𝑗+ min cost of aligning  𝑥1𝑥2 … 𝑥𝑖−1 and
𝑦1𝑦2 … 𝑦𝑗−1.

Case 2a. 𝑂𝑃𝑇𝑖, 𝑗leaves 𝑥𝑖unmatched.
Pay gap for 𝑥𝑖+ min cost of aligning 𝑥1𝑥2 … 𝑥𝑖−1 and 𝑦1𝑦2 … 𝑦𝑗.

31

<!-- page: 32 -->

Sequence Alignment: Problem Structure

Def. 𝑂𝑃𝑇𝑖, 𝑗= min cost of aligning prefix strings 𝑥1𝑥2 … 𝑥𝑖and
𝑦1𝑦2 … 𝑦𝑗.
Goal. 𝑂𝑃𝑇𝑚, 𝑛.

Case 2b. 𝑂𝑃𝑇𝑖, 𝑗leaves 𝑦𝑗unmatched.
Pay gap for 𝑦𝑗+ min cost of aligning 𝑥1𝑥2 … 𝑥𝑖and 𝑦1𝑦2 … 𝑦𝑗−1.

𝑗𝛿
𝑖𝑓𝑖= 0

𝛼𝑥𝑖𝑦𝑗+ 𝑂𝑃𝑇𝑖−1, 𝑗−1

𝑂𝑃𝑇𝑖, 𝑗=

𝑚𝑖𝑛൞

𝛿+ 𝑂𝑃𝑇𝑖−1, 𝑗
𝑜𝑡ℎ𝑒𝑟𝑤𝑖𝑠𝑒
𝛿+ 𝑂𝑃𝑇𝑖, 𝑗−1
𝑖𝛿
𝑖𝑓𝑗= 0

32

<!-- page: 33 -->

Sequence Alignment: Bottom-Up
Algorithm
Sequence-Alignment (𝑚, 𝑛, 𝑥1, … , 𝑥𝑚, 𝑦1, … , 𝑦𝑛, 𝛿, 𝛼)
---------------------------------------------------------------------
For 𝑖= 0 To 𝑚

𝑀[𝑖, 0] ←𝑖𝛿.
For 𝑗= 0 To 𝑛

𝑀0, 𝑗←𝑗𝛿.

For 𝑖= 1 To 𝑚

For 𝑗= 1 To 𝑛

𝑀𝑖, 𝑗←min{𝛼𝑥𝑖, 𝑦𝑗+ 𝑀𝑖−1, 𝑗−1 ,
                               𝛿+ 𝑀𝑖−1, 𝑗, 𝛿+ 𝑀𝑖, 𝑗−1 }.
Return 𝑀[𝑚, 𝑛].

33

<!-- page: 34 -->

Sequence Alignment: An Example

Ex. Align the words mean and name. Assume that 𝛿= 2;
matching a vowel with a different vowel, or a consonant
with a different consonant, costs 1; while matching a
vowel, or a consonant with each other costs 3.

Sequence-Alignment (𝑚, 𝑛, 𝑥1, … , 𝑥𝑚, 𝑦1, … , 𝑦𝑛, 𝛿, 𝛼)
---------------------------------------------------------------------
For 𝑖= 0 To 𝑚

n

𝑀[𝑖, 0] ←𝑖𝛿.
For 𝑗= 0 To 𝑛

a

𝑀0, 𝑗←𝑗𝛿.
For 𝑖= 1 To 𝑚

e

m

For 𝑗= 1 To 𝑛

-

𝑀𝑖, 𝑗←min{𝛼𝑥𝑖, 𝑦𝑗+ 𝑀𝑖−1, 𝑗−1 ,
                               𝛿+ 𝑀𝑖−1, 𝑗, 𝛿+ 𝑀𝑖, 𝑗−1 }.
Return 𝑀[𝑚, 𝑛].

-
n
a
m
e

34

<!-- page: 35 -->

Sequence Alignment: An Example

Ex. Align the words mean and name. Assume that 𝛿= 2;
matching a vowel with a different vowel, or a consonant
with a different consonant, costs 1; while matching a
vowel, or a consonant with each other costs 3.

𝑀𝑖, 𝑗←min{𝛼𝑥𝑖, 𝑦𝑗+ 𝑀𝑖−1, 𝑗−1 ,
                      𝛿+ 𝑀𝑖−1, 𝑗, 𝛿+ 𝑀𝑖, 𝑗−1 }

By following arrows
backward from node (4,4),
we can trace back to
construct the alignment.

35

![image](assets/assets/algorithm-design-and-analysis-022/image-015.png)

<!-- page: 36 -->

Dynamic Programming Summary

Outline.
• Define a collection of subproblems (typically, only a polynomial
number of subproblems).
• Solution to original problem can be computed from
subproblems.
• Natural ordering of subproblems from “smallest” to “largest”
that enables determining a solution to a subproblem from
solutions to smaller subproblems.

Techniques.
• Binary choice: weighted interval scheduling.
• Multiway choice: segmented least squares.
• Adding a new variable: knapsack problem.
• Intervals: RNA secondary structure.

36
