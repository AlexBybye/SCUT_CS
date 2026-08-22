---
source_id: data-structure-003
course_id: data_structure
title: contrary
original_file: "学科资料/数据结构/数据结构算法研究/代码/contrary.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# contrary

```cpp
//#include <iostream>
//#include <vector>
//#include <algorithm> // ���� std::merge �� std::sort
//#include <chrono> // ���ڲ���ʱ��
//#include <fstream> // �����ļ�����
//#include <limits> // ���� std::numeric_limits
//
//// ��������
//void quicksort(std::vector<int>& arr, int left, int right) {
//    if (left >= right) return;
//
//    int pivot = arr[(left + right) / 2];
//    int i = left, j = right;
//
//    while (i <= j) {
//        while (i <= j && arr[i] < pivot) i++;
//        while (j >= i && arr[j] > pivot) j--;
//        if (i <= j) {
//            std::swap(arr[i], arr[j]);
//            i++;
//            j--;
//        }
//    }
//
//    quicksort(arr, left, j);
//    quicksort(arr, i, right);
//}
//
//// �Դ������㷨
//void customsort(std::vector<int>& arr) {
//    if (arr.size() <= 1) return;
//
//    // ��ʼ�ȽϺͷ���
//    std::vector<int> smallarr, largearr;
//    int a = arr[0], b = arr[1];
//    if (a > b) std::swap(a, b);
//
//    smallarr.push_back(a);
//    largearr.push_back(b);
//
//    int t1 = 1, t2 = 1;
//
//    // �������Ԫ��
//    for (size_t i = 2; i < arr.size(); ++i) {
//        if (arr[i] < a) {
//            smallarr.push_back(arr[i]);
//            t1++;
//        }
//        else if (arr[i] > b) {
//            largearr.push_back(arr[i]);
//            t2++;
//        }
//        else {
//            if (t1 <= t2) {
//                smallarr.push_back(arr[i]);
//                a = arr[i]; // ����С��������ֵ
//                t1++;
//            }
//            else {
//                largearr.push_back(arr[i]);
//                b = arr[i]; // ���´��������Сֵ
//                t2++;
//            }
//        }
//    }
//
//    // �ݹ�����
//    customsort(smallarr);
//    customsort(largearr);
//
//    // �ϲ����
//    std::vector<int> temparr;
//    temparr.reserve(smallarr.size() + largearr.size());
//    std::merge(smallarr.begin(), smallarr.end(), largearr.begin(), largearr.end(), std::back_inserter(temparr));
//
//    arr.swap(temparr);
//}
//
//// ��������㷨
//void hybridsort(std::vector<int>& arr, int n, int& callCount) {
//    if (arr.size() <= 1) return;
//
//    // ÿ�� n �ε���һ�� customsort
//    if (callCount % n == 0) {
//        customsort(arr);
//    }
//    else {
//        quicksort(arr, 0, arr.size() - 1);
//    }
//
//    callCount++;
//}
//
//int main() {
//    std::vector<int> arr;
//    std::vector<int> original_arr; // ���� original_arr
//    int num;
//    std::cout << "����������Ԫ�أ���������ֽ�������" << std::endl;
//    while (std::cin >> num) {
//        arr.push_back(num);
//        original_arr.push_back(num); // ͬʱ���ӵ� original_arr
//    }
//    // ��� cin �Ĵ���״̬
//    std::cin.clear();
//    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
//
//    std::ofstream outfile("sort_times.txt"); // ���ļ���д�������ʱ
//
//    for (int i = 0; i <100; ++i) {
//        int n = i + 1;
//        arr.clear(); // ��� arr �е�����Ԫ��
//        arr = original_arr; // �� original_arr �����ݸ��Ƶ� arr
//        int callCount = 0;//������
//        // ��������ǰ��ʱ��
//        auto start = std::chrono::high_resolution_clock::now();
//        hybridsort(arr, n, callCount); // ÿ�� n �ε���һ�� customsort
//        // ����������ʱ��
//        auto end = std::chrono::high_resolution_clock::now();
//
//        // �����ʱ
//        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
//
//        // ����ʱд���ļ�
//        outfile << duration << std::endl;
//        std::cout << "ÿ��" << n << "�ν���һ�ο������򣬺�ʱΪ��" << duration << "ms" << std::endl;
//    }
//
//    outfile.close(); // �ر��ļ�
//    return 0;
//}
```
