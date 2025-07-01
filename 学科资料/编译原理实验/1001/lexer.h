#ifndef LEXER_H
#define LEXER_H

#include <string>
#include <vector>
#include <map>

// Token类型枚举
enum class TokenType {
    // 关键字
    IF, ELSE, WHILE, FOR, INT, FLOAT, VOID, RETURN,
    
    // 标识符和字面量
    IDENTIFIER, INTEGER_LITERAL, FLOAT_LITERAL,
    
    // 运算符
    PLUS, MINUS, MULTIPLY, DIVIDE, ASSIGN,
    EQUAL, NOT_EQUAL, LESS, GREATER, LESS_EQUAL, GREATER_EQUAL,
    
    // 分隔符
    SEMICOLON, COMMA, LEFT_PAREN, RIGHT_PAREN,
    LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET, RIGHT_BRACKET,
    
    // 特殊标记
    END_OF_FILE, ERROR
};

// Token结构体
struct Token {
    TokenType type;
    std::string lexeme;
    int line;
    int column;
};

class Lexer {
public:
    Lexer(const std::string& source);
    Token getNextToken();
    void reset();

private:
    std::string source;
    size_t currentPos;
    int currentLine;
    int currentColumn;
    
    static std::map<std::string, TokenType> keywords;
    
    char advance();
    char peek() const;
    bool isAtEnd() const;
    void skipWhitespace();
    Token makeToken(TokenType type, const std::string& lexeme);
    Token scanIdentifier();
    Token scanNumber();
    Token scanOperator();
};

#endif // LEXER_H 