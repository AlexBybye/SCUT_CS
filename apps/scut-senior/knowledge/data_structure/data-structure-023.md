---
source_id: data-structure-023
course_id: data_structure
title: "作业及分析"
original_file: "学科资料/数据结构/作业集（压压压趣味赛）/作业及分析.txt"
document_role: note
year: 
locator_type: none
---

# 作业及分析

```text
recursive and non-recursive methods used in-order traversal binary trees：

递归中序遍历：
#include <iostream>
using namespace std;
struct TreeNode//建立一棵树
 {
    int value;
    TreeNode* left;
    TreeNode* right;
    
    TreeNode(int val) : value(val), left(nullptr), right(nullptr) {}
};

void inOrderRecursive(TreeNode* node)//遍历 {
    if (node != nullptr) {
        inOrderRecursive(node->left);
        cout << node->value << " ";
        inOrderRecursive(node->right);
    }
}
非递归方法：（学习一下）我们可以采用建立一个栈
#include <stack>

void inOrderIterative(TreeNode* root) //栈的二叉树中序遍历
{
    stack<TreeNode*> s;
    TreeNode* current = root;

    while (!s.empty() || current != nullptr) {
        while (current != nullptr) {
            s.push(current);
            current = current->left;
        }
        
        current = s.top();
        s.pop();
        cout << current->value << " ";
        current = current->right;
    }
}

我打算用数组建立一个平衡二叉树

TreeNode* insertLevelOrder(int arr[], TreeNode* root, int i, int n) {
    if (i < n) {
        TreeNode* temp = new TreeNode(arr[i]);
        root = temp;

        root->left = insertLevelOrder(arr, root->left, 2 * i + 1, n);
        root->right = insertLevelOrder(arr, root->right, 2 * i + 2, n);
    }
    return root;
}
时间复杂度测量：（这里是一点不会，用GPT直接帮我全写了）
We'll use the chrono library to measure execution time.
cpp
#include <chrono>

int main() {
    int arr[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}; // Example dataset
    int n = sizeof(arr) / sizeof(arr[0]);
    TreeNode* root = insertLevelOrder(arr, nullptr, 0, n);

    // Measure recursive in-order traversal time
    auto start = chrono::high_resolution_clock::now();
    cout << "Recursive In-Order Traversal: ";
    inOrderRecursive(root);
    auto end = chrono::high_resolution_clock::now();
    cout << "\nTime taken (Recursive): " 
         << chrono::duration_cast<chrono::microseconds>(end - start).count() << " microseconds\n";

    // Measure non-recursive in-order traversal time
    start = chrono::high_resolution_clock::now();
    cout << "Non-Recursive In-Order Traversal: ";
    inOrderIterative(root);
    end = chrono::high_resolution_clock::now();
    cout << "\nTime taken (Non-Recursive): " 
         << chrono::duration_cast<chrono::microseconds>(end - start).count() << " microseconds\n";

    return 0;
}

综合起来整体代码如下：
#include <iostream>
#include <stack>
#include <chrono>

using namespace std;

struct TreeNode {
    int value;
    TreeNode* left;
    TreeNode* right;
    
    TreeNode(int val) : value(val), left(nullptr), right(nullptr) {}
};

void inOrderRecursive(TreeNode* node) {
    if (node != nullptr) {
        inOrderRecursive(node->left);
        cout << node->value << " ";
        inOrderRecursive(node->right);
    }
}

void inOrderIterative(TreeNode* root) {
    stack<TreeNode*> s;
    TreeNode* current = root;

    while (!s.empty() || current != nullptr) {
        while (current != nullptr) {
            s.push(current);
            current = current->left;
        }
        
        current = s.top();
        s.pop();
        cout << current->value << " ";
        current = current->right;
    }
}

TreeNode* insertLevelOrder(int arr[], TreeNode* root, int i, int n) {
    if (i < n) {
        TreeNode* temp = new TreeNode(arr[i]);
        root = temp;

        root->left = insertLevelOrder(arr, root->left, 2 * i + 1, n);
        root->right = insertLevelOrder(arr, root->right, 2 * i + 2, n);
    }
    return root;
}

int main() {
    int arr[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}; // Example dataset
    int n = sizeof(arr) / sizeof(arr[0]);
    TreeNode* root = insertLevelOrder(arr, nullptr, 0, n);

    // Measure recursive in-order traversal time
    auto start = chrono::high_resolution_clock::now();
    cout << "Recursive In-Order Traversal: ";
    inOrderRecursive(root);
    auto end = chrono::high_resolution_clock::now();
    cout << "\nTime taken (Recursive): " 
         << chrono::duration_cast<chrono::microseconds>(end - start).count() << " microseconds\n";

    // Measure non-recursive in-order traversal time
    start = chrono::high_resolution_clock::now();
    cout << "Non-Recursive In-Order Traversal: ";
    inOrderIterative(root);
    end = chrono::high_resolution_clock::now();
    cout << "\nTime taken (Non-Recursive): " 
         << chrono::duration_cast<chrono::microseconds>(end - start).count() << " microseconds\n";

    return 0;
}
分析：

递归：好处是代码简单逻辑清晰，坏处是占用栈内存大，可能溢出。
非递归：好处是占用内存少，毕竟就一个栈，但是肉眼可见代码复杂度很高，逻辑要求不低。

综上所述我认为：递归可以用于少量数据，毕竟十分简单易操作，而栈的方法可以用于冗大复杂结构二叉树计算。
```
