---
source_id: engineering-mathematical-analysis-1-013
course_id: engineering_math_analysis_1
title: "2017软件工科数学分析上B卷及答案"
original_file: "学科资料/工科数学分析I/历年试卷/13-19/2017软件工科数学分析上B卷及答案.pdf"
document_role: past_exam_answer
year: 2017
locator_type: page
---

# 2017软件工科数学分析上B卷及答案

<!-- page: 1 -->

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 封. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 线. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

诚信应考, 考试作弊将带来严重后果!

华南理工大学本科生期末考试

姓名
学号
学院
专业班级
座位号

《工科数学分析》2017-2018 学年第一学期期末考试试卷(B) 卷

参考答案

注意事项：

1. 开考前请将密封线内各项信息填写清楚;

2. 所有答案请直接答在试卷上;

3. 考试形式：闭卷;

4. 本试卷共5 个大题, 满分100 分, 考试时间120 分钟。

题
号
一
二
三
四
五
总
分
得
分
评卷人

<!-- question: engineering-mathematical-analysis-1-013-Q1 -->

一、填空题（5 小题，每小题3 分，共15 分）

（密封线内不答题）

n√2n + 3n =
3
；

1. 极限lim
n→∞

2. 设曲线y = x3 + ax2 + bx + c 有拐点(1, −1)，且在x = 0 处有极⼤值，则

a =
−3
，b =
0
，c =
1
；

3. 设y = sin(2x)，则d(n)y =
2n sin
(

2x + nπ
2
)

dxn
；

(√

1 −x2 + ex2 sin x
)

4.
´ 1

dx =
π
2
；

−1

5. 反常积分
´ 0

ex
1+ex dx =
ln 2
。

−∞

<!-- question: engineering-mathematical-analysis-1-013-Q2 -->

二、计算下列各题（3 小题，每小题8 分，共24 分）

ex2+2 cos x−3

1. 求极限lim
x→0

x4

解：考虑带Peano 余项的Maclaurin 公式，

ex2 = 1 + x2 + 1

2x4 + o(x4),

cos x = 1 −1

2x2 + 1
4!x4 + o(x4),

因此，

ex2 + 2 cos x −3

1 + x2 + 1
2x4 + o(x4) + 2 −x2 + 1
12x4 + o(x4) −3
x4

x4
= lim

lim
x→0

x→0

( 7

12 + o(1)
)

= lim

x→0

= 7

12.

《⼯科数学分析》试卷
第1 页共6 页

<!-- page: 2 -->

2. 求不定积分
´

cos(ln x)dx

解：令t = ln x，则x = et, dx = etdt,

ˆ

ˆ

cos tetdt.

cos(ln x)dx =

由分部积分法，

ˆ

ˆ

cos tetdt =

etd sin t

ˆ

= et sin t −

sin tetdt

ˆ

= et sin t +

etd cos t

ˆ

= et sin t + et cos t −

cos tetdt.

因此，
ˆ

cos tetdt = 1

2(sin t + cos t)et + C.

即，
ˆ

cos(ln x)dx = 1

2x(sin(ln x) + cos(ln x)) + C.

3. 计算定积分
´
a
√

2
0
dx

3
2
解：

(a2−x2)

ˆ
a
√

3
2 =
ˆ
π
4

dx

a cos t
a3 cos3 tdt

2

(a2 −x2)

0

0

ˆ
π
4

= 1

1
cos2 tdt

a2

0

= 1

π
4
0

a2 tan t|

= 1

a2 .

《⼯科数学分析》试卷
第2 页共6 页

<!-- page: 3 -->

<!-- question: engineering-mathematical-analysis-1-013-Q3 -->

三、解答题（4 小题，每题8 分，共32 分）

3,
√

3,
√

3
√

1. 证明数列
√

3
√

3
√

3, . . . 收敛，并求其极限。

√

3，且an+1 = √3an.

解：数列的通项an 满⾜a1 =

√

先证明数列{an} 有界，0 < a1 =

3 < 3，若0 < an < 3，则

3an <
√

0 <
√

3 · 3 = 3.

√

因此，由归纳法有0 < an <

3.

√

另⼀⽅⾯，an+1

3
an > 1，因此an+1 > an，数列{an} 是单调递增数列。

an
=

由单调有界收敛定理，数列{an} 收敛，记其极限为a，则a 满⾜

√

a =

3a.

√

因此，a = 0 或a = 3，⽽{an} 单调递增，a > a1 =

3。因此，数列的极限为3.




g(x)−e−x

x
,
x̸ = 0

其中g′′(x) 连续，且g(0) = 1, g′(0) = −1。

2. 设f(x) =



0,
x = 0

(1) 求f ′(x)；(2) 讨论f ′(x) 在(−∞, +∞) 上的连续性。

解：(1) 当x̸ = 0 时，

f ′(x) = (g′(x) + e−x)x −(g(x) −e−x)

x2
= xg′(x) −g(x) + e−x(x + 1)

x2
.

当x = 0 时，

g(x) −e−x

f(x) −f(0)

f ′(0) = lim

x
= lim

x2

x→0

x→0

g′(x) + e−x

g′′(x) −e−x

= lim

2x
= lim

2

x→0

x→0

= g′′(0) −1

2
.

因此，




xg′(x)−g(x)+e−x(x+1)

x2
,
x̸ = 0,

f ′(x) =

g′′(0)−1



2
,
x = 0.

(2) 由于g′′(x) 连续，g′(x) 和g(x) 也连续，因此f ′(x) 在x̸ = 0 处都连续。在x = 0 处，

xg′′(x) −xe−x

g′′(x) −e−x

2
= g′′(0) −1

lim
x→0 f ′(x) = lim

2
= f ′(0).

2x
= lim

x→0

x→0

因此，f ′(x) 在x = 0 处也连续。即，f ′(x) 在(−∞, +∞) 连续.

《⼯科数学分析》试卷
第3 页共6 页

<!-- page: 4 -->




2
4 + 3
´ t

√

π
4 cos2 u sin udu

x =

4 处的切线⽅程，并求d2y
dx2 。

上对应t = π

3. 求曲线

y = sin3 t



解：

= 3 sin2 t cos t

dy

dy
dx =

dt
dx

3 cos2 t sin t = tan t.

dt

4 时，x =
√

2
4 , y =
√

当t = π

2
4 .
dy
dx

4
= tan π

4 = 1.

t= π

因此，曲线对应t = π

4 处的切线⽅程为

√

√

2
4
= x −

2
4

y −

即，y = x.

d( dy

dx)
dt
dx

1
cos2 t
3 cos2 t sin t =
1
3 sin t cos4 t.

d2y
dx2 =

=

dt

4. 求曲线y = ln x 与直线y = 0 及y = e + 1 −x 所围成的平⾯图形的⾯积。

解：曲线y = ln x 与直线y = 0 交于(1, 0) 点，与直线y = e + 1 −x 交于(e, 1) 点。如图，

y

y = e + 1 −x

y = ln x

1

x

0
1
e
e + 1

所求⾯积为

ˆ e

ˆ e+1

e + 1 −xdx

V =

1
ln xdx +

e

1 −
ˆ e

1
1dx + (e + 1) · 1 −1
2((e + 1)2 −e2)

= x ln x|e

= 3

2.

《⼯科数学分析》试卷
第4 页共6 页

<!-- page: 5 -->

<!-- question: engineering-mathematical-analysis-1-013-Q4 -->

四、证明题（2 小题，每小题10 分，共20 分）

1. 设f(x) 在(a, b) 上连续，且f(a+) 与f(b−) 都存在，证明：f(x) 在(a, b) 上⼀致连续。

证明：定义函数






f(a+),
x = a,

˜f(x) =

f(x),
x ∈(a, b),





f(b−),
x = b.

由f(x) 在(a, b) 连续，知˜f(x) 在(a, b) 连续。

lim
x→a+ ˜f(x) = lim

x→a+ f(x) = f(a+) = ˜f(a).

lim
x→b−˜f(x) = lim

x→b−f(x) = f(b−) = ˜f(b).

因此，˜f(x) 在[a, b] 连续。所以，˜f(x) 在[a, b] ⼀致连续，f(x) 在(a, b) ⼀致连续。

2. 证明：当x > 0 时，ln(1 + x) > arctan x
1+x 。

证明：由Cauchy 中值定理，存在ξ ∈(0, x) 使得

1
1+ξ
1
1+ξ2
.

arctan x = ln(1 + x) −ln(1)

ln(1 + x)

arctan x −arctan 0 =

注意到，
1
1+ξ2 < 1，且ξ < x，因此

1
1+ξ
1
1+ξ2
>
1
1 + ξ >
1
1 + x.

因此，

ln(1 + x) > arctan x

1 + x .

《⼯科数学分析》试卷
第5 页共6 页

<!-- page: 6 -->

<!-- question: engineering-mathematical-analysis-1-013-Q5 -->

五、应用题（本题9 分）

设由y =
1
x2 , y = 0, x = 1, x = 2 所围成的曲边梯形被直线x = t(1 < t < 2) 分成A, B 两部分，将A, B
分别绕直线x = t 旋转，所得旋转体体积分别为VA 和VB。问t 为何值时，VA + VB 最⼩？

解：

ˆ t

1
2π(t −x) 1
x2 dx

y

VA =

t

= −2π t

1
−2π ln x|t

1

x

= 2π(t −1) −2π ln t.

ˆ 2

2π(x −t) 1
x2 dx

VB =

A
B

t

2

t + 2πt 1

x

= 2π ln x|2

0
1
t
2

x

t
= 2π(ln 2 −ln t) + π(t −2).

因此，

VA + VB = 3πt −4π ln t + 2π(ln 2 −2) =: f(t).

3 是f(t) 的极值点，且f ′′ ( 4
3
)

由f ′(t) = 3π −4π

t = 0 可知，t = 4

> 0 知其为极⼩值点。故t = 4

3 时，
VA + VB 极⼩。

《⼯科数学分析》试卷
第6 页共6 页
