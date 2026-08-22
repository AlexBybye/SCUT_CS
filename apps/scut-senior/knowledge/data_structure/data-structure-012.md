---
source_id: data-structure-012
course_id: data_structure
title: "2015级数据结构试卷A"
original_file: "学科资料/数据结构/往年卷/2015级数据结构试卷A.doc"
document_role: past_exam
year: 2015
locator_type: none
---

# 2015级数据结构试卷A

**诚信应考,考试作弊将带来严重后果！**

**华南理工大学期末考试**

**《**Data Structure**》试卷** **A**

**注意事项：1.** **考前请将密封线内填写清楚；**

**2.** **所有答案请答在答题纸上；**

**3．考试形式：闭卷；**

**4.** **本试卷共十大题，满分100分，考试时间120分钟**。

| **题 号** | **一** | **二** | **三** | **四** | **五** | **六** | **七** | **八** | **九** | **十** | **总分** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **得 分** |  |  |  |  |  |  |  |  |  |  |  |
| **评卷人** |  |  |  |  |  |  |  |  |  |  |  |

1.  1. Select the correct choice.        (20 scores, each 2 scores)

(1)  An algorithm must be or do all of the following EXCEPT:    (     )

(A) Correct      (B)  Finite   (C)  Ambiguous      (D)  Concrete steps

(2)  Pick the growth rate that corresponds to the most  inefficient algorithm as n gets large:  (     )

(A)  2n3                (B) 2n                 (C) n!         (D)  20n2logn

(3)  If a data element requires  8  bytes and a pointer requires 4 bytes, then a  linked  list representation will be more space efficient than a standard array representation when the fraction of non-null  elements is less than about:  (      )

(A)  1/4       (B) 2/3              (C)  4/5          (D)  3/4

(4)   Which statement is not correct among the following four:    (    )
- The Quick-sort is an unstable sorting algorithm.
- The number of empty sub-trees in a non-empty binary tree is one more than the number of nodes in the tree.
- The  worst  case for my algorithm is  n  becoming larger and larger  because that is the  slowest.
- A cluster is the smallest unit of allocation for a file, so all files occupy a multiple of the  cluster  size.

(5)  Which of the following is a true statement:  (      )

(A)  A general tree can be  transferred  to a binary tree with the root having both left child and right child.

(B) In a BST,  the node can be  enumerated sorted by a preorder  traversal  to the BST.

(C) In a BST, the left child of any node is less than the right child, but in a heap, the left child of any node could be less than or greater than the right child.

(D)  A  heap  must be full binary tree.

(6)  The  golden rule of  a disk-based program  design  is to:  (      )

(A) Improve the basic operations.          (B) Minimize the number of disk accesses.

(C) Eliminate the recursive calls.        (D) Reduce main memory use.

(7)  Given an array as  A[m][n].  Supposed  that  *A*[0][0]is located at  644(10)  and *A*[2][2]is stored at  676(10), and every element occupies one space.  “(10)”  means that the number is presented in  decimals. Then the element  *A*[3][3](10)  is at position:

(     )

(A)  692    (B)  695    (C)  660    (D)  708

(8)  If there is 0.5MB working memory,  4KB blocks, yield 128 blocks for working memory.  By the multi-way merge in external  sorting, the average run size  and the  sorted  size  in one pass  of multi-way  merge on average  are  separately  (           )?

(A)    0.5MB, 128 MB		         (B) 2MB, 512MB

(C)    1MB, 128MB				  	  (D)  1MB, 256MB

(9) Which algorithm is used to generate runs in classic external sorting? (      )

(A) Quick-sort       (B) Bubble sort

(C  )  Insertion sort      (D) Replacement selection

(10) Assume that we have eight records, with key values A to H, and that they are initially placed in alphabetical order. Now, consider the result of applying the following access pattern:  F D F G G F A D F G, if the list is organized by the move-to-front heuristic, then the final list will be (        ).
- G F D A C H B E                  (B)  G F D A B C E H

(C) F D G A E C B H                  (D) F D G E A B C H

2.  A certain binary tree has the preorder enumeration as  ABCEDFGHIJ  and the inorder enumeration as  CEBFDAHGJI. Try to draw the binary tree and give the postorder enumeration. (The process of your solution is required!!!)  (7  scores)

3. Fill the blank with correct C++ codes  to implement Mergesort algorithm:  (12  scores)

template <class Elem, class Comp>

void mergesort(Elem A[], Elem temp[],

int left, int right) {

int mid =  ____①_____;

if (____②___) return;

mergesort<Elem,Comp>(A, temp, left, mid);

mergesort<Elem,Comp>(A, temp, mid+1, right);

for (int i=left; i<=right; i++) // Copy

temp[i] = A[i];

int i1 = left; int i2 = mid + 1;

for (int curr=left; curr<=right; curr++) {

if (i1 == mid+1)      // Left exhausted

A[curr] =  ____③_____;

else if (i2 > right)  // Right exhausted

A[curr] =  ___  ④_____;

else if (Comp::lt(temp[i1], temp[i2]))

A[curr] =    ____⑤___;

else A[curr] =  ____⑥___;

}}

4.  Show the max-heap that results from running buildHeap with values stored in an array:

10    4   7    13   9    16    8    20   11   25 .   (8  scores)
1. Inserting the values into the heap one by one.
1. Values are available at the same time.

5.  Build the Huffman coding tree and determine the codes for the following set of letters and weights:

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| 15 | 5 | 13 | 26 | 10 | 11 | 16 | 4 |

Draw the Huffman coding tree and give the Huffman code for each letters. What is the expected length in bits of a message containing n characters for this frequency distribution?  (The process of your solution is required!!!)   (10  scores)

6. Given a hash table of size 11, assume that![formula-object](assets/assets/data-structure-012/image-001.png)and ![formula-object](assets/assets/data-structure-012/image-002.png)are  two hash functions, where  $H_1$ is  used to get home position and  $H_2$ is  used to  resolve  collision for method double hashing.  Please insert keys 20,  31,  43,  26, 30, 13, 12,  67, 1  into the hash table in order.              (10  scores)

7. Please insert  8，55，17 into  the  following  2-3 tree. Inserting a key, draw a picture for the resulted 2-3 tree.  Thus  you should draw 3 pictures.  (10 scores)

![formula-object](assets/assets/data-structure-012/image-005.png)

8.  List the order in which the edges of the  following  graph are visited when running Prim's minimum-cost spanning tree algorithm starting at vertex a. Show the final MST. (5  scores).

![image](assets/assets/data-structure-012/image-006.jpeg)

9.  Assume a disk drive is configured as follows. The total storage is approximately 1.5G divided among 15 surfaces. Each surface has 512 tracks; there are 256 sectors/track, 1024 byte/sector, and 32 sectors/cluster. The disk turns at  5400rmp (11.1 ms/r). The track-to-track seek time is 20 ms, and the average seek time is  50 ms. Now how  long  does it take to read all of the data in a 640 KB file on the disk? Assume that the file’s clusters are spread randomly across the disk. A seek must be performed each time the I/O reader moves to a new track. Show your calculations. (The process of your solution is required!!!)    (10  scores)

10.  Write a program to visit all of the nodes of a Binary Tree in breadth-first search (BFS) order. E.g. the follow Tree, the traversal result is ABCDEFG.  (8  scores)

![formula-object](assets/assets/data-structure-012/image-007.png)
