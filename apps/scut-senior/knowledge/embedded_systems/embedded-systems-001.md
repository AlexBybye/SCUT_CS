---
source_id: embedded-systems-001
course_id: embedded_systems
title: ch10DMA
original_file: "学科资料/嵌入式/课程PPT讲义/ch10DMA.ppt"
document_role: note
year: 
locator_type: slide
---

# ch10DMA

<!-- slide: 1 -->

## 第10章 DMA方式

- 嵌入式微控制器原理及设计
- —基于STM32及Proteus仿真开发
- 配套PPT

<!-- slide: 2 -->

![image](assets/assets/embedded-systems-001/image-001.jpg)
![image](assets/assets/embedded-systems-001/image-002.png)

<!-- slide: 3 -->

- 第10章  DMA
- 10.1 DMA概述
- 10.2 DMA应用实例

<!-- slide: 4 -->

- 10.1 DMA概述
- DMA（Direct Memory Access，直接存储器存取），是一种可以大大减轻CPU工作量的数据存取方式，因而被广泛地使用。早在8086的应用中就已经有Intel的这种典型的DMA控制器，而STM32的DMA则是以的类似外设的形式添加到Cortex内核之外的。
- DMA的作用就是实现数据的直接传输，而去掉了传统数据传输需要CPU寄存器参与的环节，主要涉及四种情况的数据传输:外设到内存、内存到外设、内存到内存、外设到外设。

<!-- slide: 5 -->

- STM32芯片DMA的主要特性：
- 10.1.1 STM32芯片DMA特性
- （1）12个独立的可配置的通道（请求），DMA1有7个通道，DMA2有5个通道。
- （2）每个通道都直接连接专用的硬件DMA请求，每个通道都同样支持软件触发。这些功能通过软件来配置。
- （3）优先权可以通过软件编程设置（共有4级：很高、高、中等和低），假如在相等优先权时由硬件决定（请求0优先于请求1，其余类推）。
- （4）独立的源和目标数据区的传输宽度（字节、半字、全字），模拟打包和拆包的过程。源和目标地址必须按数据传输宽度对齐。
- （5）支持循环的缓冲器管理。
- （6）每个通道都有3个事件标志（DMA半传输，DMA传输完成和DMA传输出错），这3个事件标志逻辑或成为一个单独的中断请求。
- （7）存储器和存储器间的传输。
- （8）外设和存储器，存储器和外设的传输。
- （9）闪存Flash、内部SRAM、外部SRAM、APB1、 APB2和AHB外设均可作为访问的源和目标。
- （10）可编程的数据传输数目：最大为65536。

<!-- slide: 6 -->

![image](assets/assets/embedded-systems-001/image-003.png)
- DMA1控制器结构，有7个通道

<!-- slide: 7 -->

![image](assets/assets/embedded-systems-001/image-004.png)
- DMA2控制器结构，有5个通道

<!-- slide: 8 -->

- 10.1.2 STM32的DMA主要寄存器
- DMA主要寄存器功能
![image](assets/assets/embedded-systems-001/image-005.png)

<!-- slide: 9 -->

- 10.2 DMA应用实例
- 10.2.1 ADC数据采集DMA方式
- 【例10.1】 以DMA方式对ADC的数据进行采集，利用DMA把数据从外设转移到内存。使用STM32CubeMX初始化ADC数据采集DMA模式。
![image](assets/assets/embedded-systems-001/image-006.png)
- 配置内容：ADC采集连接DMA1的通道1；DMA方向是外设到内存；优先级高；DMA模式是Circular，DMA在配置为Circular模式时循环进入中断；外设和内存的数据宽度为半字(Half Word)。相对于Circular方式，有Normal模式表示单次模式。

<!-- slide: 10 -->

- 生成的代码如下：
- 主程序相关DMA的主要内容如下：
![image](assets/assets/embedded-systems-001/image-007.png)
![image](assets/assets/embedded-systems-001/image-008.png)

<!-- slide: 11 -->

- 10.2.2 串口发送DMA方式
- 【例10.2】 通过实例对STM32的DMA进行讲解，以DMA方式使用串口发送数据，串口发送电路和前面的串行通信实例一样。此过程利用DMA把数据从内存转移到外设，这个过程是不需要内核干预的，所以在串口发送数据时，内核同时还可以进行其他操作。
- 使用STM32CubeMX初始化串行通信DMA模式：
![image](assets/assets/embedded-systems-001/image-009.png)
- 配置内容：串口发送USART1_TX连接DMA1的通道4；DMA方向是内存到外设；优先级低；DMA模式是Normal，DMA在配置为Normal模式时只能进入一次中断；外设和内存的数据宽度为1字节。相对于Normal方式，有Circular模式表示循环模式。

<!-- slide: 12 -->

- 生成的代码如下：
- 在stm32f1xx_it.c程序中产生出相应DAM函数，如下：
- 主程序相关DMA的主要内容如下
![image](assets/assets/embedded-systems-001/image-010.png)
![image](assets/assets/embedded-systems-001/image-011.png)
![image](assets/assets/embedded-systems-001/image-012.png)

<!-- slide: 13 -->

- 谢谢!
