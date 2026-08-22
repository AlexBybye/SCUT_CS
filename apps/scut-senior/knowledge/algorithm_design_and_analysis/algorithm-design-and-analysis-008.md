---
source_id: algorithm-design-and-analysis-008
course_id: algorithm_design_and_analysis
title: 11_backtrack
original_file: "学科资料/算法设计与分析/PPT-英文版/11_backtrack.pdf"
document_role: note
year: 
locator_type: page
---

# 11_backtrack

<!-- page: 1 -->

Design and Analysis of Algorithms

Backtrack

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

1

<!-- page: 2 -->

Outline

• Classical examples
• Principles of Backtrack
• Loading problem
• Graph coloring problem
• Estimation of leaves

<!-- page: 3 -->

Backtrack Paradigm

• Recursive approach is essentially travelling the whole tree
defined by the recursive relation.

The subtrees may repeat, so we need to cache intermediate
results to improve efficiency. This is exactly the essence of
dynamic programming.
• For some problems, the subtrees will not overlap.
In such case, there is no better algorithm other than traveling
the entire tree. But, we can travel the entire tree smartly.
This is what backtrack technique concerns: stop visiting the
subtree if the solution won’t appear and backtrack to the parent
node.
- Basic backtrack strategy: Domino property defined by
problem constraint.
- Advanced backtrack strategy: Branch-and-bound.

<!-- page: 4 -->

Example: 8-Queen Problems

• 8-queen puzzle. Placing eight chess queens on an 8 × 8
chessboard so that no two queens threaten each other.

A solution requires that no two queens share the same row,
column, or diagonal.

8-queen puzzle is a special case of
the more general 𝑛-queen problem:
placing 𝑛 non-attacking queens on
an 𝑛× 𝑛 chessboard.

![image](assets/assets/algorithm-design-and-analysis-008/image-001.png)

<!-- page: 5 -->

Counting Solutions

• Solution is an 𝑛-dimension vector over [𝑛]: exist for all natural
numbers 𝑛 with the exception of 𝑛 =2,3.

8-queen puzzle has 92 distinct solutions, the entire solution
space is 𝐶64

8 = 4,426,165,368.
If solutions that differ only by the symmetry operations of
rotation and reflection of the board are counted as one, the
puzzle has 12 solutions, called as fundamental solutions.

![image](assets/assets/algorithm-design-and-analysis-008/image-002.png)

<!-- page: 6 -->

Background of 8-Queen Puzzle

• Origin of 8-Queen Puzzle
Max Bezzel first proposed this problem in 1848, Frank Nauck
gave the first solution in 1850 and extended it to 𝑛-queen
puzzles. Many mathematicians including Carl Gauss also
studied this problem.
Edsger Dijkstra exemplified the power of depth-first
backtracking algorithm via this problem.
There is no known formula for the exact number of solutions,
or even for its asymptotic behavior. The 27 × 27 board is the
highest-order board that has been completely enumerated.

How to solve?

Modeling all possible solutions as leaf nodes of a tree traversal
the solution space via travelling the tree.

<!-- page: 7 -->

Demo of Quadtree for 4-Queen Puzzle

• Travel the tree via depth-first order to find all solutions.
𝑖-th level node represent 𝑖-th element in solution vector in
the 𝑖-th level, the branching choice is less than 𝑛−𝑖 leaves
correspond to solutions.

![image](assets/assets/algorithm-design-and-analysis-008/image-003.png)

<!-- page: 8 -->

Example: 0-1 Knapsack Problem

• Problem. Given 𝑛 items with value 𝑣𝑖and weight 𝑤𝑖, as well as
a knapsack with weight capacity 𝑊. The number of each item is
1. Find a solution that maximizes the overall value.

• Solution. n dimension vector (𝑥1, 𝑥2, … , 𝑥𝑛) ∈{0,1}𝑛, 𝑥𝑖=
1 ⟺selecting item 𝑖.
• Nodes: (𝑥1, 𝑥2, … , 𝑥𝑘) corresponds to partial solution.
• Search space. In all levels, the branching choice is always 2
(perfect binary tree with 2𝑛leaves).
• Candidate solution. Satisfy constraint σ𝑖=1
𝑛
𝑤𝑖𝑥𝑖≤𝑊.
• Optimal solution. The candidate solutions that achieve maximal
values.

<!-- page: 9 -->

Demo

• Ex.

Solution. n dimension vector (𝑥1, 𝑥2, … , 𝑥𝑛) ∈
{0,1}𝑛, 𝑥𝑖= 1 ⟺selecting item 𝑖.
Nodes: (𝑥1, 𝑥2, … , 𝑥𝑘) corresponds to partial
solution.
Search space. In all levels, the branching choice is
always 2 (perfect binary tree with 2𝑛leaves).

![image](assets/assets/algorithm-design-and-analysis-008/image-004.png)

<!-- page: 10 -->

Demo

• Ex.

![image](assets/assets/algorithm-design-and-analysis-008/image-005.png)

![image](assets/assets/algorithm-design-and-analysis-008/image-006.png)

![image](assets/assets/algorithm-design-and-analysis-008/image-007.png)

<!-- page: 11 -->

Example: Traversal Salesman Problem

• Problem. Given 𝑛 cities 𝐶= {𝑐1, 𝑐2, … , 𝑐𝑛} and 𝑑(𝑐𝑖, 𝑐𝑗) ∈𝑍+.
Find a cycle with minimal length that travels each city once.
• Solution. A permutation of (1,2, … , 𝑛) ⇒(𝑘1, 𝑘2, … , 𝑘𝑛) such
that

𝑛−1

min ෍

𝑑𝑐𝑘𝑖, 𝑐𝑘𝑖+1 + 𝑑𝑐𝑘𝑛, 𝑐𝑘1

𝑖=1

Ex.

![image](assets/assets/algorithm-design-and-analysis-008/image-008.png)

<!-- page: 12 -->

Search Space of TSP

• Any node can serve as the root, cause TSP is defined over an
undirected graph.

• Search space. In the 𝑖-th level, the branching choice is always
𝑛−𝑖⟹ obtain a tree with (𝑛−1)! leaves (number of all
possible permutations over {1,2, … , 𝑛} .
• Solution is (1,2,4,3), length of cycle is 5+2+7+9=23.

![image](assets/assets/algorithm-design-and-analysis-008/image-009.png)

<!-- page: 13 -->

Classical Examples of Backtrack

• Problem: 𝑛-Queen Puzzle, 0-1 Knapsack, TSP
• Solution: Vector
• Search space: Tree
Nodes correspond to partial solutions, leaves correspond to
candidate solutions.

• Search order: Depth-first, Breadth-first,…

<!-- page: 14 -->

Main Idea of Backtrack

• Scope of application. Search or optimization problem
• Search space. Tree
Leaves: candidate solution
Nodes: partial solution
• How to search. Systematically traversal the tree: DFS, BFS, …

![image](assets/assets/algorithm-design-and-analysis-008/image-010.png)

<!-- page: 15 -->

States of Nodes

• The tree is explored dynamically. Let 𝑣 be the candidate node
(corresponding to partial solution) and 𝑃 be the predicate that
checks if 𝑣 satisfies the constraint.

𝑃𝑣= 1 ⇒expand
𝑃𝑣= 0 ⇒backtrack to the parent node
• States of node

Black: finishing the traversal of this subtree
Gray: visiting its subtree
White: unexplored

![image](assets/assets/algorithm-design-and-analysis-008/image-011.png)

<!-- page: 16 -->

Basic Backtrack Technique:
Domino Property

• At note 𝑣= (𝑥1, … , 𝑥𝑘),
𝑃𝑥1, … , 𝑥𝑘= 1 ⇒𝑥1, … , 𝑥𝑘meet some property.

Example. 𝑛-queen puzzle, placing 𝑘 queens in positions without
attacking each other.
Domino property (admit safe backtrack)

𝑃𝑥1, … , 𝑥𝑘+1 = 1 ⇒𝑃𝑥1, … , 𝑥𝑘= 1, 0 < 𝑘< 𝑛
Converse-negative proposition

𝑃𝑥1, … , 𝑥𝑘= 0 ⇒𝑃𝑥1, … , 𝑥𝑘+1 = 0, 0 < 𝑘< 𝑛
𝑘-dimension vector does not satisfy constrain ⇒ its 𝑘+1-
dimension extension does not satisfy constraint either
This property guarantees that backtracking will not miss any
solution. Safely backtrack when 𝑃𝑥1, … , 𝑥𝑘= 0

<!-- page: 17 -->

Counterexample

• Find integer solutions for inequality
5𝑥1 + 4𝑥2 −𝑥3 ≤10
1 ≤𝑥𝑘≤3, 𝑘= 1,2,3

𝑘
𝑎𝑖𝑥𝑖≤10

𝑃𝑥1, … , 𝑥𝑘= 1 iff σ𝑖=1

Does not satisfy Domino property

5𝑥1 + 4𝑥2 −𝑥3 ≤10 ⇏5𝑥1 + 4𝑥2 ≤10

′ = 3 −𝑥3
5𝑥1 + 4𝑥2 + 𝑥3
′ ≤13
1 ≤𝑥1, 𝑥2 ≤3, 0 ≤𝑥3
′ ≤2

Modification to satisfy Domino property: set 𝑥3

<!-- page: 18 -->

Domino Property

• The premise condition to use backtrack: Domino Property.

• General steps of backtrack algorithm:
Define solution vector (include the range of every element),

𝑥1, … , 𝑥𝑛∈𝑋1 × ⋯× 𝑋𝑛
After fixing 𝑥1, … , 𝑥𝑘−1 , update admissible range of 𝑥𝑘as
𝐴𝑘⊆𝑋𝑘using predicate 𝑃.
Decide if Domino property is satisfied.
Decide the search strategy: DFS, BFS.

Decide the data structure to store the search path.

<!-- page: 19 -->

Backtrack Recursive Template

Algorithm 1: BackTrack(n)  // output all solutions
1: for 𝑘= 1 𝑡𝑜 𝑛do 𝐴𝑘←𝑋𝑘;  // initialize
2: ReBack(1);

Algorithm 2: ReBack(k)  // k is the current depth of recursion
1: if 𝑘= 𝑛then return solution 𝑥1, … , 𝑥𝑛;
2: else
3:
while 𝐴𝑘≠∅do
4:        𝑥𝑘←𝐴𝑘// according to some order;
5:        𝐴𝑘←𝐴𝑘−{𝑥𝑘};
6:        update 𝐴𝑘+1, ReBack(k+1)
7:     end
8: end
The above is the oversimplified pseudocode. One must be careful
when dealing with domains 𝐴𝑘and solution vector 𝑥when coding.

<!-- page: 20 -->

Backtrack Iterative Template

Algorithm 3: BackTrack(n)  // all solutions
1: for 𝑘= 1 𝑡𝑜 𝑛do 𝐴𝑘←𝑋𝑘;  // initialize

2: 𝑘←1;
3: while 𝐴𝑘≠∅do
4:
𝑥𝑘←𝐴𝑘; 𝐴𝑘←𝐴𝑘−{𝑥𝑘};

5:     if 𝑘< 𝑛then 𝑘←𝑘+ 1;
6:     else 𝑥1, … , 𝑥𝑛is solution;
7: end

8: if 𝑘> 1 then 𝑘←𝑘+ 1; goto 3;
𝐴𝑘is determined by 𝑥1, … , 𝑥𝑘−1 . The algorithm terminates
when all 𝐴𝑖are empty. Otherwise, it will backtrack (line 8).

<!-- page: 21 -->

Loading Problem

• Problem. Given 𝑛 containers with weight 𝑤𝑖, two boats with
weight capacity 𝑊1 and 𝑊2 s.t. 𝑤1 + ⋯+ 𝑤𝑛≤𝑊1 + 𝑊2.
• Goal. If there exists a scheme to load the 𝑛 containers on two
boats. Please give a scheme if it is solvable.
Ex.

𝑤1 = 90, 𝑤2 = 80, 𝑤3 = 40, 𝑤4 = 30, 𝑤5 = 20, 𝑤6 = 12,

𝑤7 = 10, 𝑊1 = 152, 𝑊2 = 130

<!-- page: 22 -->

Loading Problem

• Problem. Given 𝑛 containers with weight 𝑤𝑖, two boats with
weight capacity 𝑊1 and 𝑊2 s.t. 𝑤1 + ⋯+ 𝑤𝑛≤𝑊1 + 𝑊2.
• Goal. If there exists a scheme to load the 𝑛 containers on two
boats. Please give a scheme if it is solvable.
Ex.

𝑤1 = 90, 𝑤2 = 80, 𝑤3 = 40, 𝑤4 = 30, 𝑤5 = 20, 𝑤6 = 12,

𝑤7 = 10, 𝑊1 = 152, 𝑊2 = 130
Main idea: Let the total weights be 𝑊.

Load on boat 1 first. Using backtrack to find a solution that
maximizes 𝑊1

∗is the real capacity.
Then check if 𝑊−𝑊1

∗, where 𝑊1

∗≤𝑊2. Return “yes” if true and “no”
otherwise.
Solution: load 1, 3, 6, 7 on boat 1 and the rest on boat 2.

<!-- page: 23 -->

Pseudocode

Algorithm 4: Loading(𝑊1)
1: 𝑊1
∗←0; 𝐶←0; 𝑖←1;
2: while 𝑖≤𝑛do   // line 3-4: whether to load container 𝑖
3:     if 𝐶+ 𝑤𝑖≤𝑊1 then 𝐶←𝐶+ 𝑤𝑖, 𝑥[𝑖] ←1, 𝑖= 𝑖+ 1;
4:     else 𝑥[𝑖] ←0, 𝑖= 𝑖+ 1;
5: end
6: if 𝑊1
∗< 𝐶then record solution, 𝑊1

∗←𝐶;
7: while 𝑖> 1 and 𝑥𝑖= 0 do 𝑖−1;  // find a backtrack node
8: if 𝑖= 1 then return optimal solution;  // backtrack to root
9: else 𝑥[𝑖] ←0; 𝐶←𝐶−𝑤𝑖; 𝑖= 𝑖+ 1, goto 2;  // continue to
search
Line 7-9: find a backtrack point.
Line 8: have travelled all the tree and back to the root.
Line 9: find a left branch, means there still exist unexplored right branch

<!-- page: 24 -->

Demo

Ex.

𝑤1 = 90, 𝑤2 = 80, 𝑤3 = 40, 𝑤4 = 30, 𝑤5 = 20, 𝑤6 = 12,

𝑤7 = 10, 𝑊1 = 152, 𝑊2 = 130

![image](assets/assets/algorithm-design-and-analysis-008/image-012.png)

<!-- page: 25 -->

Demo

Ex.

𝑤1 = 90, 𝑤2 = 80, 𝑤3 = 40, 𝑤4 = 30, 𝑤5 = 20, 𝑤6 = 12,

𝑤7 = 10, 𝑊1 = 152, 𝑊2 = 130

![image](assets/assets/algorithm-design-and-analysis-008/image-013.png)

<!-- page: 26 -->

Graph Coloring Problem

• Problem. Undirected graph 𝐺 and 𝑚 colors. Coloring the
vertices to ensure the connected two vertices with different
color.

• Goal. Output all possible coloring schemes. Output “no” if there
is none.

![image](assets/assets/algorithm-design-and-analysis-008/image-014.png)

<!-- page: 27 -->

Algorithm Design

• Input. 𝐺= 𝑉, 𝐸, 𝑉= {1,2, … , 𝑛}, color set = {1,2, … , 𝑚}
• Solution vector. (𝑥1, 𝑥2, … , 𝑥𝑛), 𝑥𝑖∈[𝑚]

(𝑥1, 𝑥2, … , 𝑥𝑘) gives partial solution for vertex set {1,2, … , 𝑘}
Search tree. 𝑚-fork tree
Constraint. At node (𝑥1, 𝑥2, … , 𝑥𝑘), the set of available colors for
node 𝑘+ 1 is not empty.

If the nodes in adjacent list have used up 𝑚colors, then node
𝑘+ 1 is not colorable. In this case, back to parent node.
Search strategy: DFS

<!-- page: 28 -->

Demo

![image](assets/assets/algorithm-design-and-analysis-008/image-015.png)

<!-- page: 29 -->

Reduce Search Scope

• Symmetry (only need to search at most 1/6 solution space).
The permutation over (1,2,3) is 6. For any specific solution,
there exist 6 homogeneous solution.
Level-2 has 2-fold solution (e.g. color blue and green are
exchangeable), level-1 has 3-fold solution (node 1 can pick red,
green or blue); the closer to the root, the more choice of
replacement.
• Additional reasoning also helps to reduce search scope.
Example: if node 1,2,3 have been colored differently, then
node 7 is definitely non-colorable because it connects with
node 1,2,3 (backtrack from this node)
Need trade-off between search and decide.

<!-- page: 30 -->

Applications of Graph Coloring

• Arrangement of meeting room
There are 𝑛 events to be arranged, if the slots of event 𝑖 and
event 𝑗 overlap, we say 𝑖 and 𝑗 are not compatible. How to
arrange these events with smallest number of meeting rooms?
• Modeling
Treat event as node, if 𝑖, 𝑗 are not compatible, then add an
edge between 𝑖 and 𝑗.
Treat meeting rooms as colors.
The arrangement problem is transformed into finding a coloring
scheme with smallest colors.

<!-- page: 31 -->

Estimation of Leaves

Sometimes, we need to know the size of problems (captured by
the number of nodes)

Finding the exact number may require to travel the whole tree
exhaustively, which is equivalent to solve the problem.
Monte Carlo method

Step 1: Choose a random path from root until there is no more
branching, i.e., randomly and sequentially assign values to
𝑥1, 𝑥2, … , until the vector cannot be further expanded.
Step 2: Assume other 𝐴𝑖−1 branches has the same path as
selected one, calculate the nodes of search tree.
Repeat Steps 1-2, and compute the average number of nodes.

<!-- page: 32 -->

Estimate 𝑛-Queen Puzzle

Algorithm 5: MonteCarlo(𝑛, 𝑡)
Input: 𝑛= # number of queens, 𝑡= # number of sampling

Output: 𝑙average number of nodes for 𝑡times sampling
1: 𝑙←0;
2: for 𝑖= 0 𝑡𝑜 𝑡do   // sampling time is 𝑡

3:     𝑚←Estimate 𝑛;   // number of nodes
4:     𝑙←𝑙+ 𝑚;
5: end

6: 𝑙←𝑙/𝑡;

<!-- page: 33 -->

One Sampling

• Parameter
𝑙is the total number of nodes

𝑘is the current depth

𝑟𝑝𝑟𝑒𝑣: # nodes on the previous level

𝑟𝑐𝑢𝑟𝑟𝑒𝑛𝑡: # nodes on the current level

𝑟𝑐𝑢𝑟𝑟𝑒𝑛𝑡= 𝑟𝑝𝑟𝑒𝑣× # branches

𝑛is the depth of tree
• Computation order: randomly select until reaching the leaves

<!-- page: 34 -->

Pseudocode

Algorithm 6: Estimate(𝑛)

1: 𝑙←1; 𝑟𝑝𝑟𝑒𝑣←1; 𝑘←1;   // the root node

2: while 𝑘≤𝑛do
3:     if 𝐴𝑘= ∅then return 𝑙;   // no more branch
4:     𝑥𝑘←𝐴𝑘// randomly select a branch

5:     𝑟𝑐𝑢𝑟𝑟𝑒𝑛𝑡←𝑟𝑝𝑟𝑒𝑣× 𝐴𝑘
// number of nodes on 𝑘level

6:     𝑙←𝑙+ 𝑟𝑐𝑢𝑟𝑟𝑒𝑛𝑡;
8:     𝑘←𝑘+ 1;
9: end

<!-- page: 35 -->

Real Case: 4-Queen Puzzle

![image](assets/assets/algorithm-design-and-analysis-008/image-016.png)

<!-- page: 36 -->

Random Selected Path 1

![image](assets/assets/algorithm-design-and-analysis-008/image-017.png)

<!-- page: 37 -->

Random Selected Path 2

![image](assets/assets/algorithm-design-and-analysis-008/image-018.png)

<!-- page: 38 -->

Random Selected Path 3

![image](assets/assets/algorithm-design-and-analysis-008/image-019.png)

<!-- page: 39 -->

Estimate Result

Suppose sampling four times:

Case 1: 1
Case 2: 1
Case 3: 2

21+17+13+13
4
= 16

Average number of nodes:

The real number of nodes: 17

More samplings will make the estimation approaches the real
number
