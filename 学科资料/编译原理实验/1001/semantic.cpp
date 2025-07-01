#include "semantic.h"
#include <stdexcept>

SemanticAnalyzer::SemanticAnalyzer() 
    : currentScope(new Scope()), currentReturnType(TokenType::VOID), hasReturnStatement(false) {}

void SemanticAnalyzer::analyze(Program* program) {
    program->accept(this);
}

void SemanticAnalyzer::visitProgram(Program* program) {
    for (auto& func : program->functions) {
        func->accept(this);
    }
}

void SemanticAnalyzer::visitFunctionDecl(FunctionDecl* func) {
    // 检查函数是否已定义
    Symbol* existing = currentScope->resolve(func->name);
    if (existing) {
        throw std::runtime_error("Function '" + func->name + "' already defined");
    }
    
    // 定义函数符号
    Symbol funcSymbol{
        SymbolType::FUNCTION,
        func->returnType,
        std::vector<TokenType>(),
        true
    };
    
    // 收集参数类型
    for (const auto& param : func->params) {
        funcSymbol.paramTypes.push_back(param.second);
    }
    
    currentScope->define(func->name, funcSymbol);
    
    // 进入新的作用域
    enterScope();
    currentReturnType = func->returnType;
    hasReturnStatement = false;
    
    // 定义参数
    for (const auto& param : func->params) {
        Symbol paramSymbol{
            SymbolType::PARAMETER,
            param.second,
            std::vector<TokenType>(),
            true
        };
        currentScope->define(param.first, paramSymbol);
    }
    
    // 分析函数体
    func->body->accept(this);
    
    // 检查返回值
    if (currentReturnType != TokenType::VOID && !hasReturnStatement) {
        throw std::runtime_error("Function '" + func->name + "' must return a value");
    }
    
    exitScope();
}

void SemanticAnalyzer::visitVarDecl(VarDecl* var) {
    // 检查变量是否已定义
    Symbol* existing = currentScope->resolve(var->name);
    if (existing) {
        throw std::runtime_error("Variable '" + var->name + "' already defined");
    }
    
    // 定义变量符号
    Symbol varSymbol{
        SymbolType::VARIABLE,
        var->type,
        std::vector<TokenType>(),
        var->initializer != nullptr
    };
    
    currentScope->define(var->name, varSymbol);
    
    // 检查初始化表达式
    if (var->initializer) {
        TokenType initType = getExpressionType(var->initializer.get());
        checkAssignment(var->type, initType);
    }
}

void SemanticAnalyzer::visitBlock(Block* block) {
    enterScope();
    
    for (auto& stmt : block->statements) {
        stmt->accept(this);
    }
    
    exitScope();
}

void SemanticAnalyzer::visitIfStatement(IfStatement* ifStmt) {
    // 检查条件表达式类型
    TokenType condType = getExpressionType(ifStmt->condition.get());
    if (condType != TokenType::INT) {
        throw std::runtime_error("Condition must be of type int");
    }
    
    ifStmt->thenBranch->accept(this);
    if (ifStmt->elseBranch) {
        ifStmt->elseBranch->accept(this);
    }
}

void SemanticAnalyzer::visitWhileStatement(WhileStatement* whileStmt) {
    // 检查条件表达式类型
    TokenType condType = getExpressionType(whileStmt->condition.get());
    if (condType != TokenType::INT) {
        throw std::runtime_error("Condition must be of type int");
    }
    
    whileStmt->body->accept(this);
}

void SemanticAnalyzer::visitReturnStatement(ReturnStatement* returnStmt) {
    hasReturnStatement = true;
    
    if (returnStmt->value) {
        TokenType returnType = getExpressionType(returnStmt->value.get());
        if (!checkTypes(currentReturnType, returnType)) {
            throw std::runtime_error("Return type mismatch");
        }
    } else if (currentReturnType != TokenType::VOID) {
        throw std::runtime_error("Function must return a value");
    }
}

void SemanticAnalyzer::visitBinaryExpr(BinaryExpr* binary) {
    TokenType leftType = getExpressionType(binary->left.get());
    TokenType rightType = getExpressionType(binary->right.get());
    
    switch (binary->op) {
        case TokenType::PLUS:
        case TokenType::MINUS:
        case TokenType::MULTIPLY:
        case TokenType::DIVIDE:
            if (!checkTypes(leftType, rightType) || 
                (leftType != TokenType::INT && leftType != TokenType::FLOAT)) {
                throw std::runtime_error("Invalid operands for arithmetic operation");
            }
            break;
            
        case TokenType::EQUAL:
        case TokenType::NOT_EQUAL:
            if (!checkTypes(leftType, rightType)) {
                throw std::runtime_error("Cannot compare different types");
            }
            break;
            
        case TokenType::LESS:
        case TokenType::LESS_EQUAL:
        case TokenType::GREATER:
        case TokenType::GREATER_EQUAL:
            if (!checkTypes(leftType, rightType) || 
                (leftType != TokenType::INT && leftType != TokenType::FLOAT)) {
                throw std::runtime_error("Invalid operands for comparison");
            }
            break;
            
        case TokenType::ASSIGN:
            checkAssignment(leftType, rightType);
            break;
            
        default:
            throw std::runtime_error("Invalid binary operator");
    }
}

void SemanticAnalyzer::visitUnaryExpr(UnaryExpr* unary) {
    TokenType operandType = getExpressionType(unary->operand.get());
    
    if (unary->op == TokenType::MINUS) {
        if (operandType != TokenType::INT && operandType != TokenType::FLOAT) {
            throw std::runtime_error("Cannot negate non-numeric type");
        }
    }
}

void SemanticAnalyzer::visitLiteral(Literal* literal) {
    // 字面量类型已经在词法分析时确定
}

void SemanticAnalyzer::visitIdentifier(Identifier* id) {
    Symbol* symbol = currentScope->resolve(id->name);
    if (!symbol) {
        throw std::runtime_error("Undefined variable '" + id->name + "'");
    }
}

void SemanticAnalyzer::visitCallExpr(CallExpr* call) {
    Symbol* symbol = currentScope->resolve(call->callee);
    if (!symbol || symbol->type != SymbolType::FUNCTION) {
        throw std::runtime_error("Undefined function '" + call->callee + "'");
    }
    
    std::vector<TokenType> argTypes;
    for (auto& arg : call->arguments) {
        argTypes.push_back(getExpressionType(arg.get()));
    }
    
    checkFunctionCall(call->callee, argTypes);
}

void SemanticAnalyzer::enterScope() {
    currentScope = new Scope(currentScope);
}

void SemanticAnalyzer::exitScope() {
    Scope* oldScope = currentScope;
    currentScope = currentScope->getParent();
    delete oldScope;
}

bool SemanticAnalyzer::checkTypes(TokenType t1, TokenType t2) {
    return t1 == t2;
}

TokenType SemanticAnalyzer::getExpressionType(Expression* expr) {
    if (auto* literal = dynamic_cast<Literal*>(expr)) {
        if (literal->type == TokenType::INTEGER_LITERAL) return TokenType::INT;
        if (literal->type == TokenType::FLOAT_LITERAL) return TokenType::FLOAT;
        return literal->type;
    }
    
    if (auto* id = dynamic_cast<Identifier*>(expr)) {
        Symbol* symbol = currentScope->resolve(id->name);
        if (!symbol) {
            throw std::runtime_error("Undefined variable '" + id->name + "'");
        }
        return symbol->dataType;
    }
    
    if (auto* binary = dynamic_cast<BinaryExpr*>(expr)) {
        if (binary->op == TokenType::EQUAL || binary->op == TokenType::NOT_EQUAL ||
            binary->op == TokenType::LESS || binary->op == TokenType::LESS_EQUAL ||
            binary->op == TokenType::GREATER || binary->op == TokenType::GREATER_EQUAL) {
            return TokenType::INT;  // 比较运算返回布尔值（用int表示）
        }
        return getExpressionType(binary->left.get());
    }
    
    if (auto* unary = dynamic_cast<UnaryExpr*>(expr)) {
        return getExpressionType(unary->operand.get());
    }
    
    if (auto* call = dynamic_cast<CallExpr*>(expr)) {
        Symbol* symbol = currentScope->resolve(call->callee);
        if (!symbol) {
            throw std::runtime_error("Undefined function '" + call->callee + "'");
        }
        return symbol->dataType;
    }
    
    throw std::runtime_error("Invalid expression type");
}

void SemanticAnalyzer::checkAssignment(TokenType leftType, TokenType rightType) {
    if (leftType == rightType) {
        return;
    }
    
    // 允许整数到浮点数的隐式转换
    if (leftType == TokenType::FLOAT && rightType == TokenType::INT) {
        return;
    }
    
    throw std::runtime_error("Type mismatch in assignment");
}

void SemanticAnalyzer::checkFunctionCall(const std::string& name, const std::vector<TokenType>& argTypes) {
    Symbol* symbol = currentScope->resolve(name);
    if (!symbol || symbol->type != SymbolType::FUNCTION) {
        throw std::runtime_error("Undefined function '" + name + "'");
    }
    
    if (argTypes.size() != symbol->paramTypes.size()) {
        throw std::runtime_error("Wrong number of arguments for function '" + name + "'");
    }
    
    for (size_t i = 0; i < argTypes.size(); i++) {
        if (!checkTypes(argTypes[i], symbol->paramTypes[i])) {
            throw std::runtime_error("Type mismatch in argument " + std::to_string(i + 1) + 
                                   " of function '" + name + "'");
        }
    }
} 