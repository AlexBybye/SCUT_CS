---
source_id: computer-organization-006
course_id: computer_organization
title: "2025-2026 计算机组成原理与体系结构 A卷"
original_file: "学科资料/计算机组成原理/计组试卷（部分来自TZH）/2025-2026 计算机组成原理与体系结构 A卷.pdf"
document_role: past_exam
year: 2025
locator_type: page
---

# 2025-2026 计算机组成原理与体系结构 A卷

<!-- page: 1 -->

诚信应考，考试作弊将带来严重后果！

华南理工大学本科生期末考试

姓名
 学号
学院
 专业
 座位号

《计算机组成原理与体系结构》A 卷

2025-2026 学年第二学期

密
封
线

注意事项：1. 开考前请将密封线内各项信息填写清楚；

<!-- question: computer-organization-006-Q1 -->

2. 所有答案请直接答在试卷上；

<!-- question: computer-organization-006-Q2 -->

3. 考试形式：闭卷；

<!-- question: computer-organization-006-Q3 -->

4. 本试卷共 5 大题，满分 100 分，考试时间 120 分钟；

题 号
—
二
三
四
五
总分

得 分

( 密 封 线 内 不 答 题 )

By GuMianQAQ(没错，又是我！)

<!-- question: computer-organization-006-Q4 -->

一、选择题，每题只有一个正确选项。 共 20 题，每题 1 分，共 20 分.

<!-- question: computer-organization-006-Q5 -->

1. 下面不同的进制数中，真值最小的是 (
)

A. (10010110)2
B. 70H
C. (326)8
D. 127

<!-- question: computer-organization-006-Q6 -->

2.整数X采用8位定点整数补码表示，其机器数为11010101，X的真值是 (
)

A. -43

B. -53

C. -203

D. +53

<!-- question: computer-organization-006-Q7 -->

3.编辑文件时，对于输入的英文，文件中存储的是 ( )

A. 输入码
B. 国标码
C. 字模码
D. ASCII码

<!-- question: computer-organization-006-Q8 -->

4.设计算机主频为2GHz，其程序执行速度为400MIPS，则其执行时平均CPI是 (  )

A. 5

B. 4

C. 2

D. 1

<!-- question: computer-organization-006-Q9 -->

5. 下列8位编码中，符合奇校验且正确的是 (  )

A. 10110110
B. 11001100

《计算机组成原理与体系结构》试卷 第 1 页 共 7 页

<!-- page: 2 -->

C. 10101001
D. 01110001

<!-- question: computer-organization-006-Q10 -->

6.要设计一个32位的组内和组间均采用先行进位的多功能 ALU，需要 74181，74182 的数量
分别是

(
)

A. 4，1
B. 4，2
C. 8，1
D. 8，2

7.8位二进制补码 数10010110执行 算术右移两位后，结果为(   )

A. 00100101

B. 11100101

C. 00010110

D. 01100101

<!-- question: computer-organization-006-Q11 -->

8. 某SRAM地址线有20根，数据线有32根，则该芯片的存储容量为 (
)

A. 4MB
B. 1MB
C. 4GB
D. 32MB

<!-- question: computer-organization-006-Q12 -->

9. 某计算机有指令“ADD RO ,5”,其功能为(R0)+5→(R0)，其中RO为通用寄存器，则操作
数5在该指令中采用的是(   )

A. 寄存器寻址

B. 立即寻址

C. 隐含寻址

D. 直接寻址

<!-- question: computer-organization-006-Q13 -->

10. 下列存储器中，不可擦除的是 (  )

A. Flash

B. Mask ROM

C. EEPROM

D. EPROM

<!-- question: computer-organization-006-Q14 -->

11. 同一台计算机中，下列时间单位中最短的是(  )

A. 指令寻址
B. CPU周期
C. 存储周期
D. T周期

<!-- question: computer-organization-006-Q15 -->

12. ALU执行加法运算时，需要保存进位标志到(   )寄存器

A. PSW
B. PC
C. DR
D. IR

<!-- question: computer-organization-006-Q16 -->

13. 通常把取一条指令所需的一段时间称为微命令周期 (
)

A. 微命令周期
B. CPU周期
C. 指令周期
D. T周期

<!-- question: computer-organization-006-Q17 -->

14. 单级中断系统中，不在中断服务程序内执行的是(  )

《计算机组成原理与体系结构》试卷 第 2 页 共 7 页

<!-- page: 3 -->

A. 保护断点

B.

保护寄存器

C. 中断处理事件

D.

中断返回

<!-- question: computer-organization-006-Q18 -->

15.采用异步串行接口传送7为ASCII码，1位校验位，1位起始位，1位停止位。若字符传送速率

为120字符/s，则波特率为

A. 840波特
B. 1200波特

C. 960波特
D. 1080波特

<!-- question: computer-organization-006-Q19 -->

16. 超标量指令流水线与标量指令流水线相比，增加了(
)技术

A. 空间并行

B. 时间并行

C. 时间重叠

D. 以上说法均不正确

<!-- question: computer-organization-006-Q20 -->

17. 下列哪一个不是RISC处理器(
)

A. ARMv8

B. MIPS32

C. RISCV

D. Intel Core i7

<!-- question: computer-organization-006-Q21 -->

18. 下列指令中存在哪种数据相关

       LDA R2，B;M(B)→ R2，M(B)是存储器单元

       ADD R1，R2;(R2)+(R1)→R1

A. RAW
B. WAR
C. WAW
D. RAR

<!-- question: computer-organization-006-Q22 -->

19. DCI总线的数据传输方式属于(  )

A. 同步串行

B. 同步并行

C. 异步并行

D. 异步串行

<!-- question: computer-organization-006-Q23 -->

20. 下列选项中，属于对称多处理机（SMP）特征的是 (
)

A. 各处理机通过消息传递进行通信

B. 各处理机共享所有Cache

C. 采用松散耦合结构

D. 所有处理机共享同一主存和IO设施

《计算机组成原理与体系结构》试卷 第 3 页 共 7 页

<!-- page: 4 -->

<!-- question: computer-organization-006-Q24 -->

二、填空题。每空 2 分，共 20 分。

<!-- question: computer-organization-006-Q25 -->

1. 指令寻址的两种方式是
，
         。

<!-- question: computer-organization-006-Q26 -->

2. 指令包括
和地址码。

<!-- question: computer-organization-006-Q27 -->

3. 在计算机内存系统的RAM存储器中，不掉电数据就不丢失的是_______存储器，不掉电，数
据也可能丢失的是_______存储器。

<!-- question: computer-organization-006-Q28 -->

4. 单处理器系统中总线类型包括
，
和

。

<!-- question: computer-organization-006-Q29 -->

5. Cache是一种_______存储器，其原理是基于________原理

<!-- question: computer-organization-006-Q30 -->

6. 多体交叉存储器具有多个存储体，存储体的编址方式是______，其原理是______技术。

<!-- question: computer-organization-006-Q31 -->

三、简答题。 共 3 题，每题 8 分，共 24 分.

<!-- question: computer-organization-006-Q32 -->

1. 简述CPU的主要组成部分

<!-- question: computer-organization-006-Q33 -->

2. 一个完善的指令系统应满足哪几方面需求

《计算机组成原理与体系结构》试卷 第 4 页 共 7 页

<!-- page: 5 -->

<!-- question: computer-organization-006-Q34 -->

3. CPU有哪四个基本功能

<!-- question: computer-organization-006-Q35 -->

四、计算题。 共 2 题，每题 10 分，共 20 分.

<!-- question: computer-organization-006-Q36 -->

1. 某计算机系统的逻辑地址空间有64 KB空间，其中低端32 KB为连续的用户程序区，最
高端16 KB为系统保留区，全部采用16K×8位的SRAM存储器芯片构成。问：

<!-- question: computer-organization-006-Q37 -->

(1) 应采用哪种存储扩展方法，需要多少片SRAM芯片？
<!-- question: computer-organization-006-Q38 -->

(2) 画出该存储器的逻辑连线图。

<!-- question: computer-organization-006-Q39 -->

(3) 指出每个芯片的地址空间范围。

《计算机组成原理与体系结构》试卷 第 5 页 共 7 页

<!-- page: 6 -->

<!-- question: computer-organization-006-Q40 -->

2. 设某计算机按字节编址，虚拟存储器，采用“页目录-页表”索引的二级页表存储
管理方式，其地址结构为“页目录丨页表丨页内偏移”逻辑地址空间大小为1 GB, 物

理内存（主存）大小为128 MB, 页面大小为4 KB：

<!-- question: computer-organization-006-Q41 -->

(1) 逻辑地址应有多少位？物理地址应有多少位？
<!-- question: computer-organization-006-Q42 -->

(2) 假设一级页表（页目录）和二级页表（页表）的地址位数相等，各自有多少位？
<!-- question: computer-organization-006-Q43 -->

(3) 若访问虚拟地址，0x3B4A5678请给出其页目录、页表和页内偏移值（16进制表

示）

<!-- question: computer-organization-006-Q44 -->

五、设计题。 共 1 题，每题 16 分，共 16 分.

<!-- question: computer-organization-006-Q45 -->

1. 在一款32位嵌入式微处理器中，数据类型的位宽及浮点数表示标准定义如下：char

（8位）、short（16位）、int（32位）、float（32位 IEEE 754单精度浮点数）。
整数均以补码存储。阅读以下C语言代码：

short shX1, shX2;

int iX1, iX2;

float flx;

char c1 = -2, c2 = -1;

shX1 = c1 + c2;

shX2 = c1 - c2;

iX1 = c1 + c2;

iX2 = c1 - c2;

《计算机组成原理与体系结构》试卷 第 6 页 共 7 页

<!-- page: 7 -->

flx = 19.375 + shX1 + shX2 + iX1 + iX2;

while(1);

请结合C语言的整型提升（Integer Promotion）与类型转换规则，计算当程
序运行至 while(1); 时，以下变量在内存中对应的机器码（16进制形式）：

shX1
shX2
iX1
iX2
flx

《计算机组成原理与体系结构》试卷 第 7 页 共 7 页
