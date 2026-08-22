---
source_id: intelligent-algorithms-002
course_id: intelligent_algorithms
title: CVRP
original_file: "学科资料/智能算法/智能算法竞赛/CVRP.pdf"
document_role: note
year: 
locator_type: page
---

# CVRP

<!-- page: 1 -->

智能算法及应用

带容量约束的车辆路径问题求解

<!-- page: 2 -->

带容量约束的车辆路径问题（CVRP）

CVRP（Capacitated Vehicle Routing Problem）是经典车辆路
径问题，要求在以下限制条件下为多个客户点设计最优路线：

• 容量约束：每辆车有最大载重量（或体积），客户需求总
和不能超过车辆容量。

• 单一服务：每个客户仅由一辆车访问一次。

• 中心仓库：所有车辆从同一仓库出发并返回。

• 核心目标：通常为最小化总行驶距离或使用的车辆数，以
降低运输成本。

<!-- page: 3 -->

带容量约束的车辆路径问题（CVRP）

参数与符号说明：

![image](assets/assets/intelligent-algorithms-002/image-001.png)

<!-- page: 4 -->

带容量约束的车辆路径问题（CVRP）

决策变量：

目标函数：最小化所有车辆的总行驶距离。

<!-- page: 5 -->

带容量约束的车辆路径问题（CVRP）

约束条件：

![image](assets/assets/intelligent-algorithms-002/image-002.png)

![image](assets/assets/intelligent-algorithms-002/image-003.png)

<!-- page: 6 -->

CVRPLIB

CVRPLIB - All Instances
测试Set A (Augerat, 1995)，共27个实例，问题规模32~80

![image](assets/assets/intelligent-algorithms-002/image-004.png)

![image](assets/assets/intelligent-algorithms-002/image-005.png)

<!-- page: 7 -->

测试规则

•
算法不限，算法参数设置不限，也可自行设计新算法或者
改进算法
•
对所有问题应使用一套算法/参数，不可针对不同的问题
进行手动微调（自适应调整是可以的）

•
需自行编写算法代码，不可调相关算法库，编程语言用
C++

•请务必保证测试过程满足上述要求
•否则将只给及格分

<!-- page: 8 -->

测试规则

•
算法的计算限制：
最多50000次目标值的评估（MaxFEs=50000）

任何完整性解的成本计算均记为1次评估，包含：

✓初始种群生成
✓交叉/变异后的子代
✓局部搜索过程生成的每个候选解
……

•
示例1：采用纯遗传算法求解，种群规模50，迭代次数1000，总
评估次数为50*1000=50000，符合要求。
•
示例2：采用遗传算法+局部搜索算法求解，种群规模50，迭代次
数1000，不符合要求。局部搜索时的成本计算需要纳入，如局部
搜索消耗了20000次评估，则遗传算法部分只允许30000次评估。

<!-- page: 9 -->

测试规则

•
求解完成后，对每个实例报道相对百分比误差
（Optimality Gap）：

•
对每个实例运行25次得到统计值，按要求填入结果模版。

•请务必保证测试过程满足上述要求
•否则将只给及格分

<!-- page: 10 -->

测试规则

•
排名规则：

a) 对每个实例的计算结果排一次序，首先对比误差的平均值，

平均值一样时才对比最优值;

b) 求出各小组算法在各个实例上的平均排名，排名最小者为

冠军，其次为亚军，……

<!-- page: 11 -->

提交规则

•
5-6人一组，提交.zip压缩包，包含

a) 1-3页文档（PDF格式、不要超页），包含两部分内容：

- 小组成员介绍，包括姓名、学号、分工和小组自评分
（要求组内平均分为90，且最高分-最低分不小于8分）
- 算法介绍，应包括算法流程、伪代码、参数设置等内容

b) 按模版填写的实验结果数据（Excel格式）

c) 相关代码文件夹

<!-- page: 12 -->

提交规则

•
提交地址：
https://send2me.cn/aloCSDXN/R4yUxAwcEAPlKQ

•
截止时间：2025-04-13 20:00:00（No Extension!!）
