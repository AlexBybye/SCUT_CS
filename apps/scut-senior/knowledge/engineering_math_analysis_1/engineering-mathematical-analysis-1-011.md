---
source_id: engineering-mathematical-analysis-1-011
course_id: engineering_math_analysis_1
title: "2017软件工科数学分析上A卷及答案"
original_file: "学科资料/工科数学分析I/历年试卷/13-19/2017软件工科数学分析上A卷及答案.pdf"
document_role: past_exam_answer
year: 2017
locator_type: page
---

# 2017软件工科数学分析上A卷及答案

<!-- page: 1 -->

![image](assets/engineering-mathematical-analysis-1-011/image-001.png)

<!-- page: 2 -->

![image](assets/engineering-mathematical-analysis-1-011/image-002.jpeg)

<!-- page: 3 -->

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 密. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 封. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 线. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

诚信应考, 考试作弊将带来严重后果!

华南理工大学本科生期末考试

姓名
学号
学院
专业班级
座位号

《工科数学分析》2017-2018 学年第一学期期末考试试卷(A) 卷

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

（密封线内不答题）

<!-- question: engineering-mathematical-analysis-1-011-Q1 -->

一、填空题（5 小题，每小题3 分，共15 分）

[

]

1
√

n2+1 +
1
√

n2+2 + · · · +
1
√

1. 极限lim
n→∞

=
1
；

n2+n

2. 设在区间[0, 1] 上，f ′′(x) > 0，则f ′(0), f ′(1), f(1) −f(0) 的⼤⼩顺序

是
f ′(0) < f(1) −f(0) < f ′(1)
；

3. 设y = xex，则d(n)y =
(x + n)exdxn
；

(√

)

4.
´ 2

1 −x2
4 +
sin x
1+x6

dx =
π
；

−2

5. 反常积分
´ +∞

0
x
ex dx =
1
。

<!-- question: engineering-mathematical-analysis-1-011-Q2 -->

二、计算下列各题（3 小题，每小题8 分，共24 分）

e−x2 ´ x

0 t2et2dt
x

1. 求极限
lim
x→+∞

解：应⽤L’Hˆospital 法则和原函数存在定理，

e−x2 ´ x

´ x

0 t2et2dt
x
=
lim
x→+∞

0 t2et2dt
xex2

lim
x→+∞

x2ex2

=
lim
x→+∞

ex2 + 2x2ex2

x2

=
lim
x→+∞

1 + 2x2

= 1

2.

《⼯科数学分析》试卷
第1 页共6 页

<!-- page: 4 -->

2. 求不定积分
´ 1+sin x

1+cos xexdx

解：

ˆ
1 + sin x
1 + cos xexdx =
ˆ 1 + 2 sin x

2 cos x
2
2 cos2 x
2
exdx

ˆ
1
2 cos2 x
2
ex + tan x

2 exdx

=

ˆ

exd tan x

2 + tan x
2 dex

=

ˆ

(

2 ex)

tan x

=

d

= tan x

2 ex + C.

3. 计算定积分
´ 2a

√

x2−a2

x4
dx

a

解：

√

ˆ 2a

ˆ
π
3

x2 −a2

a tan t
a4 sec4 td(a sec t)

x4
dx =

a

0

ˆ
π
3

tan2 t
sec3 tdt

= 1

a2

0

ˆ
π
3

= 1

0
sin2 t cos tdt

a2

ˆ
π
3

= 1

0
sin2 td sin t

a2

=
1
3a2 sin3 t

π
3
0

√

3
8a2 .

=

《⼯科数学分析》试卷
第2 页共6 页

<!-- page: 5 -->

<!-- question: engineering-mathematical-analysis-1-011-Q3 -->

三、解答题（4 小题，每题8 分，共32 分）

1. 设a > 0, 0 < x1 < 1
a, xn+1 = xn(2 −axn), (n = 1, 2, . . .)，证明{xn} 收敛，并求其极限。

解：先证明数列{xn} 有界。因为

(

)2

xn −1

+ 1

xn+1 = xn(2 −axn) = −a

a.

a

因此，若0 < xn < 1

a，则0 < xn+1 < 1

a。现在有0 < x1 < 1

a，由归纳法，0 < xn < 1

a，n = 1, 2, . . ..

进⽽，{xn} 是⼀个正数列，满⾜
xn+1

= 2 −axn > 1.

xn

即{xn} 是单调递增数列。

由单调有界收敛定理，数列{xn} 收敛，记其极限为x。在等式

xn+1 = xn(2 −axn)

两端令n →∞，有

x = x(2 −ax).

解得x = 0 或x = 1

a。

由于数列{xn} 单调递增，故x ⩾x1 > 0，因此x = 1

a.

2. 求函数f(x) = (x −1)
3√
x2 的单调区间及拐点（要求列表）。

解：函数f(x) 的定义域为(−∞, +∞)，

2
3 + 2
3(x −1)x−1
3 = 5x −2
3 3√x ,

f ′(x) = x

f ′′(x) = 15

3 x−1
3 −1
9(5x −2)x−4
3 = 2
9x−4
3 (5x + 1).

列表如下

(

5
)

5
(

5, 0
)

0
(

0, 2
5
)
2
5
( 2

5, +∞
)

−∞, −1

−1

−1

x

f ′(x)
+
+
+
不存在
−
0
+
f ′′(x)
−
0
+
不存在
+
+
+

[

0, 2
5
]

[ 2

5, +∞
)

由表中数据知，函数f(x) 在(−∞, 0] 单调递增，在

单调递减，在

单调递增。

= −
6
5 3√
25，即
(

)

5 时，f
(

5
)

当x = −1

−1

−1

5, −
6
5 3√
25

是函数f(x) 的拐点。

《⼯科数学分析》试卷
第3 页共6 页

<!-- page: 6 -->




x = a(t −sin t)

(0 ⩽t ⩽2π) 上斜率为1 的切线⽅程，并求d2y

3. 求旋轮线

dx2 。



y = a(1 −cos t)

解：由参数求导法,

dy

=
a sin t
a(1 −cos t) =
sin t
1 −cos t.

y′(x) =

dt
dx

dt

在切线斜率为1 的点处, 参数t 满⾜

1 = y′(x) =
sin t
1 −cos t

即, t = π

2 . 此参数对应的旋轮线上的点为

(π

)

(π

2 −1
)

2 −sin π
2

x0 = a

= a

,
y0 = a.

因此, 切线⽅程为

(π

2 −1
)

y −a = x −a

.

函数y′(x) 可由参数⽅程表⽰为




x = a(t −sin t),

y′ =
sin t
1−cos t,
0 < t < 2π.



因此,

cos t(1−cos t)−sin2 t

dy′(x)

(1−cos t)2
a(1 −cos t)
= −
1
a(1 −cos t)2 .

y′′(x) =

dt
dx

=

dt

4. 求曲线y = (x −1)(x −2) 和x 轴所围成的平⾯图形绕y 轴旋转⽽成的⽴体的体积。
解：所求旋转体的体积为

ˆ 2

1
2πx|(x −1)(x −2)|dx

V =

ˆ 2

y

= −2π

1
x(x −1)(x −2)dx

1
2

x

ˆ 2

0

1
x3 −3x2 + 2xdx

= −2π

y = (x −1)(x −2)

4 −x3 + x2
)

(x4

2

= −2π

1

= π

2 .

《⼯科数学分析》试卷
第4 页共6 页

<!-- page: 7 -->

<!-- question: engineering-mathematical-analysis-1-011-Q4 -->

四、证明题（2 小题，每小题10 分，共20 分）

1. 设f(x) 在[a, b] 上满⾜李普希兹条件：|f(x) −f(y)| ⩽L|x −y|(∀x, y ∈[a, b])，其中L 为常数。

证明：f(x) 在[a, b] 上⼀致连续。

证明：∀ε > 0, ∃δ = ε

L，使得当x1, x2 ∈[a, b] 且满⾜|x1 −x2| < δ 时，

|f(x1) −f(x2)| ⩽L|x1 −x2| < Lδ = ε.

因此，f(x) 在[a, b] ⼀致连续。

2. 设函数f(x) 在[−1, 1] 上有三阶连续导数，且f(−1) = 0, f(1) = 1, f ′(0) = 0，证明：⾄少存在
ξ ∈(−1, 1), 使得f ′′′(ξ) = 3。

解：考虑f(x) 在x = 0 处带Lagrange 余项的三阶Taylor 公式。存在ξ1 ∈(−1, 0) 使得

f(−1) = f(0) + f ′(0)(−1) + f ′′(0)

2!
(−1)2 + f ′′′(ξ1)

3!
(−1)3.

即，

0 = f(0) + f ′′(0)
2!
−1

6f ′′′(ξ1).

同理，存在ξ2 ∈(0, 1) 使得

f(1) = f(0) + f ′(0)1 + f ′′(0)

2!
12 + f ′′′(ξ2)
3!
13.

即，

1 = f(0) + f ′′(0)
2!
+ 1

6f ′′′(ξ2).

因此，

f ′′′(ξ1) + f ′′′(ξ2)

2
= 3.

由于f ′′′(x) 在[−1, 1] 连续，由介值定理，存在ξ ∈(ξ1, ξ2) ⊂(−1, 1)，使得

f ′′′(ξ) = f ′′′(ξ1) + f ′′′(ξ2)

2
= 3.

《⼯科数学分析》试卷
第5 页共6 页

<!-- page: 8 -->

<!-- question: engineering-mathematical-analysis-1-011-Q5 -->

五、应用题（本题9 分）

(

0, π
2
)

(

0 ⩽x ⩽π
2
)

与x 轴y 轴及直线x = π

问当a 在

2 所围图形的⾯
积最⼩，并求此最⼩⾯积。

内取何值时，曲线y = sin(x −a),

(

0 ⩽x ⩽π
2
)

与x 轴y 轴及直线x =
π
2 所围图形的⾯积，则

解：记V (a) 为曲线y = sin(x −a),

y
y = sin(x −a)

ˆ
π
2

0
| sin(x −a)|dx

V (a) =

ˆ a

ˆ
π
2

= −

0
sin(x −a)dx +

sin(x −a)dx

a

x

π
2
a

= cos(x −a)|a

0 −cos(x −a)|

0
a
π
2

(π

2 −a
)

= 2 −cos a −cos

= 2 −cos a −sin a.

(

0, π
2
)

下⾯求V (a) 在

的最⼩值，

V ′(a) = sin a −cos a.

4 + sin π
4 =
√

4 ，且V ′′ ( π
4
)

由V ′(a) = 0 得a = π

= cos π

2 > 0。即V (a) 在a = π
4 处取最⼩值，最⼩值为

(π

)

4 −sin π
4 = 2 −
√

= 2 −cos π

V

2.

4

《⼯科数学分析》试卷
第6 页共6 页
