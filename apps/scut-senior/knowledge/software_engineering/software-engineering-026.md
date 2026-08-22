---
source_id: software-engineering-026
course_id: software_engineering
title: "第7章"
original_file: "学科资料/软件工程/课件/第7章.ppt"
document_role: note
year: 
locator_type: slide
---

# 第7章

<!-- slide: 1 -->

- 软件架构理论及实践
- 华南理工大学计算机学院
- 高英
- gaoying@scut.edu.cn
- 2012.2

<!-- slide: 2 -->

- 课 程 内 容
- ◇ 软件体系结构概论
- ◇ 软件体系结构建模
- ◇ 软件体系结构风格
- ◇ 软件体系结构描述
- ◇ 动态软件体系结构
- ◇ Web服务体系结构
- ◇ 基于体系结构的软件开发
- ◇ 软件体系结构的分析与测试
- ◇ 软件体系结构评估
- ◇ 软件产品线体系结构

<!-- slide: 3 -->

- 设计模式
- 设计模式（Design pattern）是一套被反复使用、多数人知晓的、经过分类编目的、代码设计经验的总结。使用设计模式是为了可重用代码、让代码更容易被他人理解、保证代码可靠性。
- 设计模式：是指在软件开发中，经过验证的、用于解决在特定环境下、重复出现的、特点问题的解决方案。

<!-- slide: 4 -->

- 设计模式四人帮
- GOF（“四人帮”，又称Gang of Four，即Erich Gamma, Richard Helm, Ralph Johnson & John Vlissides四人）的《设计模式》，原名《Design Patterns: Elements of Reusable Object-Oriented Software》（1995年出版，出版社：Addison Wesly Longman.Inc），第一次将设计模式提升到理论高度，并将之规范化。该书提出了23种基本设计模式。时至今日，在可复用面向对象软件的发展过程中，新的设计模式仍然不断出现。

<!-- slide: 5 -->

- 框架
- 框架是构成一类特定软件可复用设计的一组相互协作的类，EJB（EnterpriseJavaBeans）是Java应用于企业计算的框架。
- 框架通常定义了应用体系的整体结构类和对象的关系等等设计参数，以便于具体应用实现者能集中精力于应用本身的特定细节。框架主要记录软件应用中共同的设计决策，框架强调设计复用，因此框架设计中必然要使用设计模式。

<!-- slide: 6 -->

![image](assets/software-engineering-026/image-001.png)
![image](assets/software-engineering-026/image-002.png)
- 框架：

<!-- slide: 7 -->

![image](assets/software-engineering-026/image-003.png)

<!-- slide: 8 -->

![image](assets/software-engineering-026/image-004.png)

<!-- slide: 9 -->

![image](assets/software-engineering-026/image-005.png)
![image](assets/software-engineering-026/image-006.png)

<!-- slide: 10 -->

- 设计模式的原则
- "开－闭"原则
- 此原则是由"Bertrand Meyer"提出的。原文是："Software entities should be open for extension,but closed for modification"。就是说模块应对扩展开放，而对修改关闭。
- 里氏代换原则
- 里氏代换原则是由"Barbara Liskov"提出的。如果调用的是父类的话，那么换成子类也完全可以运行。里氏代换原则是继承复用的一个基础。
- 合成复用原则
- 要少用继承，多用合成关系来实现.

<!-- slide: 11 -->

- 依赖倒转原则
- 抽象不应该依赖于细节，细节应当依赖于抽象。
- 要针对接口编程，而不是针对实现编程。
- 传递参数，或者在组合聚合关系中，尽量引用层次高的类
- 接口隔离原则
- 定制服务的例子，每一个接口应该是一种角色，不多不少，不干不该干的事，该干的事都要干
- 抽象类
- 抽象类不会有实例，一般作为父类为子类继承，一般包含这个系的共同属性和方法。
- 迪米特法则
- 最少知识原则。不要和陌生人说话。

<!-- slide: 12 -->

- 一个模式的四个基本要素
![image](assets/software-engineering-026/image-007.png)
![image](assets/software-engineering-026/image-008.png)

<!-- slide: 13 -->

- 接口
![image](assets/software-engineering-026/image-009.png)
![image](assets/software-engineering-026/image-010.png)

<!-- slide: 14 -->

![image](assets/software-engineering-026/image-011.png)

<!-- slide: 15 -->

- 面向接口编程
![image](assets/software-engineering-026/image-012.png)
![image](assets/software-engineering-026/image-013.png)
![image](assets/software-engineering-026/image-014.png)

<!-- slide: 16 -->

![image](assets/software-engineering-026/image-015.png)

<!-- slide: 17 -->

- 不用模式的解决方案
- 假设有一个接口叫Api，然后有一个实现类Impl实现了它，在客户端怎么用这个接口呢？
![image](assets/software-engineering-026/image-016.png)

<!-- slide: 18 -->

![image](assets/software-engineering-026/image-017.png)
![image](assets/software-engineering-026/image-018.png)

<!-- slide: 19 -->

![image](assets/software-engineering-026/image-019.png)

<!-- slide: 20 -->

- 简单工厂
![image](assets/software-engineering-026/image-020.png)

<!-- slide: 21 -->

![image](assets/software-engineering-026/image-021.png)
![image](assets/software-engineering-026/image-022.png)

<!-- slide: 22 -->

- 简单工厂示例代码
![image](assets/software-engineering-026/image-023.png)

<!-- slide: 23 -->

![image](assets/software-engineering-026/image-024.png)
![image](assets/software-engineering-026/image-025.png)
![image](assets/software-engineering-026/image-026.png)

<!-- slide: 24 -->

![image](assets/software-engineering-026/image-027.png)
![image](assets/software-engineering-026/image-028.png)

<!-- slide: 25 -->

![image](assets/software-engineering-026/image-029.png)
![image](assets/software-engineering-026/image-030.png)

<!-- slide: 26 -->

![image](assets/software-engineering-026/image-031.png)

<!-- slide: 27 -->

![image](assets/software-engineering-026/image-032.png)

<!-- slide: 28 -->

![image](assets/software-engineering-026/image-033.png)

<!-- slide: 29 -->

- 可配置的简单工厂
![image](assets/software-engineering-026/image-034.png)

<!-- slide: 30 -->

![image](assets/software-engineering-026/image-035.png)

<!-- slide: 31 -->

![image](assets/software-engineering-026/image-036.png)
![image](assets/software-engineering-026/image-037.png)
![image](assets/software-engineering-026/image-038.png)
![image](assets/software-engineering-026/image-039.png)

<!-- slide: 32 -->

![image](assets/software-engineering-026/image-040.png)
![image](assets/software-engineering-026/image-041.png)

<!-- slide: 33 -->

![image](assets/software-engineering-026/image-042.png)

<!-- slide: 34 -->

- 简单工厂的优缺点
![image](assets/software-engineering-026/image-043.png)
![image](assets/software-engineering-026/image-044.png)

<!-- slide: 35 -->

![image](assets/software-engineering-026/image-045.png)

<!-- slide: 36 -->

![image](assets/software-engineering-026/image-046.png)
![image](assets/software-engineering-026/image-047.png)
![image](assets/software-engineering-026/image-048.png)

<!-- slide: 37 -->

- 工厂方法模式示例代码
![image](assets/software-engineering-026/image-049.png)
![image](assets/software-engineering-026/image-050.png)

<!-- slide: 38 -->

![image](assets/software-engineering-026/image-051.png)

<!-- slide: 39 -->

- 考虑这样一个实际应用：实现一个导出数据的应用框架，来让客户选择数据的导出方式，并真正执行数据导出。

<!-- slide: 40 -->

![image](assets/software-engineering-026/image-052.png)

<!-- slide: 41 -->

![image](assets/software-engineering-026/image-053.png)
![image](assets/software-engineering-026/image-054.png)

<!-- slide: 42 -->

![image](assets/software-engineering-026/image-055.png)
![image](assets/software-engineering-026/image-056.png)

<!-- slide: 43 -->

![image](assets/software-engineering-026/image-057.png)

<!-- slide: 44 -->

![image](assets/software-engineering-026/image-058.png)
![image](assets/software-engineering-026/image-059.png)

<!-- slide: 45 -->

![image](assets/software-engineering-026/image-060.png)

<!-- slide: 46 -->

![image](assets/software-engineering-026/image-061.png)

<!-- slide: 47 -->

![image](assets/software-engineering-026/image-062.png)
![image](assets/software-engineering-026/image-063.png)

<!-- slide: 48 -->

![image](assets/software-engineering-026/image-064.png)

<!-- slide: 49 -->

![image](assets/software-engineering-026/image-065.png)

<!-- slide: 50 -->

![image](assets/software-engineering-026/image-066.png)
![image](assets/software-engineering-026/image-067.png)

<!-- slide: 51 -->

![image](assets/software-engineering-026/image-068.png)

<!-- slide: 52 -->

- 工厂方法模式和IoC/DI有什么关系呢？

<!-- slide: 53 -->

- 单例模式（Singleton）
![image](assets/software-engineering-026/image-069.png)

<!-- slide: 54 -->

- 不用模式的解决方案
![image](assets/software-engineering-026/image-070.png)
![image](assets/software-engineering-026/image-071.png)

<!-- slide: 55 -->

![image](assets/software-engineering-026/image-072.png)
![image](assets/software-engineering-026/image-073.png)

<!-- slide: 56 -->

![image](assets/software-engineering-026/image-074.png)

<!-- slide: 57 -->

![image](assets/software-engineering-026/image-075.png)
![image](assets/software-engineering-026/image-076.png)

<!-- slide: 58 -->

- 单例模式示例代码
![image](assets/software-engineering-026/image-077.png)

<!-- slide: 59 -->

![image](assets/software-engineering-026/image-078.png)
![image](assets/software-engineering-026/image-079.png)

<!-- slide: 60 -->

![image](assets/software-engineering-026/image-080.png)
![image](assets/software-engineering-026/image-081.png)

<!-- slide: 61 -->

![image](assets/software-engineering-026/image-082.png)

<!-- slide: 62 -->

- 使用单例模式重写示例
![image](assets/software-engineering-026/image-083.png)
![image](assets/software-engineering-026/image-084.png)

<!-- slide: 63 -->

![image](assets/software-engineering-026/image-085.png)

<!-- slide: 64 -->

![image](assets/software-engineering-026/image-086.png)

<!-- slide: 65 -->

![image](assets/software-engineering-026/image-087.png)

<!-- slide: 66 -->

![image](assets/software-engineering-026/image-088.png)

<!-- slide: 67 -->

![image](assets/software-engineering-026/image-089.png)
![image](assets/software-engineering-026/image-090.png)

<!-- slide: 68 -->

![image](assets/software-engineering-026/image-091.png)

<!-- slide: 69 -->

![image](assets/software-engineering-026/image-092.png)

<!-- slide: 70 -->

![image](assets/software-engineering-026/image-093.png)
![image](assets/software-engineering-026/image-094.png)

<!-- slide: 71 -->

![image](assets/software-engineering-026/image-095.png)

<!-- slide: 72 -->

![image](assets/software-engineering-026/image-096.png)

<!-- slide: 73 -->

![image](assets/software-engineering-026/image-097.png)

<!-- slide: 74 -->

![image](assets/software-engineering-026/image-098.png)

<!-- slide: 75 -->

- 桥接模式（Bridge）
- 将抽象部分与它的实现部分分离，使它们都可以独立地变化。
- 例：
![image](assets/software-engineering-026/image-099.png)

<!-- slide: 76 -->

- 不用模式的解决方案
![image](assets/software-engineering-026/image-100.png)
![image](assets/software-engineering-026/image-101.png)

<!-- slide: 77 -->

![image](assets/software-engineering-026/image-102.png)

<!-- slide: 78 -->

![image](assets/software-engineering-026/image-103.png)
![image](assets/software-engineering-026/image-104.png)

<!-- slide: 79 -->

![image](assets/software-engineering-026/image-105.png)

<!-- slide: 80 -->

![image](assets/software-engineering-026/image-106.png)

<!-- slide: 81 -->

![image](assets/software-engineering-026/image-107.png)

<!-- slide: 82 -->

![image](assets/software-engineering-026/image-108.png)
![image](assets/software-engineering-026/image-109.png)

<!-- slide: 83 -->

![image](assets/software-engineering-026/image-110.png)

<!-- slide: 84 -->

![image](assets/software-engineering-026/image-111.png)
![image](assets/software-engineering-026/image-112.png)

<!-- slide: 85 -->

![image](assets/software-engineering-026/image-113.png)
![image](assets/software-engineering-026/image-114.png)

<!-- slide: 86 -->

![image](assets/software-engineering-026/image-115.png)

<!-- slide: 87 -->

![image](assets/software-engineering-026/image-116.png)

<!-- slide: 88 -->

![image](assets/software-engineering-026/image-117.png)
![image](assets/software-engineering-026/image-118.png)

<!-- slide: 89 -->

![image](assets/software-engineering-026/image-119.png)

<!-- slide: 90 -->

![image](assets/software-engineering-026/image-120.png)

<!-- slide: 91 -->

![image](assets/software-engineering-026/image-121.png)

<!-- slide: 92 -->

![image](assets/software-engineering-026/image-122.png)
![image](assets/software-engineering-026/image-123.png)

<!-- slide: 93 -->

- 使用桥接模式重写示例
- 1：从简单功能开始
- 从相对简单的功能开始，先实现普通消息和加急消息的功能，发送方式先实现站内短消息和Email这两种。
- 使用桥接模式来实现这些功能的程序结构如图7所示
![image](assets/software-engineering-026/image-124.png)

<!-- slide: 94 -->

![image](assets/software-engineering-026/image-125.png)

<!-- slide: 95 -->

![image](assets/software-engineering-026/image-126.png)
![image](assets/software-engineering-026/image-127.png)

<!-- slide: 96 -->

![image](assets/software-engineering-026/image-128.png)
![image](assets/software-engineering-026/image-129.png)

<!-- slide: 97 -->

![image](assets/software-engineering-026/image-130.png)

<!-- slide: 98 -->

![image](assets/software-engineering-026/image-131.png)
![image](assets/software-engineering-026/image-132.png)

<!-- slide: 99 -->

![image](assets/software-engineering-026/image-133.png)

<!-- slide: 100 -->

![image](assets/software-engineering-026/image-134.png)
![image](assets/software-engineering-026/image-135.png)

<!-- slide: 101 -->

![image](assets/software-engineering-026/image-136.png)
![image](assets/software-engineering-026/image-137.png)

<!-- slide: 102 -->

![image](assets/software-engineering-026/image-138.png)
![image](assets/software-engineering-026/image-139.png)

<!-- slide: 103 -->

- 命令模式
- 如何开机:
![image](assets/software-engineering-026/image-140.png)
- 客户端只是发出命令或者请求，不关心请求的真正接收者是谁，也不关心具体如何实现，而且同一个请求的动作可以有不同的请求内容，当然具体的处理功能也不一样，该怎么实现？

<!-- slide: 104 -->

![image](assets/software-engineering-026/image-141.png)
![image](assets/software-engineering-026/image-142.png)

<!-- slide: 105 -->

![image](assets/software-engineering-026/image-143.png)

<!-- slide: 106 -->

![image](assets/software-engineering-026/image-144.png)
![image](assets/software-engineering-026/image-145.png)

<!-- slide: 107 -->

![image](assets/software-engineering-026/image-146.png)
![image](assets/software-engineering-026/image-147.png)
![image](assets/software-engineering-026/image-148.png)

<!-- slide: 108 -->

![image](assets/software-engineering-026/image-149.png)
![image](assets/software-engineering-026/image-150.png)

<!-- slide: 109 -->

- 使用命令模式来实现示例
![image](assets/software-engineering-026/image-151.png)
![image](assets/software-engineering-026/image-152.png)

<!-- slide: 110 -->

![image](assets/software-engineering-026/image-153.png)
![image](assets/software-engineering-026/image-154.png)

<!-- slide: 111 -->

![image](assets/software-engineering-026/image-155.png)

<!-- slide: 112 -->

![image](assets/software-engineering-026/image-156.png)
![image](assets/software-engineering-026/image-157.png)
![image](assets/software-engineering-026/image-158.png)

<!-- slide: 113 -->

![image](assets/software-engineering-026/image-159.png)
![image](assets/software-engineering-026/image-160.png)

<!-- slide: 114 -->

![image](assets/software-engineering-026/image-161.png)

<!-- slide: 115 -->

![image](assets/software-engineering-026/image-162.png)

<!-- slide: 116 -->

![image](assets/software-engineering-026/image-163.png)
![image](assets/software-engineering-026/image-164.png)

<!-- slide: 117 -->

![image](assets/software-engineering-026/image-165.png)

<!-- slide: 118 -->

- 装饰模式
![image](assets/software-engineering-026/image-166.png)
![image](assets/software-engineering-026/image-167.png)

<!-- slide: 119 -->

- 不用模式的解决方案
![image](assets/software-engineering-026/image-168.png)

<!-- slide: 120 -->

- （2）按照奖金计算的规则，实现奖金计算，示例代码如下：
![image](assets/software-engineering-026/image-169.png)

<!-- slide: 121 -->

![image](assets/software-engineering-026/image-170.png)

<!-- slide: 122 -->

![image](assets/software-engineering-026/image-171.png)

<!-- slide: 123 -->

![image](assets/software-engineering-026/image-172.png)
![image](assets/software-engineering-026/image-173.png)

<!-- slide: 124 -->

- 有何问题
![image](assets/software-engineering-026/image-174.png)
- 如何才能够透明的给一个对象增加功能，并实现功能的动态组合呢？

<!-- slide: 125 -->

![image](assets/software-engineering-026/image-175.png)

<!-- slide: 126 -->

![image](assets/software-engineering-026/image-176.png)
![image](assets/software-engineering-026/image-177.png)

<!-- slide: 127 -->

![image](assets/software-engineering-026/image-178.png)
![image](assets/software-engineering-026/image-179.png)

<!-- slide: 128 -->

![image](assets/software-engineering-026/image-180.png)

<!-- slide: 129 -->

![image](assets/software-engineering-026/image-181.png)

<!-- slide: 130 -->

![image](assets/software-engineering-026/image-182.png)

<!-- slide: 131 -->

![image](assets/software-engineering-026/image-183.png)

<!-- slide: 132 -->

![image](assets/software-engineering-026/image-184.png)

<!-- slide: 133 -->

![image](assets/software-engineering-026/image-185.png)

<!-- slide: 134 -->

![image](assets/software-engineering-026/image-186.png)
![image](assets/software-engineering-026/image-187.png)

<!-- slide: 135 -->

![image](assets/software-engineering-026/image-188.png)

<!-- slide: 136 -->

![image](assets/software-engineering-026/image-189.png)

<!-- slide: 137 -->

![image](assets/software-engineering-026/image-190.png)

<!-- slide: 138 -->

- （4）使用装饰器的客户端
![image](assets/software-engineering-026/image-191.png)
![image](assets/software-engineering-026/image-192.png)

<!-- slide: 139 -->

![image](assets/software-engineering-026/image-193.png)

<!-- slide: 140 -->

![image](assets/software-engineering-026/image-194.png)

<!-- slide: 141 -->

![image](assets/software-engineering-026/image-195.png)
![image](assets/software-engineering-026/image-196.png)

<!-- slide: 142 -->

![image](assets/software-engineering-026/image-197.png)
![image](assets/software-engineering-026/image-198.png)

<!-- slide: 143 -->

![image](assets/software-engineering-026/image-199.png)

<!-- slide: 144 -->

![image](assets/software-engineering-026/image-200.png)

<!-- slide: 145 -->

![image](assets/software-engineering-026/image-201.png)
![image](assets/software-engineering-026/image-202.png)

<!-- slide: 146 -->

![image](assets/software-engineering-026/image-203.png)

<!-- slide: 147 -->

![image](assets/software-engineering-026/image-204.png)

<!-- slide: 148 -->

- 第7章 基于体系结构的软件开发
- 本章作业与思考题
- 1、请把基于体系结构的软件开发模型与其他软件开发模型进行比较。
- 2、请把基于体系结构的软件设计方法与其他软件设计方法进行比较。
- 3、如何才能提高软件系统的可演化性。
