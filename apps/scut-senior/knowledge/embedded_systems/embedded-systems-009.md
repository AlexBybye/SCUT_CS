---
source_id: embedded-systems-009
course_id: embedded_systems
title: ch5GPIO
original_file: "学科资料/嵌入式/课程PPT讲义/ch5GPIO.ppt"
document_role: note
year: 
locator_type: slide
---

# ch5GPIO

<!-- slide: 1 -->

## 第5章 GPIO

- 嵌入式微控制器原理及设计
- —基于STM32及Proteus仿真开发
- 配套PPT

<!-- slide: 2 -->

![image](assets/assets/embedded-systems-009/image-001.jpg)
![image](assets/assets/embedded-systems-009/image-002.png)

<!-- slide: 3 -->

- 第5章 GPIO
- 5.1 GPIO结构及特点
- 5.2 GPIO寄存器开发方式
- 5.3 GPIO标准库开发方式
- 5.4 GPIO HAL库开发方式
- 5.5 GPIO LL库开发方式
- 5.6 GPIO应用开发实例

<!-- slide: 4 -->

- 5.1 GPIO结构及特点
- STM32F103R6芯片通用GPIO有PA、PB、PC和PD端口，端口一般包括有15个引脚，具体引脚可表示为Px0~Px15。
![image](assets/assets/embedded-systems-009/image-003.png)
![image](assets/assets/embedded-systems-009/image-004.png)

<!-- slide: 5 -->

- 5.1.1 GPIO功能模式
- GPIO结构如下功能：
- （1）数字输入模式
- （2）模拟输入模式
- （3）推挽输出模式
- （4）开漏输出模式
- （5）GPIO输出速度设定
- （6）钳位功能
- （7）GPIO复用功能
![image](assets/assets/embedded-systems-009/image-005.png)
- 输入驱动器部分，I/O引脚连接可配置的上拉电阻和下拉电阻，并连接到模拟输入，通过肖基特触发器连接复用功能输入；在输出驱动器部分，I/O引脚连接上拉PMOS管和下拉NMOS，并且复用功能通过输出控制连接I/O引脚，在I/O引脚分别上拉和下拉一个保护二极管，对I/O引脚起着保护作用。

<!-- slide: 6 -->

- 5.1.2 GPIO特点及操作
- （1）I/O口电平兼容性，模拟口最大承受3.6V，数字口承受5V。
- （2）I/O口驱动能力，GPIO口最大可以吸收25mA电流，但是总吸收电流不能超过150mA。
- （3）I/O口可内部上拉/下拉设置，简化外部输入电路设计。
- （4）I/O口可配置为外部中断口。
- （5）具有独立的唤醒I/O口，例如一个从待机模式中唤醒的专用引脚PA0。
- （6）I/O口具有锁存功能。
- （7）具有侵入检测引脚。

<!-- slide: 7 -->

- STM32F103R6芯片的每个引脚可以由软件配置输入和输出模式
![image](assets/assets/embedded-systems-009/image-006.png)
![image](assets/assets/embedded-systems-009/image-007.png)

<!-- slide: 8 -->

- 5.1.3 GPIO开发实例
- 设计一个通过按钮控制LED亮、灭的实例，按钮连接PA0，当按下时产生低电平，弹开时产生高电平；LED正端连接3.3V，负端连接限流电阻到PB0，如图所示。
![image](assets/assets/embedded-systems-009/image-008.gif)

<!-- slide: 9 -->

- 5.2 GPIO寄存器开发方式
![image](assets/assets/embedded-systems-009/image-009.png)
- GPIO有两个32位配置寄存器(GPIOx_CRL和GPIOx_CRH)，两个32位数据寄存器（GPIOx_IDR和GPIOx_ODR），一个32位置位/复位寄存器（GPIO_BSRR），一个16位复位寄存器（GPIOx_BRR）和一个32位锁定寄存器（GPIOx_LCKR）。
- 5.2.1 GPIO寄存器说明

<!-- slide: 10 -->

![image](assets/assets/embedded-systems-009/image-010.png)

<!-- slide: 11 -->

- 5.2.2 GPIO寄存器实现应用实例
- 寄存器的描述参见《STM32F10xxx系列芯片开发手册》
![image](assets/assets/embedded-systems-009/image-011.png)
![image](assets/assets/embedded-systems-009/image-012.png)
- 英文版
- 中文版

<!-- slide: 12 -->

- （1）端口配置低寄存器(GPIOx_CRL)，用于配置引脚的功能模式。
![image](assets/assets/embedded-systems-009/image-013.png)
![image](assets/assets/embedded-systems-009/image-014.png)
- /*设置PA0为输入,配置上拉电阻,
- CNF0=10，MODE0=00*/
- GPIOA->CRL |= 0x00000008;
- GPIOA->CRL &= ~(0x00000007);
- (书中勘误：书中8错误，应该为7）
- /*设置PB0为输出,最大速度10MHz , CNF1=00，MODE1=01*/
- GPIOA->CRL |= 0x00000001;
- GPIOA->CRL &= ~(0x0000000E);

<!-- slide: 13 -->

- （2）端口输入数据寄存器(GPIOx_IDR)，用于读取输入口状态。
![image](assets/assets/embedded-systems-009/image-015.png)
![image](assets/assets/embedded-systems-009/image-016.png)
- /*检测PA0的状态*/
- if((GPIOA->IDR & 0x01)== 0)
- /*如果检测为低电平，即按钮按下*/

<!-- slide: 14 -->

- （3）端口输出数据寄存器(GPIOx_ODR)，用于控制引脚的输出。
![image](assets/assets/embedded-systems-009/image-017.png)
- GPIOB->ODR &= ~(0x0001);   /*控制PA1输出为低电平，LED亮*/
- GPIOB->ODR |= 0x0001;       /*控制PA1输出为高电平，LED灭*/

<!-- slide: 15 -->

- 5.3 GPIO标准库开发方式
- 5.3.1 GPIO标准库函数说明
- 准库函数手册
![image](assets/assets/embedded-systems-009/image-018.png)
- STM32标准库提供GPIO库函数，这些函数的声明都包含在头文件“stm_32f10x_gpio.h”文件中。
- STM32的标准库函数对于程序开发人员来说应用非常方便，只需要通过标准库函数手册了解函数的功能和输入参数。
![image](assets/assets/embedded-systems-009/image-019.png)

<!-- slide: 16 -->

- （1）GPIO_init函数
![image](assets/assets/embedded-systems-009/image-020.png)
- GPIO_InitTypeDef 结构描述：
- typedef struct
- {
- u16 GPIO_Pin;
- GPIOSpeed_TypeDef GPIO_Speed;
- GPIOMode_TypeDef GPIO_Mode;
- } GPIO_InitTypeDef;
![image](assets/assets/embedded-systems-009/image-021.png)
![image](assets/assets/embedded-systems-009/image-022.png)
![image](assets/assets/embedded-systems-009/image-023.png)

<!-- slide: 17 -->

- （2）GPIO_SetBits函数
![image](assets/assets/embedded-systems-009/image-024.png)
![image](assets/assets/embedded-systems-009/image-025.png)

<!-- slide: 18 -->

- （3）GPIO_ResetBits函数
![image](assets/assets/embedded-systems-009/image-026.png)
![image](assets/assets/embedded-systems-009/image-027.png)

<!-- slide: 19 -->

- （4）GPIO_ReadInputDataBit函数
![image](assets/assets/embedded-systems-009/image-028.png)
![image](assets/assets/embedded-systems-009/image-029.png)

<!-- slide: 20 -->

- 5.3.2 GPIO标准库应用实例
![image](assets/assets/embedded-systems-009/image-030.png)
![image](assets/assets/embedded-systems-009/image-031.png)
![image](assets/assets/embedded-systems-009/image-032.png)

<!-- slide: 21 -->

- 5.4 GPIO HAL库开发方式
![image](assets/assets/embedded-systems-009/image-033.png)
- HAL库函数手册

<!-- slide: 22 -->

- 5.4.1 GPIO HAL函数说明
- STM32固件库提供GPIO HAL库函数，这些函数的声明都包含在头文件“stm32f1xx_hal_gpio.h”文件中，GPIO HAL库函数说明。
- GPIO_TypeDef结构体
![image](assets/assets/embedded-systems-009/image-034.png)
![image](assets/assets/embedded-systems-009/image-035.png)

<!-- slide: 23 -->

- 初始化
![image](assets/assets/embedded-systems-009/image-036.png)

<!-- slide: 24 -->

![image](assets/assets/embedded-systems-009/image-037.png)
- 操作说明

<!-- slide: 25 -->

![image](assets/assets/embedded-systems-009/image-038.png)

<!-- slide: 26 -->

- 5.4.2 GPIO HAL库应用实例
- 首先利用配合HAL库使用的STM32CubeMX软件对芯片中的外设和时钟进行配置，并产生出HAL库初始的程序。
- （1）利用STM32CubeMX进行外设配置。主要是配置PA0配置为输入，PB0配置为输出；以及外部时钟引脚配置（由于系统中采用外部时钟）。
![image](assets/assets/embedded-systems-009/image-039.png)
![image](assets/assets/embedded-systems-009/image-040.png)
- GPIO引脚设置：

<!-- slide: 27 -->

- （2）对时钟进行配置。可对芯片各外设的时钟模块进行配置，本实例用到了PORTA和PORTB，都属于APB2外设总线，被配置为72MHz。
![image](assets/assets/embedded-systems-009/image-041.png)
![image](assets/assets/embedded-systems-009/image-042.png)
- 时钟引脚设置：

<!-- slide: 28 -->

- （3）产生出代码。本实例采用IDE MDK-ARMv5开发环境，其他默认配置。
![image](assets/assets/embedded-systems-009/image-043.png)
![image](assets/assets/embedded-systems-009/image-044.png)

<!-- slide: 29 -->

- 配置完成后，按下“GENERATE CODE”按钮，就会生成基本程序。同时根据实例添加key.c、key.h和led.c、led.h代码，最后得到程序代码结构如下：
![image](assets/assets/embedded-systems-009/image-045.png)

<!-- slide: 30 -->

- 其中，在Application/User文件夹中自动会生成main.c、gpio.c、stm32flxx_it.c和stm32f1xx_hal_msp.c代码。但需要在main.c中添加代码如下：
![image](assets/assets/embedded-systems-009/image-046.png)
![image](assets/assets/embedded-systems-009/image-047.png)
![image](assets/assets/embedded-systems-009/image-048.png)

<!-- slide: 31 -->

- 5.5 GPIO LL库开发方式
- 5.5.1 GPIO LL函数说明
![image](assets/assets/embedded-systems-009/image-049.png)

<!-- slide: 32 -->

- STM32固件库提供GPIO LL库函数，这些函数的声明和实现主要包含在头文件“stm32f1xx_ll_gpio.h”文件中，LL库的一大特点就是巧妙运用C语言的静态、内联函数来直接操作寄存器。LL绝大多数函数在.h文件中并且都是静态内联函数。在LL库中，只有少数函数接口是放在.c文件中的。
- 例如在“stm32f1xx_ll_gpio.h”文件中实现LL_GPIO_SetOutputPin内联函数的写法如下：
- __STATIC_INLINE void LL_GPIO_SetOutputPin(GPIO_TypeDef *GPIOx, uint32_t PinMask)
- {
- WRITE_REG(GPIOx->BSRR, (PinMask >> GPIO_PIN_MASK_POS) & 0x0000FFFFU);
- }

<!-- slide: 33 -->

- 5.5.2 GPIO LL应用实例
- 首先利用配合LL库使用的STM32CubeMX软件对芯片中的外设和时钟进行配置，并产生出LL库初始的程序。
![image](assets/assets/embedded-systems-009/image-050.png)

<!-- slide: 34 -->

- 在Application/User文件夹中自动会生成main.c、gpio.c、stm32flxx_it.c和stm32f1xx_hal_msp.c代码。但需要在main.c中添加代码，这部分和HAL库一样。
![image](assets/assets/embedded-systems-009/image-051.png)
![image](assets/assets/embedded-systems-009/image-052.png)

<!-- slide: 35 -->

- 5.6 GPIO应用开发实例
- GPIO可常用于输出控制各种设备，例如数码管；也可以用于输入检测，例如行列式键盘输入等。

<!-- slide: 36 -->

- LED数码管（LED Segment Displays）是由多个发光二极管封装在一起组成“8”字型的器件，引线已在内部连接完成，只需引出它们的各个笔划，公共电极。LED数码管常用段数一般为7段，有的另加一个小数点，所以此时会称为8段，LED数码管根据LED的接法不同分为共阴和共阳两类。
![image](assets/assets/embedded-systems-009/image-053.jpg)
![image](assets/assets/embedded-systems-009/image-054.png)
- 5.6.1数码管显示实例
- 例如，针对一个共阴极8段数码管，公共端接地，段码A,B,C,D,E,F,G,DP分别连接11011010，显示数字“2”。
![image](assets/assets/embedded-systems-009/image-055.png)

<!-- slide: 37 -->

- 静态显示驱动:
- 静态驱动也称直流驱动。静态驱动是指每个数码管的每一个段码都由单片机的一个I/O口进行驱动，或者使用如BCD码计数器进行驱动。静态驱动的优点是编程简单，显示亮度高，缺点是占用I/O口多，如驱动5个数码管静态显示则需要5×8＝40根I/O口来驱动，故实际应用时必须增加驱动器进行驱动，增加了硬体电路的复杂性。
![image](assets/assets/embedded-systems-009/image-056.png)

<!-- slide: 38 -->

- 动态显示驱动
- 动态驱动是将所有数码管的8个显示笔画"a,b,c,d,e,f,g,dp "的同名端连在一起，另外为每个数码管的公共极COM增加位元选通控制电路，位元选通由各自独立的I/O线控制，当单片机输出字形码时，所有数码管都接收到相同的字形码，但究竟是哪个数码管会显示出字形，取决于单片机对位元选通COM端电路的控制，所以我们只要将需要显示的数码管的选通控制打开，该位元就显示出字形，没有选通的数码管就不会亮。
![image](assets/assets/embedded-systems-009/image-057.gif)
- HAL_Delay(1);
- HAL_Delay(50);
![image](assets/assets/embedded-systems-009/image-058.gif)

> 备注：透过分时轮流控制各个LED数码管的COM端，就使各个数码管轮流受控显示，这就是动态驱动。在轮流显示过程中，每位元数码管的点亮时间为1～2ms，由于人的视觉暂留现象及发光二极管的余辉效应，尽管实际上各位数码管并非同时点亮，但只要扫描的速度足够快，给人的印象就是一组稳定的显示，不会有闪烁感，动态显示的效果和静态显示是一样的，能够节省大量的I/O口，而且功耗更低。

<!-- slide: 39 -->

- 【例5.5】 利用动态显示驱动方式，在4个LED数码管上显示“2021”数字。
![image](assets/assets/embedded-systems-009/image-059.gif)

<!-- slide: 40 -->

- 使用STM32CubeMX工具配置PA0,PA1,PA2,PA3,PA4, PA5,PA6,PA7和PB0,PB1,PB3,PB4为输出。
![image](assets/assets/embedded-systems-009/image-060.png)

<!-- slide: 41 -->

![image](assets/assets/embedded-systems-009/image-061.png)
![image](assets/assets/embedded-systems-009/image-062.png)
- main( )
![image](assets/assets/embedded-systems-009/image-063.png)
- GPIOSetMutiValue( )

<!-- slide: 42 -->

- 5.6.2 行列式键盘扫描实例
- 设计一个2×2行列式键盘，将键盘的每一列配置为下拉输入，依次给每一行输出高电平，如果这一行某一列的按键按下，则会在那一列产生高电平，并控制对应LED的亮、灭。具体控制过程如下：S1、S2、S3和S4控制LED1、LED2、LED3和LED4。
![image](assets/assets/embedded-systems-009/image-064.gif)

<!-- slide: 43 -->

- 行列式键盘扫描
- 独立式键盘的电路简单，易于编程，但占用的IO口线较多，当需要较多按键时可能产生IO口资源紧张问题。行列式键盘将IO口分为行线和列线，按键跨接在行线和列线上，并且把行线和列线设定为输出或输入。 这些按键都有是一端跨在一根输出线上，另一端跨在一根输入线上， 要是没有按键按下时，输入状态和输出状态没有任何关系，这时嵌入式微控制器读输入线的状态，得到的结果全是默认或设定的值；若有按键按下，输出线的状态就会反映在输入线上。然后根据输入和输出线的交叉关系，就能计算出具体的键值。

<!-- slide: 44 -->

- 使用STM32CubeMX工具配置PA0,PA1,PA2,PA3为输出，PB0,PB1,PB2,PB3为输入，同时PB2和PB3配置为下拉，具体配置
![image](assets/assets/embedded-systems-009/image-065.png)
![image](assets/assets/embedded-systems-009/image-066.png)

<!-- slide: 45 -->

![image](assets/assets/embedded-systems-009/image-067.png)
- 主程序如下：

<!-- slide: 46 -->

![image](assets/assets/embedded-systems-009/image-068.png)

<!-- slide: 47 -->

- 谢谢!
