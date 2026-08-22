---
source_id: computing-methods-003
course_id: computing_methods
title: "笔记"
original_file: "学科资料/计算方法/笔记-爱来自WJQ/笔记.docx"
document_role: note
year: 
locator_type: none
---

# 笔记

数值分析

一、误差

（绝对）误差、误差限、相对误差、相对误差限。

有效数字

上面四者的四则运算公式。

四舍五入求近似值的条件下如何将误差限和有效数字相互转换？

二、代数插值与数值微分

1.  线性插值和二次插值

**（1）线性插值**

给定p(x0) = y0, p(x1) = y1，构造一个y  = f(x)，x次数<=1次，来拟合(x0,y0)和(x1,y1)。

虽然挺好算的，但是可以注意一下Lagrange形式。

![image](assets/computing-methods-003/image-001.tmp)

一阶差商与Newton形式（点斜式）

![image](assets/computing-methods-003/image-002.tmp)

![image](assets/computing-methods-003/image-003.tmp)

线性插值误差

![image](assets/computing-methods-003/image-004.tmp)

罗尔定理（Rolle’s Theorem）：若f(x)在[a,b]连续且f(a) = f(b)，那么在(a,b)肯定至少存在一点使得f’(x) = 0.

平均值定理（Mean Value Theorem）：若f(x)在[a,b]连续且连接a点和b点的直线p(x)（线性插值得到的直线）斜率为k，那么f(x)（实际的曲线）在(a,b)中至少存在一点c，使得f’(c) = k。

例题：

![image](assets/computing-methods-003/image-005.tmp)

![image](assets/computing-methods-003/image-006.tmp)

**（2）二次插值**

就是用二次函数拟合f(x)。

这样会列出三元二次方程组，以及它的系数行列式：

![image](assets/computing-methods-003/image-007.tmp)![image](assets/computing-methods-003/image-008.tmp)

最终得到的：Lagrange形式

![image](assets/computing-methods-003/image-009.tmp)

![image](assets/computing-methods-003/image-010.tmp)

![image](assets/computing-methods-003/image-011.tmp)

二阶差商与Newton形式

![image](assets/computing-methods-003/image-012.tmp)

误差：![image](assets/computing-methods-003/image-013.tmp)

2.  更一般的情况—n次插值

![image](assets/computing-methods-003/image-014.tmp)

![image](assets/computing-methods-003/image-015.tmp)

![image](assets/computing-methods-003/image-016.tmp)

3.分段线性插值

**（1）Runge现象**：高次插值多项式不一定能更好地近似被插函数。

**（2）分段线性插值思想：**

将区间分段，然后每个分段低次差值，一般每个分段的方程都<=一次

假设f(xi) = yi，将定义域分为[x0,x1] , (x1,x2)  ,  …  , (xn-1,xn]，对每个区间做一次线性插值，得到分段目标函数p(x)：

![image](assets/computing-methods-003/image-017.tmp)

**（3）分段线性插值误差：**

![image](assets/computing-methods-003/image-018.tmp)

4.  Hermite插值

由于分段线性插值导数不连续，因此除了插值函数在插值节点上的值与被插值函数𝑓(𝑥)

在插值节点上的值相等，我们还希望这些点上的**导数值相等**。

**（1）三次Hermite插值**

![image](assets/computing-methods-003/image-019.tmp)

![image](assets/computing-methods-003/image-020.tmp)

**（2）Hermite插值误差**

![image](assets/computing-methods-003/image-021.tmp)

5. 分段三次Hermite插值

就是每个区间都做一个三次Hermite插值。

6. 三次样条插值

后续补上

7. 数值微分

有些函数能用表达式表示，能直接求导得到解。

有些函数用表格表示，采用数值微分进行近似的导数求解。

**剩下的全写个人纸质笔记上了，有想要的联系21-计科-小红**
