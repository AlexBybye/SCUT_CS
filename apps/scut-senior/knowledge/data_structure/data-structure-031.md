---
source_id: data-structure-031
course_id: data_structure
title: "BST OOperation"
original_file: "学科资料/数据结构/作业集（压压压趣味赛）/data structure9-27/data structure9-27/BST OOperation.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# BST OOperation

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <sstream>
#include <string>
using namespace std;

// ����������ڵ�
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int x) : val(x), left(NULL), right(NULL) {}
};

// ���ݲ��������������������
TreeNode* buildBST(const vector<string>& levelOrder) {
    if (levelOrder.empty() || levelOrder[0] == "n") return NULL;

    TreeNode* root = new TreeNode(stoi(levelOrder[0]));
    queue<TreeNode*> q;
    q.push(root);

    size_t i = 1;
    while (!q.empty() && i < levelOrder.size()) {
        TreeNode* current = q.front();
        q.pop();

        // ���ӽڵ�
        if (levelOrder[i] != "n") {
            current->left = new TreeNode(stoi(levelOrder[i]));
            q.push(current->left);
        }
        i++;

        // ���ӽڵ�
        if (i < levelOrder.size() && levelOrder[i] != "n") {
            current->right = new TreeNode(stoi(levelOrder[i]));
            q.push(current->right);
        }
        i++;
    }
    return root;
}

// �������
void postOrderTraversal(TreeNode* root, vector<int>& result) {
    if (!root) return;
    postOrderTraversal(root->left, result);
    postOrderTraversal(root->right, result);
    result.push_back(root->val);
}

// ���������ȡ�� k С��Ԫ��
void inOrderTraversal(TreeNode* root, vector<int>& sorted) {
    if (!root) return;
    inOrderTraversal(root->left, sorted);
    sorted.push_back(root->val);
    inOrderTraversal(root->right, sorted);
}

int main() {
    int T;
    cin >> T;  // ��ȡ���԰�������
    cin.ignore(); // ���Ի��з�

    while (T--) {
        string levelOrderLine;
        getline(cin, levelOrderLine);  // ��ȡ�����������
        int k;
        cin >> k;  // ��ȡkֵ
        cin.ignore(); // ���Ի��з�

        // ���������������
        stringstream ss(levelOrderLine);
        vector<string> levelOrder;
        string value;

        while (ss >> value) {
            levelOrder.push_back(value);
        }

        // ����BST
        TreeNode* root = buildBST(levelOrder);

        // �������
        vector<int> postOrderResult;
        postOrderTraversal(root, postOrderResult);

        // ��������Ի�ȡ������
        vector<int> sortedResult;
        inOrderTraversal(root, sortedResult);

        // �������������
        for (size_t i = 0; i < postOrderResult.size(); ++i) {
            cout << postOrderResult[i];
            if (i < postOrderResult.size() - 1) cout << " ";
        }
        cout << endl;

        // �����kС��Ԫ��
        cout << sortedResult[k - 1] << endl;

        // �ͷ��ڴ棨��ѡ�������飩
        // ������Լ���������ͷ����Ľڵ��ڴ�
    }

    return 0;
}
```
