---
source_id: engineering-mathematical-analysis-2-033
course_id: engineering_math_analysis_2
title: "2018级工科数学分析（二）B附解答"
original_file: "学科资料/工科数学分析II/往年卷/2018级工科数学分析（二）B附解答.doc"
document_role: past_exam_answer
year: 2018
locator_type: none
---

# 2018级工科数学分析（二）B附解答

![image](assets/engineering-mathematical-analysis-2-033/image-001.png)**诚信应考，考试作弊将带来严重后果！**

**华南理工大学本科生期末考试**

**《工科数学分析（二）》B卷**

**2018-2019学年第二学期**

**注意事项：1.** **开考前请将密封线内各项信息填写清楚；**

**2.** **所有答案请直接答在试卷上；**

**3．考试形式：闭卷；**

**4.** **本试卷共5大题，满分100分，考试时间120分钟**。

| **题 号** | **一** | **二** | **三** | **四** | **五** | **总分** |
|---|---|---|---|---|---|---|
| **得 分** |  |  |  |  |  |  |

评阅教师请在试卷袋上评阅栏签名

**一、填空题**（每小题3分，共15分）**.**
1. 设函数$u(x,y,z)=\sqrt{x^{2}+y^{2}+z^{2}}$,  则$div(gradu)=$$\frac{2}{\sqrt{x^{2}+y^{2}+z^{2}}}$；
1. 交换积分次序，则$\int_0^2dy\int_{y^2}^4f(x,y)dx=$![formula-object](assets/engineering-mathematical-analysis-2-033/image-006.png)；
1. 设曲线$L:\frac{x^{2}}{a^{2}}+\frac{y^{2}}{b^{2}}=1$，取顺时针方向，则$\int_L(x-y)dx+(x+y)dy=$![formula-object](assets/engineering-mathematical-analysis-2-033/image-009.png)；
1. 若级数$\sum_{n=1}^\infty\frac{(-1)^n(n+2)}{n^p}$条件收敛，则常数$p$的取值范围为![formula-object](assets/engineering-mathematical-analysis-2-033/image-012.png)；
1. 设$f(x)=\begin{cases}-1,&-1<x\leq0\\x^2+2,&0<x\leq1\end{cases}$，设![formula-object](assets/engineering-mathematical-analysis-2-033/image-014.png)为$f(x)$的展成以$2$为周期的傅里叶（Fourier）级数的和函数，则$S(0)=$$\frac{1}{2}$.

**二、计算题**（每小题9分，共36分）**.**
1. 设$u=f(x+y+z,x^2+y^2+z^2)$,  其中函数$f$有二阶连续的偏导数, 求$\frac{\partial^2u}{\partial x^2}+\frac{\partial^2u}{\partial y^2}+\frac{\partial^2u}{\partial z^2}$.

解：              ![formula-object](assets/engineering-mathematical-analysis-2-033/image-022.png)             ……2分

$\frac{\partial^2u}{\partial x^2}=f_{11}''+4xf_{12}''+4x^2f_{22}''+2f_2'$     ……8分

同理得到    $\frac{\partial^2u}{\partial y^2}=f_{11}''+4yf_{12}''+4y^2f_{22}''+2f_2'$     $\frac{\partial^2u}{\partial z^2}=f_{11}''+4zf_{12}''+4z^2f_{22}''+2f_2'$

所以$\frac{\partial^{2}u}{\partial x^{2}}+\frac{\partial^{2}u}{\partial y^{2}}+\frac{\partial^{2}u}{\partial z^{2}}=3f_{11}''+4(x+y+z)f_{12}''+4(x^{2}+y^{2}+z^{2})f_{22}''+6f_2'$   ……9分

2.    计算三重积分$\iiint_{\Omega}\left(\frac{x}{2}-y-z\right)^2dxdydz$，其中![formula-object](assets/engineering-mathematical-analysis-2-033/image-028.png)是曲面$\frac{x^2}{4}+y^2+z^2=1$所围成的区域.

解：（1）利用对称性，得到![formula-object](assets/engineering-mathematical-analysis-2-033/image-030.png)

**于是**$\iiint_\Omega\left(\frac{x}{2}-y-z\right)^2dxdydz=\iiint_\Omega\left(\frac{x^2}{4}+y^2+z^2\right)dxdydz$     ……3分

（2）利用广义球面坐标变换![formula-object](assets/engineering-mathematical-analysis-2-033/image-032.png)    ……5分

边界：$r=1$

所以$\iiint_\Omega\left(\frac{x}{2}-y-z\right)^2dxdydz=\iiint_\Omega\left(\frac{x^2}{4}+y^2+z^2\right)dxdydz$

![formula-object](assets/engineering-mathematical-analysis-2-033/image-035.png)          ……8分

$8\pi=\frac{5}{5}$                                 ……9分

3.    求抛物面$\sum:z=2-\left(x^2+y^2\right)$的质量（$z_0$的部分），其密度函数为$\rho(x,y,z)=x^{2}+y^{2}$.

解：$\sum:z=2-\left(x^2+y^2\right)$，$dS=\sqrt{1+4x^{2}+4y^{2}}dxdy$，$D_{xy}:x^{2}+y^{2}\leq2$            ……2分

$M=\iint_{\Sigma}\left(x^2+y^2\right)dS$                  ……4分

$=\iint_{D_{xy}}(x^{2}+y^{2})\sqrt{1+4x^{2}+4y^{2}}dxdy$  ……5分

![formula-object](assets/engineering-mathematical-analysis-2-033/image-045.png)        ……8分

$\frac{149\pi}{30}$                           ……9分

<!-- question: engineering-mathematical-analysis-2-033-Q1 -->

4.  求微分方程$x(2+y)dx+y(1-x)dy=0$的通解.

解：原方程化为：    $\frac{ydy}{2+y}=\frac{xdx}{x-1}$      ……4分

两边积分得到原方程的通解为：$(x-1)(y+2)^{2}=Ce^{y-x}$     ……9分

**三、解答题**（每小题10分，共30分）**.**

1.  设曲线积分![formula-object](assets/engineering-mathematical-analysis-2-033/image-050.png)与积分路径无关,  其中$\phi(x)$有一阶连续导数且$\varphi\left(\frac{\pi}{2}\right)=0$,  求$\phi(x)$，并计算曲线积分![formula-object](assets/engineering-mathematical-analysis-2-033/image-054.png).

解：（1）选![formula-object](assets/engineering-mathematical-analysis-2-033/image-055.png)为右半平面，则![formula-object](assets/engineering-mathematical-analysis-2-033/image-056.png)是单连通的，![formula-object](assets/engineering-mathematical-analysis-2-033/image-057.png)在![formula-object](assets/engineering-mathematical-analysis-2-033/image-058.png)内有一阶连续偏导数，又曲线积分![formula-object](assets/engineering-mathematical-analysis-2-033/image-059.png)与积分路径无关，则$\frac{\partial Q}{\partial x}=\frac{\partial P}{\partial y}$  ……3

即，![formula-object](assets/engineering-mathematical-analysis-2-033/image-061.png)，        ……5分

解得![formula-object](assets/engineering-mathematical-analysis-2-033/image-062.png)，又$\varphi\left(\frac{\pi}{2}\right)=0$，所以![formula-object](assets/engineering-mathematical-analysis-2-033/image-064.png)    ……7分

（2）![formula-object](assets/engineering-mathematical-analysis-2-033/image-065.png)     ……10分

2.  计算![formula-object](assets/engineering-mathematical-analysis-2-033/image-066.png)，![formula-object](assets/engineering-mathematical-analysis-2-033/image-067.png)为有界单连通区域的闭边界曲面，取外侧.

解：记![formula-object](assets/engineering-mathematical-analysis-2-033/image-068.png)围成的区域为![formula-object](assets/engineering-mathematical-analysis-2-033/image-069.png)。

$$
P=\frac{x}{(x^{2}+y^{2}+z^{2})^{3/2}},Q=\frac{y}{(x^{2}+y^{2}+z^{2})^{3/2}},R=\frac{z}{(x^{2}+y^{2}+z^{2})^{3/2}}
$$

$\frac{\partial P}{\partial x}+\frac{\partial Q}{\partial y}+\frac{\partial R}{\partial z}=0,((x,y,z)\neq(0,0,0))$    ……2分

（1）当$(0,0,0)\notin\Omega$时，$P,Q,R$在![formula-object](assets/engineering-mathematical-analysis-2-033/image-074.png)内有一阶连续偏导数，从而利用Gausse公式，得到

$I=\iint_{\Sigma}\frac{xdydz+ydzdx+zdxdy}{(x^2+y^2+z^2)^{3/2}}=0$           ……4分

（2）当$(0,0,0)\in\Omega$时，在![formula-object](assets/engineering-mathematical-analysis-2-033/image-077.png)内作$\sum_{\varepsilon}^{-}:x^{2}+y^{2}+z^{2}=\varepsilon^{2}$，取内侧，记![formula-object](assets/engineering-mathematical-analysis-2-033/image-079.png)围成的区域为![formula-object](assets/engineering-mathematical-analysis-2-033/image-080.png)，则

$P,Q,R$在$\Omega-\Omega_\varepsilon$内有一阶连续偏导数，从而利用Gausse公式，得到

$I=\iint_{\Sigma+\Sigma_\varepsilon^-}\frac{xdydz+ydzdx+zdxdy}{(x^2+y^2+z^2)^{3/2}}-\iint_{\Sigma_\varepsilon^-}\frac{xdydz+ydzdx+zdxdy}{(x^2+y^2+z^2)^{3/2}}$            ……6分

$=0+\frac{1}{\varepsilon^{3}}\iiint_{\Sigma_{\varepsilon}}xdydz+ydzdx+zdxdy$         ……9分

$=\frac{1}{\varepsilon^{3}}\iiint_{\Omega_{\varepsilon}}3dxdydz=4\pi$         ……10分

3.    求幂级数$\sum_{n=0}^{\infty}\frac{3n+1}{n!}x^{3n}$的收敛域及和函数.

解：（1）记$a_n=\frac{3n+1}{n!}$，因为$\lim_{n\to\infty}\frac{a_{n+1}}{a_n}=\lim_{n\to\infty}\frac{3(n+1)+1}{(n+1)!}\cdot\frac{n!}{3n+1}=0$     ……2分

所以，原幂级数的收敛半径为$R=+\infty$，收敛域为$(-\infty,+\infty)$。    ……4分

<!-- question: engineering-mathematical-analysis-2-033-Q2 -->

（2）利用$e^x=\sum_{n=0}^\infty\frac{x^n}{n!}$，

得到

$s(x)=\sum_{n=0}^{\infty}\frac{3n+1}{n!}x^{3n}=\sum_{n=0}^{\infty}\frac{3n}{n!}x^{3n}+\sum_{n=0}^{\infty}\frac{(x^{3})^{n}}{n!}$     ……6分

$=3x^{3}\sum_{n=1}^{\infty}\frac{x^{3(n-1)}}{(n-1)!}+e^{x^{3}}$       ……8分

![formula-object](assets/engineering-mathematical-analysis-2-033/image-094.png)   ……10分

**四、证明题**（本题10分）**.**

证明函数项级数![formula-object](assets/engineering-mathematical-analysis-2-033/image-095.png)在$(-\infty,+\infty)$上一致收敛.

证明：因为![formula-object](assets/engineering-mathematical-analysis-2-033/image-097.png)，    ……6分

又$\sum_{n=1}^{\infty}\frac{1}{n^{2}}$收敛，      ……8分

所以，利用优级数判别法（M判别法）知道，

数项级数![formula-object](assets/engineering-mathematical-analysis-2-033/image-099.png)在$(-\infty,+\infty)$上一致收敛。……10分

**五、应用题**（本题9分）**.**

欲造一无盖的长方体容器，已知底部造价为每平方米3元，侧面造价均为每平方米1元，现想用36元造一个容积最大的容器，求它的尺寸.

解:设长方体的长宽高分别为$x$米，$y$米，![formula-object](assets/engineering-mathematical-analysis-2-033/image-103.png)米，

问题为求$V=xyz$在约束条件：$3xy+2(yz+xz)=36$下的最大值。……2分

令![formula-object](assets/engineering-mathematical-analysis-2-033/image-106.png)    ……4分

令

![formula-object](assets/engineering-mathematical-analysis-2-033/image-107.png)         ……8分

解得$\begin{cases}x=2\\y=2\\z=3\end{cases}$      （唯一）

又根据实际问题，所求的最大体积存在，从而，

所求的长宽高分别为2米，2米，3米时体积最大。……10分
