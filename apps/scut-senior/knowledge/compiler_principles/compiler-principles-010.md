---
source_id: compiler-principles-010
course_id: compiler_principles
title: "2011年编译原理期末考试试卷A"
original_file: "学科资料/编译原理/往年试卷/2011年编译原理期末考试试卷A(1).pdf"
document_role: past_exam
year: 2011
locator_type: page
---

# 2011年编译原理期末考试试卷A

<!-- page: 1 -->

… … … … … … … … … … … … … … … … 密… … … … … … … … … … … … … … … … … … 封… … … … … … … … … … … … … … … 线… … … … … … … … … … … … … …

姓名                学号
  学院                  专业                     座位号

诚信应考,考试作弊将带来严重后果！

 华南理工大学期末考试

《 编译原理 》试卷 A 答案

注意事项：1. 考前请将密封线内各项信息填写清楚；
          2. 所有答案请直接答在试卷上；
          3．考试形式：闭卷；

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

<!-- question: compiler-principles-010-Q1 -->

一、
填空  （20 分，每空1 分）

 5．语法分析最常用的两类方法是 _和_   分析法。确定的自顶而下的语法

分析方法通常分为  和

_____________ ________

10. 为了构造不带回溯的递归下降分析程序，我们通常要消除              和

( 密 封 线 内 不 答 题 )

提取      。

<!-- question: compiler-principles-010-Q2 -->

二、编译过程通常分为哪几个主要阶段？每个阶段的主要功能？（15 分）

<!-- question: compiler-principles-010-Q3 -->

三、设有文法G[S] 为：（10 分）

S→SdT | T
T→T<G | G
G→(S) | a
1．证明句型 (SdG)<a 是规范句型
2．试给出句型(SdG)<a 的语法树及该句型的句柄。

《   编译原理   》试卷A 第 1 页 共 4 页

<!-- page: 2 -->

<!-- question: compiler-principles-010-Q4 -->

四、设有文法G[A]为：（15 分）

G[A] ：

A→aABe|a
B→Bb|d
（1） 试给出与G[A]等价的LL（1）文法G'[A]
（2） 构造G'[A]的预测分析表给出输入串aade#的分析过程。

五、文法G[S]及其LR 分析表如下，请给出对输入串baab#的分析过程。（15 分）
G[S]:

（0） S′→S    （1） S→AB      （2） A →aBa
（3） A →ε     （4） B→bAb     （5） B →ε
（1）为这个文法构造LR(0)项目的DFA。（6 分）
（2）按照下面的SLR 分析表给出对输入串baab#的分析过程：（9 分）

《   编译原理   》试卷A 第 2 页 共 4 页

<!-- page: 3 -->

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

<!-- question: compiler-principles-010-Q5 -->

六、把下面的语句翻译成四元式序列。    （10 分）

（只给出最后结果，设LABEL 当前值为100）

while  (A<C) and (B>0)  do

begin

X := X + 1 ;
if  X > 1  then  C:=C+1  else  A:=A*2;
         end;

《   编译原理   》试卷A 第 3 页 共 4 页

<!-- page: 4 -->

<!-- question: compiler-principles-010-Q6 -->

七、构造正规表达式( a | b )

* b 的最小化有穷自动机。  （15 分）

《   编译原理   》试卷A 第 4 页 共 4 页
