# 大学物理期末总复习

> [!info]
> 适用范围：质点运动学、质点动力学、三大守恒定律、刚体力学、机械振动、机械波、光的干涉、光的衍射、光的偏振、气体动理论、热力学第一定律、热力学第二定律。  
> 所有重要公式均采用独立数学块，便于在 Obsidian 中渲染。

---

# 0. 期末复习总览

根据期末复习资料，计算题重点集中在四类：

1. **质点平动与刚体转动综合**
2. **根据波形图写振动方程、波动方程**
3. **光栅衍射：光栅常数、缺级、最大级次、谱线重叠**
4. **热力学：等值过程、绝热过程、循环过程**

> [!important]
> 建议优先掌握上面四类计算题，再复习选择题和填空题中的概念辨析。

---

# 1. 质点运动学

## 1.1 位置、位移与路程

位置矢量：

$$
\vec r=x\vec i+y\vec j+z\vec k
$$

位移：

$$
\Delta \vec r=\vec r_2-\vec r_1
$$

路程是实际运动轨迹的长度，记为：

$$
s
$$

注意：

- 位移是矢量；
- 路程是标量；
- 路程一般不等于位移的大小。

## 1.2 速度与速率

平均速度：

$$
\bar{\vec v}=\frac{\Delta \vec r}{\Delta t}
$$

瞬时速度：

$$
\vec v=\frac{d\vec r}{dt}
$$

速率：

$$
v=\frac{ds}{dt}=|\vec v|
$$

> [!warning]
> 一般情况下：
>
> $$
> \frac{d|\vec r|}{dt}\neq \left|\frac{d\vec r}{dt}\right|
> $$

## 1.3 加速度

平均加速度：

$$
\bar{\vec a}=\frac{\Delta \vec v}{\Delta t}
$$

瞬时加速度：

$$
\vec a=\frac{d\vec v}{dt}=\frac{d^2\vec r}{dt^2}
$$

曲线运动中：

$$
\vec a=a_\tau \vec e_\tau+a_n\vec e_n
$$

切向加速度：

$$
a_\tau=\frac{dv}{dt}
$$

法向加速度：

$$
a_n=\frac{v^2}{R}
$$

总加速度大小：

$$
a=\sqrt{a_\tau^2+a_n^2}
$$

其中：

- $a_\tau$ 改变速度大小；
- $a_n$ 改变速度方向。

## 1.4 圆周运动

角速度：

$$
\omega=\frac{d\theta}{dt}
$$

角加速度：

$$
\alpha=\frac{d\omega}{dt}
$$

线速度：

$$
v=\omega R
$$

切向加速度：

$$
a_\tau=\alpha R
$$

法向加速度：

$$
a_n=\frac{v^2}{R}=\omega^2R
$$

> [!note]
> “向心力”不是一种新的力，而是所有实际力在法向方向上的合力：
>
> $$
> \sum F_n=m\frac{v^2}{R}=m\omega^2R
> $$

---

# 2. 质点动力学

## 2.1 牛顿第二定律

矢量形式：

$$
\sum \vec F=m\vec a
$$

分量形式：

$$
\sum F_x=ma_x
$$

$$
\sum F_y=ma_y
$$

$$
\sum F_z=ma_z
$$

标准步骤：

1. 选研究对象；
2. 画受力图；
3. 建立坐标系；
4. 分解各个力；
5. 列牛顿第二定律；
6. 补充运动学或几何约束。

## 2.2 常见力

重力：

$$
\vec G=m\vec g
$$

弹簧弹力：

$$
F=-kx
$$

滑动摩擦力：

$$
f_k=\mu_kN
$$

静摩擦力：

$$
0\leq f_s\leq \mu_sN
$$

最大静摩擦力：

$$
f_{s,\max}=\mu_sN
$$

> [!warning]
> 静摩擦力不一定等于 $\mu_sN$，只有在即将相对滑动时才取最大值。

---

# 3. 冲量、动量与能量

## 3.1 动量与冲量

动量：

$$
\vec p=m\vec v
$$

冲量：

$$
\vec I=\int_{t_1}^{t_2}\vec F\,dt
$$

恒力冲量：

$$
\vec I=\vec F\Delta t
$$

动量定理：

$$
\vec I=\Delta \vec p
$$

即：

$$
\int_{t_1}^{t_2}\vec F\,dt=m\vec v_2-m\vec v_1
$$

## 3.2 动量守恒

若系统所受合外力为零，或外力冲量可忽略，则：

$$
\vec P_1=\vec P_2
$$

即：

$$
\sum_i m_i\vec v_{i1}=\sum_i m_i\vec v_{i2}
$$

> [!note]
> 动量可以分方向守恒。某一方向外力冲量为零，该方向动量守恒。

## 3.3 功

恒力做功：

$$
A=\vec F\cdot \vec s=Fs\cos\theta
$$

变力做功：

$$
A=\int \vec F\cdot d\vec r
$$

沿 $x$ 轴：

$$
A=\int_{x_1}^{x_2}F_x\,dx
$$

## 3.4 动能定理

动能：

$$
E_k=\frac{1}{2}mv^2
$$

动能定理：

$$
A_{\text{合}}=\Delta E_k
$$

即：

$$
A_{\text{合}}=\frac{1}{2}mv_2^2-\frac{1}{2}mv_1^2
$$

## 3.5 势能与机械能

重力势能：

$$
E_{p,g}=mgh
$$

弹性势能：

$$
E_{p,s}=\frac{1}{2}kx^2
$$

保守力做功：

$$
A_{\text{保}}=-\Delta E_p
$$

机械能：

$$
E=E_k+E_p
$$

只有保守力做功时：

$$
E_{k1}+E_{p1}=E_{k2}+E_{p2}
$$

有非保守力做功时：

$$
A_{\text{非保}}=\Delta(E_k+E_p)
$$

> [!warning]
> 物体到达最远位置时：
>
> $$
> v=0
> $$
>
> 但不一定有：
>
> $$
> F_{\text{合}}=0
> $$

---

# 4. 刚体力学

## 4.1 线量与角量

角速度：

$$
\omega=\frac{d\theta}{dt}
$$

角加速度：

$$
\alpha=\frac{d\omega}{dt}
$$

线速度：

$$
\vec v=\vec\omega\times\vec r
$$

大小：

$$
v=\omega r
$$

切向加速度：

$$
a_\tau=\alpha r
$$

法向加速度：

$$
a_n=\omega^2r
$$

## 4.2 力矩

力矩：

$$
\vec M=\vec r\times \vec F
$$

大小：

$$
M=rF\sin\theta
$$

也可以写成：

$$
M=Fd
$$

其中 $d$ 是力臂。

## 4.3 转动惯量

离散质点系：

$$
J=\sum_i m_ir_i^2
$$

连续刚体：

$$
J=\int r^2\,dm
$$

常见结果：

质点：

$$
J=mr^2
$$

细杆绕中心垂直轴：

$$
J=\frac{1}{12}Ml^2
$$

细杆绕端点垂直轴：

$$
J=\frac{1}{3}Ml^2
$$

圆盘绕中心轴：

$$
J=\frac{1}{2}MR^2
$$

圆环绕中心轴：

$$
J=MR^2
$$

## 4.4 刚体定轴转动定律

$$
\sum M=J\alpha
$$

它对应质点平动中的：

$$
\sum F=ma
$$

## 4.5 角动量

质点对固定点的角动量：

$$
\vec L=\vec r\times\vec p
$$

大小：

$$
L=rmv\sin\theta
$$

刚体定轴转动角动量：

$$
L=J\omega
$$

## 4.6 角动量定理与守恒

角动量定理：

$$
\int_{t_1}^{t_2}M_{\text{外}}\,dt=L_2-L_1
$$

微分形式：

$$
M_{\text{外}}=\frac{dL}{dt}
$$

若对所选转轴的合外力矩为零：

$$
L_1=L_2
$$

## 4.7 转动功与转动动能

力矩做功：

$$
A=\int_{\theta_1}^{\theta_2}M\,d\theta
$$

转动动能：

$$
E_{k,\text{转}}=\frac{1}{2}J\omega^2
$$

转动动能定理：

$$
\int_{\theta_1}^{\theta_2}M\,d\theta
=
\frac{1}{2}J\omega_2^2-\frac{1}{2}J\omega_1^2
$$

## 4.8 子弹击杆类题目

### 阶段一：碰撞

对转轴使用角动量守恒：

$$
L_{\text{碰前}}=L_{\text{碰后}}
$$

若子弹质量为 $m$，速度为 $v$，击中距轴 $l$ 的位置并留在杆上：

$$
mvl=\left(J_{\text{杆}}+ml^2\right)\omega_0
$$

所以：

$$
\omega_0=
\frac{mvl}{J_{\text{杆}}+ml^2}
$$

> [!warning]
> 碰撞阶段通常机械能不守恒。

### 阶段二：受阻力矩减速

方法一：

$$
-M_r=J_{\text{总}}\alpha
$$

再用：

$$
\omega^2-\omega_0^2=2\alpha\theta
$$

方法二：

$$
-M_r\theta
=
0-\frac{1}{2}J_{\text{总}}\omega_0^2
$$

## 4.9 滑轮综合题

对物块：

$$
\sum F=ma
$$

对滑轮：

$$
(T_2-T_1)R=J\alpha
$$

无滑动条件：

$$
a=\alpha R
$$

> [!warning]
> 有质量滑轮两侧拉力通常不相等：
>
> $$
> T_1\neq T_2
> $$

---

# 5. 机械振动

## 5.1 简谐振动判据

回复力：

$$
F=-kx
$$

加速度：

$$
a=-\omega^2x
$$

动力学方程：

$$
\frac{d^2x}{dt^2}+\omega^2x=0
$$

运动方程：

$$
x=A\cos(\omega t+\varphi)
$$

## 5.2 周期、频率与圆频率

$$
T=\frac{2\pi}{\omega}
$$

$$
\nu=\frac{1}{T}
$$

$$
\omega=2\pi\nu
$$

弹簧振子：

$$
\omega=\sqrt{\frac{k}{m}}
$$

$$
T=2\pi\sqrt{\frac{m}{k}}
$$

## 5.3 速度与加速度

位移：

$$
x=A\cos(\omega t+\varphi)
$$

速度：

$$
v=-A\omega\sin(\omega t+\varphi)
$$

加速度：

$$
a=-A\omega^2\cos(\omega t+\varphi)
$$

因此：

$$
a=-\omega^2x
$$

最大速度：

$$
v_{\max}=A\omega
$$

最大加速度：

$$
a_{\max}=A\omega^2
$$

## 5.4 根据初始条件求初相

在 $t=0$ 时：

$$
x_0=A\cos\varphi
$$

$$
v_0=-A\omega\sin\varphi
$$

所以：

$$
\cos\varphi=\frac{x_0}{A}
$$

$$
\sin\varphi=-\frac{v_0}{A\omega}
$$

必须结合 $x_0$ 和 $v_0$ 的正负判断象限。

## 5.5 简谐振动能量

总机械能：

$$
E=\frac{1}{2}kA^2
$$

也可写为：

$$
E=\frac{1}{2}m\omega^2A^2
$$

势能：

$$
E_p=\frac{1}{2}kx^2
$$

动能：

$$
E_k=\frac{1}{2}m\omega^2(A^2-x^2)
$$

结论：

- 平衡位置：速度最大，动能最大；
- 端点：速度为零，势能最大；
- 总机械能不变。

## 5.6 同方向同频率振动合成

$$
x_1=A_1\cos(\omega t+\varphi_1)
$$

$$
x_2=A_2\cos(\omega t+\varphi_2)
$$

合振动：

$$
x=A\cos(\omega t+\varphi)
$$

合振幅：

$$
A=
\sqrt{
A_1^2+A_2^2+
2A_1A_2\cos(\varphi_2-\varphi_1)
}
$$

同相：

$$
A=A_1+A_2
$$

反相：

$$
A=|A_1-A_2|
$$

相位差为 $\pi/2$：

$$
A=\sqrt{A_1^2+A_2^2}
$$

---

# 6. 机械波

## 6.1 基本关系

$$
u=\lambda\nu
$$

$$
u=\frac{\lambda}{T}
$$

$$
\omega=2\pi\nu=\frac{2\pi}{T}
$$

$$
k=\frac{2\pi}{\lambda}
$$

> [!note]
> 波传播的是振动状态和能量，介质质点并不随波整体向前运动。

## 6.2 波动方程

若参考点 $x_0$ 的振动方程为：

$$
y_0=A\cos(\omega t+\varphi_0)
$$

沿 $+x$ 方向传播：

$$
y=
A\cos
\left[
\omega t-
\frac{2\pi}{\lambda}(x-x_0)+\varphi_0
\right]
$$

沿 $-x$ 方向传播：

$$
y=
A\cos
\left[
\omega t+
\frac{2\pi}{\lambda}(x-x_0)+\varphi_0
\right]
$$

记忆：

> 时间项写成正号时，空间项“减号向右，加号向左”。

## 6.3 根据波形图判断质点运动方向

沿 $+x$ 方向传播：

$$
\frac{\partial y}{\partial t}
=
-u\frac{\partial y}{\partial x}
$$

因此：

- 斜率为正，质点向下；
- 斜率为负，质点向上。

沿 $-x$ 方向传播：

$$
\frac{\partial y}{\partial t}
=
u\frac{\partial y}{\partial x}
$$

此时质点速度方向与波形斜率符号相同。

## 6.4 相位差与波程差

一般相位差：

$$
\Delta\varphi
=
\varphi_{20}-\varphi_{10}
-
\frac{2\pi}{\lambda}(r_2-r_1)
$$

若两波源初相相同：

$$
\Delta\varphi
=
-\frac{2\pi}{\lambda}\Delta r
$$

## 6.5 波的干涉

相干条件：

1. 频率相同；
2. 振动方向相同；
3. 相位差恒定。

相长干涉：

$$
\Delta\varphi=2k\pi
$$

相消干涉：

$$
\Delta\varphi=(2k+1)\pi
$$

若两波源同相，相长条件：

$$
\Delta r=k\lambda
$$

相消条件：

$$
\Delta r=
\left(k+\frac{1}{2}\right)\lambda
$$

## 6.6 反射与驻波

固定端反射：

$$
\Delta\varphi=\pi
$$

自由端反射：无 $\pi$ 相变。

驻波中：

相邻波节距离：

$$
\frac{\lambda}{2}
$$

相邻波腹距离：

$$
\frac{\lambda}{2}
$$

相邻波节与波腹距离：

$$
\frac{\lambda}{4}
$$

## 6.7 多普勒效应

$$
\nu'=
\frac{u\pm v_o}{u\mp v_s}\nu
$$

符号原则：

- 观察者向波源：分子加；
- 观察者远离波源：分子减；
- 波源向观察者：分母减；
- 波源远离观察者：分母加。

结论：

> 相互接近，接收频率增大；相互远离，接收频率减小。

---

# 7. 光的干涉

## 7.1 光程

光程：

$$
L=nr
$$

光程差：

$$
\delta=L_2-L_1
$$

相位差：

$$
\Delta\varphi=\frac{2\pi}{\lambda}\delta
$$

## 7.2 杨氏双缝干涉

光程差：

$$
\delta=d\sin\theta
$$

小角度近似：

$$
\delta\approx \frac{dx}{D}
$$

明纹条件：

$$
\delta=k\lambda
$$

明纹位置：

$$
x_k=k\frac{D\lambda}{d}
$$

暗纹条件：

$$
\delta=
\left(k+\frac{1}{2}\right)\lambda
$$

暗纹位置：

$$
x_k=
\left(k+\frac{1}{2}\right)
\frac{D\lambda}{d}
$$

条纹间距：

$$
\Delta x=\frac{D\lambda}{d}
$$

变化规律：

- $\lambda$ 增大，条纹变宽；
- $D$ 增大，条纹变宽；
- $d$ 增大，条纹变窄。

## 7.3 半波损失

光从光疏介质射向光密介质，并在界面反射时，产生相位突变：

$$
\pi
$$

等效附加光程：

$$
\frac{\lambda}{2}
$$

## 7.4 薄膜干涉

总光程差：

$$
\delta=
2ne\cos r+
\varepsilon\frac{\lambda}{2}
$$

其中：

$$
\varepsilon=0
$$

表示两束反射光半波损失情况相同；

$$
\varepsilon=1
$$

表示只有一束发生半波损失。

反射明纹：

$$
\delta=k\lambda
$$

反射暗纹：

$$
\delta=
\left(k+\frac{1}{2}\right)\lambda
$$

## 7.5 劈尖干涉

小角度：

$$
e\approx x\alpha
$$

相邻条纹对应的厚度差：

$$
\Delta e=\frac{\lambda}{2n}
$$

条纹间距：

$$
\Delta x=\frac{\lambda}{2n\alpha}
$$

## 7.6 牛顿环

反射光中，空气膜中心通常为暗斑。

第 $k$ 级暗环：

$$
r_k^2=kR\lambda
$$

直径：

$$
D_k^2=4kR\lambda
$$

两级暗环：

$$
D_{k+m}^2-D_k^2=4mR\lambda
$$

---

# 8. 光的衍射

## 8.1 单缝夫琅禾费衍射

暗纹条件：

$$
a\sin\theta=k\lambda
$$

其中：

$$
k=\pm1,\pm2,\pm3,\ldots
$$

小角度下：

$$
x_k\approx \frac{kf\lambda}{a}
$$

中央明纹宽度：

$$
\Delta x_0=\frac{2f\lambda}{a}
$$

> [!warning]
> 单缝公式求的是暗纹位置，不是明纹位置。

## 8.2 光栅常数

$$
d=a+b
$$

其中：

- $a$ 为透光缝宽；
- $b$ 为不透光部分宽。

若单位长度内有 $N$ 条刻痕：

$$
d=\frac{1}{N}
$$

## 8.3 光栅方程

$$
d\sin\theta=k\lambda
$$

其中：

$$
k=0,\pm1,\pm2,\ldots
$$

## 8.4 最大级次

按课程复习口径：

$$
|k|<\frac{d}{\lambda}
$$

若 $d/\lambda$ 恰好为整数，最大可观察级次要再减一。

## 8.5 缺级

光栅主极大：

$$
d\sin\theta=k\lambda
$$

单缝暗纹：

$$
a\sin\theta=k'\lambda
$$

同时满足时发生缺级：

$$
k=\frac{d}{a}k'
$$

若：

$$
\frac{d}{a}=q
$$

则：

$$
q,\ 2q,\ 3q,\ldots
$$

级缺失。

> [!important]
> 实际可见级次：先求最大级次，再删除缺级。

## 8.6 谱线重叠

不同波长在同一衍射角出现：

$$
k_1\lambda_1=k_2\lambda_2
$$

白光入射时：

- 零级为白色；
- 同一级中紫光靠近中央；
- 红光远离中央；
- 不同级光谱可能重叠。

---

# 9. 光的偏振

## 9.1 自然光通过偏振片

自然光强为 $I_0$，通过一个理想偏振片后：

$$
I_1=\frac{1}{2}I_0
$$

## 9.2 马吕斯定律

线偏振光通过检偏器：

$$
I=I_1\cos^2\theta
$$

自然光连续通过两个偏振片：

$$
I=\frac{1}{2}I_0\cos^2\theta
$$

> [!warning]
> 自然光通过第一个偏振片时，先乘 $\frac{1}{2}$。

## 9.3 布儒斯特定律

$$
\tan i_B=\frac{n_2}{n_1}
$$

此时：

$$
i_B+r=90^\circ
$$

反射光为完全线偏振光。

---

# 10. 气体动理论

## 10.1 理想气体状态方程

$$
pV=\nu RT
$$

也可写为：

$$
pV=NkT
$$

分子数密度：

$$
n=\frac{N}{V}
$$

所以：

$$
p=nkT
$$

## 10.2 温标

$$
T=273.15+t
$$

其中：

- $T$ 单位为 K；
- $t$ 单位为摄氏度。

## 10.3 压强微观公式

$$
p=\frac{1}{3}nm\overline{v^2}
$$

## 10.4 平均平动动能

$$
\overline{\varepsilon_t}
=
\frac{1}{2}m\overline{v^2}
$$

$$
\overline{\varepsilon_t}
=
\frac{3}{2}kT
$$

## 10.5 能量均分定理

每个独立平方型自由度平均能量：

$$
\frac{1}{2}kT
$$

单个分子平均能量：

$$
\overline{\varepsilon}
=
\frac{i}{2}kT
$$

$\nu$ 摩尔理想气体内能：

$$
U=\frac{i}{2}\nu RT
$$

常见自由度：

- 单原子刚性分子：$i=3$
- 双原子刚性分子：$i=5$
- 多原子刚性分子：$i=6$

## 10.6 三种统计速率

最概然速率：

$$
v_p=\sqrt{\frac{2RT}{M}}
$$

平均速率：

$$
\bar v=\sqrt{\frac{8RT}{\pi M}}
$$

方均根速率：

$$
v_{\mathrm{rms}}=\sqrt{\frac{3RT}{M}}
$$

大小关系：

$$
v_p<\bar v<v_{\mathrm{rms}}
$$

变化规律：

$$
v\propto \sqrt{\frac{T}{M}}
$$

> [!warning]
> 摩尔质量 $M$ 必须使用 $\mathrm{kg\cdot mol^{-1}}$。

---

# 11. 热力学第一定律

## 11.1 符号规定

本课程采用：

$$
Q=\Delta U+A
$$

其中：

- $Q>0$：系统吸热；
- $Q<0$：系统放热；
- $A>0$：系统对外做功；
- $A<0$：外界对系统做功；
- $\Delta U>0$：系统内能增加。

准静态体积功：

$$
\delta A=p\,dV
$$

总功：

$$
A=\int_{V_1}^{V_2}p\,dV
$$

热力学第一定律：

$$
Q=\Delta U+\int_{V_1}^{V_2}p\,dV
$$

## 11.2 理想气体内能与热容

$$
U=\frac{i}{2}\nu RT
$$

$$
\Delta U=\nu C_V(T_2-T_1)
$$

定体摩尔热容：

$$
C_V=\frac{i}{2}R
$$

定压摩尔热容：

$$
C_p=C_V+R
$$

$$
C_p=\frac{i+2}{2}R
$$

热容比：

$$
\gamma=\frac{C_p}{C_V}
$$

$$
\gamma=\frac{i+2}{i}
$$

## 11.3 等体过程

$$
V=\text{常量}
$$

$$
A=0
$$

$$
Q=\Delta U
$$

$$
Q=\nu C_V(T_2-T_1)
$$

## 11.4 等压过程

$$
p=\text{常量}
$$

$$
A=p(V_2-V_1)
$$

$$
A=\nu R(T_2-T_1)
$$

$$
\Delta U=\nu C_V(T_2-T_1)
$$

$$
Q=\nu C_p(T_2-T_1)
$$

## 11.5 等温过程

$$
T=\text{常量}
$$

$$
\Delta U=0
$$

$$
Q=A
$$

$$
A=
\nu RT\ln\frac{V_2}{V_1}
$$

也可写为：

$$
A=
\nu RT\ln\frac{p_1}{p_2}
$$

## 11.6 绝热过程

$$
Q=0
$$

$$
A=-\Delta U
$$

绝热方程：

$$
pV^\gamma=\text{常量}
$$

$$
TV^{\gamma-1}=\text{常量}
$$

$$
T^\gamma p^{1-\gamma}=\text{常量}
$$

绝热功：

$$
A=
\frac{p_1V_1-p_2V_2}{\gamma-1}
$$

也可写为：

$$
A=\nu C_V(T_1-T_2)
$$

绝热膨胀时：

$$
A>0
$$

$$
\Delta U<0
$$

$$
T_2<T_1
$$

## 11.7 循环过程

循环回到初态：

$$
\Delta U_{\text{循环}}=0
$$

所以：

$$
Q_{\text{净}}=A_{\text{净}}
$$

- 顺时针循环：$A_{\text{净}}>0$
- 逆时针循环：$A_{\text{净}}<0$

$p-V$ 图中，闭合曲线包围的有向面积就是循环净功。

## 11.8 热机效率

$$
A=Q_1-Q_2
$$

$$
\eta=\frac{A}{Q_1}
$$

所以：

$$
\eta=1-\frac{Q_2}{Q_1}
$$

## 11.9 卡诺热机与制冷机

卡诺热机效率：

$$
\eta_C=1-\frac{T_2}{T_1}
$$

一般制冷系数：

$$
\varepsilon=\frac{Q_2}{A}
$$

卡诺制冷系数：

$$
\varepsilon_C=
\frac{T_2}{T_1-T_2}
$$

> [!warning]
> 卡诺公式中的温度必须使用开尔文温度。

---

# 12. 热力学第二定律与熵

## 12.1 第二定律的两种表述

开尔文表述：

> 不可能从单一热源吸热，使其完全变为有用功，而不引起其他变化。

克劳修斯表述：

> 热量不可能在不引起其他变化的情况下，自动从低温物体传向高温物体。

两种表述等价。

## 12.2 可逆与不可逆过程

可逆过程要求：

1. 无限缓慢，近似准静态；
2. 无摩擦、黏滞等耗散；
3. 系统和环境都能完全恢复原状。

常见不可逆过程：

- 热量由高温物体传向低温物体；
- 摩擦生热；
- 气体向真空自由膨胀；
- 有限温差传热；
- 有限压强差膨胀。

> [!warning]
> 准静态不一定可逆，还必须没有能量耗散。

## 12.3 熵

可逆过程：

$$
dS=\frac{\delta Q_{\mathrm{rev}}}{T}
$$

两状态之间：

$$
\Delta S=
\int_1^2\frac{\delta Q_{\mathrm{rev}}}{T}
$$

理想气体熵变：

$$
\Delta S=
\nu C_V\ln\frac{T_2}{T_1}
+
\nu R\ln\frac{V_2}{V_1}
$$

也可写为：

$$
\Delta S=
\nu C_p\ln\frac{T_2}{T_1}
-
\nu R\ln\frac{p_2}{p_1}
$$

等温过程：

$$
\Delta S=
\nu R\ln\frac{V_2}{V_1}
$$

可逆绝热过程：

$$
\Delta S=0
$$

孤立系统：

$$
\Delta S\geq 0
$$

其中：

- 可逆过程：$\Delta S=0$
- 不可逆过程：$\Delta S>0$

---

# 13. 四类计算题固定模板

## 13.1 刚体综合题

1. 判断碰撞阶段能否对转轴使用角动量守恒；
2. 写：

   $$
   L_1=L_2
   $$
3. 求总转动惯量：

   $$
   J_{\text{总}}=
   J_{\text{刚体}}+\sum mr^2
   $$
4. 求碰撞后角速度；
5. 后续过程使用：

   $$
   M=J\alpha
   $$

   或：

   $$
   \int M\,d\theta=
   \Delta\left(\frac{1}{2}J\omega^2\right)
   $$

## 13.2 波动方程题

从图中读取：

$$
A,\qquad \lambda,\qquad u
$$

再求：

$$
T=\frac{\lambda}{u}
$$

$$
\omega=\frac{2\pi}{T}
$$

判断参考点运动方向，确定初相。

向右传播：

$$
y=
A\cos
\left[
\omega t-
\frac{2\pi}{\lambda}(x-x_0)+\varphi_0
\right]
$$

向左传播：

$$
y=
A\cos
\left[
\omega t+
\frac{2\pi}{\lambda}(x-x_0)+\varphi_0
\right]
$$

## 13.3 光栅题

求光栅常数：

$$
d=
\frac{k\lambda}{\sin\theta}
$$

缺级公式：

$$
k=\frac{d}{a}k'
$$

最大级次：

$$
|k|<\frac{d}{\lambda}
$$

最后删除缺级，并完整写出：

$$
0,\ \pm1,\ \pm2,\ldots
$$

## 13.4 热力学题

1. 用状态方程求各状态量：

   $$
   pV=\nu RT
   $$
2. 判断每段是什么过程；
3. 分别求：

   $$
   A,\qquad \Delta U,\qquad Q
   $$
4. 始终使用：

   $$
   Q=\Delta U+A
   $$
5. 循环中：

   $$
   \Delta U_{\text{循环}}=0
   $$

   $$
   A_{\text{净}}=Q_{\text{净}}
   $$
6. 热机效率：

   $$
   \eta=
   \frac{A_{\text{净}}}{Q_{\text{吸}}}
   $$

---

# 14. 考前易错点清单

1. 速率是路程对时间的变化率。
2. 向心力是法向合力，不是额外的一种力。
3. 静摩擦力不一定等于最大静摩擦力。
4. 最远位置表示速度为零，不表示合力为零。
5. 碰撞粘连通常机械能不守恒。
6. 对固定轴的外力矩为零时，才能使用角动量守恒。
7. 有质量滑轮两侧拉力通常不相等。
8. 简谐振动速度公式中的负号不能漏。
9. 向右传播的波，空间相位项取负号。
10. 固定端反射有 $\pi$ 相变。
11. 单缝公式求的是暗纹。
12. 光栅公式求的是主极大。
13. 自然光通过第一个偏振片后，强度先减半。
14. 热力学统一使用：

    $$
    Q=\Delta U+A
    $$
15. 理想气体内能只与温度有关。
16. 循环过程中总内能变化为零，但每一段不一定为零。
17. 卡诺效率和气体状态方程中的温度必须用 K。
18. 熵是状态函数，不可逆过程也可用假想可逆路径计算熵变。

---

# 15. 建议复习顺序

1. 刚体综合题；
2. 波动方程题；
3. 光栅衍射题；
4. 热力学过程与循环题；
5. 简谐振动与波的概念题；
6. 光的干涉、偏振；
7. 气体动理论与热力学第二定律；
8. 最后检查易错点清单。

---

# 资料来源

- 第一章 质点运动学
- 第二章 质点动力学基础
- 第三章 三大守恒定律
- 第四章 刚体力学
- 第六章 机械振动
- 第七章 机械波
- 第八章 光的干涉
- 第九章 光的衍射
- 第十章 光的偏振
- 第十一章 气体动理论
- 第十二章 热力学第一定律
- 第十三章 热力学第二定律
- 2025级大学物理Ⅰ期末复习资料
