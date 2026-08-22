---
source_id: discrete-mathematics-007
course_id: discrete_mathematics
title: "离散数学试卷（中文）答案"
original_file: "学科资料/离散数学/往年卷/离散数学试卷（中文）答案.doc"
document_role: past_exam_answer
year:
locator_type: none
---

# 离散数学试卷（中文）答案

**华南理工大学期末考试答案**

**《离散数学》试卷A**

**一、填空题(本大题共12小题，每小题2分，共24分)**

**1.** $\forall$x$\exists$z (P(x)→Q(z,y))

2.  $\phi$

3. 1

4. 9,  对称

5．Q(x,y)中的y与S(x)中的x，Q(x,y)中的x  与P(x)  中的x

6． $\exists$x (C(x) ![formula-object](assets/discrete-mathematics-007/image-002.png)$\exists$y(T(y) ![formula-object](assets/discrete-mathematics-007/image-003.png)  (Q(x, y))

7. n-1

8. {<2,2>, <3,3>,<1,3>}, {<1,3>,<2,1>,<3,1>}

9.  原子命题，复合命题

10．图中无奇数度顶点

11．{$\phi$，{$\phi$}，{{a}}，{$\phi$，{a}}}，4

12．V’![formula-object](assets/discrete-mathematics-007/image-007.png)V ,  V’= V

**二、单选题** **(本大题共12小题，每小题2分，共26分)**

**B D C D B, D D C B A, C D**

**三．计算题(30分)**

**1.**

![formula-object](assets/discrete-mathematics-007/image-008.png)

2.

3.  $\left(\begin{array}{ccccc}-1&1&0&0&0\\1&0&-1&1&-1\\0&0&0&0&1\\0&-1&1&-1&0\end{array}\right)$

4.

![formula-object](assets/discrete-mathematics-007/image-010.png)

5.

1）R的关系图                                        R的关系矩阵

![image](assets/discrete-mathematics-007/image-011.jpeg)$\left[\begin{array}{cccc}0&1&0&0\\0&0&1&1\\0&1&0&1\\0&0&1&1\\\end{array}\right]$

r(R)的关系图                                          r(R)的关系矩阵

![image](assets/discrete-mathematics-007/image-013.jpeg)$\left[\begin{array}{cccc}1&1&0&0\\0&1&1&1\\0&1&1&1\\0&0&1&1\\\end{array}\right]$

s(R)的关系图                                        s(R)的关系矩阵

![image](assets/discrete-mathematics-007/image-015.jpeg)$\left[\begin{array}{cccc}0&1&0&0\\1&0&1&1\\0&1&0&1\\0&0&1&0\\\end{array}\right]$

**五．证明题(22分)**

1.
- $t$        前提引入
- ![formula-object](assets/discrete-mathematics-007/image-018.png)     前提引入
- ![formula-object](assets/discrete-mathematics-007/image-019.png)       拒取式
- ![formula-object](assets/discrete-mathematics-007/image-020.png)    前提引入
- r                  假言推理
- ![formula-object](assets/discrete-mathematics-007/image-021.png)   前提引入
- ![formula-object](assets/discrete-mathematics-007/image-022.png)      拒取式
- ![formula-object](assets/discrete-mathematics-007/image-023.png)     前提引入
- $q$         析取三段论

2.

![formula-object](assets/discrete-mathematics-007/image-025.png)

1)  关系R的自反性

取![formula-object](assets/discrete-mathematics-007/image-026.png)

![formula-object](assets/discrete-mathematics-007/image-027.png) *u* +  *v*  =  *u* +  *v*

![formula-object](assets/discrete-mathematics-007/image-028.png)![formula-object](assets/discrete-mathematics-007/image-029.png)

所以关系R满足自反性

2)  关系R的对称性

取![formula-object](assets/discrete-mathematics-007/image-030.png)  且  ![formula-object](assets/discrete-mathematics-007/image-031.png)

![formula-object](assets/discrete-mathematics-007/image-032.png) $u+y=x+v$

![formula-object](assets/discrete-mathematics-007/image-034.png) $x+v=u+y$

![formula-object](assets/discrete-mathematics-007/image-036.png) ![formula-object](assets/discrete-mathematics-007/image-037.png)

所以关系R满足对称性

3)  关系R的传递性

取![formula-object](assets/discrete-mathematics-007/image-038.png)  且  ![formula-object](assets/discrete-mathematics-007/image-039.png)

![formula-object](assets/discrete-mathematics-007/image-040.png) ![formula-object](assets/discrete-mathematics-007/image-041.png)，![formula-object](assets/discrete-mathematics-007/image-042.png)

![formula-object](assets/discrete-mathematics-007/image-043.png) $u-v=x-y$

![formula-object](assets/discrete-mathematics-007/image-045.png) $u+y=x+v$

![formula-object](assets/discrete-mathematics-007/image-047.png) ![formula-object](assets/discrete-mathematics-007/image-048.png)

所以关系R满足传递性

由以上结论可知关系R是等价关系。

3.    设![formula-object](assets/discrete-mathematics-007/image-049.png)

![formula-object](assets/discrete-mathematics-007/image-050.png)

所以原命题成立

4．

先证  1）![formula-object](assets/discrete-mathematics-007/image-051.png)2）

如果G不是连通的，那么G中至少存在两个连通子图，任何两个不同连通子图的顶点间不存在通路，这与命题1）矛盾，所以G是连通的。

下面证  n=m+1

当n=1时， 显然n=m+1成立，

假设n=k时，n=m+1成立，往证n=k+1时n=m+1成立，

由n=k时结论成立可知，此时m=k-1；

假设新增加顶点nk+1通过边w1,w2分别与原来的k个顶点中的两个顶点nt,np连接，又由命题1）可知顶点nt，np间存在唯一的通路，不妨设为L；那么顶点np存在两条到达顶点的nk+1通路，它们分别是np—w2—nk+1和np—L—nt—w1—nk+1—nk+1；这与命题1)中任何两个顶点间存在唯一的通路矛盾，因此nk+1只能与原来的k个顶点中的一个顶点存在两条以下的边。而如果顶点nk+1与原来的k个顶点间不存在连接的边，则任何定点nt与nk+1之间不存在通路，也与命题1）矛盾。因此nk+1只能与原来的k个顶点中的一个顶点存在且仅存在一条边。这样，当n=k+1时，m=k-1+1 = k;  结论成立。

再证  2）![formula-object](assets/discrete-mathematics-007/image-052.png)1）

当n=1，2时， 如果n=m+1，则顶点间存在唯一的通路，结论成立；

假设n=k时， 如果n=m+1，顶点间存在唯一的通路成立，

往证n=k+1时，如果n=m+1，则顶点间存在唯一的通路，

由于n=k时，n=m+1，则此时m=k-1，而n=k+1时  m=k；因此在增加一个顶点nk+1之后只增加了一条边，假设顶点nk+1与顶点nt之间通过边W连接，由于其它的顶点与顶点nt之间存在唯一的通路，那么其它的顶点和顶点nk+1之间都存在一条通过顶点nt、边W的通路。假设某个顶点np与nk+1之间存在两条通路，由于np顶点nt之间的通路是唯一的，因此np必须通过nt和nk+1之间的另外一条边到达nk+1，这与顶点nk+1只由一条边与原来的k个顶点相连矛盾。所以n=k+1时，如果n=m+1，则顶点间存在唯一的通路成立。

通过以上的结论可知1）![formula-object](assets/discrete-mathematics-007/image-053.png)2）
