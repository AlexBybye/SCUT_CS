---
source_id: algorithm-design-and-analysis-004
course_id: algorithm_design_and_analysis
title: 0-introduction
original_file: "学科资料/算法设计与分析/PPT-英文版/0-introduction.pdf"
document_role: note
year: 
locator_type: page
---

# 0-introduction

<!-- page: 1 -->

Design and Analysis ofAlgorithms

Course Introduction

Si  Wu

School of CSE, SCUT

cswusi@scut.edu.cn

TA: 1684350406@qq.com

1

<!-- page: 2 -->

Outline

Part I: About thecourse

Part II: Aboutalgorithms

– What arealgorithms?
– Why are they important tostudy?

2

<!-- page: 3 -->

Part I: About thecourse

3

<!-- page: 4 -->

Course Information

Lecturer:

Prof. Si Wu (吴斯)
E-mail:cswusi@scut.edu.cn

Office: B3-302

TeachingAssistants：

Mr. Wen Xue(薛文)

E-mail:  1684350406@qq.com
Office: B3-535
If you have any questions, please feel free to contact me by email.
Pleaselist your nameand student IDwhenyousendmeanemail….

4

<!-- page: 5 -->

Course Information

Reference

Algorithms Design Techniques and Analysis.
(Saudi Arabia) M. H.Alsuwaiyel.
Publishing House of ElectronicIndustry.

Introduction to Algorithms, 3rded.
T. H. Cormen, C. E. Leiserson, R. L.
Rivest, C. Stein, MIT Press.

5

![image](assets/assets/algorithm-design-and-analysis-004/image-001.jpeg)

![image](assets/assets/algorithm-design-and-analysis-004/image-002.jpeg)

<!-- page: 6 -->

Main Topics

• Algorithm Analysis
• Sorting algorithms
• Recurrence
• Divide and Conquer
• Dynamic Programming
• Greedy Algorithms
• Linear Programming
• Network Flow
• Approximation

6

<!-- page: 7 -->

Course Information

Couse Time：64 Teaching hours

Lecture: 3:50pm-5:25pm, Wednesday, Weeks 1-10, A2302

7:00pm-9:25pm, Friday, Weeks 1-9, A2302
Lab: TBD

Final Grade：

Performance + Experiments (30%)

Final  Examination (70%)

7

<!-- page: 8 -->

Lecture

Teaching Session

Tutorial Session：

8

![image](assets/assets/algorithm-design-and-analysis-004/image-003.jpeg)

![image](assets/assets/algorithm-design-and-analysis-004/image-004.png)

<!-- page: 9 -->

Course Information

Online Judge：

– http://www.scut.edu.cn/ACM/

(South China  University of Technology)
– http://acm.zju.edu.cn/onlinejudge/

(Zhejiang  University)
– http://poj.org (Peking University)

9

<!-- page: 10 -->

About the Flavor

It’s more of a math flavor thana programming

one.

You will need to write pseudo-code,and

implement it usingC/C++…

You will design and analyze, think andprove

(rather thancoding)

10

<!-- page: 11 -->

Prerequisites

Officially:

Discrete Mathematics
Programming
Data Structures

Effectively: Basic mathematical maturity

functions, polynomial, exponential;
proof by induction;
basic data structure operations (stack, queue, …);
basic math manipulations…

11

<!-- page: 12 -->

Experiment Policy

Discussions and searchingon the web areallowed in general

But you have to implement the solution by yourself

And you should fully understand your codes.

12

<!-- page: 13 -->

Zero Tolerance for Cheating/Plagiarism

You may get 0 score for this course

Will check your codes by software; scores of both

the code provider and the copier will be 0 once the
cheating/plagiarism behavior isconfirmed

13

<!-- page: 14 -->

Suggestions

In class:

– Try to come on time.
– Try your best to get more involved in theclass.
– Please don’t chitchat.
–Treat experimentsseriously

14

<!-- page: 15 -->

Suggestions

Your suggestions will be highlyappreciated.

– Please send me/TA an e-mail

Any questions about thecourse?

My questions:

– What are yourgoals?
– Whatdoyouliketo learnfrom this course?
– What excite you the most ingeneral?

15

<!-- page: 16 -->

Part II: About algorithms

16

<!-- page: 17 -->

Factors of Programming

• Programming Languages？

18

17

![image](assets/assets/algorithm-design-and-analysis-004/image-005.png)

![image](assets/assets/algorithm-design-and-analysis-004/image-006.jpeg)

<!-- page: 18 -->

Algorithms

• Algorithm. (webster.com)

-A well-defined computational procedure that takes some
value, or set of values, as input and produces some value, or
set of values, as output.

-Broadly: a step-step procedure for solving a problem or
accomplishing some end especially by a computer.

Input
Algorithm
Output

-Issues: correctness, efficiency (amount of work done and
space used), storage, simplicity, clarity, optimality, etc.

18

<!-- page: 19 -->

Importance of Algorithms

Problem: sorting 10,000,000integers

– Case 1: Computer A executes one billion instructions per

second(1GHz), an algorithm taking time roughly equal to 2n2 to
sort n integers.
– Case 2: Computer B executes one hundred million instructions

per second(100MHz), an algorithm taking time roughly equal to
50nlogn to sort n integers.


Case 1:

200000seconds 55hours
2(107)2instructions

109instructions/second


Case 2:

105seconds
108instructions/second
50107 log107 instructions

19

<!-- page: 20 -->

Importance of Algorithms

20

23

![image](assets/assets/algorithm-design-and-analysis-004/image-007.png)

<!-- page: 21 -->

21

![image](assets/assets/algorithm-design-and-analysis-004/image-008.jpeg)

<!-- page: 22 -->

22

![image](assets/assets/algorithm-design-and-analysis-004/image-009.jpeg)

<!-- page: 23 -->

Data!! Data!!Data!!

23

![image](assets/assets/algorithm-design-and-analysis-004/image-010.jpeg)

<!-- page: 24 -->

Various Problems

Human Genome Project

– 100,000 genes，sequences of the 3 billionchemical base

pairs

Internet

– Finding good routes on which the data willtravel
– Searchengine

Electronic commerce

– Public-key cryptography and digital signatures

Manufacturing

– Allocate scarce resources in the most beneficialway

…

24

<!-- page: 25 -->

About the Course

Design andAnalysis

– How can I propose an algorithm for a specific

problem?
– Is the algorithm goodenough?

25

<!-- page: 26 -->

Analysis of Algorithms

• The theoretical study of computer-program performance
and resource usage.

• What’s more important than performance?

- modularity
- correctness
- maintainability
- functionality
- robustness

- user-friendliness

- programmertime
- simplicity
- extensibility

- reliability

26
