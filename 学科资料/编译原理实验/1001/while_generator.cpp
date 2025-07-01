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
    auto module = new Module("while_module");
    auto builder = new IRBuilder(nullptr, module);
    Type *Int32Type = Type::get_int32_type(module);

    // 定义 main 函数
    auto mainFunType = FunctionType::get(Int32Type, {});
    auto mainFun = Function::create(mainFunType, "main", module);
    auto entryBB = BasicBlock::create(module, "entry", mainFun);
    builder->set_insert_point(entryBB);

    auto aAlloca = builder->create_alloca(Int32Type);
    auto iAlloca = builder->create_alloca(Int32Type);
    builder->create_store(CONST_INT(10), aAlloca);
    builder->create_store(CONST_INT(0), iAlloca);

    auto loopEntryBB = BasicBlock::create(module, "loop_entry", mainFun);
    auto loopBodyBB = BasicBlock::create(module, "loop_body", mainFun);
    auto exitBB = BasicBlock::create(module, "exit", mainFun);

    // 初始跳转至条件判断块
    builder->create_br(loopEntryBB);

    // 条件判断块
    builder->set_insert_point(loopEntryBB);
    auto iLoad = builder->create_load(Int32Type, iAlloca);
    auto cond = builder->create_icmp_lt(iLoad, CONST_INT(10));
    builder->create_cond_br(cond, loopBodyBB, exitBB);

    // 循环体块
    builder->set_insert_point(loopBodyBB);
    auto aLoad = builder->create_load(Int32Type, aAlloca);
    auto newI = builder->create_iadd(iLoad, CONST_INT(1));
    auto newA = builder->create_iadd(aLoad, newI);
    builder->create_store(newI, iAlloca);
    builder->create_store(newA, aAlloca);
    builder->create_br(loopEntryBB);

    // 退出块
    builder->set_insert_point(exitBB);
    auto finalA = builder->create_load(Int32Type, aAlloca);
    builder->create_ret(finalA);

    // 输出模块的 IR 代码
    std::cout << module->print();
    delete module;
    return 0;
}