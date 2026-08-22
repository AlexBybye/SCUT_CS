---
source_id: embedded-systems-011
course_id: embedded_systems
title: "ch7串行通信"
original_file: "学科资料/嵌入式/课程PPT讲义/ch7串行通信.ppt"
document_role: note
year: 
locator_type: slide
---

# ch7串行通信

<!-- slide: 1 -->

## 第7章 串行通信

- 嵌入式微控制器原理及设计
- —基于STM32及Proteus仿真开发
- 配套PPT

<!-- slide: 2 -->

![image](assets/assets/embedded-systems-011/image-001.jpg)
![image](assets/assets/embedded-systems-011/image-002.png)

<!-- slide: 3 -->

- 第7章 串行通信
- 7.1 串行通信介绍
- 7.2 STM32 USART接口
- 7.3 UART异步串行操作
- 7.4 基于串口的无线通信
- 7.5串行同步通信（SPI）

<!-- slide: 4 -->

- 串行通信（Serial communication）是指在计算机总线或其他数据通道上，每次传输一个位元数据，并连续进行以上单次过程的通信方式。
- 与之对应的是并行通信，它在串行端口上通过一次同时传输若干位元数据的方式进行通信。
- 串行通信被用于长距离通信以及大多数计算机网络，在普通应用场合，电缆和同步化使并行通信面临实际应用问题。
- 7.1 串行通信介绍

<!-- slide: 5 -->

- （1）异步串行通信
- 异步串行通信所传输的数据格式（也称为串行帧）由1个起始位、7~9个数据位、1～2个停止位（含1.5个停止位）和1个校验位组成。起始位约定为0，空闲位约定为1。在异步通信方式中，接收器和发送器有各自的时钟，它们的工作是非同步的。
![image](assets/assets/embedded-systems-011/image-003.png)
- 7.1.1 串行通信介绍

<!-- slide: 6 -->

- （2）同步串行通信
- 同步串行通信中，发送器和接收器由同一个时钟源控制。
![image](assets/assets/embedded-systems-011/image-004.png)

<!-- slide: 7 -->

- （3）波特率及时钟频率
- 波特率BR是单位时间传输的数据位数，即单位:bps（bit per second）1bps = 1bit/s。采用异步串行，互相通信甲乙双方必须具有相同的波特率，否则无法成功地完成数据通信。同步通信中通过主从设备的同步时钟完成数据同步，因此很少有波特率说法，当然也可以看作数据传输的波特率即为同步时钟频率。

<!-- slide: 8 -->

- （4）串行通信的校验
- 异步通信时可能会出现帧格式错、超时错等传输错误。在具有串行接口单片机的开发中，应考虑在通信过程中对数据差错进行校验，因为差错校验是保证准确无误通信的关键。
- （5）数据通信的传输方式
- 常用于数据通信的传输方式有单工、半双工、全双工方式。单工通信是指消息只能单方向传输的工作方式，例如遥控、遥测。半双工通信是指数据可以在一个信号载体的两个方向上传输，但是不能同时传输。全双工通信允许数据在两个方向上同时传输，它在能力上相当于两个单工通信方式的结合。

<!-- slide: 9 -->

- 7.1.2微控制器常见串行通信方式
- (1) UART
- UART串行通信方式称作为异步串行通信，主要通过两个引脚发送（TXD）和接收（RXD）实现数据的发送和接收，由于没有时钟线，所以是一种全双工的异步串行通信接口，通信数据的同步利用设置好的波特率来实现，波特率的最大速率传统上是115200bps但现在对于一些微控制器如STM32芯片其波特率可以达到2Mbps。

<!-- slide: 10 -->

- (2) USART
- USART 串行通信是在UART的基础上增加了同步通信方式，称为同步/异步串行通信。当设置为异步串行通信时，和前面所述的UART的连接和特性是一模一样的。当设置为同步串行通信时，此时在通信接口增加了一个时钟线，用于同步时钟用从而不再需要设置波特率。

<!-- slide: 11 -->

- (3) SPI
- SPI接口信号：（1）MOSI，主器件数据输出，从器件数据输入；（2）MISO，主器件数据输入，从器件数据输出；（3）SCLK，时钟信号，由主器件产生；（4）/SS，从器件使能信号，由主器件控制，有的IC会标注为/CS(Chip select)。
![image](assets/assets/embedded-systems-011/image-005.png)

> 备注：SPI（Serial Peripheral Interface）是一种高速的、全双工、同步的通信总线。Motorola公司首先在其MC68HCXX系列处理器上定义的。SPI接口主要应用在EEPROM、Flash、实时时钟、A/D转换器，还有数字信号处理器和数字信号解码器之间。

<!-- slide: 12 -->

- 7.2 STM32 USART接口
- USART具有全双工、异步和支持单线半双工通信功能，数据传输是NRZ（Non Return Zero）不归零码标准格式。主要支持异步串行通信（UART）和同步串行通信（USART）两种模式；支持LIN主/从设备，LIN具有主异步间隙发送功能和从间隙检测功能，当把USART配置成LIN时，可以产生13位间隙和10/11位间隙检测；具有智能卡模拟功能，支持ISO 7816-3标准异步智能卡协议，此时通信可以有0.5或者1.5个停止位；具有IrDA SIR编解码功能，在正常模式下支持3/16位宽度；支持硬件流控制（CTS和RTS）；支持多处理器通信，如果地址匹配不成功，则进入静默模式。

<!-- slide: 13 -->

- 7.2.1 USART硬件引脚
- USART数据通信主要通过发送数据TX引脚和接收数据RX引脚实现；CTS引脚和RTS引脚主要用于硬件溢出控制，当通信的数据量不是很大时，这两个引脚通常并不使用；CK引脚用于USART同步通信时的时钟信号。STM32F103R6芯片有两路USART接口。
![image](assets/assets/embedded-systems-011/image-006.png)

<!-- slide: 14 -->

- 7.2.2 USART主要寄存器及中断请求
- 围绕着发送器和接收器控制部分，有多个寄存器(CR1、CR2、CR3、SR)，即USART的3个控制寄存器及1个状态寄存器，通过向寄存器写入各种控制参数来控制发送和接收，如奇偶校验位、停止位等，还包括对USART中断的控制；串口的状态在任何时候都可以从状态寄存器中查询到。
![image](assets/assets/embedded-systems-011/image-007.png)

<!-- slide: 15 -->

- USART的各种中断事件被连接到同一个中断向量（USART中断），有以下各种中断事件：
- 发送期间：发送完成、清除发送、发送数据寄存器空。
- 接收期间：空闲总线检测、溢出错误、接收数据寄存器非空、校验错误、LIN断开符号检测、噪声标志(仅在多缓冲器通信)和帧错误(仅在多缓冲器通信)。
- 如果设置了对应的使能控制位，这些事件就可以产生各自的中断。
![image](assets/assets/embedded-systems-011/image-008.png)
- (1)仅当使用DMA接收数据时，才使用这个标志位。

<!-- slide: 16 -->

- 7.2.3 异步通信（UART）
- （1）具有可编程波特率发生器，设置发送和接收波特率可达到2M，实现数据高速传输。
- （2）数据传输格式可编程，可以是8位或者9位，可由程序设定。
- （3）停止位可以根据需要配置1位或者2位。
- （4）奇偶控制，发送奇偶位，数据接收检查奇偶位；可以生成奇校验、偶校验和无校验位。
- （5）硬件流控制，利用nCTS输入和nRTS输出可以控制2个设备间的串行数据流。

<!-- slide: 17 -->

- 7.2.4 USART其他功能模式
- 1.USART同步模式
- 通过在USART_CR2寄存器上写CLKEN位选择同步模式。在同步模式里，下列位必须保持清零状态：USART_CR2寄存器中的LINEN位和USART_CR3寄存器中的SCEN、HDSEL和IREN位。
![image](assets/assets/embedded-systems-011/image-009.png)

<!-- slide: 18 -->

- 2. LIN（局域互联网）模式
- 局域互联网(LIN)总线是为汽车网络开发的一种低成本、低端多路复用通信标准。虽然控制器局域网(CAN)总线满足了高带宽、高级错误处理网络的需求，但是实现CAN的软硬件花费使得低性能设备（如电动车窗和座椅控制器）无法采用该总线。若应用程序无须CAN的带宽及多用性，可采用LIN这种高性价比的通信方式。LIN模式是通过设置USART_CR2寄存器的LINEN位选择。在LIN模式下，下列位必须保持为0：USART_CR2寄存器的CLKEN位；USART_CR3寄存器的STOP[1:0]，SCEN，HDSEL和IREN。

<!-- slide: 19 -->

- 3. 智能卡模式
- USART有一个与ISO7816兼容的模式。该模式允许与智能卡连接，并可通过ISO7816链接与安全访问模块（Security Access Modules，SAM）通信。智能卡是一个单线半双工通信协议，当USART与智能卡相连接时，USART的TX驱动一根智能卡也驱动的双向线，USART可以通过CK输出为智能卡提供时钟。设置USART_CR3寄存器的SCEN位选择智能卡模式。在智能卡模式下，下列位必须保持清零：USART_CR2寄存器的LINEN位和USART_CR3寄存器的HDSEL位和IREN位；此外，CLKEN位可以被设置，以提供时钟给智能卡。STM32芯片该接口符合ISO7816-3标准，支持智能卡异步协议。

<!-- slide: 20 -->

- 4. IrDA SIR ENDEC功能模块
- IrDA是一个半双工通信协议，IrDA SIR物理层规定使用反相归零调制方案(RZI)，该方案用一个红外光脉冲代表逻辑0。SIR发送编码器对从USART输出的NRZ(非归零)比特流进行调制，输出脉冲流被传送到一个外部输出驱动器和红外LED，USART为SIR ENDEC最高只支持到115.2kbps速率。SIR接收解码器对来自红外接收器的归零位比特流进行解调，并将接收到的NRZ串行比特流输出到USART。

<!-- slide: 21 -->

- 5. 单线半双工通信
- 单线半双方模式通过设置USART_CR3寄存器的HDSEL位选择。在这个模式里，下面的位必须保持清零状态：USART_CR2寄存器的LINEN和CLKEN位以及USART_CR3寄存器的SCEN和IREN位。
- USART可以配置成遵循单线半双工协议。在单线半双工模式下，TX和RX引脚在芯片内部互连。使用控制位”HALF DUPLEX SEL”(USART_CR3中的HDSEL位)选择半双工和全双工通信。当HDSEL为1时，RX不再被使用；当没有数据传输时，TX总是被释放。因此，它在空闲状态的或接收状态时表现为一个标准I/O口。这就意味着该I/O在不被USART驱动时，必须配置成悬空输入(或开漏的输出高)。

<!-- slide: 22 -->

- 6. 多处理器通信
- 通过USART可以实现多处理器通信(将几个USART连在一个网络里)。例如某个USART设备可以是主，它的TX输出和其他USART从设备的RX输入相连接；USART从设备各自的TX输出逻辑地与在一起，并且和主设备的RX输入相连接。在多处理器配置中，我们通常希望只有被寻址的接收者才被激活，来接收随后的数据，这样就可以减少由未被寻址的接收器的参与带来的多余的USART服务开销。

<!-- slide: 23 -->

- 7.3 UART异步串行操作
- UART接口通过RX（接收数据输入）、TX（发送数据输出）和GND三个引脚与其他设备连接在一起。USART串口通信模块一般分为3部分：时钟发生器、数据发送器和接收器。其中，时钟发生器主要用于异步串行通信波特率设置，波特率是串行通信的重要指标，用于表征数据传输的速度。

<!-- slide: 24 -->

- 7.3.1 串行数据发送和接收
- 1.对数据发送和接收的GPIO口进行初始化。
- 以STM32F103R6芯片的USART1模块为例，PA9可复用为TX功能口，PA10可复用为RX功能口，因此可对这两个接口进行配置，STM32CubeMX工具配置图如图所示。
![image](assets/assets/embedded-systems-011/image-010.png)

<!-- slide: 25 -->

- 2.对串行通信配置
- 对串口通信的参数进行配置，其中包括波特率、字长、是否奇偶校验和停止位。例如配置通信的波特率为9600bps，字长8位，不用奇偶校验和停止位1，异步通信模式，不需要硬件流控，利用STM32CubeMX工具配置图如图所示。
![image](assets/assets/embedded-systems-011/image-011.png)

<!-- slide: 26 -->

- 3.发送数据
- 当内核或DMA外设把数据写入到发送数据寄存器（TDR）后，发送控制器自动把数据加载到发送移位寄存器中，然后通过串口线TX，把数据逐位送出去。当数据从TDR转移到移位寄存器时，会产生发送寄存器TDR已空事件TXE；当数据从移位寄存器全部发送出去时，会产生数据发送完成事件TC，这些事件可以在状态寄存器中查询到。
![image](assets/assets/embedded-systems-011/image-012.png)
- 基于HAL库实现可直接调用库提供的串口通信发送函数实现对数据的发送，在发送过程中，有阻塞模式发送和非阻塞模式发送两种方式，其中阻塞模式发送通过HAL_UART_Transmit()函数来实现；非阻塞模式若是利用中断实现，则通过HAL_UART_Transmit_IT()函数来实现，非阻塞模式若利用DMA实现，则通过HAL_UART_Transmit_DMA()函数来实现。

<!-- slide: 27 -->

- 4.接收数据
- 接收数据是从串口线RX逐位地输入到接收移位寄存器中，然后自动地转移到接收数据寄存器RDR，并会产生接收数据事件RXNE表示数据已收到，在查询到RXNE位置1后，把数据读取1内存中。
![image](assets/assets/embedded-systems-011/image-013.png)
- 基于HAL库实现可直接调用库提供的串口通信接收函数实现对数据的接收，接收数据也有阻塞和非阻塞两种方式，其中查询方式采用循环的方式检测是否有数据，如果没有将继续检测，这是一种阻塞方式的接收，通过HAL_UART_Receive()函数来实现；非阻塞方式可通过中断方式进行实现，通过HAL_UART_Receive_IT()和HAL_UART_IRQHandler()两个函数来实现；非阻塞方式也可通过DMA进行实现，通过HAL_UART_Receive_DMA()函数来实现。

<!-- slide: 28 -->

- 7.3.2 UART数据发送和接收应用实例
- 实现基于USART1的串口发送和接收应用实例，最开始运行时发送字符串“Hello 2021”，随后等待接收的数据，并把接收的数据发送处理。
![image](assets/assets/embedded-systems-011/image-014.gif)

<!-- slide: 29 -->

- 【例7.1】使用查询方式实现。
- （1）分析STM32CubeMX工具生成的代码。
![image](assets/assets/embedded-systems-011/image-015.png)
- 同时在生成的usart.c文件中的void HAL_UART_MspInit(UART_HandleTypeDef* uartHandle)函数中，把PA9和PA10引脚配置成USART1的TX和RX功能口。

<!-- slide: 30 -->

- （2）接着在main.c文件中，主要代码如下：
![image](assets/assets/embedded-systems-011/image-016.png)
![image](assets/assets/embedded-systems-011/image-017.png)

<!-- slide: 31 -->

- 【例7.2】使用中断方式实现
- 由于中断采用非阻塞的方式处理数据，对其他运行的程序影响较小，因此常采用中断方式进行串行数据传输，尤其是数据接收的过程经常采用中断的方式。
- (1) 首先需要配置好接收中断，利用STM32CubeMX工具实现配置，使能USART1中断，设置抢占优先级1，相应优先级0，
![image](assets/assets/embedded-systems-011/image-018.png)

<!-- slide: 32 -->

- （2）生成的代码结构和查询方式类似，只是在stm32f1xx_it.c文件中调用了HAL_UART_IRQHandler(&huart1)函数。
![image](assets/assets/embedded-systems-011/image-019.png)
- 在HAL_UART_IRQHandler(&huart1)函数中调用了UART_Receive_IT(huart)函数，而在UART_Receive_IT(huart)函数中又调用了接收中断的回调函数HAL_UART_RxCpltCallback(huart)，此函数为__weak类型，因此用户可以重写此函数。
- （3）在usart.c程序中修改代码。
- 在void MX_USART1_UART_Init(void)函数中开启接收中断的程序，开始接收数据：
- HAL_UART_Receive_IT(&huart1, &rxdata, 1);  //开启接收中断，开始接收数据
- 注意，rxdata在main.c中声明和使用的，所以要在usart.c中使用此变量，需要声明如下：extern uint8_t rxdata。

<!-- slide: 33 -->

- （4）在main.c程序中重写HAL_UART_RxCpltCallback(huart)。
- 当有数据接收时触发接收中断，在中断回调函数中实现对数据的发送并开始接收下一个数据。
![image](assets/assets/embedded-systems-011/image-020.png)

<!-- slide: 34 -->

- 7.3.3 RS-232接口
- RS-232C标准对逻辑电平的定义，它规定逻辑1的电平范围是-3~-15V；逻辑0的电平范围是+3~+15V。介于-3～+3V之间的电压无意义，低于-15V或高于+15V的电压也认为无意义，因此，实际工作时，应保证电平在-3～-15V或+3～+15V之间。
![image](assets/assets/embedded-systems-011/image-021.png)
![image](assets/assets/embedded-systems-011/image-022.png)

<!-- slide: 35 -->

- RS-232C与TTL转换：RS-232C是用正负电压来表示逻辑状态，与TTL以高低电平表示逻辑状态的规定不同。因此，为了能够同计算机接口或终端的TTL器件连接，必须在RS-232C与TTL电路之间进行电平和逻辑关系的变换。实现这种变换的方法可用分立元件，也可用集成电路芯片。目前较为广泛地使用集成电路转换器件，MAX232芯片可完成TTL↔RS-232C双向电平转换：
![image](assets/assets/embedded-systems-011/image-023.png)
![image](assets/assets/embedded-systems-011/image-024.jpg)

> 备注：其中，COM口主要在PC或老型号的笔记本电脑上才有，目前主流PC很多已经没有COM接口，所以目前微控制器UART接口主要是通过USB转串口（见图7.17）实现和PC的通信。USB转串口即实现PC USB接口到通用串口之间的转换。为没有串口的PC提供快速通道，而且，使用USB转串口等于将传统的串口设备变成了即插即用的USB设备。

<!-- slide: 36 -->

- 【例7.3】 实现STM32芯片与PC的串行通信
- 利用Virtual Serial Port Driver产生出虚拟串口设备，例如，产生出连接的COM2和COM3。
![image](assets/assets/embedded-systems-011/image-025.png)

<!-- slide: 37 -->

- 7.3.4 printf串口终端实现
- 【例7.4】 在微控制器上面使用串口时，有时候为了方便调试看一下输出结果，会用到printf函数输出到电脑终端，再用串口助手显示。
- （1）首先添加头文件#include “stdio.h”，因为printf在这个里面。
- （2）需要重定义fputc函数。
- 可以在usart.c文件中实现：
- //重定义fputc函数
- int fputc(int ch,FILE *f)
- {
- HAL_UART_Transmit(&huart1,(uint8_t *)&ch,1,0xffff);
- return ch;
- }

<!-- slide: 38 -->

- （3）主程序。
![image](assets/assets/embedded-systems-011/image-026.png)

<!-- slide: 39 -->

- 7.3.5 RS-485总线
- RS-485通信网络中一般采用的是主从通信方式，即一个主机带多个从机。连接RS-485通信链路时，只是简单地用一对双绞线将各个接口的“A”、“B”端连接起来。具有如下特点：
- （1）RS-485采用差分信号，+2～+6V表示“0”，-6～-2V表示“1”。RS-485有两线制和四线制两种接线，四线制是全双工通信方式，两线制是半双工通信方式。
- （2）RS-485的数据最高传输速率为10Mbps。
- （3）RS-485接口是采用平衡驱动器和差分接收器的组合，抗共模干扰能力增强，即抗噪声干扰性好。
- （4）RS-485最大的通信距离约为1219m，最大传输速率为10Mbps，传输速率与传输距离成反比，在100kbps的传输速率下，才可以达到最大的通信距离，如果需传输更长的距离，需要加RS-485中继器。RS-485总线一般最大支持32个节点，如果使用特制的RS-485芯片，可以达到128个或者256个节点，最大的可以支持到400个节点。

<!-- slide: 40 -->

- RS-485总线电路主要是UART接口通过连接RS-485电平转换芯片（如MAX487）把TTL电平转为RS-485差分信号，输出为A和B。
![image](assets/assets/embedded-systems-011/image-027.png)
- 本电路采用2线RS-485通信，所以是半双工通信模式，通过PB0控制MAX487芯片的/RE和DE引脚设定是发送状态还是接收状态，当/RE为低电平时为接收状态，当DE为高电平时为发送状态。

<!-- slide: 41 -->

- 【例7.5】 STM32F103R6芯片通过RS-485总线向接收端发送“Hello RS-485 2021”字符串。
- （1）利用STM32CubeMX产生出gpio.c中初始化PB0的代码如下：
![image](assets/assets/embedded-systems-011/image-028.png)
- （2）在main.c 代码中实现如下主要代码：
![image](assets/assets/embedded-systems-011/image-029.png)

<!-- slide: 42 -->

![image](assets/assets/embedded-systems-011/image-030.gif)

<!-- slide: 43 -->

- 7.4 基于串口的无线通信
- 很多无线通信都可以通过串行UART接口和微控制器进行通信。程序开发过程都是直接用串口通信程序代码就行，在软件层不用修改什么，主要是硬件模块不同。

<!-- slide: 44 -->

- 7.4.1 移动通信
- 移动通信已经走过四个时代1G、2G、3G、4G，现正向第五代即5G迈进。1G模拟通信，标准有AMPS，TACS，NMT；2G数字通信,标准有GSM，D-AMPS；2.5G数字通信，标准有GPRS；2.75G数字通信，标准有EDGE；3G数字通信，标准有CDMA2000，WCDMA，TD-SCDMA；4G数字通信，标准有LTE，TD-LTE，FDD-LTE；5G数字通信，标准有NR。
![image](assets/assets/embedded-systems-011/image-031.png)

<!-- slide: 45 -->

- 广和通4G CAT1通信模块L610，通过其模块上串行通信接口和STM32芯片控制板进行串行通信，可以实现微控制器通过4G通信网络的数据收发。
- L610模块提供TTL串口和微控制器芯片连接。在微控制器芯片编写串口驱动，发送和接收相应的AT指令集，从而实现4G LTE数据通信的功能。
![image](assets/assets/embedded-systems-011/image-032.png)

<!-- slide: 46 -->

- 7.4.2 蓝牙（BlueTooth) 串口
- 蓝牙串口是基于SPP协议（Serial Port Profile），能在蓝牙设备之间创建串口进行数据传输的一种设备。蓝牙串口的目的是针对如何在两个不同设备（通信的两端）上的应用之间保证一条完整的通信路径。
![image](assets/assets/embedded-systems-011/image-033.png)

<!-- slide: 47 -->

- 7.4.3 串口无线网络(WiFi)
- 串口转WiFi模块是新一代嵌入式WiFi模块，体积小，功耗低。采用UART接口，内置IEEE802.11 协议栈以及TCP/IP协议栈，能够实现用户串口到无线网络之间的转换。串口转WiFi模块ESP8266支持串口透明数据传输模式并且具有安全多模能力，使传统串口设备更好的加入无线网络。
![image](assets/assets/embedded-systems-011/image-034.png)

<!-- slide: 48 -->

- 7.4.4  Zigbee通信
- ZigBee技术是一种短距离、低数据速率、低功耗、低成本的双向无线通信技术。ZigBee技术适用于短距离的无线控制系统，为自动控制和远程控制领域的技术发展提供了有效的协议标准。目前微控制芯片主要通过串口连接ZigBee模块，从而实现ZigBee无线组网和通信，所以在程序开发中主要是通过串口发送和接收数据来完成。如图7.26是一款ZigBee通信模块，可以连接微控制器。
![image](assets/assets/embedded-systems-011/image-035.png)

<!-- slide: 49 -->

- 7.5 串行同步通信（SPI）
- SPI(Serial Peripheral Interface，串行外设接口)总线系统是一种同步串行外设接口，它可以使微控制器与各种外围设备以串行方式进行通信。SPI总线可直接与各个厂家生产的多种标准外围器件相连，包括Flash、网络控制器、LCD显示驱动器、A/D转换器和微控制器等。

<!-- slide: 50 -->

- 7.5.1 STM32芯片SPI接口
- STM32F103R6芯片具有1个SPI接口，具体结构如图
![image](assets/assets/embedded-systems-011/image-036.png)
- STM32芯片SPI有主从两种方式，主模式在SCK引脚产生时钟；从模式SCK引脚用来接收从主设备传来的时钟。引脚MISO主设备输入从设备输出；MOSI主设备输出从设备输入；SCK时钟，由主设备输出从设备输入；NSS从设备选择，用于作为“片选引脚”。

> 备注：NSS引脚有两种模式：硬件NSS模式和软件NSS模式。硬件NSS是指SPI自动控制SPI的片选信号，发送数据时，输出低电平；不发送数据时，输出高电平。由于硬件模式需要自动置位和复位，而有时不成功，故一般不用NSS，这种方式只能一个SPI接一个从机。软件NSS：就是用软件的方式（普通I/O口）控制SPI的片选，发送数据时，软件置片选为低；结束传输时，软件置片选为高。此时一个SPI可以控制多个从机。

<!-- slide: 51 -->

- STM32芯片SPI接口内部结构图
![image](assets/assets/embedded-systems-011/image-037.png)
- SPI_CR1和SPI_CR2是SPI接口的控制寄存器用来设置SPI接口，SPI_SR是SPI接口的状态寄存器用来读取SPI接口的状态。
- NSS有内部和外部引脚，针对NSS软件模式，NSS外部引脚和内部断开，NSS引脚上的IO值将忽略。

<!-- slide: 52 -->

- 在对SPI接口初始化后，只需在SPI发送缓冲区中写入要发送的数据，芯片就会通过SPI串口发送出此数据；同理，在SPI接收缓冲区也可以接收到从SPI输入引脚传送过来的数据。
![image](assets/assets/embedded-systems-011/image-038.png)

<!-- slide: 53 -->

- 【例7.6】 STM32芯片通过SPI接口连接串行转并行芯片74HC595，通过SPI接口发送数据"2021"传送给74HC595芯片，74HC595并行输出驱动4位数码管显示"2021"。
![image](assets/assets/embedded-systems-011/image-039.gif)

<!-- slide: 54 -->

- （1）首先使用STM32CubeMX对SPI接口初始化
![image](assets/assets/embedded-systems-011/image-040.png)

<!-- slide: 55 -->

- 产生出的初始化代码如下：
![image](assets/assets/embedded-systems-011/image-041.png)

<!-- slide: 56 -->

- 和SPI接口有关的程序如下：
![image](assets/assets/embedded-systems-011/image-042.png)
- 通过此程序把要发送的数据通过SPI接口传送给74HC595芯片，随后通过控制PA1引脚连接的74HC595芯片的存储寄存器时钟引脚ST_CPST_CP，控制SPI输入转并行输出的数据传送到数码管段码的引脚上，并利用动态数码管方式显示出来。

<!-- slide: 57 -->

- 主程序如下：
![image](assets/assets/embedded-systems-011/image-043.png)

<!-- slide: 58 -->

- 谢谢!
