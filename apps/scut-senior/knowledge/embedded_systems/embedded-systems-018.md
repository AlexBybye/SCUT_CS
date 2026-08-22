---
source_id: embedded-systems-018
course_id: embedded_systems
title: "嵌入式期末真题回忆版有答案"
original_file: "学科资料/嵌入式/往年卷/嵌入式期末真题回忆版有答案.pdf"
document_role: past_exam_answer
year: 
locator_type: page
---

# 嵌入式期末真题回忆版有答案

<!-- page: 1 -->

嵌入式期末真题回忆版复原（答案与解析版）

嵌入式系统期末考试真题回忆版复原

答案与解析版

注意事项：1. 本卷依据手写真题回忆版整理；2. 题目顺序按图片可辨内容编排；3. 题目下方附答案与解

析；4. 最后一页附完整题目列表。

题号
一
二
三
四
五
总分

得分

<!-- question: embedded-systems-018-Q1 -->

一、基础题（选择、判断、填空类）

1. 下列哪一项属于嵌入式系统的特点？

A. 低功耗

B. 实时性

C. 专用性

D. 以上都是

答. D

解. 嵌入式系统通常面向特定应用，具有专用性强、实时性要求高、低功耗、体积小、可靠性高、资源

受限等特点。因此四个选项中 A、B、C 均正确。

2. STM32 的复位方式不包括下列哪一项？

A. 上电复位

B. 系统复位

C. 备份域复位

D. 软件复位

答. D

解. STM32 常见复位大类包括电源复位、系统复位和备份域复位。软件复位可以作为系统复位的一种来

源，但若按复位方式的大类划分，它不与上电复位、系统复位、备份域复位并列。

3. STM32F103 支持从下列哪一项启动？

A. 以太网

B. USB

C. 内置 SRAM

D. SD 卡

答. C

解. STM32F103 的启动方式由 BOOT0、BOOT1 引脚决定，常见启动区域有主 Flash、系统存储器和

内置 SRAM。以太网、USB、SD 卡不是 STM32F103 通过 BOOT 引脚直接选择的启动区域。

4. Cortex-M3 处理器中，程序计数器 PC 对应哪个寄存器？

A. R13

B. R14

C. R15

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 2 -->

嵌入式期末真题回忆版复原（答案与解析版）

D. xPSR

答. C

解. Cortex-M3 中 R13 是 SP，R14 是 LR，R15 是 PC。因此程序计数器 PC 对应 R15。

5. STM32 中，内核与片上外设之间主要通过下列哪一种结构进行通信？

A. I²C

B. SPI

C. AHB

D. UART

答. C

解. STM32 内核与片上外设之间通过内部总线系统连接，常见总线有 AHB、APB1、APB2。I²C、

SPI、UART 是通信接口，不是片上内部总线。

6. 若要将 STM32 的某个 GPIO 引脚配置为外部中断输入，需要完成哪些设置？

答. 使能 GPIO 和 AFIO 时钟，配置 GPIO 为输入模式，配置 GPIO 与 EXTI 线的映射，设置 EXTI 触

发方式，配置 NVIC 优先级，使能 EXTI 中断线，并编写中断服务函数。

解. GPIO 引脚本身只是普通输入输出口。若要产生外部中断，需要通过 AFIO 将 GPIO 映射到 EXTI

线，再由 EXTI 产生中断请求，并由 NVIC 管理中断响应。

7. 设置 STM32 定时器周期，操作 ______ 寄存器。

答. ARR（自动重装载）寄存器。若计算完整定时时间，通常还要配合 PSC（预分频）寄存器。

解. ARR 决定计数器计到多少后产生更新事件，PSC 决定定时器计数频率。定时周期可表示为：

(P SC+1) ( A R R+1)

T=

Ft imer

8. 看门狗定时器如果长时间不喂狗，会发生什么？

答. 系统复位。

解. 看门狗用于防止程序跑飞或死循环。程序正常运行时需要定期喂狗；如果没有及时喂狗，看门狗计

数溢出后会触发系统复位。

9. I²C 总线属于哪种通信方式？

答. 同步串行通信方式。

解. I²C 使用 SCL 时钟线和 SDA 数据线通信。它通过时钟线同步数据传输，因此属于同步通信；数据按

位传输，因此属于串行通信。

10. 下列哪些属于 RTC 的典型应用？

A. PWM 输出

B. 普通计数

C. 日历

D. 闹钟唤醒

答. C、D

解. RTC 是 Real Time Clock，即实时时钟，常用于日历、时间记录、闹钟和低功耗唤醒。PWM 输出

通常由定时器实现。

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 3 -->

嵌入式期末真题回忆版复原（答案与解析版）

<!-- question: embedded-systems-018-Q2 -->

二、填空与简答题

11. Cortex-M3 内核是 ______ 位，采用 ______ 总线结构。

答. 32 位；哈佛总线结构。

解. Cortex-M3 是 32 位 ARM 处理器内核，采用哈佛结构，指令访问和数据访问相对分离。常见总线

包括 I-Code Bus、D-Code Bus 和 System Bus。

12. STM32 的中断优先级由哪两部分组成？如何判断优先级高低？

答. 由抢占优先级和响应优先级组成。数值越小，优先级越高；抢占优先级高的中断可以打断抢占优先

级低的中断；抢占优先级相同时再比较响应优先级。

解. 抢占优先级决定中断能不能嵌套，响应优先级决定多个同抢占级中断同时到来时谁先被响应。

13. EXTI 外部中断有哪三种触发方式？

答. 上升沿触发、下降沿触发、双边沿触发。

解. 上升沿触发表示信号由低电平变为高电平时产生中断；下降沿触发表示信号由高电平变为低电平时

产生中断；双边沿触发表示两种边沿都产生中断。

14. STM32 中可用于定时的模块有：______、______。

答. SysTick、TIM 定时器。

解. SysTick 是 Cortex-M 内核自带系统定时器，常用于系统节拍和延时。TIM 是 STM32 的定时器外

设，可用于定时中断、PWM、输入捕获、输出比较等。

15. DMA 的传输方向有：______、______、______、______。

答. 外设到内存、内存到外设、内存到内存、外设到外设。

解. 按源地址和目的地址的组合可写成四类。常见应用中，ADC 采集属于外设到内存，串口发送属于内

存到外设，数组搬运属于内存到内存。

16. 写出 PWM 输出等效电压的计算公式。

答. 输出等效电压为：

U out=D×U c c

解. PWM 的等效输出电压取决于高电平在一个周期内所占比例。占空比越大，平均电压越高。若用定

时器产生 PWM，还可写为：

D≈C C R

A R R 或D= C C R

A R R+1

17. 阅读下列 ARM 汇编程序，写出执行后 R0、R1、R2、R3 的值，并写出地址 0x404~0x407 中存

放的内容。

程序代码：

MOV  R0, #0x400

ADD  R1, R0, #0x04

LDR  R2, =0x12345678

STR  R2, [R1]!

SUB  R1, #0x02

LDRB R3, [R1]

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 4 -->

嵌入式期末真题回忆版复原（答案与解析版）

答. R0 = 0x400，R1 执行前三条后为 0x404，R2 = 0x12345678。执行 STR 后，0x404~0x407 依次为

0x78、0x56、0x34、0x12。随后 SUB 使 R1 = 0x402，R3 = [0x402] 的一个字节；若题目未给出

0x402 原值，则 R3 不能唯一确定。

解. STM32 采用小端存储，低字节存放在低地址。因此 0x12345678 存入内存后，地址 0x404 存

0x78，0x405 存 0x56，0x406 存 0x34，0x407 存 0x12。LDRB 只读取一个字节。

<!-- question: embedded-systems-018-Q3 -->

三、简答题

18. 简述 STM32 与普通单片机的区别。

答. STM32 是基于 ARM Cortex-M 内核的 32 位微控制器。与传统普通单片机相比，STM32 主频更

高、运算能力更强、片上外设更丰富、存储容量更大、低功耗模式更多、调试方式更方便。

解. STM32 本质上也是单片机，只是属于性能更强、资源更多的 32 位单片机。答题时不要写

成“STM32 不是单片机”。

19. 定时器中哪些脚可以作为计数输入？说明计数实现过程。

答. 可作为计数输入的信号脚通常包括 TI1、TI2、ETR，也可理解为 CH1 输入、CH2 输入和外部触发

输入 ETR。

解. 计数实现过程为：将对应 GPIO 配置为定时器输入功能，选择外部时钟源或触发源（如 TI1、TI2 或

ETR），设置输入极性、滤波、预分频和 ARR，清零 CNT 并使能定时器。外部脉冲每来一次，CNT

按配置加 1，计到 ARR 后产生更新事件或溢出。

20. 简述 STM32 中断优先级的含义。

答. STM32 中断优先级包括抢占优先级和响应优先级。抢占优先级决定一个中断能否打断另一个正在执

行的中断；响应优先级决定同抢占级中多个中断同时到来时谁先响应。

解. 抢占优先级和响应优先级均为数值越小优先级越高。只有抢占优先级不同，才涉及中断嵌套。

21. 简述汇编语言在嵌入式开发中的作用，并列举三种寻址方式且举例说明。

答. 汇编语言可用于编写启动代码、初始化堆栈、设置中断向量表、直接访问处理器寄存器、编写异常

与上下文切换等底层代码，也可用于优化速度或空间要求高的程序片段。三种寻址方式示例见下。

示例代码：

立即寻址：      MOV R0, #10

寄存器寻址：    MOV R0, R1

寄存器间接寻址：LDR R0, [R1]

基址加偏移寻址：LDR R0, [R1, #4]

解. 立即寻址的操作数直接写在指令中；寄存器寻址的操作数在寄存器中；寄存器间接寻址是寄存器中

保存内存地址，真正访问的是该地址中的数据。

22. 列举一个可以运行在 MCU 上的嵌入式操作系统，并说明任务管理模块的作用。

答. 可运行在 MCU 上的嵌入式操作系统有 FreeRTOS、μC/OS-II、RT-Thread、RTX 等。任务管理

模块用于创建任务、删除任务、挂起任务、恢复任务、任务延时、任务调度、任务优先级管理和任务状

态切换。

解. RTOS 的核心功能之一是管理多个任务。系统通过任务调度决定当前运行哪个任务，并通过任务管

理模块完成任务的创建、阻塞、挂起、恢复和优先级控制等操作。

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 5 -->

嵌入式期末真题回忆版复原（答案与解析版）

<!-- question: embedded-systems-018-Q4 -->

四、综合题一：ADC 测电压并控制 PA6 上 LED 亮灭

23. 使用 STM32 的 ADC 测量外部模拟电压，并根据测得电压控制 PA6 引脚上的 LED 灯亮灭。请完

成下列问题：

（1）说明 ADC 测电压并控制 LED 的基本流程；

（2）若 ADC 参考电压为 3.3V，分辨率为 12 位，输入电压为 0.825V，求对应的数字量；

（3）写出 PA6 初始化代码；

（4）写出控制 LED 亮灭的函数；

（5）描述如何使用 DMA 实现 ADC 数据采集。

答. （1）配置 ADC 输入引脚为模拟输入，初始化 ADC，启动转换并读取结果，根据阈值控制 PA6 输

出高低电平，使 LED 亮灭。

解. ADC 将模拟电压转换成数字量，程序根据数字量大小判断输入电压是否超过阈值，再通过 GPIO 控

制 LED。

答. （2）数字量约为 1024，即 0x400。

A DCV alue=0.825

3.3 ×4096=1024

解. 12 位 ADC 的数字量范围通常为 0~4095。考试中若按 4096 计算，结果正好为 1024；若按 4095 计

算，结果约为 1023.75，取整后也可写约 1024。

答. （3）PA6 初始化代码如下。

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

解. PA6 属于 GPIOA，因此要先打开 GPIOA 时钟。LED 控制引脚通常配置为通用推挽输出。

答. （4）若 LED 高电平点亮，控制函数如下。若实际电路为低电平点亮，则 SetBits 和 ResetBits 的

作用相反。

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 6 -->

嵌入式期末真题回忆版复原（答案与解析版）

代码：

void LED_On(void)

{

    GPIO_SetBits(GPIOA, GPIO_Pin_6);

}

void LED_Off(void)

{

    GPIO_ResetBits(GPIOA, GPIO_Pin_6);

}

解. LED 亮灭取决于硬件连接方式。高电平点亮时，置位点亮、复位熄灭；低电平点亮时，复位点亮、

置位熄灭。

答. （5）ADC + DMA 的流程为：使能 GPIO、ADC、DMA 时钟；配置 ADC 输入引脚为模拟输入；

配置 DMA 外设地址为 ADC 数据寄存器、内存地址为结果变量或数组、方向为外设到内存、数据宽度

为半字，可使用循环模式；配置 ADC 通道、采样时间、转换模式并使能 DMA 请求；最后使能 DMA

和 ADC 并启动转换。

解. 普通 ADC 采样需要 CPU 主动读取 ADC 数据寄存器。使用 DMA 后，ADC 转换结果可以自动搬运

到内存中，减少 CPU 参与，提高采样效率。

<!-- question: embedded-systems-018-Q5 -->

五、综合题二：测外部脉冲宽度并通过串口发送到电脑

24. 使用 STM32 测量外部输入脉冲宽度，并通过串口每 800ms 将测得的宽度发送到电脑串口助手。

请完成下列问题：

（1）PA3、PA4、PA5 中哪个引脚可以测外部脉冲宽度？使用哪个定时器通道？

（2）根据 800ms 定时要求，设置 prescaler 和 reload；

（3）说明用查询方式实现 800ms 定时发送的方法；

（4）说明用中断方式实现 800ms 定时发送的方法；

（5）使用 UART4 作为串口，根据串口助手参数写出 UART4 初始化代码。

答. （1）选择 PA3，对应 TIM2_CH4。

解. STM32F103 中 PA3 可复用为 TIM2_CH4，可作为定时器输入捕获通道，用于测量外部脉冲宽度。

PA4、PA5 通常不是 TIM2 的输入捕获通道。

答. （2）假设定时器时钟为 72MHz，可令 Prescaler = 7200 - 1 = 7199，Reload = 8000 - 1 = 7999。

T=7200×8000

72000000 =0.8 s=800m s

解. 72MHz 经 7200 分频后为 10kHz，计数周期为 100μs；800ms / 100μs = 8000，因此 ARR 可设为

7999。

答. （3）查询方式是在主循环中不断检测定时器更新标志位，到 800ms 后清除标志并发送脉冲宽度。

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 7 -->

嵌入式期末真题回忆版复原（答案与解析版）

查询方式代码：

while (1)

{

    if (TIM_GetFlagStatus(TIMx, TIM_FLAG_Update) != RESET)

    {

        TIM_ClearFlag(TIMx, TIM_FLAG_Update);

        Send_Width();

    }

}

解. 查询方式结构简单，但 CPU 需要不断轮询标志位。

答. （4）中断方式是在定时器每 800ms 产生更新中断时进入中断服务函数，在中断中清除标志并发送

脉冲宽度。

中断方式代码：

void TIMx_IRQHandler(void)

{

    if (TIM_GetITStatus(TIMx, TIM_IT_Update) != RESET)

    {

        TIM_ClearITPendingBit(TIMx, TIM_IT_Update);

        Send_Width();

    }

}

解. 中断方式不需要主循环一直查询标志位，定时器到时后 CPU 自动进入中断服务函数。

答. （5）UART4 常用引脚为 PC10 和 PC11，其中 PC10 为 UART4_TX，PC11 为 UART4_RX。初始

化代码如下。

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 8 -->

嵌入式期末真题回忆版复原（答案与解析版）

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

解. UART4 挂在 APB1 总线上，所以要使能 RCC_APB1Periph_UART4。PC10 配置为复用推挽输出

作为 TX，PC11 配置为浮空输入作为 RX。串口参数应与串口助手保持一致，如 115200 波特率、8 位

数据位、1 位停止位、无校验、无硬件流控。

— 由回忆版整理，答案以课堂与教材要求为准 —

<!-- page: 9 -->

嵌入式期末真题回忆版复原（答案与解析版）

附：复原出的完整题目列表

1. 下列哪一项属于嵌入式系统的特点？

2. STM32 的复位方式不包括下列哪一项？

3. STM32F103 支持从下列哪一项启动？

4. Cortex-M3 处理器中，程序计数器 PC 对应哪个寄存器？

5. STM32 中，内核与片上外设之间主要通过下列哪一种结构进行通信？

6. 若要将 STM32 的某个 GPIO 引脚配置为外部中断输入，需要完成哪些设置？

7. 设置 STM32 定时器周期，操作 ______ 寄存器。

8. 看门狗定时器如果长时间不喂狗，会发生什么？

9. I²C 总线属于哪种通信方式？

10. 下列哪些属于 RTC 的典型应用？

11. Cortex-M3 内核是 ______ 位，采用 ______ 总线结构。

12. STM32 的中断优先级由哪两部分组成？如何判断优先级高低？

13. EXTI 外部中断有哪三种触发方式？

14. STM32 中可用于定时的模块有：______、______。

15. DMA 的传输方向有：______、______、______、______。

16. 写出 PWM 输出等效电压的计算公式。

17. 阅读 ARM 汇编程序，写出 R0、R1、R2、R3 的值，并写出 0x404~0x407 中存放的内容。

18. 简述 STM32 与普通单片机的区别。

19. 定时器中哪些脚可以作为计数输入？说明计数实现过程。

20. 简述 STM32 中断优先级的含义。

21. 简述汇编语言在嵌入式开发中的作用，并列举三种寻址方式且举例说明。

22. 列举一个可以运行在 MCU 上的嵌入式操作系统，并说明任务管理模块的作用。

23. 使用 STM32 的 ADC 测量外部模拟电压，并根据测得电压控制 PA6 引脚上的 LED 灯亮灭。

24. 使用 STM32 测量外部输入脉冲宽度，并通过串口每 800ms 将测得的宽度发送到电脑串口助手。

— 由回忆版整理，答案以课堂与教材要求为准 —
