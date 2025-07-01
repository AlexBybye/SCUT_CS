#ifndef SYNTAX_ANALYZER_H
#define SYNTAX_ANALYZER_H

#include "syntax_tree.h"

syntax_tree *parse(const char *input_path);
void yyerror(const char *s);
int yarseyp(FILE *yyin);

#endif // SYNTAX_ANALYZER_H