---
source_id: operating-systems-021
course_id: operating_systems
title: "OS2013EG真题Que"
original_file: "学科资料/操作系统/往年卷/OS2013EG真题Que.pdf"
document_role: note
year: 2013
locator_type: page
---

# OS2013EG真题Que

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

I.
单选题(30 points, 2 points each)

For each question in this section, choose 1 answer. Choose the best answer. Fill your

choice in the following table.

1.
2.
3.
4.
5.
6.
7.
8.
9.
10.

_____________ ________

( 密封线内不答题)

11.
12.
13.
14.
15.

1.
(
) Which one is not the role or function of the operating system?

A. Extended machine
C. Providing abstractions to application programs

B.
Resource manager
D. Executing application programs

2.
(
) The ________ solution to the critical section problem will cause the situation

that a process running outside its critical region may block another process.

A. Disabling interrupts
C. Strict Alternation

B.
Peterson’s Algorithm
D. Test and Set Lock

3.
(
) We define a semaphore, whose initial value is 2 (this means that the number

of a certain resource is 2). Now, its value becomes to -1. Assume that M represents

the number of available resource and N shows the number of processes waiting for

this resource, then the value of M and N is _______ respectively.

《操作系统》试卷
第1 页共10 页

<!-- page: 2 -->

A. 1, 0
B. 0, 1
C. 2, 0
D. 0, 2

4.
(
) If the time slice is too large, round robin scheduling algorithm may

degenerate (退化) to _______scheduling algorithm. (2 mark)

A. First Come First Served (FCFS)
C. Shortest Job First (SJF)

B.
Priority
D. Multi-level feedback queue

5.
(
) A 128-MB memory is allocated in units of n bytes. We use a linked list to

keep track of free memory. Assume that memory consists of an alternating sequence

of segments and holes, each 64KB. Also assume that each node in the linked list

needs a 32-bit memory address, a 16-bit length, and a 16-bit next-node field. How

many bytes of storage are required in bitmap method?

A. 227/n
B. 224/n
C. 211
D. 214

6.
(
) If the page entry says that the page is not in RAM, it raises a
, an

exception telling the operating system that it needs to bring a page into memory.

A. page fault
C. array index out of bound

B.
trap
D. none of the above

7.
(
) Which of the following statements is true?

A. The use of a TLB for a paging memory system eliminates the need for keeping a

page table in memory.

B.
External fragmentation can be prevented by frequent use of compaction, but the

cost would be too high for most systems.

C.
The first fit allocation algorithm often creates small holes that can't be used.

D. More page frames always have fewer page faults.

8.
(
) Which one of the following methods in implementing file storage can support

random accesses easily?

A. Contiguous allocation
C. Linked list allocation using FAT

B.
Linked list allocation
D. none of the above

9. (
) The file-reference count is used for
.

A. counting number of bytes read from the file.

B.
counting number of open files.

C.
counting number of links pointing to a file.

《操作系统》试卷
第2 页共10 页

<!-- page: 3 -->

D. counting number of process accessing a file.

10. (
) How many disk operations are needed to read the third block of the file

/home/courses/os/test/A.doc. Assume that the i-node for the root directory is in

memory, but nothing else along the path is in memory.

A. 9
B. 10
C. 11
D. 12

11. (
) Requesting all resources initially is often used to prevent deadlock to attack

the ______ condition.

A. mutual exclusion
C. no preemption

B.
hold and wait
D. circular wait

12. Unix takes _____ to deal with deadlocks.

A. ostrich algorithm
C. banker’s algorithm

B.
deadlock detection algorithm
D. deadlock prevention algorithm

13. (
) “Device independence” means ________.

A. that devices are accessed dependent of their model and types of physical device.

B.
systems that have one set of calls for writing on a file and the console (terminal)

exhibit device independence.

C.
that files and devices are accessed the same way, independent of their physical

nature.

D. none of the above

14. (
) In which of the four I/O software layers is “Writing commands to the device

registers” is done?

A. Interrupt handlers
C. Device-independent OS software

B.
Device drivers
D. User-level I/O software

15. (
) Disk requests come in to the disk driver for cylinders 9, 35, 22, 16, 40, 11 and

2, in that order. Assume that the arm is initially at cylinder 12. What is the total

distance (in cylinders) that the disk arm moves to satisfy all the pending requests for

elevator algorithm (Assume that the arm is initially moving towards cylinder 0)?

A. 48
B.
66
C.
72
D. 75

《操作系统》试卷
第3 页共10 页

<!-- page: 4 -->

II. 简答题(20 points, 5 points each)

1.
What is the difference between a process and a thread? Describe some benefits using

threads.

2.
If a disk has double interleaving, does it also need cylinder skew in order to avoid

missing data when making a track-to-track seek? Explain your answer briefly.

《操作系统》试卷
第4 页共10 页

<!-- page: 5 -->

3.
In a paging system, the page table might be extremely large and requires much

memory space. Give 2 possible solutions and explain them briefly.

4.
What is the difference between hard link and symbolic link?

《操作系统》试卷
第5 页共10 页

<!-- page: 6 -->

III.
综合题(50 points, 10 points each)

1.
Consider a multi-level feedback queue in a single-CPU system. The first level (queue

0) is given a quantum of 4 ms (scheduled using RR), the second one a quantum of 8

ms (scheduled using RR), the third is scheduled using FCFS. Assume jobs arrive all

at time zero with the following CPU burst times (in ms): 4, 7, 12, 20, 25 and 30.

Show the Gantt chart for this system (5 points) and compute the average turnaround

time (5 points).

《操作系统》试卷
第6 页共10 页

<!-- page: 7 -->

2.
Consider a demand paging system with 3 frames. And the given page reference

sequence is A, D, B, E, A, E, F, G, A, G, E, F. How many page faults does each of

the FIFO, LRU, and the optimal page replacement algorithms generate? (Show your

answer step-by-step. A simple answer will receive no credit.)

《操作系统》试卷
第7 页共10 页

<!-- page: 8 -->

3.
Consider the following system snapshot using the data structures in the Banker's

algorithm, with resources A, B and C, and processes P0 to P4:

Max
Allocation
Available

Process

A
B
C
A
B
C
A
B
C

P0

7
5
3

0
1
0

3
3
2

P1

3
2
2

2
0
0

P2

9
0
2

3
0
0

P3

2
2
2

2
1
1

P4

4
3
3

0
0
2

Use Banker's algorithm to answer the following questions.

(1) What are the contents of the Need matrix? (2 points)

(2) Is the system in a safe state? Why? (You will receive no credit if only a Yes or Not

is given without an elaboration.) (4 points)

(3) If a request from process P1 arrives for additional resources of (1, 0, 2), can the

Banker's algorithm grant the request immediately? Why？(You will receive no

credit if only a Yes or Not is given without an elaboration.) (4 points)

《操作系统》试卷
第8 页共10 页

<!-- page: 9 -->

4.
Consider the following 3-process concurrent program which uses semaphores S1, S2,

and S3. The semaphore operation, which are sometimes called “wait” and “signal”,

are denoted here with the classical notation of “P” and “V”.

Process 1
Process 2
Process 3

L1: P(S3);

L2: P(S1);

L3: P(S2);

print(“T”);

print(“U”);

print(“B”);

V(S2);

V(S3);

V(S1);

goto L1;

goto L2;

goto L3;

(1) Suppose the initial values are S1=0, S2=0, S3=0. Is it possible for the processes to

cooperate to produce a string that begins with BBTTUTT? Explain your answer.

(5 points)

(2) Are there initial values that can be given to the semaphores so that the processes

cooperate to print the string BUTBUTBUTBU? If so, give the initial values (tell

which value is to be used for which semaphore) and explain how the string is

printed. (5 points)

《操作系统》试卷
第9 页共10 页

<!-- page: 10 -->

5.
A UNIX file system has 2-KB blocks and 32bit disk addresses. Each i-node contains

10 entries, including one single, one double, and one triple indirect entry. What is the

maximum file size?

《操作系统》试卷
第10 页共10 页
