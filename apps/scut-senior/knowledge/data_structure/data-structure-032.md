---
source_id: data-structure-032
course_id: data_structure
title: "BST operation"
original_file: "学科资料/数据结构/作业集（压压压趣味赛）/data structure9-27/data structure9-27/BST operation.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# BST operation

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <queue>
#include <algorithm>

using namespace std;

struct treenode {
    int val;
    treenode* left;
    treenode* right;
    treenode(int x) : val(x), left(nullptr), right(nullptr) {}
};

treenode* insertbst(treenode* root, int val) {
    if (!root) return new treenode(val);
    if (val < root->val) {
        root->left = insertbst(root->left, val);
    }
    else {
        root->right = insertbst(root->right, val);
    }
    return root;
}

treenode* buildbstfromlevelorder(const vector<string>& levelorder) {
    treenode* root = nullptr;
    for (const string& value : levelorder) {
        if (value != "n") { // 'n'��ʾ�սڵ�
            root = insertbst(root, stoi(value));
        }
    }
    return root;
}

void postordertraversal(treenode* root, vector<int>& result) {
    if (!root) return;
    postordertraversal(root->left, result);
    postordertraversal(root->right, result);
    result.push_back(root->val);
}

void inordertraversal(treenode* root, vector<int>& result) {
    if (!root) return;
    inordertraversal(root->left, result);
    result.push_back(root->val);
    inordertraversal(root->right, result);
}

int main() {
    int t;
    cin >> t;
    cin.ignore(); // ���Ի��з�

    while (t--) {
        string levelorderline;
        getline(cin, levelorderline);
        vector<string> levelorder;
        stringstream ss(levelorderline);
        string token;
        while (ss >> token) {
            levelorder.push_back(token);
        }

        int k;
        cin >> k;
        cin.ignore(); // ���Ի��з�

        // ���� bst
        treenode* bstroot = buildbstfromlevelorder(levelorder);

        // �������
        vector<int> postorderresult;
        postordertraversal(bstroot, postorderresult);

        // �������
        vector<int> inorderresult;
        inordertraversal(bstroot, inorderresult);

        // ������
        for (size_t i = 0; i < postorderresult.size(); ++i) {
            cout << postorderresult[i];
            if (i < postorderresult.size() - 1) cout << " ";
        }
        cout << endl;

        cout << inorderresult[k - 1] << endl; // ����� k С��Ԫ��
    }

    return 0;
}

```
