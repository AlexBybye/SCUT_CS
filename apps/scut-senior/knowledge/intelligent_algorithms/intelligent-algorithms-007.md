---
source_id: intelligent-algorithms-007
course_id: intelligent_algorithms
title: "10. 价值学习方法pr"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/10. 价值学习方法pr.pdf"
document_role: note
year: 
locator_type: page
---

# 10. 价值学习方法pr

<!-- page: 1 -->

智能算法及应用

10. 价值学习方法
智能算法及应用@华南理工大学2025

<!-- page: 2 -->

价值学习

智能算法及应用@华南理工大学2025

（为了方便描述，下面我们将Q∗函数简记为Q ）

<!-- page: 3 -->

Q-Learning

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-001.png)

<!-- page: 4 -->

Q-Learning

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-002.png)

![image](assets/assets/intelligent-algorithms-007/image-003.png)

![image](assets/assets/intelligent-algorithms-007/image-004.png)

<!-- page: 5 -->

Q-Learning

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-005.png)

<!-- page: 6 -->

深度Q网络（DQN）

智能算法及应用@华南理工大学2025

这里注意到：动作集合有多少个动作，网络就需要多少个输出节点，
隐含了我们的动作是有限个的离散动作。

![image](assets/assets/intelligent-algorithms-007/image-006.png)

<!-- page: 7 -->

深度Q网络（DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-007.png)

<!-- page: 8 -->

深度Q网络（DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-008.png)

<!-- page: 9 -->

深度Q网络（DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-009.png)

<!-- page: 10 -->

经验回放（Experience Replay）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-010.png)

![image](assets/assets/intelligent-algorithms-007/image-011.png)

<!-- page: 11 -->

经验回放（Experience Replay）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-012.png)

<!-- page: 12 -->

经验回放（Experience Replay）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-013.jpeg)

<!-- page: 13 -->

目标网络（Target Network）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-014.png)

<!-- page: 14 -->

目标网络（Target Network）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-015.jpeg)

<!-- page: 15 -->

目标网络（Target Network）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-016.jpeg)

<!-- page: 16 -->

深度Q网络（DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-017.png)

![image](assets/assets/intelligent-algorithms-007/image-018.jpeg)

<!-- page: 17 -->

DQN的进一步改进

算法名称
核心创新
解决的关键问题

优先经验回放
根据TD误差的绝对值对经验样本设定

采样优先级
均匀采样导致低效学习

Q值过估计（因最大化操作导

Double DQN
解耦动作选择与价值评估：用主网络

选动作，目标网络评估价值

致误差累积）

智能算法及应用@华南理工大学2025

Dueling DQN
网络结构拆分为状态价值 V 和优势函

数A
难以区分状态价值和动作优势

Multi-Step DQN
多步回报（使用 n 步TD误差）
单步TD更新引入短视偏差

Noisy DQN
在网络权重中注入参数化噪声ع－greedy探索效率低下（随机

动作与环境无关）

Distributional DQN
预测Q值的分布而非期望值
传统Q-learning无法表达回报的

随机性

Rainbow
集成以上6种方法
单一改进的局限性与潜在优势

互补

<!-- page: 18 -->

优先经验回放（Prioritized Experience Replay, PER）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-019.png)

<!-- page: 19 -->

优先经验回放（Prioritized Experience Replay, PER）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-020.png)

<!-- page: 20 -->

优先经验回放（Prioritized Experience Replay, PER）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-021.png)

![image](assets/assets/intelligent-algorithms-007/image-022.png)

<!-- page: 21 -->

优先经验回放（Prioritized Experience Replay, PER）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-023.png)

<!-- page: 22 -->

双Q网络（Double DQN）

智能算法及应用@华南理工大学2025

如果所有的Q值都被高估了相同的幅度，那么在决策时也没有影响。
但在实际情况下高估量并不是均匀的（考虑对经验回放数组的采样），
这会增加网络预测的偏差。

![image](assets/assets/intelligent-algorithms-007/image-024.png)

<!-- page: 23 -->

双Q网络（Double DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-025.png)

<!-- page: 24 -->

双Q网络（Double DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-026.png)

<!-- page: 25 -->

对决网络 （Dueling DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-027.png)

<!-- page: 26 -->

对决网络 （Dueling DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-028.png)

<!-- page: 27 -->

对决网络 （Dueling DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-029.png)

![image](assets/assets/intelligent-algorithms-007/image-030.jpeg)

<!-- page: 28 -->

多步DQN（Multi-Step DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-031.png)

![image](assets/assets/intelligent-algorithms-007/image-032.png)

<!-- page: 29 -->

噪声DQN（Noisy DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-033.jpeg)

<!-- page: 30 -->

噪声DQN（Noisy DQN）

对比维度
ε-Greedy
NoisyNet

噪声注入位置
动作空间（直接扰动动作选
择）

参数空间（通过噪声扰动神经网络
权重）

噪声更新频率
每时间步独立决定是否探索
Episode开始时重置噪声，episode
内保持固定

智能算法及应用@华南理工大学2025

探索的连贯性
低（逐时间步独立随机扰动）高（一个episode内噪声固定，形成

方向一致的探索轨迹）

探索与策略的
耦合性
解耦（噪声独立于策略优化）强耦合（噪声是网络参数的一部分，

与策略共同优化）

学习稳定性
低（频繁动作切换导致Q值
震荡）

高（固定噪声下参数更新方向更一
致）

在训练的时候往 DQN 的参数中加入噪声，不仅有利于探索，还能增强鲁棒
性（即使参数被扰动，DQN 也能对Q值做出可靠的估计）。

<!-- page: 31 -->

分布DQN（Distributional DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-034.png)

![image](assets/assets/intelligent-algorithms-007/image-035.png)

<!-- page: 32 -->

分布DQN（Distributional DQN）

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-036.jpeg)

![image](assets/assets/intelligent-algorithms-007/image-037.png)

<!-- page: 33 -->

Rainbow

智能算法及应用@华南理工大学2025

![image](assets/assets/intelligent-algorithms-007/image-038.jpeg)

![image](assets/assets/intelligent-algorithms-007/image-039.png)
