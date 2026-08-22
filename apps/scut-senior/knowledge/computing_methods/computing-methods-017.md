---
source_id: computing-methods-017
course_id: computing_methods
title: "数值分析试卷"
original_file: "学科资料/计算方法/大纲+试卷/paper/数值分析试卷.docx"
document_role: past_exam
year: 
locator_type: none
---

# 数值分析试卷

一填空&问答

<!-- question: computing-methods-017-Q1 -->

1. 误差的来源通常有4种，它们是：

<!-- question: computing-methods-017-Q2 -->

1. 下列各数是按四舍五入原则得到的近似数，它们各有几位有效数字？误差限是多少？

86.3325			0.0618			6.38005			0.7500

<!-- question: computing-methods-017-Q3 -->

1. 数值积分公式的代数精确度是根据什么来定义的？对于Newton-Cotes求积公式，其代数精确度是多少？

<!-- question: computing-methods-017-Q4 -->

1. 使用样条插值函数来逼近f(x)的有优点是什么？

<!-- question: computing-methods-017-Q5 -->

1. 试给出用牛顿法和弦位法求$\sqrt {\mathrm {3}}$的迭代公式。

<!-- question: computing-methods-017-Q6 -->

1. 试给出埃特金(Aitken)方法的几何解释。

二．用拉格朗日插值或牛顿插值找经过(-1，0) (0，-1)(1，-2)(2，3)的三次插值多项式，并求它的一阶数值微分。

三．求	$2x_1+x_2=2-x_1+2x_2=02x_1-2x_2=2$	的最小二乘解。

四．（1）取n=8，分别用复化梯形和复化抛物线公式计算下列积分

$\int _{\mathrm {0}} ^{\pi } \mathrm {sin} \mathrm {xdx}$（保留小数点后7位）

<!-- question: computing-methods-017-Q7 -->

（2）与精确值比较它们各有几位有效数字。

五．

设 $2x_1-x_2+x_3=2x_1+x_2+x_3=1x_1+3x_2-2x_3=5$

试写出求解次方程组的Jacobi迭代，Seidel迭代的迭代格式，并讨论它们的收敛性。

六．用LU分解法求解下列方程组。

$$
3x_1-x_2+4x_3=0-x_1+2x_2-2x_3=12x_1-3x_2-2x_3=-7
$$

七

<!-- question: computing-methods-017-Q8 -->

1. 试写出列主元高斯求解n阶线性代数方程组AX=b的详细算法。

<!-- question: computing-methods-017-Q9 -->

1. 试写出自动选取步长梯形求积法的算法。

八．设p1（x）是过（x0,y0）（x0,y0）两点的线性插值函数，[a，b]是包含[x0，x1]的任意区间，并设f’’（x）在[a，b]上连续，证明对任意给定的x$\mathrm { \in }$[a，b]，总存在一点$\mathrm {\xi \in }$（a，b），使得

$$
R(x)=f(x)-P_{1}(x)=\frac{f''(\xi)}{2!}(x-x_0)(x-x_1)
$$
