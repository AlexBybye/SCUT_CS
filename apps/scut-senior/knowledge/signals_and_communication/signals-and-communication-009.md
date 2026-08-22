---
source_id: signals-and-communication-009
course_id: signals_and_communication
title: "通信基础-数字基带传输系统2-2025F"
original_file: "学科资料/信号处理与通信基础/通信基础/通信基础-数字基带传输系统2-2025F.pdf"
document_role: note
year: 2025
locator_type: page
---

# 通信基础-数字基带传输系统2-2025F

<!-- page: 1 -->

第5章 数字基带传输系统

（第2讲）

1

<!-- page: 2 -->

目录

n 引言

n 码间串扰

n 部份响应基带传输系统

n 基带信号的检测与最佳接收

<!-- page: 3 -->

回顾：问题的描述

基带传输系统的基本结构：

输出

输入

( )
r t
( )
T
G
f
( )
R
G
f
( )
C f

'
{
}
na

{
}
na

)
(t
x
( )
s t
)
(t
y

)
(t
n
噪声

3

<!-- page: 4 -->

回顾：1.1　问题的描述

基带传输系统的基本结构：

输出

输入

( )
r t
( )
T
G
f
( )
R
G
f
( )
C f

'
{
}
na

{
}
na

)
(t
x
( )
s t
)
(t
y

cp

)
(t
n
噪声
定时脉冲

形成适于信道传输的波形，
使其具有较高的频带利用率
及较强的抗码间干扰能力 ；
如升余弦脉冲、钟形脉冲等

改变数字基带信号
的码型，使其适于
信道传输；如单(双)

以矩形为基础。含有
较大的低频和高频分
量，占用频带较宽。

极性(不)归零等

4

<!-- page: 5 -->

1.1　问题的描述

滤除带外噪声，对信道特
性均衡，使输出的基带波

基带传输系统的基本结构：

形有利于抽样判决。

输出

输入

( )
r t
( )
T
G
f
( )
R
G
f
( )
C f

'
{
}
na

{
}
na

)
(t
x
( )
s t
)
(t
y

cp

)
(t
n
噪声
定时脉冲

在位定时脉冲规定时
刻（由位定时脉冲控
制）对接收滤波器的
输出波形进行抽样判
决，以恢复或再生基
带信号。信号失真和
噪声的影响，可能会
出现误码。

将判决器判决出的“1”码
及“0”码变换成所需的数

为低通型传输特性
的有线信道。通常
是不理想的，信号
通过它会产生失真；

字基带信号形式。

还会引入零均值的
高斯白噪声(AWGN)。

5

<!-- page: 6 -->

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

a
b
c
d
e
g

f

定时脉冲

同步提取

0

误码

1

![image](assets/assets/signals-and-communication-009/image-001.jpeg)

<!-- page: 7 -->

目标:

n 可靠性：

  接收端以最小的错误概率恢复出发送序列。研究误码

率与系统的什么参数有关，如何使误码率达到最小

n 有效性：

  基带传输系统的带宽都是有限的，在有限带宽情况下

如何尽可能提高码元速率，即使频带利用率尽可能的
高

7

<!-- page: 8 -->

数学描述：

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

p 如何设计总传输特性H(f),使得收发两端差错尽可能少；
p 如何设计总传输特性H(f),使得在物理可实现时，频带利用

率尽可能高；
p 当总传输特性H(f)达不到设计要求时，可以采取什么办法补

偿；

p 结合H(f)评价数字基带传输系统的性能；

8

![image](assets/assets/signals-and-communication-009/image-002.jpeg)

<!-- page: 9 -->

数字基带传输系统：

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

接收端

发送端

p 信号设计问题，重点：发送信号如何形成，对发送信号有何要求。

p 系统传输问题，重点：传输系统（信道）对通信有何影响，对传输系
                       统有何要求。

p 接收问题，重点：接收性能如何，哪些因素会影响接收性能及如何定
                   量计算。

9

<!-- page: 10 -->

1.2 数字基带信号的码型

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

原始
信号

具有一定码

具有一定码型
和波形的信号

型的信号

抽象信号
具体电信号

数字基带信号的码型：数字信息的表示方式。
数字基带信号的波形：数字信息的电脉冲形状。

10

<!-- page: 11 -->

1.2 数字基带信号的码型

n 回顾：对传输码型的要求：

n 相应的基带信号无直流分量，且低频分量少；

n 便于从信号中提取定时信息；

n 信号中高频分量尽量少，以节省传输频带；

n 不受信源统计特性的影响，即能适应信源的变化；

n 具有内在的检错能力；

n 编译码设备要尽可能简单；

11

<!-- page: 12 -->

1.2 数字基带信号的码型

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

原始
信号
具有一定码

具有一定码型和波

型的信号

形的信号

抽象信号
具体电信号

Ø 对传输码型的要求
   原始消息代码必须编成适合于传输用的码型
Ø 对基带脉冲的要求：
   所选码型对应的电波形应适合于基带系统的传输

12

<!-- page: 13 -->

以矩形为基础。含有较
大的低频和高频分量，

占用频带较宽。

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

原始信

号
具有一定码型

具有一定码型和波形

的信号

的信号

抽象信号
具体电信号

Ø 对传输码型的要求
   原始消息代码必须编成适合于传输用的码型
Ø 对基带脉冲的要求：
   所选码型对应的电波形应适合于基带系统的传输

13

<!-- page: 14 -->

波形设计与编码
广义信道

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

对发送信号有何要求，如何形
成发送信号

p 信号设计问题

传输系统（信道）对通信有何
影响，对传输系统有何要求

p 系统传输问题

p 接收问题

14

<!-- page: 15 -->

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

a
b
c
d
e
g

f

定时脉冲

同步
提取

1       0        1        0        1       1       0

产生误码的原因：

噪声和码间串扰

误码

1       0        1        1        1       1       0

1

15

![image](assets/assets/signals-and-communication-009/image-003.jpeg)

<!-- page: 16 -->

目录

n 引言

n 码间串扰

n 部份响应基带传输系统

n 基带信号的检测与最佳接收

<!-- page: 17 -->

5.5 数字基带传输中的码间串扰

n问题：基带传输中的可靠性问题
n研究对象：码间串扰
n研究目的：如何设计没有码间串扰的基带传

          输系统
n方法：由定性到定量，由复杂到简单再到复杂

17

<!-- page: 18 -->

数字基带传输中的码间串扰

p 码间串扰的概念

p 码间串扰的数学分析

p 无码间串扰的传输特性

18

<!-- page: 19 -->

一、码间串扰的概念

接收

码型

发送

抽样

判决
信道

滤波

变换

滤波

输入脉冲

带宽不受限信道

输出脉冲

H(f)

t

f

t

信道带宽受限、特

传输信道

性不理想

输出脉冲

输入脉冲

H(f)

t
f

-B            B

t

带宽受限信道

19

<!-- page: 20 -->

一、码间串扰的概念

接收

码型

发送

抽样

判决
信道

滤波

变换

滤波

信道带宽受限、特

性不理想

20

![image](assets/assets/signals-and-communication-009/image-004.jpeg)

<!-- page: 21 -->

1
1
0
1
1

发送

t

接收

a1

a2

Tb+t0

a3

t

t0

3Tb+t0

2Tb+t0

a4

0
0
0
1
a
a
a
a
a
a
a
a










当
时判为“ ”，反之当
判为“”。

1
2
3
4
1
2
3
4

a
a
a
a





因此当
时将发生错判，从而造成误码。

1
2
3
4

21

<!-- page: 22 -->

码间串扰的定义

   由于信道带宽的有限性和信道特性的不理想，波形将发生展宽

和失真，当这种情况比较严重时，当前时刻码元的抽样判决将
受到它前后几个码元所对应的波形的影响。这种影响就叫做码
间串扰。

思考：
1）什么情况下会引入误码？
2）无码间串扰可能吗？

22

<!-- page: 23 -->

数字基带传输中的码间串扰

p 码间串扰的概念
p 码间串扰的数学分析
p 无码间串扰的传输特性

什么是码间串扰？
   其它码元波形在当前码元取样时刻的值。带限系统，存
在码间串扰。和噪声一样，码间串扰也是产生误码的主要
原因。

怎样实现无码间串扰传输？

23

<!-- page: 24 -->

二、码间串扰的数学分析

2
j
ft
T
R
H
f
G
f C f G
f
h t
H
f e
df
















接收

发送

抽样

判决
信道
码型

滤波

滤波

变换







假设

( )
(
)
n
b
n
d t
a
t
nT


带宽受限


















y t
d t
h t
n t
a
t
nT
h t
n t

( )
( )
( )
( )
(
) * ( )
( )



n
b
n







a h t
nT
n t





(
)
( )

n
b
n

24



![image](assets/assets/signals-and-communication-009/image-005.jpeg)

<!-- page: 25 -->

二、码间串扰的数学分析

导致误码的
两大原因：
噪声和码间

设第k个码元的判决时刻为

串扰





y kT
t
a h k
n T
t
n kT
t

(
)
[(
)
]
(
)








b
n
b
b
n

0
0
0







a h t
a h k
n T
t
n kT
t








( )
[(
)
]
(
)

k
n
b
b
n
n k

0
0
0




除第k个码元外其

第k个码元取样时

第k个码元的

它码元的串扰值

刻的输出噪声

取样值

25

<!-- page: 26 -->

三、无码间串扰的传输特性









码间串扰

a h k
y kT
t
a
t
T
h
n
t

0
0
0
[
(
(
)
)
)
]
(
n
b

b
k

n
n




k

方法：
（1）通过各项互相抵消使串扰为0；





（2）使

26

![image](assets/assets/signals-and-communication-009/image-006.jpeg)

![image](assets/assets/signals-and-communication-009/image-007.jpeg)

<!-- page: 27 -->

1、无码间串扰的时域传输特性

k
h kT
k







(
0,
0)
(
)
0
(
0)
b

A
A

( )
h t

有等间隔的过0点。
以此间隔为码元间隔。

0
t

27

![image](assets/assets/signals-and-communication-009/image-008.jpeg)

<!-- page: 28 -->

例：

( )
h t

( )
H f
1

bT

bT
2 bT
3 bT
4 bT
4 bT

3 bT

2 bT

bT


1
2 bT

1
2 bT
0

f

t

(b)

(a)

即其它码元的波形在当
前码元取样时刻的值为
0

28

![image](assets/assets/signals-and-communication-009/image-009.jpeg)

<!-- page: 29 -->

2、无码间串扰的频域特性推导

k
h kT
k







(
0,
0)
(
)
0
(
0)
b

A
A

2
( )
( )
j
ft
h t
H f e
df






2
(
)
( )
b
j
fkT
b
h kT
H f e
df





t=kTb

1/
b
b
f
T







常数)

H f
mf
A

B
R
(
)
(
b
m



n 说明：H(f) 以fb为间隔进行周期性重复（频域），

叠加起来为常数。

29

<!-- page: 30 -->

2、无码间串扰的频域传输特性(1)

n 码元速率为fb时，无码间串扰时的基带传输特性必须满足奈

奎斯特(Nyquist)第一准则:



b
b
f
f
f




eq
H
f





常数)

H f
mf
A

(
)
(
b
m

2
2



奈奎斯特第一准则，也称为无码间串扰准则。
它的核心思想是：在理想条件下，要实现在一个码元的抽样时

刻上，其他所有码元的响应值为零。
奈奎斯特第一准则为所有现代数字通信系统（从传统的调制解

调器到今天的5G和Wi-Fi）的设计奠定了基石，它指明了在有
限带宽信道中实现可靠高速传输的根本限制和实现途径。

30

![image](assets/assets/signals-and-communication-009/image-010.jpeg)

<!-- page: 31 -->

2、无码间串扰的频域传输特性(2)

Ø 系统函数H(f)（频域响应）在频率轴上以fb 为间隔平移并叠加

后，结果为一个常数：






常数)

H f
mf
A

(
)
(
b
m



Ø 理想情况下，无码间串扰传输所需的最小系统带宽Wmin是码元

速率fb 的一半：（奈奎斯特带宽）
                      Wmin= fb /2=1/2Ts

b
b
f
f
f




2
2

Ø 对于一个给定带宽为W的理想信道，其能够支持的最高无码间

串扰的码元速率为：（奈奎斯特速率）
                     Rs,max=2W

31

<!-- page: 32 -->

无码间串扰的传输特性_结论

n 输入序列若以fb波特的速率进行传输时，所需的最小传输带

宽为fb/2Hz（理想低通）。这是在抽样时刻无码间串扰条件
下，基带系统所能达到的极限情况。

n 奈奎斯特带宽： fb/2 Hz

n 奈奎斯特速率：给定基带系统带宽为W时，则该系统无码间

串扰的最高传输速率为2W波特

n 基带系统所能提供的最高频带利用率为=2 B/Hz

n 当码元速率小于奈奎斯特速率时，判断基带传输系统是否

在抽样时刻无码间串扰的条件为：

f
H
f
H f
m T
f









常数

( )
(
/
)
2

b
eq
b
m

32

<!-- page: 33 -->

小结

广义信道

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

p码间串扰是造成系统误码的主要原
因之一，必须加以控制；

传输特性决定
了是否存在码
间串扰，或码
间串扰有多大

p 无码间串扰的系统，其传输要满
足奈奎斯特准则。

33

<!-- page: 34 -->

目录

n 引言

n 码间串扰

n 部份响应基带传输系统

n 基带信号的检测与最佳接收

<!-- page: 35 -->

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

)
(
)
(
)
(
)
(
f
G
f
C
f
G
f
H
R
T




k
h
kT
h
k
b




0
0
0
)
(
k





常数








（常数）

H f
mf

(
)
A
b
m



35

<!-- page: 36 -->

Ø 具有理想低通传输特性的系统：

（1）物理不可实现：频带利用率高，达2波特/赫兹，但无法实现(系统的响应在
t<0时就已经存在，它要求系统在输入信号到来之前就必须有输出，这违背了自然
界的因果性)；
（2）对定时误差极其敏感：拖尾振荡幅度大，衰减慢，所以对定时的要求高。

Ø 具有升余弦特性的系统：
为了解决理想低通滤波器的问题，工程上广泛采用升余弦滚降滤波器。
思路：放松对频域截止边缘的陡峭程度要求，使其从通带到阻带有一个平滑的

过渡（即“滚降”）。
滚降因子α：用来描述这种过渡带的宽度，0≤α≤1。

•
α=0 时，理想的矩形滤波器。
•
α=1 时，过渡带最宽。
优点：

•
物理可实现：其时域响应是因果的，可以被实际电路或数字滤波器逼近。
•
对定时误差不敏感：由于频域过渡平滑，其拖尾衰减得非常快，即使采样
时刻有偏移，引入的码间串扰也很小。

36

![image](assets/assets/signals-and-communication-009/image-011.jpeg)

<!-- page: 37 -->

具有升余弦特性的系统的代价：

（1）拖尾振荡幅度小，衰减快，对定时要求相对较低；

（2）但是，频带利用率低:

所需的系统带宽：B=(1+α)* Rs/2

​当α=0.5 时，带宽为0.75Rs

​当α=1 时，带宽为Rs,此时频带利用率为1Baud/Hz

问题：

37

![image](assets/assets/signals-and-communication-009/image-012.jpeg)

![image](assets/assets/signals-and-communication-009/image-013.jpeg)

![image](assets/assets/signals-and-communication-009/image-014.jpeg)

<!-- page: 38 -->

n 问题：基带传输中的有效性问题

n 研究对象：部分响应系统

n 研究目的：如何设计频带利用率高又可实现

的基带传输系统

n 方法：放宽对无码间串扰的要求以提高有效

性

38

![image](assets/assets/signals-and-communication-009/image-015.jpeg)

<!-- page: 39 -->

39

![image](assets/assets/signals-and-communication-009/image-016.jpeg)

![image](assets/assets/signals-and-communication-009/image-017.jpeg)

![image](assets/assets/signals-and-communication-009/image-018.jpeg)

<!-- page: 40 -->

n 观察：相距一个码元间

隔的两个sinx/x波形

n “拖尾”刚好正负相反

n 思路：利用这样的波形

组合肯定可以构成“拖

尾”衰减很快的脉冲波

形

40

![image](assets/assets/signals-and-communication-009/image-019.jpeg)

![image](assets/assets/signals-and-communication-009/image-020.jpeg)

<!-- page: 41 -->

( )
(
)
[
(
)]
b
b
b
g t
Sa
f t
Sa
f t
T






Sa
f t
g t
f t




(
)
( )
1

b

b

k
g kT
k

1,
0,1
(
)
0,
0,1
b







波形特点：

n
当前码元仅对下一码元有干扰值为1，与自身值相同，而对其它码元无干扰。

n
g (t )波形的拖尾幅度与t 2成反比，而sinx/x波形幅度与t成反比，这说明g (t ) 波
形拖尾的衰减速度加快了；相距一个码元间隔的两个sinx/x波形的“拖尾”正
负相反而相互抵消，使合成波形“拖尾”迅速衰减；

41

![image](assets/assets/signals-and-communication-009/image-021.jpeg)

![image](assets/assets/signals-and-communication-009/image-022.jpeg)

![image](assets/assets/signals-and-communication-009/image-023.jpeg)

<!-- page: 42 -->

( )
(
)
[
(
)]
b
b
b
g t
Sa
f t
Sa
f t
T






n 传输函数







f
f
e
fT
T
f
G
b
fT
j
b
b






2
/
)
cos(
2
)
(

b

else

0

n 频带利用率为=RB/B=2波特／赫，达到基带系统在

传输二进制序列时的理论极限值

42

![image](assets/assets/signals-and-communication-009/image-024.jpeg)

![image](assets/assets/signals-and-communication-009/image-025.jpeg)

<!-- page: 43 -->

能用g(t)作传送波形吗？

n 若用g(t)作为传送波形，

且码元间隔为Tb，则有
串扰；

n 串扰值：+1或-1

n 串扰发生位置：仅受前

一码元的相同幅度样值
的串扰

n 结论：串扰可控，仍可

按1/Tb传输速率传送码
元

43

![image](assets/assets/signals-and-communication-009/image-026.jpeg)

![image](assets/assets/signals-and-communication-009/image-027.jpeg)

<!-- page: 44 -->

错误传播：提出问题

n 设发送码元ak

n 接收波形g(t)在第k个时刻上获得的样值Ck可能有2、

0、+2三种取值

1
k
k
k
C
a
a 



1
k
k
k
a
C
a 

－

存在问题：
p ak不仅由Ck确定，而且须参考ak-1的判决结果，如果

ak-1发生差错，则不但造成ak值错误，而且还会影响
到以后所有的ak+1，ak+2，的抽样值错误，我们把
这种现象称为错误传播现象。

44

![image](assets/assets/signals-and-communication-009/image-028.jpeg)

<!-- page: 45 -->

错误传播：举例

输入
信码
1
0
1
1
0
0
0
1
0
1
1

发送
端{ak} +1
-1
+1
+1
-1
-1
-1
+1
-1
+1
+1

发送
端{Ck}
0
0
+ 2
0
-2
-2
0
0
0
+2

接收
的
{Ck’}

0
0
+2
0
-2
0 X
0
0
0
+2

恢复
的
{ak’}

+1
-1
+1
+1
-1
-1
+1 X -1 X +1 X -1 X +3 X

45

<!-- page: 46 -->

错误传播：如何解决？

单极
性码

n 先将输入信码ak变成bk ，bk=akbk1

n 把{bk}作为发送序列，形成g(t)波形序列，则

　　　　Ck=bk+bk1

                [Ck]mod2=[bk+bk1]mod2=bkbk1=ak

　　　　ak=[Ck]mod2

n 结论：对接收到的Ck作模2处理后便直接得到发

送端的ak，此时不需要预先知道ak-1，因而不存在

错误传播现象。

46

![image](assets/assets/signals-and-communication-009/image-029.jpeg)

<!-- page: 47 -->

双极性

单极性

情况

情况
ak=[Ck]mod2
0,
2

C
a
C







k
k

1,
0

k

{ak}
1
0
1
1
0
0
0
1
0
1
1

{bk-1} 0
1
1
0
1
1
1
1
0
0
1

单极
性情

{bk}
1
1
0
1
1
1
1
0
0
1
0

况

{Ck}
1
2
1
1
2
2
2
1
0
1
1

{Ck’} 1
2
1
1
1 ×
2
2
1
0
1
1

{ak’} 1
0
1
1
1 ×
0
0
1
0
1
1

{bk-1} 0
1
1
0
1
1
1
1
0
0
1

双极
性情

{bk}
1
1
0
1
1
1
1
0
0
1
0

况

{Ck}
0
+2
0
0
+2
+2
+2
0
-2
0
0

{Ck’} 0
+2
0
0
+2
+2
+2
0
0 ×
0
0

{ak’} 1
0
1
1
0
0
0
1
1 ×
1
1

47

![image](assets/assets/signals-and-communication-009/image-030.jpeg)

<!-- page: 48 -->

双极性

单极性

情况

情况
ak=[Ck]mod2
0,
2

C
a
C







k
k

1,
0

k

{ak}
1
0
1
1
0
0
0
1
0
1
1

{bk-1} 0
1
1
0
1
1
1
1
0
0
1

单极
性情

{bk}
1
1
0
1
1
1
1
0
0
1
0

况

{Ck}
1
2
1
1
2
2
2
1
0
1
1

{Ck’} 1
2
1
1
1 ×
2
2
1
0
1
1

预编码解除了码元间的相关性，由当前Ck
值可直接得到当前的ak，错误不会传播下
去，而只局限在受干扰码元本身的位置。

{ak’} 1
0
1
1
1 ×
0
0
1
0
1
1

{bk-1} 0
1
1
0
1
1
1
1
0
0
1

双极
性情

{bk}
1
1
0
1
1
1
1
0
0
1
0

况

{Ck}
0
+2
0
0
+2
+2
+2
0
-2
0
0

{Ck’} 0
+2
0
0
+2
+2
+2
0
0 ×
0
0

{ak’} 1
0
1
1
0
0
0
1
1 ×
1
1

48

![image](assets/assets/signals-and-communication-009/image-031.jpeg)

![image](assets/assets/signals-and-communication-009/image-032.jpeg)

<!-- page: 49 -->

预编码——相关编码——模2判决

bk=akbk1
Ck=bk+bk1

单极性

情况

预编码
相关编码

2
mod
'
'
)
(
k
k
c
a


双极性

情况





'
'

c
a





2
0

k
k
c

'

0
1



k

49

![image](assets/assets/signals-and-communication-009/image-033.jpeg)

![image](assets/assets/signals-and-communication-009/image-034.jpeg)

![image](assets/assets/signals-and-communication-009/image-035.jpeg)

<!-- page: 50 -->

部分响应的一般形式

n 部分响应波形的一般形式是N个相继间隔Tb的sinx/x

波形之和

1
2
1
(
1)
L
k
k
k
N
k
N
a
R b
R b
R b








模加




1
2
( )
(
)
[
(
)]
(
1)
b
b
b
N
b
b
g t
R Sa
f t
R Sa
f t
T
R Sa
f
t
N
T












n R1，R2，，RN为加权系数，其取值为正、负整数及零。例如，

当取R1=1，R2=1，其余系数Ri=0时，就是前面所述的第I类部
分响应波形。

1
2
1
(
1)
L
k
k
k
N
k
N
a
R b
R b
R b








模加

此时：

1
2
1
(
1)
k
k
k
N
k
N
C
R b
R b
R b






算术加

L
k
k
C
a
mod
]
[


Ck的电平数要超过ak的进制数

50

<!-- page: 51 -->

L
C
a
k
k
mod
)
(


51

![image](assets/assets/signals-and-communication-009/image-036.jpeg)

![image](assets/assets/signals-and-communication-009/image-037.jpeg)

<!-- page: 52 -->

采用部分响应的优缺点

优点：

n 能实现2B/Hz的频带利用率

n 它的“尾巴”衰减大且收敛快

缺点：

n 当输入数据为L进制时，部分响应波形的相关编码电

平数要超过L个。因此，在同样输入信噪比条件下，
部分响应系统的抗噪声性能要比零类响应系统差。

52

<!-- page: 53 -->

目录

n 引言

n 码间串扰

n 部份响应基带传输系统

n 基带信号的检测与最佳接收

<!-- page: 54 -->

1
2

3

GT (f )
C (f )
GR (f )

输入
输出

码型
变换器

发送
滤波器
信道
接收
滤波器

抽样
判决

码型
变换器

同步
提取

定时脉冲

对发送信号有何要求，如何形
成发送信号

p 信号设计问题

传输系统（信道）对通信有何
影响，对传输系统有何要求

p 系统传输问题

p 接收问题

无码间串扰时，加性高斯白噪声
（AWGN）信道，如何实现最佳
接收（使差错概率最低）？

54

<!-- page: 55 -->

5.7 二进制信号的最佳接收

n 问题：数字信号的可靠性问题

n 研究对象：传输中的噪声

n 研究目的：如何设计特定噪声下的

                 最佳接收机

n 方法：简化条件，根据准则

55

<!-- page: 56 -->

二进制信号的最佳接收

n 1 问题的描述

n 2 匹配滤波器与最佳接收机的一般结构

n 3 最佳检测*

n 4 二进制信号的最佳接收机结构及性能*

56

<!-- page: 57 -->

 问题的描述

数字基带信号的接收机原理框图

假设：仅存在噪声，无码间串扰，二元信号传输

接收机波形：

b
H
r t
s t
n t
t
T
H
r t
s t
n t

:
( )
( )
( )
0
:
( )
( )
( )










0
0

1
1

接收机的任务：根据接收信号r(t)判定发送的比特值是0还是1

57

![image](assets/assets/signals-and-communication-009/image-038.jpeg)

<!-- page: 58 -->

最佳接收：误
码率最小的接

问题的描述

收

数字基带信号的接收机原理框图

最佳接收滤波器：针对
接收信号r(t)，设计出一个
最佳滤波器，使滤波器的输

最佳检测：针对滤波器的输
出y(t)，设计出最佳的检测方
法，使恢复出的序列和发送序

出y(t)最有利于判决

列间的误码最小

接收

接收

发送

抽样

判决
信道
码型

滤波

滤波

滤波

H(f)

变换

58

![image](assets/assets/signals-and-communication-009/image-039.jpeg)

<!-- page: 59 -->

问题的描述

p 什么样的输出最利于判决？

    理论和实践证明，同样输入噪声的条件下，若某滤波器在判
决时刻t0能够输出最大的信号瞬时功率与噪声平均功率之比，
则检测器错误判决的概率最小。

 该滤波器称为最大输出信噪比意义下的最佳线性滤波器，通信
中更多地称它为匹配滤波器（MF：matched filter）。

p 什么样的检测叫最佳检测？

¯问题：匹配滤波器如何设计？即如何得到匹配滤
波器的H( f )和h(t)呢？







1|
0
0
0 |
1
1
eP
p
p
p
p

判为发射
发射
＋
判为
发射
发射

59

<!-- page: 60 -->

匹配滤波器与最佳接收机一般结构

1. 匹配滤波器（MF）

S
N







o

MF: 输出信噪比最大的线性滤波器

n接收滤波器输入端加入的是信号和噪声的混合波形

                                r(t) = s(t) + n(t)
n式中s(t)为输入的数字信号，n(t)为高斯白噪声，其双边功
率谱密度为n0/2

n 问题：求线性滤波器是否在某时刻t0上，信号瞬时功率
  与噪声平均功率的比值能达到最大？这一最大值是多少？

60

![image](assets/assets/signals-and-communication-009/image-040.jpeg)

<!-- page: 61 -->

1. 匹配滤波器

线性滤波器

r(t)=s(t)+n(t)
y(t)=so(t)+no(t)

H( f )

( )
( )
s t
S f

o
o
( )
( )
s t
S
f


2
o
o
( )
( )
j
ft
s t
S
f e
df



2
( )
( )
j
ft
S f H f e
df









输出信号：

2
0
2
n
H
f
df



o
o
n
N
P
f df


inP
f
H f
df


2















输出噪声功率：

0
2
2

2
o
0
o

( )
s
t
r
N









j
ft
H
f
S
f
e
df



t0时刻输出信噪比：

n
H
f
df



2
0
2






o



61

<!-- page: 62 -->

1. 匹配滤波器

在t0时刻输出信噪比：

0
2
2
2







j
ft
H
f S f e
df
s
t
r
n
N
H
f
df



o
0
o
2
0
o







2



¯ ro与S( f )和H( f )有关

¯在输入信号s(t)给定的情况下，ro只与H( f )有关

¯ 什么样的H( f )能使ro取得最大值呢？

62

<!-- page: 63 -->

p 匹配滤波器的传递函数H(f)

利用 施瓦兹不等式：





P
f
H
f

令

S
f
f e








0
2
2

( ) j
ft

2
|
|
|
|

0
2
2

df
df
r
n
H f
d

H

(

)

j
ft df
s
t
r
n
N
H
f







2



H

S
f
f e




o
0

o



o
2
o





2
0

f

|
( )

|



d

f

0




0
2
j
ft
Q f
S f e



2

2









从而：

2

S f
df
r
n

2
|
( ) |

2E
n


o

0

0

2
E
r
n


0
2
j
ft
H
f
KS
f e






P f
KQ
f






omax

0

¯注意：romax与K无关，K可为任意常数，一般取1。

63

![image](assets/assets/signals-and-communication-009/image-041.jpeg)

![image](assets/assets/signals-and-communication-009/image-042.jpeg)

<!-- page: 64 -->




0
2
j
ft
H
f
KS
f e





结论：在白噪声干扰的背景下，按上式设计的线
性滤波器，将能在给定时刻t0上获得最大的输出信
噪比2E/n0。这种滤波器就是最大信噪比意义下的
最佳线性滤波器。由于它的传输特性与信号频谱
的复共轭相一致（除相乘因子外），故又称它为
匹配滤波器。

64

<!-- page: 65 -->

p 匹配滤波器的冲激响应h(t)





2
( )
j
ft
H f e
df













0
2
2
( )
j
ft
j
ft
KS
f e
e
df









( )
h t




j
f t
t
K
S f e
df


0
2
(
)
( )

0
(
)
Ks t
t




0
( )
(
)
h t
Ks t
t



h(t)是s(t)
的镜像函数

0

0

0
¯t0到底取何值呢？

65

<!-- page: 66 -->

p 匹配滤波器的冲激响应h(t)

物理可实现性：

0
0
0
0,
0
( )
(
)
(
)
0,
0
( )
0,
0,
0
t
h t
Ks t
t
s t
t
t
s t
t
t
t
















u 结论：由匹配滤波器的物理可实现性可知，s(t)必
须在它输出最大信噪比的时刻t0之前结束。即：

u 若输入信号在T时刻结束，则输出最大信噪比时刻t0
应为：t0 T

u 通常为了获得迅速的判决，选取信号结束的瞬间作
为取样判决时刻，即取t0=T

66

<!-- page: 67 -->

小结（匹配滤波器）

匹配滤波器：最大信噪比意义下的最佳接收滤波器
结论：

2
E
r
n


omax

0




0
2
j
ft
H
f
KS
f e





0
( )
(
)
h t
Ks t
t



u 若输入信号在T时刻结束，则判决时刻t0应为：t0 T

o
0
0
( )
(
)
(
)
s
s
s
t
KR
t
t
KR
t
t





67

![image](assets/assets/signals-and-communication-009/image-043.jpeg)

![image](assets/assets/signals-and-communication-009/image-044.jpeg)

<!-- page: 68 -->

p 匹配滤波器的输出

o
0
( )
( )
( )
( ) (
)
( ) [
(
)]
s
t
s t
h t
s u h t
u du
K
s u s t
t
u du















0
( ) (
)
K
s u s u
t
t du








o
0
0
( )
(
)
(
)
s
s
s
t
KR
t
t
KR
t
t





2
o
0
( )
(0)
( )
s
s
t
KR
K
s
t dt
KE








结论：匹配滤波器的输出信号在形式上与输入信号的
自相关函数相同，仅差一个常数因子K及时间上延迟t0。
所以可用相关器代替匹配滤波器。

68

![image](assets/assets/signals-and-communication-009/image-045.jpeg)

![image](assets/assets/signals-and-communication-009/image-046.jpeg)

<!-- page: 69 -->

p 匹配滤波器的输出

匹配滤波器：（设 s(t) 仅在[0, T]有值，T时刻判决）

( )
( )
[ ( )
( )] [
(
)]
|t T
r
r t
h t
s u
n u s T
t
u du


2( )
( ) ( )
s
u du
s u n u du




















相关器：

0 [ ( )
( )] ( )
T
r
s t
n t
s t dt




0
0
( )
( ) ( )
T
T
s
t dt
s t n t dt





2

69

![image](assets/assets/signals-and-communication-009/image-047.jpeg)

![image](assets/assets/signals-and-communication-009/image-048.jpeg)

![image](assets/assets/signals-and-communication-009/image-049.jpeg)

<!-- page: 70 -->

2. 最佳接收机结构

¯由匹配滤波器构成的最佳接收机结构

针对信号
专门定制

¯注意：信号有多少种形式，MF就有多少种形式

70

![image](assets/assets/signals-and-communication-009/image-050.jpeg)

<!-- page: 71 -->

2. 最佳接收机结构

由于匹配滤波器在t=T时刻的输出值恰好等于相关
器的输出值，也即用相关器可以代替匹配滤波器：

　相关器方式的最佳接收机结构

71

![image](assets/assets/signals-and-communication-009/image-051.jpeg)

<!-- page: 72 -->

 最佳检测

问题：根据被检测量（判决变量）y如何来设计检

测准则，使总的错误概率最小？







1|
0
0
0 |
1
1
eP
p
p
p
p

判为发射
发射
＋
判为
发射
发射

P(D1/H0)：假设H0为真，但检
测结果为H1时的错误概率，即
发送“0”码，却被错判为“1”

P(D0/H1)：假设H1为真，但检
测结果为H0时的错误概率，即
发送“1”码，却被错判为“0”

码的概率，称“虚警概率”

码的概率，称“漏警概率”







1
0
0
0
1
1
|
|
eP
p D
p
p
p

H
H
＋
D
H
H

我们必须知道在判决时刻被检测量（判决变量）y的概率分布和判决门限

72

<!-- page: 73 -->

最佳检测:问题的数学描述

问题：如果已知判决变量y此时的概率密度函数
      f0(y)和f1(y)，那么什么样的判决门限是
      使误码率最小的呢？

判决准则：

y
V
y
V








0 |1
p


1|0
p
1
0

判为“”
判为“ ”

d

d

误码率（全概率公式）：

V

V
P
f
y dy
P
f
y dy








0
1
(0)
( )
(1)
( )
d

(0) (1/ 0)
(1) (0/1)
eP
P
P
P
P



d

73

![image](assets/assets/signals-and-communication-009/image-052.jpeg)

<!-- page: 74 -->

5.7.3 眼图

n 问题：码间串扰和噪声的估计

n 研究对象：眼图

n 研究目的：如何用实验的方法来减小码间串

                 扰和噪声的影响

n 方法：定性分析，实验观察

74

<!-- page: 75 -->

眼图：什么是眼图？

n 眼图是指利用实验的方法估计和改善传输系统性能时在示波

器上观察到的像人的眼睛一样的图形。

( )
y t

接收
滤波器

n 从中可以估计出系统的性能（指码间串扰和噪声的大小）并

据此对接收滤波器的特性加以调整，以减小码间串扰和改善
系统的传输性能。

n 与码型有关

75

<!-- page: 76 -->

第5章 数字基带传输系统

n  基带传输系统特性的眼图观测方法

   眼图：利用示波器观测基带传输系统特性的一种简便方法。

   二进制的基带信号波形

理想信道下眼图

非理想信道下眼图

![image](assets/assets/signals-and-communication-009/image-053.jpeg)

<!-- page: 77 -->

第5章 数字基带传输系统

n  基带传输系统特性的眼图观测方法(续)

  二进制的基带信号波形的抽象表示

通过眼图可以基本确定整个基带传输系统的传输性能
  眼图张开程度越大，波形曲线越细越清晰，系统的性能越好。
  噪声干扰和码间串扰等影响严重的系统眼图张开度小，曲线粗

大且模糊。

![image](assets/assets/signals-and-communication-009/image-054.jpeg)

<!-- page: 78 -->

第5章 数字基带传输系统

n  基带传输系统特性的眼图观测方法(续)

  示波器上实际观测到的“眼图”效果

![image](assets/assets/signals-and-communication-009/image-055.jpeg)

<!-- page: 79 -->

小结-1

抽样
判决
输入
输出
GT (f )
C (f )
GR (f )

码型
变换器

发送
滤波器
信道
接收
滤波器

码型
变换器

p  信号设计问题

p 系统传输问题

p 接收问题

79

<!-- page: 80 -->

小结-2

n 本章围绕提高数字基带传输系统传输信息的有效性和可靠性

展开了讨论。

n 通过学习奈奎斯特第一准则，认识到通信系统的有效性不可

能无限提高，即：在信道带宽受限和无码间串扰的条件下，
可传送的最高码元速率数值上等于信道带宽的两倍；

n 通过对数字基带传输系统性能（误码率）的分析，认识到噪

声是影响通信系统可靠性的重要因素；

n 通过对最佳接收机和匹配滤波器的讨论，可知设计最佳接收

机的步骤是：
（1）首先了解信道条件和发送信号的先验知识
（2）选择并确定设计准则（最大后验概率准则、最大似然准则

     等等）
（3）通过数学推导获取最佳接收机结构

80

<!-- page: 81 -->

小结-3

n 在实际系统中，奈奎斯特第一准则通常是不可实现的，

即系统既无码间串扰又可达到最大的频带利用率是不可

能的；

n 通过运用部分响应技术设计信号将大大提高系统的可实

现性，提高系统的有效性；

n 本章讨论了加性高斯白噪声信道下基带信号的最佳接收

问题和信道不随时间变化条件下的时域均衡技术等。实

际情况要复杂得多，信道中不仅仅存在加性高斯白噪声，

而且信道特性是随时间变化的。

81
