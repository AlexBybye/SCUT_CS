---
source_id: software-testing-062
course_id: software_testing
title: "软件测试与质量保证实验"
original_file: "学科资料/软件测试与质量保证/实验内容及模板/软件测试与质量保证实验.docx"
document_role: note
year: 
locator_type: none
---

# 软件测试与质量保证实验

实验（一）
1. 实验目标

学习并掌握googletest，并用其进行单元测试
1. 实验背景：

软件测试是一个庞大而复杂的主题。单元测试是一种将一个单元（如类等）与其他单元隔离开来的测试。单元测试的目的是将程序的每一部分与其他部分隔离开来，证实每一部分的正确性。

googletest是一个非常著名的C++单元测试框架。它可以在不同平台上工作（Linux, Mac OS X, Windows, Cygwin, Windows CE,  以及Symbian），它基于xUnit体系结构。支持自动测试发觉，提供了一套丰富的断言，支持用户自定义断言，死亡测试，致命和非致命错误，值测试和参数化测试，多种运行测试的方式，并且可以生成XML格式的测试报告。
1. 实验内容
  1. 根据课程PPT（第三课），在Windows, VisualStudio平台上配置googletest测试环境。（也可以参考网址https://blog.csdn.net/officercat/article/details/39621423）
  1. 采用googletest对所提供的c++函数（如下所示）进行等价类划分单元测试。
  1. 采用googletest对所提供的c++函数（如下所示）在去掉注释后进行等价类划分单元测试。
1. 实验报告
  1. 提交测试代码
  1. 提交实验报告（word文档），其中包含googletest测试报告。

*被测试功能及代码：*

*程序规定：**"**输入三个数* *a* *、* *b* *、* *c* *分别作为三边的边长构成三角形。通过程序判定所构成的三角形的类型，当此三角形为一般三角形、等腰三角形及等边三角形时，分别作计算周长，高，和面积**。否则返回**-1**"**。用等价类划分方法为该程序进行测试用例设计，并采用**googletest**进行单元测试。*

*#include <iostream>*

*double compute**_triangle_**property**(**double a, double b, double* *c**)*

*{*

*//**if(a + b <= c || a + c <= b || b + c <= a)* *{*

*//**std::cout<<**”**This is not a triangle!**”**<<std::endl;*

*//**return -1;*

*//**}*

*if(a==b && b ==c){*

*return sqrt(3.0) * a * a / 4.0**;*

*}*

*else if(a==b){*

*return sqrt(**a * a* *–* *c * c / 4.0**)**;*

*}*

*else if(a==c){*

*return sqrt(a*a* *–* *b*b /4.0);*

*}*

*else if(b == c**){*

*return sqrt(b*b* *–* *a*a/4.0);*

*else{*

*return a + b + c;*

*}*

*}*

实验（二）
1. 实验目标

学习JMeter的基本知识，包括线程组，采样器，定时器，监听器等。学会使用JMeter进行网络性能测试。
1. 实验背景

Apache JMeter是Apache组织开发的基于Java的压力测试工具。用于对软件做压力测试，它最初被设计用于Web应用测试，但后来扩展到其他测试领域。 它可以用于测试静态和动态资源，例如静态文件、Java  小服务程序、CGI  脚本、Java  对象、数据库、FTP  服务器，等等。JMeter  可以用于对服务器、网络或对象模拟巨大的负载，来自不同压力类别下测试它们的强度和分析整体性能。另外，JMeter能够对应用程序做功能/回归测试，通过创建带有断言的脚本来验证你的程序返回了你期望的结果。为了最大限度的灵活性，JMeter允许使用正则表达式创建断言。
1. 实验内容
  1. 结合教学内容第六课，学会JMeter安装和环境配置
  1. 构建测试计划，对bing.com发起20个线程共循环10次的查询，每次查询间隔5秒，并设置监听器，监听查询过程并保存查询结果。查询内容可从如下列表中选取：软件测试，软件工程，白盒测试，黑盒测试，自动化测试等。
  1. 构建测试计划，从[http://quote.eastmoney.com/stocklist.html](http://quote.eastmoney.com/stocklist.html)中获取白云机场的股票代码，然后根据该股票代码访问其在东方财富网的主页（[http://quote.eastmoney.com/sh???.html](http://quote.eastmoney.com/sh???.html)，问号部分为股票代码），获得白云机场的总市值，净资产，净利润信息，并存储在监听器中。
1. 实验报告

提交(b)和(c)的测试计划(.jmx文件)

总体实验要求：
1. ***鼓励讨论，但禁止互相抄袭实验报告***
1. ***所有需要提交的代码和实验报告，打包后，命名为***

***名字******+******学号******.zip***

***在考试之前******通过微信文件上传系统上传。***
