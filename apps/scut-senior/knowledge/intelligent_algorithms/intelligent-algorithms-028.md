---
source_id: intelligent-algorithms-028
course_id: intelligent_algorithms
title: "进化策略ES"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/进化策略ES.md"
document_role: note
year: 
locator_type: heading
---

# 进化策略ES

## ES基本理念：![[6. 进化策略pr(1).pdf#page=7&rect=58,32,813,538|6. 进化策略pr(1), p.7]]

## CMA-ES（协方差矩阵自适应演化）
![[6. 进化策略pr(1).pdf#page=32&rect=63,33,784,532|6. 进化策略pr(1), p.32]]
# 我们学这两个东西用处是什么？
这其实是一种普适性的进化优化，故而叫做策略，后续我们在神经网络甚至是大模型中都可以用到这个策略用来优化参数![[6. 进化策略pr(1).pdf#page=35&rect=429,261,793,454|6. 进化策略pr(1), p.35]]
当然，神经进化NES替代方案有SGD（梯度下降），ES优于SGD于
1：非连续非微分函数；
2：复杂神经网络；
3：并行化（计算资源充足时）
4：多模态的优化！
5：需要鲁棒性和泛化能力；
下面是代码示例
## 使用遗传算法来优化一个简单的神经网络，解决XOR问题
``` python
import numpy as np

# 初始化神经网络参数
input_size = 2
hidden_size = 4
output_size = 1

np.random.seed(0)
weights_ih = np.random.rand(hidden_size, input_size)
weights_ho = np.random.rand(output_size, hidden_size)

# 定义适应度函数
def fitness(y_true, y_pred):
    return 1 / (1 + np.sum((y_true - y_pred) ** 2))

# 定义评估函数
def evaluate(individual):
    y_pred = sigmoid(np.dot(weights_ih, individual[:hidden_size]) + np.dot(weights_ho, individual[hidden_size:]))
    return fitness(y_true, y_pred)

# 定义交叉操作
def crossover(parent1, parent2):
    crossover_point = np.random.randint(0, hidden_size)
    child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
    child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
    return child1, child2

# 定义变异操作
def mutation(individual, mutation_rate):
    for i in range(len(individual)):
        if np.random.rand() < mutation_rate:
            individual[i] += np.random.randn()
    return individual

# 初始化个体群体
population_size = 10
population = np.random.rand(population_size, hidden_size)

# 训练神经进化算法
generations = 100
for generation in range(generations):
    # 评估个体群体的适应度
    fitness_values = np.array([evaluate(individual) for individual in population])

    # 选择、交叉和变异操作
    sorted_indices = np.argsort(fitness_values)[::-1]
    parents = population[sorted_indices[:2]]
    children = []
    for i in range(0, population_size, 2):
        child1, child2 = crossover(parents[i], parents[i+1])
        child1 = mutation(child1, mutation_rate)
        child2 = mutation(child2, mutation_rate)
        children.append(child1)
        children.append(child2)
    population = np.vstack(children)

# 输出最佳个体
best_individual = population[np.argmax(fitness_values)]
print("Best individual:", best_individual)
```
