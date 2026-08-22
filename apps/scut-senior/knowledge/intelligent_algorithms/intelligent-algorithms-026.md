---
source_id: intelligent-algorithms-026
course_id: intelligent_algorithms
title: "粒子群优化PSO"
original_file: "学科资料/智能算法/智能算法PPT与笔记（开源）/粒子群优化PSO.md"
document_role: note
year: 
locator_type: heading
---

# 粒子群优化PSO

# PSO算法的基本理念：
接下来我们接触群智的内容：
![[4. 粒子群优化pr(1).pdf#page=8&rect=102,36,796,477|4. 粒子群优化pr(1), p.8]]
![[4. 粒子群优化pr(1).pdf#page=14&rect=51,29,817,571|4. 粒子群优化pr(1), p.14]]
# PSO算法适合应用场景
## 在函数优化和参数权重及图像处理有优势，但传统PSO函数优化比不过DE DE的rand/1适合多峰 best/1适合单峰
1. **函数优化**：PSO算法在连续空间优化问题中表现出色，适用于各种类型的函数优化，如单峰函数、多峰函数、非线性函数等。
2. **神经网络&金融模型训练**：PSO算法可用于优化神经网络的权重和偏置，提高神经网络的训练效率和泛化能力。
3. **图像处理**：PSO算法在图像分割、图像配准、目标识别等领域有广泛应用，能够有效处理高维数据。
## 优点

### 1. **全局搜索能力强**：PSO算法通过个体和群体的合作与竞争机制，能够在较大的搜索空间中找到全局最优解，避免陷入局部最优。
#### 2. **并行性好**：PSO算法中的粒子更新操作相互独立，适合并行计算，可以利用多核处理器或集群提高计算效率。
##### 3. **适应性强**：PSO算法对目标函数的连续性和可导性没有严格要求，适用于处理非线性、不连续、多模态等复杂优化问题。
## 缺点
### 1. **早熟收敛**：PSO算法在某些情况下可能会过早收敛到局部最优解，特别是在复杂或高维问题中。
#### 2. **参数选择敏感**：PSO算法的性能对参数（如惯性权重、学习因子等）的选择较为敏感，需要通过试验或经验进行调整。
##### 3. **计算复杂度高**：对于大规模或高维问题，PSO算法的计算量较大，可能导致计算时间过长。
# 自适应参数调整、邻域最优经验和精英策略的优化PSO算法的Python代码示例，用于求解Sphere函数优化问题:
``` python
import numpy as np

# 优化后的PSO算法
class OptimizedPSO:
    def __init__(self, objective_function, dimensions, bounds, population_size=30, max_iterations=100):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.bounds = bounds
        self.population_size = population_size
        self.max_iterations = max_iterations
        
        # 初始化参数
        self.w = 0.9  # 初始惯性权重
        self.w_min = 0.4
        self.c1 = 2.0  # 学习因子
        self.c2 = 2.0
        self.neighborhood_size = 5  # 邻域大小
        
        # 初始化粒子位置、速度、个体最优和全局最优
        self.particles = np.random.uniform(low=bounds[0], high=bounds[1], size=(population_size, dimensions))
        self.velocities = np.zeros_like(self.particles)
        self.pbest_positions = self.particles.copy()
        self.pbest_values = np.full(population_size, float('inf'))
        self.gbest_position = np.random.uniform(low=bounds[0], high=bounds[1], size=dimensions)
        self.gbest_value = float('inf')
        self.elite_position = self.gbest_position.copy()
        self.elite_value = self.gbest_value
        
    def optimize(self):
        for iteration in range(self.max_iterations):
            # 评估每个粒子的适应度
            for i in range(self.population_size):
                fitness = self.objective_function(self.particles[i])
                # 更新个体最优
                if fitness < self.pbest_values[i]:
                    self.pbest_values[i] = fitness
                    self.pbest_positions[i] = self.particles[i].copy()
                # 更新全局最优和精英策略
                if fitness < self.gbest_value:
                    self.gbest_value = fitness
                    self.gbest_position = self.particles[i].copy()
                if fitness < self.elite_value:
                    self.elite_value = fitness
                    self.elite_position = self.particles[i].copy()
            
            # 动态调整惯性权重
            self.w = self.w_min + (self.w - self.w_min) * (1 - iteration / self.max_iterations)
            
            # 更新速度和位置
            for i in range(self.population_size):
                # 邻域最优经验
                neighborhood = np.random.choice(self.population_size, self.neighborhood_size, replace=False)
                lbest_value = np.min(self.pbest_values[neighborhood])
                lbest_position = self.pbest_positions[np.argmin(self.pbest_values[neighborhood])].copy()
                
                # 更新速度
                r1, r2 = np.random.rand(2)
                self.velocities[i] = self.w * self.velocities[i] + self.c1 * r1 * (self.pbest_positions[i] - self.particles[i]) + self.c2 * r2 * (lbest_position - self.particles[i])
                
                # 更新位置
                self.particles[i] += self.velocities[i]
                
                # 保持粒子在搜索空间内
                self.particles[i] = np.clip(self.particles[i], self.bounds[0], self.bounds[1])
            
            # 精英策略：将精英解加入种群
            self.particles[np.random.randint(0, self.population_size)] = self.elite_position
        
        return self.gbest_position, self.gbest_value

# 测试函数：Sphere函数
def sphere_function(x):
    return np.sum(x**2)

# 参数设置
dimensions = 30
bounds = (-100, 100)
population_size = 30
max_iterations = 100

# 执行优化
optimizer = OptimizedPSO(sphere_function, dimensions, bounds, population_size, max_iterations)
best_position, best_value = optimizer.optimize()

print("最优解的位置：", best_position)
print("最优解的值：", best_value)
```
# 解析：对传统PSO的优化：
1. **自适应参数调整**：
    - **惯性权重（W）**：根据迭代次数或目标评价次数动态调整惯性权重，例如从0.9线性下降至0.4。
    - **学习因子（c1和c2）**：根据粒子群的收敛状态自适应地调整学习因子的值。
2. **拓扑结构调整**：
    - **邻域最优经验（lBest）**：用邻域最优经验代替全局最优经验，增强群体搜索多样性，防止陷入局部最优。
    - **小世界拓扑网络**：引入小世界拓扑结构，提高算法的求解精度与效率。
3. **更新公式改进**：
    - **构造模范向量**：将个体历史最优和群体历史最优整合成一个模范向量，避免粒子在两个相反方向震荡。
    - **全面学习粒子群优化（CLPSO）**：粒子在不同维度上向不同的优秀个体学习，提高算法的搜索能力和收敛速度。
4. **离散化处理**：
    - **二进制编码（BPSO）**：将粒子速度转化为更新粒子位置为0或1的概率，拓展PSO在离散优化问题中的应用。
    - **整数型离散PSO**：在转换为最终解时取整，或重新定义表示和更新方法。
5. **其他优化策略**：
    - **精英策略**：保留历史最优解，防止算法在进化过程中丢失已找到的优良解。
    - **混合算法**：将PSO与其他优化算法结合，如模拟退火（SA）、遗传算法（GA）等，提高算法的性能。
