#include "BasicBlock.h"
#include "Constant.h"
#include "Function.h"
#include "IRBuilder.h"
#include "Module.h"
#include "Type.h"
#include <iostream>

#ifdef DEBUG
#define DEBUG_OUTPUT std::cout << __LINE__ << std::endl;
#else
#define DEBUG_OUTPUT
#endif

#define CONST_INT(num) ConstantInt::get(num, module)

int main() {
    auto module = new Module("assign_module");
    auto builder = new IRBuilder(nullptr, module);
    Type *Int32Type = Type::get_int32_type(module);

    // 定义 main 函数
    auto mainFunType = FunctionType::get(Int32Type, {});
    auto mainFun = Function::create(mainFunType, "main", module);
    auto entryBB = BasicBlock::create(module, "entry", mainFun);
    builder->set_insert_point(entryBB);

    // 创建数组：int a[10];
    auto arrayType = ArrayType::get(Int32Type, 10);
    auto aAlloca = builder->create_alloca(arrayType);

    // a[0] = 10;
    auto zero = CONST_INT(0);
    auto a0GEP = builder->create_gep(aAlloca, {zero, zero});
    builder->create_store(CONST_INT(10), a0GEP);

    // a[1] = a[0] * 2;
    auto a1GEP = builder->create_gep(aAlloca, {zero, CONST_INT(1)});
    auto a0Load = builder->create_load(Int32Type, a0GEP);
    auto mulResult = builder->create_imul(a0Load, CONST_INT(2));
    builder->create_store(mulResult, a1GEP);

    // return a[1];
    auto a1Load = builder->create_load(Int32Type, a1GEP);
    builder->create_ret(a1Load);

    // 输出模块的 IR 代码
    std::cout << module->print();
    delete module;
    return 0;
}