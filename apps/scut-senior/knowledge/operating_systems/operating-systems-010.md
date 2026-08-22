---
source_id: operating-systems-010
course_id: operating_systems
title: "OS2008EGB真题Que"
original_file: "学科资料/操作系统/往年卷/OS2008EGB真题Que.pdf"
document_role: note
year: 2008
locator_type: page
---

# OS2008EGB真题Que

<!-- page: 1 -->

… … … … … … … … … … … … … … … … 密… … … … … … … … … … … … … … … … … … 封… … … … … … … … … … … … … … … 线… … … … … … … … … … … … … …

诚信应考,考试作弊将带来严重后果！

华南理工大学期末考试

《操作系统》试卷(B)

姓名
学号
学院
专业
座位号

注意事项：1. 考前请将密封线内填写清楚；

2. 所有答案请答在答题纸上；
3．考试形式：闭卷；

4. 本试卷共四大题，满分100 分，考试时间120 分钟。
题号
一
二
三
四
五
总分
得分
评卷人

一、选择题(共20 分，每题2 分)

1.
When the printing event which a process requested is finished, transition
_______ will occur.
A. Running→ready
C. blocked→running
B.
running→blocked
D. blocked→ready
2.
Shared variables are those that ______
A. can only be accessed by system processes
B.
can only be accessed by a lot of process mutual exclusively
C.
can only be accessed by user processes
D. can be accessed by a lot of process
3.
It is provable that ______ scheduling algorithm is optimal if all the jobs are
available simultaneously.
A. FCFS
B. SJF
C. Round-robin
D. Priority
4.
In a system, we require all processes to request all their resources before
starting execution. This is a method for preventing deadlock to attack the
________ condition.
A. Mutual Exclusion
C. No Preemption
B.
Hold and Wait
D. Circular Wait
5.
Which of the following algorithm can result in external fragmentation
problem?
A. first fit
C. best fit
B.
next fit
D. worst fit
6.
Which of the following page replacement algorithm need to clear R bit
periodically?
A. FIFO
B. Second Chance
C. Aging
D. Working Set
7.
Writing commands to the device registers is done in which layers?
A. Interrupt handlers
C. Device-independent OS software
B.
Device drivers
D. User-level I/O software
8.
“Device independence” means
A. that devices are accessed dependent of their model and types of physical

_____________ ________

( 密封线内不答题)

《操作系统》试卷
第1 页共7 页

<!-- page: 2 -->

device.
B.
systems that have one set of calls for writing on a file and the console
(terminal) exhibit device independence.
C.
that files and devices are accessed the same way, independent of their
physical nature.
D. None of the above
9.
The purpose of the open file call is to ______.
A. search for the specified file in main memory
B.
copy the specified file into main memory
C.
search for the directory of the file in storage medium
D. fetch the directory of the file into main memory
10. As for MS-DOS/Windows system, the attributes of file are stored in______.
A. file
B. directory
C. directory entry
D. i-node

二、填空题(共10 分，每空1 分)

1.
Operating
systems
can
be
viewed
from
two
viewpoints:
__________________ and _________________.
2.
If we implement thread in kernel space, __________ (process or thread) is a
basic unit of CPU utilization.
3.
The initial value of the semaphore S is 2. If the current value is -1, then there
are _____ (how many) processes waiting.
4.
__________ scheduling algorithm can deal with the urgent process in time.
5.
A computer with a 32-bit address uses a two-level page table. Virtual
addresses are split into a 9-bit top-level page table system, an 11-bit second
page table field, and an offset. Each page is _______ bytes. And there are
__________ (how many) pages in the address space.
6.
Disk requests come in to the disk driver for cylinders 10, 22, 20, 2, 40, 6, and
38, in that order. The arm is initially at cylinder 20. A seek takes 6 msec per
cylinder moved. How much seek time is needed for Elevator algorithm
(initially moving upward)? _________ ms; And how much seek time is
needed for Closest cylinder next algorithm? ________ ms
7.
With __________ links, only the true owner of the file has a pointer to the
i-node.

三、简答题(共20 分，每题5 分)

1.
Please describe the difference between a process and a program.
2.
Describe the concept of the critical resource and critical region, and give an
example for them each.
3.
Will Resource Allocation Graph with a cycle lead to deadlock? Why?
4.
How many disk operations are needed to fetch the i-node for the file
/usr/ast/workspace/mp1.tar? Why? Assume that the i-node for the root
directory is in memory, but nothing else along the path is in memory. Also
assume that all directories fit in one disk block.

《操作系统》试卷
第2 页共7 页

<!-- page: 3 -->

四、综合题(共50 分)

1.
(12 分)There are 32 pages in the user space of virtual storage. Each page is
1K bytes size. And the computer has 16K bytes main memory.
(1) How many bits are needed to describe logical address space?
(2) How many bits are needed to describe physical address space?
(3) Assume one instance that the page 0, 1, 2, 3 was respectively loaded into

frame page 5, 10, 4, 7, please calculate the physical address of the logical
address 2,652 and 1,340(Decimal).

2.
(14 分) One tunnel, which is very narrow, allows only one passenger to pass
once, Please using semaphores to realize the following situation:

The passengers at one direction must pass the tunnel continuously.
Another direction’s visitors can start to go through tunnel when no
passengers want to pass the tunnel from the opposite direction.

3.
(12 分)Basing on the Banker’s Algorithm，if exists the following allocation：

Process
Allocation
Need
Available

A
B
C
D
A
B
C
D
A
B
C
D

P1
P2
P3
P4
P5

0
1
1
0
0

0
0
3
3
0

3
0
5
3
1

2
0
4
2
4

0
1
2
0
0

0
7
3
6
6

1
5
5
5
5

2
0
6
2
6

1
6
2
2

Please answer：

(1) Is state safe?
(2) If P3 Requests Resources (1,2,2,2)，should system meet the demand

and allocate them to it?

4.
(12 分) In a batch system，the arrival time and burst time of three jobs are
listed in following table (time unit: hour in decimal ), if schedule with FCFS
and SJF Algorithm respectively:

Job
Arrival time
Burst time
1
10.00
2.00
2
10.10
1.00
3
10.25
0.25

(1) Please calculate start time and finish time of each job.
(2) Calculate average Turnaround Time.

《操作系统》试卷
第3 页共7 页

<!-- page: 4 -->

选择题(共20 分，每题2 分)

NO.
1
2
3
4
5
6
7
8
9
10
answer
A
D
B
B
C
C
B
C
D
D

五、填空题(共10 分，每空1 分)

1. Extended Machine(扩展机器)，Resource Manager(资源管理者)
2. thread
3. 1
4. Priority(优先级)
5. 4K，2
20

6. 348ms，360ms
7. symbolic(符号)

六、简答题(共20 分，每题5 分)

1. 答：进程是具有独立功能的程序关于某个数据集合的一次运行活动，是
系统进行资源分配和调度的独立单位。程序是指令的有序序列。进程与
程序的区别：


进程是动态的，程序是静态的；

进程是短暂的，程序可以永久保存；

进程与程序之间不具有一一对应关系：一个程序可以对应一个
进程，也可以对应多个进程；一个进程可以对应一个程序，或
者对应一段程序；

进程可以创建子进程。

2. 答：临界资源：一次仅允许一个进程访问的资源。如：硬件资源：输入
机、打印机等；软件资源：共享变量、表格、队列、文件等。
临界区：访问临界资源的程序段。假设a 为共享变量，则访问a 的那段
程序就是临界区。如：a:=a+1; print(a);
3. 答：不一定。
如果每个资源只有一个资源实例，则有环路的资源分配图会导致死锁；
如果每个资源有多个资源实例，则有环路的资源分配图可能、但不一定
会导致死锁。

4. ①directory for /
②i-node for /usr
③directory for /usr
④i-node for /usr/ast
⑤directory for /usr/ast
⑥i-node for /usr/ast/workspace
⑦directory for /usr/ast/workspace
⑧i-node for /usr/ast/workspace/mp1.tar
In total, 8 disk reads are required.

《操作系统》试卷
第4 页共7 页

<!-- page: 5 -->

七、综合题(共50 分)

1. 解：
(4) 用户空间的大小为32×1KB=32KB，所以需要15 位逻辑地址。
(5) 内存空间的大小为16KB，所以需要14 为物理地址。
(6) 页表如下：

页号
块号

0

5

1

10

2

4

3

7


(2652)10 ＝(000,1010,0101,1100)2 ，后10 位为页内偏移量
(offset)，前5 位00010 为虚页号2，查页表知，该页装入到内
存第4 页，故实页号为0100，与后10 位页内偏移量拼接形成物
理地址为：(01,0010,0101,1100)2＝(125C)16＝(4700)10


(1340)10 ＝(000,0101,0011,1100)2 ，后10 位为页内偏移量
(offset)，前5 位00001 为虚页号1，查页表知，该页装入到内
存第10 页，故实页号为1010，与后10 位页内偏移量拼接形成物
理地址为：(10,1001,0011,1100)2＝(293C)16＝(10556)10

2. 解：将隧道的两个方向标记为A 和B；

(1) 设置信号量AB 和BA，分别表示轮到哪个方向的行人过隧道，初值

都为1；

设置mutex 用来实现两个方向的行人对隧道的互斥使用。
A 方向的行人：
B 方向的行人：
P(AB);
P(BA);
P(mutex);
P(mutex);
通过隧道；
通过隧道；
V(mutex);
V(mutex);
V(BA);
V(AB);

(2)
用变量countA 和conutB 表示A 和B 方向上已经在隧道中的行人数目，初
值为0；

再设置三个互斥信号量，初值都为1：


SA 实现对countA 互斥修改

SB 实现对countB 变量的互斥修改

mutex 用来实现两个方向的行人对隧道的互斥使用

《操作系统》试卷
第5 页共7 页

<!-- page: 6 -->

A 方向的行人：

P(SA);
If(countA=0) then P(mutex);
countA=countA+1;
V(SA);

通过隧道；
P(SA);
countA=countA-1;
If(countA=0) then V(mutex);
V(SA);

B 方向的行人：

P(SB);
If(countB=0) then P(mutex);
countB=countB+1;
V(SB);

通过隧道；
P(SB);
countB=countB-1;
If(countB=0) then V(mutex);
V(SB);

3. 解：
(3) 该状态是安全的。


(1,6,2,2)>(0,0,1,2)，先满足P1 的请求，执行完毕后回收P1 资源
(0,0,3,2)，则可用资源变为(1,6,5,4)；

(1,6,5,4)>(0,6,5,2)，可满足P4 的请求，执行完毕后回收P4 资源
(0,3,3,2)，则可用资源变为(1,9,8,6)；

(1,9,8,6)>(0,6,5,6)，可满足P5 的请求，执行完毕后回收P5 资源
(0,0,1,4)，则可用资源变为(1,9,9,10)；

(1,9,9,10)>(1,7,5,0)，可满足P2 的请求，执行完毕后回收其资源
(1,0,0,0)，则可用资源变为(2,9,9,10)；

(2,9,9,10)>(2,3,5,6)，可满足P3 的请求，执行完毕后回收其资源
(1,3,5,4)，则可用资源变为(3,12,14,14)，即为资源总量。
存在一安全序列：{P1,P4,P5,P2,P3}，故该状态是安全的。

(4) 当前可用资源(1,6,2,2)大于进程P3 提出的请求(1,2,2,2)，若满足

P3 的资源请求，则可用资源变为(0,4,0,0)，资源分配情况变为：

《操作系统》试卷
第6 页共7 页

<!-- page: 7 -->

Process
Allocation
Need
Available

A
B
C
D
A
B
C
D
A
B
C
D

P1
P2
P3
P4
P5

0
4
0
0

0
1
2
0
0

0
0
5
3
0

3
0
7
3
1

2
0
6
2
4

0
1
1
0
0

0
7
1
6
6

1
5
3
5
5

2
0
4
2
6

检查此刻是否为安全状态：可用资源(0,4,0,0)不能满足任何一个进程的
Need 请求，故此状态为不安全状态，故不能将P3 请求的资源分配给它。

4.
(1)

FCFS
SJF

作业
提交
时间

执行
时间

开始时间
完成时间
周转时间
开始时间
完成时间
周转时间

1
10.00
2
10.00
12.00
①
2.0
10.00
12.00
①
2.0

2
10.20
1
12.00
13.00
②
2.8
12.80
13.80
④
3.6

3
10.40
0.5
13.00
13.50
③
3.1
12.30
12.80
③
2.4

4
10.50
0.3
13.50
13.80
④
3.3
12.00
12.30
②
1.8

(2) 平均周转时间：

FCFS 法的平均周转时间为：(2.0 + 2.8 + 3.1 + 3.3) / 4 = 2.8 小
时
SJF 法的平均周转时间为：(2.0 + 3.6 + 2.4 + 1.8) / 4 = 2.45 小时

《操作系统》试卷
第7 页共7 页
