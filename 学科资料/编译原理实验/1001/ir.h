#ifndef IR_H
#define IR_H

#include "parser.h"
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>

// IR指令类型
enum class IROp {
    // 算术运算
    ADD, SUB, MUL, DIV,
    
    // 比较运算
    EQ, NE, LT, LE, GT, GE,
    
    // 控制流
    JMP, JZ, JNZ, LABEL,
    
    // 内存操作
    LOAD, STORE,
    
    // 函数调用
    CALL, RET,
    
    // 其他
    ALLOCA, CONST
};

// IR指令
struct IRInst {
    IROp op;
    std::string result;  // 结果变量
    std::string arg1;    // 第一个操作数
    std::string arg2;    // 第二个操作数（如果有）
    
    IRInst(IROp op, const std::string& result = "", 
           const std::string& arg1 = "", const std::string& arg2 = "")
        : op(op), result(result), arg1(arg1), arg2(arg2) {}
};

// 基本块
class BasicBlock {
public:
    std::string name;
    std::vector<IRInst> instructions;
    std::vector<std::string> predecessors;
    std::vector<std::string> successors;
    
    BasicBlock(const std::string& name) : name(name) {}
};

// 函数
class Function {
public:
    std::string name;
    TokenType returnType;
    std::vector<TokenType> paramTypes;
    std::vector<std::string> params;
    std::vector<std::unique_ptr<BasicBlock>> blocks;
    std::unordered_map<std::string, int> localVars;
    
    Function(const std::string& name, TokenType returnType)
        : name(name), returnType(returnType) {}
};

// 中间代码生成器
class IRGenerator : public ASTVisitor {
public:
    IRGenerator();
    std::vector<std::unique_ptr<Function>> generate(Program* program);
    
    // 访问者模式实现
    void visitProgram(Program* program) override;
    void visitFunctionDecl(FunctionDecl* func) override;
    void visitVarDecl(VarDecl* var) override;
    void visitBlock(Block* block) override;
    void visitIfStatement(IfStatement* ifStmt) override;
    void visitWhileStatement(WhileStatement* whileStmt) override;
    void visitReturnStatement(ReturnStatement* returnStmt) override;
    void visitBinaryExpr(BinaryExpr* binary) override;
    void visitUnaryExpr(UnaryExpr* unary) override;
    void visitLiteral(Literal* literal) override;
    void visitIdentifier(Identifier* id) override;
    void visitCallExpr(CallExpr* call) override;
    
private:
    std::vector<std::unique_ptr<Function>> functions;
    Function* currentFunction;
    BasicBlock* currentBlock;
    int tempCounter;
    int labelCounter;
    
    std::string newTemp();
    std::string newLabel();
    void addInstruction(const IRInst& inst);
    IROp convertOp(TokenType op);
    std::string getVarName(const std::string& name);
    void createBasicBlock(const std::string& name);
};

#endif // IR_H 