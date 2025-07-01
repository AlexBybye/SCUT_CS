#include "syntax_tree.h"

syntax_tree_node *new_syntax_tree_node(const char *name) {
    syntax_tree_node *node = (syntax_tree_node *)malloc(sizeof(syntax_tree_node));
    node->name = strdup(name);
    node->num_children = 0;
    node->children = NULL;
    return node;
}

syntax_tree *new_syntax_tree() {
    syntax_tree *tree = (syntax_tree *)malloc(sizeof(syntax_tree));
    tree->root = NULL;
    return tree;
}

void syntax_tree_add_child(syntax_tree_node *parent, syntax_tree_node *child) {
    parent->num_children++;
    parent->children = (syntax_tree_node **)realloc(parent->children, parent->num_children * sizeof(syntax_tree_node *));
    parent->children[parent->num_children - 1] = child;
}