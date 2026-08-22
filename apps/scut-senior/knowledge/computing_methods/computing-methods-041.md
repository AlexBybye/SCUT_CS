---
source_id: computing-methods-041
course_id: computing_methods
title: "计算方法Unit5课后题"
original_file: "学科资料/计算方法/书后作业题目及其解答：老粉福利，作业开源啦！/计算方法Unit5课后题.md"
document_role: note
year: 
locator_type: heading
---

# 计算方法Unit5课后题

## 于博宇 计算机科学与技术一班 202330453151![[Pasted image 20260511093151.png]]
### 要求完成1、2、3题，如下所示：
- ### 1、分别用顺序高斯消去法、列主元高斯消去法、全主元高斯消去法求解方程组

$$\begin{cases}2x_1 + 3x_2 + 5x_3 = 5 \\3x_1 + 4x_2 + 7x_3 = 6 \\x_1 + 3x_2 + 3x_3 = 5\end{cases}$$
#### （1）顺序高斯消去法
增广矩阵：
$$\left[\begin{array}{ccc|c}2 & 3 & 5 & 5 \\3 & 4 & 7 & 6 \\1 & 3 & 3 & 5\end{array}\right]$$
第一次消元：
$$\left[\begin{array}{ccc|c}2 & 3 & 5 & 5 \\0 & -0.5 & -0.5 & -1.5 \\0 & 1.5 & 0.5 & 2.5\end{array}\right]$$
第二次消元：
$$\left[\begin{array}{ccc|c}2 & 3 & 5 & 5 \\0 & -0.5 & -0.5 & -1.5 \\0 & 0 & -1 & -2\end{array}\right]$$
回代求解：
`x3=2`，`x2=1`，`x1=-4`

##### （2）列主元高斯消去法
交换行后增广矩阵：
$$\left[\begin{array}{ccc|c}3 & 4 & 7 & 6 \\2 & 3 & 5 & 5 \\1 & 3 & 3 & 5\end{array}\right]$$
第一次消元：
$$\left[\begin{array}{ccc|c}3 & 4 & 7 & 6 \\0 & (1/3) & (1/3) & 1 \\0 & (5/3) & (2/3) & 3\end{array}\right]$$
交换行后消元：
$$\left[\begin{array}{ccc|c}3 & 4 & 7 & 6 \\0 & (5/3) & (2/3) & 3 \\0 & 0 & (1/5) & (2/5)\end{array}\right]$$
回代求解：
`x3=2`，`x2=1`，`x1=-4`

##### （3）全主元高斯消去法
行列交换后矩阵：
$$\left[\begin{array}{ccc|c}7 & 4 & 3 & 6 \\5 & 3 & 2 & 5 \\3 & 3 & 1 & 5\end{array}\right]$$
第一次消元：
$$\left[\begin{array}{ccc|c}7 & 4 & 3 & 6 \\0 & (1/7) & -(1/7) & (5/7) \\0 & (9/7) & -(2/7) & (17/7)\end{array}\right]$$
二次变换消元：
$$\left[\begin{array}{ccc|c}7 & 3 & 4 & 6 \\0 & -(2/7) & (9/7) & (17/7) \\0 & 0 & -(1/2) & -(1/2)\end{array}\right]$$
回代求解：
`x1=-4`，`x2=1`，`x3=2`
最终解：`x1=-4，x2=1，x3=2`

 - ###  2、用LU分解法求解方程组

$$\begin{cases}2x_1 - 3x_2 + 2x_3 = 5 \\-4x_1 + 2x_2 - 6x_3 = 14 \\2x_1 + 2x_2 + 4x_3 = 8\end{cases}$$
矩阵分解 `A=LU`：
$$L=\begin{bmatrix}1 & 0 & 0 \\-2 & 1 & 0 \\1 & -(5/4) & 1\end{bmatrix},\quad U=\begin{bmatrix}2 & -3 & 2 \\0 & -4 & -2 \\0 & 0 & -(1/2)\end{bmatrix}$$
求解 `Ly=b`：`b=[5,14,8]^T`
`y1=5`，`y2=24`，`y3=33`
求解 `Ux=y`：
`x3=-66`，`x2=27`，`x1=109`
最终解：`x1=109，x2=27，x3=-66`

- #### 3、用平方根法Cholesky分解求解方程组
$$\begin{cases}3x_1 + 2x_2 + x_3 = 5 \\2x_1 + 2x_2 = 3 \\x_1 + 3x_3 = 4\end{cases}$$
矩阵分解 `A=LL^T`：
$$L=\begin{bmatrix}\sqrt{3} & 0 & 0 \\(2/\sqrt{3}) & (\sqrt{6}/3) & 0 \\(1/\sqrt{3}) & -(\sqrt{6}/3) & \sqrt{2}\end{bmatrix}$$
求解 `Ly=b`：`b=[5,3,4]^T`
`y1=(5/\sqrt{3})`，`y2=-(1/\sqrt{6})`，`y3=\sqrt{2}`
求解 `L^Tx=y`：
`x3=1`，`x2=(1/2)`，`x1=1`
最终解：`x1=1，x2=1/2，x3=1`
