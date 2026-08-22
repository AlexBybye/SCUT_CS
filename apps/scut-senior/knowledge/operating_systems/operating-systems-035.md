---
source_id: operating-systems-035
course_id: operating_systems
title: "OS试卷CN"
original_file: "学科资料/操作系统/往年卷/OS试卷CN2.pdf"
document_role: past_exam
year: 
locator_type: page
---

# OS试卷CN

<!-- page: 1 -->

操作系统试卷二

<!-- question: operating-systems-035-Q1 -->

一、是非题(下列各题，你认为正确的，请在题干的括号内打“ √”，错的打“×”。每题2 分，共24
分)

<!-- question: operating-systems-035-Q2 -->

1、对批处理作业，运行时不须提供相应的作业控制信息。（
）

<!-- question: operating-systems-035-Q3 -->

2、并发性是指若干事件在同一时刻发生。（
）

<!-- question: operating-systems-035-Q4 -->

3、对临界资源，应采用互斥访问方式来实现共享。（
）

<!-- question: operating-systems-035-Q5 -->

4、临界段是指进程中用于实现进程互斥的那段代码。（
）

<!-- question: operating-systems-035-Q6 -->

5、在动态优先级高度中，随着进程执行时间的增加，其优先级降低。（
）

<!-- question: operating-systems-035-Q7 -->

6、联机用户接口是指用户与操作系统之间的接口，它不是命令接口。（
）

<!-- question: operating-systems-035-Q8 -->

7、即使在多道程序环境下，用户也能设计用内存物理地址直接访问内存的程序。（
）

<!-- question: operating-systems-035-Q9 -->

8、在页式虚存系统中，为了提高内存利用率，允许用户使用不同大小的页面。（
）

<!-- question: operating-systems-035-Q10 -->

9、在分配共享设备和独占设备时，都可能引起死锁。（
）

<!-- question: operating-systems-035-Q11 -->

10、虚拟设备是指把一个物理设备变换成多个对应的逻辑设备。（
）

<!-- question: operating-systems-035-Q12 -->

11、顺序文件适合于建立在顺序存储设备上，而不适合建立在磁盘上。（
）

<!-- question: operating-systems-035-Q13 -->

12、若系统中存在一个循环等待的进程集合，则必定会死锁。（
）

<!-- question: operating-systems-035-Q14 -->

二、填空题(每题2 分，共20 分)

<!-- question: operating-systems-035-Q15 -->

1、通常所说操作系统的四大模块是指：文件管理、设备管理、（
）和（
）。

<!-- question: operating-systems-035-Q16 -->

2、作业调度是从（
）中选一道作业，为它分配资源，并为它创建（
）。

<!-- question: operating-systems-035-Q17 -->

3、进程的基本特征为：动态性、独立性、（
）和（
）。

<!-- question: operating-systems-035-Q18 -->

4、中断分类后，中断是指（
），异常是指（
）。

<!-- question: operating-systems-035-Q19 -->

5、所谓脱机用户接口是指（
）。

<!-- question: operating-systems-035-Q20 -->

6、用户程序必须通过程序级接口方能获得操作系统的服务，庐接口主要是由一组（
）组
成。

<!-- question: operating-systems-035-Q21 -->

7、在多道连续可变划分法中，可通过（
）来减少外零头。

<!-- question: operating-systems-035-Q22 -->

8、设访问串为：1，3，2，4，1，2，驻留集大小为3，按LRU 策略控制上述访问串，应发生（
）
次页故障。

<!-- question: operating-systems-035-Q23 -->

9、按用途可将文件分为：系统文件、（
）和（
）。

<!-- question: operating-systems-035-Q24 -->

10、破坏“循环等待”条件，通常可采用（
）。

<!-- question: operating-systems-035-Q25 -->

三、多选题(在本题的每小题的备选答案中，正确答案有两个或两个以上，请把你认为正确答案
的题号，填入题干的括号内。少选、多选不给分。每题3 分，共18 分)

<!-- question: operating-systems-035-Q26 -->

1、下列哪些信息应含于PCB 表中（
）
①用户名
②进程名
③现场区
④进程优先级

<!-- question: operating-systems-035-Q27 -->

2、下列哪些是驻留集可变的页面替换策略（
）
①OPT
②WS
③LRU
④VMIN

<!-- question: operating-systems-035-Q28 -->

3、下列哪些可用作进程间的通讯手段（
）
①系统调用
②P、V 操作
③原语
④DMA

<!-- question: operating-systems-035-Q29 -->

4、多道程序系统的主要特征包括（
）
①资源共享
②临界段互斥
③程序并发
④多级中断处理

<!-- question: operating-systems-035-Q30 -->

5、下面哪些是可以不连续的内存分配方法（
）
①页式
②段式
③可变分区
④虚存

<!-- question: operating-systems-035-Q31 -->

6、在页式系统中，页表应包含（
）
①保护码
②页长
③修改位
④页帧号

<!-- question: operating-systems-035-Q32 -->

四、何为文件系统？为何要引入文件系统？(6 分)

<!-- page: 2 -->

<!-- question: operating-systems-035-Q33 -->

五、现为某临界资源设一把锁w，当w＝1 时，表示关锁，w＝0 时，表示锁已打开，试写出开
锁和关锁的原语，并说明如何利用它们去控制对该临界资源的互斥访问？(7 分)

<!-- question: operating-systems-035-Q34 -->

六、在页式虚存管理系统中，设页面大小为26，页表内容如下，现访问虚地址：(245)8 和(126)8，

问是否会发生页故障中断？若会则简述故障中断的处理过程，否则将虚地址变换成相应的物
理地址。(8 分)

页表：(表中的数均为八进制)

页帧号
合法位
修改位

100

0

┇

┇

5

1

┇

┇

20

1

┇

┇

30

0

┇

┇

<!-- question: operating-systems-035-Q35 -->

七、设有三道作业，它们的提交时间及运行时间如下表，若采用短作业优先调度策略，试给出作
业单道串行运行时的调度次序及平均周转时间。(8 分)

作
业
提交时间(单位：基本时间单位)
运行时间(单位：基本时间单位)

J1

0

7

J2

2

4

J3

3

5

<!-- question: operating-systems-035-Q36 -->

八、设系统有三种类型的资源，数量为(4，2，2)，系统中有进程A，B，C 按如下顺序请求资源：

进程A 申请(3，2，1)
进程B 申请(1，0，1)
进程A 申请(0，1，0)
进程C 申请(2，0，0)
请你给出一和防止死锁的资源剥夺分配策略，完成上述请求序列，并列出资源分配过程，
指明哪些进程需要等待，哪些资源被剥夺。(9 分)
