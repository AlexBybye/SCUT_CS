%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include "syntax_tree.h"

typedef struct {
    syntax_tree_node *node;
    // 可以加更多字段
} YYSTYPE;

#define YYSTYPE_IS_DECLARED 1

// external functions from lex
extern int yylex();
// external variables from lexical_analyzer module
extern int lines;
extern char *yytext;
extern int pos_end;
extern int pos_start;
extern FILE *yyin;
// Global syntax tree
syntax_tree *gt;
// Error reporting
void yyerror(const char *s);
// Helper functions written for you with love
syntax_tree_node *node(const char *node_name, int children_num, ...);
%}

%union {
    syntax_tree_node *node;
}

%token <node> ADD SUB MUL DIV
%token <node> LT LTE GT GTE EQ NEQ ASSIN
%token <node> SEMICOLON COMMA LPARENTHESE RPARENTHESE LBRACKET RBRACKET LBRACE RBRACE
%token <node> ELSE IF INT FLOAT RETURN VOID WHILE IDENTIFIER INTEGER FLOATPOINT

%left ADD SUB
%left MUL DIV
%nonassoc LT LTE GT GTE EQ NEQ
%right ASSIN
%nonassoc IFX
%nonassoc ELSE

%type <node> program declaration_list declaration var_declaration fun_declaration
%type <node> compound_stmt local_declarations statement_list statement expression_stmt selection_stmt iteration_stmt return_stmt
%type <node> expression var simple_expression additive_expression term factor
%type <node> type_specifier params param_list param args arg_list call
%type <node> relop  /* 添加 relop 的类型声明 */

%start program

%%

program : declaration_list { $$ = node("program", 1, $1); gt->root = $$; }

declaration_list : declaration_list declaration { $$ = node("declaration_list", 2, $1, $2); }
                 | declaration { $$ = node("declaration_list", 1, $1); }

declaration : var_declaration { $$ = node("declaration", 1, $1); }
            | fun_declaration { $$ = node("declaration", 1, $1); }

var_declaration : type_specifier IDENTIFIER SEMICOLON { $$ = node("var_declaration", 3, $1, $2, $3); }
                | type_specifier IDENTIFIER LBRACKET INTEGER RBRACKET SEMICOLON { $$ = node("var_declaration", 6, $1, $2, $3, $4, $5, $6); }

type_specifier : INT { $$ = node("type_specifier", 1, $1); }
               | FLOAT { $$ = node("type_specifier", 1, $1); }
               | VOID { $$ = node("type_specifier", 1, $1); }

fun_declaration : type_specifier IDENTIFIER LPARENTHESE params RPARENTHESE compound_stmt { $$ = node("fun_declaration", 6, $1, $2, $3, $4, $5, $6); }

params : param_list { $$ = node("params", 1, $1); }
       | VOID { $$ = node("params", 1, $1); }

param_list : param_list COMMA param { $$ = node("param_list", 3, $1, $2, $3); }
           | param { $$ = node("param_list", 1, $1); }

param : type_specifier IDENTIFIER { $$ = node("param", 2, $1, $2); }
      | type_specifier IDENTIFIER LBRACKET RBRACKET { $$ = node("param", 4, $1, $2, $3, $4); }

compound_stmt : LBRACE local_declarations statement_list RBRACE { $$ = node("compound_stmt", 4, $1, $2, $3, $4); }

local_declarations : local_declarations var_declaration { $$ = node("local_declarations", 2, $1, $2); }
                   | { $$ = node("local_declarations", 0); }

statement_list : statement_list statement { $$ = node("statement_list", 2, $1, $2); }
               | { $$ = node("statement_list", 0); }

statement : expression_stmt { $$ = node("statement", 1, $1); }
          | compound_stmt { $$ = node("statement", 1, $1); }
          | selection_stmt { $$ = node("statement", 1, $1); }
          | iteration_stmt { $$ = node("statement", 1, $1); }
          | return_stmt { $$ = node("statement", 1, $1); }

expression_stmt : expression SEMICOLON { $$ = node("expression_stmt", 2, $1, $2); }
                | SEMICOLON { $$ = node("expression_stmt", 1, $1); }

selection_stmt 
    : IF LPARENTHESE expression RPARENTHESE statement %prec IFX
        { $$ = node("selection_stmt", 5, $1, $2, $3, $4, $5); }
    | IF LPARENTHESE expression RPARENTHESE statement ELSE statement
        { $$ = node("selection_stmt", 7, $1, $2, $3, $4, $5, $6, $7); }


iteration_stmt : WHILE LPARENTHESE expression RPARENTHESE statement { $$ = node("iteration_stmt", 5, $1, $2, $3, $4, $5); }

return_stmt : RETURN SEMICOLON { $$ = node("return_stmt", 2, $1, $2); }
            | RETURN expression SEMICOLON { $$ = node("return_stmt", 3, $1, $2, $3); }

expression : var ASSIN expression { $$ = node("expression", 3, $1, $2, $3); }
           | simple_expression { $$ = node("expression", 1, $1); }

var : IDENTIFIER { $$ = node("var", 1, $1); }
    | IDENTIFIER LBRACKET expression RBRACKET { $$ = node("var", 4, $1, $2, $3, $4); }

simple_expression : additive_expression relop additive_expression { $$ = node("simple_expression", 3, $1, $2, $3); }
                  | additive_expression { $$ = node("simple_expression", 1, $1); }

relop : LTE { $$ = node("relop", 1, $1); }
      | LT { $$ = node("relop", 1, $1); }
      | GT { $$ = node("relop", 1, $1); }
      | GTE { $$ = node("relop", 1, $1); }
      | EQ { $$ = node("relop", 1, $1); }
      | NEQ { $$ = node("relop", 1, $1); }

additive_expression : additive_expression ADD term { $$ = node("additive_expression", 3, $1, $2, $3); }
                    | term { $$ = node("additive_expression", 1, $1); }

term : term MUL factor { $$ = node("term", 3, $1, $2, $3); }
     | factor { $$ = node("term", 1, $1); }

factor : LPARENTHESE expression RPARENTHESE { $$ = node("factor", 3, $1, $2, $3); }
       | var { $$ = node("factor", 1, $1); }
       | call { $$ = node("factor", 1, $1); }
       | INTEGER { $$ = node("factor", 1, $1); }
       | FLOATPOINT { $$ = node("factor", 1, $1); }

call : IDENTIFIER LPARENTHESE args RPARENTHESE { $$ = node("call", 4, $1, $2, $3, $4); }

args : arg_list { $$ = node("args", 1, $1); }
     | { $$ = node("args", 0); }

arg_list : arg_list COMMA expression { $$ = node("arg_list", 3, $1, $2, $3); }
         | expression { $$ = node("arg_list", 1, $1); }

%%

void yyerror(const char *s) {
    fprintf(stderr, "error at line %d column %d: %s\n", lines, pos_start, s);
}

syntax_tree *parse(const char *input_path) {
    if (input_path != NULL) {
        if (!(yyin = fopen(input_path, "r"))) {
            fprintf(stderr, "[ERR] Open input file %s failed.\n", input_path);
            exit(1);
        }
    } else {
        yyin = stdin;
    }

    lines = pos_start = pos_end = 1;
    gt = new_syntax_tree();
    yyrestart(yyin);
    yyparse();
    return gt;
}

syntax_tree_node *node(const char *name, int children_num, ...) {
    syntax_tree_node *p = new_syntax_tree_node(name);
    syntax_tree_node *child;
    if (children_num == 0) {
        child = new_syntax_tree_node("epsilon");
        syntax_tree_add_child(p, child);
    } else {
        va_list ap;
        va_start(ap, children_num);
        for (int i = 0; i < children_num; ++i) {
            child = va_arg(ap, syntax_tree_node *);
            syntax_tree_add_child(p, child);
        }
        va_end(ap);
    }
    return p;
}