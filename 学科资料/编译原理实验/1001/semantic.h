#ifndef SEMANTIC_H
#define SEMANTIC_H

#include "parser.h"
#include <unordered_map>
#include <string>
#include <vector>
#include <memory>

// 符号类型
enum class SymbolType {
    VARIABLE,
    FUNCTION,
    PARAMETER
};

// 符号信息
struct Symbol {
    SymbolType type;
    TokenType dataType;
    std::vector<TokenType> paramTypes;  // 仅用于函数
    bool isInitialized;
};

// 作用域
class Scope {
public:
    Scope(Scope* parent = nullptr) : parent(parent) {}
    
    bool define(const std::string& name, const Symbol& symbol) {
        if (symbols.find(name) != symbols.end()) {
            return false;
        }
        symbols[name] = symbol;
        return true;
    }
    
    Symbol* resolve(const std::string& name) {
        auto it = symbols.find(name);
        if (it != symbols.end()) {
            return &it->second;
        }
        if (parent) {
            return parent->resolve(name);
        }
        return nullptr;
    }

    Scope* getParent() const { return parent; }
    
private:
    std::unordered_map<std::string, Symbol> symbols;
    Scope* parent;
};

// 语义分析器
class SemanticAnalyzer : public ASTVisitor {
public:
    SemanticAnalyzer();
    void analyze(Program* program);
    
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
    Scope* currentScope;
    TokenType currentReturnType;
    bool hasReturnStatement;
    
    void enterScope();
    void exitScope();
    bool checkTypes(TokenType t1, TokenType t2);
    TokenType getExpressionType(Expression* expr);
    void checkAssignment(TokenType leftType, TokenType rightType);
    void checkFunctionCall(const std::string& name, const std::vector<TokenType>& argTypes);
};

#endif // SEMANTIC_H 