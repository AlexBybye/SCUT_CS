---
source_id: signals-and-communication-024
course_id: signals_and_communication
title: "7. 跳频和扩频"
original_file: "学科资料/信号处理与通信基础/数字信号处理/通信原理（补充）/7. 跳频和扩频.ppt"
document_role: note
year: 
locator_type: slide
---

# 7. 跳频和扩频

<!-- slide: 1 -->

## 通信原理

- 6.  跳频和扩频

<!-- slide: 2 -->

## 跳频技术
概念：一种扩频通信技术，通过快速切换载波频率来传输数据，广泛应用于军事通信、蓝牙、Wi-Fi等领域。
基本原理：按预设的“跳频图案”（由伪随机序列控制），在大量窄带信道间高速切换（每秒数百至数千次）。
关键优势
    -- 抗干扰与抗截获：即使部分频段被干扰或监听，仅影响局部数据传输，整体通信仍可通过纠错机制恢复。
    -- 多用户共享：不同用户采用正交跳频图案（如蓝牙的79个信道），避免冲突，提升频谱利用率。
    -- 低功率密度：信号能量分散在宽频带内，符合法规（如FCC Part 15），降低对其他设备的干扰。

![image](assets/assets/signals-and-communication-024/image-001.png)

<!-- slide: 3 -->

## 典型应用
     -- 蓝牙（Bluetooth）：采用1600次/秒的跳频速率，79个信道（蓝牙5.0后扩展至40个），确保短距离稳定连接。
     -- 军事通信：如美军JTIDS系统，通过加密跳频图案抵御电子战干扰。
     -- 早期Wi-Fi（802.11）：已逐步被DSSS（直接序列扩频）和OFDM取代，但仍在特定场景使用。

![image](assets/assets/signals-and-communication-024/image-002.png)

<!-- slide: 4 -->

## 扩频技术
概念：把原始信号“摊开”到远比它本身带宽宽得多的频谱上再发射的通信技术。
理解：用带宽换抗干扰、换隐蔽、换多址能力。即，把单位比特的能量打散到一大片频带上，看起来像噪声。
技术：
     -- 直接序列扩频 DSSS（“糖果变糖粉”）：数据比特 ⊕ 高速伪随机码（chip 速率远高于比特速率）→ 基带带宽被“拉宽”N 倍。
     -- 跳频扩频 FHSS（“换座躲猫猫”）：载波按伪随机序列在 N 个窄信道间“跳房子”，每跳只驻留几百微秒～几毫秒。

<!-- slide: 5 -->

## 应用

  -- 军事：JTIDS、Link-16、保密电台、导弹遥测。
  -- 民用蜂窝：cdmaOne(IS-95)、CDMA2000、WCDMA 的下行。
  -- 卫星导航：GPS、北斗、Galileo 全部 DSSS。
  -- 短距无线：蓝牙（FHSS）、IEEE 802.11b（DSSS）、UWB（THSS+DS 混合）。
  -- 物联网/定位：LoRa 的 CSS（Chirp Spread Spectrum）可看作 DSSS 的线性调频变体。
