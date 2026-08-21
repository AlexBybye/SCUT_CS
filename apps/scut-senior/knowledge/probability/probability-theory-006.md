---
source_id: probability-theory-006
course_id: probability_theory
title: 2016春季《概率论与数理统计》A卷答案
original_file: 学科资料/概率论/往年卷/2016春季A卷答案.docx
document_role: past_exam_answer
year: 2016
locator_type: heading
---

# 2016春季《概率论与数理统计》A卷答案

<!-- question: 1 -->

## 一、填空题（每小题3分，共18分）

1．设随机变量$X$和$Y$的数学期望分别为$-2$和2,方差分别为1和4,而相关系数为$-0.5$,则根据契比雪夫不等式$P\{|X+Y|\ge6\}\le$1/12 .
解因为$E(X+Y)=EX+EY=0$
$$
D(X+Y)=DX+DY+2cov(X,Y)
$$

$$
=DX+DY+2\rho _{ XY } \sqrt { DX\cdot DY }
$$

$$
=1+4-2\times 0.5\times 2=3
$$

根据契比雪夫不等式

$$
P\left \{ \begin{array}{l} \left | { X-EX } \right |\ge \varepsilon \end{array} \right \}\le \frac { DX } { \varepsilon ^ { 2 } }
$$

所以

$$
P\left \{ \begin{array}{l} \left | { X+Y } \right |\ge 6 \end{array} \right \}\le \frac { 3 } { 36 }=\frac { 1 } { 12 }
$$

2．设总体$X$服从正态分布$N(0,2^2)$,而$X_1,X_2,\ldots,X_{15}$是来自总体$X$的简单随机样本,则随机变量

$$
Y=\frac{X_1^2+X_2^2+\cdots+X_{10}^2}{2(X_{11}^2+X_{12}^2+\cdots+X_{15}^2)}
$$

服从 F 分布,参数为 (10, 5) ..

3．设总体$X$的概率密度$f(x,\sigma )=\frac { 1 } { 2\sigma }e ^ { -\frac { |x| } { \sigma } } ,-\infty < x < +\infty$，其中参数$\sigma (\sigma >0)$未知，若$X_{ 1 } ,X_{ 2 } ,....,X_{ n }$是来自总体$X$的简单随机样本，$\widehat { \sigma }=\frac { 1 } { n-1 }\sum \limits_{ i=1 } ^ n { |X_{ i } | }$是$\sigma$的估计量，则$E( \widehat { \sigma })=$_____________

解

$$
E \hat \sigma =\frac { 1 } { n-1 }\sum \limits_{ i=1 } ^ n { E\left | { X_{ i } } \right | }=\frac { n } { n-1 }E\left | { X_{ i } } \right |
$$

$$
\begin{aligned}
&=\frac{n}{n-1}\int_{-\infty}^{+\infty}|x|\frac1{2\sigma}e^{-\frac{|x|}{\sigma}}\,dx
=\frac{2n}{n-1}\int_0^{+\infty}\frac{x}{2\sigma}e^{-\frac{x}{\sigma}}\,dx\\
&\xrightarrow{\,t=\frac{x}{\sigma}\,}\frac{n}{n-1}\int_0^{+\infty}t e^{-t}\sigma\,dt
\end{aligned}
$$

$$
=\frac{n\sigma}{n-1}\int_0^{+\infty}t e^{-t}\,dt=\frac{n}{n-1}\sigma
$$

4．设二维随即变量$(X,Y)$服从$N(\mu ,\mu ;\sigma ^ { 2 } ,\sigma ^ { 2 } ;0)$，则$E(XY ^ { 2 } )=$_____.

解 因为$(X,Y)\simN(\mu ,\mu ;\sigma ^ { 2 } ,\sigma ^ { 2 } ;0)$，则$X\simN(\mu ,\sigma ^ { 2 } )$，$Y\simN(\mu ,\sigma ^ { 2 } )$，从而有

$$
E\left ( { X } \right )=\mu ,E\left ( { X ^ { 2 } } \right )=D(X)+E ^ { 2 } (X)=\sigma ^ { 2 } +\mu ^ { 2 }
$$

又由$\rho =0$知$X,Y$相互独立，于是$X$与$Y ^ { 2 }$也独立；故

$$
E(XY ^ { 2 } )=E(X)E(Y ^ { 2 } )=\mu (\sigma ^ { 2 } +\mu ^ { 2 } )
$$

5．设随机变量$X$的分布函数$F(x)=\begin{cases} 0, \\ x < 0 \\ \frac { 1 } { 2 }, \\ 0\le x < 1 \\ 1-e ^ { -x } , \\ x\ge 1 \end{cases}$，则$P\{X=1\}=\_\_\_\_\_$.

解 由概率值与分布函数的定义知：

$$
P\{X=1\}=P\{X\le 1\}-P\{X < 1\}=F(1)-F(1-0)=1-e ^ { -1 } -\frac { 1 } { 2 }=\frac { 1 } { 2 }-e ^ { -1 }
$$

6．设随机变量$X$服从参数为1的泊松分布，则$P\left \{ \begin{array}{l} X=EX ^ { 2 } \end{array} \right \}=$ ${\underline{ }}$.

解 由$DX=EX ^ { 2 } -(EX) ^ { 2 }$，得$EX ^ { 2 } =DX+(EX) ^ { 2 }$，又因为$X$服从参数为1的泊松分布，所以$DX=EX=1$，所以$EX ^ { 2 } =1+1=2$，所以$P\left \{ \begin{array}{l} X=2 \end{array} \right \}=\frac { 1 ^ { 2 } } { 2! }e ^ { -1 } =\frac { 1 } { 2 }e ^ { -1 }$.

<!-- question: 2 -->

## 二、单项选择题（每小题3分，共18分）

1． 设$X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n }$为总体$X\simN\left ( { 0,1 } \right )$的一个样本,$\bar X$与$S ^ { 2 }$分别为样本均值和样本方差,则( )成立.
(A)$\bar X\simN\left ( { 0,1 } \right )$(B)$\sqrt { n } \bar X\simN\left ( { 0,1 } \right )$
(C)$\sum \limits_{ i=1 } ^ n { X_{ i } ^{ 2 } }\sim\chi ^ { 2 } \left ( { 2n } \right )$(D)$\bar X/S\simt\left ( { n-1 } \right )$
解：因为$\bar X\simN\left ( { 0,1/n } \right )$,所以A项不正确,B项正确.
因为$X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n }$独立,$X_{ i } \simN\left ( { 0,1 } \right )$,所以$\sum \limits_{ i=1 } ^ n { X_{ i } ^{ 2 } }\sim\chi ^ { 2 } \left ( { n } \right )$,因此C项也不正确.
$\frac { \bar X-\mu } { S/\sqrt { n-1 } }\simt\left ( { n-1 } \right )$; 当$\mu =0$,$n\ne 1$时,$\frac { \bar X } { S/\sqrt { n-1 } }\ne \frac { \bar X } { S }$,所以D项也不正确.

2．设随机变量$X$和$Y$都服从标准正态分布,则( ).[C]

(A)$X+Y$服从正态分布 (B)$X^2+Y^2$服从$\chi^2$分布

(C)$X^2$和$Y^2$都服从$\chi^2$分布 (D)$X^2/Y^2$服从$F$分布

3．设随机事件A，B满足$A\subset B$且$0 < P(A) < 1$，则必有（ ）

（A）$P\left ( { A } \right )\ge P\left ( { A\left | { A\cup B } \right . } \right )$（B）$P\left ( { A } \right )\le P\left ( { A\left | { A\cup B } \right . } \right )$

（C）$P\left ( { B } \right )\ge P\left ( { B\left | { A } \right . } \right )$（D）$P\left ( { B } \right )\le P\left ( { B\left | { \bar A } \right . } \right )$

解 因为$A\subset B$，$0 < P(A) < 1$，有$0 < P(A)\le P(B) < 1$，$A\cup B=B,AB=A$，故

$$
P\left ( { A\left | { A\cup B } \right . } \right )=P\left ( { A\left | { B } \right . } \right )=\frac { P(AB) } { P(B) }=\frac { P(A) } { P(B) }\ge P\left ( { A } \right )
$$

故选（B）.
4．设$X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ 6 }$是总体$N\left ( { \mu ,\sigma ^ { 2 } } \right )$的样本,$S ^ { 2 }$是样本方差,则$DS ^ { 2 } =$( ).
(A)$\frac { 1 } { 5 }\sigma ^ { 2 }$(B)$\frac { 1 } { 5 }\sigma ^ { 4 }$(C)$\frac { 2 } { 5 }\sigma ^ { 2 }$(D)$\frac { 5 } { 18 }\sigma ^ { 4 }$
解：因为是正态分布,且$n=6$,故$\frac { 6S ^ { 2 } } { \sigma ^ { 2 } }\sim\chi ^ { 2 } \left ( { 5 } \right )$
由$\chi ^ { 2 }$分布的性质可知$D\left ( { \frac { 6S ^ { 2 } } { \sigma ^ { 2 } } } \right )=2\times 5=10$,即$DS ^ { 2 } =\frac { 10 } { 36 }\sigma ^ { 4 } =\frac { 5 } { 18 }\sigma ^ { 4 }$.故D项正确.
5．随机变量$X{ \rm{ \sim } }N\left ( { 0,1 } \right )$，$Y{ \rm{ \sim } }N\left ( { 1,4 } \right )$且相关系数$\rho _{ XY } =1$，则（ ）
$\left ( { A } \right )$ $P\left \{ \begin{array}{l} Y=-2X-1 \end{array} \right \}=1$.$\left ( { B } \right )$ $P\left \{ \begin{array}{l} Y=2X-1 \end{array} \right \}=1$.
$\left ( { C } \right )$ $P\left \{ \begin{array}{l} Y=-2X+1 \end{array} \right \}=1$.$\left ( { D } \right )$ $P\left \{ \begin{array}{l} Y=2X+1 \end{array} \right \}=1$.
解 用排除法. 设$Y=aX+b$，由$\rho _{ XY } =1$，知道$X,Y$正相关，得$a>0$，排除$\left ( { A } \right )$、$\left ( { C } \right )$；由$X\simN(0,1),Y\simN(1,4)$，得$EX=0,EY=1,$所以
$E(Y)=E(aX+b)=aEX+b$ $=a\times 0+b=1,$因此$b=1$. 排除$\left ( { B } \right )$. 故选择$\left ( { D } \right )$
6．某人向同一目标独立重复射击，每次射击命中目标的概率为$p\ (0<p<1)$，则此人第4次射击恰好第2次命中目标的概率为
（A）$3p(1-p)^2$（B）$6p(1-p)^2$
（C）$3p^2(1-p)^2$（D）$6p^2(1-p)^2$
解 第4次一定要命中，则对前3次使用伯努列概型：$C_3^1p(1-p)^2$，加上第4次命中，概率为$C_3^1p(1-p)^2\cdot p$＝$3p^2(1-p)^2$.故选（C）.

<!-- question: 3 -->

## 三、（10分）

箱中装有6个球，其中红、白、黑球的个数分别是1，2，3个，现从箱中随机地取出2个球，记$X$为取出的红球个数，$Y$为取出的白球个数.
（Ⅰ）求随机变量$(X,Y)$的概率分布；（Ⅱ）求$Cov(X,Y)$.
解 （Ⅰ）$(X,Y)$是二维离散型随机变量，$X$只能取0和1，而$Y$可以取0，1，2各值，由于$P\{X=0,Y=0\}=\frac { C_{ 3 } ^{ 2 } } { C_{ 6 } ^{ 2 } }=\frac { 1 } { 5 }$，$P\{X=0,Y=1\}=\frac { C_{ 2 } ^{ 1 }C_{ 3 } ^{ 1 } } { C_{ 6 } ^{ 2 } }=\frac { 2 } { 5 }$，
$P\{X=0,Y=2\}=\frac { C_{ 2 } ^{ 2 } } { C_{ 6 } ^{ 2 } }=\frac { 1 } { 15 }$，$P\{X=1,Y=0\}=\frac { C_{ 3 } ^{ 1 } } { C_{ 6 } ^{ 2 } }=\frac { 1 } { 5 }$，$P\{X=1,Y=1\}=\frac { C_{ 2 } ^{ 1 } } { C_{ 6 } ^{ 2 } }=\frac { 2 } { 15 }$，$P\{X=1,Y=2\}=P\{\varphi \}=0$；于是得$(X,Y)$的联合概率分布：

| $Y$ $X$ | 0 | 1 | 2 | $P\{X=i\}$ |
|---|---:|---:|---:|---:|
| 0 | 1/5 | 2/5 | 1/15 | 2/3 |
| 1 | 1/5 | 2/15 | 0 | 1/3 |
| $P\{Y=j\}$ | 2/5 | 8/15 | 1/15 |   |

（Ⅱ）根据$(X,Y)$的联合概率分布表可以计算出$E(X)=\frac { 1 } { 3 },E(Y)=\frac { 2 } { 3 },E(XY)=\frac { 2 } { 15 }$，

于是有

$$
Cov(X,Y)=E(XY)-E(X)E(Y)=\frac { 2 } { 15 }-\frac { 1 } { 3 }\times \frac { 2 } { 3 }=-\frac { 4 } { 45 }
$$

<!-- question: 4 -->

## 四、（8分）

已知男子中有5%是色盲患者，女子中有0.25%是色盲患者，若从男女人数相等的人群中随机地挑选一人，恰好是色盲患者，问此人是男性的概率是多少？
解设$A$={抽到一名男性}；$B$={抽到一名女性}；$C$={抽到一名色盲患者}，由全概率公式得
$$
P(C)=P(C|A)P(A)+P(C|B)P(B)=5%\times \frac { 1 } { 2 }+0.25%\times \frac { 1 } { 2 }=2.625%
$$

$$
P(AC)=P(A)P(C|A)=\frac { 1 } { 2 }\times 5%=2.5%
$$

由贝叶斯公式得

$$
P(A|C)=\frac { P(AC) } { P(C) }=\frac { 20 } { 21 }
$$

<!-- question: 5 -->

## 五、（12分）

设随机变量$X$的概率密度为$f_X(x)=\begin{cases}\frac12,&-1<x<0,\\\frac14,&0\le x<2,\\0,&\text{其他},\end{cases}$，令$Y=X ^ { 2 } ,F\left ( { x,y } \right )$为二维随机变量$(X,Y)$的分布函数.
(Ⅰ)求$Y$的概率密度$f_{ Y } \left ( { y } \right )$;(Ⅱ)$Cov(X,Y)$；(Ⅲ)$F\left ( { -\frac { 1 } { 2 },4 } \right )$.
解（I） 设$Y$的分布函数为$F_{ Y } (y)$，即$F_{ Y } (y)=P(Y\le y)=P(X ^ { 2 } \le y)$，则

当$y < 0$时，$F_{ Y } (y)=0$；

当$0\le y < 1$时，$F_{ Y } (y)=P(X ^ { 2 } < y)=P\left ( { -\sqrt { y } < X < \sqrt { y } } \right )$

$$
=\int_{-\sqrt y}^{0}\frac12\,dx+\int_0^{\sqrt y}\frac14\,dx=\frac34\sqrt y
$$

当$1\le y < 4$时，$F_{ Y } (y)=P(X ^ { 2 } < y)=P\left ( { -1 < X < \sqrt { y } } \right )$

$$
=\int_{-1}^{0}\frac12\,dx+\int_0^{\sqrt y}\frac14\,dx=\frac14\sqrt y+\frac12
$$

当$y\ge 4$，$F_{ Y } (y)=1$. 所以

$$
f_Y(y)=F_Y'(y)=\begin{cases}\frac3{8\sqrt y},&0<y<1,\\\frac1{8\sqrt y},&1\le y<4,\\0,&\text{其他},\end{cases}
$$
（II）$Cov(X,Y)=Cov(X,X ^ { 2 } )=E(X-EX)(X ^ { 2 } -EX ^ { 2 } )=EX ^ { 3 } -EXEX ^ { 2 }$，而
$EX=\int_{-1}^{0}\frac{x}{2}\,dx+\int_0^2\frac{x}{4}\,dx=\frac14$，$EX^2=\int_{-1}^{0}\frac{x^2}{2}\,dx+\int_0^2\frac{x^2}{4}\,dx=\frac56$，
$EX^3=\int_{-1}^{0}\frac{x^3}{2}\,dx+\int_0^2\frac{x^3}{4}\,dx=\frac78$，所以$Cov(X,Y)=\frac { 7 } { 8 }-\frac { 1 } { 4 }\cdot \frac { 5 } { 6 }=\frac { 2 } { 3 }$.
(Ⅲ)$F\left ( { -\frac { 1 } { 2 },4 } \right )$ $=P\left ( { X\le -\frac { 1 } { 2 },Y\le 4 } \right )=P\left ( { X\le -\frac { 1 } { 2 },X ^ { 2 } \le 4 } \right )$
$$
=P\left ( { X\le -\frac { 1 } { 2 },-2\le X\le 2 } \right )=P\left ( { -2\le X\le -\frac { 1 } { 2 } } \right )
$$

$$
=\int_{-1}^{-\frac12}\frac12\,dx=\frac14
$$

<!-- question: 6 -->

## 六、（8分）

某地某种商品在一家商场中的月消费额ξ～N(*μ*,σ2),且已知σ=100元。现商业部门要对该商品在商场中的平均月消费额*μ*进行估计，且要求估计的结果须以不小于95%的把握保证估计结果的误差不超过20元，问至少需要随机调查多少家商场？
$$
\Phi (1.65)=0.95\quad \Phi (1.96)=0.975\quad \Phi (1.45)=0.926\quad \Phi \left ( { 1.40 } \right )=0.92
$$

解：求n，s.t.$P\{|\mu-\overline X|\le20\}\ge0.95$

$$
P\{|\mu-\overline X|\le20\}=P\left\{-\frac{20}{\sigma/\sqrt n}\le\frac{\overline X-\mu}{\sigma/\sqrt n}\le\frac{20}{\sigma/\sqrt n}\right\}
$$

$$
=\Phi \left ( { \frac { \sqrt { n } } { 5 } } \right )-\Phi \left ( { -\frac { \sqrt { n } } { 5 } } \right )
$$

$\Phi \left ( { \frac { \sqrt { n } } { 5 } } \right )$=0.975 n=96.04 至少调查97家

<!-- question: 7 -->

## 七、（16分）

设总体$X$服从$\left[ 0,\theta \right]$的均匀分布,$X_{ 1 } ,X_{ 2 } ,\cdots ,X_{ n }$是来自$X$的样本.
(1)求$\theta$的矩估计量$\widehat { \theta }_{ 1 }$; (2)求$\theta$的最大似然估计$\widehat { \theta }_{ 2 }$; (3)证明$\widehat { \theta }_{ 1 }$,$T_{ 1 } =\frac { n+1 } { n } \widehat { \theta }_{ 2 }$和$T_{ 2 } =$ $\left ( { n+1 } \right )\mathop { min } \limits_{ 1\le i\le n } X_{ i }$均是$\theta$的无偏估计量。
解(1)$EX=\int_0^\theta x\,dx=\frac\theta2$
令$\frac { \theta } { 2 }= \bar X$,得$\theta$的矩估计量为$\widehat { \theta }_{ 1 } =2 \bar X$.
(2)似然函数为
$$
L(x_1,x_2,\ldots,x_n;\theta)=\begin{cases}\frac1{\theta^n},&0<x_i<\theta\ (i=1,2,\ldots,n),\\0,&\text{其他},\end{cases}
$$

$$
=\begin{cases}\frac1{\theta^n},&0\le x_{(1)}\le x_{(2)}\le\cdots\le x_{(n)}\le\theta,\\0,&\text{其他},\end{cases}
$$

又因为$\frac { dlnL } { d\theta }=-\frac { n } { \theta } < 0$,所以$L\left ( { x_{ 1 } ,x_{ 2 } ,\cdots ,x_{ n } ;\theta } \right )$关于$\theta$单调减,故当$\theta =X_{ \left ( { n } \right ) }$时,$L\left ( { x_{ 1 } ,x_{ 2 } ,\cdots ,x_{ n } ;\theta } \right )$取得最大值,因此,$\theta$的最大似然估计量是

$$
\widehat { \theta }_{ 2 } =X_{ \left ( { n } \right ) } =\mathop { max } \limits_{ 1\le i\le n } \left ( { X_{ i } } \right )
$$

(3)

$$
E \widehat { \theta }_{ 1 } =E\left ( { 2 \bar X } \right )=2E \bar X=2EX=2\times \frac { \theta } { 2 }=\theta
$$

所以$\widehat { \theta }_{ 1 }$是$\theta$的无偏估计量.

$X_{ \left ( { n } \right ) }$的密度函数为

$$
f_{X_{(n)}}(x)=\begin{cases}\frac{nx^{n-1}}{\theta^n},&0<x<\theta,\\0,&\text{其他},\end{cases}
$$

故$ET_1=\frac{n+1}{n}E(X_{(n)})=\frac{n+1}{n}\int_0^\theta\frac{nx^n}{\theta^n}\,dx=\theta$

所以$T_{ 1 }$是$\theta$的无偏估计量.

$X_{ \left ( { 1 } \right ) } =\mathop { min } \limits_{ 1\le i\le n } \left ( { X_{ i } } \right )$的密度函数为

$$
f_{ X_{ \left ( { 1 } \right ) } } \left ( { x } \right )=n\left[ 1-F\left ( { x;\theta } \right ) \right] ^ { n-1 } f\left ( { x;\theta } \right )
$$

$$
=\begin{cases}n\left(1-\frac{x}{\theta}\right)^{n-1}\frac1\theta,&0<x<\theta,\\0,&\text{其他},\end{cases}
$$

故

$$
ET_2=(n+1)E(X_{(1)})=(n+1)\int_0^\theta n\left(1-\frac{x}{\theta}\right)^{n-1}\frac{x}{\theta}\,dx=\theta
$$

所以$T_{ 2 }$也是$\theta$的无偏估计量.

<!-- question: 8 -->

## 八、（10分）

化肥厂用自动打包机装化肥，某日测得8包化肥的重量（斤）如下：
98.7　100.5　101.2　98.3　99.7　99.5　101.4　100.5
已知各包重量服从正态分布N（$\mu,\sigma^2$）
（1）是否可以认为每包平均重量为100斤（取$\alpha=0.05$）？
（2）求参数$\sigma^2$的90%置信区间。
可能用到的分位点：
$t_{ 0.99 } (7)=2.998 , t_{ 0.95 } (7)=1.895 , t_{ 0.975 } (7)=2.3646,\quad t_{ 0.95 } (6)=1.943$ $\begin{gathered} \chi _{ 0.95 } ^{ 2 }(7)=14.067\quad \chi _{ 0.05 } ^{ 2 }(7)=2.167 \\ \chi _{ 0.95 } ^{ 2 }\left ( { 6 } \right )=12.592\quad \chi _{ 0.05 } ^{ 2 }\left ( { 6 } \right )=1.635 \end{gathered}$

解、$H_0:\mu_0=100$ $H_1:\mu_0\ne100$

检验统计量为$t=\frac { \bar X-\mu _{ 0 } } { \frac { s } { \sqrt { n-1 } } }$，$H_0$的拒绝域为$W=\{|t|\ge t_{ 1-\frac { \alpha } { 2 } } (n-1)\}$

计算可得：$\overline x=99.975,\quad s^2=1.102,\quad t=\frac{\overline x-\mu_0}{s/\sqrt{n-1}}=-0.063$

$t_{ 1-\frac { \alpha } { 2 } } (n-1)=t_{ 0.975 } \left ( { 7 } \right )=2.3646$，$\left | { t } \right |\le t_{ 1-\frac { \alpha } { 2 } } (n-1)$故接受原假设。

（2）$\alpha=0.1$，n=8 查表得$\chi _{ 0.95 } ^{ 2 }(7)=14.067$，$\chi _{ 0.05 } ^{ 2 }(7)=2.167$

$s ^ { 2 } =1.102$故置信区间为

$$
[\frac { ns ^ { 2 } } { \chi _{ 1-\frac { \alpha } { 2 } } ^{ 2 }(n-1) },\frac { ns ^ { 2 } } { \chi _{ \frac { \alpha } { 2 } } ^{ 2 }(n-1) }]=[0.627,4.068]
$$
