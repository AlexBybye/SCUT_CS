import re

# 定义 token 类型及对应值
TOKEN_TYPES = {
    'EQ': '==',
    'NEQ': '!=',
    'LTE': '<=',
    'GTE': '>=',
    'ARRAY': '[]',
    'ELSE': 'else',
    'IF': 'if',
    'INT': 'int',
    'FLOAT': 'float',
    'RETURN': 'return',
    'VOID': 'void',
    'WHILE': 'while',
    'ADD': '+',
    'SUB': '-',
    'MUL': '*',
    'DIV': '/',
    'LT': '<',
    'GT': '>',
    'ASSIN': '=',
    'SEMICOLON': ';',
    'COMMA': ',',
    'LPARENTHESE': '(',
    'RPARENTHESE': ')',
    'LBRACKET': '[',
    'RBRACKET': ']',
    'LBRACE': '{',
    'RBRACE': '}',
    'IDENTIFIER': r'[a-zA-Z]+',
    'INTEGER': r'\d+',
    'FLOATPOINT': r'\d+\.\d+|\.\d+',
    'COMMENT': r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/',
    'BLANK': r'[ \t]+',
    'EOL': r'\n'
}

# 定义保留字
RESERVED_KEYWORDS = {
    'else': 'ELSE',
    'if': 'IF',
    'int': 'INT',
    'float': 'FLOAT',
    'return': 'RETURN',
    'void': 'VOID',
    'while': 'WHILE'
}


class Token:
    def __init__(self, token_type, value, line, pos_start, pos_end):
        self.type = token_type
        self.value = value
        self.line = line
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line}, {self.pos_start}-{self.pos_end})"


class LexicalAnalyzer:
    def __init__(self, input_string):
        self.input_string = input_string
        self.tokens = []
        self.current_pos = 0
        self.line = 1
        self.pos_in_line = 1

    def analyze(self):
        while self.current_pos < len(self.input_string):
            char = self.input_string[self.current_pos]

            # 处理注释
            if char == '/' and self.input_string[self.current_pos + 1] == '*':
                self.handle_comment()
                continue

            # 处理保留字和标识符
            if char.isalpha():
                identifier = self.handle_identifier()
                if identifier in RESERVED_KEYWORDS:
                    self.add_token(RESERVED_KEYWORDS[identifier], identifier)
                else:
                    self.add_token('IDENTIFIER', identifier)
                continue

            # 处理数字
            if char.isdigit() or char == '.':
                number = self.handle_number()
                if '.' in number:
                    self.add_token('FLOATPOINT', number)
                else:
                    self.add_token('INTEGER', number)
                continue

            # 处理运算符
            if char in '+-*/=<>':
                self.handle_operator()
                continue

            # 处理括号
            if char in '(){}[];,':
                self.add_token(self.get_bracket_type(char), char)
                self.current_pos += 1
                self.pos_in_line += 1
                continue

            # 处理空白字符
            if char in ' \t\n':
                self.handle_whitespace(char)
                continue

            # 处理错误字符
            self.add_token('ERROR', char)
            self.current_pos += 1
            self.pos_in_line += 1

        return self.tokens

    def handle_comment(self):
        start_pos = self.current_pos
        self.current_pos += 2
        self.pos_in_line += 2
        while self.current_pos < len(self.input_string) and not (
                self.input_string[self.current_pos] == '*' and self.input_string[self.current_pos + 1] == '/'):
            if self.input_string[self.current_pos] == '\n':
                self.line += 1
                self.pos_in_line = 1
            self.current_pos += 1
            self.pos_in_line += 1
        self.current_pos += 2
        self.pos_in_line += 2
        self.add_token('COMMENT', self.input_string[start_pos:self.current_pos])

    def handle_identifier(self):
        start_pos = self.current_pos
        while self.current_pos < len(self.input_string) and self.input_string[self.current_pos].isalpha():
            self.current_pos += 1
        identifier = self.input_string[start_pos:self.current_pos]
        self.pos_in_line += len(identifier)
        return identifier

    def handle_number(self):
        start_pos = self.current_pos
        while self.current_pos < len(self.input_string) and (
                self.input_string[self.current_pos].isdigit() or self.input_string[self.current_pos] == '.'):
            self.current_pos += 1
        number = self.input_string[start_pos:self.current_pos]
        self.pos_in_line += len(number)
        return number

    def handle_operator(self):
        start_pos = self.current_pos
        self.current_pos += 1
        operator = self.input_string[start_pos:self.current_pos]
        if self.current_pos < len(self.input_string) and self.input_string[self.current_pos] in '=!<>':
            self.current_pos += 1
            operator += self.input_string[self.current_pos - 1]
        self.pos_in_line += len(operator)
        self.add_token(self.get_operator_type(operator), operator)

    def handle_whitespace(self, char):
        start_pos = self.current_pos
        while self.current_pos < len(self.input_string) and self.input_string[self.current_pos] in ' \t\n':
            if self.input_string[self.current_pos] == '\n':
                self.line += 1
                self.pos_in_line = 1
            self.current_pos += 1
        whitespace = self.input_string[start_pos:self.current_pos]
        self.pos_in_line += len(whitespace)
        if '\n' in whitespace:
            self.add_token('EOL', '\n')
        else:
            self.add_token('BLANK', whitespace)

    def add_token(self, token_type, value):
        self.tokens.append(Token(token_type, value, self.line, self.pos_in_line, self.pos_in_line + len(value)))

    def get_bracket_type(self, char):
        bracket_map = {
            '(': 'LPARENTHESE',
            ')': 'RPARENTHESE',
            '[': 'LBRACKET',
            ']': 'RBRACKET',
            '{': 'LBRACE',
            '}': 'RBRACE',
            ';': 'SEMICOLON',
            ',': 'COMMA'
        }
        return bracket_map.get(char, 'ERROR')

    def get_operator_type(self, operator):
        operator_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            '<': 'LT',
            '>': 'GT',
            '=': 'ASSIN',
            '==': 'EQ',
            '!=': 'NEQ',
            '<=': 'LTE',
            '>=': 'GTE'
        }
        return operator_map.get(operator, 'ERROR')


# 测试
input_string = """
int main() {
    float x = 3.14;
    if (x > 0) {
        return x;
    } else {
        return -x;
    }
}
"""

analyzer = LexicalAnalyzer(input_string)
tokens = analyzer.analyze()

for token in tokens:
    print(token)