---
source_id: embedded-systems-020
course_id: embedded_systems
title: "嵌入式"
original_file: "学科资料/嵌入式/嵌入式复习方向/嵌入式.pptx"
document_role: note
year: 
locator_type: slide
---

# 嵌入式

<!-- slide: 1 -->

- 嵌入式系统
- 202330453151 计科一班 于博宇

<!-- slide: 2 -->

![image](assets/assets/embedded-systems-020/image-001.png)

<!-- slide: 3 -->

![image](assets/assets/embedded-systems-020/image-002.png)

<!-- slide: 4 -->

![image](assets/assets/embedded-systems-020/image-003.png)

<!-- slide: 5 -->

![image](assets/assets/embedded-systems-020/image-004.png)

<!-- slide: 6 -->

![image](assets/assets/embedded-systems-020/image-005.png)

<!-- slide: 7 -->

![image](assets/assets/embedded-systems-020/image-006.png)

<!-- slide: 8 -->

![image](assets/assets/embedded-systems-020/image-007.png)

<!-- slide: 9 -->

![image](assets/assets/embedded-systems-020/image-008.png)

<!-- slide: 10 -->

![image](assets/assets/embedded-systems-020/image-009.png)

<!-- slide: 11 -->

![image](assets/assets/embedded-systems-020/image-010.png)

<!-- slide: 12 -->

- 计算 ADC 数字值对应的模拟电压
- STM32 的 ADC 是一个 12 位的模数转换器，其数字输出范围是 0 - 4095（因为 2^12=4096）。
- 假设 ADC 的参考电压（VREF）为 3.3V（不同的 STM32 芯片可能有所不同，这里以常见的 3.3V 为例）。
- 当 ADC 数字值为 819 时，对应的模拟电压计算公式为：
- Uin = (ADC 数值 / 4095) × VREF
- Uin = (819 / 4095) × 3.3V≈0.66V

<!-- slide: 13 -->

![image](assets/assets/embedded-systems-020/image-011.png)
