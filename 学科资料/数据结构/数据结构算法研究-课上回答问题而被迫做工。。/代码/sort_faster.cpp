#include <iostream>
#include <vector>
#include <algorithm> // 用于 std::merge 和 std::sort
#include <chrono> // 用于测量时间
#include<fstream>

// 自创排序算法
void customsort(std::vector<int>& arr, int threshold) {
    if (arr.size() <= 1) return;

    // 如果数组大小小于等于阈值，切换到 std::sort
    if (arr.size() <= threshold) {
        std::sort(arr.begin(), arr.end());
        return;
    }

    // 初始比较和分组
    std::vector<int> smallarr, largearr;
    int a = arr[0], b = arr[1];
    if (a > b) std::swap(a, b);

    smallarr.push_back(a);
    largearr.push_back(b);

    int t1 = 1, t2 = 1;

    // 插入后续元素
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
                a = arr[i]; // 更新小数组的最大值
                t1++;
            }
            else {
                largearr.push_back(arr[i]);
                b = arr[i]; // 更新大数组的最小值
                t2++;
            }
        }
    }

    // 递归排序
    customsort(smallarr, threshold);
    customsort(largearr, threshold);

    // 合并结果
    std::vector<int> temparr;
    temparr.reserve(smallarr.size() + largearr.size());
    std::merge(smallarr.begin(), smallarr.end(), largearr.begin(), largearr.end(), std::back_inserter(temparr));

    arr.swap(temparr);
}

int main() {
    std::vector<int> arr = {};
    int num;
    std::cout << "请输入数组元素（输入非数字结束）：" << std::endl;
    while (std::cin >> num) {
        arr.push_back(num);
    }
    // 清除 cin 的错误状态
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    std::vector<int> original_arr = arr; // 保存原始数组
    std::ofstream outfile("sort_times.txt"); // 打开文件以写入排序耗时
    for (int i = 0; i < 300; i++)
    {
        arr = original_arr; // 每次循环前重置数组到初始状态
        int threshold = i; // 设置阈值

        // 测量排序前的时间
        auto start = std::chrono::high_resolution_clock::now();
        customsort(arr, threshold);
        // 测量排序后的时间
        auto end = std::chrono::high_resolution_clock::now();

        // 计算耗时
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();

        std::cout << "第" << i << "次排序耗时：" << duration << " 毫秒" << std::endl;
        outfile << duration << std::endl;
    }
    outfile.close(); // 关闭文件
    return 0;
}