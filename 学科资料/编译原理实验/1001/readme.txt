1. 编译项目
你已经在build目录下用CMake和MSVC编译过项目，命令如下：
cmake ..
cmake --build .
如果你还没有编译，进入build目录后执行上面两条命令即可。
2. 准备测试源文件
你已经有一个测试文件test.c，内容如下：
int main() {
    int x = 10;
    int y = 20;
    if (x < y) {
        return x + y;
    } else {
        return x - y;
    }
}
你可以用记事本或VSCode等编辑器修改或新建其它测试文件。
3. 运行编译器前端
在build目录下，运行如下命令：
.\Debug\compiler.exe ..\test.c

.\Debug\compiler.exe 是生成的可执行文件路径
..\test.c 是你的测试源文件路径（相对于build目录）
4. 查看输出
程序会输出中间代码（IR），例如：
function main() {
entry:
  %t0 = 10
  store %t0, 
  %t1 = 20
  store %t1, 
  %t2 = load %x
  %t3 = load %y
  %t4 = lt %t2, %t3
  jz %t4, L1
L0:
  %t5 = load %x
  %t6 = load %y
  %t7 = add %t5, %t6
  ret %t7
  jmp
L1:
  %t8 = load %x
  %t9 = load %y
  %t10 = sub %t8, %t9
  ret %t10
  jmp
L2:
  ret
}
5. 常见问题
编码警告：如果有C4819警告，建议用VSCode等编辑器将所有.h和.cpp文件保存为UTF-8编码。
报错信息：如果有类型不匹配等报错，请根据提示检查你的源代码或语法。
总结
进入build目录
编译：cmake .. && cmake --build .
运行：.\Debug\compiler.exe ..\test.c
查看输出的中间代码
如需进一步扩展功能或有其它问题，欢迎随时提问！