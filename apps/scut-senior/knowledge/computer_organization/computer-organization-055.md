---
source_id: computer-organization-055
course_id: computer_organization
title: "答案"
original_file: "学科资料/计算机组成原理/计算机组成与体系结构参考答案（来自SRW）/答案10.doc"
document_role: note
year: 
locator_type: none
---

# 答案

**本科生期末试卷十答案**

**一**．**选择题**

1．D     2．A         3．B       4．D     5．B

6．B     7．A B C     8．A、C     9．B    10．B

**二**．**填空题**

1.A.容量大    B.速度快    C.成本低  ；

2.A.性能    B.格式    C.功能  ；

3.A.指令    B.程序    C.地址  ；

4 A.VGA  B.1280×1024  C.24位  ；

5..A.优先级仲裁    B.向量    C.控制逻辑  ；

6.  A.  指令  B.  流水线  C.多处理机

**三**.

解：（1）最大正数

x = [ 1 +（1  –  2-23 ）]  ×2127

（2）最小正数

x = 1．0×2-128

（3）最大负数

x = -1．0×2-128

（4）最小负数

x = - [ 1 +  （1  –  2-23 ）]  ×2127

四、解：因为：ta =  tc  /  e   所以 ：tc =  ta×e =  60×0.85 = 510ns (cache存取周期)

tm =  tc×r  =510  ×4 = 204ns (主存存取周期)

因为：e  =  1  /  [r + (1 – r )H]

所以： H =  2.4 / 2.55 = 0.94

五、解：“ADD  （R1），（R2）+”指令是SS型指令，两个操作数均在主存中。其中源操作数地址在R1中，所以是R1间接寻址。目的操作数地址在R2中，由R2间接寻址，但R2的内容在取出操作数以后要加1进行修改。指令周期流程图如图B10.4

![image](assets/assets/computer-organization-055/image-001.png)

图B10.4

六、解：节拍脉冲T1 ，T2 ，T3 的宽度实际等于时钟脉冲的周期或是它的倍数，此时T1  = T2  =200ns ，T3  = 400  ns ，所以主脉冲源的频率应为  f = 1 / T1  =5MHZ 为了消除节拍脉冲上的毛刺，环型脉冲发生器采用移位寄存器形式。图B10.5画出了题目要求的逻辑电路图和时序信号关系。根据关系，节拍脉冲T1 ，T2 ，T3 的逻辑表达式如下：

T1  = C1×C2    ，T2  = C2   ，T3  = C1

![image](assets/assets/computer-organization-055/image-002.png)

图  B 10.5

七、解：I / O系统组成如图**B10.6**所示：

![image](assets/assets/computer-organization-055/image-003.png)

图  **B 10.6**

根据设备传输速率不同，磁盘、磁带采用DMA方式，打印机、CRT  采用中断方式；因

而使用了独立请求与链式询问相结合的二维总线控制方式。DMA  请求的优先权高于中

断请求线。每一对请求线与响应线又是一对链式查询电路。

八、
1. 立即
1. 寄存器
1. 直接
1. 基址
1. 基址+偏移量
1. 比例娈址+偏移量
1. 基址+变址+偏移量
1. 基址+比例变址+偏移量
1. 相对

九解：1）n条指令进入流水线的时空图如下：

![formula-object](assets/assets/computer-organization-055/image-004.png)

2）顺序方式执行n条指令的总时间T0为

T0=k×Δt×n

流水方式n条指令所需的总时间Tk为：

Tk=（k+n-1）×Δt

加速比S的表达式为

S= $\frac {{T}_{0}} {{T}_{k}}$= $\frac {k\times n\times \Delta t} {(k+n-1)\times \Delta t}$=$\frac {k\times n} {k+n-1}$

效率E的表达式为

E=$\frac {k\times n\times \Delta t} {k\times (k+n-1)\times \Delta t}$=  $\frac {n} {k+n-1}$

式中分子部分是完成n条指令实际占用的时空图有效面积，分母部分是n条指令所用的总时间同k个流水段所围成的时空图总面积。
