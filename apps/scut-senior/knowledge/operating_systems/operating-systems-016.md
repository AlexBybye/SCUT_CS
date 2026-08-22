---
source_id: operating-systems-016
course_id: operating_systems
title: "OS2011EGB真题Q&A"
original_file: "学科资料/操作系统/往年卷/OS2011EGB真题Q&A.pdf"
document_role: note
year: 2011
locator_type: page
---

# OS2011EGB真题Q&A

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
(A)
A. Running→ready
C. blocked→running
B.
running→blocked
D. blocked→ready
2.
Shared variables are those that ______
（D)
A. can only be accessed by system processes
B.
can only be accessed by a lot of process mutual exclusively
C.
can only be accessed by user processes
D. can be accessed by a lot of process
3.
It is provable that ______ scheduling algorithm is optimal if all the jobs are
available simultaneously.
(B)
A. FCFS
B. SJF
C. Round-robin
D. Priority
4.
In a system, we require all processes to request all their resources before
starting execution. This is a method for preventing deadlock to attack the
________ condition.
(B)
A. Mutual Exclusion
C. No Preemption
B.
Hold and Wait
D. Circular Wait
5.
Which of the following algorithm can result in external fragmentation
problem?
(C)
A. first fit
C. best fit
B.
next fit
D. worst fit
6.
Which of the following page replacement algorithm need to clear R bit
periodically?
(C)
A. FIFO
B. Second Chance
C. Aging
D. Working Set
7.
Writing commands to the device registers is done in which layers?
(B)
A. Interrupt handlers
C. Device-independent OS software
B.
Device drivers
D. User-level I/O software
8.
“Device independence” means
(C)
A. that devices are accessed dependent of their model and types of physical

_____________ ________

( 密封线内不答题)

《操作系统》试卷
第1 页共4 页

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
(D)
A. search for the specified file in main memory
B.
copy the specified file into main memory
C.
search for the directory of the file in storage medium
D. fetch the directory of the file into main memory
10. As for MS-DOS/Windows system, the attributes of file are stored in
D .
A. file
B. directory
C. directory entry
D. i-node

二、填空题(共10 分，每空1 分)

1.
Operating systems can be viewed from two viewpoints: ____Extended
Machine(扩展机器)_and _Resource Manager(资源管理者)_.
2.
If we implement thread in kernel space, __thread_ (process or thread) is a
basic unit of CPU utilization.
3.
The initial value of the semaphore S is 2. If the current value is -1, then there
are __1___ (how many) processes waiting.
4.
__Priority(优先级)_scheduling algorithm can deal with the urgent process
in time.
5.
A computer with a 32-bit address uses a two-level page table. Virtual
addresses are split into a 9-bit top-level page table system, an 11-bit second
page table field, and an offset. Each page is __4K__ bytes. And there are
___220__(how many) pages in the address space.
6.
Disk requests come in to the disk driver for cylinders 10, 22, 20, 2, 40, 6, and
38, in that order. The arm is initially at cylinder 20. A seek takes 6 msec per
cylinder moved. How much seek time is needed for Elevator algorithm
(initially moving upward)? ____348__ ms; And how much seek time is
needed for Closest cylinder next algorithm? __360__ ms
7.
With __symbolic( 符号)__ links, only the true owner of the file has a
pointer to the i-node.

三、简答题(共20 分，每题5 分)

1.
Please describe the difference between a process and a program.
答：进程是具有独立功能的程序关于某个数据集合的一次运行活动，是系统
进行资源分配和调度的独立单位。程序是指令的有序序列。进程与程序的区
别：


进程是动态的，程序是静态的；

进程是短暂的，程序可以永久保存；

进程与程序之间不具有一一对应关系：一个程序可以对应一个
进程，也可以对应多个进程；一个进程可以对应一个程序，或

《操作系统》试卷
第2 页共4 页

<!-- page: 3 -->

者对应一段程序；
进程可以创建子进程。

2.
Describe the concept of the critical resource and critical region, and give an
example for them each.
临界资源：一次仅允许一个进程访问的资源。如：硬件资源：输入机、打印
机等；软件资源：共享变量、表格、队列、文件等。

临界区：访问临界资源的程序段。假设a 为共享变量，则访问a 的那段
程序就是临界区。如：a:=a+1; print(a);

3.
Will Resource Allocation Graph with a cycle lead to deadlock? Why?
答：不一定。
如果每个资源只有一个资源实例，则有环路的资源分配图会导致死锁；如果
每个资源有多个资源实例，则有环路的资源分配图可能、但不一定会导致死
锁。

4.
How many disk operations are needed to fetch the i-node for the file
/usr/ast/workspace/mp1.tar? Why? Assume that the i-node for the root
directory is in memory, but nothing else along the path is in memory. Also
assume that all directories fit in one disk block.
答：①directory for /

②i-node for /usr
③directory for /usr
④i-node for /usr/ast
⑤directory for /usr/ast
⑥i-node for /usr/ast/workspace
⑦directory for /usr/ast/workspace
⑧i-node for /usr/ast/workspace/mp1.tar
In total, 8 disk reads are required.

四、综合题(共50 分)

1.
(12 分)There are 32 pages in the user space of virtual storage. Each page is
1K bytes size. And the computer has 16K bytes main memory.
(1) How many bits are needed to describe logical address space?
(2) How many bits are needed to describe physical address space?
(3) Assume one instance that the page 0, 1, 2, 3 was respectively loaded into

frame page 5, 10, 4, 7, please calculate the physical address of the logical
address 2,652 and 1,340(Decimal).

《操作系统》试卷
第3 页共4 页

<!-- page: 4 -->

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
0
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
3

Please answer：

(1) Is state safe?
(2) If P2 Requests Resources (1,2,2,2)，should system meet the demand

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
第4 页共4 页
