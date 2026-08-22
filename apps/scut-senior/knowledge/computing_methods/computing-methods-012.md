---
source_id: computing-methods-012
course_id: computing_methods
title: "《计算方法》课程考试试卷(B卷)"
original_file: "学科资料/计算方法/大纲+试卷/paper/《计算方法》课程考试试卷(B卷).doc"
document_role: past_exam
year: 
locator_type: none
---

# 《计算方法》课程考试试卷(B卷)

**2006～2007学年 第一学期**

**《计算方法》课程考试试卷(B卷)**

**(开卷)**

**院(系)__________专业班级______________学号______________** **姓名__________________**

**考试日期:**  2007年1月30日                                           **考试时间:** 下午 2:30~5:00

| **题号** | 一 | 二 | 三 | 四 | 五 | 六 | 七 | 八 | 九 | 十 | **总分** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **得分** |  |  |  |  |  |  |  |  |  |  |  |

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- 填空题 (每小题 4分，共 28份)

1．已知矩阵 $A=\begin {gathered} \left [ {\sqrt {2} -\sqrt {2}\middle | }\right ] \end {gathered}$，则${\left ‖ {A}\right ‖}_{2}=$             。

<!-- question: computing-methods-012-Q1 -->

2． 若用正$n$边形的面积作为其内接圆面积的近似值，则该近似值的相对误差是           。

<!-- question: computing-methods-012-Q2 -->

3．方程$x=ln(1+{x}^{2})$的牛顿迭代格式是                       。

4．若求解某线性方程组有迭代公式${X}^{(n+1)}={BX}^{(n)}+F$，其中$B=\begin {gathered} \left [ { 1 \sqrt {a}\middle | }\right ] \end {gathered}$，则该迭代公式收敛的充要条件是           。

5．设$f(x)=\frac {x} {\sqrt {1+{x}^{2}}}$，则满足条件$p\left ( {\frac {i} {2}}\right )=f\left ( {\frac {i} {2}}\right ) (i=0, 1, 2)$的二次插值公式$p(x)=$                       。

6．已知求积公式$\int f(x) dx\approx \frac {1} {8}[f(0)+6f(\alpha )+f(1)]$至少具1次代数精度，则$\alpha =$           。

<!-- question: computing-methods-012-Q3 -->

7．隐式中点方法

$$
{y}_{n+1}={y}_{n}+h f({t}_{n}+h/2, \frac {{y}_{n}+{y}_{n+1}} {2})
$$

应用于初值问题$y'(t)=y(t), y(0)=1$的数值解${y}_{n}=$           。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (10分)    证明：对任何初值${x}_{0}$，由迭代公式

$$
{x}_{n}=cos{x}_{n-1} , n=1, 2,\cdots
$$

所生成的序列$\left \{ {{x}_{n}}\right \}$均收敛于方程$x=cosx$的根。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (20分)    给定线性方程组

$$
\begin {gathered} \left \{ {8{x}_{1}+{x}_{2}-{x}_{3}=8\middle | }\right \left \{ {{x}_{1}-7{x}_{2}+2{x}_{3}=-4\middle | }\right \end {gathered}
$$

<!-- question: computing-methods-012-Q4 -->

（1）试用Gauss消去法求解其方程组；

(2)    给出求解其方程组的Jacobi迭代格式和 Gauss-Seidel迭代格式，并说明其二种迭代格式的收敛性。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (12分)  已知$f(x)={e}^{x}(3x-{e}^{x})$，插值节点

$$
{x}_{0}=1.00, {x}_{1}=1.02, {x}_{2}=1.04, {x}_{3}=1.06,
$$

试构造Lagrange插值公式计算$f(1.03)$ 的近似值（保留4位有效数字），并给出其实际误差。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (14分)  用Romberg算法计算积分

$\int sin(x{}^{2})dx$（精确到${10}^{-4}$）。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (16分)  给出单支$\theta$-方法

${y}_{n+1}={y}_{n}+h f[\theta {t}_{n}+(1-\theta ){t}_{n+1},\theta {y}_{n}+(1-\theta ){y}_{n+1}] (0\le \theta \le 1)$，

<!-- question: computing-methods-012-Q5 -->

1. 计算其方法的截断误差；

<!-- question: computing-methods-012-Q6 -->

1. 当$\theta$=？时，其方法为2阶相容；

<!-- question: computing-methods-012-Q7 -->

1. 当该方法应用于初值问题

$$
\begin {gathered} \left \{ {y'(t)=\lambda y(t), t\in [{t}_{0}, T],\middle | }\right \end {gathered}
$$

时（其中$\lambda$为实常数），其在$t={t}_{n}$处的数值解${y}_{n}=?$
