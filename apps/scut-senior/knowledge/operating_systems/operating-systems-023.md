---
source_id: operating-systems-023
course_id: operating_systems
title: "OS2018真题Que"
original_file: "学科资料/操作系统/往年卷/OS2018真题Que.doc"
document_role: note
year: 2018
locator_type: none
---

# OS2018真题Que

**诚信应考,考试作弊将带来严重后果！**

**华南理工大学期末考试**

**《操作系统》试卷(B)**

**注意事项：1.** **考前请将密封线内填写清楚；**

**2.** **所有答案请答在答题纸上；**

**3．考试形式：闭卷；**

**4.** **本试卷共** **四** **大题，满分100分，**	**考试时间120分钟**。

| **题** **号** | **一** | **二** | **三** | **四** | **五** | **总分** |
|---|---|---|---|---|---|---|
| **得** **分** |  |  |  |  |  |  |
| **评卷人** |  |  |  |  |  |  |

- 选择题(共20分，每题2分)
  - When the printing event which a process requested is finished, transition _______ will occur.
- Running→ready			C. blocked→running
- running→blocked		D. blocked→ready
  - Shared variables are those that ______
- can only be accessed by system processes
- can only be accessed by a lot of process mutual exclusively
- can only be accessed by user processes
- can be accessed by a lot of process
  - It is provable that ______ scheduling algorithm is optimal if all the jobs are available simultaneously.
- FCFS		B. SJF			C. Round-robin		D. Priority
  - In a system, we require all processes to request all their resources before starting execution. This is a method for preventing deadlock to attack the ________ condition.
- Mutual Exclusion			C. No Preemption
- Hold and Wait				D. Circular Wait
  - Which of the following algorithm can result in external fragmentation problem?
- first fit					C. best fit
- next fit					D. worst fit
  - Which of the following page replacement algorithm need to clear R bit periodically?
- FIFO		B. Second Chance		C. Aging		D. Working Set
  - Writing commands to the device registers is done in which layers?
- Interrupt handlers		C. Device-independent OS software
- Device drivers			D. User-level I/O software
  - “Device independence” means
- that devices are accessed dependent of their model and types of physical device.
- systems that have one set of calls for writing on a file and the console (terminal) exhibit device independence.
- that files and devices are accessed the same way, independent of their physical nature.
- None of the above
  - The purpose of the open file call is to ______.
- search for the specified file in main memory
- copy the specified file into main memory
- search for the directory of the file in storage medium
- fetch the directory of the file into main memory
  - As for MS-DOS/Windows system, the attributes of file are stored in______.
- file	 B. directory		C. directory entry		D. i-node
- 填空题(共10分，每空1分)
  - Operating systems can be viewed from two viewpoints: __________________ and _________________.
  - If we implement thread in kernel space, __________ (process or thread) is a basic unit of CPU utilization.
  - The initial value of the semaphore S is 2. If the current value is -1, then there are _____ (how many) processes waiting.
  - __________ scheduling algorithm can deal with the urgent process in time.
  - A computer with a 32-bit address uses a two-level page table. Virtual addresses are split into a 9-bit top-level page table system, an 11-bit second page table field, and an offset. Each page is _______ bytes. And there are __________ (how many) pages in the address space.
  - Disk requests come in to the disk driver for cylinders 10, 22, 20, 2, 40, 6, and 38, in that order. The arm is initially at cylinder 20. A seek takes 6 msec per cylinder moved. How much seek time is needed for Elevator algorithm (initially moving upward)? _________ ms; And how much seek time is needed for Closest cylinder next algorithm? ________ ms
  - With __________ links, only the true owner of the file has a pointer to the i-node.
- 简答题(共20分，每题5分)
  - Please describe the difference between a process and a program.
  - Describe the concept of the critical resource and critical region, and give an example for them each.
  - Will Resource Allocation Graph with a cycle lead to deadlock? Why?
  - How many disk operations are needed to fetch the i-node for the file /usr/ast/workspace/mp1.tar? Why? Assume that the i-node for the root directory is in memory, but nothing else along the path is in memory. Also assume that all directories fit in one disk block.
- 综合题(共50分)
  - (12分)There are 32 pages in the user space of virtual storage. Each page is 1K bytes size. And the computer has 16K bytes main memory.
1. How many bits are needed to describe logical address space?
1. How many bits are needed to describe physical address space?
1. Assume one instance that the page 0, 1, 2, 3 was respectively loaded into frame page 5, 10, 4, 7, please calculate the physical address of the logical address 2,652 and 1,340(Decimal).
  - (14分) One tunnel, which is very narrow,  allows  only one passenger to pass once, Please  using semaphores to realize the following  situation:

The passengers at one direction must pass the tunnel continuously.  Another direction’s visitors can start to go through tunnel when no passengers want to pass the tunnel from the opposite direction.
  - (12分)Basing on the Banker’s Algorithm，if exists the following allocation：

<table>
<tr><td>**Process**</td><td>**Allocation**</td><td>**Need**</td><td>**Available**</td></tr>
<tr><td></td><td>**A**</td><td>**B**</td><td>**C**</td><td>**D**</td><td>**A**</td><td>**B**</td><td>**C**</td><td>**D**</td><td>**A**</td><td>**B**</td><td>**C**</td><td>**D**</td></tr>
<tr><td>**P1**<br>**P2**<br>**P3**<br>**P4**<br>**P5**</td><td>0<br>1<br>1<br>0<br>0</td><td>0<br>0<br>3<br>0<br>0</td><td>3<br>0<br>5<br>3<br>1</td><td>2<br>0<br>4<br>2<br>4</td><td>0<br>1<br>2<br>0<br>0</td><td>0<br>7<br>3<br>6<br>6</td><td>1<br>5<br>5<br>5<br>5</td><td>2<br>0<br>6<br>2<br>6</td><td>1</td><td>6</td><td>2</td><td>3</td></tr>
</table>

Please answer：
1. Is state safe?
1. If P2 Requests Resources (1,2,2,2)，should system meet the demand and allocate  them  to it?
  - (12分) In a batch system，the arrival time and burst time of three jobs are listed in following table (time unit: hour  in  decimal ), if schedule with FCFS and SJF  Algorithm  respectively:

| Job | Arrival time | Burst time |
|---|---|---|
| 1 | 10.00 | 2.00 |
| 2 | 10.10 | 1.00 |
| 3 | 10.25 | 0.25 |

1. Please  calculate  start time and finish time of each  job.
1. Calculate average Turnaround Time.
