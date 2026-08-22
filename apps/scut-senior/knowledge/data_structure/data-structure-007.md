---
source_id: data-structure-007
course_id: data_structure
title: "3"
original_file: "学科资料/数据结构/数据结构上机实验（Ai代替，停止维护）/ConsoleApplication1/3.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# 3

```cpp
//#include <iostream>
//#include <vector>
//
//using namespace std;
//
//struct ListNode {
//    int val;
//    ListNode* next;
//    ListNode(int x) : val(x), next(nullptr) {}
//};
//
//// Function to create a linked list from a vector of values
//ListNode* createList(const vector<int>& values) {
//    if (values.empty()) return nullptr;
//
//    ListNode* head = new ListNode(values[0]);
//    ListNode* current = head;
//
//    for (size_t i = 1; i < values.size(); ++i) {
//        current->next = new ListNode(values[i]);
//        current = current->next;
//    }
//
//    return head;
//}
//
//// Function to merge two sorted linked lists
//ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
//    ListNode dummy(0);  // Dummy node to simplify edge cases
//    ListNode* tail = &dummy;
//
//    while (l1 && l2) {
//        if (l1->val <= l2->val) {
//            tail->next = l1;
//            l1 = l1->next;
//        }
//        else {
//            tail->next = l2;
//            l2 = l2->next;
//        }
//        tail = tail->next;
//    }
//
//    // Append the remaining nodes
//    tail->next = l1 ? l1 : l2;
//
//    return dummy.next;
//}
//
//// Function to print the linked list
//void printList(ListNode* head) {
//    if (!head) {
//        cout << "NULL";
//        return;
//    }
//
//    while (head) {
//        cout << head->val;
//        head = head->next;
//        if (head) cout << " ";
//    }
//}
//
//int main() {
//    int N1, N2;
//    while (cin >> N1 >> N2) {
//        vector<int> vals1(N1);
//        vector<int> vals2(N2);
//
//        for (int i = 0; i < N1; ++i) cin >> vals1[i];
//        for (int i = 0; i < N2; ++i) cin >> vals2[i];
//
//        ListNode* list1 = createList(vals1);
//        ListNode* list2 = createList(vals2);
//
//        ListNode* mergedList = mergeTwoLists(list1, list2);
//        printList(mergedList);
//        cout << endl;
//
//        // Clean up memory
//        while (mergedList) {
//            ListNode* temp = mergedList;
//            mergedList = mergedList->next;
//            delete temp;
//        }
//    }
//
//    return 0;
//}

```
