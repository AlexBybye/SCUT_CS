---
source_id: intelligent-algorithms-010
course_id: intelligent_algorithms
title: "13. 基于学习的优化pr"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/13. 基于学习的优化pr.pdf"
document_role: note
year: 
locator_type: page
---

# 13. 基于学习的优化pr

<!-- page: 1 -->

智能算法及应用

13. 基于学习的优化

![image](assets/intelligent-algorithms-010/image-001.jpeg)

![image](assets/intelligent-algorithms-010/image-002.png)

![image](assets/intelligent-algorithms-010/image-003.png)

![image](assets/intelligent-algorithms-010/image-004.png)

![image](assets/intelligent-algorithms-010/image-005.png)

![image](assets/intelligent-algorithms-010/image-006.png)

![image](assets/intelligent-algorithms-010/image-007.png)

![image](assets/intelligent-algorithms-010/image-008.png)

![image](assets/intelligent-algorithms-010/image-009.png)

![image](assets/intelligent-algorithms-010/image-010.png)

![image](assets/intelligent-algorithms-010/image-011.png)

![image](assets/intelligent-algorithms-010/image-012.png)

![image](assets/intelligent-algorithms-010/image-013.png)

![image](assets/intelligent-algorithms-010/image-014.png)

![image](assets/intelligent-algorithms-010/image-015.jpeg)

![image](assets/intelligent-algorithms-010/image-016.png)

![image](assets/intelligent-algorithms-010/image-017.png)

![image](assets/intelligent-algorithms-010/image-018.png)

![image](assets/intelligent-algorithms-010/image-019.png)

![image](assets/intelligent-algorithms-010/image-020.png)

![image](assets/intelligent-algorithms-010/image-021.jpeg)

![image](assets/intelligent-algorithms-010/image-022.png)

![image](assets/intelligent-algorithms-010/image-023.jpeg)

![image](assets/intelligent-algorithms-010/image-024.png)

![image](assets/intelligent-algorithms-010/image-025.png)

![image](assets/intelligent-algorithms-010/image-026.png)

![image](assets/intelligent-algorithms-010/image-027.png)

![image](assets/intelligent-algorithms-010/image-028.png)

![image](assets/intelligent-algorithms-010/image-029.png)

![image](assets/intelligent-algorithms-010/image-030.png)

![image](assets/intelligent-algorithms-010/image-031.png)

![image](assets/intelligent-algorithms-010/image-032.png)

![image](assets/intelligent-algorithms-010/image-033.png)

![image](assets/intelligent-algorithms-010/image-034.png)

![image](assets/intelligent-algorithms-010/image-035.png)

![image](assets/intelligent-algorithms-010/image-036.png)

![image](assets/intelligent-algorithms-010/image-037.png)

![image](assets/intelligent-algorithms-010/image-038.png)

![image](assets/intelligent-algorithms-010/image-039.png)

![image](assets/intelligent-algorithms-010/image-040.png)

![image](assets/intelligent-algorithms-010/image-041.png)

![image](assets/intelligent-algorithms-010/image-042.png)

![image](assets/intelligent-algorithms-010/image-043.png)

![image](assets/intelligent-algorithms-010/image-044.png)

![image](assets/intelligent-algorithms-010/image-045.png)

![image](assets/intelligent-algorithms-010/image-046.png)

![image](assets/intelligent-algorithms-010/image-047.png)

![image](assets/intelligent-algorithms-010/image-048.png)

![image](assets/intelligent-algorithms-010/image-049.jpeg)

![image](assets/intelligent-algorithms-010/image-050.png)

![image](assets/intelligent-algorithms-010/image-051.png)

![image](assets/intelligent-algorithms-010/image-052.png)

![image](assets/intelligent-algorithms-010/image-053.png)

![image](assets/intelligent-algorithms-010/image-054.png)

![image](assets/intelligent-algorithms-010/image-055.png)

![image](assets/intelligent-algorithms-010/image-056.png)

![image](assets/intelligent-algorithms-010/image-057.png)

![image](assets/intelligent-algorithms-010/image-058.png)

![image](assets/intelligent-algorithms-010/image-059.png)

![image](assets/intelligent-algorithms-010/image-060.png)

<!-- page: 2 -->

算法设计
算法运行
优化结果
实际问题
问题建模

1.

2.

![image](assets/intelligent-algorithms-010/image-061.jpeg)

![image](assets/intelligent-algorithms-010/image-062.jpeg)

![image](assets/intelligent-algorithms-010/image-063.jpeg)

![image](assets/intelligent-algorithms-010/image-064.jpeg)

![image](assets/intelligent-algorithms-010/image-065.jpeg)

![image](assets/intelligent-algorithms-010/image-066.jpeg)

![image](assets/intelligent-algorithms-010/image-067.jpeg)

![image](assets/intelligent-algorithms-010/image-068.jpeg)

![image](assets/intelligent-algorithms-010/image-069.png)

<!-- page: 3 -->

没有免费的午餐定理（No Free Lunch Theorem）

我们前面已经学习了非常多的优化
算法和变种……

但No Free Lunch 定理告诉我们，对
于任何优化算法，在所有可能的问
题上进行平均，其性能是一样的。
这意味着没有一个万能的优化算法
（参数）可以在所有问题上都表现
得最好。因此，为了在特定问题上
取得最优的优化效果，我们需要根
据问题的特性设计合适的算法（参
数）。

3

![image](assets/intelligent-algorithms-010/image-070.png)

![image](assets/intelligent-algorithms-010/image-071.png)

<!-- page: 4 -->

设计算法的方法

1.
Rule-based Approaches

经验法则方法基于领域专家的经验和知识，设计优化算法的规则。例如，对于某
些类型的问题，经验告诉我们某些算法设计策略通常表现较好。

简单直接；易于理解和实现
依赖于专家的经验，可能存在主观性；难以适应复杂和多变的问题

2.
Meta-learning

元学习利用机器学习方法，根据以往问题和算法的表现，设计新的优化算法。这
个过程包括特征提取、数据获取、模型训练和预测等步骤。

能够自动化设计算法，适应性强；不依赖于专家的经验
需要大量的历史数据和计算资源；模型的准确性和可靠性取决于数据质量
和模型的选择

4

![image](assets/intelligent-algorithms-010/image-072.png)

<!-- page: 5 -->

基于学习的优化（Learning to optimize, L2O）

Neural Combinatorial Optimization
利用神经网络/
深度学习直接产生组合优化问题的候选解，在近年来得到了广泛关注，
并取得了长足进步。

5

![image](assets/intelligent-algorithms-010/image-073.jpeg)

![image](assets/intelligent-algorithms-010/image-074.jpeg)

<!-- page: 6 -->

基于学习的优化（Learning to optimize, L2O）

但当我们面对的是连续空间的优化问题、尤其是复杂的黑箱优化问题时：

•
泛化性能（任务、
维度）有局限性
•
优化步长受限

Y. Chen et al. Learning to Learn without Gradient Descent by Gradient Descent, ICML 2017.

6

![image](assets/intelligent-algorithms-010/image-075.jpeg)

![image](assets/intelligent-algorithms-010/image-076.jpeg)

<!-- page: 7 -->

基于学习的优化（Learning to optimize, L2O）

OPRO: Optimization by Prompting

C. Yang, X. Wang, Y. Lu, H. Liu, Q. V. Le, D. Zhou, and X. Chen,
Large language models as optimizers, arXiv preprint arXiv:2309.03409, 2023.

7

![image](assets/intelligent-algorithms-010/image-077.jpeg)

![image](assets/intelligent-algorithms-010/image-078.png)

<!-- page: 8 -->

基于学习的优化（Learning to optimize, L2O）

LMEA: LLM-Driven Evolutionary Algorithm

S. Liu, C. Chen, X. Qu, K. Tang, and Y.-S. Ong, Large language models as evolutionary
optimizers, arXiv preprint arXiv:2310.19046, 2023.

8

![image](assets/intelligent-algorithms-010/image-079.jpeg)

![image](assets/intelligent-algorithms-010/image-080.jpeg)

<!-- page: 9 -->

元黑箱优化（Meta-Black-Box Optimization, MetaBBO）

Mathematically:

/generation

ܦ: optimization task distribution
ߨఏ: meta level control policyܴ

௧: performance gain at lower level

9

![image](assets/intelligent-algorithms-010/image-081.jpeg)

![image](assets/intelligent-algorithms-010/image-082.jpeg)

<!-- page: 10 -->

元黑箱优化（Meta-Black-Box Optimization, MetaBBO）

从学习方式上来划分：

•
强化学习（Reinforcement Learning）

•
神经进化（Neuroevolution）

/generation

•
监督学习（Supervised Learning）

•
上下文学习（In-Context Learning）

10

![image](assets/intelligent-algorithms-010/image-083.jpeg)

![image](assets/intelligent-algorithms-010/image-084.jpeg)

<!-- page: 11 -->

元黑箱优化（Meta-Black-Box Optimization, MetaBBO）

从功能角度来划分：

•
算法选择（Algorithm Selection）

•
算法配置（Algorithm Configuration）

/generation

•
算法组装(Algorithm Composition)

•
算法生成(Algorithm Generation)

11

![image](assets/intelligent-algorithms-010/image-085.jpeg)

![image](assets/intelligent-algorithms-010/image-086.jpeg)

<!-- page: 12 -->

算法选择（Algorithm Selection）

RL-DAS: Reinforcement Learning based Dynamic Algorithm Selection

H. Guo (学生), Y. Ma, Z. Ma, J. Chen, X. Zhang, Z. Cao, J. Zhang, and Y.-J. Gong . Deep Reinforcement Learning for
Dynamic Algorithm Selection: A Proof-of-Principle Study on Differential Evolution, IEEE TSMC-Systems, 2024.

12

![image](assets/intelligent-algorithms-010/image-087.jpeg)

![image](assets/intelligent-algorithms-010/image-088.jpeg)

<!-- page: 13 -->

算法选择（Algorithm Selection）

13

![image](assets/intelligent-algorithms-010/image-089.png)

![image](assets/intelligent-algorithms-010/image-090.png)

<!-- page: 14 -->

算法配置（Algorithm Configuration）

GLEET: Generalizable Learning-based Exploration-Exploitation Tradeoff

State：Optimization status

Test data

Train
data

Environment

BBO problem

Reward
Problem

DRL agent

Optimize

PBO pardigm

Action：EET configuration

基于问题集合进行训练

联合控制种群中个体
（网络每步输出NxM个参数）

Z. Ma (学生), J. Chen, H. Guo, Y. Ma, Y.-J. Gong, “Auto-configuring Exploration-Exploitation Tradeoff in
Evolutionary Computation via Deep Reinforcement Learning,” GECCO 2024.

14

![image](assets/intelligent-algorithms-010/image-091.jpeg)

<!-- page: 15 -->

算法配置（Algorithm Configuration）

15

![image](assets/intelligent-algorithms-010/image-092.jpeg)

![image](assets/intelligent-algorithms-010/image-093.jpeg)

![image](assets/intelligent-algorithms-010/image-094.jpeg)

<!-- page: 16 -->

算法组装(Algorithm Composition)

ALDe: Autoregressive Learning-based Designer

Q. Zhao, T. Liu, B. Yan, Q. Duan, J. Yang, Y. Shi. Automated Metaheuristic Algorithm Design with Autoregressive
Learning. arXiv preprint arXiv:2405.03419, 2024.

16

![image](assets/intelligent-algorithms-010/image-095.png)

![image](assets/intelligent-algorithms-010/image-096.jpeg)

![image](assets/intelligent-algorithms-010/image-097.jpeg)

<!-- page: 17 -->

算法组装(Algorithm Composition)

17

![image](assets/intelligent-algorithms-010/image-098.png)

![image](assets/intelligent-algorithms-010/image-099.png)

![image](assets/intelligent-algorithms-010/image-100.png)

<!-- page: 18 -->

算法生成(Algorithm Generation)

SYMBOL: Generating Symbolic Equations for Black-Box Optimizer Learning

Traditional BBO optimizer

General workflow

of BBO optimizer

Human-

ݔ௧ݔ௧ାଵ

crafted

rules

ݔ௧

动态
算法迭代公式：
•
不依赖专家先验
•
更好的灵活性和自适应性
•
更好的可解释性
•
更好的可扩展性

MetaBBO for Auto-Configuration

Human-

Config

Neural
Network

Update

ݔ௧ݔ௧ାଵ

crafted

rule

rules

MetaBBO for Candidate Solution Proposal

ݔ௧ାଵ

Neural
Network

ݔ௧ݔ௧ାଵ

No

Terminate?

SYMBOL

Yes

symbolic update rule

Neural
Network
x* - 0.18 xr

ݔ௧ݔ௧ାଵ

J. Chen (学生), Z. Ma, H. Guo, Y. Ma, J. Zhang,
and Y.-J. Gong, SYMBOL: Generating Flexible
Black-Box Optimizers through Symbolic
Equation Learning, ICLR 2024.

ݔ∗

⨁

18

![image](assets/intelligent-algorithms-010/image-101.jpeg)

<!-- page: 19 -->

算法生成(Algorithm Generation)

19

![image](assets/intelligent-algorithms-010/image-102.png)

![image](assets/intelligent-algorithms-010/image-103.png)

![image](assets/intelligent-algorithms-010/image-104.png)

![image](assets/intelligent-algorithms-010/image-105.png)

![image](assets/intelligent-algorithms-010/image-106.jpeg)

![image](assets/intelligent-algorithms-010/image-107.png)

![image](assets/intelligent-algorithms-010/image-108.png)

![image](assets/intelligent-algorithms-010/image-109.png)

![image](assets/intelligent-algorithms-010/image-110.png)

![image](assets/intelligent-algorithms-010/image-111.png)

![image](assets/intelligent-algorithms-010/image-112.png)

![image](assets/intelligent-algorithms-010/image-113.jpeg)

![image](assets/intelligent-algorithms-010/image-114.png)

![image](assets/intelligent-algorithms-010/image-115.png)

![image](assets/intelligent-algorithms-010/image-116.png)

<!-- page: 20 -->

算法生成(Algorithm Generation)

Fitness Landscape Analysis

20

![image](assets/intelligent-algorithms-010/image-117.png)

![image](assets/intelligent-algorithms-010/image-118.png)

![image](assets/intelligent-algorithms-010/image-119.png)

<!-- page: 21 -->

算法生成(Algorithm Generation)

Vectorized Tree Embedding
Symbol Set

operators:

＋
－
×

∗
c
∆ݔ
ݔ௥

ݔ
ݔ∗ݔ௜

operands:ݔି

The symbols are sufficient for deriving
many well-known optimizers such as

DE:

PSO:

21

![image](assets/intelligent-algorithms-010/image-120.png)

![image](assets/intelligent-algorithms-010/image-121.jpeg)

![image](assets/intelligent-algorithms-010/image-122.jpeg)

<!-- page: 22 -->

算法生成(Algorithm Generation)

Masks for streamlined generation

Constance Inference

c

＋

Infer the concrete

5
2

constant value

on-the-fly

＋

LSTM

x
-

FF
layer

FF
layer

VTE

x

...

0.8
0ܿ
=
10
´

Set the violated tokens
with a sample probability of 0.

mantissaexponent

22

![image](assets/intelligent-algorithms-010/image-123.jpeg)

<!-- page: 23 -->

算法生成(Algorithm Generation)

23

![image](assets/intelligent-algorithms-010/image-124.png)

![image](assets/intelligent-algorithms-010/image-125.png)

![image](assets/intelligent-algorithms-010/image-126.png)

![image](assets/intelligent-algorithms-010/image-127.png)

![image](assets/intelligent-algorithms-010/image-128.jpeg)

![image](assets/intelligent-algorithms-010/image-129.png)

![image](assets/intelligent-algorithms-010/image-130.png)

![image](assets/intelligent-algorithms-010/image-131.png)

![image](assets/intelligent-algorithms-010/image-132.png)

![image](assets/intelligent-algorithms-010/image-133.png)

![image](assets/intelligent-algorithms-010/image-134.png)

![image](assets/intelligent-algorithms-010/image-135.png)

![image](assets/intelligent-algorithms-010/image-136.png)

![image](assets/intelligent-algorithms-010/image-137.jpeg)

<!-- page: 24 -->

算法生成(Algorithm Generation)

24

![image](assets/intelligent-algorithms-010/image-138.png)

![image](assets/intelligent-algorithms-010/image-139.png)

<!-- page: 25 -->

算法生成(Algorithm Generation)

25

![image](assets/intelligent-algorithms-010/image-140.png)

![image](assets/intelligent-algorithms-010/image-141.png)

![image](assets/intelligent-algorithms-010/image-142.png)

![image](assets/intelligent-algorithms-010/image-143.jpeg)

![image](assets/intelligent-algorithms-010/image-144.png)

![image](assets/intelligent-algorithms-010/image-145.png)

<!-- page: 26 -->

算法生成(Algorithm Generation)

26

![image](assets/intelligent-algorithms-010/image-146.jpeg)

![image](assets/intelligent-algorithms-010/image-147.jpeg)

<!-- page: 27 -->

如何给问题和优化状态自动提取特征？

NeurELA: Neural Exploratory Landscape Analysis

RL Agent (meta level)

state
(optimization state)

action
(algorithm settings)
reward
(feedback signal)

optimization

loop

BBO
Algorithm
BBO
Problem

Environment (lower level)

Z. Ma (学生), J. Chen, H. Guo, Y.-J. Gong, "Neural Exploratory Landscape Analysis for Meta-Black-
Box-Optimization," ICLR 2025.

![image](assets/intelligent-algorithms-010/image-148.jpeg)

<!-- page: 28 -->

如何给问题和优化状态自动提取特征？

NeurELA: Neural Exploratory Landscape Analysis

We adopt Fast-CMA-ES to evolve a population of NeurELA networks.

![image](assets/intelligent-algorithms-010/image-149.jpeg)

![image](assets/intelligent-algorithms-010/image-150.jpeg)

![image](assets/intelligent-algorithms-010/image-151.jpeg)

<!-- page: 29 -->

如何给问题和优化状态自动提取特征？

NeurELA: Neural Exploratory Landscape Analysis

![image](assets/intelligent-algorithms-010/image-152.jpeg)

![image](assets/intelligent-algorithms-010/image-153.png)

![image](assets/intelligent-algorithms-010/image-154.png)

![image](assets/intelligent-algorithms-010/image-155.png)

![image](assets/intelligent-algorithms-010/image-156.png)

![image](assets/intelligent-algorithms-010/image-157.png)

![image](assets/intelligent-algorithms-010/image-158.png)

![image](assets/intelligent-algorithms-010/image-159.png)

![image](assets/intelligent-algorithms-010/image-160.png)

![image](assets/intelligent-algorithms-010/image-161.png)

![image](assets/intelligent-algorithms-010/image-162.png)

![image](assets/intelligent-algorithms-010/image-163.png)

![image](assets/intelligent-algorithms-010/image-164.png)

![image](assets/intelligent-algorithms-010/image-165.png)

![image](assets/intelligent-algorithms-010/image-166.png)

![image](assets/intelligent-algorithms-010/image-167.png)

<!-- page: 30 -->

如何给问题和优化状态自动提取特征？

NeurELA: Neural Exploratory Landscape Analysis

![image](assets/intelligent-algorithms-010/image-168.jpeg)

![image](assets/intelligent-algorithms-010/image-169.jpeg)

![image](assets/intelligent-algorithms-010/image-170.jpeg)

![image](assets/intelligent-algorithms-010/image-171.jpeg)

<!-- page: 31 -->

如何用好大模型？

LLaMoCo: Large Language Models for optimization Code generation

•
LLaMoCo-S: CodeGen-Mono(350M)
•
LLaMoCo-M: Phi-2(2.7B)
•
LLaMoCo-L: CodeLlama(7B)

Z. Ma (学生), H. Guo, Ji. Chen, G. Peng, Z. Cao, Y.
Ma, Y.-J. Gong, LLaMoCo: Instruction Tuning of
Large Language Models for Optimization Code
Generation, arXiv preprint arXiv:2403.01131, 2024.

31

![image](assets/intelligent-algorithms-010/image-172.jpeg)

![image](assets/intelligent-algorithms-010/image-173.jpeg)

![image](assets/intelligent-algorithms-010/image-174.jpeg)

<!-- page: 32 -->

如何用好大模型？

32

![image](assets/intelligent-algorithms-010/image-175.jpeg)

![image](assets/intelligent-algorithms-010/image-176.jpeg)

<!-- page: 33 -->

如何用好大模型？

33

![image](assets/intelligent-algorithms-010/image-177.png)

![image](assets/intelligent-algorithms-010/image-178.png)

<!-- page: 34 -->

MetaBox平台

Z. Ma (学生), H. Guo, J. Chen, Z. Li, G. Peng, Y.-J. Gong, Y. Ma, and Z. Cao, MetaBox: A Benchmark Platform for Meta-Black-Box
Optimization with Reinforcement Learning,  NeurIPS 2023.

34

![image](assets/intelligent-algorithms-010/image-179.jpeg)

![image](assets/intelligent-algorithms-010/image-180.jpeg)

![image](assets/intelligent-algorithms-010/image-181.jpeg)

<!-- page: 35 -->

MetaBox平台

•
1.0版本Github地址：https://github.com/GMC-DRL/MetaBox
（请帮助点亮小星星）

•
QQ交流群：952185139

35

![image](assets/intelligent-algorithms-010/image-182.jpeg)

![image](assets/intelligent-algorithms-010/image-183.jpeg)

![image](assets/intelligent-algorithms-010/image-184.jpeg)

![image](assets/intelligent-algorithms-010/image-185.jpeg)

<!-- page: 36 -->

相关综述

Z. Ma (学生), H. Guo, Y.-J. Gong, J. Zhang, K. C. Tan, "Toward Automated Algorithm Design: A Survey and Practical Guide to
Meta-Black-Box-Optimization," https://arxiv.org/abs/2411.00625

36

![image](assets/intelligent-algorithms-010/image-186.jpeg)

![image](assets/intelligent-algorithms-010/image-187.jpeg)

<!-- page: 37 -->

论文阅读作业

单人作业，提交.zip压缩包，包含
1. 论文阅读笔记（Markdown格式，图文并茂，2500字以内），包含摘要、
研究背景与研究动机、方法、实验结果
2. 论文阅读笔记（PDF格式）
3. 相关源文件如图片的文件夹

选题来源：
https://github.com/GMC-DRL/Awesome-MetaBBO
https://github.com/LabGong/psc4ddea
（请顺手点亮小星星）

截止时间：2025-05-09 20:00
提交地址：https://send2me.cn/ZU1OPzvl/QoqtIeo5uUAITQ

37

![image](assets/intelligent-algorithms-010/image-188.png)
