---
source_id: probability-theory-028
course_id: probability_theory
title: "2013春-A"
original_file: "学科资料/概率论/往年卷/2013春-A.docx"
document_role: note
year: 2013
locator_type: none
---

# 2013春-A

**2012－2013学年第2学期《概率论与数理统计》期末试题（A卷）**

| 题号 | 一 | 二 | 三 | 四 | 五 | 六 | 七 | 八 | 总分 |
|---|---|---|---|---|---|---|---|---|---|
| 得分 |  |  |  |  |  |  |  |  |  |
| 评卷人 |  |  |  |  |  |  |  |  |  |

**注意：** **![formula-object](assets/probability-theory-028/image-001.png)**

$$
t_{0.975}(7)=2.3646t_{0.95}(7)=1.8946t_{0.975}(8)=2.3060t_{0.95}(8)=1.8595
$$

$$
X_{0.95}^2(7)=14.067X_{0.05}^2(7)=2.167X_{0.95}^2(8)=15.507X_{0.05}^2(8)=2.733
$$

**一、填空题（每空3分，共15分）。**

1、设X服从参数为λ的泊松分布，且$E[(X-1)(X-2)]=1$，则![formula-object](assets/probability-theory-028/image-005.png)=

1

2、设![formula-object](assets/probability-theory-028/image-006.png)为来自总体$N(0,1)$的简单随机样本,$\overline{X}$为样本均值,$S^{2}$为样本方差,则$\frac{(n-1)X_1^2}{\sum_{i=2}^{n}X_i^2}$服从的分布是           .                                                            ![formula-object](assets/probability-theory-028/image-011.png)

3、设随机变量$X$与$Y$相互独立,且均服从区间$[0,3]$上的均匀分布,则![formula-object](assets/probability-theory-028/image-015.png)![formula-object](assets/probability-theory-028/image-016.png)    1/9    .

4、设随机变量$X$和$Y$的数学期望分别为-2和2,方差分别为1和4,而相关系数为-0.5,则根据契比雪夫不等式![formula-object](assets/probability-theory-028/image-019.png)

![formula-object](assets/probability-theory-028/image-020.png)

5、设随机变量X1，X2，X3相互独立，其中X1在[0，6]上服从均匀分布，X2服从正态分布N（0，22），X3服从参数为![formula-object](assets/probability-theory-028/image-021.png)=3的泊松分布，记Y=X1－2X2+3X3，则D（Y）=    46

**二、（10分）**从5双尺码不同的鞋子中任取4只，求下列事件的概率：

（1）所取的4只中没有两只成对；（2）所取的4只中只有两只成对（3）所取的4只都成对

（1）$\frac{C_5^42^4}{C_{10}^4}=\frac{8}{21}$（2）1-$\frac{C_5^2+C_5^1\cdot2^1}{C_{10}^4}=\frac{12}{21}$（3）$\frac{C_5^2}{C_{10}^4}=\frac{1}{21}$

三、**(10分)**玻璃杯成箱出售，每箱20只。已知任取一箱，箱中0、1、2只残次品的概率相应为0.8、0.1和0.1，某顾客欲购买一箱玻璃杯，在购买时，售货员随意取一箱，而顾客随机地察看4只，若无残次品，则买下该箱玻璃杯，否则退回。试求：（1）顾客买下该箱的概率 ；（2）在顾客买下的该箱中，没有残次品的概率 。

解：设事件$A$表示“顾客买下该箱”，$B_i$表示“箱中恰好有$i$件次品”，$i=0,1,2$。则

$P(B_0)=0.8$，$P(B_1)=0.1$，$P(B_2)=0.1$，$P(A|B_0)=1$，$P(A|B)=\frac{C_{19}^{4}}{C_{20}^{4}}=\frac{4}{5}$，$P(A|B_2)=\frac{C_{15}^{4}}{C_{20}^{4}}=\frac{12}{19}$。

由全概率公式得

$$
P(A)=\sum_{i=0}^{2}P(B_i)P(A|B_i)=0.8\times1+0.1\times\frac{4}{5}+0.1\times\frac{12}{19}=0.94
$$

由贝叶斯公式

$$
(B_{0}|A)=\frac{P(B_{0})P(A|B_{0})}{P(A)}=\frac{0.8\times1}{0.94}=0.85
$$

**四、（15）**设二维随机变量![image](assets/probability-theory-028/image-037.png)的概率分布为

![image](assets/probability-theory-028/image-038.png)

![image](assets/probability-theory-028/image-039.png)            -1           0           1

-1                ![image](assets/probability-theory-028/image-040.png)          0        0.2

0        0.1        ![image](assets/probability-theory-028/image-041.png)        0.2

1         0     0.1        ![image](assets/probability-theory-028/image-042.png)

其中![image](assets/probability-theory-028/image-043.png)、![image](assets/probability-theory-028/image-044.png)、![image](assets/probability-theory-028/image-045.png)为常数，且![image](assets/probability-theory-028/image-046.png)的数学期望![image](assets/probability-theory-028/image-047.png),![image](assets/probability-theory-028/image-048.png),记![image](assets/probability-theory-028/image-049.png). 求  (1) ![image](assets/probability-theory-028/image-050.png)、![image](assets/probability-theory-028/image-051.png)、![image](assets/probability-theory-028/image-052.png)的值;   (2)![image](assets/probability-theory-028/image-053.png)的概率分布;   (3)![image](assets/probability-theory-028/image-054.png).

解    (1)由概率分布的性质可知, ![image](assets/probability-theory-028/image-055.png),即![image](assets/probability-theory-028/image-056.png).

由![image](assets/probability-theory-028/image-057.png),可得![image](assets/probability-theory-028/image-058.png).

再由![image](assets/probability-theory-028/image-059.png),解得![image](assets/probability-theory-028/image-060.png).

解以上关于![image](assets/probability-theory-028/image-061.png)、![image](assets/probability-theory-028/image-062.png)、![image](assets/probability-theory-028/image-063.png)的三个方程可得, ![image](assets/probability-theory-028/image-064.png).

(2)![image](assets/probability-theory-028/image-065.png)的所有可能取值为-2,-1,0,1,2.则

![image](assets/probability-theory-028/image-066.png)

![image](assets/probability-theory-028/image-067.png)

![image](assets/probability-theory-028/image-068.png)

![image](assets/probability-theory-028/image-069.png)

![image](assets/probability-theory-028/image-070.png)

所以![image](assets/probability-theory-028/image-071.png)的概率分布为

![image](assets/probability-theory-028/image-072.png)            -2        -1        0        1        2

![image](assets/probability-theory-028/image-073.png)            0.2       0.1      0.3       0.3      0.1

(3) ![image](assets/probability-theory-028/image-074.png).

**五、（15）**设随机变量$X$的概率密度为

![formula-object](assets/probability-theory-028/image-076.png)

令$Y=X^{2}$,$F(x,y)$为二维随机变量$(X,Y)$的分布函数.

求(1)$Y$的密度函数$f_Y(y)$;	 (2) $cov(X,Y)$;		(3) $F\left(-\frac{1}{2},4\right)$.

解    (1)$Y$的分布函数为

![formula-object](assets/probability-theory-028/image-085.png)

当$y\leq0$时, $F_y(y)=0,f_y(y)=0$.

当$0<y<1$时,

![formula-object](assets/probability-theory-028/image-089.png)

$$
f_{Y}(y)=\frac{3}{8\sqrt{y}}
$$

当![formula-object](assets/probability-theory-028/image-091.png)时,

![formula-object](assets/probability-theory-028/image-092.png)

$$
f_{Y}(y)=\frac{1}{8\sqrt{y}}
$$

当$y4$时,$F_y(y)=1,f_y'(y)=0$.

所以$Y$的概率密度为

![formula-object](assets/probability-theory-028/image-097.png)

(2)    $EX=\int_{-\infty}^{+\infty}xf_X(x)dx=\int_{-1}^{0}\frac{1}{2}xdx+\int_{0}^{1}\frac{1}{4}xdx=\frac{1}{4}$

![image](assets/probability-theory-028/image-099.png)

![image](assets/probability-theory-028/image-100.png)

故                   ![image](assets/probability-theory-028/image-101.png)

(3) ![image](assets/probability-theory-028/image-102.png)

![image](assets/probability-theory-028/image-103.png)

**六、**（10分）设供电站供应某地区1000户居民用电，各户用电情况相互独立。已知每户每天用电量（单位：度）在[0，20]上服从均匀分布。现要以0.99的概率满足该地区居民供应电量的需求，问供电站每天至少需向该地区供应多少度电？

解：设第K户居民每天用电量为$X_k$度，1000户居民每天用电量为$X$度， $EX_{k}=$10，$DX_k=\frac{20^2}{12}$=。再设供应站需供应L度电才能满足条件，则

![formula-object](assets/probability-theory-028/image-108.png)

即		$\frac{L-10000}{\sqrt{100000/3}}=2.33$，则L=10425度。

**七、**（10分）化肥厂用自动打包机装化肥，某日测得8包化肥的重量（斤）如下：

98.7  100.5  101.2  98.3  99.7  99.5  101.4  100.5

已知各包重量服从正态分布N（$\mu,\sigma^2$）

（1）是否可以认为每包平均重量为100斤（取$\alpha=0.05$）？

（2）求参数$\sigma^2$的90%置信区间。

解、需要检验的假设  $H_{0}:\mu=100$   $H_1:\mu=100$

检验统计量为$t=\frac{\overline{X}-100}{S_n/\sqrt{n-1}}$，

计算可得： $x=99.98,S_n=1.05,t=\frac{\overline{x}-\mu_0}{S_n/\sqrt{n-1}}=-0.063$

$t_{1-\frac{\alpha}{2}}(n-1)=t_{0.975}(7)=2.3646$   ，![formula-object](assets/probability-theory-028/image-118.png)  故接受原假设。

（2）$\alpha=0.1$ ，n=8    查表得$X_{0.95}^2(7)=14.067$，$X_{0.05}^2(7)=2.167$

$S_n^2=1.102$  故置信区间为

$$
\left[\frac{nS_n^2}{\chi_{1-\frac{\alpha}{2}}^2(n-1)},\frac{nS_n^2}{\chi_{\frac{\alpha}{2}}^2(n-1)}\right]=[0.548,3.559]
$$

**八、（15分）** 设总体$X$的密度函数是$f(x;\theta)=\frac{1}{2\theta}e^{-\frac{|x|}{\theta}}$，其中$\theta$>0是参数。样本$X_1,X_2,...,X_n$来自总体X。

(1)  求$\theta$的矩估计$\hat{\theta}_M$；

(2)  求$\theta$的最大似然估计$\hat{\theta}_L$；

(3)  证明$\hat{\theta}_L$是$\theta$的无偏估计，且$\hat{\theta}_L$是$\theta$的相合估计（一致估计）。

解：（1）$EX=\int_{-\infty}^{\infty}\frac{1}{2\theta}xe^{-\frac{|x|}{\theta}}dx=0$，

![formula-object](assets/probability-theory-028/image-137.png)，

$$
\hat{\sigma}_M=\sqrt{\frac{1}{2n}\sum_{i=1}^{n}X_i^2}
$$

或：![formula-object](assets/probability-theory-028/image-139.png)，![formula-object](assets/probability-theory-028/image-140.png)，$\hat{\theta}_M=\frac{S_n^*}{\sqrt{2}}$

（2）似然函数：$L=\prod_{i=1}^{n}\frac{1}{2\theta}e^{\frac{-|x_i|}{\sigma}}$，$L=\frac{1}{(2\theta)^r}e^{-\sum_{i=1}^{r}\frac{|x_i|}{a}}$，

![formula-object](assets/probability-theory-028/image-144.png)

![formula-object](assets/probability-theory-028/image-145.png)，

令，$-\frac{n}{\hat{\theta}}+\frac{1}{\hat{\theta}^{2}}\sum_{i=1}^{n}|x_i|=0$，$\hat{\theta}_L=\frac{1}{n}\sum_{i=1}^{n}|X_i|$

（3）![formula-object](assets/probability-theory-028/image-148.png)

$E\hat{\theta}_L=\frac{1}{n}\sum_{i=1}^{n}E|X_i|=E|X|=\theta$，$\hat{\theta}_L$是$\theta$的无偏估计，

$E[X]^2=EX^2=2\theta^2$，

$D[X]=EX^2-(EX)^2=2\theta^2-\theta^2=\theta^2$，![formula-object](assets/probability-theory-028/image-154.png)

$P\left[\hat{\theta}_{L}-E\hat{\theta}_{L}<\varepsilon\right]\leq\frac{\sigma^{2}}{ne^{\varepsilon}}\rightarrow0$，$\hat{\theta}_L$是$\theta$的相合估计
