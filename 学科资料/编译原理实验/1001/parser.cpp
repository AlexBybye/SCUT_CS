#include "parser.h"
#include <stdexcept>

Parser::Parser(Lexer& lexer) : lexer(lexer) {
    advance();
}

void Parser::advance() {
    previous = current;
    current = lexer.getNextToken();
}

bool Parser::check(TokenType type) const {
    return current.type == type;
}

bool Parser::match(TokenType type) {
    if (check(type)) {
        advance();
        return true;
    }
    return false;
}

Token Parser::consume(TokenType type, const std::string& message) {
    if (check(type)) {
        Token token = current;
        advance();
        return token;
    }
    throw std::runtime_error(message);
}

std::unique_ptr<Program> Parser::parse() {
    return parseProgram();
}

std::unique_ptr<Program> Parser::parseProgram() {
    auto program = std::make_unique<Program>();
    
    while (!check(TokenType::END_OF_FILE)) {
        program->functions.push_back(parseFunctionDecl());
    }
    
    return program;
}

std::unique_ptr<FunctionDecl> Parser::parseFunctionDecl() {
    TokenType returnType = current.type;
    advance();
    
    std::string name = consume(TokenType::IDENTIFIER, "Expected function name.").lexeme;
    
    consume(TokenType::LEFT_PAREN, "Expected '(' after function name.");
    
    std::vector<std::pair<std::string, TokenType>> params;
    if (!check(TokenType::RIGHT_PAREN)) {
        do {
            TokenType paramType = current.type;
            advance();
            std::string paramName = consume(TokenType::IDENTIFIER, "Expected parameter name.").lexeme;
            params.emplace_back(paramName, paramType);
        } while (match(TokenType::COMMA));
    }
    
    consume(TokenType::RIGHT_PAREN, "Expected ')' after parameters.");
    consume(TokenType::LEFT_BRACE, "Expected '{' before function body.");
    
    auto body = parseBlock();
    
    return std::make_unique<FunctionDecl>(name, std::move(params), returnType, std::move(body));
}

std::unique_ptr<VarDecl> Parser::parseVarDecl() {
    TokenType type = current.type;
    advance();
    
    std::string name = consume(TokenType::IDENTIFIER, "Expected variable name.").lexeme;
    
    std::unique_ptr<Expression> initializer = nullptr;
    if (match(TokenType::ASSIGN)) {
        initializer = parseExpression();
    }
    
    consume(TokenType::SEMICOLON, "Expected ';' after variable declaration.");
    
    return std::make_unique<VarDecl>(name, type, std::move(initializer));
}

std::unique_ptr<Block> Parser::parseBlock() {
    std::vector<std::unique_ptr<Statement>> statements;
    
    while (!check(TokenType::RIGHT_BRACE) && !check(TokenType::END_OF_FILE)) {
        statements.push_back(parseStatement());
    }
    
    consume(TokenType::RIGHT_BRACE, "Expected '}' after block.");
    
    return std::make_unique<Block>(std::move(statements));
}

std::unique_ptr<Statement> Parser::parseStatement() {
    if (match(TokenType::IF)) return parseIfStatement();
    if (match(TokenType::WHILE)) return parseWhileStatement();
    if (match(TokenType::RETURN)) return parseReturnStatement();
    if (current.type == TokenType::INT || current.type == TokenType::FLOAT) return parseVarDecl();
    
    auto expr = parseExpression();
    consume(TokenType::SEMICOLON, "Expected ';' after expression.");
    return std::make_unique<ReturnStatement>(std::move(expr));
}

std::unique_ptr<IfStatement> Parser::parseIfStatement() {
    consume(TokenType::LEFT_PAREN, "Expected '(' after 'if'.");
    auto condition = parseExpression();
    consume(TokenType::RIGHT_PAREN, "Expected ')' after if condition.");
    
    consume(TokenType::LEFT_BRACE, "Expected '{' before then branch.");
    auto thenBranch = parseBlock();
    
    std::unique_ptr<Block> elseBranch = nullptr;
    if (match(TokenType::ELSE)) {
        consume(TokenType::LEFT_BRACE, "Expected '{' before else branch.");
        elseBranch = parseBlock();
    }
    
    return std::make_unique<IfStatement>(std::move(condition), std::move(thenBranch), std::move(elseBranch));
}

std::unique_ptr<WhileStatement> Parser::parseWhileStatement() {
    consume(TokenType::LEFT_PAREN, "Expected '(' after 'while'.");
    auto condition = parseExpression();
    consume(TokenType::RIGHT_PAREN, "Expected ')' after while condition.");
    
    consume(TokenType::LEFT_BRACE, "Expected '{' before while body.");
    auto body = parseBlock();
    
    return std::make_unique<WhileStatement>(std::move(condition), std::move(body));
}

std::unique_ptr<ReturnStatement> Parser::parseReturnStatement() {
    std::unique_ptr<Expression> value = nullptr;
    if (!check(TokenType::SEMICOLON)) {
        value = parseExpression();
    }
    
    consume(TokenType::SEMICOLON, "Expected ';' after return value.");
    
    return std::make_unique<ReturnStatement>(std::move(value));
}

std::unique_ptr<Expression> Parser::parseExpression() {
    return parseAssignment();
}

std::unique_ptr<Expression> Parser::parseAssignment() {
    auto expr = parseEquality();
    
    if (match(TokenType::ASSIGN)) {
        auto value = parseAssignment();
        
        if (auto* id = dynamic_cast<Identifier*>(expr.get())) {
            return std::make_unique<BinaryExpr>(TokenType::ASSIGN, std::move(expr), std::move(value));
        }
        
        throw std::runtime_error("Invalid assignment target.");
    }
    
    return expr;
}

std::unique_ptr<Expression> Parser::parseEquality() {
    auto expr = parseComparison();
    
    while (match(TokenType::EQUAL) || match(TokenType::NOT_EQUAL)) {
        TokenType op = previous.type;
        auto right = parseComparison();
        expr = std::make_unique<BinaryExpr>(op, std::move(expr), std::move(right));
    }
    
    return expr;
}

std::unique_ptr<Expression> Parser::parseComparison() {
    auto expr = parseTerm();
    
    while (match(TokenType::LESS) || match(TokenType::LESS_EQUAL) ||
           match(TokenType::GREATER) || match(TokenType::GREATER_EQUAL)) {
        TokenType op = previous.type;
        auto right = parseTerm();
        expr = std::make_unique<BinaryExpr>(op, std::move(expr), std::move(right));
    }
    
    return expr;
}

std::unique_ptr<Expression> Parser::parseTerm() {
    auto expr = parseFactor();
    
    while (match(TokenType::PLUS) || match(TokenType::MINUS)) {
        TokenType op = previous.type;
        auto right = parseFactor();
        expr = std::make_unique<BinaryExpr>(op, std::move(expr), std::move(right));
    }
    
    return expr;
}

std::unique_ptr<Expression> Parser::parseFactor() {
    auto expr = parseUnary();
    
    while (match(TokenType::MULTIPLY) || match(TokenType::DIVIDE)) {
        TokenType op = previous.type;
        auto right = parseUnary();
        expr = std::make_unique<BinaryExpr>(op, std::move(expr), std::move(right));
    }
    
    return expr;
}

std::unique_ptr<Expression> Parser::parseUnary() {
    if (match(TokenType::MINUS)) {
        auto operand = parseUnary();
        return std::make_unique<UnaryExpr>(TokenType::MINUS, std::move(operand));
    }
    
    return parsePrimary();
}

std::unique_ptr<Expression> Parser::parsePrimary() {
    if (match(TokenType::INTEGER_LITERAL) || match(TokenType::FLOAT_LITERAL)) {
        return std::make_unique<Literal>(previous.type, previous.lexeme);
    }
    
    if (match(TokenType::IDENTIFIER)) {
        std::string name = previous.lexeme;
        
        if (match(TokenType::LEFT_PAREN)) {
            return parseCall(name);
        }
        
        return std::make_unique<Identifier>(name);
    }
    
    if (match(TokenType::LEFT_PAREN)) {
        auto expr = parseExpression();
        consume(TokenType::RIGHT_PAREN, "Expected ')' after expression.");
        return expr;
    }
    
    throw std::runtime_error("Expected expression.");
}

std::unique_ptr<CallExpr> Parser::parseCall(const std::string& callee) {
    std::vector<std::unique_ptr<Expression>> arguments;
    
    if (!check(TokenType::RIGHT_PAREN)) {
        do {
            arguments.push_back(parseExpression());
        } while (match(TokenType::COMMA));
    }
    
    consume(TokenType::RIGHT_PAREN, "Expected ')' after arguments.");
    
    return std::make_unique<CallExpr>(callee, std::move(arguments));
} 