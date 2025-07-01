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
#define CONST_FP(num) ConstantFP::get(num, module)

int main() {
    auto module = new Module("if_module");
    auto builder = new IRBuilder(nullptr, module);
    Type *Int32Type = Type::get_int32_type(module);
    Type *FloatType = Type::get_float_type(module);

    // 定义 main 函数
    auto mainFunType = FunctionType::get(Int32Type, {});
    auto mainFun = Function::create(mainFunType, "main", module);
    auto entryBB = BasicBlock::create(module, "entry", mainFun);
    builder->set_insert_point(entryBB);

    auto aAlloca = builder->create_alloca(FloatType);
    builder->create_store(CONST_FP(5.555), aAlloca);
    auto aLoad = builder->create_load(FloatType, aAlloca);
    auto cond = builder->create_fcmp_gt(aLoad, CONST_FP(1.0));

    auto trueBB = BasicBlock::create(module, "true", mainFun);
    auto falseBB = BasicBlock::create(module, "false", mainFun);
    builder->create_cond_br(cond, trueBB, falseBB);

    // 真分支
    builder->set_insert_point(trueBB);
    builder->create_ret(CONST_INT(233));

    // 假分支
    builder->set_insert_point(falseBB);
    builder->create_ret(CONST_INT(0));

    // 输出模块的 IR 代码
    std::cout << module->print();
    delete module;
    return 0;
}