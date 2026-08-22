---
source_id: data-structure-029
course_id: data_structure
title: "1"
original_file: "学科资料/数据结构/作业集（压压压趣味赛）/压压压/压压压/1.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# 1

```cpp
#include <iostream>
#include <fstream>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <queue>
#include<bitset>
// ���������ڵ�ṹ
struct Node {
    char ch;
    int freq;
    Node* left;
    Node* right;

    Node(char character, int frequency) : ch(character), freq(frequency), left(nullptr), right(nullptr) {}
};

// �Զ���ȽϺ������������ȶ���
struct Compare {
    bool operator()(Node* a, Node* b) {
        return a->freq > b->freq; // С���ѣ�Ƶ��С������
    }
};

// ���ɹ���������
void generateHuffmanCodes(Node* root, const std::string& code, std::unordered_map<char, std::string>& huffmanCodes) {
    if (!root) return;
    if (root->left == nullptr && root->right == nullptr) {
        huffmanCodes[root->ch] = code; // �洢�ַ��������
    }
    generateHuffmanCodes(root->left, code + "0", huffmanCodes);
    generateHuffmanCodes(root->right, code + "1", huffmanCodes);
}

// ѹ���ļ�
void compressFile(const std::string& filename, const std::unordered_map<char, std::string>& huffmanCodes) {
    std::ifstream inputFile(filename);
    std::ofstream outputFile(filename + ".huff", std::ios::binary);

    // ����ļ��Ƿ�ɹ���
    if (!inputFile.is_open() || !outputFile.is_open()) {
        std::cerr << "�޷����ļ�: " << filename << std::endl;
        return;
    }

    std::string encodedString;
    char ch;
    while (inputFile.get(ch)) {
        encodedString += huffmanCodes.at(ch); // ѹ��Ϊ����������
    }

    // �������ַ���ת��Ϊ�ֽڲ�д������ļ�
    for (size_t i = 0; i < encodedString.size(); i += 8) {
        std::string byteString = encodedString.substr(i, 8); // ÿ8������Ϊһ���ֽ�
        if (byteString.size() < 8) { // ��ȫ����8λ���ֽ�
            byteString.append(8 - byteString.size(), '0');
        }
        unsigned char byte = static_cast<unsigned char>(std::bitset<8>(byteString).to_ulong());
        outputFile.put(byte);
    }

    inputFile.close();
    outputFile.close();
}

void countAllCharacters(const std::string& filename) {
    std::ifstream file(filename);

    // ����ļ��Ƿ�ɹ���
    if (!file.is_open()) {
        std::cerr << "�޷����ļ�: " << filename << std::endl;
        return;
    }

    // ʹ�� unordered_map ��ͳ���ַ��ĳ��ִ���
    std::unordered_map<char, int> charCount;
    char ch;

    // ����ַ���ȡ�ļ�
    while (file.get(ch)) {
        // ͳ�������ַ�
        charCount[ch]++;
    }

    file.close();

    // �������ȶ���
    std::priority_queue<Node*, std::vector<Node*>, Compare> minHeap;

    // Ϊÿ���ַ��������������ڵ㲢�������ȶ���
    for (const auto& pair : charCount) {
        minHeap.push(new Node(pair.first, pair.second));
    }

    // ������������
    while (minHeap.size() > 1) {
        Node* left = minHeap.top(); minHeap.pop();
        Node* right = minHeap.top(); minHeap.pop();
        Node* newNode = new Node('\0', left->freq + right->freq);
        newNode->left = left;
        newNode->right = right;
        minHeap.push(newNode);
    }

    // ���ɹ���������
    std::unordered_map<char, std::string> huffmanCodes;
    generateHuffmanCodes(minHeap.top(), "", huffmanCodes);

    // �����ַ�
    std::vector<std::pair<char, int>> sortedChars(charCount.begin(), charCount.end());
    std::sort(sortedChars.begin(), sortedChars.end(), [](const auto& a, const auto& b) {
        return a.first < b.first; // ���ַ�����
        });

    // ������
    std::cout << "�����ַ����ִ���:" << std::endl;
    for (const auto& pair : sortedChars) {
        std::cout << "'" << pair.first << "' : " << pair.second << " -> " << huffmanCodes[pair.first] << std::endl;
    }

    // ѹ���ļ�
    compressFile(filename, huffmanCodes);
}

int main() {
    std::string filename;
    std::cout << "������Ҫ�������ļ���: ";
    std::cin >> filename;

    countAllCharacters(filename);

    return 0;
}

```
