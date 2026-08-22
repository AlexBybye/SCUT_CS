---
source_id: computer-networks-004
course_id: computer_networks
title: "教学资源_参考答案"
original_file: "学科资料/计算机网络（全英&普通）/计算机网络往年试题？（全英&普通）/教学资源_参考答案1.pdf"
document_role: note
year: 
locator_type: page
---

# 教学资源_参考答案

<!-- page: 1 -->

KEY TO SELECTED TEST ONE

I、 BLANK FILLING (1 points each question, 15 points in total)

1. UTP
2. physical layer
3. email,ftp,telnet (2 points)
4. 11001101.11111111.10101010.11001101 (2 points)
5. 128
6. receiver
7. speed, bus type, network type ( 3 points)
8. the first 30 bits is network-bits.
9. Bps,bps (1 point)
10. Positive acknowledgement with retransmission
11. 1

II、 DICIDE TRUE OR FALSE (1 point each, 10 points in total)

No.
1
2
3
4
5
6
7
8
9
10
Answer
√
×
×
√
×
×
×
√
√
√

III、
MAKE A CHOICE (1 point each question, 15 points intotal

No.
1
2
3
4
5
6
7
8
9
10
Answer
D
C
B
C
A
C
C
A
D
B
No.
11
12
13
14
15
16
17
18
19
20
Answer
B
C
C
E
A
A
D
B
A
B
No.
21
22
23
24
25
Answer
B
D
A
C
B

IV、
SHORT ANSWERS (6 points each question, 30 points in total)

1.key points:
Hello: ①when it starts up②when it send keep-alive message periodically.
DD(database description):the abstract of link state database, It’s used when two OSPF
routers are in exchange-status.

LSR(link state request): It’s sent when one OSPF router know the other router has a full
record about a link.

LSU(link state update): ①as an answer of LSR ②send when OSPF router discover that
its link has changed.

LSA(link state acknowledgement): when an OSPF router receives a LSU, It must send
back a LSA.

<!-- page: 2 -->

2.Principle:
Flooding
Filtering
Forwarding
Learning
3.
Step 1:H send S SYN segment,it’s  header:

Destination
port=_______80__________
Sequence number=_____200________
Acknowledge number=___________________
Step 2:S send back it’s SYN,it’s header:

Source
port=____3000______________

Destination
port=_____3000____________
Sequence number=_____500________
Acknowledge number=_____201______________
Step 3: H send S final acknowledgement, it’s header:

Source
port=____80______________

Destination
port=____80_____________
Sequence number=____201_________
Acknowledge number=___501________________
4.

Source
port=____3000______________

5. is error, correct code should be: 00101000100
No.1 bit has parity collection: 1,3,5,7,9,11
No.2 bit has parity collection: 2、3、6、7、10、11、…
No.4 bit has parity collection: 4、5、6、7、……

<!-- page: 3 -->

No.8 bit has parity collection: 8、9、10、11、……

V、 ANALYSIS (20 points)

1．Borrow 3 bit from the last 8 bit, so submask is 255.255.255.111000000
No. of
subnet

Network addr.
Is
usable?
No.1
255.255.255.224
/
/
212.112.32.0
No
No.2
255.255.255.224
212.112.32.33-
212.112.32.62
212.112.32.63
212.112.32.32
Yes

submask
Useable Address
range

Broadcast
addr.

No.3
255.255.255.224
212.112.32.65-
212.112.32.94
212.112.32.95
212.112.32.64
Yes

No.4
255.255.255.224
212.112.32.97-
212.112.32.126
212.112.32.127
212.112.32.96
Yes

No.5
255.255.255.224
212.112.32.129-
212.112.32.158
212.112.32.159 212.112.32.128
Yes

…………
2.can be many answer
3.must be identical as No.2
Destination
network addr.

Interface
Gateway addr.(nethop)
Metric(cost)

212.112.32.96
S0
212.112.32.65
1
212.112.32.32
E0
212.112.32.62
0
212.112.32.63
S0
212.112.32.66
0
4. must be identical as No.2 and N0.3
Destination
network addr.

Interface
Gateway addr.(nethop)
Metric(cost)

212.112.32.96
S0
212.112.32.65
1
212.112.32.32
S0
212.112.32.65
2
212.112.32.63
S0
212.112.32.66
0
