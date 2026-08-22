---
source_id: operating-systems-017
course_id: operating_systems
title: "OS2011EGB真题Que"
original_file: "学科资料/操作系统/往年卷/OS2011EGB真题Que.pdf"
document_role: note
year: 2011
locator_type: page
---

# OS2011EGB真题Que

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

一、单项选择题(20pts total, 2pts each)

1.
(
) What is the main advantage of multiprogramming?
A. Efficient use of the CPU
C.
Efficient use of disk

B.
Fast response
D. Short Turnaround time
2.
(
) Mutex is used for mutual exclusion problem. For 2 parallel processes, the
value of mutex cannot be______.
A. 1
B. 0
C. -1
D. -2

_____________ ________

( 密封线内不答题)

3.
(
) It is provable that _____ scheduling algorithm is optimal if all the jobs are
available simultaneously.
A. First Come First Served (FCFS)
C. Shortest Remaining Time Next (SRTN)
B.
Shortest Job First (SJF)
D. Priority

4.
(
) Suppose that the operating system is running a non-preemptive scheduler and
that process p is currently running. A context switch can occur
.
A. when p terminates or blocks
B. when another process unblocks
C. when another process enters
D. when the time quantum is exhausted

5.
(
) Which of the following statements is true?
A. The use of a TLB for a paging memory system eliminates the need for keeping a

page table in memory.
B.
External fragmentation can be prevented by frequent use of compaction, but the
cost would be too high for most systems.
C.
The first fit allocation algorithm often creates small holes that can't be used.
D. More page frames always have fewer page faults

6.
(
) The file-reference count is used for
.
A. counting number of bytes read from the file
B.
counting number of open files

《操作系统》试卷B
第1 页共9 页

<!-- page: 2 -->

C.
counting number of links pointing to a file
D. counting number of process accessing a file

7. As for Unix system, the attributes of file are stored in
.
A. file
B. directory
C. i-node
D. directory entry
8.
(
) “Device independence” means
.
A. that devices are accessed dependent of their model and types of physical device.
B.
systems that have one set of calls for writing on a file and the console (terminal)
exhibit device independence.
C.
that files and devices are accessed the same way, independent of their physical
nature.
D. none of the above

9.
(
) How much cylinder skew is needed for a 10000-rpm disk with a
track-to-track seek time of 800us? Assuming that the disk has 300 sectors of 512
bytes each on each track.
A. 24
B.
48
C.
20
D. 40

10.
(
) In a system, all resource requests must be made in numerical order. This is a
method for preventing deadlock to attack the
condition.
A. mutual exclusion
C. no preemption
B.
hold and wait
D. circular wait

二、简答题(20pts total, 5pts each)

1.
(5 pts) What is the biggest advantage of implementing threads in user space? What is
the biggest disadvantage?

《操作系统》试卷B
第2 页共9 页

<!-- page: 3 -->

2.
(5pts) In a virtual memory system, does a TLB miss imply a disk operation will
follow? Why or why not?

3.
(5 pts) How does MS-DOS implement random access to files?

4.
(5pts) A system has p processes each needing a maximum of m resources and a total
of r resources available. What condition must hold to make the system deadlock
free?

《操作系统》试卷B
第3 页共9 页

<!-- page: 4 -->

三、综合题(60pts total)

1.
(10pts) Men and women share a bathroom. But when a women is in the bathroom,
other women may enter, but no men, and vice versa. Please use semaphores to solve
this problem.

《操作系统》试卷B
第4 页共9 页

<!-- page: 5 -->

2.
(10 pts) Suppose two processes enter the ready queue with the following properties:
(1) Process 1 has a total of 8 units of work to perform, but after every 2 units of

work, it must perform 1 unit of I/O (so the minimum completion time of this
process is 12 units). Assume that there is no work to be done following the last
I/O operation.
(2) Process 2 has a total of 20 units of work to perform. This process arrives just

behind P1.
Show the resulting schedule for the Shortest-Job-First (preemptive) and the
Round-Robin algorithms. Assume a time slice of 4 units for RR. What is the
completion time of each process under each algorithm?

《操作系统》试卷B
第5 页共9 页

<!-- page: 6 -->

3.
(10pts) Consider the following system snapshot using the data structures in the
Banker's algorithm, with resources R0, R1, and R2, and processes P0 to P4:

Process
Max
Allocation
Available
R0 R1 R2 R3
R0 R1 R2 R3
R0 R1 R2 R3
P0
P1
P2
P3
P4

7
0
2
1
1
6
5
0
3
3
4
6
1
5
6
2
2
4
3
2

4
0
0
1
1
1
0
0
1
0
4
5
0
4
2
1
0
3
1
2

3
2
2
1

Using Banker's algorithm answer the following questions.
(1) What are the contents of the Need matrix?
(2) Is the system in a safe state? Why?
(3) If a request from process P2 arrives for additional resources of (0,2,0,0), can the

Banker's algorithm grant the request immediately? Why? Show the new system
state and other criteria.

《操作系统》试卷B
第6 页共9 页

<!-- page: 7 -->

4.
(10 pts) Consider a demand paging system with three frames. And the given page
reference sequence is A, D, B, E, A, E, F, G, A, G, E, F. How many page faults does
each of the LRU, FIFO, and Optimal page replacement algorithms generate? (Show
your work step-by-step. A simple answer will receive no credit.)

《操作系统》试卷B
第7 页共9 页

<!-- page: 8 -->

5.
(10 pts) A certain file system uses 2-KB disk blocks. And the i-nodes contain 8 direct
entries, one single and one double indirect entry each. The size of each entry is 4 B.
Answer the following questions:
(1) What is the maximum file size of this file system?
(2) How much disk space a 128-MB file actually occupied? (including all the direct

and indirect index blocks)

《操作系统》试卷B
第8 页共9 页

<!-- page: 9 -->

6.
(10 pts) Disk requests come in to the disk driver for cylinders 10, 22, 20, 2, 40, 6, and
38, in that order. Assume that initially the disk read/write arm is at cylinder 20.
(1) Using Shortest Seek First (SSF) algorithm, give the order in which the cylinders

are serviced and the total cylinders the arm moves.
(2) Using elevator algorithm, give the order in which the cylinders are serviced and

the total cylinders the arm moves (initially moving upward).

《操作系统》试卷B
第9 页共9 页
