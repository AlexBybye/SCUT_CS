---
source_id: software-testing-041
course_id: software_testing
title: Unit
original_file: "学科资料/软件测试与质量保证/笔记（Lin是计院的笔记，其余来自软院兄弟们）/Lin/Unit3.md"
document_role: note
year: 
locator_type: heading
---

# Unit

## ✅ **第三章：单元测试与Google Test框架**

### 一、单元测试基础

- **对象**：模块（函数/类）
- **依据**：软件设计规格说明
- **方法**：以白盒为主
- **通过准则**：命名规范、控制流正确、覆盖率达标、错误已修复

### 二、单元测试焦点（重点）

1. **模块接口**：输入输出一致性、资源释放
2. **局部数据结构**：变量未初始化、数组越界、指针错误
3. **边界条件**：合法/非法数据、边界内外点
4. **独立执行路径**：不可达代码、计算错误、循环错误
5. **错误处理路径**：错误检测、处理策略、有效性

### 三、单元测试步骤

1. 冒烟测试
2. 肯定测试（正向）
3. 否定测试（反向）
4. 专用测试（性能、安全）
5. 覆盖测试
6. 覆盖率评估
7. 覆盖率完善

### 四、动态测试环境

- **驱动模块**：调用被测模块（如Google Test）
- **桩模块**：模拟被调用模块

### 五、Google Test框架（重点掌握）

- **优点**：开源、跨平台、测试独立、失败继续、组织清晰
- **安装与配置**：include、lib、依赖项
- **TEST宏**：`TEST(TestCaseName, TestName)`
- **断言类型**：
    - `EXPECT_*`：非致命失败
    - `ASSERT_*`：致命失败
    - 比较：`EQ`、`NE`、`LT`、`LE`、`GT`、`GE`
    - 字符串：`STREQ`、`STRNE`、`STRCASEEQ`
- **Test Fixture**：
    - 继承 `::testing::Test`
    - 重写 `SetUp()` / `TearDown()`
    - 使用 `TEST_F()`
- **事件机制**：
    - 全局事件（`Environment`）
    - TestSuite事件（`SetUpTestCase`）
    - TestCase事件（`SetUp` / `TearDown`）
- **参数化测试**：
    - 继承 `TestWithParam<T>`
    - 使用 `TEST_P` 和 `GetParam()`
    - 使用 `Values()` 等生成器
- **进阶断言**：
    - 异常检查（`EXPECT_THROW`）
    - 谓词断言（`EXPECT_PRED`）
    - 浮点数比较（`EXPECT_FLOAT_EQ`）
    - HRESULT、类型检查

### 六、单元测试实例（平方根函数）

- 等价类划分：正数、负数
- 边界值分析：0、极小正数、最大正数、负数边界
- 用Google Test重写原始测试代码
