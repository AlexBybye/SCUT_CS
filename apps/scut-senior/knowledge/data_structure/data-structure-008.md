---
source_id: data-structure-008
course_id: data_structure
title: "4"
original_file: "学科资料/数据结构/数据结构上机实验（Ai代替，停止维护）/ConsoleApplication1/4.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# 4

```cpp
//#include <iostream>
//#include <set>  // ���� set
//
//template<class Elem>
//class Set {
//public:
//    virtual void Insert(const Elem& e) = 0;
//    virtual bool Remove(const Elem& e) = 0;
//    virtual bool GetFirstElement(Elem& e) = 0;
//    virtual bool GetLastElement(Elem& e) = 0;
//    virtual int GetSize() const = 0;  // ȷ������һ�� const ����
//    virtual void Print() const = 0;
//    virtual void operator += (const Set<Elem>& s) = 0;
//    virtual void operator -= (const Set<Elem>& s) = 0;
//};
//
//template<class Elem>
//class ASet : public Set<Elem> {
//private:
//    std::set<Elem> elements;  // ʹ�� set ���� vector
//
//public:
//    ASet() {}
//    virtual ~ASet() {}
//
//    void Insert(const Elem& e) override {
//        elements.insert(e);  // set �Զ������ظ�Ԫ��
//    }
//
//    bool Remove(const Elem& e) override {
//        auto it = elements.find(e);
//        if (it != elements.end()) {
//            elements.erase(it);
//            return true;
//        }
//        return false;
//    }
//
//    bool GetFirstElement(Elem& e) override {
//        if (elements.empty()) return false;
//        e = *elements.begin();
//        return true;
//    }
//
//    bool GetLastElement(Elem& e) override {
//        if (elements.empty()) return false;
//        e = *elements.rbegin();
//        return true;
//    }
//
//    int GetSize() const override {  // ȷ����������� const
//        return elements.size();
//    }
//
//    void Print() const override {
//        for (const auto& elem : elements) {
//            std::cout << elem << " ";
//        }
//        std::cout << std::endl;
//    }
//
//    void operator += (const Set<Elem>& s) override {
//        const ASet<Elem>* other = dynamic_cast<const ASet<Elem>*>(&s);
//        if (other) {
//            elements.insert(other->elements.begin(), other->elements.end());
//        }
//    }
//
//    void operator -= (const Set<Elem>& s) override {
//        const ASet<Elem>* other = dynamic_cast<const ASet<Elem>*>(&s);
//        if (other) {
//            for (const auto& elem : other->elements) {
//                Remove(elem);
//            }
//        }
//    }
//};
//
//int main() {
//    ASet<int> S1, S2, S3;
//    S1.Insert(1);
//    S1.Insert(3);
//    S1.Insert(4);
//    S1.Insert(5);
//    S1.Insert(6);
//    S1.Insert(7);
//    S1.Insert(8);
//
//    S2.Insert(2);
//    S2.Insert(3);
//    S2.Insert(4);
//    S2.Insert(10);
//    S2.Insert(12);
//
//    S3.Insert(1);
//    S3.Insert(3);
//    S3.Insert(4);
//    S3.Insert(100);
//    S3.Insert(101);
//
//    // Output the first and last elements of S1
//    int first, last;
//    if (S1.GetFirstElement(first) && S1.GetLastElement(last)) {
//        std::cout << first << " " << last << std::endl;
//    }
//
//    // Output the size of S2
//    std::cout << S2.GetSize() << std::endl;
//
//    // Output elements of S3
//    S3.Print();
//
//    // Perform S1 += S2 and output the elements of S1
//    S1 += S2;
//    S1.Print();
//
//    // Perform S2 -= S3 and output the elements of S2
//    S2 -= S3;
//    S2.Print();
//
//    return 0;
//}

```
