---
source_id: intelligent-algorithms-008
course_id: intelligent_algorithms
title: "11. 策略学习方法pr"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/11. 策略学习方法pr.pdf"
document_role: note
year: 
locator_type: page
---

# 11. 策略学习方法pr

<!-- page: 1 -->

智能算法及应用

11. 策略学习方法
智能算法及应用@华南理工大学2025

<!-- page: 2 -->

策略学习

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-001.png)

![image](assets/intelligent-algorithms-008/image-002.png)

<!-- page: 3 -->

策略学习

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-003.png)

![image](assets/intelligent-algorithms-008/image-004.png)

<!-- page: 4 -->

策略梯度的推导

智能算法及应用@华南理工大学2025

直接代入存在两个问题：

1. 乘积的导数计算十分复杂！

2. 在Model-Free方法中状态转移函数不可知！

![image](assets/intelligent-algorithms-008/image-005.png)

<!-- page: 5 -->

策略梯度的推导

1.
智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-006.png)

![image](assets/intelligent-algorithms-008/image-007.png)

![image](assets/intelligent-algorithms-008/image-008.png)

<!-- page: 6 -->

策略梯度的推导

1.

智能算法及应用@华南理工大学2025

2.

![image](assets/intelligent-algorithms-008/image-009.png)

![image](assets/intelligent-algorithms-008/image-010.png)

![image](assets/intelligent-algorithms-008/image-011.png)

<!-- page: 7 -->

策略梯度的推导

智能算法及应用@华南理工大学2025

代入2.

![image](assets/intelligent-algorithms-008/image-012.png)

<!-- page: 8 -->

策略梯度的推导

3.

智能算法及应用@华南理工大学2025

4.

![image](assets/intelligent-algorithms-008/image-013.png)

![image](assets/intelligent-algorithms-008/image-014.png)

<!-- page: 9 -->

策略梯度的推导

智能算法及应用@华南理工大学2025

<!-- page: 10 -->

REINFORCE算法

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-015.jpeg)

<!-- page: 11 -->

改进一：修正回报

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-016.png)

![image](assets/intelligent-algorithms-008/image-017.png)

<!-- page: 12 -->

改进一：修正回报

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-018.png)

![image](assets/intelligent-algorithms-008/image-019.png)

![image](assets/intelligent-algorithms-008/image-020.png)

<!-- page: 13 -->

改进二：引入基线

智能算法及应用@华南理工大学2025

最简单的解决方式叫做“Baseline”。其基本
想法是采样到的累积奖励减去一个基线值，
作为“Advantage”

![image](assets/intelligent-algorithms-008/image-021.png)

![image](assets/intelligent-algorithms-008/image-022.png)

<!-- page: 14 -->

改进二：引入基线

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-023.png)

![image](assets/intelligent-algorithms-008/image-024.png)

<!-- page: 15 -->

改进二：引入基线

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-025.png)

![image](assets/intelligent-algorithms-008/image-026.png)

<!-- page: 16 -->

Actor-Critic

引入值函数Q

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-027.png)

![image](assets/intelligent-algorithms-008/image-028.png)

![image](assets/intelligent-algorithms-008/image-029.png)

<!-- page: 17 -->

Actor-Critic

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-030.png)

![image](assets/intelligent-algorithms-008/image-031.png)

<!-- page: 18 -->

Actor-Critic

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-032.jpeg)

<!-- page: 19 -->

Actor-Critic

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-033.png)

<!-- page: 20 -->

同步优势 Actor-Critic（Synchronous Advantage Actor-Critic, A2C）

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-034.png)

<!-- page: 21 -->

同步优势 Actor-Critic（Synchronous Advantage Actor-Critic, A2C）

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-035.png)

<!-- page: 22 -->

同步优势 Actor-Critic（Synchronous Advantage Actor-Critic, A2C）

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-036.png)

![image](assets/intelligent-algorithms-008/image-037.png)

<!-- page: 23 -->

异步优势 Actor-Critic（Asynchronous Advantage Actor-Critic, A3C）

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-038.png)

![image](assets/intelligent-algorithms-008/image-039.png)

![image](assets/intelligent-algorithms-008/image-040.png)

<!-- page: 24 -->

异步优势 Actor-Critic（Asynchronous Advantage Actor-Critic, A3C）

智能算法及应用@华南理工大学2025

![image](assets/intelligent-algorithms-008/image-041.png)

![image](assets/intelligent-algorithms-008/image-042.png)
