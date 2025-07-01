#include <stdio.h>
#include <stdlib.h>

// 包含语法分析器相关头文件
#include "parser.h"

int main() {
    const char *input_file = "test.c"; // 直接指定输入文件为 test.c

    FILE *yyin = fopen(input_file, "r");
    if (!yyin) {
        perror("Failed to open input file");
        return EXIT_FAILURE;
    }

    // 调用 yyparse 进行语法分析
    int result = yyparse(yyin);

    fclose(yyin);

    if (result != 0) {
        fprintf(stderr, "Failed to parse the input file.\n");
        return EXIT_FAILURE;
    }

    printf("Successfully parsed the input file.\n");

    return EXIT_SUCCESS;
}