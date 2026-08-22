---
source_id: data-structure-017
course_id: data_structure
title: "2023-2024-1-数据结构参考答案-A卷"
original_file: "学科资料/数据结构/往年卷/2023-2024-1-数据结构参考答案-A卷.docx"
document_role: past_exam_answer
year: 2023
locator_type: none
---

# 2023-2024-1-数据结构参考答案-A卷

数据结构参考答案

2023-2024-1-A卷

**I. Select the correct choice.   (10 points)**

CCBCA

评分标准：每题2分。

**II. Fill in the blanks.  (10 points)**

<!-- question: data-structure-017-Q1 -->

(1) 2n-1

<!-- question: data-structure-017-Q2 -->

(2) n, 1

<!-- question: data-structure-017-Q3 -->

(3) v2, v4, v1, v3, v5

<!-- question: data-structure-017-Q4 -->

(4) 150000

<!-- question: data-structure-017-Q5 -->

(5) 3

评分标准：每题2分，部分正确可以考虑给1分。

**III  Application of Data Structure （60** **points, 10 points each）**
<!-- question: data-structure-017-Q6 -->

1. (a)  θ(n2)    (b)  θ(nlogn)   (c)  θ(n3)

评分标准：(a)和(b)各3分，(c)4分。
<!-- question: data-structure-017-Q7 -->

1. (1)                     (2)EGHFBCDA         (3)

评分标准：(1)4分; (2)3分；(3)3分。

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 17 | 13 |  |  | 21 | 12 | 22 | 14 | 34 | 2 |

(1+1+2+1+1+2+5+6)/8=19/8=2.375

评分标准：哈希过程8分，平均比较次数2分。
<!-- question: data-structure-017-Q8 -->

1. (1)

|  | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Initial | 0 | $\infty$ | $\infty$ | $\infty$ | $\infty$ | $\infty$ |
| Process 1 | 0 | 8 | $\infty$ | 20 | $\infty$ | 2 |
| Process 6 | 0 | 8 | $\infty$ | 12 | 5 | 2 |
| Process 5 | 0 | 8 | 20 | 12 | 5 | 2 |
| Process 2 | 0 | 8 | 11 | 12 | 5 | 2 |
| Process 3 | 0 | 8 | 11 | 12 | 5 | 2 |
| Process 4 | 0 | 8 | 11 | 12 | 5 | 2 |

<!-- question: data-structure-017-Q9 -->

1. 1->6, 6->5, 2->3, 2->4, 1->2

或：1->6, 2->3, 6->5, 2->4, 1->2

评分标准：(1)7分，(2)3分。
<!-- question: data-structure-017-Q10 -->

1. (1)                                 (2)

评分标准：(1)8分，(2)2分。

6.

评分标准：每个数1分。

**IV. Design of Algorithm.        (20** **points)**

<!-- question: data-structure-017-Q11 -->

1. template <class Elem, class Comp>

void qsort(Elem A[], int i, int j) {

if (j <= i) return;

int pivotindex = findpivot(A, i, j);

swap(A, pivotindex, j);

int k = partition<Elem,Comp>(A, i, j, A[j]);

swap(A, k, j);         // Put pivot in place

qsort<Elem,Comp>(A, i, k-1);

qsort<Elem,Comp>(A, k+1, j);

}

template <class Elem>

int partition(Elem A[], int l, int r,Elem& pivot) {

do {

while (A[l] < pivot) l++;

while ((r > l) && A[r] >=pivot)         r--;

swap(A, l, r);

} while (l < r);

return l;

}

评分标准：qsort函数5分，partition函数5分。

void PrintRange(BinNode<Elem>*  root,Key low,  Key high) {

if ( root == NULL)  return;

if (root->val() <=high)

PrintRange(root->right(), low, high);

if (root->val() >=low && root->val()<=high)

cout<<root->val()<<endl;

if (root->val() >=low)

PrintRange(root->left(), low, high);

}

评分标准：全对10分，部分正确酌情给分。
