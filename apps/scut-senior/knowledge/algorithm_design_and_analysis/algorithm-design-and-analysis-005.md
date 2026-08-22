---
source_id: algorithm-design-and-analysis-005
course_id: algorithm_design_and_analysis
title: 1-sort
original_file: "学科资料/算法设计与分析/PPT-英文版/1-sort.pdf"
document_role: note
year: 
locator_type: page
---

# 1-sort

<!-- page: 1 -->

Design and Analysis ofAlgorithms

Sorting

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

1

<!-- page: 2 -->

2

![image](assets/algorithm-design-and-analysis-005/image-001.jpeg)

<!-- page: 3 -->

Overview

Goals:

Start using frameworks for describingand
analyzingalgorithms.
– See how to describe algorithms inpseudocode.
– Begin using asymptotic notation toexpress

running-time analysis.
– Learn the technique of “divide and conquer”in

the context of merge-sort.
– Examine two algorithms for sorting: insertion-sort

and merge-sort.

3

<!-- page: 4 -->

Insertion Sort

Sorting a hand of cards using insertion sort.

4

![image](assets/algorithm-design-and-analysis-005/image-002.jpeg)

<!-- page: 5 -->

5

![image](assets/algorithm-design-and-analysis-005/image-003.png)

<!-- page: 6 -->

6

![image](assets/algorithm-design-and-analysis-005/image-004.png)

![image](assets/algorithm-design-and-analysis-005/image-005.png)

<!-- page: 7 -->

7

![image](assets/algorithm-design-and-analysis-005/image-006.png)

<!-- page: 8 -->

8

![image](assets/algorithm-design-and-analysis-005/image-007.png)

<!-- page: 9 -->

9

![image](assets/algorithm-design-and-analysis-005/image-008.jpeg)

<!-- page: 10 -->

10

![image](assets/algorithm-design-and-analysis-005/image-009.jpeg)

<!-- page: 11 -->

11

![image](assets/algorithm-design-and-analysis-005/image-010.jpeg)

<!-- page: 12 -->

12

![image](assets/algorithm-design-and-analysis-005/image-011.jpeg)

<!-- page: 13 -->

13

![image](assets/algorithm-design-and-analysis-005/image-012.jpeg)

<!-- page: 14 -->

14

![image](assets/algorithm-design-and-analysis-005/image-013.jpeg)

<!-- page: 15 -->

15

![image](assets/algorithm-design-and-analysis-005/image-014.jpeg)

<!-- page: 16 -->

16

![image](assets/algorithm-design-and-analysis-005/image-015.jpeg)

<!-- page: 17 -->

Insertion Sort (anotherexample)

INSERTION-SORT (A, n) ⊳
A[1 . . n]
1
for j ← 2 to n
2
do key ← A[j ]
3
i ← j – 1
4
while i > 0 and A[i] > key
5
do A[i + 1] ← A[i]
6
i ← i – 1
7
A[i + 1] = key

Initial

j=2

j=3

1
2
3
4
5
6

1
2
3
4
5
6

1
2
3
4
5
6

-∞
8
5
7
9
6
4

-∞
8
5
7
9
6
4

-∞
5
8
7
9
6
4

j=4
j=5
j=6

1
2
3
4
5
6
1
2
3
4
5
6
1
2
3
4
5
6

-∞
5
7
8
9
6
4

-∞
5
6
7
8
9
4

-∞
5
7
8
9
6
4

17

![image](assets/algorithm-design-and-analysis-005/image-016.png)

<!-- page: 18 -->

Running time

•
The running time depends on the input: an already
sorted  sequence is easier to sort.

•
Parameterize the running time by the size of the
input, since short sequences are easier to sort
than long ones.

•
Generally, we seek upper bounds on the running
time,  because everybody likes a guarantee.

18

<!-- page: 19 -->

19

![image](assets/algorithm-design-and-analysis-005/image-017.png)

<!-- page: 20 -->

20

![image](assets/algorithm-design-and-analysis-005/image-018.png)

<!-- page: 21 -->

Analysis of INSERTION-SORT

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛- 1
2
do key ← A[j ]
3
i ← j – 1
4
while i > 0
and A[i] > key
5
6
7

do A[i + 1] ←A[i]

i ← i – 1
A[i + 1] = key

21

<!-- page: 22 -->

Analysis of INSERTION-SORT

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛- 1
2
do key ← A[j ]
c2
𝑛- 1
3
i ← j – 1
4
while i > 0
and A[i] > key
5
6
7

do A[i + 1] ←A[i]

i ← i – 1
A[i + 1] = key

22

<!-- page: 23 -->

Analysis of INSERTION-SORT

INSERTION-SORT (A, n)
⊳A[1 .
. n]
cost
times
1
for j ← 2 to n
c1
𝑛- 1
2
do key ← A[j ]
c2
𝑛- 1
3
i ← j–
1
c3
𝑛- 1
4
while i> 0 and A[i]
> key
5
6
7

do A[i + 1] ←A[i]

i ← i – 1
A[i + 1] = key

23

<!-- page: 24 -->

Analysis of INSERTION-SORT

INSERTION-SORT (A, n) ⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛- 1
2
do key ← A[j ]
c2
𝑛- 1
𝑛−1
c3

i ← j – 1

3
4
5
6
7

𝑛

while i > 0 and A[i] > key

c4
෍

𝑡𝑗

j=2

do A[i + 1] ←A[i]

i ← i – 1
A[i + 1] = key

24

<!-- page: 25 -->

Analysis of INSERTION-SORT

INSERTION-SORT (A, n) ⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛- 1
2
do key ← A[j ]
c2
𝑛- 1

i ← j – 1

𝑛-1
c3

3
4
5
6
7

𝑛

while i > 0 and A[i] > key

c4
c5

෍

𝑡𝑗

j=2

do A[i + 1] ←A[i]
i ← i – 1
A[i + 1] = key

𝑛

෍

(𝑡𝑗−1)

j=2

25

<!-- page: 26 -->

Analysis of INSERTION-SORT

INSERTION-SORT (A, n) ⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛- 1
2
do key ← A[j ]
c2
𝑛- 1

i ← j – 1

𝑛-1
c3
c4
c5
c6

3
4
5
6
7

𝑛

while i > 0 and A[i] > key

෍

𝑡𝑗

j=2

do A[i + 1] ←A[i]

𝑛

෍

(𝑡𝑗−1)

j=2

i ← i – 1
A[i + 1] = key

𝑛

෍

(𝑡𝑗−1)

j=2

26

<!-- page: 27 -->

Analysis of INSERTION-SORT

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛- 1
2
3
4

do key ← A[j ]

c2
c3
c4

𝑛- 1
𝑛- 1
σj=2

i ← j – 1

while i > 0 and A[i] > key

𝑛
𝑡𝑗

𝑛(𝑡𝑗−1)

5
do A[i + 1] ←A[i]
c5
σj=2

𝑛(𝑡𝑗−1)

6
i ← i – 1
c6
σj=2

7
A[i + 1] = key
c7
𝑛- 1

27

<!-- page: 28 -->

Analysis of INSERTION-SORT

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛- 1
2
3
4

do key ← A[j ]

c2
c3

𝑛-1
n-1

i ← j – 1

𝑛

while i > 0 and A[i] > key

c4

𝑡𝑗

෍

j=2

5
do A[i + 1] ←A[i]
c5
෍

𝑛

(𝑡𝑗−1)

j=2

6
i ← i – 1
c6
෍

𝑛

(𝑡𝑗−1)

j=2

7
A[i + 1] = key
c7
𝑛−1

Let 𝑇(𝑛) = running time of INSERTION-SORT.

𝑛
(𝑡𝑗−1) +
c6 σj=2

𝑛
𝑡𝑗+ c5 σj=2

𝑇(𝑛) = c1 (𝑛– 1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 σj=2

𝑛
(𝑡𝑗−1) + c7(𝑛– 1)

28

<!-- page: 29 -->

INSERTION-SORT (A, n) ⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛-1
2
do key ← A[j ]
c2
𝑛−1
𝑛−1
c3
c4
c5
c6

i ← j – 1

3
4
5
6
7

𝑛

while i > 0 and A[i] > key

෍

𝑡𝑗

j=2

do A[i + 1] ←A[i]
i ← i – 1
A[i + 1] = key
c7

𝑛

෍

(𝑡𝑗−1)

j=2

𝑛

෍

(𝑡𝑗−1)

j=2

𝑛−1
𝑇(𝑛) = c1 (𝑛– 1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 σj=2

𝑛
(𝑡𝑗−1) +
c6 σj=2

𝑛
𝑡𝑗+ c5 σj=2

𝑛
(𝑡𝑗−1) + c7(𝑛– 1)

Best-case: The array is already sorted.


Always find that A[i ] ≤keyupon the first time the while loop test is run
(when i = j −1).


All 𝑡𝑗are1.


Running time is

𝑇(𝑛) = 𝑐1(𝑛−1)+ 𝑐2 (𝑛−1)+ 𝑐3 (𝑛− 1)+ 𝑐4 (𝑛− 1)+ c7 ( n −1)

=(𝑐1 + 𝑐2 + 𝑐3 + 𝑐4 + 𝑐7 )𝑛− (𝑐1 +𝑐2 + 𝑐3 + 𝑐4 +𝑐7)


Can express 𝑇(𝑛) as𝑎𝑛+𝑏for constants 𝑎and 𝑏(that depend on the
statement costs 𝑐𝑖) ⇒𝑇(𝑛)is a linear function of 𝑛. ⇒𝑇(𝑛)=Θ(𝑛)

29

<!-- page: 30 -->

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛-1
2
3
4

do key ← A[j ]

c2
c3
c4

𝑛-1
𝑛-1

i ← j – 1

𝑛

while i > 0 and A[i] > key

𝑡𝑗

෍

j=2

𝑛

5
do A[i + 1] ←A[i]
c5
෍

(𝑡𝑗−1)

j=2

𝑛

6
i ← i – 1
c6
෍

(𝑡𝑗−1)

j=2

7
A[i + 1] = key
c7
𝑛−1

𝑛
(𝑡𝑗−1) +
c6 σj=2

𝑛
𝑡𝑗+ c5 σj=2

𝑇(𝑛) = c1(n-1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 σj=2

𝑛
(𝑡𝑗−1) + c7(𝑛– 1)

Worst-case: The array is in reverse sorted order.


Always find that A[i ] > key in while loop test.

30

<!-- page: 31 -->

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛-1
2
3
4

do key ← A[j ]

c2
c3
c4

𝑛-1
𝑛-1

i ← j – 1

𝑛

while i > 0 and A[i] > key

𝑡𝑗

෍

j=2

𝑛

5
do A[i + 1] ←A[i]
c5
෍

(𝑡𝑗−1)

j=2

𝑛

6
i ← i – 1
c6
෍

(𝑡𝑗−1)

j=2

7
A[i + 1] = key
c7
𝑛−1

𝑛
(𝑡𝑗−1) +
c6 σj=2

𝑛
𝑡𝑗+ c5 σj=2

𝑇(𝑛) = c1(n-1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 σj=2

𝑛
(𝑡𝑗−1) + c7(𝑛– 1)

Worst-case: The array is in reverse sorted order.

Have to compare keywith all elements to the left of the jth

position ⇒compare with j−1 elements.

31

<!-- page: 32 -->

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛-1
2
3
4

do key ← A[j ]

c2
c3
c4

𝑛-1
𝑛-1

i ← j – 1

𝑛

while i > 0 and A[i] > key

𝑡𝑗

෍

j=2

𝑛

5
do A[i + 1] ←A[i]
c5
෍

(𝑡𝑗−1)

j=2

𝑛

6
i ← i – 1
c6
෍

(𝑡𝑗−1)

j=2

7
A[i + 1] = key
c7
𝑛−1

𝑛
(𝑡𝑗−1) +
c6 σj=2

𝑛
𝑡𝑗+ c5 σj=2

𝑇(𝑛) = c1(n-1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 σj=2

𝑛
(𝑡𝑗−1) + c7(𝑛– 1)

Worst-case: The array is in reverse sorted order.


Since the while loop exits because ireaches 0, there's one additional test
after the j − 1 tests ⇒tj = j .

32

<!-- page: 33 -->

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛-1
2
3
4

do key ← A[j ]

c2
c3
c4

𝑛-1
𝑛-1

i ← j – 1

𝑛

while i > 0 and A[i] > key

𝑡𝑗

෍

j=2

𝑛

5
do A[i + 1] ←A[i]
c5
෍

(𝑡𝑗−1)

j=2

𝑛

6
i ← i – 1
c6
෍

(𝑡𝑗−1)

j=2

7
A[i + 1] = key
c7
𝑛−1

𝑛
(𝑡𝑗−1) +
c6 σj=2

𝑛
𝑡𝑗+ c5 σj=2

𝑇(𝑛) = c1(n-1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 σj=2

𝑛
(𝑡𝑗−1) + c7(𝑛– 1)

Worst-case: The array is in reverse sorted order.

𝑛(𝑡𝑗−1) = σj=2

𝑛(𝑗−1)

σj=2

33

<!-- page: 34 -->

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛-1
2
3
4

do key ← A[j ]

c2
c3
c4

𝑛-1
𝑛-1

i ← j – 1

𝑛

while i > 0 and A[i] > key

𝑡𝑗

෍

j=2

𝑛

5
do A[i + 1] ←A[i]
c5
෍

(𝑡𝑗−1)

j=2

𝑛

6
i ← i – 1
c6
෍

(𝑡𝑗−1)

j=2

7
A[i + 1] = key
c7
𝑛−1

𝑛
(𝑡𝑗−1) +
c6 σj=2

𝑛
𝑡𝑗+ c5 σj=2

𝑇(𝑛) = c1(n-1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 σj=2

𝑛
(𝑡𝑗−1) + c7(𝑛– 1)

Worst-case: The array is in reverse sorted order. Runningtime:


𝑇(𝑛) = c1(𝑛– 1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 ( 𝑛(𝑛+1)

2
- 1) +
c6 ( 𝑛(𝑛−1)

2
- 1) + c5 ( 𝑛(𝑛−1)

𝒂
𝒄

b

2
- 1) + c7(𝑛– 1)

=
𝑛2 +
c1 + c2 + c3 - ( c4

2 + c5
2 +c6
2 ) + 𝑐7 𝑛− (𝑐1 + 𝑐3 + 𝑐4 +c7)

(c4

2 + c5
2 +c6
2 )

34

<!-- page: 35 -->

INSERTION-SORT (A, n)
⊳A[1 . . n]
cost
times
1
for j ← 2 to n
c1
𝑛-1
2
3
4

do key ← A[j ]

c2
c3
c4

𝑛-1
𝑛-1

i ← j – 1

𝑛

while i > 0 and A[i] > key

𝑡𝑗

෍

j=2

𝑛

5
do A[i + 1] ←A[i]
c5
෍

(𝑡𝑗−1)

j=2

𝑛

6
i ← i – 1
c6
෍

(𝑡𝑗−1)

j=2

7
A[i + 1] = key
c7
𝑛−1

𝑛
(𝑡𝑗−1) +
c6 σj=2

𝑛
𝑡𝑗+ c5 σj=2

𝑇(𝑛) = c1(n-1) + c2(𝑛– 1) + c3(𝑛– 1) + c4 σj=2

𝑛
(𝑡𝑗−1) + c7(𝑛– 1)

Worst-case: The array is in reverse sortedorder.


𝐶𝑎𝑛𝑒𝑥𝑝𝑟𝑒𝑠𝑠
𝑇𝑛𝑎𝑠𝑎𝑛2 + 𝑏𝑛+ 𝑐𝑓𝑜𝑟𝑐𝑜𝑛𝑠𝑡𝑎𝑛𝑡𝑠𝑎,b, c


𝑇(𝑛) 𝑖𝑠𝑎𝑞𝑢𝑎𝑑𝑟𝑎𝑡𝑖𝑐𝑓𝑢𝑛𝑐𝑡𝑖𝑜𝑛𝑜𝑓𝑛.⇒𝑇(𝑛)=Θ(𝑛2)

35

<!-- page: 36 -->

Order of Growth

We will only consider order of growth of running time:

• We can ignore the lower-order terms, since they are
relatively insignificant for very largen.
• We can also ignore leading term’s constant coefficients,
since theyare  not as important for the rate of growth in
computational efficiency for  very large n.
• For the insertion-sort algorithm, we just said that best case
was linear to n and worst/averagecase quadratic to n.

36

<!-- page: 37 -->

Designing Algorithms

•We discussed insertion sort

- Can we design better than n2 sortingalgorithms?

- We will do so using one of the most powerful
algorithm design techniques.

37

<!-- page: 38 -->

Divide-and-Conquer

•To solve problem P:

- Divide P into smaller problems P1, P2, …,Pk.

- Conquer by solving the (smaller) subproblems recursively.

- Combine the solutions to P1, P2, …, Pk into the solution for P.

38

<!-- page: 39 -->

Merge-SortAlgorithm

•Using divide-and-conquer, we can obtain the Merge-
Sort algorithm

- Divide: Divide the n elements into two subsequences
of n/2elements  each.

- Conquer: Sort the two subsequences recursively.
- Combine: Merge the two sorted subsequences to
produce thesorted answer.

39

<!-- page: 40 -->

Merge-Sort (A, p, r)

• INPUT: a sequence of n numbers stored in array A

• OUTPUT: an ordered sequence of n numbers

40

<!-- page: 41 -->

Merge (A, p, q,r)

41

![image](assets/algorithm-design-and-analysis-005/image-019.png)

![image](assets/algorithm-design-and-analysis-005/image-020.png)

<!-- page: 42 -->

42

![image](assets/algorithm-design-and-analysis-005/image-021.png)

<!-- page: 43 -->

43

![image](assets/algorithm-design-and-analysis-005/image-022.png)

<!-- page: 44 -->

44

![image](assets/algorithm-design-and-analysis-005/image-023.png)

<!-- page: 45 -->

45

![image](assets/algorithm-design-and-analysis-005/image-024.png)

<!-- page: 46 -->

46

![image](assets/algorithm-design-and-analysis-005/image-025.png)

<!-- page: 47 -->

47

![image](assets/algorithm-design-and-analysis-005/image-026.png)

<!-- page: 48 -->

48

![image](assets/algorithm-design-and-analysis-005/image-027.png)

<!-- page: 49 -->

49

![image](assets/algorithm-design-and-analysis-005/image-028.png)

<!-- page: 50 -->

50

![image](assets/algorithm-design-and-analysis-005/image-029.png)

<!-- page: 51 -->

51

![image](assets/algorithm-design-and-analysis-005/image-030.png)

<!-- page: 52 -->

52

![image](assets/algorithm-design-and-analysis-005/image-031.png)

<!-- page: 53 -->

53
Time?

![image](assets/algorithm-design-and-analysis-005/image-032.png)

<!-- page: 54 -->

54

![image](assets/algorithm-design-and-analysis-005/image-033.png)

<!-- page: 55 -->

Action of MergeSort

1
2
2
3
4
5
6
7

merge

2
4
5
7

1
2
3
6

merge

merge

2
5

4
7

1
3

2
6

merge

merge

merge

merge

5
2
4
7
1
3
2
6
Initial

Sequence

55

<!-- page: 56 -->

Analyzing Merge-Sort

• How long does merge-sort take?
-- Bottleneck = merging (and copying).

>> merging two files of size n/2 requires n comparisons
-- T(n) = comparisons to merge sort n elements.

>>to make analysis cleaner, assume n is a power of 2

•Claim. T(n) = n log2n
-- Note: same number of comparisons for ANYfile.

>> even already sorted

56

![image](assets/algorithm-design-and-analysis-005/image-034.png)

<!-- page: 57 -->

57

![image](assets/algorithm-design-and-analysis-005/image-035.png)

<!-- page: 58 -->

58

![image](assets/algorithm-design-and-analysis-005/image-036.png)

<!-- page: 59 -->

59

![image](assets/algorithm-design-and-analysis-005/image-037.png)

<!-- page: 60 -->

60

![image](assets/algorithm-design-and-analysis-005/image-038.png)

<!-- page: 61 -->

61

![image](assets/algorithm-design-and-analysis-005/image-039.png)

<!-- page: 62 -->

62

![image](assets/algorithm-design-and-analysis-005/image-040.png)

<!-- page: 63 -->

63

![image](assets/algorithm-design-and-analysis-005/image-041.png)

<!-- page: 64 -->

64

![image](assets/algorithm-design-and-analysis-005/image-042.png)

<!-- page: 65 -->

65

![image](assets/algorithm-design-and-analysis-005/image-043.png)

<!-- page: 66 -->

66

![image](assets/algorithm-design-and-analysis-005/image-044.png)

<!-- page: 67 -->

67

![image](assets/algorithm-design-and-analysis-005/image-045.png)

<!-- page: 68 -->

Conclusions

Θ(𝑛𝑙𝑔𝑛) grows more slowly than Θ(𝑛2).

Therefore, merge-sort asymptotically beats

insertion-sort in the worstcase.

In practice, merge-sort beats insertion-sortfor

n > 30 .

68
