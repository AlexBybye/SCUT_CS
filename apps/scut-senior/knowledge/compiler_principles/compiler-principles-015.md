---
source_id: compiler-principles-015
course_id: compiler_principles
title: "编译原理A卷"
original_file: "学科资料/编译原理/往年试卷/编译原理A卷.doc"
document_role: past_exam
year: 
locator_type: none
---

# 编译原理A卷

**诚信应考,考试作弊将带来严重后果！**

**华南理工大学期末考试**

**《 编译原理 》试卷** **A**

**注意事项：1.** **考前请将密封线内各项信息填写清楚；**

**2.** **所有答案请直接答在试卷上；**

**3．考试形式：闭卷；**

**4.** **本试卷共 八 大题，满分100分，**	**考试时间120分钟**。

| **题 号** | **一** | **二** | **三** | **四** | **五** | **六** | **七** | **八** | **总分** |
|---|---|---|---|---|---|---|---|---|---|
| **得 分** |  |  |  |  |  |  |  |  |  |
| **评卷人** |  |  |  |  |  |  |  |  |  |

- **填空**    （20分，每题2分）

<!-- question: compiler-principles-015-Q1 -->

1．设G是一个文法，S是它的开始符号，如果 S   >  α，则称α是一个句型。仅由终结符号组成  的句型是一个句子。

<!-- question: compiler-principles-015-Q2 -->

2.  在编译器的设计中，通常采用 EBNF   作为描述程序设计语言语法的工具，从语法上描述程序设计语言。

<!-- question: compiler-principles-015-Q3 -->

3.  词法分析器分析的单词通常可以分为：关键词、标识符、运算符  、常数和界符几种。

4．在编译器设计中，在生成源代码之前，通常在内部采用一种不依赖目标机的结构的代码表示原代码，这种代码被称为      中间代码    。

<!-- question: compiler-principles-015-Q4 -->

5.  表达式a*b+(c+d/(e+f))的逆波兰式（后缀式）为 ab*cdef+/++ 。

<!-- question: compiler-principles-015-Q5 -->

6．对中间代码优化按涉及的范围分为局部优化，循环优化    和全局优化。

<!-- question: compiler-principles-015-Q6 -->

7．  S={a, b}上的正规式a|b的正规集是   {a,b}      。

<!-- question: compiler-principles-015-Q7 -->

8．为了将非LL(1)变换为与之等价的LL(1)文法，通常采用消除左递归和

提取左公共因子对文法进行等价变换。

<!-- question: compiler-principles-015-Q8 -->

9．局部优化主要包括合并已知量、利用公共子表达式和 删除无用赋值等内容。

<!-- question: compiler-principles-015-Q9 -->

10．运行编译程序的计算机称为  宿主机  ，运行编译程序所产生的目标代码的计算机称为  目标机  。

**二、编译过程通常分为哪几个主要阶段？每个阶段的主要功能？**（10分）

**三、设有文法G[S]** **为：**（25分）

S**→**number | List

List**→**  (Seq)

Seq**→**  Seq, S | S

number  **→** **4|5**

其中number是终结符表示数字，其它字符均为非终结符      please pay attention to this

<!-- question: compiler-principles-015-Q10 -->

1．试给出句型(4, (5))的短语， 直接(简单)短语,句柄。(5分)

短语：

直接短语：

句柄：
<!-- question: compiler-principles-015-Q11 -->

1. 请通过消除左递归将该文法变换为等价的LL(1)文法G1。(10分)  kill

<!-- question: compiler-principles-015-Q12 -->

3．针对变换后的文法G1，构造其相应的LL(1)分析表。(10分)kill

**（另）三、设有文法G[S]** **为：**（25分）

*S -> (SEQ)*

*SEQ -> SEQ, Letter| Letter*

*Letter->***a***|***b**

其中**a,** **b**是终结符，其它字符均为非终结符。

<!-- question: compiler-principles-015-Q13 -->

1．给出句型 (**b**,  **a**) 的最左推导。(5分)
<!-- question: compiler-principles-015-Q14 -->

1. 请通过消除左递归将该文法变换为等价的LL(1)文法G1。(5分)

<!-- question: compiler-principles-015-Q15 -->

4．针对变换后的文法G1，构造其相应的LL(1)分析表。(10分)

**四、文法G[S]：**

**S*****→*****(N)*****|a*** 		**N*****→*****N,S** ***|*****S**

**其中“(”、** **“)”、** **“*****a*****”和“,”** **是终结符。（25分）**

<!-- question: compiler-principles-015-Q16 -->

1．构建该文法的  LR(0)有穷确定自动机。[10分]

<!-- question: compiler-principles-015-Q17 -->

2．构建该文法的SLR(1)分析表.[  15分]

<!-- question: compiler-principles-015-Q18 -->

3．请给出对输入串(a, a)#的分析过程[  10分]

**五、把下面的语句翻译成四元式序列。**        （10分）

（只给出最后结果，设nextstat当前值为100）

**while**  **B>D**  **do**  **if**  **B=1**  **then**  **D:=D+1**  **else**  **B:=B*****2**

**六、NFA如下图所示**（10分）kill

![formula-object](assets/compiler-principles-015/image-001.png)
<!-- question: compiler-principles-015-Q19 -->

1. 请给出与该NFA等价的正则表达式(3分)

<!-- question: compiler-principles-015-Q20 -->

2.  请将该NFA确定化为DFA（7分）
