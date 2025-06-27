//#include <iostream>
//#include <vector>
//#include <algorithm> // 用于 std::merge 和 std::sort
//#include <chrono> // 用于测量时间
//#include <fstream> // 用于文件操作
//#include <limits> // 用于 std::numeric_limits
//
//// 快速排序
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
//// 自创排序算法
//void customsort(std::vector<int>& arr) {
//    if (arr.size() <= 1) return;
//
//    // 初始比较和分组
//    std::vector<int> smallarr, largearr;
//    int a = arr[0], b = arr[1];
//    if (a > b) std::swap(a, b);
//
//    smallarr.push_back(a);
//    largearr.push_back(b);
//
//    int t1 = 1, t2 = 1;
//
//    // 插入后续元素
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
//                a = arr[i]; // 更新小数组的最大值
//                t1++;
//            }
//            else {
//                largearr.push_back(arr[i]);
//                b = arr[i]; // 更新大数组的最小值
//                t2++;
//            }
//        }
//    }
//
//    // 递归排序
//    customsort(smallarr);
//    customsort(largearr);
//
//    // 合并结果
//    std::vector<int> temparr;
//    temparr.reserve(smallarr.size() + largearr.size());
//    std::merge(smallarr.begin(), smallarr.end(), largearr.begin(), largearr.end(), std::back_inserter(temparr));
//
//    arr.swap(temparr);
//}
//
//// 混合排序算法
//void hybridsort(std::vector<int>& arr, int n, int& callCount) {
//    if (arr.size() <= 1) return;
//
//    // 每隔 n 次调用一次 customsort
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
//    std::vector<int> original_arr; // 定义 original_arr
//    int num;
//    std::cout << "请输入数组元素（输入非数字结束）：" << std::endl;
//    while (std::cin >> num) {
//        arr.push_back(num);
//        original_arr.push_back(num); // 同时添加到 original_arr
//    }
//    // 清除 cin 的错误状态
//    std::cin.clear();
//    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
//
//    std::ofstream outfile("sort_times.txt"); // 打开文件以写入排序耗时
//
//    for (int i = 0; i <100; ++i) {
//        int n = i + 1;
//        arr.clear(); // 清除 arr 中的所有元素
//        arr = original_arr; // 将 original_arr 的内容复制到 arr
//        int callCount = 0;//计数器
//        // 测量排序前的时间
//        auto start = std::chrono::high_resolution_clock::now();
//        hybridsort(arr, n, callCount); // 每隔 n 次调用一次 customsort
//        // 测量排序后的时间
//        auto end = std::chrono::high_resolution_clock::now();
//
//        // 计算耗时
//        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
//
//        // 将耗时写入文件
//        outfile << duration << std::endl;
//        std::cout << "每隔" << n << "次进行一次快速排序，耗时为：" << duration << "ms" << std::endl;
//    }
//
//    outfile.close(); // 关闭文件
//    return 0;
//}