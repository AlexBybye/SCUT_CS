#include "lexer.h"
#include <cctype>

std::map<std::string, TokenType> Lexer::keywords = {
    {"if", TokenType::IF},
    {"else", TokenType::ELSE},
    {"while", TokenType::WHILE},
    {"for", TokenType::FOR},
    {"int", TokenType::INT},
    {"float", TokenType::FLOAT},
    {"void", TokenType::VOID},
    {"return", TokenType::RETURN}
};

Lexer::Lexer(const std::string& source) 
    : source(source), currentPos(0), currentLine(1), currentColumn(1) {}

Token Lexer::getNextToken() {
    skipWhitespace();
    
    if (isAtEnd()) {
        return makeToken(TokenType::END_OF_FILE, "");
    }
    
    char c = peek();
    
    if (isalpha(c) || c == '_') {
        return scanIdentifier();
    }
    
    if (isdigit(c)) {
        return scanNumber();
    }
    
    return scanOperator();
}

void Lexer::reset() {
    currentPos = 0;
    currentLine = 1;
    currentColumn = 1;
}

char Lexer::advance() {
    char c = source[currentPos++];
    if (c == '\n') {
        currentLine++;
        currentColumn = 1;
    } else {
        currentColumn++;
    }
    return c;
}

char Lexer::peek() const {
    return source[currentPos];
}

bool Lexer::isAtEnd() const {
    return currentPos >= source.length();
}

void Lexer::skipWhitespace() {
    while (!isAtEnd() && isspace(peek())) {
        advance();
    }
}

Token Lexer::makeToken(TokenType type, const std::string& lexeme) {
    return Token{type, lexeme, currentLine, static_cast<int>(currentColumn - lexeme.length())};
}

Token Lexer::scanIdentifier() {
    std::string lexeme;
    while (!isAtEnd() && (isalnum(peek()) || peek() == '_')) {
        lexeme += advance();
    }
    
    auto it = keywords.find(lexeme);
    if (it != keywords.end()) {
        return makeToken(it->second, lexeme);
    }
    
    return makeToken(TokenType::IDENTIFIER, lexeme);
}

Token Lexer::scanNumber() {
    std::string lexeme;
    bool hasDecimalPoint = false;
    
    while (!isAtEnd() && (isdigit(peek()) || peek() == '.')) {
        if (peek() == '.') {
            if (hasDecimalPoint) break;
            hasDecimalPoint = true;
        }
        lexeme += advance();
    }
    
    return makeToken(hasDecimalPoint ? TokenType::FLOAT_LITERAL : TokenType::INTEGER_LITERAL, lexeme);
}

Token Lexer::scanOperator() {
    char c = advance();
    std::string lexeme(1, c);
    
    switch (c) {
        case '+': return makeToken(TokenType::PLUS, lexeme);
        case '-': return makeToken(TokenType::MINUS, lexeme);
        case '*': return makeToken(TokenType::MULTIPLY, lexeme);
        case '/': return makeToken(TokenType::DIVIDE, lexeme);
        case ';': return makeToken(TokenType::SEMICOLON, lexeme);
        case ',': return makeToken(TokenType::COMMA, lexeme);
        case '(': return makeToken(TokenType::LEFT_PAREN, lexeme);
        case ')': return makeToken(TokenType::RIGHT_PAREN, lexeme);
        case '{': return makeToken(TokenType::LEFT_BRACE, lexeme);
        case '}': return makeToken(TokenType::RIGHT_BRACE, lexeme);
        case '[': return makeToken(TokenType::LEFT_BRACKET, lexeme);
        case ']': return makeToken(TokenType::RIGHT_BRACKET, lexeme);
        case '=':
            if (!isAtEnd() && peek() == '=') {
                advance();
                return makeToken(TokenType::EQUAL, "==");
            }
            return makeToken(TokenType::ASSIGN, lexeme);
        case '!':
            if (!isAtEnd() && peek() == '=') {
                advance();
                return makeToken(TokenType::NOT_EQUAL, "!=");
            }
            break;
        case '<':
            if (!isAtEnd() && peek() == '=') {
                advance();
                return makeToken(TokenType::LESS_EQUAL, "<=");
            }
            return makeToken(TokenType::LESS, lexeme);
        case '>':
            if (!isAtEnd() && peek() == '=') {
                advance();
                return makeToken(TokenType::GREATER_EQUAL, ">=");
            }
            return makeToken(TokenType::GREATER, lexeme);
    }
    
    return makeToken(TokenType::ERROR, lexeme);
} 