---
source_id: algorithm-design-and-analysis-027
course_id: algorithm_design_and_analysis
title: 9-tutorial
original_file: "学科资料/算法设计与分析/PPT-英文版/9-tutorial.pdf"
document_role: note
year: 
locator_type: page
---

# 9-tutorial

<!-- page: 1 -->

1.给定如下两个带流的网络，画出对应的剩余图。

7,3

a

3,2
a

b

7,5

5,5

9,1

4,4

6,6

s

t
b

t

s

2,1

8,5

5,3

6,1

2,2

7,5

c

d

c

8,4

<!-- page: 2 -->

7,3

5,5
原始图

a

3,2
a

b

7,5

9,1

4,4

6,6

s

t
b

t

s

2,1

8,5

5,3

6,1

2,2

7,5

c

d

c

8,4

剩余图

4

a

1
a

b

3

2

5

8

4

1

5
2

5

6

1

s

t
b

1

t

s

3

5

3

2

1

2

2

4
5

c

d

c

4

<!-- page: 3 -->

2. 给定如下网络，采用Ford-Fulkerson算法按照增广路
径1,2交替迭代，并更新剩余图。
增广路径1：s-a-b-t，增广路径2：s-b-a-t

Ford-Fulkerson算法：
输入：网络（G,s,t,c）
输出：G中的一个流
1. 初始化剩余图，设R=G
2. for 边(u,v)∈E
3.
f(u,v) <- 0
4. end for
5. While 在 R中有一条曾广路径p=s,…,t
6.   设△为p的瓶颈容量
7.
for p 中的每条边(u,v)
8.
f(u,v) <- f(u,v)+△
9.
end for
10.
更新剩余图R
11.End while

a

500

500

1

s

t

500
500

b

<!-- page: 4 -->

2. 给定如下网络，采用Ford-Fulkerson算法按照增广路
径1,2交替迭代，并更新剩余图。
a

500

500

1
增广路径1：s-a-b-t
增广路径2：s-b-a-t

s

t

500
500

b

第一次迭代，路径s-a-b-t

第二次迭代，路径s-b-a-t

a

a

500

499

499

499

1

1
1

1

1

s

t

s

t

1

499

499

1
500

499

1

b

b

<!-- page: 5 -->

3. 给定如下剩余图，画出相应的层次图。

12

12

a

a

c

c

4

12

20

16

8
4

12

4

10

t

t

s

s

10
7

7

9

9

9
4

13

4

10
4

d

d

b

b

14

4

<!-- page: 6 -->

剩余图

12

12

a

a

c

c

4

12

20

16

8
4

12

4

10

t

t

s

s

10
7

7

9

9

9
4

13

4

10
4

d

d

b

b

14

4

层次图

12

a

a

c

c

20

4

16

8

t

t

s

s

7

9

13

4

10

d

d

b

b

14

<!-- page: 7 -->

4. 给定如下网络，采用最小路径长度增值法（MPLA）计
算最大流。

MPLA算法：
输入：网络(G,s,t,c)
输出：G中的最大流
1. for 每条边(u,v)∈E
2.
f(u,v) <- 0
3. end for
4. 初始化剩余图，设R=G
5. 查找R的层次图L
6. while t 为 L中的顶点
7.
while t 在L中能从s到达
8.
设p为L中从s到t的一条路径
9.
设△为p的瓶颈容量
10.
用△增值当前流f
11.
沿着路径p更新L和R
12.
end while
13.
用剩余图R计算新的层次图L
14.end while

12

a

c

16

20

10

4

t

s

7

9

13

4

d

b

14

<!-- page: 8 -->

12

12/12

a

c

a

c

20

16

16/12

20/12

t

s

t

s

13

4

d

b

d

b

14

第一层次图

增值s,a,c,t

12

a

c

a

c

12

4

8
4

12

t

s

t

s

10
7

9

9
4

13/4

10
4

4/4

d

b

d

b

14/4

4
剩余图

增值s,b,d,t

<!-- page: 9 -->

a

a

c

c

12

4

4

8
4

12

8

t

s

t

s

10
7

7

9

9
4

9

10
4

10

d

b

d

b

4
剩余图

第二层次图

12

a

a

c

c

19

4

8/7

4

1
4

12

t

t

s

s

10
7

7/7

9

2
11

9/7

3
4

10/7

d

b

d

b

11
剩余图

增值s,b,d,c,t

<!-- page: 10 -->

12

a

c

a

19

4

4

1
4

12

t

s

10
7

s

9

2
11

3
2

3
4

d

b

b
d

11
剩余图

第三层次图

12

a

c

19

12

t

s

7

11

4

d

b

11

最后的流
