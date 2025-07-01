#ifndef PARSER_H
#define PARSER_H

#include "lexer.h"
#include <memory>
#include <vector>
#include <string>

// 前向声明
class ASTNode;
class Expression;
class Statement;
class Program;
class FunctionDecl;
class VarDecl;
class Block;
class IfStatement;
class WhileStatement;
class ReturnStatement;
class BinaryExpr;
class UnaryExpr;
class Literal;
class Identifier;
class CallExpr;

// 访问者模式基类
class ASTVisitor {
public:
    virtual ~ASTVisitor() = default;
    virtual void visitProgram(Program* program) = 0;
    virtual void visitFunctionDecl(FunctionDecl* func) = 0;
    virtual void visitVarDecl(VarDecl* var) = 0;
    virtual void visitBlock(Block* block) = 0;
    virtual void visitIfStatement(IfStatement* ifStmt) = 0;
    virtual void visitWhileStatement(WhileStatement* whileStmt) = 0;
    virtual void visitReturnStatement(ReturnStatement* returnStmt) = 0;
    virtual void visitBinaryExpr(BinaryExpr* binary) = 0;
    virtual void visitUnaryExpr(UnaryExpr* unary) = 0;
    virtual void visitLiteral(Literal* literal) = 0;
    virtual void visitIdentifier(Identifier* id) = 0;
    virtual void visitCallExpr(CallExpr* call) = 0;
};

// AST节点基类
class ASTNode {
public:
    virtual ~ASTNode() = default;
    virtual void accept(ASTVisitor* visitor) = 0;
};

// 表达式基类
class Expression : public ASTNode {
public:
    virtual ~Expression() = default;
};

// 语句基类
class Statement : public ASTNode {
public:
    virtual ~Statement() = default;
};

// 程序节点
class Program : public ASTNode {
public:
    std::vector<std::unique_ptr<FunctionDecl>> functions;
    void accept(ASTVisitor* visitor) override { visitor->visitProgram(this); }
};

// 函数声明
class FunctionDecl : public ASTNode {
public:
    std::string name;
    std::vector<std::pair<std::string, TokenType>> params;
    TokenType returnType;
    std::unique_ptr<Block> body;

    FunctionDecl(const std::string& name, 
                std::vector<std::pair<std::string, TokenType>> params,
                TokenType returnType,
                std::unique_ptr<Block> body)
        : name(name), params(std::move(params)), returnType(returnType), body(std::move(body)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitFunctionDecl(this); }
};

// 变量声明
class VarDecl : public Statement {
public:
    std::string name;
    TokenType type;
    std::unique_ptr<Expression> initializer;

    VarDecl(const std::string& name, TokenType type, std::unique_ptr<Expression> initializer)
        : name(name), type(type), initializer(std::move(initializer)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitVarDecl(this); }
};

// 代码块
class Block : public Statement {
public:
    std::vector<std::unique_ptr<Statement>> statements;

    explicit Block(std::vector<std::unique_ptr<Statement>> statements)
        : statements(std::move(statements)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitBlock(this); }
};

// if语句
class IfStatement : public Statement {
public:
    std::unique_ptr<Expression> condition;
    std::unique_ptr<Block> thenBranch;
    std::unique_ptr<Block> elseBranch;

    IfStatement(std::unique_ptr<Expression> condition,
               std::unique_ptr<Block> thenBranch,
               std::unique_ptr<Block> elseBranch)
        : condition(std::move(condition)),
          thenBranch(std::move(thenBranch)),
          elseBranch(std::move(elseBranch)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitIfStatement(this); }
};

// while语句
class WhileStatement : public Statement {
public:
    std::unique_ptr<Expression> condition;
    std::unique_ptr<Block> body;

    WhileStatement(std::unique_ptr<Expression> condition,
                  std::unique_ptr<Block> body)
        : condition(std::move(condition)), body(std::move(body)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitWhileStatement(this); }
};

// return语句
class ReturnStatement : public Statement {
public:
    std::unique_ptr<Expression> value;

    explicit ReturnStatement(std::unique_ptr<Expression> value)
        : value(std::move(value)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitReturnStatement(this); }
};

// 二元表达式
class BinaryExpr : public Expression {
public:
    TokenType op;
    std::unique_ptr<Expression> left;
    std::unique_ptr<Expression> right;

    BinaryExpr(TokenType op,
              std::unique_ptr<Expression> left,
              std::unique_ptr<Expression> right)
        : op(op), left(std::move(left)), right(std::move(right)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitBinaryExpr(this); }
};

// 一元表达式
class UnaryExpr : public Expression {
public:
    TokenType op;
    std::unique_ptr<Expression> operand;

    UnaryExpr(TokenType op, std::unique_ptr<Expression> operand)
        : op(op), operand(std::move(operand)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitUnaryExpr(this); }
};

// 字面量
class Literal : public Expression {
public:
    TokenType type;
    std::string value;

    Literal(TokenType type, const std::string& value)
        : type(type), value(value) {}

    void accept(ASTVisitor* visitor) override { visitor->visitLiteral(this); }
};

// 标识符
class Identifier : public Expression {
public:
    std::string name;

    explicit Identifier(const std::string& name)
        : name(name) {}

    void accept(ASTVisitor* visitor) override { visitor->visitIdentifier(this); }
};

// 函数调用
class CallExpr : public Expression {
public:
    std::string callee;
    std::vector<std::unique_ptr<Expression>> arguments;

    CallExpr(const std::string& callee,
            std::vector<std::unique_ptr<Expression>> arguments)
        : callee(callee), arguments(std::move(arguments)) {}

    void accept(ASTVisitor* visitor) override { visitor->visitCallExpr(this); }
};

// 语法分析器
class Parser {
public:
    Parser(Lexer& lexer);
    std::unique_ptr<Program> parse();

private:
    Lexer& lexer;
    Token current;
    Token previous;
    
    void advance();
    bool check(TokenType type) const;
    bool match(TokenType type);
    Token consume(TokenType type, const std::string& message);
    
    std::unique_ptr<Program> parseProgram();
    std::unique_ptr<FunctionDecl> parseFunctionDecl();
    std::unique_ptr<VarDecl> parseVarDecl();
    std::unique_ptr<Block> parseBlock();
    std::unique_ptr<Statement> parseStatement();
    std::unique_ptr<IfStatement> parseIfStatement();
    std::unique_ptr<WhileStatement> parseWhileStatement();
    std::unique_ptr<ReturnStatement> parseReturnStatement();
    std::unique_ptr<Expression> parseExpression();
    std::unique_ptr<Expression> parseAssignment();
    std::unique_ptr<Expression> parseEquality();
    std::unique_ptr<Expression> parseComparison();
    std::unique_ptr<Expression> parseTerm();
    std::unique_ptr<Expression> parseFactor();
    std::unique_ptr<Expression> parseUnary();
    std::unique_ptr<Expression> parsePrimary();
    std::unique_ptr<CallExpr> parseCall(const std::string& callee);
};

#endif // PARSER_H 