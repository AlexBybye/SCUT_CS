---
source_id: data-structure-021
course_id: data_structure
title: "2024-B-数据结构"
original_file: "学科资料/数据结构/往年卷/2024-B-数据结构.doc"
document_role: note
year: 2024
locator_type: none
---

# 2024-B-数据结构

**WARNING: MISBEHAVIOR AT EXAM TIME WILL LEAD TO SERIOUS CONSEQUENCE.**

**SCUT Final Exam**

**Data Structure Exam Paper** **B** **(2024-2025-1)**

**Notice:     1. Make sure that you have filled the form on the left side of seal line.**

**2. Write your answers on the exam paper .**

**3. This is a close-book exam.**

**4. The exam with full score of 100 points lasts 120 minutes.**

| **Question No.** | **I** | **II** | **III** | **IV** | **Sum** |
|---|---|---|---|---|---|
| **Score** |  |  |  |  |  |

**I. Select the correct choice.   (10 points)**
1. In a doubly - linked list, if we have a node structure with pointers 'prev' and 'next', and we want to insert a new node 'newNode' between two existing nodes 'nodeA' and 'nodeB' (where 'nodeA' is before 'nodeB'). What is the correct sequence of operations to achieve this?  (A) newNode->next = nodeA; newNode->prev = nodeB; nodeA->prev = newNode; nodeB->next = newNode; (B) nodeA->next = newNode; newNode->prev = nodeA; newNode->next = nodeB; nodeB->prev = newNode; (C) nodeB->prev = newNode; newNode->next = nodeB; newNode->prev = nodeA; nodeA->next = newNode;
- newNode->prev = nodeA; newNode->next = nodeB; nodeA->next = newNode; nodeB->prev = newNode;
1. In a binary search tree, the following nodes are inserted in the order: 5, 3, 7, 2, 4, 6, 8. After all insertions, what is the in-order traversal of the tree?  (A)5, 3, 2, 4, 7, 6, 8 	(B) 2, 3, 4, 5, 6, 7, 8	(C) 8, 7, 6, 5, 4, 3, 2	(D) 3, 2, 4, 5, 7, 6, 8
1. In a full binary tree, if the number of leaf nodes is 32, what is the total number of nodes in the tree?  (A) 61	(B) 62	(C) 63	(D) 64

(4)In a weighted graph, we want to find the minimum spanning tree using Kruskal's algorithm. The graph has the following edges and weights: (A, B, 3), (A, C, 4), (B, C, 2), (B, D, 5), (C, D, 6). Which edge will be the third one added to the minimum spanning tree?  (A) (A, B, 3)	(B) (A, C, 4)	(C) (B, D, 5)	(D) (C, D, 6)

(5)When using the Insertion Sort algorithm, we have an array  A=[5,3,4,6,2]. After the third iteration (when the element  is being inserted), what does the array  look like? (A) [3, 4, 5, 2, 6] 	(B)[3, 4, 5, 6, 2]	(C) [3, 5, 4, 6, 2]	(D) [2, 3, 4, 5, 6]

**II. Fill in the blanks.  (10 points)**
1. There are_____________nodes  in  a  full binary tree with  *n*  leaf nodes.
1. In a linked list with n nodes, if we want to reverse the order of the first m nodes (m  ≤ n), the time complexity is  _____________.
1. If the post-order traversal of a binary tree is  DECBFA and the in-order traversal is DBCEAF, then the pre-order traversal of this tree is  _________.
1. When using the Insertion Sort algorithm to sort an array with n elements, the number of comparisons in the best case is  _________.
1. G is an undirected graph  with  2024 nodes. G has two connected components and each one is a tree. The number of edges in G is  _________.

**III  Application of Data Structure** **（60 points, 10 points each）**

1.  Determine Θ for the following code fragments in the average case. Assume that all variables are of type int.

(a) The  time cost of the  code fragments  is  Θ(_______)  .

int sum = 0;

int n;

cin >> n;

for (int i = 1; i <= n; i++) {

for (int j = 1; j <= n; j++) {

for (int k = 1; k <= i * j; k++) {

sum++;

}

}

}

(b)  The  time cost of the  code fragments  is  Θ(_______)  .

int sum = 0;

int n;

cin >> n;

for (int i = 0; i < n; i++) {

for (int j = 0; j < n * n; j++) {

for (int k = 0; k < j; k++) {

sum++;

}

}

}

(c)  The  time cost of the  code fragments  is  Θ(_______)  .

int sum = 0;

int n;

cin >> n;

for (int i = 1; i <= n; i *= 2) {

for (int j = 1; j <= n; j *= 3) {

for (int k = 1; k <= n; k++) {

sum++;

}

}

}
1. Given a set of numbers to be inserted into a binary search tree: 50, 30, 20, 40, 70, 60, 80, 90, 10, 15.

(1) Insert the numbers into the binary search tree and show the final tree structure.

(2) Delete the node with value 40 from the binary search tree and show the steps and resulting tree structure.

3.Consider a hash table of size 15 with a hash function h(x)=(5x+3)%10. The following keys need to be inserted: 23, 31, 42, 57, 68, 73, 85, 94, 106, 112. The quadratic probing ( p(k,i) = i2  )is used as collision resolution.
1. Show the state of the hash table after all insertions.
1. Search for the key 94 and describe the search process step by step, including the number of probes made.

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |

4. Given a weighted undirected graph G=(V, E) where V={v1, v2, v3, v4, v5, v6, v7, v8} and E={(v1, v2, 3), (v1, v3, 5), (v2, v4, 7), (v2, v5, 4), (v3, v6, 6), (v3, v7, 9), (v4, v8, 2),(v5, v6, 1),(v6,v7,2),(v6,v8,3)}

(1) Draw the adjacency list of the graph.

(2) Use Dijkstra's algorithm to find the shortest path from v1 to other nodes.

(3) Show the MST (Minimum Spanning Tree) of G using  Kruskal’s MST algorithm.
1. Given a set of keys to be inserted into a 2-3 tree: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120.

(1) Insert the keys one by one into the 2-3 tree and show the structure of the tree after each insertion.

(2)Search for the key 120 in the tree and describe the search path and the number of comparisons made.
1. Given the general tree, whose pre-order sequential representation is: AB)D)E)G)H)I))C)F))  (‘)’ indicates the end of a subtree)

(1) Draw the general tree.

(2) Show the post-order traversal results of the tree.

(3)Convert the general tree to a binary tree using the  left  child-right  sibling representation.

**IV. Design of Algorithm.        (20 points,** **10 points each)**

1.  Write a function named findShortestPath that finds the shortest path between two vertices in an unweighted undirected graph. The graph is represented using an adjacency matrix-like structure where we have a 2D array of integers. A value of  1  in the array at position  [i][j]  indicates an edge between vertex  i  and vertex  j  (and since it's undirected,  [j][i]  is also  1  if there's an edge), and  0  indicates no edge. Here are the structure definitions:

const int MAX_VERTICES = 100;

class Graph {

private:

int adjMatrix[MAX_VERTICES][MAX_VERTICES];

int numVertices;

public:

Graph(int numVertices) {

this->numVertices = numVertices;

for (int i = 0; i < numVertices; i++) {

for (int j = 0; j < numVertices; j++) {

adjMatrix[i][j] = 0;

}

}

}

void addEdge(int from, int to) {

adjMatrix[from][to] = 1;

adjMatrix[to][from] = 1;

}

// Function prototype for finding the shortest path

int* findShortestPath( int source, int destination){

//to do ...

}

};

Your findShortestPath function should take the index of the source vertex  source, and the index of the destination vertex  destination  as parameters. It should return an array representing the shortest path from the source to the destination (where the first element is the source vertex and the last element is the destination vertex). If there is no path between the two vertices, the function should return  NULL. The function should use an appropriate algorithm (such as breadth-first search) to find the shortest path.

2.Write a function named mergeSortLinkedList that sorts a singly linked list using the merge sort algorithm. The linked list node structure is defined as follows:

template <class Elem>class ListNode {public:

Elem data;

ListNode* next;

ListNode(const Elem& value) : data(value), next(nullptr) {}};

template <class Elem>

ListNode<Elem>* mergeSortLinkedList(ListNode<Elem>* head);

Your  mergeSortLinkedList  function should take the head pointer of the singly linked list as input. It should recursively split the list into two halves, sort each half, and then merge them back together to form the sorted list. The sorting should be done in-place (without using additional data structures like arrays to store the entire list elements). Return the pointer to the head of the sorted linked list.
