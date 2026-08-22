---
source_id: data-structure-033
course_id: data_structure
title: BST
original_file: "学科资料/数据结构/作业集（压压压趣味赛）/data structure9-27/data structure9-27/BST.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# BST

```cpp
//#include <iostream>
//#include<sstream>
//
//using namespace std;
//
//class TreeNode {
//public:
//    int value;
//    TreeNode* left;
//    TreeNode* right;
//
//    TreeNode(int key) : value(key), left(nullptr), right(nullptr) {}
//};
//
//class BST {
//public:
//    TreeNode* root;
//
//    BST() : root(nullptr) {}
//
//    void insert(int key) {
//        if (root == nullptr) {
//            root = new TreeNode(key);
//        }
//        else {
//            insertRec(root, key);
//        }
//    }
//
//    int getHeight(TreeNode* node) {
//        if (node == nullptr) {
//            return 0; // Height of an empty tree is 0
//        }
//        // Recursively calculate the height of both subtrees
//        int leftHeight = getHeight(node->left);
//        int rightHeight = getHeight(node->right);
//        // Return the greater height plus one for the current node
//        return max(leftHeight, rightHeight) + 1;
//    }
//
//    void insertRec(TreeNode* node, int key) {
//        if (key < node->value) {
//            if (node->left == nullptr) {
//                node->left = new TreeNode(key);
//            }
//            else {
//                insertRec(node->left, key);
//            }
//        }
//        else if (key > node->value) {
//            if (node->right == nullptr) {
//                node->right = new TreeNode(key);
//            }
//            else {
//                insertRec(node->right, key);
//            }
//        }
//    }
//};
//
//int main() {
//    int T;
//    cin >> T;
//    cin.ignore();
//    for (int i = 0; i < T; ++i) {
//        string input;
//        getline(cin, input); // Read the entire line of input
//
//        BST bst; // Create a new BST for this test case
//        stringstream ss(input);
//        int number;
//
//        // Insert each number from the input into the BST
//        while (ss >> number) {
//            bst.insert(number);
//        }
//
//        // Calculate the height of the BST
//        int height = bst.getHeight(bst.root);
//        cout << height << endl; // Output the height
//    }
//
//
//    return 0;
//}

```
