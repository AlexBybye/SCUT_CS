---
source_id: intelligent-algorithms-030
course_id: intelligent_algorithms
title: "遗传编程GP"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/遗传编程GP.md"
document_role: note
year: 
locator_type: heading
---

# 遗传编程GP

## 先对我们的GA派梳理下应用场景
### GA老祖宗[[遗传算法GA]]，用于离散优化问题和组合优化问题
#### 下设一个[[差分进化DE]]用于连续优化问题，尤其是在多维空间中寻找 `全局最优解`
#### 出来一个[[进化策略ES]]，主要也是连续优化，但相比DE他更注重快速收敛，特别是在 `机器学习中的参数优化`，如 神经网络的权值优化和结构优化
#### 最后是今天的[[遗传编程GP]]，主要用于`自动化程序设计`，生成解决特定问题的计算机程序

### 他们之间的差异还有：
#### - **编码方式**：遗传算法通常使用二进制编码，而差分进化和进化策略使用实数编码，遗传编程使用树形结构
#### - **变异和交叉操作**：遗传算法通过基因片段交换和随机变异，差分进化通过差分变异，进化策略通过变异强度调整，遗传编程通过树形结构的操作  
#### - **选择机制**：遗传算法使用多种选择策略（如轮盘赌、锦标赛选择），差分进化采用一对一竞争，进化策略采用“最优个体存活策略”，遗传编程通过适应度评估选择最优程序

## 回到主角GP，这个基本上就用来生成程序
## ![[7. 遗传编程pr.pdf#page=13&rect=62,104,800,451|7. 遗传编程pr, p.13]]![[7. 遗传编程pr.pdf#page=14&rect=64,58,800,468|7. 遗传编程pr, p.14]]##  GP参数终止条件
![[7. 遗传编程pr.pdf#page=15&rect=50,82,645,459|7. 遗传编程pr, p.15]]
## GP解决符号回归代码示例：
``` python
# 导入必要的库
import operator
import math
import random

import numpy as np
import matplotlib.pyplot as plt

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

# 定义目标函数，这里是一个简单的多项式函数
TARGET = lambda x: x**3 - x**2 + x - 2  # 目标函数

# 生成训练数据
MIN_VAL = -10  # 输入数据的最小值
MAX_VAL = 10   # 输入数据的最大值
N_POINTS = 100  # 生成的数据点数量

# 生成输入和输出数据
x = np.linspace(MIN_VAL, MAX_VAL, N_POINTS)
y = TARGET(x)

# 定义函数集和终端集
def protected_div(left, right):
    # 保护除法操作，避免除以零的错误
    try:
        return left / right
    except ZeroDivisionError:
        return 1

# 创建原始集合，包含基本的数学运算和终端
pset = gp.PrimitiveSet("MAIN", 1)  # 定义一个原始集合，包含一个输入参数
pset.addPrimitive(operator.add, 2)  # 添加加法运算
pset.addPrimitive(operator.sub, 2)  # 添加减法运算
pset.addPrimitive(operator.mul, 2)  # 添加乘法运算
pset.addPrimitive(protected_div, 2)  # 添加保护除法运算
pset.addPrimitive(operator.neg, 1)  # 添加负号运算
pset.addPrimitive(math.cos, 1)  # 添加余弦运算
pset.addPrimitive(math.sin, 1)  # 添加正弦运算
pset.addEphemeralConstant("rand101", lambda: random.randint(-1, 1))  # 添加随机常数
pset.renameArguments(ARG0='x')  # 重命名输入参数为x

# 创建适应度类和个体类
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))  # 创建适应度类，权重为负表示最小化问题
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)  # 创建个体类，继承自原始树

# 注册工具
toolbox = base.Toolbox()  # 创建工具箱
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)  # 注册表达式生成函数
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)  # 注册个体初始化函数
toolbox.register("population", tools.initRepeat, list, toolbox.individual)  # 注册种群初始化函数
toolbox.register("compile", gp.compile, pset=pset)  # 注册编译函数

# 定义适应度评估函数
def eval_symb_reg(individual):
    # 编译个体表达式
    func = toolbox.compile(expr=individual)
    # 计算预测值
    y_pred = np.array([func(i) for i in x])
    # 计算均方误差
    return (np.mean((y - y_pred) ** 2),)

toolbox.register("evaluate", eval_symb_reg)  # 注册评估函数
toolbox.register("select", tools.selTournament, tournsize=3)  # 注册选择函数
toolbox.register("mate", gp.cxOnePoint)  # 注册交叉函数
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)  # 注册变异表达式生成函数
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)  # 注册变异函数

# 限制树的深度，防止过拟合
toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

# 运行遗传编程
def main():
    random.seed(42)  # 设置随机种子，确保结果可重复
    pop = toolbox.population(n=300)  # 初始化种群，种群大小为300
    hof = tools.HallOfFame(1)  # 创建名人堂，保存最优个体
    
    # 定义统计信息
    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(lambda ind: len(ind))
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg", np.mean)
    mstats.register("std", np.std)
    mstats.register("min", np.min)
    mstats.register("max", np.max)
    
    # 运行遗传算法
    pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.2, 40, stats=mstats,
                                   halloffame=hof, verbose=True)
    
    # 输出最优个体及其适应度
    best_ind = hof[0]
    print(f"\nBest individual: {best_ind}")
    print(f"Fitness: {best_ind.fitness.values[0]}")
    
    # 绘制结果
    func = toolbox.compile(expr=best_ind)
    y_pred = np.array([func(i) for i in x])
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label="Target")
    plt.plot(x, y_pred, label="GP Prediction")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Symbolic Regression with Genetic Programming")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
```
1. **目标函数**：我们定义了一个简单的多项式函数 `TARGET = x³ - x² + x - 2`，作为我们要拟合的目标函数。
2. **数据生成**：生成了100个点的输入和输出数据。
3. **函数集和终端集**：定义了基本的数学运算（加、减、乘、除、负号、正弦、余弦）和随机常数。
4. **适应度函数**：计算个体预测值与目标值之间的均方误差（MSE）。
5. **遗传操作**：包括选择、交叉和变异操作，并限制了树的深度以防止过拟合。
6. **运行遗传编程**：使用DEAP库的 `eaSimple` 算法进行进化，输出最佳个体及其适应度，并绘制结果。
