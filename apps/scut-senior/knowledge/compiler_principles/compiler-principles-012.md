---
source_id: compiler-principles-012
course_id: compiler_principles
title: "2011年编译原理期末考试试卷A答案"
original_file: "学科资料/编译原理/往年试卷/2011年编译原理期末考试试卷A答案(1).pdf"
document_role: past_exam_answer
year: 2011
locator_type: page
---

# 2011年编译原理期末考试试卷A答案

<!-- page: 1 -->

… … … … … … … … … … … … … … … … 密… … … … … … … … … … … … … … … … … … 封… … … … … … … … … … … … … … … 线… … … … … … … … … … … … … …

姓名                学号
  学院                  专业                     座位号

诚信应考,考试作弊将带来严重后果！

 华南理工大学期末考试

《 编译原理 》试卷 A 答案

注意事项：1. 考前请将密封线内各项信息填写清楚；
<!-- question: compiler-principles-012-Q1 -->

          2. 所有答案请直接答在试卷上；
<!-- question: compiler-principles-012-Q2 -->

          3．考试形式：闭卷；

<!-- question: compiler-principles-012-Q3 -->

          4. 本试卷共 八 大题，满分100 分， 考试时间120 分钟。

题 号
一
二
三
四
五
六
七
总分
得 分
评卷

人

<!-- question: compiler-principles-012-Q4 -->

一、
填空  （20 分，每空1 分）

<!-- question: compiler-principles-012-Q5 -->

 1．   最右     推导称为规范推导，由  规范推导   产生的句型称为规范句

型。

_____________ ________

<!-- question: compiler-principles-012-Q6 -->

 2．文法按产生式的形式分为四种类型，它们是：0 型文法，又称短语文法；1

( 密 封 线 内 不 答 题 )

型文法，又称上下文有关文法；2 型文法，又称上下文无关文法； 3 型文法，

又称正规文法。

<!-- question: compiler-principles-012-Q7 -->

 3．对于一个文法G 而言，如果L(G)中存在某个句子对应两棵不同的语法树，，

那么该文法就称为是二义的。

<!-- question: compiler-principles-012-Q8 -->

 4．设G 是一个文法，S 是它的开始符号，如果 S=*>α，则称α是一个句型。

仅由终结符号组成的句型是一个句子。

<!-- question: compiler-principles-012-Q9 -->

 5．语法分析最常用的两类方法是自底向上的语法分析_和_自顶向下的语法分析

分析法。确定的自顶而下的语法分析方法通常分为 递归子程序法和  预测

分析法

<!-- question: compiler-principles-012-Q10 -->

 6．编译中常用的中间代码形式有逆波兰式、三元式、树代码和  四元式  等。

<!-- question: compiler-principles-012-Q11 -->

 7．在自底向上分析法中，LR 分析法把“可归约串”定义为  句柄。

<!-- question: compiler-principles-012-Q12 -->

 8．对中间代码优化按涉及的范围分为局部优化，循环优化和全局优化。

<!-- question: compiler-principles-012-Q13 -->

 9．局部优化主要包括合并已知量、利用公共子表达式和删除无用赋值等内容。

<!-- question: compiler-principles-012-Q14 -->

10. 为了构造不带回溯的递归下降分析程序，我们通常要消除 公共子表达式

和提取  左公因子    。

《   编译原理   》试卷A 第 1 页 共 8 页

<!-- page: 2 -->

<!-- question: compiler-principles-012-Q15 -->

二、编译过程通常分为哪几个主要阶段？每个阶段的主要功能？（15 分）

答：编译过程通常分为词法分析、语法分析、语义分析、中间代码生成、代码优

化和目标代码生成六个主要阶段。各个阶段的主要功能如下：

词法分析阶段：读入源程序，对构成源程序的字符流进行扫描和分解，
识别出一个个单词，并表示成计算机内部的形式（TOKEN 字）。

语法分析阶段：在词法分析的基础上，将单词序列分解成各类语法短语，
如“表达式”、“语句”、“程序”等，确定整个输入串是否构成语法上正确的
程序。

语义分析阶段：审查源程序有无语义错误，为代码生成阶段收集类型信
息。

中间代码生成阶段：将源程序翻译成一种复杂性介于源程序与目标程序
之间的内部形式（中间代码）。

代码优化：对前阶段产生的中间代码进行等价变换，目的是使将来生成
的目标代码更为高效。

目标代码生成：把中间代码变换成特定机器上的绝对指令代码或可重定
位的指令代码或汇编指令代码。

<!-- question: compiler-principles-012-Q16 -->

三、设有文法G[S] 为：（10 分）

S→SdT | T
T→T<G | G
G→(S) | a
<!-- question: compiler-principles-012-Q17 -->

1．证明句型 (SdG)<a 是规范句型
证：因为句型 (SdG)<a 可由文法开始符S 经过规范推导产生，推导过程如下：

S =R>T =R> T<G =R> T<a =R> G<a =R> (S)<a=R>(SdT)<a =R>(SdG)<a
所以句型(SdG)<a 是规范句型。
<!-- question: compiler-principles-012-Q18 -->

2．试给出句型(SdG)<a 的语法树及该句型的句柄。

S

T

T     <    G

a

(     S   )

S     d   T

G

语法树：
句柄：G

《   编译原理   》试卷A 第 2 页 共 8 页

<!-- page: 3 -->

<!-- question: compiler-principles-012-Q19 -->

四、设有文法G[A]为：（15 分）

G[A] ：

A→aABe|a
B→Bb|d
<!-- question: compiler-principles-012-Q20 -->

（1） 试给出与G[A]等价的LL（1）文法G'[A]
<!-- question: compiler-principles-012-Q21 -->

（2） 构造G'[A]的预测分析表给出输入串aade#的分析过程。
改造后的文法：
<!-- question: compiler-principles-012-Q22 -->

(1) A->aA’
<!-- question: compiler-principles-012-Q23 -->

(2) A’->ABe |ε
<!-- question: compiler-principles-012-Q24 -->

(3) B->dB’
<!-- question: compiler-principles-012-Q25 -->

(4) B’ ->bB’ |ε

根据LL(1)文法的定义判断:
1)
First（aA’）={a}

First(ABe) ∩First(ε)= {a}∩{ ε}=φ;
First(dB’)={d}
First(bB’) ∩First(ε)={b}∩{ ε}=φ;
2)

考虑A’=>ε,

   First(A’) ∩FOLLOW(A’)={a, ε}∩{d}=φ;
考虑B’ =>ε,
  First(B’) ∩FOLLOW(B’)= {b, ε}∩{e}

根据定义判断修改后的文法是LL(1)文法.

预测分析表

a
b
d
e
#

A
A->aA’

 A’
A’->ABl
A’->ε
A’->ε

B
B->dB’

B’
 B’ ->bB’
B’ ->c

步骤
分析栈
剩余输入串
所用产生式

1
#A
aade#
A->aA’

2
# A’ a
aade#
A 匹配

3
# A’
ade#
A’->ABe

4
#eBA
ade#
A->aA’

5
#eBA’a
ade#
A 匹配

6
#eBA’
de#
A’->ε

7
#eB
de#
B->dB’

8
#eB’d
de#
D 匹配

9
#eB’
e#
B’ ->ε

《   编译原理   》试卷A 第 3 页 共 8 页

<!-- page: 4 -->

10
#e
e#
E 匹配

11
#
#
识别成功

<!-- question: compiler-principles-012-Q26 -->

五、文法G[S]及其LR 分析表如下，请给出对输入串baab#的分析过程。（15 分）
G[S]:

<!-- question: compiler-principles-012-Q27 -->

（0） S′→S    （1） S→AB      （2） A →aBa
<!-- question: compiler-principles-012-Q28 -->

（3） A →ε     （4） B→bAb     （5） B →ε
<!-- question: compiler-principles-012-Q29 -->

（1）为这个文法构造LR(0)项目的DFA。（6 分）

B

I4：S→A B·

A

I2：S→A·B

 B→·bAb

b

B→·

I5：B→b·Ab

A

I7：B→bA·b

 I0：S’→·S

A→·aBa
A→·

b

  S→·AB
  A→·aBa

S

a
b

I9：B→bAb·

I1：S’ →S·

A→·

a

I3：A→a·Ba

a

B I6：A→aB·a

I8：A→aBa·

    B→·bAb

B→·

《   编译原理   》试卷A 第 4 页 共 8 页

<!-- page: 5 -->

<!-- question: compiler-principles-012-Q30 -->

（2）按照下面的SLR 分析表给出对输入串baab#的分析过程：（9 分）

状态
ACTION
GOTO

a
b
$
S
A
B

0
S3
r3
r3
1
2

1
acc

2
r5
S5
r5
4

3
r5
S5
r5
6

4
r1

5
S3
r3
r3
7

6
S8

7
S9

8
r2
r2

9
r4
r4

解：
对输入串baab$的分析过程：

步骤
状态栈
符号栈
输入串
ACTION
GOTO
（1）
0
#
baab#
r3
2
（2）
02
#A
baab#
S5
（3）
025
#Ab
aab#
S3
（4）
0253
#Aba
ab#
r5
6
（5）
02536
#AbaB
ab#
S8
（6）
025368
#AbaBa
b#
r2
7
（7）
0257
#AbA
b#
S9

《   编译原理   》试卷A 第 5 页 共 8 页

<!-- page: 6 -->

（8）
02579
#AbAb
#
r4
4
（9）
024
#AB
#
r1
1
（10）
01
#S
#
acc

<!-- question: compiler-principles-012-Q31 -->

六、把下面的语句翻译成四元式序列。    （10 分）

（只给出最后结果，设LABEL 当前值为100）

while  (A<C) and (B>0)  do

begin

X := X + 1 ;
if  X > 1  then  C:=C+1  else  A:=A*2;
         end;

100:
j< , A , C , 102
101:
j ,
- ,
- ,
0
102:
j> , B , 0 , 104

103:
j ,
- ,
- ,
0
104:
+ , X , 1 , T1
105:
:= , T1 , - ,
X
106:
j >, X , 1,
108
107:
j ,
- ,
- ,
111
108:
+ , C , 1,
T2
109:
:= , T2 , - ,
C
110     j,   -,  -,   100
111:    *,   A,  2,  T3
112:    :=,  T3,  -,  A
113:    j,    -,   -,  100
114
S.CHAIN=114

《   编译原理   》试卷A 第 6 页 共 8 页

<!-- page: 7 -->

* b 的最小化有穷自动机。  （15 分）
解：
<!-- question: compiler-principles-012-Q32 -->

( 1 ) 构造正规表达式( a | b )

<!-- question: compiler-principles-012-Q33 -->

七、构造正规表达式( a | b )

* b 对应的NFA：

a

ε

b
ε

 Y
1
2

X

b

<!-- question: compiler-principles-012-Q34 -->

(2) 用子集法确定化如下表：

I
Ia
Ib
{x,1,2}T0
{1,2}T1
{1,2,Y}T2
 {1,2}T1
{1,2}T1
{1,2,Y}T2
{1,2,Y}T2
{1,2}T1
{1,2,Y}T2
<!-- question: compiler-principles-012-Q35 -->

(3) 确定化后如下图：

《   编译原理   》试卷A 第 7 页 共 8 页

<!-- page: 8 -->

b

T2

b

a

b

T0

T1
a

a

<!-- question: compiler-principles-012-Q36 -->

 (4) 用分割法最小化DFA：
{T0,T1}{T2}
T0 与T1 等价，删除T1

b

a

T0
 T2

b

a

《   编译原理   》试卷A 第 8 页 共 8 页
