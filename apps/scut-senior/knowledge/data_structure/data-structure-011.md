---
source_id: data-structure-011
course_id: data_structure
title: "2012数据结构试卷A及答案"
original_file: "学科资料/数据结构/往年卷/2012数据结构试卷A及答案.doc"
document_role: past_exam_answer
year: 2012
locator_type: none
---

# 2012数据结构试卷A及答案

**诚信应考,考试作弊将带来严重后果！**

**华南理工大学期末考试**

**《**  **Data Structure**  **》A试卷**

**注意事项：1.** **考前请将密封线内填写清楚；**

**2.** **所有答案请直接答在试卷上；**

**3．考试形式：闭卷；**

**4.** **本试卷共十大题，满分100分，考试时间120分钟**。

| **题 号** | **一** | **二** | **三** | **四** | **五** | **六** | **七** | **八** | **九** | **十** | **总分** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **得 分** |  |  |  |  |  |  |  |  |  |  |  |
| **评卷人** |  |  |  |  |  |  |  |  |  |  |  |

1. Select the correct choice.        (20 scores, each 2 scores)

(1)  An algorithm must be or do all of the following EXCEPT:    (   B   )

(A)  Partially correct      (B)  Infinite   (C)  No Ambiguous      (D)  Concrete steps

(2)  Pick the growth rate that corresponds to the  slowest growing  algorithm as n gets larger:  (    D    )

(A)  4n3                (B)  2n                 (C)  3n!         (D)  50n2logn

(3)  If a data element requires  8  bytes and a pointer requires  4  bytes, then a  linked  list representation will be more space efficient than a standard array representation when the fraction of non-null  elements is less than about:  (    B    )

(A)  1/4       (B)  2/3       (C)  3/5          (D)  3/4

(4)   Which is the realization of a data type as a software component:  (   A   )

(A) An abstract data type      (B) A real data type

(C) A type                  (D)A data structure

(5)  We use the parent pointer representation for general trees to solve  (C)  problem?

(A)  Shortest paths                                    (B) General tree traversal

(C) Equivalence classes                            (D) Exact-match query

(6)  The most effective way to reduce the time required by a disk-based program is to:  (   D    )

(A) Improve the basic  I/O  operations.        (B) Reduce main memory use.

(C) Eliminate the recursive calls.       (D) Minimize the number of disk accesses.

<!-- question: data-structure-011-Q1 -->

(7)  In the hash function, collision refers to (   B     ).

(A) Two elements have the same  key value.

(B) Different keys are mapped to the same  position  of hash table.

(C) Two records have the same requiring  number.

(D) Data elements are too much.

(8)  Given an array as  A[m][n].  Supposed  that  *A*[0][0]is located at  644(10)  and *A*[4][4]is stored at  676(10), and every element occupies one space.  “(10)”  means that the number is presented in  decimals. Then the element  *A*[3][3](10)  is at position:

(        B        )

(A)  692    (B)  668    (C)  650    (D)  708

(9) Which statement is not correct among the following four:    (        A      )
- The number of empty sub-trees in a non-empty binary tree is one less than the number of nodes in the tree.
- The  Mergesort  is a stable sorting algorithm.
- The root of a binary tree  transferred  from a general tree has only left child.
- A sector is the smallest unit of allocation for a record, so all records occupy a multiple of the sector size.

(10) Assume that we have eight records, with key values A to H, and that they are initially placed in alphabetical order. Now, consider the result of applying the following access pattern:  F D F G E G F A D F G E  if the list is organized by the transpose  heuristic, then the final list will be (    B     ).
- A F C D H G E B                      (B)  A B F D G E C H

(C) A B F G D C E H                      (D)  A H F D G E C B

<!-- question: data-structure-011-Q2 -->

2. Fill the blank with correct C++ codes:    (18 scores)
1. Given an array storing integers ordered by value, modify the binary search routines to return the position of the first integer with the least value greater than K when K itself does not appear in the array. Return ERROR if the greatest value in the array is less than K:  (14 scores)

// Return position of  lest element  >= K

int newbinary(int array[], int n, int K) {

int l = -1;

int r = n;             // l and r beyond array bounds

while (l+1 != r) {     // Stop when l and r meet

___  int i=（l+r）/2_____;          //  Check  middle of  remaining  subarray

if (K < array[i])        __  r=i  ___;       // In left half

if (K == array[i])      __  return  i ___;        // Found it

if (K > array[i])        ___  l=i  ___              // In right half

}

//  K is  not in array  or the greatest value is less than K

if      K< array[n-1]  or r!=n

then   return   r;      //  the first integer with the least value greater than K // when K itself does not appear in the array

else      return    ERROR;   // the greatest value in the array is less than K

}

(2)

The height of the shortest tree and the tallest tree with both n nodes is respectively  _2_or n(n<2)    and  __n_  , suppose that the height of the one-node tree is 1 ( 4 scores)

3. Please calculate the number of binary trees in  different  shape with 5 nodes in total, and 6 nodes? (4 scores)

5:42, 6:132,    C2nn/n+1

4.  A certain binary tree has the preorder enumeration as  ABCDFEGIHJ  and the inorder enumeration as  BCDAEFGHIJ. Try to draw the binary tree and give the postorder enumeration. (The process of your solution is required!!!)  (6 scores)

Postorder  enumeration: DCBEHJIGFA

5.  Trace by hand the execution of Radix-sort algorithm on the array: int a[] = {265 301 751 129 937 863 742 694 076 438}.    (6 scores)

initial:    265 301 751 129 937 863 742 694 076 438

pass 1:  [] [301 751] [742] [863] [694] [265] [076] [937] [438] [129]

pass 2:  [301] [] [129] [937 438] [742] [751] [863 265] [076] [] [694]

pass 3:  [075] [129] [265] [301] [438] [] [694] [742 751] [863] [937]

final sorted array: 075 129 265 301 438 694 742 751 863 937

6. (a) Describe simply the main tasks of the  two phases  of  external sorting. (4 scores)The task of first phase is to break the files into large initial runs  by replacement  selection; the second phase is to merge  the runs together to form a single sorted run file.(b)Assume that  working memory is 256KB  broken into blocks of 8192 bytes (there is also additional space available for I/O buffers, program variables, etc.) What is the expected size for the largest file that can be merged using replacement selection followed by two passes of multi-way merge? Explain how you got your answer. (4 scores)

Since working memory is 256KB and the blocksize is 8KB, the working memory holds 32 blocks. The expected runlength is 512KB, so a single pass of multiway merge forms runs of length  512KB*32=16MB. The second pass then forms a run as large as 16MB*32=512MB.

7. Assume a disk drive is configured as follows. The total storage is approximately 675M divided among 15 surfaces. Each surface has 612 tracks; there are 144 sectors/track, 512 byte/sector, and 16 sectors/cluster. The interleaving factor is 3. The disk turns at 7200rmp (8.3ms/r). The track-to-track seek time is 20 ms, and the average seek time is 80 ms. Now how  long  does it take to read all of the data in a 360 KB file on the disk? Assume that the file’s clusters are spread randomly across the disk. A seek must be performed each time the I/O reader moves to a new track. Show your calculations.  (The process of your solution is required!!!)        (8cores)

A  cluster  holds 16*0.5K = 8K.   Thus, the file requires 360/8=45clusters.

The time to read a cluster is seek time to the  cluster+ latency time + (interleaf factor  ×  rotation time).Average seek time is defined to be 80 ms. Latency time is 0.5  *8.3,  and cluster rotation time is  3 * (16/144)*8.3.Seek time for the total file read time is

45* (80 + 0.5  * 8.3+ 3 * (16/144)*8.3 ) =  3911.25

8. Using closed hashing, with double hashing to resolve collisions, insert the following keys into a hash table of eleven slots (the slots are numbered 0 through 10). The hash functions to be used are H1 and H2, defined below. You should show the hash table after all eight keys have been inserted. Be sure to indicate how you are using H1 and H2 to do the hashing. ( The process of your solution is required!!!)

H1(k) = 3k mod 11        H2(k) = 7k mod 10+1

Keys: 22, 31, 19, 35, 41, 13, 1, 67.                            (8 scores)

Answer:

H1(22)=0, H1(31)=5, H1(19)=2, H1(35)=6, no conflict

When H1(41)=2, H2(41)=8  （2+8*1）%11=10，so 41 enters the 10rd  slot;

H1(13)=6, H2(13)=2  (6+1*2)%11=8,  so 13 enters the 8th  slot;

H1(1)=3, so 1 enters 3 ;

H1(67)=3, H2(67)=10   (3+2*10)%11= 1  so 67 enters 1(pass by 2)

9.. Converting from a general tree to a binary tree.      (4 scores)

10.

Figure 1 Example graph

(a) Draw the adjacency matrix representation and adjacency list representation for the graph of the figure-1. (6)

(b)  Use  Dijkstra’s Algorithm  to find the shortest paths from  Vertex1  to all the other vertices. (6)

(c)  Use Kruskal’s algorithm to find the minimum-cost spanning tree.  (4)

(a) adjacency matrix

1   2   3   4   5   6

--------------------------

1 |    10      20     2     |

2 | 10      3   5           |

3 |     3          15        |

4 | 20 5         11 10    |

5 |        15 11      3    |

6 | 2         10   3        |

--------------------------

adjacency list:

1 -> 2(10) -> 4(20) -> 6(2) -> \

2 -> 1(10) -> 3(3) -> 4(5) -> \

3 -> 2(3) -> 5(15) -> \

4 -> 1(20) -> 2(5) -> 5(11) -> 6(10) -> \

5 -> 3(15) -> 4(11) -> 6(3) -> \

6 -> 1(2) -> 4(10) -> 5(3) -> \

(b)  1 to 2: 10 (1,2);

1 to 3: 13(1,2,3);

1 to 4: 12 (1,6,4);

1 to 5: 5 (1,6,5);

1 to 6: 2 (1,6,);

(c)
