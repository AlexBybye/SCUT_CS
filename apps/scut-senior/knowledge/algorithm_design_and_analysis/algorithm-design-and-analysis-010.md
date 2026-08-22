---
source_id: algorithm-design-and-analysis-010
course_id: algorithm_design_and_analysis
title: 1_tutorial
original_file: "学科资料/算法设计与分析/PPT-英文版/1_tutorial.pdf"
document_role: note
year: 
locator_type: page
---

# 1_tutorial

<!-- page: 1 -->

1.
给定一个长度为10的非负数组A，请给
出输出数组最大值的伪代码.

<!-- page: 2 -->

1.
给定一个长度为10的非负数组A，请给
出输出数组最大值的伪代码.

Begin:

Input: A
Output: max_member
max_tmp ←-1
For i = 0 to 9 do:

If A[i] > max_tmp do:

max_tmp ←A[i]
End if
End for
max_member ←max_tmp
End

<!-- page: 3 -->

2. 给定数组A, 长度为N, 按以下伪代码进行排序：

for i= 1 to N-1:

for j= 1 to N-i:

if(A[j] > A[j+1]):

swap(A[j],A[j+1])

swap(a,b)表示交换两个数的位置,

1）以上排序的结果是升序还是降序？

2）最外层for循环每进行一次，数组就排序一次，直至排序
完成，设数组为[1,10,7,6,9,3]，写出前3次排序后的数组。

<!-- page: 4 -->

1）以上排序的结果是升序还是降序？

如果前一个元素比后一个元素大，就要交换两者
的位置，直至最大的元素交换到最后一个位置，
因此排序的结果是升序。

for i= 1 to N-1:

for j= 1 to N-i:

if(A[j] > A[j+1]):

swap(A[j],A[j+1])

<!-- page: 5 -->

2）最外层for循环每进行一次，数组就排序一次，
直至排序完成，设数组为[1,10,7,6,9,3]，写出前3
次排序后的数组。

①[1,7,6,9,3,10]
②[1,6,7,3,9,10]
③[1,6,3,7,9,10]
…

for i= 1 to N-1:

for j= 1 to N-i:

if(A[j] > A[j+1]):

swap(A[j],A[j+1])

<!-- page: 6 -->

3.
给定数组[54,26,93,17,77,31,44,55,20],
使用Merge-Sort算法进行由小到大的
排序，画出过程。

<!-- page: 7 -->

3.
给定数组[54,26,93,17,77,31,44,55,20],
使用Merge-Sort算法进行由小到大的
排序，画出过程。

![image](assets/assets/algorithm-design-and-analysis-010/image-001.png)

![image](assets/assets/algorithm-design-and-analysis-010/image-002.png)

<!-- page: 8 -->

3.
给定数组[54,26,93,17,77,31,44,55,20],
使用Merge-Sort算法进行由小到大的
排序，画出过程。

![image](assets/assets/algorithm-design-and-analysis-010/image-003.png)

![image](assets/assets/algorithm-design-and-analysis-010/image-004.png)

![image](assets/assets/algorithm-design-and-analysis-010/image-005.png)

![image](assets/assets/algorithm-design-and-analysis-010/image-006.png)

![image](assets/assets/algorithm-design-and-analysis-010/image-007.png)
