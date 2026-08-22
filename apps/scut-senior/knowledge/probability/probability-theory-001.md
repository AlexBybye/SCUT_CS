---
source_id: probability-theory-001
course_id: probability_theory
title: 2012－2013学年第2学期《概率论与数理统计》期末试题（A卷）
original_file: 学科资料/概率论/往年卷/2013春-A.docx
document_role: past_exam
year: 2013
locator_type: heading
---

# 2012－2013学年第2学期《概率论与数理统计》期末试题（A卷）

| 题号 | 一 | 二 | 三 | 四 | 五 | 六 | 七 | 八 | 总分 |
|---|---|---|---|---|---|---|---|---|---|
| 得分 |  |  |  |  |  |  |  |  |  |
| 评卷人 |  |  |  |  |  |  |  |  |  |

**注意：**

$$
\Phi (1.67)=0.9525\quad \Phi (2.33)=0.99\quad \Phi (1.45)=0.926
$$

$$
\begin{gathered} t_{ 0.975 }  (7)=2.3646\quad \,t_{ 0.95 }  \left ( { 7 } \right )=1.8946 \\ t_{ 0.975 }  (8)=2.3060\quad \,t_{ 0.95 }  \left ( { 8 } \right )=1.8595 \end{gathered}
$$

$$
\begin{gathered} \chi _{ 0.95 }  ^{ 2 }(7)=14.067\quad \chi _{ 0.05 }  ^{ 2 }(7)=2.167 \\ \chi _{ 0.95 }  ^{ 2 }(8)=15.507\quad \chi _{ 0.05 }  ^{ 2 }(8)=2.733 \end{gathered}
$$

<!-- question: 1 -->

## 一、填空题（每空3分，共15分）

1. 设X服从参数为λ的泊松分布，且$E[(X-1)(X-2)]=1$，则$\lambda$=

   1

2. 设$X_{ 1 }  ,X_{ 2 }  ,\cdots ,X_{ n }  \left ( { n\ge 2 } \right )$为来自总体$N\left ( { 0,1 } \right )$的简单随机样本，$\bar X$为样本均值，$S ^ { 2 }$为样本方差，则$\frac { \left ( { n-1 } \right )X_{ 1 }  ^{ 2 } } { \sum  \limits_{ i=2 } ^ n { X_{ i }  ^{ 2 } } }$服从的分布是 $\frac { \left ( { n-1 } \right )X_{ 1 }  ^{ 2 } } { \sum  \limits_{ i=2 } ^ n { X_{ i }  ^{ 2 } } }\sim F\left ( { 1,n-1 } \right )$

3. 设随机变量$X$与$Y$相互独立，且均服从区间$\left[ 0,3 \right]$上的均匀分布，则$P\{\max\{X,Y\}\le 1\}=$1/9。

4. 设随机变量$X$和$Y$的数学期望分别为-2和2，方差分别为1和4，而相关系数为-0.5，则根据契比雪夫不等式$P\left \{ \begin{array}{l} \left | { X+Y } \right  |\ge 6 \end{array} \right \}\le \_\_\_\_\_$

   $$
   P\left \{ \begin{array}{l} \left | { X+Y } \right  |\ge 6 \end{array} \right \}\le \frac { 1 } { 12 }
   $$

5. 设随机变量X1，X2，X3相互独立，其中X1在[0，6]上服从均匀分布，X2服从正态分布N（0，2²），X3服从参数为$\lambda$=3的泊松分布，记Y=X1－2X2+3X3，则D（Y）=46。

<!-- question: 2 -->

## 二、（10分）

从5双尺码不同的鞋子中任取4只，求下列事件的概率：

（1）所取的4只中没有两只成对；（2）所取的4只中只有两只成对；（3）所取的4只都成对。

（1）$\frac { C_{ 5 }  ^{ 4 }2 ^ { 4 }  } { C_{ 10 }  ^{ 4 } }=\frac { 8 } { 21 }$（2）1-$\frac { C_{ 5 }  ^{ 2 }+C_{ 5 }  ^{ 4 }2 ^ { 4 }  } { C_{ 10 }  ^{ 4 } }=\frac { 12 } { 21 }$（3）$\frac { C_{ 5 }  ^{ 2 } } { C_{ 10 }  ^{ 4 } }=\frac { 1 } { 21 }$

<!-- question: 3 -->

## 三、（10分）

玻璃杯成箱出售，每箱20只。已知任取一箱，箱中0、1、2只残次品的概率相应为0.8、0.1和0.1，某顾客欲购买一箱玻璃杯，在购买时，售货员随意取一箱，而顾客随机地察看4只，若无残次品，则买下该箱玻璃杯，否则退回。试求：（1）顾客买下该箱的概率；（2）在顾客买下的该箱中，没有残次品的概率。

解：设事件$A$表示“顾客买下该箱”，${B}_{i}$表示“箱中恰好有$i$件次品”，$i=0\,,\,1\,,\,2$。则

$P({B}_{0})=0.8$，$P({B}_{1})=0.1$，$P({B}_{2})=0.1$，$P(A|{B}_{0})=1$，$P(A|{B}_{1})=\frac{C_{19}^{4}}{C_{20}^{4}}=\frac{4}{5}$，$P(A|{B}_{2})=\frac{C_{18}^{4}}{C_{20}^{4}}=\frac{12}{19}$。

由全概率公式得

$$
P(A)=\sum  \limits_{ i=0 } ^ 2 { P(B_{ i }  )P(A|B_{ i }  )=0.8\times 1+0.1\times \frac { 4 } { 5 }+0.1\times \frac { 12 } { 19 }=0.94 }
$$

由贝叶斯公式

$$
(B_{ 0 }  |A)=\frac { P(B_{ 0 }  )P(A|B_{ 0 }  ) } { P(A) }=\frac { 0.8\times 1 } { 0.94 }=0.85
$$

<!-- question: 4 -->

## 四、（15）

设二维随机变量$(X,Y)$的概率分布为

| X\Y | -1 | 0 | 1 |
|---|---:|---:|---:|
| -1 | a | 0 | 0.2 |
| 0 | 0.1 | b | 0.2 |
| 1 | 0 | 0.1 | c |

其中$a$、$b$、$c$为常数，且$X$的数学期望$E(X)=-0.2$，$P\{Y\le 0\mid X\le 0\}=0.5$，记$Z=X+Y$。求（1）$a$、$b$、$c$的值；（2）$Z$的概率分布；（3）$P\{X=Z\}$。

解：（1）由概率分布的性质可知，$a+b+c+0.6=1$，即$a+b+c=0.4$。

由$E(X)=-0.2$，可得$-a+c=-0.1$。

再由

$$
P\{Y\le 0\mid X\le 0\}
=\frac{P\{X\le 0,Y\le 0\}}{P\{X\le 0\}}
=\frac{a+b+0.1}{a+b+0.5}
=0.5
$$

解得$a+b=0.3$。

解以上关于$a$、$b$、$c$的三个方程可得，$a=0.2,b=0.1,c=0.1$。

（2）$Z$的所有可能取值为-2，-1，0，1，2。则

$$
\begin{aligned}
P\{Z=-2\}&=P\{X=-1,Y=-1\}=0.2,\\
P\{Z=-1\}&=P\{X=-1,Y=0\}+P\{X=0,Y=-1\}=0.1,\\
P\{Z=0\}&=P\{X=-1,Y=1\}+P\{X=1,Y=-1\}+P\{X=0,Y=0\}=0.3,\\
P\{Z=1\}&=P\{X=1,Y=0\}+P\{X=0,Y=1\}=0.3,\\
P\{Z=2\}&=P\{X=1,Y=1\}=0.1.
\end{aligned}
$$

所以$Z$的概率分布为

| Z | -2 | -1 | 0 | 1 | 2 |
|---|---:|---:|---:|---:|---:|
| P | 0.2 | 0.1 | 0.3 | 0.3 | 0.1 |

（3）$P\{X=Z\}=P\{Y=0\}=0+b+0.1=0.1+0.1=0.2$。

<!-- question: 5 -->

## 五、（15）

设随机变量$X$的概率密度为

$$
f_X(x)=\begin{cases} \frac{1}{2}, & \text{当 }-1<x<0, \\ \frac{1}{4}, & \text{当 }0\le x<2, \\ 0, & \text{其他} \end{cases}
$$

令$Y=X ^ { 2 }$，$F\left ( { x,y } \right )$为二维随机变量$\left ( { X,Y } \right )$的分布函数。

求（1）$Y$的密度函数$f_{ Y }  \left ( { y } \right )$；（2）$cov\left ( { X,Y } \right )$；（3）$F\left ( { -\frac { 1 } { 2 },4 } \right )$。

解：（1）$Y$的分布函数为

$$
F_{ Y }  \left ( { y } \right )=P\left \{ \begin{array}{l} Y\le y \end{array} \right \}=P\left \{ \begin{array}{l} X ^ { 2 } \le y \end{array} \right \}
$$

当$y\le 0$时，$F_{ Y }  \left ( { y } \right )=0,f_{ Y }  \left ( { y } \right )=0$。

当$0 < y < 1$时，

$$
F_{ Y }  \left ( { y } \right )=P\left \{ \begin{array}{l} -\sqrt { y }\le X\le \sqrt { y } \end{array} \right \}=P\left \{ \begin{array}{l} -\sqrt { y }\le X < 0 \end{array} \right \}+P\left \{ \begin{array}{l} 0\le X\le \sqrt { y } \end{array} \right \}=\frac { 3 } { 4 }\sqrt { y }
$$

$$
f_{ Y }  \left ( { y } \right )=\frac { 3 } { 8\sqrt { y } }
$$

当$1\le y < 4$时，

$$
F_{ Y }  \left ( { y } \right )=P\left \{ \begin{array}{l} -1\le X < 0 \end{array} \right \}+P\left \{ \begin{array}{l} 0\le X\le \sqrt { y } \end{array} \right \}=\frac { 1 } { 2 }+\frac { 1 } { 4 }\sqrt { y }
$$

$$
f_{ Y }  \left ( { y } \right )=\frac { 1 } { 8\sqrt { y } }
$$

当$y\ge 4$时，$F_{ Y }  \left ( { y } \right )=1,f_{ Y }  \left ( { y } \right )=0$。

所以$Y$的概率密度为

$$
f_Y(y)=\begin{cases} \frac{3}{8\sqrt{y}}, & \text{当 }0<y<1, \\ \frac{1}{8\sqrt{y}}, & \text{当 }1\le y<4, \\ 0, & \text{其他} \end{cases}
$$

（2）![公式原图（MathType v5 无法可靠解析，待人工复核）](assets/probability-theory-001/image-098.png)

![公式原图（原件疑似缺项，待人工修复）](assets/probability-theory-001/image-099.png)

$$
\begin{aligned}
E(XY)=E(X^3)
&=\int_{-\infty}^{+\infty}x^3f_X(x)\,dx\\
&=\int_{-1}^{0}\frac{1}{2}x^3\,dx+\int_{0}^{2}\frac{1}{4}x^3\,dx
=\frac{7}{8}.
\end{aligned}
$$

故

$$
\operatorname{cov}(X,Y)=E(XY)-E(X)E(Y)=\frac{2}{3}.
$$

（3）

$$
\begin{aligned}
F\left(-\frac{1}{2},4\right)
&=P\left\{X\le-\frac{1}{2},Y\le4\right\}
=P\left\{X\le-\frac{1}{2},X^2\le4\right\}\\
&=P\left\{X\le-\frac{1}{2},-2\le X\le2\right\}
=P\left\{-2\le X\le-\frac{1}{2}\right\}\\
&=P\left\{-1\le X\le-\frac{1}{2}\right\}
=\frac{1}{4}.
\end{aligned}
$$

<!-- question: 6 -->

## 六、（10分）

设供电站供应某地区1000户居民用电，各户用电情况相互独立。已知每户每天用电量（单位：度）在[0，20]上服从均匀分布。现要以0.99的概率满足该地区居民供应电量的需求，问供电站每天至少需向该地区供应多少度电？

解：设第K户居民每天用电量为${X}_{k}$度，1000户居民每天用电量为$X$度，${EX}_{k}=$10，${DX}_{k}=\frac{{20}^{2}}{12}$=。再设供应站需供应L度电才能满足条件，则

$$
P\{X\le L\}=\Phi(\frac{L-1000\times 10}{\sqrt{1000\times \frac{{20}^{2}}{12}}})=0.99
$$

即$\frac{L-10000}{\sqrt{100000/3}}=2.33$，则L=10425度。

<!-- question: 7 -->

## 七、（10分）

化肥厂用自动打包机装化肥，某日测得8包化肥的重量（斤）如下：

98.7　100.5　101.2　98.3　99.7　99.5　101.4　100.5

已知各包重量服从正态分布N（$\mu\,,\,{\sigma}^{2}$）

（1）是否可以认为每包平均重量为100斤（取$\alpha=0.05$）？

（2）求参数${\sigma}^{2}$的90%置信区间。

解：需要检验的假设$H_{ 0 }  :\mu =100,\quad H_{ 1 }  :\mu \ne 100$

检验统计量为$t=\frac {  \bar X-100 } { \frac { S_{ n }   } { \sqrt { n-1 } } }$，

计算可得：![公式原图（MathType v5 无法可靠解析，待人工复核）](assets/probability-theory-001/image-116.png)

$t_{ 1-\frac { \alpha  } { 2 } }  (n-1)=t_{ 0.975 }  \left ( { 7 } \right )=2.3646$，$|t|\le {t}_{\frac{\alpha}{2}}(n-1)$故接受原假设。

（2）$\alpha=0.1$，n=8，查表得$\chi _{ 0.95 }  ^{ 2 }(7)=14.067$，$\chi _{ 0.05 }  ^{ 2 }(7)=2.167$

$S_{ n }  ^{ 2 }=1.102$故置信区间为

$$
\left[ \frac { nS_{ n }  ^{ 2 } } { \chi _{ 1-\frac { \alpha  } { 2 } }  ^{ 2 }(n-1) },\frac { nS_{ n }  ^{ 2 } } { \chi _{ \frac { \alpha  } { 2 } }  ^{ 2 }(n-1) } \right]=[0.548,3.559]
$$

<!-- question: 8 -->

## 八、（15分）

设总体$X$的密度函数是$f(x;\theta)=\frac{1}{2\theta}{e}^{-\frac{|x|}{\theta}}$，其中$\theta$>0是参数。样本${X}_{1},{X}_{2},...,{X}_{n}$来自总体X。

（1）求$\theta$的矩估计$\hat \theta _{ M }$；

（2）求$\theta$的最大似然估计$\hat \theta _{ L }$；

（3）证明$\hat \theta _{ L }$是$\theta$的无偏估计，且$\hat \theta _{ L }$是$\theta$的相合估计（一致估计）。

解：（1）

$$
EX=\int _{-\infty}^{+\infty}\frac{1}{2\theta}{xe}^{-\frac{|x|}{\theta}}\,dx=0
$$

$$
\begin{aligned}{EX}^{2}=\int _{-\infty}^{+\infty}\frac{1}{2\theta}{x}^{2}{e}^{-\frac{|x|}{\theta}}\,dx=\int _{0}^{+\infty}\frac{1}{\theta}{x}^{2}{e}^{-\frac{x}{\theta}}\,dx \\ =-({x}^{2}{e}^{-\frac{x}{\theta}})\left.\right|_{0}^{+\infty}+2\int _{0}^{+\infty}{xe}^{-\frac{x}{\theta}}\,dx \\ =-2({x\theta e}^{-\frac{x}{\theta}})\left.\right|_{0}^{+\infty}+2\theta\int _{0}^{+\infty}{e}^{-\frac{x}{\theta}}\,dx=-2({\theta}^{2}{e}^{-\frac{x}{\theta}})\left.\right|_{0}^{+\infty}=2{\theta}^{2}\end{aligned}
$$

$$
\hat \theta _{ M }  =\sqrt { \frac { 1 } { 2n }\sum  \limits_{ i=1 } ^ n { X_{ i }  ^{ 2 } } }
$$

或：$DX={EX}^{2}-{(EX)}^{2}=2{\theta}^{2}$，$S_{ n }  ^{ *2 }=\mathop { DX }  ==2 \hat \theta  ^ { 2 }$，$\hat \theta _{ M }  =\frac { S_{ n }  ^{ * } } { \sqrt { 2 } }$

（2）似然函数：$L=\prod _{i=1}^{n}\frac{1}{2\theta}{e}^{-\frac{|{x}_{i}|}{\theta}}$，$L=\frac{1}{{(2\theta)}^{n}}{e}^{-\sum _{i=1}^{n}\frac{|{x}_{i}|}{\theta}}$，

$$
\ln L=-n\ln (2\theta)-\frac{1}{\theta}\sum _{i=1}^{n}|{x}_{i}|
$$

$$
\frac{d}{d\theta}(\ln L)=-\frac{n}{\theta}+\frac{1}{{\theta}^{2}}\sum _{i=1}^{n}|{x}_{i}|
$$

令，$-\frac{n}{\hat{\theta}}+\frac{1}{{\hat{\theta}}^{2}}\sum _{i=1}^{n}|{x}_{i}|=0$，$\hat \theta _{ L }  =\frac { 1 } { n }\sum  \limits_{ i=1 } ^ n { \left | { X_{ i }   } \right  | }$

（3）

$$
E|X|=\int _{0}^{+\infty}\frac{1}{\theta}{xe}^{-\frac{x}{\theta}}\,dx=-({xe}^{-\frac{x}{\theta}})\left.\right|_{0}^{+\infty}+\int _{0}^{+\infty}{e}^{-\frac{x}{\theta}}\,dx=-({\theta e}^{-\frac{x}{\theta}})\left.\right|_{0}^{+\infty}=\theta
$$

$E \hat \theta _{ L }  =\frac { 1 } { n }\sum  \limits_{ i=1 } ^ n { E\left | { X_{ i }   } \right  | }=E\left | { X } \right  |=\theta$，$\hat \theta _{ L }$是$\theta$的无偏估计，

$$
E{|X|}^{2}={EX}^{2}=2{\theta}^{2}
$$

$$
D|X|={EX}^{2}-{(E|X|)}^{2}=2{\theta}^{2}-{\theta}^{2}={\theta}^{2}
$$

$$
D(\frac{1}{n}\sum _{i=1}^{n}|{X}_{i}|)=\frac{D(|X|)}{n}=\frac{{\theta}^{2}}{n}
$$

$P\left \{ \begin{array}{l} \left | {  \hat \theta _{ L }  -E \hat \theta _{ L }   } \right  | < \varepsilon  \end{array} \right \}\le \frac { \theta  ^ { 2 }  } { n\varepsilon  ^ { 2 }  }\to 0$，$\hat \theta _{ L }$是$\theta$的相合估计。
