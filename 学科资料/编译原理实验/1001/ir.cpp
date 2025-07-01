#include "ir.h"
#include <stdexcept>

IRGenerator::IRGenerator() 
    : currentFunction(nullptr), currentBlock(nullptr), tempCounter(0), labelCounter(0) {}

std::vector<std::unique_ptr<Function>> IRGenerator::generate(Program* program) {
    program->accept(this);
    return std::move(functions);
}

void IRGenerator::visitProgram(Program* program) {
    for (auto& func : program->functions) {
        func->accept(this);
    }
}

void IRGenerator::visitFunctionDecl(FunctionDecl* func) {
    // 创建新函数
    auto function = std::make_unique<Function>(func->name, func->returnType);
    currentFunction = function.get();
    
    // 设置参数
    for (const auto& param : func->params) {
        function->params.push_back(param.first);
        function->paramTypes.push_back(param.second);
        function->localVars[param.first] = static_cast<int>(function->localVars.size());
    }
    
    // 创建入口基本块
    createBasicBlock("entry");
    
    // 生成函数体代码
    func->body->accept(this);
    
    // 添加返回指令
    if (currentBlock->instructions.empty() || 
        currentBlock->instructions.back().op != IROp::RET) {
        addInstruction(IRInst(IROp::RET));
    }
    
    functions.push_back(std::move(function));
}

void IRGenerator::visitVarDecl(VarDecl* var) {
    // 分配局部变量
    currentFunction->localVars[var->name] = static_cast<int>(currentFunction->localVars.size());
    
    // 生成初始化代码
    if (var->initializer) {
        var->initializer->accept(this);
        addInstruction(IRInst(IROp::STORE, var->name, currentBlock->instructions.back().result));
    }
}

void IRGenerator::visitBlock(Block* block) {
    for (auto& stmt : block->statements) {
        stmt->accept(this);
    }
}

void IRGenerator::visitIfStatement(IfStatement* ifStmt) {
    // 生成条件代码
    ifStmt->condition->accept(this);
    std::string cond = currentBlock->instructions.back().result;
    
    // 创建基本块
    std::string thenLabel = newLabel();
    std::string elseLabel = newLabel();
    std::string endLabel = newLabel();
    
    // 条件跳转
    addInstruction(IRInst(IROp::JZ, "", cond, elseLabel));
    
    // then分支
    createBasicBlock(thenLabel);
    ifStmt->thenBranch->accept(this);
    addInstruction(IRInst(IROp::JMP, "", "", endLabel));
    
    // else分支
    createBasicBlock(elseLabel);
    if (ifStmt->elseBranch) {
        ifStmt->elseBranch->accept(this);
    }
    addInstruction(IRInst(IROp::JMP, "", "", endLabel));
    
    // 结束标签
    createBasicBlock(endLabel);
}

void IRGenerator::visitWhileStatement(WhileStatement* whileStmt) {
    // 创建基本块
    std::string startLabel = newLabel();
    std::string bodyLabel = newLabel();
    std::string endLabel = newLabel();
    
    // 开始标签
    createBasicBlock(startLabel);
    
    // 生成条件代码
    whileStmt->condition->accept(this);
    std::string cond = currentBlock->instructions.back().result;
    
    // 条件跳转
    addInstruction(IRInst(IROp::JZ, "", cond, endLabel));
    
    // 循环体
    createBasicBlock(bodyLabel);
    whileStmt->body->accept(this);
    addInstruction(IRInst(IROp::JMP, "", "", startLabel));
    
    // 结束标签
    createBasicBlock(endLabel);
}

void IRGenerator::visitReturnStatement(ReturnStatement* returnStmt) {
    if (returnStmt->value) {
        returnStmt->value->accept(this);
        addInstruction(IRInst(IROp::RET, "", currentBlock->instructions.back().result));
    } else {
        addInstruction(IRInst(IROp::RET));
    }
}

void IRGenerator::visitBinaryExpr(BinaryExpr* binary) {
    // 生成左操作数代码
    binary->left->accept(this);
    std::string left = currentBlock->instructions.back().result;
    
    // 生成右操作数代码
    binary->right->accept(this);
    std::string right = currentBlock->instructions.back().result;
    
    // 生成操作结果
    std::string result = newTemp();
    addInstruction(IRInst(convertOp(binary->op), result, left, right));
}

void IRGenerator::visitUnaryExpr(UnaryExpr* unary) {
    // 生成操作数代码
    unary->operand->accept(this);
    std::string operand = currentBlock->instructions.back().result;
    
    // 生成操作结果
    std::string result = newTemp();
    if (unary->op == TokenType::MINUS) {
        addInstruction(IRInst(IROp::SUB, result, "0", operand));
    }
}

void IRGenerator::visitLiteral(Literal* literal) {
    std::string result = newTemp();
    addInstruction(IRInst(IROp::CONST, result, literal->value));
}

void IRGenerator::visitIdentifier(Identifier* id) {
    std::string result = newTemp();
    addInstruction(IRInst(IROp::LOAD, result, getVarName(id->name)));
}

void IRGenerator::visitCallExpr(CallExpr* call) {
    // 生成参数代码
    std::vector<std::string> args;
    for (auto& arg : call->arguments) {
        arg->accept(this);
        args.push_back(currentBlock->instructions.back().result);
    }
    
    // 生成函数调用
    std::string result = newTemp();
    addInstruction(IRInst(IROp::CALL, result, call->callee));
}

std::string IRGenerator::newTemp() {
    return "%t" + std::to_string(tempCounter++);
}

std::string IRGenerator::newLabel() {
    return "L" + std::to_string(labelCounter++);
}

void IRGenerator::addInstruction(const IRInst& inst) {
    currentBlock->instructions.push_back(inst);
}

IROp IRGenerator::convertOp(TokenType op) {
    switch (op) {
        case TokenType::PLUS: return IROp::ADD;
        case TokenType::MINUS: return IROp::SUB;
        case TokenType::MULTIPLY: return IROp::MUL;
        case TokenType::DIVIDE: return IROp::DIV;
        case TokenType::EQUAL: return IROp::EQ;
        case TokenType::NOT_EQUAL: return IROp::NE;
        case TokenType::LESS: return IROp::LT;
        case TokenType::LESS_EQUAL: return IROp::LE;
        case TokenType::GREATER: return IROp::GT;
        case TokenType::GREATER_EQUAL: return IROp::GE;
        default:
            throw std::runtime_error("Invalid operator for IR conversion");
    }
}

std::string IRGenerator::getVarName(const std::string& name) {
    auto it = currentFunction->localVars.find(name);
    if (it == currentFunction->localVars.end()) {
        throw std::runtime_error("Undefined variable: " + name);
    }
    return "%" + name;
}

void IRGenerator::createBasicBlock(const std::string& name) {
    auto block = std::make_unique<BasicBlock>(name);
    currentBlock = block.get();
    currentFunction->blocks.push_back(std::move(block));
} 