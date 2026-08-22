---
source_id: intelligent-algorithms-029
course_id: intelligent_algorithms
title: "遗传算法GA"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/遗传算法GA.md"
document_role: note
year: 
locator_type: heading
---

# 遗传算法GA

# GA算法的基本理念：
![[2. 遗传算法pr(1).pdf#page=6&rect=116,66,789,390|2. 遗传算法pr(1), p.6]]
![[2. 遗传算法pr(1).pdf#page=7&rect=124,21,796,483|2. 遗传算法pr(1), p.7]]
# GA算法适合应用场景
## 广泛应用于优化和搜索问题，可以用于优化函数和TSP问题
- **优点**：
    - **全局搜索能力**：能够进行全局搜索，避免陷入局部最优解。
    - **并行性**：可以同时处理多个个体，具有一定的并行性。
    - **适应性强**：适用于各种类型的优化问题，尤其是传统优化方法难以解决的问题。
- **缺点**：
    - **计算复杂度高**：种群规模较大需要进行大量的计算。
    - **参数选择敏感**：算法的性能对参数（如交叉概率、变异概率等）的选择较为敏感。
    - **早熟收敛**：在某些情况下，可能会过早收敛到局部最优解。**说白了就是局部搜索能力弱**

``` python
import random

# 问题参数
c = 15  # 背包容量
w = [7, 3, 12, 5, 14]  # 物品重量
v = [10, 4, 15, 6, 9]  # 物品价值
n = len(w)  # 物品数量

# GA算法参数
population_size = 50  # 种群大小
crossover_probability = 0.8  # 交叉概率
mutation_probability = 0.1  # 变异概率
generations = 100  # 迭代次数

# 初始化种群
def initialize_population():
    population = []
    for _ in range(population_size):
        individual = [random.randint(0, 1) for _ in range(n)]
        # 确保初始个体合法
        while not is_feasible(individual):
            individual = [random.randint(0, 1) for _ in range(n)]
        population.append(individual)
    return population

# 判断解是否合法
def is_feasible(individual):
    total_weight = sum(w[i] * individual[i] for i in range(n))
    return total_weight <= c

# 计算目标函数值（适应度）
def calculate_fitness(individual):
    return sum(v[i] * individual[i] for i in range(n))

# 选择操作（轮盘赌选择）
def selection(population):
    fitness_values = [calculate_fitness(individual) for individual in population]
    total_fitness = sum(fitness_values)
    probabilities = [fitness / total_fitness for fitness in fitness_values]
    # 累积概率
    cumulative_probabilities = [sum(probabilities[:i+1]) for i in range(len(probabilities))]
    # 选择两个父代个体
    parents = []
    for _ in range(2):
        r = random.random()
        for i, cp in enumerate(cumulative_probabilities):
            if r <= cp:
                parents.append(population[i])
                break
    return parents

# 交叉操作（单点交叉）
def crossover(parents):
    if random.random() < crossover_probability:
        crossover_point = random.randint(1, n-1)
        child1 = parents[0][:crossover_point] + parents[1][crossover_point:]
        child2 = parents[1][:crossover_point] + parents[0][crossover_point:]
        return child1, child2
    else:
        return parents[0], parents[1]

# 变异操作
def mutation(individual):
    for i in range(n):
        if random.random() < mutation_probability:
            individual[i] = 1 - individual[i]
    # 修复不合法解
    while not is_feasible(individual):
        # 随机选择一个选中的物品并移除
        selected = [i for i in range(n) if individual[i] == 1]
        if not selected:
            break
        remove = random.choice(selected)
        individual[remove] = 0
    return individual

# 遗传算法主循环
def genetic_algorithm():
    population = initialize_population()
    best_individual = None
    best_fitness = 0

    for generation in range(generations):
        # 计算适应度
        fitness_values = [calculate_fitness(individual) for individual in population]
        current_best_fitness = max(fitness_values)
        current_best_individual = population[fitness_values.index(current_best_fitness)]

        # 更新全局最优解
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_individual = current_best_individual

        # 选择、交叉和变异生成新一代
        new_population = []
        for _ in range(population_size // 2):
            parents = selection(population)
            child1, child2 = crossover(parents)
            child1 = mutation(child1)
            child2 = mutation(child2)
            new_population.extend([child1, child2])

        # 如果种群大小为奇数，添加一个随机个体
        if len(new_population) < population_size:
            new_population.append(initialize_population()[0])

        # 精英策略：保留当前最优解
        population = new_population
        population.append(best_individual)

        # 限制种群大小
        population = population[:population_size]

    return best_individual, best_fitness

# 执行算法
best_solution, best_value = genetic_algorithm()

# 输出结果
print("最优解为：", best_solution)
print("最大价值为：", best_value)
```
# 问题：初始参数的选择
## 1. 种群大小（Population Size）
- **作用**：种群大小决定了每一代中包含的个体数量。较大的种群大小可以增加种群的多样性，提高算法的全局搜索能力，但会增加计算量。
- **选择方法**：
    - **常见取值范围**：20到100之间。
    - **问题规模**：对于较小规模的问题，可以选择较小的种群大小；对于较大规模的问题，可以选择较大的种群大小。
    - **计算资源**：根据可用的计算资源调整种群大小，以平衡计算时间和搜索能力。
    
### 2. 交叉概率（Crossover Probability）
- **作用**：交叉概率决定了两个父代个体进行交叉操作生成子代个体的概率。较高的交叉概率可以增加种群的多样性，但过高的概率可能导致优良个体的特征被破坏。
- **选择方法**：
    - **常见取值范围**：0.6到0.95之间。
    - **问题特点**：对于需要较强全局搜索能力的问题，可以选择较高的交叉概率；对于局部搜索能力较强的问题，可以选择较低的交叉概率。
    - **试验法**：通过多次试验，观察算法的收敛速度和解的质量，调整交叉概率。
    
### 3. 变异概率（Mutation Probability）
- **作用**：变异概率决定了个体中的每个基因发生变异的概率。适当的变异概率可以增加种群的多样性，防止算法过早收敛。
- **选择方法**：
    - **常见取值范围**：0.001到0.1之间。
    - **问题特点**：对于需要较强全局搜索能力的问题，可以选择较高的变异概率；对于局部搜索能力较强的问题，可以选择较低的变异概率。
    - **试验法**：通过多次试验，观察算法的收敛速度和解的质量，调整变异概率。
    
### 4. 迭代次数（Generations）
- **作用**：迭代次数决定了算法运行的代数。较多的迭代次数可以提高算法的搜索能力，但会增加计算时间。
- **选择方法**：
    - **常见取值范围**：100到1000之间。
    - **问题规模**：对于较小规模的问题，可以选择较少的迭代次数；对于较大规模的问题，可以选择较多的迭代次数。
    - **收敛条件**：可以根据算法的收敛情况动态调整迭代次数，例如当最优解在连续若干代中不再改进时停止。
    
### 5. 选择策略（Selection Strategy）
- **作用**：选择策略决定了如何从当前种群中选择父代个体进行交叉和变异操作。不同的选择策略对算法的收敛速度和解的质量有影响。
- **常见选择策略**：
    - **轮盘赌选择（Roulette Wheel Selection）**：根据个体的适应度值计算选择概率，适应度越高的个体被选中的概率越大。

### 6. 交叉策略（Crossover Strategy）
- **作用**：交叉策略决定了如何对两个父代个体进行交叉操作生成子代个体。不同的交叉策略对算法的搜索能力和解的质量有影响。
- **常见交叉策略**：
    - **单点交叉（One-Point Crossover）**：随机选择一个交叉点，交换两个父代个体在该点后的基因片段。
    - **均匀交叉（Uniform Crossover）**：每个基因以一定的概率从两个父代个体中随机选择一个值。

### 7. 变异策略（Mutation Strategy）
- **作用**：变异策略决定了如何对个体中的基因进行变异操作。不同的变异策略对算法的搜索能力和解的质量有影响。
- **常见变异策略**：
    - **位翻转变异（Bit-Flip Mutation）**：对二进制编码的个体，随机选择一个或多个位进行翻转。
    - **均匀变异（Uniform Mutation）**：对实数编码的个体，随机选择一个或多个基因，将其值在一定范围内进行均匀变化。
    - **高斯变异（Gaussian Mutation）**：对实数编码的个体，随机选择一个或多个基因，将其值加上一个高斯分布的随机数。

### 8. 精英策略（Elitist Strategy）
- **作用**：精英策略旨在将当前最优解保留到下一代，以防止算法在进化过程中丢失已找到的优良解。
- **常见精英策略**：
    - **保留最优解**：在每一代中，将当前最优解直接复制到下一代种群中。
    - **替换最差解**：在每一代中，将当前最优解替换掉种群中最差的解。
