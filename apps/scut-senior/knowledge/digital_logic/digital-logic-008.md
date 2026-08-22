---
source_id: digital-logic-008
course_id: digital_logic
title: "计算机学院数字逻辑2024级复习大纲"
original_file: "学科资料/数字逻辑/往年卷/计算机学院数字逻辑2024级复习大纲.doc"
document_role: review_outline
year: 2024
locator_type: none
---

# 计算机学院数字逻辑2024级复习大纲

**2024级数字逻辑复习大纲**

**本课程掌握要点：**

**第一章 数制和编码**

（1）数制转换，主要掌握  2进制、8进制、10进制和16进制的转换关系,包括整数和小数转换。

（2）编码。对8421码，2421码，奇偶校验码，余3码和格雷码特点进行了解。

**第二章**  **逻辑代数基础**

（1）布尔代数定律：2.2.1  逻辑代数的公理和基本定理，一些常用公式：$A+\overline {A}B=A+B$和摩根定律。

（2）三个规则：代入规则，反演规则，对偶规则

（3）逻辑函数证明：公式规则证明法

（4）了解最小项和最大项的特点。

（5）逻辑化简：公式化简法，卡诺图，利用无关项卡诺图化简

**第三章和第六章部分 组合逻辑电路和集成电路**

（1）逻辑门电路

![image](assets/assets/digital-logic-008/image-001.png)

![image](assets/assets/digital-logic-008/image-002.png)

![image](assets/assets/digital-logic-008/image-003.png)    ![image](assets/assets/digital-logic-008/image-004.png)

同或      ![formula-object](assets/assets/digital-logic-008/image-005.png)    ![image](assets/assets/digital-logic-008/image-006.png)

（2）逻辑函数实现（与非，或非，与或非形式）

（3）组合逻辑电路分析

（4）组合逻辑电路设计

（5）组合逻辑电路的竞争和冒险（原因，解决思路）

（6）组合逻辑构件

(a)译码器（3-8译码器），会用译码器实现逻辑电路。

(b)多路选择器（4选1），会用多路选择器实现逻辑电路。

(c)了解加法器，数值比较器的功能，如何应用。

**第四章和第六章部分 同步时序逻辑和集成电路**

（1）时序逻辑电路特点，与组合逻辑电路区别。

掌握JK触发器，D触发器的特征方程。

（2）时序逻辑分析，会分析用JK触发器，D触发器组成的时序逻辑电路。

会写出激励函数，输出函数，状态函数；从而得到状态表（状态转换表），状态图，时序波形图，会在电路分析过程中画出标准的Moore和Mealy型逻辑的状态表（状态转换表）和状态图（状态转移图）。

（3）时序逻辑电路设计，会用分别利用Moore  和  Mealy  状态机实现一个时序逻辑的设计，只掌握用D触发器即可。

(a)会根据实际问题，画出时序状态转移图（直接实现最简即可，书中化简过程方法了解就好）。

(b)会根据状态转移图，状态编码（如何状态编码不做要求）和并会利用D触发器建立出时序逻辑电路图。

（4）了解常用同步时序逻辑电路的功能和特点：寄存器，只读存储器。

（5）掌握时序逻辑构件：计数器（主要器件：74LS163，74LS161,74LS193）

(a)什么是同步/异步置位、什么是同步/异步清零。

(b)会设计任意进制模数的计数器。

(c)会分析计数器电路功能（计数器计数）。

（6）可编程逻辑阵列

(1)可编程逻辑构件。了解PLA、PAL、GAL、FPGA、CPLD的概念和特点。

（2）会用PLA实现逻辑函数，难度不超出书中  P204页 例6.14。

6．可编程逻辑语言

可编程逻辑系列器件的特点、应用及开发过程。

**复习内容参考（仅供参考）：**
- **数制与编码**

**1．考点：**

（1）几种常用的计数体制，十进制、二进制、十六进制、八进制。

（2）不同数制之间的相互转换。

（3）编码形式。

什么是余3码，什么是格雷码，了解编码的形式就好。

**二．逻辑代数**

**1．考点：**

（1）逻辑代数是分析和设计逻辑电路的工具。应熟记基本公式与基本规则。

表1  逻辑代数的基本公式

**$A.1=AA.0=0A+0=AA+1=1AA=0A+A=1AB=BAA+B=B+AA(BC)=(AB)CA(B+C)=AB+ACA+B=C+(A+B)CAB=ABA(A+B)=AA·A̅B=AB(A+B)(A̅+C)=(A+B)(A̅+C)A̅=AAB+AC=AB+AC$**

逻辑代数的基本规则：

**a.代入规则**     对于任何一个逻辑等式，以某个逻辑变量或逻辑函数同时取代等式两端任何一个逻辑变量后，等式依然成立。                                               例如，在反演律中用BC去代替等式中的B，则新的等式仍成立：

b. **对偶规则**

将一个逻辑函数L进行下列变换：                                                   ·→＋，＋ →·                                                   0  →  1，1  →  0  所得新函数表达式叫做L的对偶式.。

对偶规则的基本内容是：如果两个逻辑函数表达式相等，那么它们的对偶式也一定相等。

基本公式中的公式l和公式2就互为对偶 式。

**c.** **反演规则**  将一个逻辑函数L进行下列变换：                                         ·→＋，＋ →·  ；                                         0  →  1，1  →  0  ；                     原变量 → 反变量，  反变量 → 原变量。 所得新函数表达式叫做L的反函数。

利用反演规则，可以非常方便地求得一个函数的反函数。

（2）可用两种方法化简逻辑函数，公式法和卡诺图法。

公式法是用逻辑代数的基本公式与规则进行化简，必须熟记基本公式和规则并具有一定的运算技巧和经验。
- 合并项法
- 吸收法
- 消去法
- 配项法

卡诺图法是基于合并相邻最小项的原理进行化简的，特点是简单、直观，不易出错，有一定的步骤和方法可循。

![image](assets/assets/digital-logic-008/image-008.png)

![image](assets/assets/digital-logic-008/image-009.png)

2．练习题：

**（1）利用公式证明下列等式：**

$AB+BCD+\overline {A}C+\overline {B}C=AB+C$

$A\overline {B}+B\overline {C}+C\overline {A}=\overline {A}B+\overline {B}C+\overline {C}A$

**（2）化简逻辑函数：**

![image](assets/assets/digital-logic-008/image-010.png)

**(3)** **用卡诺图化简逻辑函数：**

![image](assets/assets/digital-logic-008/image-011.png)

（4）**具有无关项的逻辑函数的化简：**

例:某逻辑函数输入是8421BCD码，其逻辑表达式为：   L（A,B,C,D）=∑m（1,4,5,6,7,9）+∑d（10,11,12,13,14,15）   用卡诺图法化简该逻辑函数。

![image](assets/assets/digital-logic-008/image-012.png)

三．**组合逻辑电路的分析和设计**

1．组合逻辑电路的分析：

![formula-object](assets/assets/digital-logic-008/image-013.png)

**例：组合电路如图所示，分析该电路的逻辑功能。**

![formula-object](assets/assets/digital-logic-008/image-014.png)

![image](assets/assets/digital-logic-008/image-015.png)

2．组合逻辑电路的设计：

**![formula-object](assets/assets/digital-logic-008/image-016.png)**

**![image](assets/assets/digital-logic-008/image-017.png)**

**![image](assets/assets/digital-logic-008/image-018.png)**

**画出逻辑电路图：**

![formula-object](assets/assets/digital-logic-008/image-019.png)

**四．组合逻辑模块及其应用**

**1.译码器**

![image](assets/assets/digital-logic-008/image-020.png)

**2.多路选择器**

**（1）4选** **1多路选择器参考书中例题（例6.7，6.8）。**

**（2）8选1多路选择器。**

![image](assets/assets/digital-logic-008/image-021.png)

![image](assets/assets/digital-logic-008/image-022.png)

**练习题：**

1．

![image](assets/assets/digital-logic-008/image-023.png)

2．

![image](assets/assets/digital-logic-008/image-024.png)

**五.时序逻辑电路的分析与设计**

1．触发器

主要掌握边沿型的JK、D触发器，特征方程。

2．会分析JK、D  触发器构成的时序电路（可见书中例题及PPT）

例题：这道题也告诉如何画出Mealy型逻辑的状态表和状态图。

![image](assets/assets/digital-logic-008/image-025.png)

![image](assets/assets/digital-logic-008/image-026.png)

3．会设计D触发器时序电路，在设计时序电路过程中要有状态机思路。

![image](assets/assets/digital-logic-008/image-027.png)

例题：这道题也告诉如何画出Moore型逻辑的状态图和状态表。

（１）设计一个奇偶校验器，数输入信号X中1的个数，如果X中1的个数为奇数，输出Z为1；若X中1的个数为偶数，则输出Z为0。画出状态图和状态表，分别用D触发器构成。

画出状态图：

![formula-object](assets/assets/digital-logic-008/image-028.png)

列出状态表：

![formula-object](assets/assets/digital-logic-008/image-029.png)

利用D触发器来实现：

分别用0，1来表示S0,S1状态，画出次态和输出的卡诺图。

![formula-object](assets/assets/digital-logic-008/image-030.png)

得出：

$$
{Q}^{n+1}=X\overline {{Q}^{n}}+\overline {X}{Q}^{n}
$$

$$
Z={Q}^{n+1}
$$

又因为：  D触发器方程：${Q}^{n+1}=D$

所以：$D=X\overline {{Q}^{n}}+\overline {X}{Q}^{n}$

根据逻辑表达式，画出电路图：

注：本题所实现的状态为Moore状态机，这种状态机的输出电位只与目前所处的状态有关，而与输入信号无立即的关系。

![image](assets/assets/digital-logic-008/image-031.png)

![image](assets/assets/digital-logic-008/image-032.png)

![image](assets/assets/digital-logic-008/image-033.png)

![image](assets/assets/digital-logic-008/image-034.png)

![image](assets/assets/digital-logic-008/image-035.png)

![image](assets/assets/digital-logic-008/image-036.png)

注：本题所实现的状态为Mealy状态机，这种状态机的输出电位不仅与目前所处的状态有关，而且与输入信号也有关联。

**用Moore逻辑来实现**

![image](assets/assets/digital-logic-008/image-037.png)

![image](assets/assets/digital-logic-008/image-038.png)

![image](assets/assets/digital-logic-008/image-039.png)

![image](assets/assets/digital-logic-008/image-040.png)         ![image](assets/assets/digital-logic-008/image-041.png)

![image](assets/assets/digital-logic-008/image-042.png)

**六.时序逻辑电路-计数器**

中规模集成计数器：有同步计数器和异步计数器两大类，而且是多功能的。

| 型号 | 模式 | 预置 | 清零 | 工作频率 |
|---|---|---|---|---|
| 74LS162A | 十进 | 同步 | 同步（低） | 25MHz |
| 74LS160A | 十进 | 同步 | 异步（低） | 25MHz |
| 74LS168 | 十进可逆 | 同步 | 无 | 40MHz |
| 74LS190 | 十进可逆 | 异步 | 无 | 20MHz |
| 74ALS568 | 十进可逆 | 同步 | 同步（低） | 20MHz |
| **74LS163A** | **4****位二进** | **同步** | **同步（低）** | **25MHz** |
| **74LS161A** | **4****位二进** | **同步** | **异步（低）** | **25MHz** |
| 74ALS561 | 4位二进 | 同步 | 同步（低） | 30MHz |
| **74LS193** | **4****位二进可逆** | **异步** | **异步（高）** | **25MHz** |
| 74LS191 | 4位二进可逆 | 异步 | 无 | 20MHz |
| 74ALS569 | 4位二进可逆 | 同步 | 异步（低） | 20MHz |
| 74ALS867 | 8位二进 | 同步 | 同步 | 115MHz |
| 74ALS869 | 8位二进 | 异步 | 异步 | 115MHz |

会设计任意进制模数的计数器。

会分析计数器电路功能（计数器计数）。

**七．存储器，可编程阵列**

**只读存储器：**

![image](assets/assets/digital-logic-008/image-043.png)

可编程逻辑阵列PLA、可编程阵列逻辑(PAL)、通用阵列逻辑（GAL）和高密度可编程逻辑器件（CPLD  和  FPGA）。

了解：

![image](assets/assets/digital-logic-008/image-044.png)
