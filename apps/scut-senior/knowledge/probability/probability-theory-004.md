---
source_id: probability-theory-004
course_id: probability_theory
title: 2014春《概率论与数理统计》A卷答案
original_file: 学科资料/概率论/往年卷/2014春A卷答案.docx
document_role: past_exam_answer
year: 2014
locator_type: heading
---

# 2014春《概率论与数理统计》A卷答案

诚信应考，考试作弊将带来严重后果！

华南理工大学本科生期末考试

《概率论与数理统计》A卷

**注意事项：**

1. 开考前请将密封线内各项信息填写清楚；
2. 所有答案请直接答在试卷上；
3. 考试形式：闭卷；
4. 本试卷共八大题，满分100分，考试时间120分钟。

| 题号 | 一 | 二 | 三 | 四 | 五 | 六 | 七 | 八 | 总分 |
|---|---|---|---|---|---|---|---|---|---|
| 得分 |  |  |  |  |  |  |  |  |  |

**注意：** $\Phi (1.67)=0.9525\quad \Phi (1.96)=0.975\quad \Phi (1.45)=0.926$

$$
\quad t_{ 0.975 } \left ( { 15 } \right )=2.132,\quad t_{ 0.95 } \left ( { 16 } \right )=1.746,\quad t_{ 0.95 } \left ( { 15 } \right )=1.753
$$

$$
\begin{gathered} \chi _{ 0.975 } ^{ 2 }(4)=11.143\quad \chi _{ 0.025 } ^{ 2 }(4)=0.484 \\ \chi _{ 0.95 } ^{ 2 }(5)=11.071\quad \chi _{ 0.05 } ^{ 2 }(5)=1.145 \\ \chi _{ 0.975 } ^{ 2 }\left ( { 5 } \right )=12.833\quad \chi _{ 0.025 } ^{ 2 }\left ( { 5 } \right )=0.831 \end{gathered}
$$

<!-- question: 1 -->

## 一、（12分）

设有n个人排成一行，甲与乙是其中的两个人，求这n个人的任意排列中，甲与乙之间恰有r个人的概率。如果这n个人围成一圈，试证明甲与乙之间恰有r个人的概率与r无关。(甲到乙是顺时针)
解：
$$
\begin{gathered} 1)P(A)=\frac { C_{ 2 } ^{ 1 }\left ( { n-r-1 } \right )(n-2)! } { n! }=\frac { 2(n-r-1) } { n(n-1) } \\ 2)P(A)=\frac { C_{ n-2 } ^{ r }(n-r-2)!r! } { (n-1)! }=\frac { 1 } { n-1 } \end{gathered}
$$

<!-- question: 2 -->

## 二、（10分）

甲、乙、丙三车间加工同一产品，加工量分别占总量的25%、35%、40%，次品率分别为0.03、0.02、0.01。现从所有的产品中抽取一个产品，试求
（1）该产品是次品的概率；
（2）若检查结果显示该产品是次品，则该产品是乙车间生产的概率是多少？
解：设$A_{ 1 }$，$A_{ 2 }$，$A_{ 3 }$表示甲乙丙三车间加工的产品，B表示此产品是次品。
（1）所求事件的概率为$P(B)=P(A_{ 1 } )P(B|A_{ 1 } )+P(A_{ 2 } )P(B|A_{ 2 } )+P(A_{ 3 } )P(B|A_{ 3 } )$ $=0.25\times 0.03+0.35\times 0.02+0.4\times 0.01=0.0185$
（2）

$$
P(A_{ 2 } |B)=\frac { P(A_{ 2 } )P(B|A_{ 2 } ) } { P(B) }=\frac { 0.35\times 0.02 } { 0.0185 }\approx 0.38
$$

<!-- question: 3 -->

## 三、（10分）

假设一部机器在一天内发生故障的概率为0.2，机器发生故障时全天停止工作，若一周5个工作日里无故障，可获利润10万元；发生一次故障可获利润5万元；发生二次故障所获利润0元；发生三次或三次以上故障就要亏损2万元，求一周内期望利润是多少？
解 由条件知$X\sim B(5,0.2)$，即$P\{X=k\}=\binom{5}{k}0.2^k0.8^{5-k},\quad k=0,1,\ldots,5$
$$
Y=g(X)=\begin{cases}10,&X=0,\\5,&X=1,\\0,&X=2,\\-2,&X\ge3,\end{cases}
$$

$$
\begin{aligned}EY=Eg(X)&=\sum_{k=0}^{5}g(k)P\{X=k\}\\&=10P\{X=0\}+5P\{X=1\}+0P\{X=2\}\\&\quad-2\bigl(P\{X=3\}+P\{X=4\}+P\{X=5\}\bigr)\\&=10\times0.328+5\times0.410-2\times0.057=5.216\text{（万元）}.\end{aligned}
$$

<!-- question: 4 -->

## 四、（15分）

设随机变量$X$和$Y$的联合分布在以点$(0,1),(1,0),(1,1)$为顶点的三角形区域上服从均匀分布,试求
(1) 关于X的边缘密度
(2) X和Y的协方差
(3) 随机变量$U=X+Y$的方差.
解三角形区域为$G=\{(x,y):0\le x\le1,\ 0\le y\le1,\ x+y\ge1\}$;随机变量$X$和$Y$的联合密度为
$$
f(x,y)=\begin{cases}2,&(x,y)\in G,\\0,&(x,y)\notin G,\end{cases}
$$

以$f_1(x)$表示$X$的概率密度,则当$x\le0$或$x\ge1$时,$f_1(x)=0$;当$0<x<1$时,有

$$
f_1(x)=\int_0^\infty f(x,y)\,dy=\int_{1-x}^{1}2\,dy=2x
$$

因此

$$
EX=\int_0^1 2x^2\,dx=\frac23,\qquad EX^2=\int_0^1 2x^3\,dx=\frac12
$$

$$
DX=EX^2-(EX)^2=\frac12-\frac49=\frac1{18}
$$

同理可得,$EY=\frac23,\qquad DY=\frac1{18}$.

现在求$X$和$Y$的协方差

$$
EXY=\iint_G 2xy\,dx\,dy=2\int_0^1x\,dx\int_{1-x}^{1}y\,dy=\frac5{12}
$$

$$
\operatorname{cov}(X,Y)=EXY-EX\cdot EY=\frac5{12}-\frac49=-\frac1{36}
$$

于是$DU=D(X+Y)=DX+DY+2\operatorname{cov}(X,Y)=\frac1{18}+\frac1{18}-\frac2{36}=\frac1{18}$

<!-- question: 5 -->

## 五、（12分）

向一目标射击，目标中心为坐标原点，已知命中点的横坐标$X$和纵坐标$Y$相互独立，且均服从$N(0,\ 2 ^ { 2 } )$分布. 求
（1）命中环形区域$D=\left \{ \begin{array}{l} \left ( { x,y } \right )\left | { 1\le x ^ { 2 } +y ^ { 2 } \le 2 } \right . \end{array} \right \}$的概率；
（2）命中点到目标中心距离$Z=\sqrt { X ^ { 2 } +Y ^ { 2 } }$的数学期望.

解： （1）$P\{(X,Y)\in D\}=\iint_D f(x,y)\,dx\,dy$

![环形区域坐标图](assets/probability-theory-004/diagram-001.png)

$$
=\iint_D\frac1{2\pi}\cdot\frac14e^{-\frac{x^2+y^2}{8}}\,dx\,dy=\frac1{8\pi}\int_0^{2\pi}\int_1^2e^{-\frac{r^2}{8}}r\,dr\,d\theta
$$

$$
=-\left.e^{-\frac{r^2}{8}}\right|_1^2=e^{-\frac18}-e^{-\frac12}
$$

（2）

$$
EZ=E\!\left(\sqrt{X^2+Y^2}\right)=\int_{-\infty}^{+\infty}\int_{-\infty}^{+\infty}\sqrt{x^2+y^2}\cdot\frac1{8\pi}e^{-\frac{x^2+y^2}{8}}\,dx\,dy
$$

$$
=\frac1{8\pi}\int_0^{2\pi}\int_0^{+\infty}re^{-\frac{r^2}{8}}r\,dr\,d\theta=\frac14\int_0^{+\infty}e^{-\frac{r^2}{8}}r^2\,dr
$$

$$
=-\left.re^{-\frac{r^2}{8}}\right|_0^{+\infty}+\int_0^{+\infty}e^{-\frac{r^2}{8}}\,dr=\frac{\sqrt{2\pi}}2\int_{-\infty}^{+\infty}\frac1{\sqrt{2\pi}}e^{-\frac{r^2}{8}}\,dr=\sqrt{2\pi}
$$

<!-- question: 6 -->

## 六、（10分）

某种电子器件的寿命(小时)具有数学期望$\mu$(未知),方差$\sigma ^ { 2 } =400$.为了估计$\mu$,随机地取$n$只这种器件,在时刻$t=0$投入测试(设测试是相互独立的)直到失败,测得寿命为$X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n }$,以$\bar X=\frac { 1 } { n }\sum \limits_{ i=1 } ^ n { X_{ i } }$作为$\mu$的估计,为了使$P\left \{ \begin{array}{l} \left | { \bar X-\mu } \right | < 1 \end{array} \right \}\ge 0.95$,问$n$至少为多少?
解、由于$X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n }$独立同分布,且$EX_{ i } =\mu ,DX_{ i } =\sigma ^ { 2 } =400$.
由林德伯格-列维定理得
$$
P\left \{ \begin{array}{l} \left | { \bar X-\mu } \right | < 1 \end{array} \right \}=P\left \{ \begin{array}{l} \left | { \frac { \bar X-\mu } { \sqrt { \sigma ^ { 2 } /n } } } \right | < \frac { 1 } { \sqrt { \sigma ^ { 2 } /n } } \end{array} \right \}\approx \Phi \left ( { \frac { \sqrt { n } } { \sigma } } \right )-\Phi \left ( { -\frac { \sqrt { n } } { \sigma } } \right )
$$

$$
=2\Phi \left ( { \frac { \sqrt { n } } { \sigma } } \right )-1=2\Phi \left ( { \frac { \sqrt { n } } { 20 } } \right )-1\ge 0.95
$$

即$\Phi \left ( { \frac { \sqrt { n } } { 20 } } \right )\ge 0.975$,查表得$\frac { \sqrt { n } } { 20 }\ge 1.96$,故$n\ge 400\times 1.96 ^ { 2 } =1536.64$.

因此$n$至少为1537.

<!-- question: 7 -->

## 七、（10分）

(1)设某机器生产的零件长度（单位：cm）$X\sim N(\mu,\sigma^2)$，今抽取容量为16的样本，测得样本均值$\overline X=10$，样本方差$S^2=0.16$. 求$\mu$的置信度为0.95的置信区间.
(2)某涤纶厂的生产的维尼纶的纤度（纤维的粗细程度）在正常生产的条件下，服从正态分布N(1.405 , 0.0482)，某日随机地抽取5根纤维，测得纤度为
1.32　1.55　1.36　1.40　1.44
问一天涤纶纤度总体X的均方差是否正常（α=0.05）?
解：（1）$\mu$的置信度为$1-\alpha$下的置信区间为
$$
\left ( { \bar X-\frac { S } { \sqrt { n-1 } }t_{ 1-\frac { \alpha } { 2 } } \left ( { n-1 } \right ),\quad \bar X+\frac { S } { \sqrt { n-1 } }t_{ 1-\frac { \alpha } { 2 } } \left ( { n-1 } \right ) } \right )
$$

$$
\bar x=10,\quad s=0.4,\quad n=16,\quad \alpha =0.05,\quad t_{ 0.975 } \left ( { 15 } \right )=2.132
$$

所以$\mu$的置信度为0.95的置信区间为（9.7868，10.2132）

(2)

$$
\begin{gathered}H_0:\sigma^2=\sigma_0^2=0.048^2,\qquad H_1:\sigma^2\ne\sigma_0^2,\\[2pt]\chi^2=\frac1{\sigma_0^2}\sum_{i=1}^{n}(X_i-\mu)^2\sim\chi^2(n),\\\chi^2_{1-\alpha/2}(n)=\chi^2_{0.975}(5)=12.833,\qquad\chi^2_{\alpha/2}(n)=\chi^2_{0.025}(5)=0.831,\\\chi^2=\frac1{0.048^2}\left[(1.32-1.405)^2+(1.55-1.405)^2+\cdots+(1.44-1.405)^2\right]=13.683,\\\text{因为 }13.683>\chi^2_{0.975}(5)=12.833,\text{ 所以拒绝 }H_0,\text{ 即均方差可认为不正常。}\end{gathered}
$$

<!-- question: 8 -->

## 八、（21分）

设总体$X$的概率密度为
$$
f(x)=\begin{cases}2e^{-2(x-\theta)},&x>\theta,\\0,&x\le\theta,\end{cases}
$$

其中$\theta >0$是未知参数,从总体$X$中抽取简单随机样本$X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n }$,记

$$
\widehat { \theta }=min\left ( { X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n } } \right )
$$

求:(1) 总体$X$的分布函数$F\left ( { x } \right )$;(2)统计量$\widehat { \theta }$的分布函数$F_{ \widehat { \theta } } \left ( { x } \right )$;(3)如果用$\widehat { \theta }$作为$\theta$的估计量,讨论它是否具有无偏性. (4)计算$\widehat { \theta }$的方差$Var\left[ \widehat { \theta } \right]$.

解(1)

$$
F(x)=\int_{-\infty}^{x}f(t)\,dt=\begin{cases}1-e^{-2(x-\theta)},&x>\theta,\\0,&x\le\theta,\end{cases}
$$
(2)

$$
F_{ \widehat { \theta } } \left ( { x } \right )=P\left \{ \begin{array}{l} \widehat { \theta }\le x \end{array} \right \}=P\left \{ \begin{array}{l} min\left ( { X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n } } \right )\le x \end{array} \right \}
$$
$$
=1-P\left \{ \begin{array}{l} min\left ( { X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n } } \right )>x \end{array} \right \}=1-P\left \{ \begin{array}{l} X_{ 1 } >x,X_{ 2 } >x,\cdots ,X_{ n } >x \end{array} \right \}
$$

$$
1-[1-F(x)]^n=\begin{cases}1-e^{-2n(x-\theta)},&x>\theta,\\0,&x\le\theta,\end{cases}
$$

(3)$\widehat { \theta }$的概率密度为

$$
f_{\widehat\theta}(x)=\frac{dF_{\widehat\theta}(x)}{dx}=\begin{cases}2ne^{-2n(x-\theta)},&x>\theta,\\0,&x\le\theta,\end{cases}
$$

因为

$$
E\widehat\theta=\int_{-\infty}^{+\infty}x f_{\widehat\theta}(x)\,dx=\int_\theta^{+\infty}2nxe^{-2n(x-\theta)}\,dx=\theta+\frac1{2n}\ne\theta
$$

所以$\widehat { \theta }$作为$\theta$的估计量不具有无偏性.

(4)

$$
\begin{aligned}E\widehat\theta^2&=\int_{-\infty}^{+\infty}x^2 f_{\widehat\theta}(x)\,dx=\int_\theta^{+\infty}2nx^2e^{-2n(x-\theta)}\,dx=\frac{2\theta^2n^2+2\theta n+1}{2n^2},\\D\widehat\theta&=E\widehat\theta^2-(E\widehat\theta)^2=\frac1{4n^2}.\end{aligned}
$$
