---
source_id: data-structure-010
course_id: data_structure
title: "2011级数据结构试卷A及答案"
original_file: "学科资料/数据结构/往年卷/2011级数据结构试卷A及答案.doc"
document_role: past_exam_answer
year: 2011
locator_type: none
---

# 2011级数据结构试卷A及答案

**诚信应考,考试作弊将带来严重后果！**

**华南理工大学期末考试**

**《**  **Data Structure**  **》试卷** **A**

**注意事项：1.** **考前请将密封线内填写清楚；**

**2.** **所有答案请答在答题纸上；**

**3．考试形式：闭卷；**

**4.** **本试卷共十大题，满分100分，考试时间120分钟**。

| **题 号** | **一** | **二** | **三** | **四** | **五** | **六** | **七** | **八** | **九** | **十** | **总分** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **得 分** |  |  |  |  |  |  |  |  |  |  |  |
| **评卷人** |  |  |  |  |  |  |  |  |  |  |  |

1. Select the correct choice.        (20 scores, each 2 scores)

(1)  Pick the growth rate that corresponds to the most  inefficient algorithm as n gets large:  (        C      )

(A)  2n3                (B)  2n2logn                  (C) n!         (D) 2n

(2)  An algorithm must be or do all of the following EXCEPT:    (        B        )

(A)  Partially correct      (B)  Ambiguous      (C)  Can stop     (D)  Concrete steps

(3)  If a data element requires  6  bytes and a pointer requires  2  bytes, then a  linked  list representation will be more space efficient than a standard array representation when the fraction of non-null  elements is less than about:  (        B        )

(A)  1/4       (B)  3/4       (C)  4/7         (D)  2/3

(4)   Which statement is not correct among the following four:    (      C      )
- The Quick-sort is an unstable sorting algorithm.
- The number of empty sub-trees in a non-empty full binary tree is one more than the number of nodes in the tree.
- The  best  case for my algorithm is  n  becoming larger and larger  because that is the  most quickly.
- A cluster is the smallest unit of allocation for a file, so all files occupy a multiple of the  cluster  size.

(5)  Which of the following is a true statement:  (        C      )

(A)  A general tree can be  transferred  to a binary tree with the root having both left child and right child.

(B) In a BST,  the node can be  enumerated sorted by a preorder  traversal  to the BST.

(C) In a BST, the left child of any node is less than the right child, but in a heap, the left child of any node could be less than or greater than the right child.

(D)  A  heap  must be full binary tree.

(6)  The  golden rule of  a disk-based program  design  is to:  (      B        )

(A) Improve the basic  I/O  operations.          (B) Minimize the number of disk accesses.

(C) Eliminate the recursive calls.        (D) Reduce main memory use.

(7)  Given an array as  A[m] [n].  Supposed  that  *A*  [0] [0] is  located at  644(10)  and *A*  [2] [2] is  stored at  676(10), and every element occupies one space.  “(10)”  means that the number is presented in  decimals. Then the element  *A*  [1] [1](10)  is at position:

(        D      )

(A)  692    (B)  695    (C)  650    (D)  660

(8)  If there is 1MB working memory,  4KB blocks, and yield 128 blocks for working memory.  By the multi-way merge in external  sorting, the average run size  and the  sorted  size  in one pass  of multi-way  merge on average  are  separately  (        C      )?

(A)    1MB, 128 MB		         (B) 2MB, 512MB

(C)    2MB, 256MB				  	  (D)  1MB, 256MB

(9)  In the following sorting algorithms, which is the best one to find the first 10 biggest elements in the 1000 unsorted elements?    (      B      )

(A) Quick-sort       (B) Heap sort

(C  )  Insertion sort      (D) Replacement selection

(10)  Assume that we have eight records, with key values A to H, and that they are initially placed in alphabetical order. Now, consider the result of applying the following access pattern:  F D F G E G F A D F G E  if the list is organized by the  Move-to-front heuristic, then the final list will be (        B          ).
- F G D E A B C H                      (B) E G F D A B C H

(C) A B F D G E C H                      (D)  E G F A C B D H

2. Fill the blank with correct C++ codes:      (16 scores)

(1)      Given an array storing integers ordered by distinct value  without duplicate, modify the binary search routines to return the position of the integer with the  greatest value  less  than K when K itself does not appear in the array. Return ERROR if the  lest  value in the array is  greater  than K: (10 scores)

// Return position of  greatest element  <  K

int newbinary(int array[], int n, int K) {

int l = -1;

int r = n;             // l and r beyond array bounds

while (l+1 != r) {     // Stop when l and r meet

___ int i=（l+r）/2_____;          // Look at middle of subarray

if (K < array[i])    __ r=i ___;       // In left half

if (K == array[i])   return i ;    // Found it

if (K > array[i])        ___ l=i ___       // In right half

}

// K is not in array or the greatest value is less than K

if    K>  array[0]  （or  l!=  -1）// the  lest  value in the array is  greater  than K  with l updated

then                           return  l   ;   // when K itself does not appear in the array

else      return  ERROR;   // the integer with the  lest value  greater  than K

}

(2)

The number of nodes in a complete binary tree as big as possible with height h is  2h-1(suppose 1-node tree’s height is 1) (3  scores)

(3) The number of different shapes of binary trees with 6 nodes is  _132.  (3  scores)

3. A certain binary tree has the post-order enumeration as EDCBIHJGFA and the in-order enumeration as  EBDCAFIHGJ. Try to draw the binary tree and give the postorder enumeration. (The process of your solution is required!!!)  (6 scores)

preorder  enumeration:  ABECDFGHIJ

4. Determine Θ for the following code fragments in the average case. Assume that all variables are of type int.                            (6 scores)

(1) sum=0;

for (i=0; i<5; i++)

for (j=0; j<n; j++)

sum++;                solution : Θ___(n)_______

(2)  sum = 0;

for(i=1;i<=n;i++)

for(j=n;j>=i;j--)

sum++;                              solution : Θ__(n2)________

(3) sum=0;

if (EVEN(n))

for (i=0; i<n; i++)

sum++;

else

sum=sum+n;                          solution : Θ___(n)_____

5.  Show the min-heap that results from running buildheap on the following values stored in an array: 4, 2, 5, 8, 3, 6, 10, 14.                     (6 scores)

6. Design an algorithm to transfer the score report from 100-point to 5-point, the level E corresponding score<60, 60～69 being D, 70～79 being C, 80～89 as B，score>=90 as  A. The distribution table is as following. Please describe your algorithm using a decision tree and give the total path length. (9 scores)

| Score in 100-point | 0-59 | 60-69 | 70-79 | 80-89 | 90-100 |
|---|---|---|---|---|---|
| Distribution rate | 5% | 10% | 45% | 35% | 5% |

solution:

the design logic is to build a  Huffman  tree

Total length:  4 *  10%  +10%  *  3  +  15 %* 3 +  35%  *  2  +  45%		= 2.25, the 0-false,1-true as the logic branches.

7. Assume a disk drive is configured as follows. The total storage is approximately 675M divided among 15 surfaces. Each surface has 612 tracks; there are 144 sectors/track, 512 byte/sector, and 16 sectors/cluster. The interleaving factor is 3. The disk turns at 7200rmp (8.3ms/r). The track-to-track seek time is 20 ms, and the average seek time is 80 ms. Now how  long  does it take to read all of the data in a 360 KB file on the disk? Assume that the file’s clusters are spread randomly across the disk. A seek must be performed each time the I/O reader moves to a new track. Show your calculations.  (The process of your solution is required!!!)        (9 scores)

Solution：

A  cluster  holds 16*0.5K = 8K.   Thus, the file requires 360/8=45clusters.

The time to read a cluster is seek time to the  cluster+ latency time + (interleaf factor  ×  rotation time).Average seek time is defined to be 80 ms. Latency time is 0.5  *8.3,  and cluster rotation time is  3 * (16/144)*8.3.Seek time for the total file read time is

45* (80 + 0.5  * 8.3+ 3 * (16/144)*8.3 ) =  3911.25

8. Using closed hashing, with double hashing to resolve collisions, insert the following keys into a hash table of eleven slots (the slots are numbered 0 through 10). The hash functions to be used are H1 and H2, defined below. You should show the hash table after all eight keys have been inserted. Be sure to indicate how you are using H1 and H2 to do the hashing. ( The process of your solution is required!!!)

H1(k) = 3k mod 11        H2(k) = 7k mod 10+1

Keys: 22, 41, 53, 46, 30, 13, 1, 67.                            (9 scores)

Solution：

H1(22)=0, H1(41)=2, H1(53)=5, H1(46)=6, no conflict

When H1(30)=2, H2(30)=1    （2+1*1）%11=3，so 30 enters the 3rd slot;

H1(13)=6, H2(13)=2  (6+1*2)%11=8,  so 13 enters the 8th slot;

H1(1)=3, H2(1)=8  (3+5*8)%11= 10   so 1 enters 10 (pass by 0, 8, 5, 2 );

H1(67)=3, H2(67)=10   (3+2*10)%11= 1    so 67 enters 1(pass by 2)

| 22 | 67 | 41 | 30 |  | 53 | 46 |  | 13 |  | 1 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |

9. You are given a series of records whose keys are chars. The records arrive in the following order: C, S, D, T, A, M, P, I, B, W, N, G, U, R. Show the 2-3 tree that results from inserting these records.  （the process of your solution is required!!!） (9 scores)

Solution：

MS

BD           P          U

A  C  GI      N   R     T   W

10.

The following graph is a communication network in some area, whose edge presents the channel between two cities with the weight as the channel’s cost. How to choose the cheapest path that can connect all cities? And how to get cheapest  paths  connecting each city-pair? You can draw all choices if there  is  more than one path.  (10 scores)

Solution：

1,C to A: 4 (C,A);  CF: 5(C,F);  CD: 6(C,A,D);  CB: 12(C,A,D,B);

CG:11 (C,F,G);  CE: 13(C,A,D,B,E)

2.  Draw the MST:  It is a  Hamilton  path.
