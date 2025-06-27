import random

# 获取用户输入并转换为整数
num_num = int(input("Please enter how many numbers you need: "))

# 初始化计数器
num = 0

# 生成并打印随机数
while num < num_num:
    num_need = random.randint(0, 10000)
    print(num_need, end=" ")
    num += 1