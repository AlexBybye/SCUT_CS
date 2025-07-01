#include "lexer.h"
#include "parser.h"
#include "semantic.h"
#include "ir.h"
#include <iostream>
#include <fstream>
#include <sstream>

std::string readFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file: " + filename);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

void printIR(const std::vector<std::unique_ptr<Function>>& functions) {
    for (const auto& func : functions) {
        std::cout << "function " << func->name << "(";
        for (size_t i = 0; i < func->params.size(); ++i) {
            if (i > 0) std::cout << ", ";
            std::cout << func->params[i];
        }
        std::cout << ") {\n";
        
        for (const auto& block : func->blocks) {
            std::cout << block->name << ":\n";
            for (const auto& inst : block->instructions) {
                std::cout << "  ";
                switch (inst.op) {
                    case IROp::ADD: std::cout << inst.result << " = add " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::SUB: std::cout << inst.result << " = sub " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::MUL: std::cout << inst.result << " = mul " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::DIV: std::cout << inst.result << " = div " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::EQ: std::cout << inst.result << " = eq " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::NE: std::cout << inst.result << " = ne " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::LT: std::cout << inst.result << " = lt " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::LE: std::cout << inst.result << " = le " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::GT: std::cout << inst.result << " = gt " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::GE: std::cout << inst.result << " = ge " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::JMP: std::cout << "jmp " << inst.arg1; break;
                    case IROp::JZ: std::cout << "jz " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::JNZ: std::cout << "jnz " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::LABEL: std::cout << inst.arg1 << ":"; break;
                    case IROp::LOAD: std::cout << inst.result << " = load " << inst.arg1; break;
                    case IROp::STORE: std::cout << "store " << inst.arg1 << ", " << inst.arg2; break;
                    case IROp::CALL: std::cout << inst.result << " = call " << inst.arg1; break;
                    case IROp::RET: 
                        if (!inst.arg1.empty()) {
                            std::cout << "ret " << inst.arg1;
                        } else {
                            std::cout << "ret";
                        }
                        break;
                    case IROp::ALLOCA: std::cout << inst.result << " = alloca"; break;
                    case IROp::CONST: std::cout << inst.result << " = " << inst.arg1; break;
                }
                std::cout << "\n";
            }
        }
        std::cout << "}\n\n";
    }
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file>\n";
        return 1;
    }
    
    try {
        // 读取输入文件
        std::string source = readFile(argv[1]);
        
        // 词法分析
        Lexer lexer(source);
        
        // 语法分析
        Parser parser(lexer);
        auto program = parser.parse();
        
        // 语义分析
        SemanticAnalyzer semantic;
        semantic.analyze(program.get());
        
        // 中间代码生成
        IRGenerator ir;
        auto functions = ir.generate(program.get());
        
        // 打印生成的IR代码
        printIR(functions);
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    
    return 0;
} 