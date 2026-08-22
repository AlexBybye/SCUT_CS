---
source_id: intelligent-algorithms-022
course_id: intelligent_algorithms
title: "差分进化DE"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/差分进化DE.md"
document_role: note
year: 
locator_type: heading
---

# 差分进化DE

# DE算法的基本理念：
现代智能算法有两种，一种是GA派，还有一种是群智派，DE是目前优化函数的最好算法之一，是GA派的。
## 1. 初始化种群&设置算法参数
每个个体是D维向量，Xi​=(xi1​,xi2​,…,xiD​)。
![[3. 差分进化pr(1).pdf#page=16&rect=123,84,783,394|3. 差分进化pr(1), p.16]]
- **最大迭代次数（G_max）**：算法停止的条件之一，一开始置为1

### 2. 进化过程
对于每一代 G 从 1 到 Gmax​：
- **变异操作**：对每个目标个体 Xi​，通过与其他个体的差异生成一个变异个体 Vi​。常见的变异策略包括：
    
    - **DE/rand/1**：随机选择三个不同的个体 Xa​,Xb​,Xc​，生成变异个体 Vi​=Xa​+F⋅(Xb​−Xc​)。
        
    - **DE/best/1**：选择当前最优个体 Xbest​，生成变异个体 Vi​=Xbest​+F⋅(Xb​−Xc​)。
- **交叉操作**：将目标个体 Xi​ 和变异个体 Vi​ 进行交叉，生成试验个体 Ui​。交叉方式可以是二进制交叉或指数交叉。
    - **二进制交叉**：对于每个维度 j，以概率 CR 选择 Vi​ 的基因，否则选择 Xi​ 的基因。
    - **指数交叉**：随机选择一个起始点，连续选择一段基因。
- **修正新个体**：确保试验个体 Ui​ 满足问题的约束条件，并计算其适应度值。
- **选择操作**：比较目标个体 Xi​ 和试验个体 Ui​ 的适应度，选择适应度更高的个体进入下一代种群。
- **更新最优解**：记录并更新当前找到的最优解。

![[3. 差分进化pr(1).pdf#page=17&rect=112,23,793,482|3. 差分进化pr(1), p.17]]
# DE算法适合应用场景
DE的rand/1适合多峰 best/1适合单峰
## 相比GA，它不能做离散优化问题，但优势是参数少，可以在精度和速度中较为平衡。![[3. 差分进化pr(1).pdf#page=16&rect=123,84,783,394|3. 差分进化pr(1), p.16]]

``` python
import random

# 问题参数
c = 15  # 背包容量
w = [7, 3, 12, 5, 14]  # 物品重量
v = [10, 4, 15, 6, 9]  # 物品价值
n = len(w)  # 物品数量

# DE算法参数
population_size = 50  # 种群大小
F = 0.5  # 变异因子
CR = 0.7  # 交叉概率
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

# 变异操作
def mutation(population):
    mutated_population = []
    for i in range(population_size):
        # 随机选择三个不同的个体
        indices = [j for j in range(population_size) if j != i]
        a, b, c = random.sample(indices, 3)
        # 生成变异个体
        mutated_individual = []
        for j in range(n):
            if random.random() < 0.5:
                mutated_gene = population[a][j] + F * (population[b][j] - population[c][j])
                # 保持基因在[0, 1]范围内
                mutated_gene = 1 if mutated_gene > 1 else 0 if mutated_gene < 0 else mutated_gene
            else:
                mutated_gene = population[i][j]
            mutated_individual.append(round(mutated_gene))
        # 修复不合法解
        while not is_feasible(mutated_individual):
            selected = [j for j in range(n) if mutated_individual[j] == 1]
            if not selected:
                break
            remove = random.choice(selected)
            mutated_individual[remove] = 0
        mutated_population.append(mutated_individual)
    return mutated_population

# 交叉操作
def crossover(population, mutated_population):
    crossed_population = []
    for i in range(population_size):
        crossed_individual = []
        for j in range(n):
            if random.random() < CR:
                crossed_individual.append(mutated_population[i][j])
            else:
                crossed_individual.append(population[i][j])
        # 修复不合法解
        while not is_feasible(crossed_individual):
            selected = [j for j in range(n) if crossed_individual[j] == 1]
            if not selected:
                break
            remove = random.choice(selected)
            crossed_individual[remove] = 0
        crossed_population.append(crossed_individual)
    return crossed_population

# 选择操作
def selection(population, crossed_population):
    new_population = []
    for i in range(population_size):
        # 计算适应度
        fitness_original = calculate_fitness(population[i])
        fitness_crossed = calculate_fitness(crossed_population[i])
        # 选择适应度更高的个体
        if fitness_crossed > fitness_original:
            new_population.append(crossed_population[i])
        else:
            new_population.append(population[i])
    return new_population

# 差分进化算法主循环
def differential_evolution():
    population = initialize_population()
    best_individual = None
    best_fitness = 0

    for generation in range(generations):
        # 变异和交叉操作
        mutated_population = mutation(population)
        crossed_population = crossover(population, mutated_population)
        # 选择操作
        population = selection(population, crossed_population)
        # 更新全局最优解
        for individual in population:
            fitness = calculate_fitness(individual)
            if fitness > best_fitness:
                best_fitness = fitness
                best_individual = individual

    return best_individual, best_fitness

# 执行算法
best_solution, best_value = differential_evolution()

# 输出结果
print("最优解为：", best_solution)
print("最大价值为：", best_value)
```
