---
source_id: embedded-systems-019
course_id: embedded_systems
title: "作业内容-2025"
original_file: "学科资料/嵌入式/嵌入式复习方向/作业内容-2025.docx"
document_role: note
year: 2025
locator_type: none
---

# 作业内容-2025

1. 汇编部分：

（1）运行以下程序后:

MOV  r0, #10

MOV  r1, #3

ADD  r0, r0, r1

MOV  r2,#10h

ADD  r2, r2, r1

ADD  r3, r1, #2

AND  r4, r1, r0

SUB  r5, r0, r1

CMP  r0,r1

MRS  r6,CPSR

CMP  r1,r0

MRS  r7,CPSR

MUL  r8, r0, r1

MVN  r9,#0x88000000

MOV  r10,#0x12800000

r0=      r1=       r2=        r3=

r4=      r5=       r6=        r7=

r8=      r9=       r10=

（2）运行以下程序后:

MOV  R0,#0x100

MOV  R1,#0x100

LDR  R2,=0x66122345

STR  R2,[R0]

LDRB  R3,[R0,#2]

LDRB  R4,[R0]

LDRB  R5,[R1,#2]!

LDRB  R6,[R1]

LDRB  R7,[R0],#2

LDRB  R8,[R0]

LDRH  R9,0x100

小端模式：

r0=      r1=       r2=        r3=

r4=      r5=       r6=        r7=

r8=      r9=

大端模式：

r0=      r1=       r2=        r3=

r4=      r5=       r6=        r7=

r8=      r9=
1. 编程题 （可利用proteus仿真实现）

（1）编写程序控制2个LED全亮和2个LED全灭的代码，包括初始化代码和运行代码，2个引脚可以考虑选择PA0和PA1。

（2）利用外部中断实现按钮控制灯亮灭程序，按键接PA8，按键按下时PA8为低电平；LED接PB1，当PB1为高电平时，LED灯亮；按键没有按下时，熄灭LED。

（3）编写程序使用USART1串口，实现可接收任意字节的串口通信程序，并可把接收到的数据显示在串口终端上。

（4）编写利用STM32通用定时器精确延时10ms的主要代码。

（5）编写程序：使用STM32芯片采用查询和中断两种方式采集ADC1通道5中的外部电压。计算当STM32芯片ADC的数字值为819时，对应的模拟电压是多少，写出计算过程。

（6）编写程序利用STM32 DMA实现对ADC通道5外部电压的采集。
