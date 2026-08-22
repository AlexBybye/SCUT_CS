---
source_id: embedded-systems-017
course_id: embedded_systems
title: "嵌入式期末真题回忆版无答案"
original_file: "学科资料/嵌入式/往年卷/嵌入式期末真题回忆版无答案.pdf"
document_role: past_exam_answer
year: 
locator_type: page
---

# 嵌入式期末真题回忆版无答案

<!-- page: 1 -->

嵌入式期末真题回忆版复原（仅题目版）

嵌入式系统期末考试真题回忆版复原

仅题目版

注意事项：1. 本卷依据手写真题回忆版整理；2. 题目顺序按图片可辨内容编排；3. 本版本仅保留题目，

不含答案与解析。

题号
一
二
三
四
五
总分

得分

<!-- question: embedded-systems-017-Q1 -->

一、基础题（选择、判断、填空类）

<!-- question: embedded-systems-017-Q2 -->

1. 下列哪一项属于嵌入式系统的特点？

A. 低功耗

B. 实时性

C. 专用性

D. 以上都是

<!-- question: embedded-systems-017-Q3 -->

2. STM32 的复位方式不包括下列哪一项？

A. 上电复位

B. 系统复位

C. 备份域复位

D. 软件复位

<!-- question: embedded-systems-017-Q4 -->

3. STM32F103 支持从下列哪一项启动？

A. 以太网

B. USB

C. 内置 SRAM

D. SD 卡

<!-- question: embedded-systems-017-Q5 -->

4. Cortex-M3 处理器中，程序计数器 PC 对应哪个寄存器？

A. R13

B. R14

C. R15

D. xPSR

<!-- question: embedded-systems-017-Q6 -->

5. STM32 中，内核与片上外设之间主要通过下列哪一种结构进行通信？

A. I²C

B. SPI

C. AHB

D. UART

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 2 -->

嵌入式期末真题回忆版复原（仅题目版）

<!-- question: embedded-systems-017-Q7 -->

6. 若要将 STM32 的某个 GPIO 引脚配置为外部中断输入，需要完成哪些设置？

<!-- question: embedded-systems-017-Q8 -->

7. 设置 STM32 定时器周期，操作 ______ 寄存器。

<!-- question: embedded-systems-017-Q9 -->

8. 看门狗定时器如果长时间不喂狗，会发生什么？

<!-- question: embedded-systems-017-Q10 -->

9. I²C 总线属于哪种通信方式？

<!-- question: embedded-systems-017-Q11 -->

10. 下列哪些属于 RTC 的典型应用？

A. PWM 输出

B. 普通计数

C. 日历

D. 闹钟唤醒

<!-- question: embedded-systems-017-Q12 -->

二、填空与简答题

<!-- question: embedded-systems-017-Q13 -->

11. Cortex-M3 内核是 ______ 位，采用 ______ 总线结构。

<!-- question: embedded-systems-017-Q14 -->

12. STM32 的中断优先级由哪两部分组成？如何判断优先级高低？

<!-- question: embedded-systems-017-Q15 -->

13. EXTI 外部中断有哪三种触发方式？

<!-- question: embedded-systems-017-Q16 -->

14. STM32 中可用于定时的模块有：______、______。

<!-- question: embedded-systems-017-Q17 -->

15. DMA 的传输方向有：______、______、______、______。

<!-- question: embedded-systems-017-Q18 -->

16. 写出 PWM 输出等效电压的计算公式。

<!-- question: embedded-systems-017-Q19 -->

17. 阅读下列 ARM 汇编程序，写出执行后 R0、R1、R2、R3 的值，并写出地址 0x404~0x407 中存

放的内容。

程序代码：

MOV  R0, #0x400

ADD  R1, R0, #0x04

LDR  R2, =0x12345678

STR  R2, [R1]!

SUB  R1, #0x02

LDRB R3, [R1]

<!-- question: embedded-systems-017-Q20 -->

三、简答题

<!-- question: embedded-systems-017-Q21 -->

18. 简述 STM32 与普通单片机的区别。

<!-- question: embedded-systems-017-Q22 -->

19. 定时器中哪些脚可以作为计数输入？说明计数实现过程。

<!-- question: embedded-systems-017-Q23 -->

20. 简述 STM32 中断优先级的含义。

<!-- question: embedded-systems-017-Q24 -->

21. 简述汇编语言在嵌入式开发中的作用，并列举三种寻址方式且举例说明。

示例代码：

立即寻址：      MOV R0, #10

寄存器寻址：    MOV R0, R1

寄存器间接寻址：LDR R0, [R1]

基址加偏移寻址：LDR R0, [R1, #4]

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 3 -->

嵌入式期末真题回忆版复原（仅题目版）

<!-- question: embedded-systems-017-Q25 -->

22. 列举一个可以运行在 MCU 上的嵌入式操作系统，并说明任务管理模块的作用。

<!-- question: embedded-systems-017-Q26 -->

四、综合题一：ADC 测电压并控制 PA6 上 LED 亮灭

<!-- question: embedded-systems-017-Q27 -->

23. 使用 STM32 的 ADC 测量外部模拟电压，并根据测得电压控制 PA6 引脚上的 LED 灯亮灭。请完

成下列问题：

<!-- question: embedded-systems-017-Q28 -->

（1）说明 ADC 测电压并控制 LED 的基本流程；

<!-- question: embedded-systems-017-Q29 -->

（2）若 ADC 参考电压为 3.3V，分辨率为 12 位，输入电压为 0.825V，求对应的数字量；

<!-- question: embedded-systems-017-Q30 -->

（3）写出 PA6 初始化代码；

<!-- question: embedded-systems-017-Q31 -->

（4）写出控制 LED 亮灭的函数；

<!-- question: embedded-systems-017-Q32 -->

（5）描述如何使用 DMA 实现 ADC 数据采集。

代码：

void LED_Init(void)

{

    GPIO_InitTypeDef GPIO_InitStructure;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_6;

    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;

    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;

    GPIO_Init(GPIOA, &GPIO_InitStructure);

}

代码：

void LED_On(void)

{

    GPIO_SetBits(GPIOA, GPIO_Pin_6);

}

void LED_Off(void)

{

    GPIO_ResetBits(GPIOA, GPIO_Pin_6);

}

<!-- question: embedded-systems-017-Q33 -->

五、综合题二：测外部脉冲宽度并通过串口发送到电脑

<!-- question: embedded-systems-017-Q34 -->

24. 使用 STM32 测量外部输入脉冲宽度，并通过串口每 800ms 将测得的宽度发送到电脑串口助手。

请完成下列问题：

<!-- question: embedded-systems-017-Q35 -->

（1）PA3、PA4、PA5 中哪个引脚可以测外部脉冲宽度？使用哪个定时器通道？

<!-- question: embedded-systems-017-Q36 -->

（2）根据 800ms 定时要求，设置 prescaler 和 reload；

<!-- question: embedded-systems-017-Q37 -->

（3）说明用查询方式实现 800ms 定时发送的方法；

<!-- question: embedded-systems-017-Q38 -->

（4）说明用中断方式实现 800ms 定时发送的方法；

<!-- question: embedded-systems-017-Q39 -->

（5）使用 UART4 作为串口，根据串口助手参数写出 UART4 初始化代码。

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 4 -->

嵌入式期末真题回忆版复原（仅题目版）

查询方式代码：

while (1)

{

    if (TIM_GetFlagStatus(TIMx, TIM_FLAG_Update) != RESET)

    {

        TIM_ClearFlag(TIMx, TIM_FLAG_Update);

        Send_Width();

    }

}

中断方式代码：

void TIMx_IRQHandler(void)

{

    if (TIM_GetITStatus(TIMx, TIM_IT_Update) != RESET)

    {

        TIM_ClearITPendingBit(TIMx, TIM_IT_Update);

        Send_Width();

    }

}

UART4 初始化代码：

void UART4_Init(void)

{

    GPIO_InitTypeDef GPIO_InitStructure;

    USART_InitTypeDef USART_InitStructure;

    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOC, ENABLE);

    RCC_APB1PeriphClockCmd(RCC_APB1Periph_UART4, ENABLE);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;

    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;

    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;

    GPIO_Init(GPIOC, &GPIO_InitStructure);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_11;

    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;

    GPIO_Init(GPIOC, &GPIO_InitStructure);

    USART_InitStructure.USART_BaudRate = 115200;

    USART_InitStructure.USART_WordLength = USART_WordLength_8b;

    USART_InitStructure.USART_StopBits = USART_StopBits_1;

    USART_InitStructure.USART_Parity = USART_Parity_No;

    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;

    USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;

    USART_Init(UART4, &USART_InitStructure);

    USART_Cmd(UART4, ENABLE);

}

— 由回忆版整理，答案以课堂与教材要求为准 —
