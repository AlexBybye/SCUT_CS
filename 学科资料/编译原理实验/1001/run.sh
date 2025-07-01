
# 默认的输入文件
input_file="test.c"

# 检查是否指定了输入文件
if [ $# -eq 1 ]; then
    input_file="$1"
fi

# 检查输入文件是否存在
if [ ! -f "$input_file" ]; then
    echo "输入文件 $input_file 不存在。"
    exit 1
fi

# 编译源代码
g++ -o main main.cpp ir.cpp lexer.cpp parser.cpp semantic.cpp

# 检查编译是否成功
if [ $? -eq 0 ]; then
    echo "编译成功，开始运行程序..."
    # 运行程序并传递输入文件作为参数（如果需要的话）
    ./main "$input_file"
else
    echo "编译失败，请检查代码中的错误。"
    exit 1
fi