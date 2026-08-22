---
source_id: algorithm-design-and-analysis-019
course_id: algorithm_design_and_analysis
title: 6-linear
original_file: "学科资料/算法设计与分析/PPT-英文版/6-linear.pdf"
document_role: note
year: 
locator_type: page
---

# 6-linear

<!-- page: 1 -->

Design and Analysis of Algorithms

Linear Programming

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

1

<!-- page: 2 -->

Topics

• An Example
• Standard Form
• Geometry
• Linear Algebra
• Simplex Algorithm

2

<!-- page: 3 -->

Linear Programming

Linear programming. Optimize a linear function subject to linear
inequalities.

𝑛
𝑐𝑗𝑥𝑗
𝑠. 𝑡. σ𝑗=1

max σ𝑗=1

𝑛
𝑎𝑖𝑗𝑥𝑗≥𝑏𝑖
1 ≤𝑖≤𝑚
𝑥𝑗≥0
1 ≤𝑗≤𝑛

Ranked among most important scientific advances of 20th century.

3

<!-- page: 4 -->

Linear Programming

Linear programming. Optimize a linear function subject to linear
inequalities.

Generalizes: AX=B, 2-person zero-sum games, shortest path, max
flow, assignment problem, …

4

<!-- page: 5 -->

Brewery Problem

Small brewery produces ale and beer.
• Production limited by scarce resources: corn, hops, barley malt.
• Recipes for ale and beer require different proportions of
resources.

How can brewer maximize profit?
• Devote all resources to ale: 34 barrels of ale -> $442
• Devote all resources to beer: 32 barrels of beer -> $736
• 7.5 barrels of ale, 29.5 barrels of beer -> $ 776
• 12 barrels of ale, 28 barrels of beer -> $800

5

![image](assets/assets/algorithm-design-and-analysis-019/image-001.png)

<!-- page: 6 -->

Brewery Problem

6

![image](assets/assets/algorithm-design-and-analysis-019/image-002.png)

![image](assets/assets/algorithm-design-and-analysis-019/image-003.png)

<!-- page: 7 -->

Standard Form

“Standard form” of a linear program.
•
Input: real numbers 𝑎𝑖𝑗, 𝑐𝑗, 𝑏𝑖.
•
Output: real numbers 𝑥𝑗.
•
𝑛= # decision variables, 𝑚= # constraints.
•
Maximize linear objective function subject to linear equalities.

𝑛
𝑐𝑗𝑥𝑗
𝑠. 𝑡. σ𝑗=1

max σ𝑗=1

𝑛
𝑎𝑖𝑗𝑥𝑗= 𝑏𝑖
1 ≤𝑖≤𝑚
𝑥𝑗≥0
1 ≤𝑗≤𝑛

7

<!-- page: 8 -->

Brewery Problem: Converting to
Standard Form
Original input.

Standard form？
• Add slack variable for each inequality.
• Now a 5-dimensional problem.

8

![image](assets/assets/algorithm-design-and-analysis-019/image-004.png)

<!-- page: 9 -->

Basic and Non-basic Variables

Basic variables are selected arbitrarily with the restriction that
there will be as many basic variables as the equations. The
remaining variables are non-basic variables.

+
+
=

x
x
s

2
32

1
2
1

+
+
=

3
4
84

x
x
s

1
2
2

This system has two equations, we can select any two of the four
variables as basic variables. The remaining two variables are then
non-basic variables. A solution found by setting the two non-basic
variables equal to 0 and solving for the two basic variables is a
basic solution. If a basic solution has no negative values, it is a basic
feasible solution.

9

<!-- page: 10 -->

Equivalent Forms

Easy to convert variants to standard form.

max 𝑐𝑇𝑥
𝑠. 𝑡. 𝐴𝑥= 𝑏

𝑥≥0

• Less than to equality.
𝑥+ 2𝑦−3𝑧≤17
• Greater than to equality.
𝑥+ 2𝑦−3𝑧≥17
• Min to max.
min 𝑥+ 2𝑦−3𝑧
• Unrestricted to nonnegative.
𝑥 unrestricted

10

<!-- page: 11 -->

Equivalent Forms

Easy to convert variants to standard form.

max 𝑐𝑇𝑥
𝑠. 𝑡. 𝐴𝑥= 𝑏

𝑥≥0

• Less than to equality.
𝑥+ 2𝑦−3𝑧≤17 →𝑥+ 2𝑦−3𝑧+ 𝑠= 17, 𝑠≥0
• Greater than to equality.
𝑥+ 2𝑦−3𝑧≥17 →𝑥+ 2𝑦−3𝑧−𝑠= 17, 𝑠≥0
• Min to max.
min 𝑥+ 2𝑦−3𝑧→max −𝑥−2𝑦+ 3𝑧
• Unrestricted to nonnegative.
𝑥 unrestricted →𝑥= 𝑥+ −𝑥−, 𝑥+ ≥0, 𝑥−≥0

11

<!-- page: 12 -->

Brewery Problem: Feasible Region

12

![image](assets/assets/algorithm-design-and-analysis-019/image-005.png)

<!-- page: 13 -->

Brewery Problem: Geometry

Brewery problem observation. Regardless of objective function
coefficients, an optimal solution occurs at a vertex.

13

![image](assets/assets/algorithm-design-and-analysis-019/image-006.png)

<!-- page: 14 -->

Brewery Problem: Objective Function

14

![image](assets/assets/algorithm-design-and-analysis-019/image-007.png)

<!-- page: 15 -->

Convexity

Convex set. If two points 𝑥 and 𝑦 are in the set, then so is 𝜆𝑥+

1 −𝜆𝑦 for 0 ≤𝜆≤1.

Vertex. A point 𝑥 in the set that can’t be written as a strict convex
combination of two distinct points in the set.

Observation. LP feasible region is a convex set.

15

![image](assets/assets/algorithm-design-and-analysis-019/image-008.png)

<!-- page: 16 -->

Vertex

Intuition. A vertex in 𝑅𝑚is uniquely specified by 𝑚linearly
independent equations.

16

![image](assets/assets/algorithm-design-and-analysis-019/image-009.png)

<!-- page: 17 -->

Vertex

Theorem. If there exists an optimal solution to (P), then there
exists one that is a vertex.

max 𝑐𝑇𝑥
𝑠. 𝑡. 𝐴𝑥= 𝑏

𝑥≥0
Intuition. If the optimum is not a vertex, move in a non-
decreasing direction until you reach a boundary.

17

<!-- page: 18 -->

Vertex

Theorem. If there exists an optimal solution to (P), then there
exists one that is a vertex.

Pf.
Since there exists an optimal solution, there exists an optimal
solution 𝑥with a minimal number of non-zero components.

Suppose 𝑥is not a vertex, so that

𝑥= 𝜆𝑢+ 1 −𝜆𝑣，
for some 𝑢≠𝑣, 𝜆∈(0,1).

18

<!-- page: 19 -->

Vertex

Theorem. If there exists an optimal solution to (P), then there
exists one that is a vertex.

Since 𝑥is optimal, 𝑐𝑇𝑢≤𝑐𝑇𝑥and 𝑐𝑇𝑣≤𝑐𝑇𝑥.
But also 𝑐𝑇𝑥= 𝜆𝑐𝑇𝑢+ (1 −𝜆)𝑐𝑇𝑣so in fact 𝑐𝑇𝑢= 𝑐𝑇𝑣= 𝑐𝑇𝑥.
Now consider the line defined by

𝑥(𝜖) = 𝑥+ 𝜖𝑢−𝑣
Then
• 𝐴𝑥= 𝐴𝑢= 𝐴𝑣= 𝑏so 𝐴𝑥𝜖= 𝑏for all 𝜖,
• 𝑐𝑇𝑥𝜖= 𝑐𝑇𝑥for all 𝜖,
• If 𝑥𝑖= 0 then 𝑢𝑖= 𝑣𝑖= 0, which implies 𝑥𝜖𝑖= 0 for all 𝜖,
• If 𝑥𝑖> 0 then 𝑥0 𝑖> 0, and 𝑥𝜖𝑖is continuous in 𝜖.

19

<!-- page: 20 -->

Vertex

Theorem. If there exists an optimal solution to (P), then there
exists one that is a vertex.

So we can increase 𝜖from zero, in a positive or a negative
direction as appropriate, until at least one extra component of
𝑥(𝜖) becomes zero.

This gives an optimal solution 𝑥(𝜖) with fewer non-zero
components than 𝑥.

So 𝑥must be a vertex.

20

<!-- page: 21 -->

Basic Feasible Solution: Example

Basic feasible solutions.

21

![image](assets/assets/algorithm-design-and-analysis-019/image-010.png)

<!-- page: 22 -->

Simplex Algorithm: Intuition

Simplex algorithm. Move from BFS (Basic Feasible Solution) to
adjacent BFS, without decreasing objective function (replace one
basic variable with another).

Greedy property. BFS optimal iff no adjacent BFS is better.

22

![image](assets/assets/algorithm-design-and-analysis-019/image-011.png)

<!-- page: 23 -->

Simplex Algorithm: Initialization

23

![image](assets/assets/algorithm-design-and-analysis-019/image-012.png)

<!-- page: 24 -->

Simplex Algorithm: Pivot 1

24

![image](assets/assets/algorithm-design-and-analysis-019/image-013.png)

<!-- page: 25 -->

Simplex Algorithm: Pivot 1

Q. Why pivot on column 2 (or 1)?
A. Each unit increase in B increases objective value by $23.

Q. Why pivot on row 2.
A. Preserves feasibility by ensuring RHS (Right Hand Side) ≥0.
(min ratio rule: min{480/15, 160/4, 1190/20})

25

![image](assets/assets/algorithm-design-and-analysis-019/image-014.png)

<!-- page: 26 -->

Simplex Algorithm: Pivot 2

26

![image](assets/assets/algorithm-design-and-analysis-019/image-015.png)

<!-- page: 27 -->

Simplex Algorithm: Optimality

Q. When to stop pivoting?
A. When all coefficients in top row are non-positive.

Q. Why is the resulting solution optimal?
A. Any feasible solution satisfies systems of equations in tableau.
• In particular: 𝑍= 800 −𝑆𝐶−2𝑆𝐻, 𝑆𝐶≥0, 𝑆𝐻≥0.
• Thus, optimal objective value 𝑍∗≤800.
• Current BFS has value 800 -> optimal.

27

![image](assets/assets/algorithm-design-and-analysis-019/image-016.png)

<!-- page: 28 -->

Variant Tableau

The constraints are a linear system including 𝑚equations
and 𝑛variables. 𝑚of the variables can be evaluated in terms
of the other 𝑛−𝑚variables

𝑥1 = 𝑏1 −𝑎1,𝑚+1𝑥𝑚+1 −⋯−𝑎1,𝑛𝑥𝑛
𝑥2 = 𝑏2 −𝑎2,𝑚+1𝑥𝑚+1 −⋯−𝑎2,𝑛𝑥𝑛

……
𝑥𝑚= 𝑏𝑚−𝑎𝑚,𝑚+1𝑥𝑚+1 −⋯−𝑎𝑚,𝑛𝑥𝑛
Objective function 𝑧= σ𝑗=1

𝑛
𝑐𝑗𝑥𝑗
= σ𝑖=1

𝑚𝑐𝑖𝑎𝑖𝑗)𝑥𝑗.
Let 𝑧0 = σ𝑖=1

𝑚𝑐𝑖𝑏𝑖+ σ𝑗=𝑚+1

𝑛
(𝑐𝑗−σ𝑖=1

𝑚𝑐𝑖𝑏𝑖, 𝜎𝑗= 𝑐𝑗−σ𝑖=1

𝑚𝑐𝑖𝑎𝑖𝑗, and we have

𝑛

𝑧= 𝑧0 +
෍

𝜎𝑗𝑥𝑗

𝑗=𝑚+1

indicator
28

<!-- page: 29 -->

Variant Tableau

29

![image](assets/assets/algorithm-design-and-analysis-019/image-017.png)

<!-- page: 30 -->

Variant Tableau

To solve a linear programming problem, use the following steps:

1.
Convert each inequality in the set of constraints to an equation by adding
slack variables.
2.
Create the initial simplex tableau.
3.
Select the pivot column (The column with the “most positive value” element in
the last row).
4.
Select the pivot row (The row with the smallest non-negative result when the
last element in the row is divided by the corresponding in the pivot column).
5.
Use elementary row operations calculate new values for the pivot row so that
the pivot is 1.
6.
Use elementary row operations to make all numbers in the pivot column
equal to 0 except for the pivot.
7.
If all entries in the bottom row are non-positive, this the final tableau. If not,
go back to Step 3.

30

<!-- page: 31 -->

Variant Tableau: An Example

31

![image](assets/assets/algorithm-design-and-analysis-019/image-018.png)

<!-- page: 32 -->

Variant Tableau: An Example

Pivot column. The column of the tableau representing the variable
to be entered into the solution mix.

Pivot row. The row of the tableau representing the variable to be
replaced in the solution mix.

Basic variable. Variables in the solution mix.

Initial tableau
Pivot column

Min ratio

rule

Pivot row

32

![image](assets/assets/algorithm-design-and-analysis-019/image-019.png)

<!-- page: 33 -->

Variant Tableau: An Example

•
Since the entry 3 is the most positive entry in the last row of the
tableau, the second column in the tableau is the pivot column.
•
Divide each positive number of the pivot column into the
corresponding entry in the column of constants. The ratio 5/2 is less
then the ratio 4/1, so row 2 is the pivot row.
33

![image](assets/assets/algorithm-design-and-analysis-019/image-020.png)

<!-- page: 34 -->

Variant Tableau: An Example

•
Since the entry 1/2 is the most positive entry in the last row of the
tableau, the first column in the tableau is the pivot column.
•
Divide each positive number of the pivot column into the
corresponding entry in the column of constants. The ratio 3/2 is less
then the ratio 5/2, so row 1 is the pivot row.
34

![image](assets/assets/algorithm-design-and-analysis-019/image-021.png)

<!-- page: 35 -->

Variant Tableau: An Example

•
The last row of the tableau contains no positive numbers, so an
optimal solution has been reached.

35

![image](assets/assets/algorithm-design-and-analysis-019/image-022.png)

<!-- page: 36 -->

Matrix Form

36

![image](assets/assets/algorithm-design-and-analysis-019/image-023.png)

<!-- page: 37 -->

Matrix Form

Standard form:

max 𝑍= 𝐶𝑇𝑋

𝑠. 𝑡. 𝐴𝑋= 𝑏

𝑋≥0

Let 𝐴= [𝐴𝐵, 𝐴𝑁], 𝑋= 𝑋𝐵

𝑋𝑁, 𝐶= 𝐶𝐵

𝐶𝑁, we have

𝐴𝐵𝑋𝐵+ 𝐴𝑁𝑋𝑁= 𝑏
→𝑋𝐵= 𝐴𝐵

−1𝐴𝑁𝑋𝑁
For the basis 𝐵,

−1𝑏−𝐴𝐵

𝑇
𝑋𝐵
𝑋𝑁= 𝐶𝐵

𝑇𝑋𝑁
= 𝐶𝐵

𝑇, 𝐶𝑁

𝑇𝑋𝐵+ 𝐶𝑁

𝑍= 𝐶𝑇𝑋= 𝐶𝐵

𝑇𝑋𝑁
= 𝐶𝐵

𝑇(𝐴𝐵

−1𝑏−𝐴𝐵

−1𝐴𝑁𝑋𝑁) + 𝐶𝑁

𝑇𝐴𝐵

−1𝑏+ (𝐶𝑁

𝑇−𝐶𝐵

𝑇𝐴𝐵

−1𝐴𝑁)𝑋𝑁

37

<!-- page: 38 -->

Matrix Form: Variant Tableau

𝑻
𝑪𝑵

𝑻

𝑪𝑩

𝑻
𝑿𝑵

𝑻

𝑿𝑩

−𝟏𝑨𝑵
𝑨𝑩

−𝟏𝒃

𝑪𝑩𝑿𝑩
𝑰
𝑨𝑩

𝑻−𝑪𝑩

𝑻𝑨𝑩

−𝟏𝑨𝑵

Indicator
0
𝑪𝑵

38
