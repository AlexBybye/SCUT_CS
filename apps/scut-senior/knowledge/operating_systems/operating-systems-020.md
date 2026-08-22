---
source_id: operating-systems-020
course_id: operating_systems
title: "OS2012EGB真题Que"
original_file: "学科资料/操作系统/往年卷/OS2012EGB真题Que.pdf"
document_role: note
year: 2012
locator_type: page
---

# OS2012EGB真题Que

<!-- page: 1 -->

… … … … … … … … … … … … … … … 密… … … … … … … … … … … … … … … … … … 封… … … … … … … … … … … … … … … 线… … … … … … … … … … … … … …

诚信应考,考试作弊将带来严重后果！

华南理工大学期末考试

《操作系统》试卷B

姓名
学号
学院
专业
座位号

注意事项：1. 考前请将密封线内填写清楚；

2. 所有答案请答在答题纸上；
3．考试形式：闭卷；

4. 本试卷共三大题，满分100 分，考试时间120 分钟。
题号
一
二
三
总分
得分
评卷人

一、单项选择题(30pts total, 2pts each)

1.
(
) The operating system is not responsible for the following activities in
connection with process management? _____
.
A. Suspending and resuming processes
B.
Providing mechanism for process synchronization
C.
Handling deadlock
D. Keeping track of free memory

_____________ ________

( 密封线内不答题)

2.
(
) Which of the following process schedule algorithm can lead to starvation?
_______ .
A. FCFS
B. Round Robin
C. SJF
D. Guaranteed Scheduling

3.
(
) _______ register contains the size of a process.
A. Base
B. Limit
C. Index
D. Stack pointer

4.
(
) Deadlock can arise if four conditions hold simultaneously. Which of the
following is not one of these four conditions? ________.
A. mutual exclusion
B. busy waiting
C. hold and wait

D. no preemption
E. circular wait

5.
(
) Let graph represent “resource allocation graph”. Which statement is wrong?
________.
A. If graph contains cycle, and there is only one instance per resource type, then

there is deadlock.
B.
If graph contains cycle, and there can be several instances per resource type, then
there may or may not have deadlock
C.
If graph contains no cycle, then no deadlock
D. If no deadlock, then graph contains no cycle

6.
(
) The ability of a computer system to switch execution among several jobs that
are in memory at the same time is called ______.

《操作系统》试卷B
第1 页共10 页

<!-- page: 2 -->

A. time slicing
C. multiprocessing
B. multiprogramming
D. multitasking

7.
(
) In the readers-writers problem, processes p and q are allowed to
simultaneously access the shared resource if and only if _____.
A. p and q are both reading.
C. Either p or q or both is reading
B. p and q are both writing
D. Either p or q or both is writing

8.
(
) Suppose that a machine has 48-bit virtual address and 32-bit physical address.
If pages are 4KB, how many entries are in the page table if it has only a single level?
A. 227
B. 216
C. 224
D. 236

9.
“Computing the track, sector, and head for a disk read” is done in which layers?
A. Interrupt handlers
C. Device-independent OS software
B.
Device drivers
D. User-level I/O software

10. (
) If there are no name collisions in a file system, the easiest method is to
use______.
A. single-level directory system
C.
single-level or two-level directory system
B.
two-level directory system
D. hierarchical directory system

11. (
) A computer has four page frames. The time of loading, time of last access,
and the R and M bits for each page are as shown below (the times are in clock ticks):

Page
Loaded
Last ref.
R
M
0
126
280
1
0
1
230
265
0
1
2
140
270
0
0
3
110
285
1
1
Which page will NRU, LRU and second chance replace respectively?
A.
2, 2,1
B. 2,3,1
C.
2,1,2
D.
3,1,2

12. (
) A computer has six tape drives, with n processes competing for them. Each
process may need two drives. For which values of n is the system deadlock free?
A. 8
B. 7
C. 6
D. 5

13. (
) The beginning of a free space bitmap looks like this after the disk partition is
first formatted: 1000 0000 0000 (the first block is used by the root directory). The
system always searches for free blocks starting
at the lowest-numbered block, so
after writing file A, which uses six blocks, the bitmap looks like this: 1111 1110 0000
0000. Show the bitmap after the following additional action: file B is written, using
five blocks.
A. 1000 0001 1111 0000
C. 1111 1111 1111 1100
B. 1111 1111 1111 0000
D. 1111 1110 0000 1100

14. (
) In which of the four I/O software layers is “Writing commands to the device
registers” is done?
A. Interrupt handlers
C. Device-independent OS software

《操作系统》试卷B
第2 页共10 页

<!-- page: 3 -->

B.
Device drivers
D. User

15. (
) How much cylinder skew is needed for a 7200-rpm disk with a track-to-track
seek time of 1msec? Assuming that the disk has 200 sectors of 512 bytes each on
each track. ______
A. 12
B.
24
C.
48
D. 40

二、简答题(15pts total, 5pts each)

1.
(5 pts) List at least three key differences between user-level threads and kernel-level
threads.

2.
(5pts) In a virtual memory system, does a TLB miss imply a disk operation will
follow? Why or why not?

《操作系统》试卷B
第3 页共10 页

<!-- page: 4 -->

3.
(5 pts) How many disk operations are needed to open the file /usr/student/lab/test.doc?
Why? (Assume that nothing else along the path is in memory. Also assume that all
directories fit in one disk block. )

三、综合题(55pts total)

1. (10pts) Suppose that in a bus, the activities of the driver and the conductor are as
following:

driver:
conductor:

Start the bus;
close the door;

Drive the bus;
sell the tickets;

Stop the bus;
open the door;

Please use semaphore and P/V operations to synchronize the activities of them.

《操作系统》试卷B
第4 页共10 页

<!-- page: 5 -->

《操作系统》试卷B
第5 页共10 页

<!-- page: 6 -->

2.
(8pts) Five batch jobs A through E, arrive at a computer center at almost the same
time. They have estimated running times of 10, 6, 2, 4, and 8 minutes. Their
(externally determined) priorities are 3, 5, 2, 1, and 4, respectively, with 5 being the
highest priority. For each of the following scheduling algorithms, determine the mean
process turnaround time. Ignore process switching overhead.

Job
Arrival time
Execution time
Priority
A
0
10
3
B
0
6
5
C
0
2
2
D
0
4
1
E
0
8
4

(1) Round robin

(2) Priority scheduling

(3) First-come, first-served (run order 10, 6, 2, 4, 8).

(4) Shortest job first

《操作系统》试卷B
第6 页共10 页

<!-- page: 7 -->

3.
(10pts) A system has five processes and four allocatable resources. The current
allocation and additional needs are as follows:

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

Please answer the following questions:
(1) Is this state safe? Why?

(2) The request (1,2,2,2) of P3 can be granted or not? Why?

《操作系统》试卷B
第7 页共10 页

<!-- page: 8 -->

4.
(10 pts) Given a 36-bit processor with 4 active
processes being executed concurrently. Please
answer the following questions. Show all the
addresses of your answer in hex number. If a
translation cannot be found, enter page fault.

V
PID
VPN
1
9
0x0DF0
1
A
0x3630
1
C
0x1B70
1
C
0x37C1
0
F
0x1F04
1
A
0x3640
1
9
0x1FFF
1
A
0x23A4
1
9
0x3004
1
A
0x0D7C
1
C
0x0DF0
0
B
0x1F04
1
A
0x0DF0
1
9
0x020D
1
A
0x31A2
1
C
0x07C1

(1) Assume an inverted page table (IPT) is used

by the OS. The IPT is shown below (Only
Valid, PID and VPN are shown). Each page
size is 4MB. What “virtual address” of which
“process” maps to the physical address
“0x363055B”?

(2) Now we switch to use an index-based linear

page table, how much memory (in KB) is
required for just process A? Assume each
page table entry (PTE) contains a valid and
dirty bit.

《操作系统》试卷B
第8 页共10 页

<!-- page: 9 -->

5.
(8 pts) A UNIX file system has 1-KB blocks and 32bit disk addresses. What is the
maximum file size if i-nodes contain 10 direct entries, and one single, double, and
triple indirect entry each?

《操作系统》试卷B
第9 页共10 页

<!-- page: 10 -->

6.
(9pts) Suppose that a disk drive has 300 cylinders, numbered 0 to 299. The drive is
currently serving a request at cylinder 143. The queue of pending requests, in FIFO
order, is

86, 147, 291, 18, 95, 151, 12, 175, 30
Starting from the current head position, what is the total distance (in cylinders) that
the disk arm moves to satisfy all the pending requests, for each of the following
disk-scheduling algorithms?
(1)
First-Come First-Served (FCFS)
(2)
Shortest Seek First (SSF)
(3)
Elevator Algorithm (Assume that initially the arm is moving towards cylinder 0)

《操作系统》试卷B
第10 页共10 页
