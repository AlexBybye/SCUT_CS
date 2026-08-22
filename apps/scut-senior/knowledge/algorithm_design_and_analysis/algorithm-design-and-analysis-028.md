---
source_id: algorithm-design-and-analysis-028
course_id: algorithm_design_and_analysis
title: "Algorthm 2023-2024 A"
original_file: "学科资料/算法设计与分析/PPT-英文版/Algorthm 2023-2024  A.pdf"
document_role: note
year: 2023
locator_type: page
---

# Algorthm 2023-2024 A

<!-- page: 1 -->

South China University of Technology
Academic year 2023/2024
2nd Year Undergraduate

Design and Analysis of Algorithms

1st Assessment 1st Exam
Calculations

Surname: ......................................................................................... Name: ............................................

Group: ............................. Date: ..............................................

Question
1
2
3
4
5
6
7
Total

Points
15
10
10
15
15
20
15
100

Grade

Answer the questions in the spaces provided. If you run out of room for an answer, continue on
the back of the page.

1. (15 points) Directly determine if 𝑓(𝑛) = 𝑂(𝑔(𝑛)), or if 𝑓(𝑛) = Ω(𝑔(𝑛)), or if 𝑓(𝑛) = Θ(𝑔(𝑛)).

(a) 𝑓(𝑛) = 22𝑛, 𝑔(𝑛) = 2𝑛.

(b) 𝑓(𝑛) = 𝑛log 𝑐, 𝑔(𝑛) = 𝑐log 𝑛.

(c) 𝑓(𝑛) = 8 log(𝑛𝑛), 𝑔(𝑛) = 100 log(𝑛!).

(d) 𝑓(𝑛) = 𝑛, 𝑔(𝑛) = log2 𝑛.

(e) 𝑓(𝑛) = 𝑛log 𝑛+ 𝑛, 𝑔(𝑛) = log 𝑛+ 𝑛.

Solution:

a)We evaluate the limit:

(2𝑛)2

22𝑛

𝑓(𝑛)
𝑔(𝑛) = lim

𝑛→∞2𝑛= ∞

lim
𝑛→∞

2𝑛= lim
𝑛→∞

2𝑛
= lim

𝑛→∞

Since the limit is ∞, 𝑓(𝑛) grows asymptotically faster than 𝑔(𝑛). Therefore, 𝑓(𝑛) = Ω(𝑔(𝑛)).

𝑦=
𝑒𝑦ln 𝑥𝑦= 𝑒𝑦ln 𝑥.

b)We use the identity 𝑎𝑏 =𝑏log𝑘𝑎 for any base 𝑘. More simply, we can use the property 𝑥𝑦 =(𝑒ln𝑥)

𝑓(𝑛) = 𝑛log 𝑐= 𝑒ln(𝑛log 𝑐) = 𝑒log 𝑐⋅ln 𝑛

𝑔(𝑛) = 𝑐log 𝑛= 𝑒ln(𝑐log 𝑛) = 𝑒log 𝑛⋅ln 𝑐

Since ln 𝑛· ln 𝑐= ln 𝑐· ln 𝑛, we have 𝑓(𝑛) = 𝑔(𝑛). Therefore, 𝑓(𝑛) = Θ(𝑔(𝑛)).

c) First, simplify 𝑓(𝑛) using the logarithm property log(𝑎𝑏) = 𝑏log 𝑎:

𝑓(𝑛) = 8 log(𝑛𝑛) = 8𝑛log 𝑛

For 𝑔(𝑛), we use Stirling’s approximation for ln(𝑛!) which states ln(𝑛!) ≈𝑛ln 𝑛−𝑛. Assuming log
is ln (natural logarithm) or any other base, the dominant term is 𝑛log 𝑛.

Model A

𝑔(𝑛) = 100 log(𝑛!) ≈100(𝑛log 𝑛−𝑛) = 100𝑛log 𝑛−100𝑛

Now, we evaluate the limit:

1 of 8

![image](assets/algorithm-design-and-analysis-028/image-001.png)

<!-- page: 2 -->

South China University of Technology
Academic year 2023/2024
2nd Year Undergraduate

Design and Analysis of Algorithms

1st Assessment 1st Exam
Calculations

𝑓(𝑛)
𝑔(𝑛) = lim

8𝑛log 𝑛
100𝑛log 𝑛−100𝑛= lim
𝑛→∞

8𝑛log 𝑛
100𝑛(log 𝑛−1)

lim
𝑛→∞

𝑛→∞

8 log 𝑛
100(log 𝑛−1) = lim
𝑛→∞

8

=
8
100(1 −0) =
8
100 = 2
25

= lim

100(1 −
1
log 𝑛)

𝑛→∞

Since the limit is a positive finite constant 2

25, 𝑓(𝑛) and 𝑔(𝑛) have the same asymptotic growth rate.

Therefore, 𝑓(𝑛) = Θ(𝑔(𝑛)).

d)We evaluate the limit:

𝑓(𝑛)
𝑔(𝑛) = lim

𝑛
log2 𝑛

lim
𝑛→∞

𝑛→∞

This is an indeterminate form ∞

∞, so we can apply L’Hôpital’s rule. We assume log 𝑛 is ln 𝑛.

Applying L’Hôpital’s rule once:

𝑑
𝑑𝑛(𝑛)

1
2 ln 𝑛⋅1
𝑛

𝑛
2 ln 𝑛

lim
𝑛→∞

𝑑
𝑑𝑛(ln2 𝑛) = lim

= lim

𝑛→∞

𝑛→∞

This is still an indeterminate form ∞

∞, so we apply L’Hôpital’s rule again:

𝑑
𝑑𝑛(𝑛)

1
2 ⋅1
𝑛

𝑛

lim
𝑛→∞

𝑑
𝑑𝑛(2 ln 𝑛) = lim

= lim

2 = ∞

𝑛→∞

𝑛→∞

Since the limit is ∞, 𝑓(𝑛) grows asymptotically faster than 𝑔(𝑛).

Therefore, 𝑓(𝑛) = Ω(𝑔(𝑛)).

e)We evaluate the limit:

𝑓(𝑛)
𝑔(𝑛) = lim

𝑛log 𝑛+ 𝑛

lim
𝑛→∞

log 𝑛+ 𝑛

𝑛→∞

Divide both numerator and denominator by 𝑛:

𝑛
𝑛
log 𝑛

log 𝑛+1

𝑛log 𝑛

𝑛
+ 𝑛

log 𝑛

= lim

𝑛
+

𝑛= lim

𝑛
+ 1

𝑛→∞

𝑛→∞

log 𝑛

We know that lim𝑛→∞

𝑛
= 0.

= ∞+ 1

0 + 1 = ∞
1 = ∞

Model A

Since the limit is ∞, 𝑓(𝑛) grows asymptotically faster than 𝑔(𝑛).

Therefore, 𝑓(𝑛) = Ω(𝑔(𝑛)).

2. (10 points) Solve the recurrence relation: for 𝑛≥2, 𝑓(𝑛) = 5𝑓(𝑛−1) −6𝑓(𝑛−2); 𝑓(0) = 1;
𝑓(1) = 0.

2 of 8

![image](assets/algorithm-design-and-analysis-028/image-002.png)

<!-- page: 3 -->

South China University of Technology
Academic year 2023/2024
2nd Year Undergraduate

Design and Analysis of Algorithms

1st Assessment 1st Exam
Calculations

Solution:

For the recurrence relation 𝑓(𝑛) = 5𝑓(𝑛−1) −6𝑓(𝑛−2), the characteristic equation is:

𝑥2 −5𝑥+ 6 = 0

Factoring: (𝑥−2)(𝑥−3) = 0, so 𝑥1 = 2 and 𝑥2 = 3.

The general solution is: 𝑓(𝑛) = 𝑐1 ⋅2𝑛+ 𝑐2 ⋅3𝑛

Using initial conditions 𝑓(0) = 1 and 𝑓(1) = 0:

{𝑐1 + 𝑐2 = 1

2𝑐1 + 3𝑐2 = 0

Solving: 𝑐2 = −2 and 𝑐1 = 3.

Therefore: 𝑓(𝑛) = 3 ⋅2𝑛−2 ⋅3𝑛

3. (10 points) Using Prim’s algorithm, find the minimum spanning tree of the graph below.

6

4

1

3

5

3
7
2
9
7
3

1

6

2

2

4

6

Solution:

Prim’s Algorithm Steps

Step 1: Start with node 1. Available edges: 1-2(1), 1-3(6), 1-4(7). Choose 1-2 with weight 1.

6

4

1

3

5

3
7
2
9
7
3

1

6

2

2

4

6

Step 2: MST = {1,2}. Available edges: 1-3(6), 1-4(2), 2-4(2), 2-3(7). Choose 2-4 with weight 2.

Model A

3 of 8

![image](assets/algorithm-design-and-analysis-028/image-003.png)

<!-- page: 4 -->

South China University of Technology
Academic year 2023/2024
2nd Year Undergraduate

Design and Analysis of Algorithms

1st Assessment 1st Exam
Calculations

6

4

1

3

5

3
7
2
9
7
3

1

6

2

2

4

6

Step 3: MST = {1,2,4}. Available edges: 1-3(6), 2-3(7), 4-6(6), 4-5(3). Choose 1-3 with weight 6.

6

4

1

3

5

3
7
2
9
7
3

1

6

2

2

4

6

Step 4: MST = {1,2,3,4}. Available edges: 3-5(4), 3-6(3), 4-6(6), 4-5(7). Choose 3-6 with weight 3.

6

4

1

3

5

3
7
2
9
7
3

1

6

2

2

4

6

Step 5: MST = {1,2,3,4,6}. Available edges: 3-5(4), 4-5(7), 5-6(3). Choose 5-6 with weight 3.

6

4

1

3

5

3
7
2
9
7
3

1

6

2

2

4

6

Model A

Step 6: All nodes included. MST complete.

Final MST:

4 of 8

![image](assets/algorithm-design-and-analysis-028/image-004.png)

<!-- page: 5 -->

South China University of Technology
Academic year 2023/2024
2nd Year Undergraduate

Design and Analysis of Algorithms

1st Assessment 1st Exam
Calculations

6

1

3

5

3
3

1

2

2

4

6

4. (15 points) Using Dijkstra’s algorithm, solve the single-source shortest path problem for the graph
below, with the source node set to 1.

12

2

4

9

2

5
3

1

4

6

15

4

13

3

5

Solution:

Dijkstra’s Algorithm Steps

Step
1
2
3
4
5
6

1
0
∞
∞
∞
∞
∞

2
9
4
∞
∞
∞

3
8
∞
17
∞

4
20
13
∞

5
16
28

6
18

Final Shortest Distances

Model A

5 of 8

![image](assets/algorithm-design-and-analysis-028/image-005.png)

<!-- page: 6 -->

South China University of Technology
Academic year 2023/2024
2nd Year Undergraduate

Design and Analysis of Algorithms

1st Assessment 1st Exam
Calculations

2

4

2

4
5
3

1

6

4

3

5

5. (15 points) Use dynamic programming to solve the 0 −1 knapsack problem. Given that the knapsack
capacity is 22, and the volumes of 5 items are 3, 5, 7, 8, 9 respectively, with corresponding values of
4, 6, 7, 9, 10. Find the maximum value of the knapsack and the selected items.

Solution:

It.
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22

0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0

1
0
0
0
4
4
4
4
4
4
4
4
4
4
4
4
4
4
4
4
4
4
4
4

2
0
0
0
4
4
6
6
6
10
10
10
10
10
10
10
10
10
10
10
10
10
10
10

3
0
0
0
4
4
6
6
7
10
10
11
11
13
13
13
17
17
17
17
17
17
17
17

4
0
0
0
4
4
6
6
7
10
10
11
13
13
15
15
17
19
19
20
20
22
22
22

5
0
0
0
4
4
6
6
7
10
10
11
13
14
15
16
17
19
20
20
21
23
23
25

Therefore, the maximum value of items we can select is 25, and the items chosen are 2, 4, and 5.

6.  Find the matrix chain multiplication for the following 5 matrices: 𝑀1(4 × 5); 𝑀2(5 × 4); 𝑀3(4 ×
6); 𝑀4(6 × 4); 𝑀5(4 × 5).

(a) (10 points) Using either a textual description or pseudocode, outline the dynamic programming
algorithm for the problem.

Solution:

Matrix-Chain(p, n):
  for i ← 1 to n do m[i][i] ← 0;
  for l ← 2 to n do // l is length of sub-chain
      for i ← 1 to n - l + 1 do
          j ← i + l - 1;
          m[i][j] ← ∞;
          for k ← i to j - 1 do
              q ← m[i][k] + m[k+1][j] + p[i-1] * p[k] * p[j];
              if q < m[i][j] then
                  m[i][j] ← q;
                  s[i][j] ← k;
  return m and s;

Model A

6 of 8

![image](assets/algorithm-design-and-analysis-028/image-006.png)

<!-- page: 7 -->

South China University of Technology
Academic year 2023/2024
2nd Year Undergraduate

Design and Analysis of Algorithms

1st Assessment 1st Exam
Calculations

(b) (10 points) Describe how this algorithm is used to solve the problem, and present the final results.

Solution:

Table of multiplication costs:

1
2
3
4
5

1
0
80
176
240
320

2
0
120
176
276

3
0
96
176

4
0
120

5
0

Table of optimal splits:

1
2
3
4
5

1
1
2
2
4

2
2
2
2

3
3
4

4
4

5

Therefore, the optimal parenthesization for this matrix chain is ((𝑀1𝑀2)(𝑀3𝑀4))𝑀5, and the
minimum number of multiplications required is 320.

7. (15 points) Let 𝐴 be a sequence of 𝑛 numbers. An element 𝑥 in 𝐴 is called an “approximate median”
if the number of elements less than 𝑥 is at least 𝑛

3, and the number of elements greater than 𝑥 is also
at least 𝑛

3. Design an algorithm to find an approximate median of 𝐴. Explain the design idea of your
algorithm and its worst-case time complexity.

Solution:

An approximate median means the element 𝑥’s rank falls between 𝑛

3 and 2𝑛
3 . In simpler terms, 𝑥 is an
element located in the middle third of the sorted array.

Therefore, any element in the middle third of a sorted array will satisfy the approximate median
condition. We can use QuickSort to completely sort the array, then select any element from the valid
range.

Algorithm: QuickSort Approach

Model A

void QSort(Elem A[], int p, int q) {
  if (p >= q) return;
  Elem pivot = A[p];
  int m = partition(A, p, q, pivot);
  QSort(A, p, m - 1);
  QSort(A, m + 1, q);
}

7 of 8

![image](assets/algorithm-design-and-analysis-028/image-007.png)

<!-- page: 8 -->

South China University of Technology
Academic year 2023/2024
2nd Year Undergraduate

Design and Analysis of Algorithms

1st Assessment 1st Exam
Calculations

int partition(Elem A[], int p, int q, Elem x) {
  int i = p;
  for (int j = p + 1; j <= q; ++j) {
      if (A[j] <= x) {
          ++i;
          swap(A[i], A[j]);
      }
  }
  swap(A[p], A[i]);
  return i;
}

Then, just return any element from the range 𝐴[𝑛

3] to 𝐴[2𝑛
3 ].

The worst-case time complexity of this algorithm is 𝑂(𝑛log 𝑛).

Model A

8 of 8

![image](assets/algorithm-design-and-analysis-028/image-008.png)
