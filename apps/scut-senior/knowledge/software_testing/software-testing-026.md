---
source_id: software-testing-026
course_id: software_testing
title: "软件测试与维护(试卷B)答案"
original_file: "学科资料/软件测试与质量保证/试卷（大多来自软件学院仓库，本科目只有Lin一人回忆版...）/软件测试与维护(试卷B)答案.doc"
document_role: past_exam_answer
year: 
locator_type: none
---

# 软件测试与维护(试卷B)答案

**诚信应考,考试作弊将带来严重后果！**

**华南理工大学期末考试**

**《软件测试与维护》试卷B**

**注意事项：1.** **考前请将密封线内填写清楚；**

**2.** **前2题答案请直接答在试卷上，第3题答案请答在答题纸上**

**3．考试形式：闭卷；**

**4.** **本试卷共  三  大题，满分100分，**	**考试时间120分钟**。

| **题 号** | **一** | **二** | **三** | **总分** |
|---|---|---|---|---|
| **得 分** |  |  |  |  |
| **评卷人** |  |  |  |  |

1. **Explain the** **following** **concept** **in your own words.( 25 points/5 points each)**

<!-- question: software-testing-026-Q1 -->

1. W model

![image](assets/software-testing-026/image-001.png)

<!-- question: software-testing-026-Q2 -->

1. stub

也有人称为存根程序，用以模拟被测模块工作过程中所调用的模块。桩模块由被测模块调用，它们一般只进行很少的数据处理，例如打印入口和返回，以便于检验被测模块与其下级模块的接口

<!-- question: software-testing-026-Q3 -->

1. Acceptance Testing

在软件产品完成了功能测试和系统测试之后、产品发布之前所进行的软件测试活动它是技术测试的最后一个阶段,也称为交付测试。

<!-- question: software-testing-026-Q4 -->

1. Testcase

满足特定目的的测试数据、测试代码、测试规程的集合

是发现软件缺陷的最小测试执行单元

有特殊的书写标准和基本原则

<!-- question: software-testing-026-Q5 -->

1. software maintenance

软件维护是指软件系统交付使用以后，为了改正错误或满足新的需要而修改软件的过程。4种类型：改正性维护、适应性维护、完善性维护、预防性维护
1. **Answer the** **following** **question** **briefly** **in your own words( 41 points)**

1、Briefly describe  JUnit  framework through drawing its structure graph?  （**8 points**）

![image](assets/software-testing-026/image-002.png)s

2、Briefly describe the primary tasks of  Unit Testing？（**6 points**）

<!-- question: software-testing-026-Q6 -->

1、 模块接口测试

<!-- question: software-testing-026-Q7 -->

2、 模块局部数据结构测试

<!-- question: software-testing-026-Q8 -->

3、 模块边界条件测试

<!-- question: software-testing-026-Q9 -->

4、 模块独立执行通路测试

<!-- question: software-testing-026-Q10 -->

5、 模块的各条错误处理通路测试

3、How do you understand the relation between the Cost of Bugs and time when Bug is found?（6 **points**）

![image](assets/software-testing-026/image-003.png)

4、Please descricbe  the difference between  Top-down Integration and Bottom-up Integration  through drawing their model graph？（**8 points**）
- Top-down
  - Start with top-level modules
  - Use stubs for lower-level modules
  - As each level is completed, replace stubs with next level of modules
- Bottom-up
  - Start with bottom-level modules
  - Use drivers for upper-level modules
  - As each level is completed, replace drivers with next level of modules

|  | **自底向上** | **自顶向下** |
|---|---|---|
| **集成** | **早** | **早** |
| **基本程序能工作时间** | **晚** | **早** |
| **需要驱动程序** | **是** | **否** |
| **需要桩程序** | **否** | **是** |
| **计划与控制** | **容易** | **难** |

绘图，优缺点对比

5、What is the  relation between Software  Testing and  SQA? （**5 points**）
- SQA 是管理工作、审查对象是流程、强调以预防为主
- 测试是技术实施工作、测试对象是产品、主要是以事后检查（文档、程序）为主
- SQA指导测试、监控测试
- 测试为SQA提供依据
- 测试是SQA的一个环节、一个手段

6、What is the Stress Testing? Briefly describe the process of Stress Testing through using  Loadrunner testing tool ?  （8 **points**）

压力测试是一种基本的质量保证行为，它是每个重要软件测试工作的一部分。压力测试是在一种需要**反常数量、频率或资源**的方式下，执行可重复的**负载测试或强度测试**，以检查程序对异常情况的**抵抗能力**，找出**性能瓶颈**。包括：稳定性压力测试和破坏性压力测试。
- 1）Virtual User Generator  创建脚本
- 2）中央控制器（Controller）来调度虚拟用户
- 3）运行脚本
- 分析scenario
- 4）分析测试结果

<!-- question: software-testing-026-Q11 -->

1. **应用题：( 34 points/17 points each)）**

Please draw the program process graph and control flow graph for the following program,and design testcases  through using the techniques of decision coverage?**（17 points）**

void Func(int a, int b,int c)

{

if (a>0 and b>0)

{

a=a-b;

if(c>0)  c=a+b;

else   c=a+1;

}

else c=b+1;

}

判定：a>0 and b>0, a<=0 or b<=0; c>0, c<=0

**程序流程图4分、控制流图3分、判定7分、用例3分**

2、There is a file management system  which  requires users to enter a date that  is expressed by year and month.  The  date  is limited  from  January 1990  to  December 2049 and   is composed of six characters, year  is  expressed by the first four  characters ,  month is  expressed by the last two  characters  .Please  design testcases to  check the date  through using techniques of    Equivalence  Partitioning and Boundary  Conditions. **（17 points）**

<table>
<tr><td>输入等价类</td><td>有效等价类</td><td>编号</td><td>无效等价类</td><td>编号</td></tr>
<tr><td>日期的类型及长度</td><td>1.6位数字字符  and<br>在1990~2049之间and<br>在01~12之间</td><td></td><td>2.有非数字字符<br>3.少于6位数字字符<br>4.多于6位数字字符</td><td></td></tr>
<tr><td>年份范围</td><td></td><td></td><td>5.小于1990<br>6.大于2049</td><td></td></tr>
<tr><td>月份范围</td><td></td><td></td><td>7.小于01<br>8.大于12</td><td></td></tr>
</table>

- 边界值：
- 6位，  1990，2049，01，12
- 6位，5位，7位
- 1990，1989
- 2049，2050
- 00，13

**等价类8分，等价类用例4分，边界值与用例5分，**
