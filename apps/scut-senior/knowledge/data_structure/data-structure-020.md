---
source_id: data-structure-020
course_id: data_structure
title: "2024-A-数据结构"
original_file: "学科资料/数据结构/往年卷/2024-A-数据结构.doc"
document_role: note
year: 2024
locator_type: none
---

# 2024-A-数据结构

**WARNING: MISBEHAVIOR AT EXAM TIME WILL LEAD TO SERIOUS CONSEQUENCE.**

**SCUT Final Exam**

**Data Structure Exam Paper A (2024-2025-1)**

**Notice:     1. Make sure that you have filled the form on the left side of seal line.**

**2. Write your answers on the exam paper .**

**3. This is a close-book exam.**

**4. The exam with full score of 100 points lasts 120 minutes.**

| **Question No.** | **I** | **II** | **III** | **IV** | **Sum** |
|---|---|---|---|---|---|
| **Score** |  |  |  |  |  |

**I. Select the correct choice.   (10 points)**

(1)  In a circular queue with an array of size 6, the front pointer initially points to the 2nd position and the rear pointer points to the 4th position. After enqueueing two elements and then dequeueing one element, where do the front and rear pointers point respectively (assuming the indexing starts from 0)? 	 	(A) Front at 3rd position, Rear at 6th position 	(B) Front at 3rd position, Rear at 0th position 	(C) Front at 1st position, Rear at 5th position 	(D) Front at 0th position, Rear at 4th position

(2)  We are given a stack operation sequence: push(1), push(2), pop(), push(3), push(4), pop(), pop(). What is the value of the top element of the stack after these operations? 	 	(A) 1			(B) 3			(C) None (stack is empty)		(D) 4

(3)  In a binary tree, the number of nodes  having 2 children  is  n2, the number of nodes having 1  child is n1 , and the number of leaf nodes is n0. Which of the following equations always holds true for a binary tree? 	(A) n0 = n2+1		(B) n1=n2+1		(C) n0=n1+1		(D) n0=n1=n2

(4)  In a simple graph G=(V,E), the degree of each vertex is at least 3. If |V|=n, what is a lower bound for  |E| (the number of edges)? 	(A) n-3			(B) n/3			(C) 3n			(D) 3n/2

(5)  When using the Heap Sort algorithm to sort an array of  elements, what is the time complexity of building the initial heap? (	A) O(n)			(B) O(nlogn)		(C)O(logn)		(D)O(n2)

**II. Fill in the blanks.  (10 points)**
1. The time complexity of searching for an element in a sorted linked list is    _______.
1. For a complete binary tree with height h, the number of nodes  is  ___________.
1. If the pre-order traversal result of a binary tree is EFHGJI and the in-order traversal result is FEGHIJ, then the height of the tree is ______.
1. When using the Quick Sort algorithm to sort an array with n  elements, the number of swaps in the worst case is    Ө（______）
1. Given an directed graph  and we want to check if the graph has cycles, we can use _______________________ algorithm.

**III  Application of Data Structure** **（60 points, 10 points each）**

1.  Determine Θ for the following code fragments in the average case. Assume that all variables are of type int.

(a) The  time cost of the  code fragments  is  Θ(_______)  .

int sum = 0;

int n;

cin >> n;

for (int i = 0; i < n; i++) {

for (int j = 1; j < n * n; j *= 4) {

sum++;

}

}

(b)  The  time cost of the  code fragments  is  Θ(_______)  .

int sum = 0;

int n;

cin >> n;

for (int i = 0; i < n * n; i++) {

if (i % 5 == 0) {

for (int j = 0; j < i; j++) {

sum++;

}

} else {

for (int k = 0; k < n; k++) {

sum += n;

}

}

}

(c) The  time cost of the  code fragments  is  Θ(_______)

int sum = 0;

int n;

cin >> n;

for (int i = 0; i < n; i++) {

for (int j = 0; j < i; j++) {

for (int k = 0; k < n * n; k++) {

sum++;

}

}

}

2.Given the characters and their frequencies as follows: 'a' (10), 'b' (15), 'c' (20), 'd' (30), 'e' (35), 'f' (40), 'g' (50), 'h' (60).

(1) Construct the Huffman tree and clearly label the frequencies on each node.

(2) Derive the Huffman codes for all the characters.

(3) If a message contains n characters with the given frequency distribution, calculate the total number of bits required to encode the message using the Huffman codes and compare it with the number of bits required if using a fixed-length code .

3.  Consider a hash table of size 10 with a hash function h(x)=(3x+5)%10. The following keys need to be inserted: 12, 25, 37, 49, 52, 64, 76, 88, 91, 103. The linear probing is used as collision resolution.

(1) Show the final state of the hash table after all insertions using linear probing.

(2) Search for the key 91 and describe the process step by step, including the number of probes made.

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |

1. Given a directed graph  G=(V,E) where  V={v1, v2, v3, v4, v5, v6, v7, v8, v9, v10} and E={(v1, v2), (v1, v3), (v2, v4), (v2, v5), (v3, v6), (v3, v7), (v4, v8), (v5, v9), (v6, v10), (v7, v10), (v8, v9), (v9, v10)}.
1. Draw the graph with proper arrow directions.
1. Show the BFS Tree of the graph (traversal starting from v1).

(3) Perform a topological sort on the graph and show one possible valid topological orderings.
1. Given an array [15, 9, 25, 7, 30, 12, 35, 5, 40, 3, 45, 1, 50, 2, 55], sort the array using Heap Sort. Show the the heap-building process and the steps of swapping elements during the sorting process.
1. Given a binary tree where the pre-order traversal is "ABDECFGHIJKLMNO" and the in-order traversal is "DBEAFCGHIKJLNMO".

(1) Draw the binary tree.

(2) Perform a level-order traversal of the tree and display the result.

**IV. Design of Algorithm.        (20 points,** **10 points each)**

1.  Write a function named countLeaves that, given the root of a binary tree (not necessarily a binary search tree), counts and returns the number of leaf nodes in the tree. A leaf node is a node that has no children. The binary tree node class is defined as follows:

template  <class Elem>  class BinNode {

public:

virtual Elem& val( ) = 0;

virtual void setVal( const Elem& ) = 0;

virtual BinNode* left( ) const = 0;

virtual void setLeft( BinNode* ) = 0;

virtual BinNode* right( ) const = 0;

virtual void setRight( BinNode* ) = 0;

virtual bool isLeaf( ) = 0;};

template <class Elem>

int countLeaves(BinNode<Elem>* root);

Your implementation of countLeaves should use a recursive approach to traverse the tree and correctly count the leaf nodes.

2.Write a function named insertionSortLinkedList that sorts a singly linked list using the insertion sort algorithm. The linked list node structure is defined as follows:

template <class Elem> class ListNode {

public:

Elem data;

ListNode* next;

ListNode(const Elem& value) : data(value), next(nullptr) {}

};

template <class Elem>

void insertionSortLinkedList(ListNode<Elem>* head);

Your insertionSortLinkedList function should take the head pointer of the singly linked list as input and sort the list in-place (i.e., without using additional data structures like arrays).

s
