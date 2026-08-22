---
source_id: data-structure-034
course_id: data_structure
title: "print a tree"
original_file: "学科资料/数据结构/作业集（压压压趣味赛）/data structure9-27/data structure9-27/print a tree.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# print a tree

```cpp
//#include <iostream>
//#include <queue>
//#include <string>
//#include <vector>
//using namespace std;
//struct TreeNode//���ڵ�
//{
//    char value;//ֵ
//    TreeNode* left;//����
//    TreeNode* right;//�Һ���
//
//    TreeNode(char val) : value(val), left(nullptr), right(nullptr) {}
//};
//
//TreeNode* buildTree(const string& preorder, int& index) //ǰ�������������
//{
//    if (index >= preorder.length()) return nullptr;
//
//    TreeNode* node = new TreeNode(preorder[index++]);
//
//    if (islower(node->value)) {
//        node->left = buildTree(preorder, index);
//        node->right = buildTree(preorder, index);
//    }
//
//    return node;//������
//}
////ˮƽ��ӡ��
//void printLevelOrder(TreeNode* root) {
//    if (!root) return;
//
//    queue<TreeNode*> q;
//    q.push(root);
//
//    while (!q.empty()) {
//        int levelSize = q.size();
//        for (int i = 0; i < levelSize; ++i) {
//            TreeNode* node = q.front();
//            q.pop();
//            cout << node->value;
//
//            // Push left and right children (if they exist)
//            if (node->left) q.push(node->left);
//            if (node->right) q.push(node->right);
//        }
//    }
//    cout << endl;
//}
//
//int main() {
//    int T;
//    cin >> T;  // Read number of test cases
//    cin.ignore();  // To ignore the newline after the integer input
//
//    for (int i = 0; i < T; ++i) {
//        string preorder;
//        getline(cin, preorder);  // Read the preorder traversal string
//
//        int index = 0;
//        TreeNode* root = buildTree(preorder, index); // Build the tree
//        printLevelOrder(root); // Print the tree level-wise
//
//    }
//
//    return 0;
//}

```
