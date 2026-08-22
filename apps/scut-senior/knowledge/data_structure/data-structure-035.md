---
source_id: data-structure-035
course_id: data_structure
title: "000"
original_file: "学科资料/数据结构/作业集（压压压趣味赛）/TEST/TEST/000.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# 000

```cpp
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
    int arr[200000] = {}; // Example dataset
    for (int i = 0; i < 200000; i++)
    {
        arr[i] = i;
    }
    int n = sizeof(arr) / sizeof(arr[0]);
    TreeNode* root = insertLevelOrder(arr, nullptr, 0, n);

    // Measure recursive in-order traversal time
    auto start = chrono::high_resolution_clock::now();
    cout << "Recursive In-Order Traversal: ";
    inOrderRecursive(root);
    auto end = chrono::high_resolution_clock::now();
    cout << "\nTime taken (Recursive): "
        << chrono::duration_cast<chrono::microseconds>(end - start).count() << " microseconds\n";

   /*  Measure non-recursive in-order traversal time*/
   //auto start = chrono::high_resolution_clock::now();
   // cout << "Non-Recursive In-Order Traversal: ";
   // inOrderIterative(root);
   //auto end = chrono::high_resolution_clock::now();
   // cout << "\nTime taken (Non-Recursive): "
   //     << chrono::duration_cast<chrono::microseconds>(end - start).count() << " microseconds\n";

    return 0;
}

```
