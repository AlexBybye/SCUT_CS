---
source_id: data-structure-004
course_id: data_structure
title: sort_faster
original_file: "学科资料/数据结构/数据结构算法研究/代码/sort_faster.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# sort_faster

```cpp
#include <iostream>
#include <vector>
#include <algorithm> // ���� std::merge �� std::sort
#include <chrono> // ���ڲ���ʱ��
#include<fstream>

// �Դ������㷨
void customsort(std::vector<int>& arr, int threshold) {
    if (arr.size() <= 1) return;

    // ��������СС�ڵ�����ֵ���л��� std::sort
    if (arr.size() <= threshold) {
        std::sort(arr.begin(), arr.end());
        return;
    }

    // ��ʼ�ȽϺͷ���
    std::vector<int> smallarr, largearr;
    int a = arr[0], b = arr[1];
    if (a > b) std::swap(a, b);

    smallarr.push_back(a);
    largearr.push_back(b);

    int t1 = 1, t2 = 1;

    // �������Ԫ��
    for (size_t i = 2; i < arr.size(); ++i) {
        if (arr[i] < a) {
            smallarr.push_back(arr[i]);
            t1++;
        }
        else if (arr[i] > b) {
            largearr.push_back(arr[i]);
            t2++;
        }
        else {
            if (t1 <= t2) {
                smallarr.push_back(arr[i]);
                a = arr[i]; // ����С��������ֵ
                t1++;
            }
            else {
                largearr.push_back(arr[i]);
                b = arr[i]; // ���´��������Сֵ
                t2++;
            }
        }
    }

    // �ݹ�����
    customsort(smallarr, threshold);
    customsort(largearr, threshold);

    // �ϲ����
    std::vector<int> temparr;
    temparr.reserve(smallarr.size() + largearr.size());
    std::merge(smallarr.begin(), smallarr.end(), largearr.begin(), largearr.end(), std::back_inserter(temparr));

    arr.swap(temparr);
}

int main() {
    std::vector<int> arr = {};
    int num;
    std::cout << "����������Ԫ�أ���������ֽ�������" << std::endl;
    while (std::cin >> num) {
        arr.push_back(num);
    }
    // ��� cin �Ĵ���״̬
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    std::vector<int> original_arr = arr; // ����ԭʼ����
    std::ofstream outfile("sort_times.txt"); // ���ļ���д�������ʱ
    for (int i = 0; i < 300; i++)
    {
        arr = original_arr; // ÿ��ѭ��ǰ�������鵽��ʼ״̬
        int threshold = i; // ������ֵ

        // ��������ǰ��ʱ��
        auto start = std::chrono::high_resolution_clock::now();
        customsort(arr, threshold);
        // ����������ʱ��
        auto end = std::chrono::high_resolution_clock::now();

        // �����ʱ
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

        std::cout << "��" << i << "�������ʱ��" << duration << " ����" << std::endl;
        outfile << duration << std::endl;
    }
    outfile.close(); // �ر��ļ�
    return 0;
}
```
