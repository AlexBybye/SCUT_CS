%option noyywrap
%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "syntax_tree.h"
#include "syntax_analyzer.h"
#include "y.tab.h"

int lines = 1;
int pos_start = 1;
int pos_end = 1;

void pass_node(char *text) {
    yylval.node = new_syntax_tree_node(text);
}
%}

DIGIT   [0-9]
LETTER  [a-zA-Z]
ID      {LETTER}+
INTEGER {DIGIT}+
FLOAT   ({DIGIT}+\.|{DIGIT}*\.{DIGIT}+)

%%

"=="       { pos_end = pos_start + 2; pass_node(yytext); return EQ; }
"!="       { pos_end = pos_start + 2; pass_node(yytext); return NEQ; }
"<="       { pos_end = pos_start + 2; pass_node(yytext); return LTE; }
">="       { pos_end = pos_start + 2; pass_node(yytext); return GTE; }
"else"     { pos_end = pos_start + 4; pass_node(yytext); return ELSE; }
"if"       { pos_end = pos_start + 2; pass_node(yytext); return IF; }
"int"      { pos_end = pos_start + 3; pass_node(yytext); return INT; }
"float"    { pos_end = pos_start + 5; pass_node(yytext); return FLOAT; }
"return"   { pos_end = pos_start + 6; pass_node(yytext); return RETURN; }
"void"     { pos_end = pos_start + 4; pass_node(yytext); return VOID; }
"while"    { pos_end = pos_start + 5; pass_node(yytext); return WHILE; }
"+"        { pos_end = pos_start + 1; pass_node(yytext); return ADD; }
"-"        { pos_end = pos_start + 1; pass_node(yytext); return SUB; }
"*"        { pos_end = pos_start + 1; pass_node(yytext); return MUL; }
"/"        { pos_end = pos_start + 1; pass_node(yytext); return DIV; }
"<"        { pos_end = pos_start + 1; pass_node(yytext); return LT; }
">"        { pos_end = pos_start + 1; pass_node(yytext); return GT; }
"="        { pos_end = pos_start + 1; pass_node(yytext); return ASSIN; }
";"        { pos_end = pos_start + 1; pass_node(yytext); return SEMICOLON; }
","        { pos_end = pos_start + 1; pass_node(yytext); return COMMA; }
"("        { pos_end = pos_start + 1; pass_node(yytext); return LPARENTHESE; }
")"        { pos_end = pos_start + 1; pass_node(yytext); return RPARENTHESE; }
"["        { pos_end = pos_start + 1; pass_node(yytext); return LBRACKET; }
"]"        { pos_end = pos_start + 1; pass_node(yytext); return RBRACKET; }
"{"        { pos_end = pos_start + 1; pass_node(yytext); return LBRACE; }
"}"        { pos_end = pos_start + 1; pass_node(yytext); return RBRACE; }
{ID}       { pos_end = pos_start + yyleng; pass_node(yytext); return IDENTIFIER; }
{INTEGER}  { pos_end = pos_start + yyleng; pass_node(yytext); return INTEGER; }
{FLOAT}    { pos_end = pos_start + yyleng; pass_node(yytext); return FLOATPOINT; }
"/*"([^*]|\*+[^*/])*\*+"/" {
    for (int i = 0; i < strlen(yytext); i++) {
        if (yytext[i] == '\n') {
            lines++;
            pos_end = 1;
        } else {
            pos_end++;
        }
    }
}
[ \t]      { pos_end = pos_start + yyleng; }
\n         { lines++; pos_start = 1; pos_end = 1; }
.          { pos_start = pos_end; pos_end += 1; printf("lexical analyze error at line %d pos %d: %s\n", lines, pos_start, yytext); }

%%