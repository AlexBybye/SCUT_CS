---
source_id: compiler-principles-005
course_id: compiler_principles
title: "编译模拟试题"
original_file: "学科资料/编译原理/编译原理复习提纲、复习课/编译模拟试题.doc"
document_role: past_exam
year: 
locator_type: none
---

# 编译模拟试题

《编译原理》模拟试题

班级             学号            姓名               评分
- **填空**

1．文法G包括四个组成部分：一组终结符号，                 ，一组产生式，以及                    。

2．文法按产生式的形式分为四种类型，它们是：0型文法，又称短语文法；1型文法，又称上下文有关文法；2型文法，又称               文法； 3型文法，又称              文法。

<!-- question: compiler-principles-005-Q1 -->

3．             推导称为规范推导，由                 产生的句型称为规范句型。

4．设G是一个文法，S是它的开始符号，如果 S        α，则称α是一个句型。                   的句型是一个句子。

5  对于一个文法G而言，如果L(G)中                   对应                  ，那么该文法就称为是二义的。

6．通常程序设计语言的单词符号分为五种：基本字、                、常数、              、界限符。

<!-- question: compiler-principles-005-Q2 -->

7．在自底向上分析法中，LR分析法把“可归约串”定义为              。

<!-- question: compiler-principles-005-Q3 -->

8．编译中常用的中间代码形式有逆波兰式、            、           和四元式等。

<!-- question: compiler-principles-005-Q4 -->

9．对中间代码优化按涉及的范围分为局部优化，           和           。

<!-- question: compiler-principles-005-Q5 -->

10．局部优化主要包括合并已知量、            和             等内容。

**二、编译过程通常分为哪几个主要阶段？每个阶段的主要功能？**

**三、设有文法G1**                                                                      G1：S→SaQ  ∣  Q

1．证明句型  **QbRae** 是规范句型                                              Q→QbR  ∣ R

R→cSd ∣ e

<!-- question: compiler-principles-005-Q6 -->

2．给出句型  **QbRae** 的短语，直接短语和句柄：

短语：

直接短语：

句柄：

**四、对于文法G2，填写各产生式的选择集合和G2的预测分析表。**

G2：①  E→TE'                            SELECT(①)={              }

②  E'→+TE’           SELECT(②)={              }

③  E'→ε              SELECT(③)={              }

④ T→FT'                            SELECT(④)={              }

⑤ T'→*FT’           SELECT(⑤)={              }

⑥  T'→ε              SELECT(⑥)={              }

⑦ F→(E)                            SELECT(⑦)={              }

⑧ F→  i               SELECT(⑧)={              }

|  | + | * | ( | ) | i | # |
|---|---|---|---|---|---|---|
| E |  |  |  |  |  |  |
| E' |  |  |  |  |  |  |
| T |  |  |  |  |  |  |
| T' |  |  |  |  |  |  |
| F |  |  |  |  |  |  |

**五、把下面的语句翻译成四元式序列。**

（只给出最后结果，设nextstat当前值为100）

**while  A<C  do  if  A<0  then  A:=A+1  else  A:=A+2**

**六、用基本块代码生成算法生成目标代码。**

（假定允许使用R1和R2寄存器，临时变量Ti  出基本块后都不活跃）

| 四元式 | 选取R | 目标代码 | RVALUE | AVALUE |
|---|---|---|---|---|
| T1：= A+B<br>T2：= C-T1<br>T3：= D*E<br>T4：= F+G<br>T5:= T3-T4<br>W：= T2/T5 |  |  |  |  |
