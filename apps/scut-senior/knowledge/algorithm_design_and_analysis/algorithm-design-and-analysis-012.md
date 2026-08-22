---
source_id: algorithm-design-and-analysis-012
course_id: algorithm_design_and_analysis
title: 2-tutorial
original_file: "学科资料/算法设计与分析/PPT-英文版/2-tutorial.pdf"
document_role: note
year: 
locator_type: page
---

# 2-tutorial

<!-- page: 1 -->

1. 求f 𝑛= log 𝑛! 的确界。

1

<!-- page: 2 -->

1. 求f 𝑛= log 𝑛! 的确界。

𝑛
log 𝑗
• 显然σ𝑗=1
𝑛
log 𝑗≤σ𝑗=1

f 𝑛= log 𝑛! = σ𝑗=1

𝑛
log 𝑛
⇒σ𝑗=1

𝑛
log 𝑗= Ο 𝑛𝑙𝑜𝑔𝑛

𝑛

𝑛

• σ𝑗=1
𝑛
log 𝑗≥σ𝑗=1

2
log

2
=

n
2 log
𝑛

2
=

n
2 log 𝑛−
n
2
⇒σ𝑗=1

𝑛
log 𝑗= Ω 𝑛𝑙𝑜𝑔𝑛

因此，f 𝑛= Θ 𝑛𝑙𝑜𝑔𝑛.

2

<!-- page: 3 -->

2. 分析Selection-Sort算法的复杂度。

Selection-Sort
• 输入: n个元素的数组：A[1…n]
• 输出: 按非降序排列的数组：A[1…n]
1.
sort(1)

• 过程: sort(i) {对A[1…n]排序}
1.
if i < n then
2.
k ← i
3.
for j ← i+1 to n
4.
if A[j] < A[k] then k ← j
5.
end for
6.
if k ≠i then 互换A[i] 和A[k]
7.
sort(i+1)
8.
end if

3

<!-- page: 4 -->

2. 分析Selection-Sort算法的复杂度。

C(𝑛)表示有𝑛个输入元素时的比较次数
• C(1)=0
• 第𝑖= 1次调用sort的比较次数等于𝑛−𝑖次元素比
较加上对A[𝑖+1,…,𝑛]排序的比较次数C(𝑛−𝑖)，

得到递推式C(𝑛)= ቊ0
𝑖𝑓𝑛= 1
C(𝑛−1)+(𝑛−1)
𝑖𝑓𝑛> 1

• 该递推式的解为C(𝑛)= σ𝑖=1
n−1 𝑖= 𝑛(𝑛−1)/2
因此，C 𝑛= Θ 𝑛2 .

4
