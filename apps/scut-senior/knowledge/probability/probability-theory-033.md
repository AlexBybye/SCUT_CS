---
source_id: probability-theory-033
course_id: probability_theory
title: "2016春季A卷答案"
original_file: "学科资料/概率论/往年卷/2016春季A卷答案.docx"
document_role: past_exam_answer
year: 2016
locator_type: none
---

# 2016春季A卷答案

**一、** **填空题（每小题3分，共18分）**

1．设随机变量![image](assets/probability-theory-033/image-001.png)和![image](assets/probability-theory-033/image-002.png)的数学期望分别为![image](assets/probability-theory-033/image-003.png)和2,方差分别为1和4,而相关系数为![image](assets/probability-theory-033/image-004.png),则根据契比雪夫不等式![image](assets/probability-theory-033/image-005.png)    1/12    .

**解**  因为                  $E(X+Y)=EX+EY=0$

$$
D(X+Y)=DX+DY+2cov(X,Y)
$$

![formula-object](assets/probability-theory-033/image-008.png)

$$
=1+4-2\times0.5\times2=3
$$

根据契比雪夫不等式

$$
P\{|X-EX|\leq\varepsilon\}\leq\frac{DX}{\varepsilon^{2}}
$$

所以                         $P\{X+Y|\leq6\}\leq\frac{3}{36}=\frac{1}{12}$

2．设总体![image](assets/probability-theory-033/image-012.png)服从正态分布![image](assets/probability-theory-033/image-013.png),而![image](assets/probability-theory-033/image-014.png)是来自总体![image](assets/probability-theory-033/image-015.png)的简单随机样本,则随机变量

![image](assets/probability-theory-033/image-016.png)

服从      F      分布,参数为    (10, 5)    ..

3．设总体$X$的概率密度![formula-object](assets/probability-theory-033/image-018.png)，其中参数$\sigma(\sigma>0)$未知，若$X_1,X_2,...,X_n$是来自总体$X$的简单随机样本，$\sigma=\frac{1}{n-1}\sum_{i=1}^{n}X_i$是$\sigma$的估计量，则$E(\sigma)=$_____________

解 $E\hat{O}=\frac{1}{n-1}\sum_{i=1}^{n}E|X_i|=\frac{n}{n-1}E|X|$

![formula-object](assets/probability-theory-033/image-026.png)

$$
\frac{n\sigma}{n-1}\int_0^{+\infty}te^{-t}dt=\frac{n}{n-1}\sigma
$$

4．设二维随即变量$(X,Y)$服从$N(\mu,\mu;\sigma^2,\sigma^2;0)$，则$E(XY^2)=$_____.

解 因为![formula-object](assets/probability-theory-033/image-031.png)，则![formula-object](assets/probability-theory-033/image-032.png)，![formula-object](assets/probability-theory-033/image-033.png)，从而有

$$
E(X)=\mu,E(X^2)=D(X)+E^2(X)=\sigma^2+\mu^2
$$

又由$\rho=0$知$X,Y$相互独立，于是$X$与$Y^2$也独立；故

$E(XY^2)=E(X)E(Y^2)=\mu(\sigma^2+\mu^2)$.

5．设随机变量$X$的分布函数![formula-object](assets/probability-theory-033/image-041.png)，则$P\{X=1\}=$.

解  由概率值与分布函数的定义知：

![formula-object](assets/probability-theory-033/image-043.png).

6．设随机变量$X$服从参数为1的泊松分布，则$P\left\{X=EX^2\right\}=$![formula-object](assets/probability-theory-033/image-046.png).

解  由$DX=EX^{2}-(EX)^{2}$，得$EX^{2}=DX+(EX)^{2}$，又因为$X$服从参数为1的泊松分布，所以$DX=EX=1$，所以$EX^2=1+1=2$，所以 $P\{X=2\}=\frac{1_2^2}{2!}e^{-1}=\frac{1}{2}e^{-1}$.

**二、单项选择题（每小题3分，共18分）**

1． 设$X_1,X_2,...,X_n$为总体![formula-object](assets/probability-theory-033/image-054.png)的一个样本,  $\overline{X}$与$S^{2}$分别为样本均值和样本方差,则(    )成立.

(A)  $X_N(0,1)$                                              (B)  ![formula-object](assets/probability-theory-033/image-058.png)

(C)  $\sum_{i=1}^{n}X_i^2\sim\chi^2(2n)$                                        (D)  ![formula-object](assets/probability-theory-033/image-060.png)

解：因为![formula-object](assets/probability-theory-033/image-061.png),所以A项不正确,B项正确.

因为$X_1,X_2,...,X_n$独立, ![formula-object](assets/probability-theory-033/image-063.png),所以$\sum_{i=1}^{n}X_i^2-\chi^2(n)$,因此C项也不正确.

![formula-object](assets/probability-theory-033/image-065.png); 当$mu=0$,  $n\neq1$时,  $\frac{\bar{X}}{S/\sqrt{n-1}}\sim\frac{\bar{X}}{S}$,所以D项也不正确.

2．设随机变量![image](assets/probability-theory-033/image-069.png)和![image](assets/probability-theory-033/image-070.png)都服从标准正态分布,则(    ).                                                  **[C]**

(A)![image](assets/probability-theory-033/image-071.png)服从正态分布                        (B)![image](assets/probability-theory-033/image-072.png)服从![image](assets/probability-theory-033/image-073.png)分布

(C)![image](assets/probability-theory-033/image-074.png)和![image](assets/probability-theory-033/image-075.png)都服从![image](assets/probability-theory-033/image-076.png)分布                  (D)![image](assets/probability-theory-033/image-077.png)服从![image](assets/probability-theory-033/image-078.png)分布

3．设随机事件A，B满足![formula-object](assets/probability-theory-033/image-079.png)且$0<P(A)<1$，则必有（  ）

（A）$P(A)P(A|A∪B)$       （B）![formula-object](assets/probability-theory-033/image-082.png)

（C）$P(B)P(B|A)$           （D）![formula-object](assets/probability-theory-033/image-084.png)

解 因为![formula-object](assets/probability-theory-033/image-085.png)，$0<P(A)<1$，有![formula-object](assets/probability-theory-033/image-087.png)，![formula-object](assets/probability-theory-033/image-088.png)，故

![formula-object](assets/probability-theory-033/image-089.png)

故选（B）.

4. 设![formula-object](assets/probability-theory-033/image-090.png)是总体![formula-object](assets/probability-theory-033/image-091.png)的样本,  $S^{2}$是样本方差,则![formula-object](assets/probability-theory-033/image-093.png)  (    ).

(A)  $\frac{1}{5}\sigma^2$                (B)  ![formula-object](assets/probability-theory-033/image-095.png)                (C)$\frac{2}{5}\sigma^2$                (D)  $\frac{5}{18}\sigma^{4}$

解：因为是正态分布,且$n=6$,故![formula-object](assets/probability-theory-033/image-099.png)

由$χ^{2}$分布的性质可知$D\left(\frac{6S^{2}}{\sigma^{-2}}\right)=2\times5=10$,即![formula-object](assets/probability-theory-033/image-102.png).故D项正确.

5. 随机变量$X~N(0,1)$，$Y~N(1,4)$且相关系数![formula-object](assets/probability-theory-033/image-105.png)，则（   ）

![formula-object](assets/probability-theory-033/image-106.png) $P\{Y=-2X-1\}=1$.			$(B)$$P\{Y=2X-1\}=1$.

$(C)$$P\{Y=-2X+1\}=1$.			$(D)$$P\{Y=2X+1\}=1$.

解  用排除法.  设![formula-object](assets/probability-theory-033/image-114.png)，由![formula-object](assets/probability-theory-033/image-115.png)，知道$X,Y$正相关，得$a>0$，排除![formula-object](assets/probability-theory-033/image-118.png)、$(C)$；由![formula-object](assets/probability-theory-033/image-120.png)，得$EX=0,EY=1,$ 所以

$E(Y)=E(aX+b)=aEX+b$$=a\times0+b=1,$ 因此$b=1$.  排除$(B)$.  故选择$(D)$

6.  某人向同一目标独立重复射击，每次射击命中目标的概率为$p(0<p<1)$，则此人第4次射击恰好第2次命中目标的概率为

（A）$3p(1-p)^2$							（B）$6p(1-p)^2$

（C）$3p^{2}(1-p)^{2}$						（D）$6p^{2}(1-p)^{2}$

解  第4次一定要命中，则对前3次使用伯努列概型：$C_{3}^{1}p(1-p)^{2}$，加上第4次命中，概率为$C_1^1p(1-p)^2\cdotp$＝$3p^{2}(1-p)^{2}$.故选（C）.

**三、(10分）**箱中装有6个球，其中红、白、黑球的个数分别是1，2，3个，现从箱中随机地取出2个球，记$X$为取出的红球个数，$Y$为取出的白球个数.

（Ⅰ）求随机变量$(X,Y)$的概率分布；（Ⅱ）求$Cov(X,Y)$.

解    （Ⅰ）$(X,Y)$是二维离散型随机变量，$X$只能取0和1，而$Y$可以取0，1，2各值，由于![formula-object](assets/probability-theory-033/image-142.png)，$P\{X=0,Y=1\}=\frac{C_2^1C_3^1}{C_6^2}=\frac{2}{5}$  ，

$P\{X=0,Y=2\}=\frac{C_2^2}{C_6^2}=\frac{1}{15}$，![formula-object](assets/probability-theory-033/image-145.png)，$P\{X=1,Y=1\}=\frac{C_2^1}{C_6^2}=\frac{2}{15}$，$P\{X=1,Y=2\}=P\{\phi\}=0$；于是得$(X,Y)$的联合概率分布

| $Y$<br>$X$ | 0 | 1 | 2 | $P\{X=i\}$ |
|---|---|---|---|---|
| 0 | 1/5 | 2/5 | 1/15 | 2/3 |
| 1 | 1/5 | 2/15 | 0 | 1/3 |
| $P\{Y=j\}$ | 2/5 | 8/15 | 1/15 |  |

（Ⅱ）根据$(X,Y)$的联合概率分布表可以计算出$E(X)=\frac{1}{3},E(Y)=\frac{2}{3},E(XY)=\frac{2}{15}$，

于是有$Cov(X,Y)=E(XY)-E(X)E(Y)=\frac{2}{15}-\frac{1}{3}\times\frac{2}{3}=-\frac{4}{45}$.

**四、（8分）**已知男子中有5%是色盲患者，女子中有0.25%是色盲患者，若从男女人数相等的人群中随机地挑选一人，恰好是色盲患者，问此人是男性的概率是多少？

**解**  设$A$={抽到一名男性}；![formula-object](assets/probability-theory-033/image-157.png)={抽到一名女性}；![formula-object](assets/probability-theory-033/image-158.png)={抽到一名色盲患者}，由全概率公式得

![formula-object](assets/probability-theory-033/image-159.png)

$$
P(AC)=P(A)P(C|A)=\frac{1}{2}\times5\%=2.5\%
$$

由贝叶斯公式得

$$
P(A|C)=\frac{P(AC)}{P(C)}=\frac{20}{21}
$$

**五.（12分）** 设随机变量$X$的概率密度为![formula-object](assets/probability-theory-033/image-163.png)，令$Y=X^{2}F(x,y)$为二维随机变量$(X,Y)$的分布函数.

(Ⅰ)求$Y$的概率密度$f_Y(y)$;(Ⅱ)$Cov(X,Y)$；(Ⅲ)　　$F\left(-\frac{1}{2},4\right)$.

解（I） 设$Y$的分布函数为$F_Y(y)$，即![formula-object](assets/probability-theory-033/image-172.png)，则
<!-- question: probability-theory-033-Q1 -->

1. 当$y<0$时，$F_y(y)=0$；
1. 当![formula-object](assets/probability-theory-033/image-175.png)时，  $F_{Y}(y)=P(X^{2}<y)=P(-\sqrt{y}<X<\sqrt{y})$

![formula-object](assets/probability-theory-033/image-177.png).
1. 当![formula-object](assets/probability-theory-033/image-178.png)时，$F_{Y}(y)=P(X^{2}<y)=P(-\sqrt{y}<X<\sqrt{y})$

$=\int_{-1/2}^{0}\frac{1}{2}\mathrm{d}x+\int_{0}^{\sqrt{y}}\frac{1}{4}\mathrm{d}x=\frac{1}{4}\sqrt{y}+\frac{1}{2}$.
<!-- question: probability-theory-033-Q2 -->

1. 当$y4$，$F_{Y}(y)=1$.  所以

![formula-object](assets/probability-theory-033/image-183.png).

（II）  $Cov(X,Y)=Cov(X,X^2)=E[(X-E[X])(X^2-E[X^2])]=EX^3-E[EX^2]$，而

$EX=\int_{-1}^{0}\frac{x}{2}dx+\int_{0}^{1}\frac{x}{4}dx=\frac{1}{4}$，$EX^{2}=\int_{-1}^{0}\frac{x^{3}}{2}dx+\int_{0}^{6}\frac{x^{2}}{4}dx=\frac{5}{6}$，

$EX^{3}=\int_{-1}^{0}\frac{x^{3}}{2}dx+\int_{0}^{6}\frac{x^{3}}{4}dx=\frac{7}{8}$，所以  $Cov(X,Y)=\frac{7}{8}-\frac{1}{4}\cdot\frac{5}{6}=\frac{2}{3}$.

(Ⅲ)  $F\left(-\frac{1}{2},4\right)$$=P\left(X\leq-\frac{1}{2},Y\leq4\right)=P\left(X\leq-\frac{1}{2},X^{2}\leq4\right)$

![formula-object](assets/probability-theory-033/image-191.png)

$=\int_{-1}^{1/2}\frac{1}{2}\mathrm{d}x=\frac{1}{4}$.

**六．（8分）** 某地某种商品在一家商场中的月消费额～N(*μ*,σ2),且已知σ=100元。现商业部门要对该商品在商场中的平均月消费额*μ*进行估计，且要求估计的结果须以不小于95%的把握保证估计结果的误差不超过20元，问至少需要随机调查多少家商场？

**$\Phi(1.65)=0.95\quad\Phi(1.96)=0.975\quad\Phi(1.45)=0.926\quad\Phi(1.40)=0.92$**

解：求n，s.t.  $P\left\{\mu-\overline{X}\leq20\right\}0.95$

$$
P\left\{\mu-\overline{X}\leq20\right\}=P\left\{-\frac{20}{\sigma/\sqrt{n}}\leq\frac{\overline{X}-\mu}{\sigma/\sqrt{n}}\leq\frac{20}{\sigma/\sqrt{n}}\right\}
$$

$$
-\Phi\left(\frac{\sqrt{n}}{5}\right)-\Phi\left(-\frac{\sqrt{n}}{5}\right)
$$

$\Phi\left(\frac{\sqrt{n}}{5}\right)$=0.975  n=96.04            至少调查97家

**七、(16分)**、设总体$X$服从$[0,\theta]$的均匀分布, $X_1,X_2,...,X_n$是来自$X$的样本.

(1)求$\theta$的矩估计量$\hat{\theta}_1$; (2)求$\theta$的最大似然估计$\hat{\theta}_{2}$; (3)证明$\hat{\theta}_1$,$T_1=\frac{n+1}{n}\hat{\theta}_2$和![formula-object](assets/probability-theory-033/image-208.png)$(n+1)\min_{i=1}^{n}X_i$均是$\theta$的无偏估计量。

**解**    (1)                   $EX=\int_{0}^{\theta}xdx=\frac{\theta}{2}$

令$\frac{\theta}{2}=\bar{X}$,得$\theta$的矩估计量为$\hat{\theta}_1=2\bar{X}$.

<!-- question: probability-theory-033-Q3 -->

(2)似然函数为

![formula-object](assets/probability-theory-033/image-215.png)

![formula-object](assets/probability-theory-033/image-216.png)

又因为![formula-object](assets/probability-theory-033/image-217.png),所以$L(x_1,x_2,...,x_n;\theta)$关于$\theta$单调减,故当$\theta=X_{(n)}$时, $L(x_1,x_2,...,x_n;\theta)$取得最大值,因此,$\theta$的最大似然估计量是

![formula-object](assets/probability-theory-033/image-223.png)

(3)     $E\hat{\theta_1}=E(2\bar{X})=2EX=2EX=2\times\frac{\theta}{2}=\theta$

所以$\hat{\theta}_1$是$\theta$的无偏估计量.

$X_{(n)}$的密度函数为

![formula-object](assets/probability-theory-033/image-228.png)

故          $ET_{1}=\frac{n+1}{n}E(X_{(n)})=\frac{n+1}{n}\int_{0}^{\theta}\frac{x^{n}}{\theta^{n}}dx=\theta$

所以$T_1$是$\theta$的无偏估计量.

![formula-object](assets/probability-theory-033/image-232.png)的密度函数为

$$
f_{X(0)}(x)=n[1-F(x;\theta)]^{n-1}f(x;\theta)
$$

![formula-object](assets/probability-theory-033/image-234.png)

故            ![formula-object](assets/probability-theory-033/image-235.png)

所以$T_2$也是$\theta$的无偏估计量.

**八．**（10分）

化肥厂用自动打包机装化肥，某日测得8包化肥的重量（斤）如下：

98.7  100.5    101.2  98.3  99.7  99.5  101.4  100.5

已知各包重量服从正态分布N（$\mu,\sigma^2$）

<!-- question: probability-theory-033-Q4 -->

（1）是否可以认为每包平均重量为100斤（取$\alpha=0.05$）？

<!-- question: probability-theory-033-Q5 -->

（2）求参数$\sigma^2$的90%置信区间。

可能用到的分位点：

$t_{0.99}^{\prime}(7)=2.998,t_{0.95}^{\prime}(7)=1.895,t_{0.975}^{\prime}(7)=2.3646,t_{0.95}^{\prime}(6)=1.943$       $X_{0.95}^{2}(7)=14.067X_{0.05}^{2}(7)=2.167X_{0.95}^{2}(6)=12.592X_{0.05}^{2}(6)=1.635$

解、 $H_0:\mu_0=100$   $H_1:\mu_0=100$

检验统计量为$t=\frac{\overline{X}-\mu_0}{s/\sqrt{n-1}}$，$H_0$的拒绝域为$W=\{t|t_{1-\alpha/2}(n-1)\}$

计算可得：  $x=99.975,s^2=1.102,t=\frac{\overline{x}-\mu_0}{s/\sqrt{n-1}}=-0.063$

$t_{1-\frac{\alpha}{2}}(n-1)=t_{0.975}(7)=2.3646$      ，$t_{\frac{n-1}{2}}(n-1)$    故接受原假设。

（2）$\alpha=0.1$，n=8  查表得$X_{0.95}^2(7)=14.067$，$X_{0.05}^2(7)=2.167$

$s^{2}=1.102$    故置信区间为

$$
[\frac{ns^{2}}{\chi_{1-\frac{n}{2}}^{2}(n-1)},\frac{ns^{2}}{\chi_{\frac{n}{2}}^{2}(n-1)}]=[0.627,4.068]
$$
