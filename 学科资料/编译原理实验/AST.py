from graphviz import Digraph
import ast
import os
import argparse

class ASTVisualizer(ast.NodeVisitor):
    def __init__(self):
        self.dot = Digraph()
        self.parent_stack = []

    def add_node(self, node, label):
        node_id = str(id(node))
        self.dot.node(node_id, label)
        if self.parent_stack:
            self.dot.edge(self.parent_stack[-1], node_id)
        return node_id

    def generic_visit(self, node):
        # 获取操作符符号
        label = node.__class__.__name__

        # 处理常量值（兼容Python 3.8+）
        if isinstance(node, ast.Constant):
            label = f"Const({node.value})"
        elif isinstance(node, ast.Num):  # 兼容旧版本Python
            label = f"Num({node.n})"

        node_id = self.add_node(node, label)
        self.parent_stack.append(node_id)
        super().generic_visit(node)
        self.parent_stack.pop()


def visualize_ast(expr):
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError:
        return "Invalid expression syntax"

    viz = ASTVisualizer()
    viz.visit(tree)
    return viz.dot


def process_file(input_path, output_dir="output"):
    """处理单个文件并生成可视化结果"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            expr = f.read().strip()
    except FileNotFoundError:
        return f"错误：文件 {input_path} 不存在"

    if not expr:
        return "错误：文件内容为空"

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成AST图
    result = visualize_ast(expr)
    if isinstance(result, str):
        return result  # 返回错误信息

    # 生成输出文件名
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_ast")

    # 保存并渲染
    result.render(output_path, format='png', cleanup=True)
    return f"AST已保存至 {output_path}.png"


# 使用示例
if __name__ == "__main__":
    # 替换旧的测试代码为命令行接口
    parser = argparse.ArgumentParser(description='AST可视化工具')
    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('-o', '--output', default="output", help='输出目录')
    args = parser.parse_args()

    msg = process_file(args.input, args.output)
    print(msg)