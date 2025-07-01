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
    auto module = new Module("fun_module");
    auto builder = new IRBuilder(nullptr, module);
    Type *Int32Type = Type::get_int32_type(module);

    // 定义 callee 函数
    auto calleeFunType = FunctionType::get(Int32Type, {Int32Type});
    auto calleeFun = Function::create(calleeFunType, "callee", module);
    auto calleeBB = BasicBlock::create(module, "entry", calleeFun);
    builder->set_insert_point(calleeBB);

    std::vector<Value *> calleeArgs;
    for (auto arg = calleeFun->arg_begin(); arg != calleeFun->arg_end(); arg++) {
        calleeArgs.push_back(*arg);
    }
    auto mulResult = builder->create_imul(calleeArgs[0], CONST_INT(2));
    builder->create_ret(mulResult);

    // 定义 main 函数
    auto mainFunType = FunctionType::get(Int32Type, {});
    auto mainFun = Function::create(mainFunType, "main", module);
    auto mainBB = BasicBlock::create(module, "entry", mainFun);
    builder->set_insert_point(mainBB);

    auto callCallee = builder->create_call(calleeFun, {CONST_INT(110)});
    builder->create_ret(callCallee);

    // 输出模块的 IR 代码
    std::cout << module->print();
    delete module;
    return 0;
}