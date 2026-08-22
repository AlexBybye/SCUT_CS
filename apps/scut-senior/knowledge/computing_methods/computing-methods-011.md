---
source_id: computing-methods-011
course_id: computing_methods
title: "《计算方法》课程考试试卷(A卷)"
original_file: "学科资料/计算方法/大纲+试卷/paper/《计算方法》课程考试试卷(A卷).doc"
document_role: past_exam
year: 
locator_type: none
---

# 《计算方法》课程考试试卷(A卷)

**2006～2007学年 第一学期**

**《计算方法》课程考试试卷(A卷)**

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

1．已知矩阵 $A=\begin {gathered} \left [ {1 -1\middle | }\right ] \end {gathered}$，则${\left ‖ {A}\right ‖}_{\infty }=$             。

<!-- question: computing-methods-011-Q1 -->

2． 若用正$n$边形的面积作为其外接圆面积的近似值，则该近似值的相对误差是           。

3．三次方程${x}^{3}-{x}^{2}-x+1=0$的牛顿迭代格式是                       。

4．若求解某线性方程组有迭代公式${X}^{(n+1)}={BX}^{(n)}+F$，其中$B=\begin {gathered} \left [ { a -\sqrt {a}\middle | }\right ] \end {gathered}$，则该迭代公式收敛的充要条件是           。

5．设$f(x)={xe}^{x}$，则满足条件$p\left ( {\frac {i} {2}}\right )=f\left ( {\frac {i} {2}}\right ) (i=0, 1, 2)$的二次插值公式$p(x)=$                       。

6．已知求积公式$\int f(x) dx\approx (1-\alpha )f(0)+\alpha f(1/2)+(1+\alpha )f(1)$至少具0次代数精度，则$\alpha =$           。

<!-- question: computing-methods-011-Q2 -->

7．改进的Euler方法

$$
{y}_{n+1}={y}_{n}+\frac {h} {2} [ f({t}_{n},{y}_{n})+f({t}_{n+1},{y}_{n}+h {f}_{n})]
$$

应用于初值问题$y'(t)=y(t), y(0)=1$的数值解${y}_{n}=$           。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (10分)    为数值求得方程${x}^{2}-x-2=0$的正根，可建立如下迭代格式

${x}_{n}=\sqrt {2+{x}_{n-1}} , n=0, 1, 2,\cdots$,

试利用迭代法的收敛理论证明该迭代序列收敛，且满足$\lim_ {n\to \infty } {x}_{n}=2$.

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (20分)    给定线性方程组

$$
\begin {gathered} \left \{ {2{x}_{1}+{x}_{2}+2{x}_{3}=10\middle | }\right \left \{ {-4{x}_{1}-{x}_{2} -5{x}_{3}=-19\middle | }\right \end {gathered}
$$

<!-- question: computing-methods-011-Q3 -->

（1）试用Gauss消去法求解其方程组；

(2)    给出求解其方程组的Jacobi迭代格式和 Gauss-Seidel迭代格式，并说明其二种迭代格式的收敛性。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (12分)  已知y=sinx的函数表

| X | 1.5 | 1.6 | 1.7 |
|---|---|---|---|
| sinx | 0.99749 | 0.99957 | 0.99166 |

试造出差商表，利用二次Newton插值公式计算sin(1.609)  （保留5位有效数字），并给出其误差估计。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (14分)  用Romberg算法计算积分

$\int cos(x{}^{2})dx$（精确到${10}^{-4}$）。

| **得**  **分** |  |
|---|---|
| **评卷人** |  |

- (16分)  给出线性$\theta$-方法

${y}_{n+1}={y}_{n}+h [ \theta {f}_{n}+(1-\theta ){f}_{n+1}] (0\le \theta \le 1)$，

<!-- question: computing-methods-011-Q4 -->

1. 计算其方法的截断误差；

<!-- question: computing-methods-011-Q5 -->

1. 当$\theta$=？时，其方法为2阶相容；

<!-- question: computing-methods-011-Q6 -->

1. 当该方法应用于初值问题

$$
\begin {gathered} \left \{ {y'(t)=\lambda y(t), t\in [{t}_{0}, T],\middle | }\right \end {gathered}
$$

时（其中$\lambda$为实常数），其在$t={t}_{n}$处的数值解${y}_{n}=?$
