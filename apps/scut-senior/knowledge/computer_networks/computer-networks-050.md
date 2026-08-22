---
source_id: computer-networks-050
course_id: computer_networks
title: "术语和缩写大全"
original_file: "学科资料/计算机网络（全英&普通）/图片笔记（开源，来源未知）/术语和缩写大全.docx"
document_role: note
year: 
locator_type: none
---

# 术语和缩写大全

第一章(标*的不是很必要的)

1. internet：互联网，通用名词，是多个计算机互连而成的网络，协议任意

2.Internet：因特网，专有名词，全球最大最开放的特定计算机网络，采用TCP/IP协议族，前身为美国的ARPANET。

3.ISP：因特网服务提供者(Internet Service Provider)，提供IP地址，中国的ISP有中国电信、移动、联通等。因特网可以基于ISP分为三层：国际性的主干网（完全互连）、区域性和国家性的第二层（大公司等），以及第三层的本地ISP（提供校园网、企业网等）。用户购买调制解调器和路由器可以自己成为ISP

*4.RFC:  因特网技术文档Request For Comments；ISOC:  因特网协会

5.RTT:  往返时间Round-Trip Time，网络信息双向交互一次所需的时间

6.TCP/IP协议：IP协议位于网际层，TCP协议位于运输层，IP协议可以为各种网络应用提供服务，也可以互连不同的网络接口，通常用这两个协议指代整个协议大家族

7.PDU:  协议数据单元Protocol Data Unit，指对等层次之间传送的数据包

8.SDU:  服务数据单元，同一系统内，层与层之间交换的数据包。多个SDU可以合成为一个PDU；一个SDU也可以划分为几个PDU

**第二章：物理层**

1.UTP、STP：无屏蔽双绞线和屏蔽双绞线，可用于局域网

*2.FCC：美国无线电频谱管理机构，联邦通讯委员会

3.ISM: Industrial, Scientific, Medical,  提供无线电频谱的公用频段

4.QAM:  正交振幅调制，包括QAM-16: 12种相位，每种相位有1~2种振幅可选，可以调制出16种码元，每种可以表示4个比特（2^4=16）

5.  奈氏准则：为了避免码间串扰（失真），码元传输速率有上限，提出了理想低通信道和带通信道的最高码元传输速率

6.  香农公式：c  = W*log_2(1+S/N)

7. RZ编码：归零编码；NRZ编码：不归零编码；NRZI编码：反向不归零编码

8. SONET:  光纤传输系统的标准（题目）

9. FHSS:  跳频扩频；DSSS：直列扩频

10. FDM（包括OFDM）、WDM（DWDM）、TDM（包括STDM）、CDMA：都是复用技术。

**第三章：数据链路层**

1.  帧：数据在数据链路层的说法

2.  HDLC协议：对比特流组帧，使之不影响定界作用。

3. MTU：最大传送单元，一个帧中数据部分的最大长度。

4. BER：误码率Bit Error Rate，传输错误的比特占所传输比特总数的比率

5.CRC：循环冗余校验码Cyclic Redundancy Check。

比较常用的有CRC-16, CRC-CCITT, CRC-32，仅仅是生成多项式不同。CRC-16: x^{16}+x^{15}+x^{2}+1, CRC-CCITT: x^{16}+x^{12}+x^{5}+1, CRC-32: x^{32}+x{26}+x{23}+x{22}+x{16}+……，了解即可。

6. SW:停止-等待协议，GBN:回退N帧协议，SR:选择重传协议

7. ACK、NAK：接收方收到发送方的正确数据，向发送方发送ACK信号，如果不接受，则发送NAK信号。

8. ARQ: Automatic Repeat reQuest

9. FDM、TDM、WDM、CDM：频分复用、时分复用、波分复用、码分复用

10. FDMA、TDMA、CDMA：频分多址、时分多址、码分多址

11. DSSS：直接序列扩频

12. MA、CS、CD：多址接入、载波监听、碰撞检测

CSMA/CD协议用于总线型的网络、CSMA/CA协议用于802.11这种无线局域网

13. DCF:  分布式协调功能Distributed Coordination Function

PCF:  点协调功能  Point Coordination Function
