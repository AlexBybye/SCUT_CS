---
source_id: intelligent-algorithms-025
course_id: intelligent_algorithms
title: "模拟退火SA"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/模拟退火SA.md"
document_role: note
year: 
locator_type: heading
---

# 模拟退火SA

# SA算法的基本理念：
![[1. 模拟退火pr(1).pdf#page=7&rect=117,54,782,376|1. 模拟退火pr(1), p.7]]
![[1. 模拟退火pr(1).pdf#page=8&rect=86,23,796,485|1. 模拟退火pr(1), p.8]]
# SA算法适合应用场景
## 在解空间复杂、存在多个局部最优解的情况下表现出色
### **优点**
#### -**全局搜索能力**：能够跳出局部最优，具有较强的全局优化能力。
##### - **对初始解不敏感**：初始解的选择对最终结果影响较小。
##### - **适用于复杂问题**：对于一些传统优化方法难以解决的复杂问题，SA算法往往能取得较好的效果。
##### **缺点**
##### - **计算效率较低**：在高温阶段需要进行大量的迭代和计算。
##### - **参数选择敏感**：算法的性能对参数（如初始温度、降温系数等）的选择较为敏感。

``` python
import random
import math

# 问题参数
c = 15  # 背包容量
w = [7, 3, 12, 5, 14]  # 物品重量
v = [10, 4, 15, 6, 9]  # 物品价值
n = len(w)  # 物品数量

# SA算法参数
T0 = 1000  # 初始温度
Tk = 1e-5  # 结束温度
L = 100  # 每个温度下的迭代次数
alpha = 0.95  # 降温系数

# 初始化解
def initial_solution():
    x = [0] * n
    while True:
        for i in range(n):
            x[i] = random.randint(0, 1)
        if is_feasible(x):
            return x

# 判断解是否合法
def is_feasible(x):
    total_weight = sum(w[i] * x[i] for i in range(n))
    return total_weight <= c

# 计算目标函数值
def calculate_value(x):
    return sum(v[i] * x[i] for i in range(n))

# 生成邻近解
def generate_neighbor(x):
    neighbor = x.copy()
    # 随机选择两个不同的物品，交换它们的选取状态
    i, j = random.sample(range(n), 2)
    neighbor[i] = 1 - neighbor[i]
    neighbor[j] = 1 - neighbor[j]
    # 如果邻近解不合法，尝试修复
    if not is_feasible(neighbor):
        # 找到重量超过的部分，尝试移除一些物品
        while not is_feasible(neighbor):
            # 随机选择一个选中的物品并移除
            selected = [k for k in range(n) if neighbor[k] == 1]
            if not selected:
                break
            remove = random.choice(selected)
            neighbor[remove] = 0
    return neighbor

# SA算法主循环
def simulated_annealing():
    x_current = initial_solution()
    x_best = x_current.copy()
    value_best = calculate_value(x_best)
    T = T0
    k = 0
    while T > Tk:
        for _ in range(L):
            x_neighbor = generate_neighbor(x_current)
            value_current = calculate_value(x_current)
            value_neighbor = calculate_value(x_neighbor)
            if value_neighbor >= value_current:
                x_current = x_neighbor
                if calculate_value(x_current) > value_best:
                    x_best = x_current.copy()
                    value_best = calculate_value(x_best)
            else:
                # 根据Metropolis准则接受较差解
                delta = value_neighbor - value_current
                if random.random() < math.exp(delta / T):
                    x_current = x_neighbor
        # 降温
        T *= alpha
        k += 1
    return x_best, value_best

# 执行算法
best_solution, best_value = simulated_annealing()

# 输出结果
print("最优解为：", best_solution)
print("最大价值为：", best_value)
```
# 问题：初始参数的选择
## 1. 初始温度（T0）

- **作用**：初始温度决定了算法在开始时接受较差解的概率。温度越高，接受较差解的概率越大，算法的全局搜索能力越强。
    
- **选择方法**：
    
    - **经验公式**：可以根据问题的规模和特点，通过经验公式估算初始温度。例如，对于0-1背包问题，可以取初始温度为 T0=0.1×n1​，其中 n 是物品的数量。
        
    - **试验法**：通过多次试验，观察算法的收敛情况和解的质量，调整初始温度。如果初始温度过低，算法可能过早收敛到局部最优解；如果初始温度过高，算法可能需要更多的迭代次数才能收敛。
        
    - **自适应调整**：在算法运行过程中，根据当前解的质量和接受概率动态调整初始温度。
        

## 2. 降温系数（alpha）

- **作用**：降温系数决定了温度下降的速度。较大的降温系数会使温度下降较慢，算法的搜索过程较为充分；较小的降温系数会使温度下降较快，算法的搜索过程较为迅速。
    
- **选择方法**：
    
    - **常见取值**：通常取值在0.8到0.99之间。例如，0.9、0.95、0.98等。
        
    - **问题规模**：对于规模较大的问题，可以选择较大的降温系数，以保证充分的搜索；对于规模较小的问题，可以选择较小的降温系数，以加快收敛速度。
        
    - **试验法**：通过多次试验，观察算法的收敛速度和解的质量，调整降温系数。
        

## 3. 每个温度下的迭代次数（L）

- **作用**：每个温度下的迭代次数决定了在该温度下进行的局部搜索次数。迭代次数越多，搜索越充分，但计算时间也越长。
    
- **选择方法**：
    
    - **固定次数**：可以根据问题的规模和复杂度，设定一个固定的迭代次数。例如，对于较小规模的问题，可以设定为100次；对于较大规模的问题，可以设定为1000次。
        
    - **动态调整**：根据当前温度和解的质量动态调整迭代次数。例如，在高温阶段可以增加迭代次数，以充分探索解空间；在低温阶段可以减少迭代次数，以加快收敛速度。
        
    - **试验法**：通过多次试验，观察算法的收敛情况，调整迭代次数。
        

## 4. 结束温度（Tk）

- **作用**：结束温度决定了算法停止的条件。当温度降到结束温度时，算法终止。
    
- **选择方法**：
    
    - **常见取值**：通常取一个非常小的值，例如 1e−5 或 1e−6。
        
    - **问题要求**：根据问题的精度要求选择结束温度。如果对解的精度要求较高，可以设定较小的结束温度；如果对解的精度要求较低，可以设定较大的结束温度。
        
    - **试验法**：通过多次试验，观察算法的收敛情况和解的质量，调整结束温度。
