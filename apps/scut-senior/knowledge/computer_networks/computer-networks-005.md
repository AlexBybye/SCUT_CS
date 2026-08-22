---
source_id: computer-networks-005
course_id: computer_networks
title: "教学资源_参考答案"
original_file: "学科资料/计算机网络（全英&普通）/计算机网络往年试题？（全英&普通）/教学资源_参考答案2.pdf"
document_role: note
year: 
locator_type: page
---

# 教学资源_参考答案

<!-- page: 1 -->

KEY TO SELECTED TEST TWO

I、 BLANK FILLING (14 points)

1. 201:4aff:fe83:721c (2points)
2. CSMA/CD
3. 100
4. flooding, learning, forwarding, filtering（2points）
5. rm,avi,mp4,mpeng2 (not only one key)（2points）
6. Resource (html)，URL，HTTP（2points）
7. RARP,DHCP,Bootp（3points）
8. Flow lable

II、 TRUE OR FALSE (1 point each question, 10 points in total)

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
×
×
×
×
√
√
√
×
×
√

III、
MAKE A CHOICE(2 points each question, 26 points in total)

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
A
D
B
A
B
B
D
A
C
B
No.
11
12
13
Answer
D
A
D

IV、
SHORT ANSWERS (6 points each question, 30 points in total)

1.

① A’s encapsulation
② ARP/proxy ARP
③ Finish encapsulation
④ Send to R1,R1’s process, change MAC address
⑤ Send to R2 from R1,destination MAC is B
⑥ Broadcast to whole LAN which B is in
⑦ B receive bits ,and de-capsulation
2.
There are eight legal values per baud, so the bit rate is thrice the baud rate. At
1200 baud, the data rate is 3600 bps.

<!-- page: 2 -->

amplitude modulation, because it has only changed amplitude.
Every baud has 8 legal values, and accordingly 3 bits are needed. The data rate corresponds
to 1200 baud is 3600b/s. In every cycle there are two amplitudes but one phase.
3. Just compute the four normalized inner products:
（-1-1-1+1+1-1+1+1），（-1-1+1-1+1+1+1-1），（-1+1-1+1+1+1-1-1），（-1+1-1-1-1-1+1-1）

S.A=（1-1+3+1-1+3+1+1）/8=1
S.B=（1-1-3-1-1-3+1-1）/8=－1
S.C=（1+1+3+1-1-3-1-1）/8=0
S.D=（1+1+3-1+1+3-1+1）/8=1，
The result is that A and D sent 1 bits, B sent a 0 bit, and C was silent.

4. m=8,
r
r
m
2
1≤
+
+
,so r=4

No.1 bit has parity collection: 1,3,5,7,9,11
No.2 bit has parity collection: 2、3、6、7、10、11、…
No.4 bit has parity collection: 4、5、6、7、12……
No.8 bit has parity collection: 8、9、10、11、12……
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
11
12
0
1
1
1
0
1
0
1
1
1
1
1
1   010   1111
5.
The entire TCP segment must fit in the 65,515-byte payload field of an IP
packet. Since the TCP header is a minimum of 20 bytes, only 65,495 bytes
are left for TCP data.
65535-20-20

V、 ANALYSIS (20 points)

1. Borrow 3 bit from the last 8 bit, so submask is 255.255.255.111000000
No.
of
subnet

submask
Useable
Address
range

Broadcast
addr.

Network addr.
Is usable?

No.1
255.255.255.224
/
/
222.17.46.0
No
No.2
255.255.255.224
222.17.46.33-
222.17.46.62
222.17.46.63
222.17.46.32
Yes

No.3
255.255.255.224
222.17.46.65-
212.112.32.94
222.17.46.95
222.17.46.64
Yes

No.4
255.255.255.224
222.17.46.97-
222.17.46.126
222.17.46.127
222.17.46.96
Yes

No.5
255.255.255.224
222.17.46.129-
222.17.46.158
222.17.46.159
222.17.46.128
Yes

…………

2.not only

R1-S0：10.0.0.1

R1-E0：222.17.46.33

R1-E1：222.17.46.65

<!-- page: 3 -->

R1-E2：222.17.46.97

R2-S0：10.0.0.2

R2-E0：222.17.46.129

R2-E1：222.17.46.161

R2-E2：222.17.46.193

3.1785(1786)

Down

Initial

Two way

Exstart

Exange

Loading

Full adjacency
