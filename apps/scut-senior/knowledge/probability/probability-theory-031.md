---
source_id: probability-theory-031
course_id: probability_theory
title: "2014春A卷答案"
original_file: "学科资料/概率论/往年卷/2014春A卷答案.docx"
document_role: past_exam_answer
year: 2014
locator_type: none
---

# 2014春A卷答案

**![image](assets/probability-theory-031/image-001.png)诚信应考，考试作弊将带来严重后果！**

**华南理工大学本科生期末考试**

**《概率论与数理统计》A卷**

**注意事项：1. 开考前请将密封线内各项信息填写清楚；**

**2. 所有答案请直接答在试卷上；**

**3．考试形式：闭卷；**

**4. 本试卷共八大题，满分100分，**	**考试时间120分钟**。

| **题 号** | **一** | **二** | **三** | **四** | **五** | **六** | **七** | **八** | **总分** |
|---|---|---|---|---|---|---|---|---|---|
| **得 分** |  |  |  |  |  |  |  |  |  |

**注意：** **$\Phi(1.67)=0.9525\quad\Phi(1.96)=0.975\quad\Phi(1.45)=0.926$**

$$
t_{0.975}(15)=2.132,t_{0.95}(16)=1.746,t_{0.99}(15)=1.753
$$

![formula-object](assets/probability-theory-031/image-004.png)

**一、（12分）**设有n个人排成一行，甲与乙是其中的两个人，求这n个人的任意排列中，甲与乙之间恰有r个人的概率。如果这n个人围成一圈，试证明甲与乙之间恰有r个人的概率与r无关。(甲到乙是顺时针)

解：

![formula-object](assets/probability-theory-031/image-005.png)

**二、（10分）** 甲、乙、丙三车间加工同一产品，加工量分别占总量的25%、35%、40%，次品率分别为0.03、0.02、0.01。现从所有的产品中抽取一个产品，试求

<!-- question: probability-theory-031-Q1 -->

（1）该产品是次品的概率；

<!-- question: probability-theory-031-Q2 -->

（2）若检查结果显示该产品是次品，则该产品是乙车间生产的概率是多少？

解：设$A_1$，$A_{2}$，$A_3$表示甲乙丙三车间加工的产品，B表示此产品是次品。

（1）所求事件的概率为$P(B)=P(A_1)P(B|A_1)+P(A_2)P(B|A_2)+P(A_3)P(B|A_3)$$=0.25\times0.03+0.35\times0.02+0.4\times0.01=0.0185$

（2）$P(A_2|B)=\frac{P(A_2)P(B|A_2)}{P(B)}=\frac{0.35\times0.02}{0.0185}=0.38$

**三、** **(10分)** 假设一部机器在一天内发生故障的概率为0.2，机器发生故障时全天停止工作，若一周5个工作日里无故障，可获利润10万元；发生一次故障可获利润5万元；发生二次故障所获利润0元；发生三次或三次以上故障就要亏损2万元，求一周内期望利润是多少？

解  由条件知![formula-object](assets/probability-theory-031/image-012.png)，即$P\{X=k\}=\binom{5}{k}0.2^{k}0.8^{5-k},k=0,1,\cdots,5$

$$
Y=g(X)=\begin{cases}10,&X=0;\\5,&X=1;\\0,&X=2;\\-2,&X=3\end{cases}
$$

![formula-object](assets/probability-theory-031/image-015.png)

**四、(15分)**  设随机变量![image](assets/probability-theory-031/image-016.png)和![image](assets/probability-theory-031/image-017.png)的联合分布在以点![image](assets/probability-theory-031/image-018.png)为顶点的三角形区域上服从均匀分布,试求 (1)    关于X的边缘密度

<!-- question: probability-theory-031-Q3 -->

(2)  X和Y的协方差

(3)    随机变量![image](assets/probability-theory-031/image-019.png)的方差.

**解**  三角形区域为![image](assets/probability-theory-031/image-020.png);随机变量![image](assets/probability-theory-031/image-021.png)和![image](assets/probability-theory-031/image-022.png)的联合密度为

![image](assets/probability-theory-031/image-023.png)

以![image](assets/probability-theory-031/image-024.png)表示![image](assets/probability-theory-031/image-025.png)的概率密度,则当![image](assets/probability-theory-031/image-026.png)或![image](assets/probability-theory-031/image-027.png)时, ![image](assets/probability-theory-031/image-028.png);当![image](assets/probability-theory-031/image-029.png)时,有

![image](assets/probability-theory-031/image-030.png)

因此                 ![image](assets/probability-theory-031/image-031.png)

![image](assets/probability-theory-031/image-032.png)

同理可得, ![image](assets/probability-theory-031/image-033.png).

现在求![image](assets/probability-theory-031/image-034.png)和![image](assets/probability-theory-031/image-035.png)的协方差

![image](assets/probability-theory-031/image-036.png)

![image](assets/probability-theory-031/image-037.png)

于是      ![image](assets/probability-theory-031/image-038.png)

**五、（12）**向一目标射击，目标中心为坐标原点，已知命中点的横坐标![image](assets/probability-theory-031/image-039.png)和纵坐标![image](assets/probability-theory-031/image-040.png)相互独立，且均服从$N(0,2^{2})$分布.  求

<!-- question: probability-theory-031-Q4 -->

（1）命中环形区域$D=\{(x,y)|sx^2+y^2s2\}$的概率；

<!-- question: probability-theory-031-Q5 -->

（2）命中点到目标中心距离$Z=\sqrt{X^{2}+Y^{2}}$的数学期望.

解：                  （1）![image](assets/probability-theory-031/image-044.png)

![image](assets/probability-theory-031/image-045.png)

![image](assets/probability-theory-031/image-046.png)

<!-- question: probability-theory-031-Q6 -->

（2）![image](assets/probability-theory-031/image-047.png)

![image](assets/probability-theory-031/image-048.png)

![image](assets/probability-theory-031/image-049.png).

**六、（10分）**某种电子器件的寿命(小时)具有数学期望$mu$(未知),方差$\sigma^2=400$.为了估计$mu$,随机地取$n$只这种器件,在时刻$t=0$投入测试(设测试是相互独立的)直到失败,测得寿命为$X_1,X_2,...,X_n$,以$\overline{X}=\frac{1}{n}\sum_{i=1}^{n}X_i$作为$mu$的估计,为了使$P\{\vert\bar{X}-\mu\vert<1\}0.95$,问$n$至少为多少?

**解、**  由于$X_1,X_2,...,X_n$独立同分布,且$EX_=\mu,DX_=\sigma^2=400$.

由林德伯格-列维定理得

$$
P\{\overline{X}-\mu<1\}=P\left\{\frac{\left|\overline{X}-\mu\right|}{\sqrt{\sigma^{2}/n}}<\frac{1}{\sqrt{\sigma^{2}/n}}\right\}\approx\Phi\left(\frac{\sqrt{n}}{\sigma}\right)-\Phi\left(-\frac{\sqrt{n}}{\sigma}\right)
$$

$$
=2\Phi\left(\frac{\sqrt{n}}{\sigma}\right)-1=2\Phi\left(\frac{\sqrt{n}}{20}\right)-1.0.95
$$

即$\Phi\left(\frac{\sqrt{n}}{20}\right)^{0.975}$,查表得$\frac{\sqrt{n}}{20}1.96$,故$n400\times1.96^2=1536.64$.

因此$n$至少为1537.

**七、（10分）**

**(1)** 设某机器生产的零件长度（单位：cm）![image](assets/probability-theory-031/image-068.png)，今抽取容量为16的样本，测得样本均值![image](assets/probability-theory-031/image-069.png)，样本方差![image](assets/probability-theory-031/image-070.png). 求![image](assets/probability-theory-031/image-071.png)的置信度为0.95的置信区间.

**(2)** 某涤纶厂的生产的维尼纶的纤度（纤维的粗细程度）在正常生产的条件下，服从正态分布N(1.405 , 0.0482)，某日随机地抽取5根纤维，测得纤度为

1.32  ，1.55  ，1.36  ，1.40  ，1.44

问一天涤纶纤度总体X的均方差是否正常（α=0.05）**?**

解：（1）![image](assets/probability-theory-031/image-072.png)的置信度为![image](assets/probability-theory-031/image-073.png)下的置信区间为

$$
\left(\bar{X}-\frac{S}{\sqrt{n-1}}t_{\frac{\alpha}{2}}(n-1),\quad\bar{X}+\frac{S}{\sqrt{n-1}}t_{\frac{\alpha}{2}}(n-1)\right)
$$

$$
x=10,s=0.4,n=16,a=0.05,t_{0.975}(15)=2.132
$$

所以![image](assets/probability-theory-031/image-076.png)的置信度为0.95的置信区间为（9.7868，10.2132）

(2)

![formula-object](assets/probability-theory-031/image-077.png)

**八、（21分）**  设总体$X$的概率密度为

![formula-object](assets/probability-theory-031/image-079.png)

其中$\theta>0$是未知参数,从总体$X$中抽取简单随机样本$X_1,X_2,...,X_n$,记

$$
\hat{\theta}=\min(X_1,X_2,\cdots,X_n)
$$

求:(1)  总体$X$的分布函数$F(x)$;(2)统计量$\hat{\theta}$的分布函数$F_{\hat{\theta}}(x)$;(3)如果用$\hat{\theta}$作为$\theta$的估计量,讨论它是否具有无偏性.  (4)计算$\hat{\theta}$的方差$Var[θ]$.

**解**    (1)              $F(x)=\int_{x}^{t}f(t)dt=\begin{cases}1-e^{-2(x-\theta)}&x>\theta\\0&x\leq\theta\end{cases}$

(2)  ![formula-object](assets/probability-theory-031/image-093.png)

$$
=1-P\{min(X_1,X_2,...,X_n)>x\}=1-P\{X_1>x,X_2>x,...,X_n>x\}
$$

![formula-object](assets/probability-theory-031/image-095.png)

<!-- question: probability-theory-031-Q7 -->

(3)  $\hat{\theta}$的概率密度为

![formula-object](assets/probability-theory-031/image-097.png)

因为        $E\hat{\theta}=\int_{-\infty}^{+\infty}xf_\theta(x)dx=\int_{\theta}^{+\infty}2nxe^{-2n(x-\theta)}dx=\theta+\frac{1}{2n}\neq\theta$

所以$\hat{\theta}$作为$\theta$的估计量不具有无偏性.

(4)

![formula-object](assets/probability-theory-031/image-101.png)
