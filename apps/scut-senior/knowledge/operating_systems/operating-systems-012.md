---
source_id: operating-systems-012
course_id: operating_systems
title: "OS2010EGB真题Que"
original_file: "学科资料/操作系统/往年卷/OS2010EGB真题Que.pdf"
document_role: note
year: 2010
locator_type: page
---

# OS2010EGB真题Que

<!-- page: 1 -->

选择题(共20 分，每题2 分)

1.
When the printing event which a process requested is finished, transition _______ will
occur.
A.
Running→ready
C. blocked→running
B.
running→blocked
D. blocked→ready
2.
Shared variables are those that ______
A.
can only be accessed by system processes
B.
can only be accessed by a lot of process mutual exclusively
C.
can only be accessed by user processes
D.
can be accessed by a lot of process
3.
It is provable that ______ scheduling algorithm is optimal if all the jobs are available
simultaneously.
A.
FCFS
B. SJF
C. Round-robin
D. Priority
4.
In a system, we require all processes to request all their resources before starting
execution. This is a method for preventing deadlock to attack the ________ condition.
A.
Mutual Exclusion
C. No Preemption
B.
Hold and Wait
D. Circular Wait
5.
Which of the following algorithm can result in external fragmentation problem?
A.
first fit
C. best fit
B.
next fit
D. worst fit
6.
Which of the following page replacement algorithm need to clear R bit periodically?
A.
FIFO
B. Second Chance
C. Aging
D. Working Set
7.
Writing commands to the device registers is done in which layers?
A.
Interrupt handlers
C. Device-independent OS software
B.
Device drivers
D. User-level I/O software
8.
“Device independence” means
A.
that devices are accessed dependent of their model and types of physical device.
B.
systems that have one set of calls for writing on a file and the console (terminal)
exhibit device independence.
C.
that files and devices are accessed the same way, independent of their physical
nature.
D.
None of the above
9.
The purpose of the open file call is to ______.
A.
search for the specified file in main memory
B.
copy the specified file into main memory
C.
search for the directory of the file in storage medium
D.
fetch the directory of the file into main memory
10. As for MS-DOS/Windows system, the attributes of file are stored in______.
A.
file
B. directory
C. directory entry
D. i-node
二、填空题(共10 分，每空1 分)

1.
Operating systems can be viewed from two viewpoints: __________________ and
_________________.
2.
If we implement thread in kernel space, __________ (process or thread) is a basic unit
of CPU utilization.
3.
The initial value of the semaphore S is 2. If the current value is -1, then there are _____
(how many) processes waiting.
4.
__________ scheduling algorithm can deal with the urgent process in time.
5.
A computer with a 32-bit address uses a two-level page table. Virtual addresses are split
into a 9-bit top-level page table system, an 11-bit second page table field, and an offset.
Each page is _______ bytes. And there are __________ (how many) pages in the
address space.
6.
Disk requests come in to the disk driver for cylinders 10, 22, 20, 2, 40, 6, and 38, in that
order. The arm is initially at cylinder 20. A seek takes 6 msec per cylinder moved. How
much seek time is needed for Elevator algorithm (initially moving upward)? _________
ms; And how much seek time is needed for Closest cylinder next algorithm? _______ms
7.
With __________ links, only the true owner of the file has a pointer to the i-node

《操作系统》试卷
第1 页共2 页

<!-- page: 2 -->

三、简答题(共20 分，每题5 分)

1.
Please describe the difference between a process and a program.
2.
Describe the concept of the critical resource and critical region, and give an example for
them each.
3.
Will Resource Allocation Graph with a cycle lead to deadlock? Why?
4.
How
many
disk
operations
are
needed
to
fetch
the
i-node
for
the
file
/usr/ast/workspace/mp1.tar? Why? Assume that the i-node for the root directory is in
memory, but nothing else along the path is in memory. Also assume that all directories
fit in one disk block.
四、综合题(共50 分)

1.
(12 分)There are 32 pages in the user space of virtual storage. Each page is 1K bytes size.

And the computer has 16K bytes main memory.
(1)
How many bits are needed to describe logical address space?
(2)
How many bits are needed to describe physical address space?
(3)
Assume one instance that the page 0, 1, 2, 3 was respectively loaded into frame page
5, 10, 4, 7, please calculate the physical address of the logical address 2,652 and
1,340(Decimal).

2.
(14 分) One tunnel, which is very narrow, allows only one passenger to pass once,
Please using semaphores to realize the following situation:

The passengers at one direction must pass the tunnel continuously.
Another
direction’s visitors can start to go through tunnel when no passengers want to pass the
tunnel from the opposite direction.
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
3

Please answer：

(1)
Is state safe?
(2)
If P2 Requests Resources (1,2,2,2) ，should system meet the demand and
allocate them to it?
4.
(12 分) In a batch system，the arrival time and burst time of three jobs are listed in

following table (time unit: hour in decimal ), if schedule with FCFS and SJF Algorithm
respectively:

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

(1)
Please calculate start time and finish time of each job.
(2)
Calculate average Turnaround Time.

《操作系统》试卷
第2 页共2 页
