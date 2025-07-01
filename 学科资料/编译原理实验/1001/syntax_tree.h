#ifndef SYNTAX_TREE_H
#define SYNTAX_TREE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct syntax_tree_node {
    char *name;
    int num_children;
    struct syntax_tree_node **children;
} syntax_tree_node;

typedef struct syntax_tree {
    syntax_tree_node *root;
} syntax_tree;

syntax_tree_node *new_syntax_tree_node(const char *name);
syntax_tree *new_syntax_tree();
void syntax_tree_add_child(syntax_tree_node *parent, syntax_tree_node *child);

#endif // SYNTAX_TREE_H