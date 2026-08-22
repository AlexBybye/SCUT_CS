---
source_id: intelligent-algorithms-027
course_id: intelligent_algorithms
title: "蚁群优化ACO"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/蚁群优化ACO.md"
document_role: note
year: 
locator_type: heading
---

# 蚁群优化ACO

# 1：对离散和连续的理解：![[5. 蚁群优化pr(1).pdf#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiipage=2&rect=63,74,790,426|5. 蚁群优化pr(1), p.2]]
# ACO算法的基本理念：
![[5. 蚁群优化pr(1).pdf#page=14&rect=76,20,791,565|5. 蚁群优化pr(1), p.14]]
# ACO算法适合应用场景
## 广泛应用于解决组合优化问题
### ACO应用：TSP、车辆路径、任务分配
#### 优点：
#### 可找全局最优解
#### 可以适用于各种组合优化问题
#### 缺点：
#### 收敛速度慢
### EACO（加强型蚁群算法）：
#### 优点：
#### 收敛快于经典ACO
#### 可以保持最优解
#### 缺点：
#### 可能局部最优
#### 添加的精英策略参数极其重要
### ACOrank（蚁群排序算法）：
#### 优点：
#### 解的质量更高
#### 缺点：
#### 计算复杂度高
### MMACO（最大最小蚁群算法）：
#### 优点：
#### 收敛速度较快且解的质量较高。
#### 缺点：
#### 需要合理设置信息素的上下限。
#### 对参数的敏感性较高。
### ACS（自适应蚁群算法）：
#### 优点：
#### 具有较好的探索和开发平衡。
#### 收敛速度较快。
#### 缺点：
#### 参数选择较为复杂。
#### 在大规模问题上计算量较大。
### 具体优化：
![[5. 蚁群优化pr(1).pdf#page=37&rect=44,33,799,548|5. 蚁群优化pr(1), p.37]]
### 相关优化参数设置：
![[5. 蚁群优化pr(1).pdf#page=38&rect=49,42,794,483|5. 蚁群优化pr(1), p.38]]
``` python
import numpy as np
import math

# CVRP问题参数
num_customers = 10  # 客户数量
capacity = 100  # 车辆容量
demands = np.random.randint(1, 20, num_customers)  # 各客户的需求
distance_matrix = np.random.rand(num_customers + 1, num_customers + 1)  # 距离矩阵，包括仓库（索引0）

# MMACO算法参数
num_ants = 30  # 蚂蚁数量
max_iterations = 100  # 最大迭代次数
alpha = 1.0  # 信息素重要性参数
beta = 2.0  # 启发式信息重要性参数
evaporation_rate = 0.1  # 信息素蒸发率
Q = 100.0  # 信息素增加量
tau_min = 1e-6  # 信息素最小值
tau_max = 1.0  # 信息素最大值

# 初始化信息素矩阵
num_nodes = num_customers + 1  # 包括仓库
tau = np.ones((num_nodes, num_nodes)) * tau_min

# 计算启发式信息（距离的倒数）
eta = 1.0 / (distance_matrix + 1e-6)  # 避免除以零

# MMACO算法主循环
best_solution = None
best_cost = float('inf')

for iteration in range(max_iterations):
    # 每只蚂蚁构建一个路径
    ant_paths = []
    for ant in range(num_ants):
        path = [0]  # 从仓库出发
        remaining_capacity = capacity
        current_node = 0
        
        while len(path) < num_customers + 1:
            # 选择下一个客户
            feasible_customers = [i for i in range(1, num_customers + 1) if i not in path and demands[i - 1] <= remaining_capacity]
            if not feasible_customers:
                break  # 返回仓库
            probabilities = []
            for customer in feasible_customers:
                probabilities.append((tau[current_node][customer] ** alpha) * (eta[current_node][customer] ** beta))
            probabilities = np.array(probabilities)
            probabilities /= probabilities.sum()
            
            next_node = np.random.choice(feasible_customers, p=probabilities)
            path.append(next_node)
            remaining_capacity -= demands[next_node - 1]
            current_node = next_node
        
        # 计算路径成本
        cost = 0.0
        for i in range(len(path) - 1):
            cost += distance_matrix[path[i]][path[i + 1]]
        cost += distance_matrix[path[-1]][0]  # 返回仓库
        
        ant_paths.append((path, cost))
    
    # 更新信息素
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                tau[i][j] *= (1 - evaporation_rate)
                if tau[i][j] < tau_min:
                    tau[i][j] = tau_min
                elif tau[i][j] > tau_max:
                    tau[i][j] = tau_max
    
    # 找到最优路径并更新信息素
    iteration_best_path = None
    iteration_best_cost = float('inf')
    for path, cost in ant_paths:
        if cost < iteration_best_cost:
            iteration_best_path = path
            iteration_best_cost = cost
    
    if iteration_best_cost < best_cost:
        best_solution = iteration_best_path
        best_cost = iteration_best_cost
    
    # 在最优路径上增加信息素
    for i in range(len(iteration_best_path) - 1):
        a = iteration_best_path[i]
        b = iteration_best_path[i + 1]
        tau[a][b] += Q / iteration_best_cost
        if tau[a][b] > tau_max:
            tau[a][b] = tau_max

# 输出结果
print("最佳路径：", best_solution)
print("最小总行驶距离：", best_cost)
```
# 问题：初始参数的选择
## 1. 蚂蚁数量（num_ants）
- **作用**：蚂蚁数量决定了每一代中搜索路径的数量。较多的蚂蚁可以增加解的多样性，但会增加计算量。
- **常见取值范围**：20到100之间。
### 2. 最大迭代次数（max_iterations）

- **作用**：最大迭代次数决定了算法运行的代数。较多的迭代次数可以提高算法的搜索能力，但会增加计算时间。
- **常见取值范围**：100到1000之间。
### 3. 信息素重要性参数（alpha）
- **作用**：alpha决定了信息素在路径选择中的重要性。较大的alpha值会使蚂蚁更倾向于选择信息素浓度高的路径。
- **选择方法**：
    - **常见取值范围**：0.5到2.0之间。
    - **问题特点**：对于需要较强全局搜索能力的问题，可以选择较小的alpha值；对于需要较快收敛的问题，可以选择较大的alpha值。    
### 4. 启发式信息重要性参数（beta）
- **作用**：beta决定了启发式信息在路径选择中的重要性。较大的beta值会使蚂蚁更倾向于选择启发式信息高的路径。
- **选择方法**：
    - **常见取值范围**：1.0到5.0之间。
    - **问题特点**：对于需要较强局部搜索能力的问题，可以选择较大的beta值；对于需要较强全局搜索能力的问题，可以选择较小的beta值。
### 5. 信息素蒸发率（evaporation_rate）
- **作用**：信息素蒸发率决定了信息素的挥发速度。较高的蒸发率可以增加算法的探索能力，防止过早收敛。
- **选择方法**：
    - **常见取值范围**：0.1到0.5之间。
    - **问题特点**：对于需要较强探索能力的问题，可以选择较高的蒸发率；对于需要较快收敛的问题，可以选择较低的蒸发率。
### 6. 信息素增加量（Q）
- **作用**：Q决定了每只蚂蚁在路径上增加的信息素量。较大的Q值可以加快信息素的积累。
- **选择方法**：
    - **常见取值范围**：10到100之间。
    - **问题特点**：对于需要较快收敛的问题，可以选择较大的Q值；对于需要较强探索能力的问题，可以选择较小的Q值。
### 7. 信息素最小值（tau_min）和最大值（tau_max）
- **作用**：tau_min和tau_max限制了信息素浓度的范围，防止信息素过度集中或分散。
- **选择方法**：
    - **常见取值范围**：tau_min通常在1e-6到1e-4之间，tau_max通常在1.0到10.0之间。
    - **问题特点**：对于需要较强探索能力的问题，可以选择较大的tau_min和较小的tau_max；对于需要较快收敛的问题，可以选择较小的tau_min和较大的tau_max。
