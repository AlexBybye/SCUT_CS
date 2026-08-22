---
source_id: artificial-intelligence-intro-011
course_id: artificial_intelligence_intro
title: "A星算法"
original_file: "学科资料/人工智能导论/神之华工官方PPT，爱来自密歇根大学/A星算法.pdf"
document_role: note
year: 
locator_type: page
---

# A星算法

<!-- page: 1 -->

1.4 启发式图搜索

• 利用知识来引导搜索，达到减少搜索范
围，降低问题复杂度的目的。
• 启发信息的强度
– 强：降低搜索工作量，但可能导致找不到最

      优解
– 弱：一般导致工作量加大，极限情况下变为

      盲目搜索，但有可能找到最优解

46

![image](assets/assets/artificial-intelligence-intro-011/image-001.jpeg)

<!-- page: 2 -->

希望：

• 引入启发知识，在保证找到最佳解的情
况下，尽可能减少搜索范围，提高搜索
效率。

47

![image](assets/assets/artificial-intelligence-intro-011/image-002.jpeg)

<!-- page: 3 -->

基本思想

• 定义一个评价函数f，对当前的搜索状态
进行评估，找出一个最有希望的节点来
扩展。

48

![image](assets/assets/artificial-intelligence-intro-011/image-003.jpeg)

<!-- page: 4 -->

启发式搜索算法A（A算法）

• 评价函数的格式：

f(n) = g(n) + h(n)

f(n)：评价函数
h(n)：启发函数

49

![image](assets/assets/artificial-intelligence-intro-011/image-004.jpeg)

<!-- page: 5 -->

符号的意义

• g*(n)：从s到n的最小耗散值
• h*(n)：从n到g的最小耗散值
• f*(n)=g*(n)+h*(n)：从s经过n到g的最小耗
散值

• g(n)、h(n)、f(n)分别是g*(n)、h*(n)、f*(n)
的估计值

50

![image](assets/assets/artificial-intelligence-intro-011/image-005.jpeg)

<!-- page: 6 -->

A算法

1, OPEN:=(s), f(s):=g(s)+h(s);
2, LOOP: IF OPEN=( ) THEN EXIT(FAIL);
3, n:=FIRST(OPEN);
4, IF GOAL(n) THEN EXIT(SUCCESS);
5, REMOVE(n, OPEN), ADD(n, CLOSED);
6, EXPAND(n) →{mi},
计算f(n, mi):=g(n, mi)+h(mi);

51

![image](assets/assets/artificial-intelligence-intro-011/image-006.jpeg)

<!-- page: 7 -->

A算法（续）

ADD(mj, OPEN), 标记mj到n的指针；
IF f(n, mk)<f(mk) THEN f(mk):=f(n, mk),
标记mk到n的指针；
IF f(n, ml)<f(ml) THEN f(ml):=f(n, ml),
标记ml到n的指针, ADD(ml, OPEN);
7, OPEN中的节点按f值从小到大排序；
8, GO LOOP；

52

![image](assets/assets/artificial-intelligence-intro-011/image-007.jpeg)

<!-- page: 8 -->

一个A算法的例子

2    8    3
1    6    4
7          5

1    2    3
8          4
7    6    5

定义评价函数：

f(n) = g(n) + h(n)
g(n)为从初始节点到当前节点的耗散值
h(n)为当前节点“不在位”的将牌数

53

![image](assets/assets/artificial-intelligence-intro-011/image-008.jpeg)

<!-- page: 9 -->

h计算举例

1    2    3

2    8    3
1    6    4
7          5

8

4
5

7    6

h(n) =4

54

![image](assets/assets/artificial-intelligence-intro-011/image-009.jpeg)

<!-- page: 10 -->

s(4)

2   8   3
1   6   4
7        5

1

2

2   8   3
1   6   4
    7    5

2   8   3
1        4
7   6   5

2   8   3
1   6   4
7   5

A(6)
B(4)
C(6)

3
4

2   8   3
     1   4
7   6   5

2        3
1   8   4
7   6   5

2   8   3
1   4
7    6  5

D(5)
E(5)
F(6)

5

     8   3
2   1   4
7   6   5

2   8   3
7   1   4
    6    5

     2   3
1   8   4
7   6   5

2   3
1   8   4
7   6   5

I(5)
J(7)

G(6)
H(7)

6

1   2    3
     8   4
7   6   5

K(5)

1   2   3
8        4
7   6   5

1   2   3
7   8   4
     6   5

L(5)
M(7)
目标

55

![image](assets/assets/artificial-intelligence-intro-011/image-010.jpeg)

<!-- page: 11 -->

最佳图搜索算法A*（A*算法）

• 在A算法中，如果满足条件：
h(n)≤h*(n)
则A算法称为A*算法。

56

![image](assets/assets/artificial-intelligence-intro-011/image-011.jpeg)

<!-- page: 12 -->

A*条件举例

• 8数码问题
– h1(n) = “不在位”的将牌数
– h2(n) = 将牌“不在位”的距离和

1    2    3

将牌1：1
将牌2：1
将牌6：1
将牌8：2

2    8    3
1    6    4
7          5

8

4
5

7    6

57

![image](assets/assets/artificial-intelligence-intro-011/image-012.jpeg)

<!-- page: 13 -->

A*算法的性质

• 当问题有解时，A*算法一定能找到最佳
路径。
• 极端情况下，若h(n)≡0，一定能找到最佳
路径，此时，若g≡d，则A*算法等同于宽
度优先算法。
• 几个等式：
    f*(s) = f*(t) = h*(s) = g*(t) = f*(n)
    其中s是初始节点，t是目标节点，n是s到

t的最佳路径上的节点。

58

![image](assets/assets/artificial-intelligence-intro-011/image-013.jpeg)

<!-- page: 14 -->

A*算法的性质（续1）

定理1.1：

对有限图，如果从初始节点s到目标节点t
有路径存在，则算法A一定成功结束。

59

![image](assets/assets/artificial-intelligence-intro-011/image-014.jpeg)

<!-- page: 15 -->

A*算法的性质（续2）

引理1.1 ：

对无限图，若有从初始节点s到目标节点t
的路径，则A*不结束时，在OPEN表中
即使最小的一个f值也将增到任意大，或
有f(n)>f*(s)。

60

![image](assets/assets/artificial-intelligence-intro-011/image-015.jpeg)

<!-- page: 16 -->

A*算法的性质（续3）

引理1.2：

A*结束前，OPEN表中必存在f(n)≤f*(s)的
结点（n是在最佳路径上的结点）。

存在一个节点n，n在最佳路径上。
f(n) = g(n) + h(n)
       = g*(n)+h(n)
      ≤g*(n)+h*(n)
      = f*(n)
      = f*(s)

61

![image](assets/assets/artificial-intelligence-intro-011/image-016.jpeg)

<!-- page: 17 -->

A*算法的性质（续3）

定理1.2：

对无限图，若从初始节点s到目标节点t有
路径存在，则A*一定成功结束。

引理1.1：A*如果不结束，则OPEN中所有的n有

f(n) > f*(s)
引理1.2：在A*结束前，必存在节点n，使得

f(n) ≤ f*(s)
所以，如果A*不结束，将导致矛盾。

62

![image](assets/assets/artificial-intelligence-intro-011/image-017.jpeg)

<!-- page: 18 -->

A*算法的性质（续4）

推论1.1：

OPEN表上任一具有f(n)<f*(s)的节点n，
最终都将被A*选作扩展的节点。

   由定理1.2，知A*一定结束，由A*的结束

条件，OPEN表中f(t)最小时才结束。而
         f(t) ≥ f*(t) ＝ f*(s)

   所以f(n)<f*(s)的n，均被扩展。得证。

63

![image](assets/assets/artificial-intelligence-intro-011/image-018.jpeg)

<!-- page: 19 -->

A*算法的性质（续5）

定理1.3 (可采纳性定理)：

若存在从初始节点s到目标节点t有路径，
则A*必能找到最佳解结束。

64

![image](assets/assets/artificial-intelligence-intro-011/image-019.jpeg)

<!-- page: 20 -->

可采纳性的证明

• 由定理1.1、1.2知A*一定找到一条路径结束
• 设找到的路径s→ t不是最佳的（t为目标）
    则：f(t) = g(t) > f*(s)
• 由引理1.2知结束前OPEN中存在f(n)≤f*(s)的节点
n，所以
          f(n) ≤ f*(s) < f(t)
• 因此A*应选择n扩展，而不是t。与假设A*选择t
结束矛盾。得证。
• 注意：A*的结束条件

65

![image](assets/assets/artificial-intelligence-intro-011/image-020.jpeg)

<!-- page: 21 -->

A*算法的性质（续6）

推论1.2：

A*选作扩展的任一节点n，有f(n)≤f*(s)。

l 由引理1.2知在A*结束前，OPEN中存在

节点n’， f(n’)≤f*(s)

l 设此时A*选择n扩展。

l 如果n＝n’，则f(n)≤f*(s)，得证。

l 如果n≠ n’，由于A*选择n扩展，而不是n’，

所以有f(n) ≤ f(n’)≤f*(s)。得证。

66

![image](assets/assets/artificial-intelligence-intro-011/image-021.jpeg)

<!-- page: 22 -->

A*算法的性质（续7）
定理1.4：设对同一个问题定义了两个A*算

法A1和A2，若A2比A1有较多的启发信息，
即对所有非目标节点有h2(n) > h1(n)，则
在具有一条从s到t的路径的隐含图上，搜
索结束时，由A2所扩展的每一个节点，
也必定由A1所扩展，即A1扩展的节点数
至少和A2一样多。

简写：如果h2(n) > h1(n) (目标节点除外)，

则A1扩展的节点数≥A2扩展的节点数

67

![image](assets/assets/artificial-intelligence-intro-011/image-022.jpeg)

<!-- page: 23 -->

A*算法的性质（续7）

• 注意：
   在定理1.4中，评价指标是“扩展的节点

数”，也就是说，同一个节点无论被扩
展多少次，都只计算一次。

68

![image](assets/assets/artificial-intelligence-intro-011/image-023.jpeg)

<!-- page: 24 -->

定理1.4的证明

• 使用数学归纳法，对节点的深度进行归纳
• （1）当d(n)＝0时，即只有一个节点，显然
定理成立。
• （2）设d(n)≤k时定理成立。（归纳假设）
• （3）当d(n)=k+1时，用反证法。
• 设存在一个深度为k＋1的节点n，被A2扩展，
但没有被A1扩展。而由假设，A1扩展了n的
父节点，即n已经被生成了。因此当A1结束
时，n将被保留在OPEN中。

69

![image](assets/assets/artificial-intelligence-intro-011/image-024.jpeg)

<!-- page: 25 -->

定理1.4的证明（续1）

• 所以有：f1(n) ≥ f*(s)
• 即：g1(n)+h1(n) ≥ f*(s)
• 所以： h1(n) ≥ f*(s) - g1(n)
• 另一方面，由于A2扩展了n，有f2(n) ≤ f*(s)
• 即： h2(n) ≤ f*(s) – g2(n)                       (A)
• 由于d(n)=k时，A2扩展的节点A1一定扩展，有
           g1(n) ≤ g2(n)   (因为A2的路A1均走到了)
• 所以： h1(n) ≥ f*(s) - g1(n) ≥ f*(s) – g2(n)  (B)
• 比较A、B两式，有 h1(n) ≥ h2(n) ，与定理条件
矛盾。故定理得证。

70

![image](assets/assets/artificial-intelligence-intro-011/image-025.jpeg)

<!-- page: 26 -->

A*算法的改进

• 问题的提出：
因A算法第6步对ml类节点可能要重新放
回到OPEN表中，因此可能会导致多次重
复扩展同一个节点，导致搜索效率下降。

71

![image](assets/assets/artificial-intelligence-intro-011/image-026.jpeg)

<!-- page: 27 -->

一个例子：

OPEN表
CLOSED表

s(10)

s(10)

1

s(10)
A(7) B(8) C(9)

C(8)

6
3

A(7) s(10)
B(8) C(9) G(14)

1
1

B(8) s(10)
A(5) B(8) s(10)
C(9) A(5) s(10)
B(7) C(9) s(10)
A(4) B(7) C(9) s(10)

A(5) C(9) G(14)
C(9) G(12)

A(1)
B(5)

8

B(7) G(12)
A(4) G(12)

G 目标

G(11)

72

![image](assets/assets/artificial-intelligence-intro-011/image-027.jpeg)

<!-- page: 28 -->

出现多次扩展节点的原因

• 在前面的扩展中，并
没有找到从初始节点
到当前节点的最短路
径，如节点A。

s(10)

1

C(8)

6
3

1
1

A(1)
B(5)

8

G 目标

73

![image](assets/assets/artificial-intelligence-intro-011/image-028.jpeg)

<!-- page: 29 -->

解决的途径

• 对h加以限制
– 能否对h增加适当的限制，使得第一次扩展

一个节点时，就找到了从s到该节点的最短
路径。
• 对算法加以改进
– 能否对算法加以改进，避免或减少节点的多

次扩展。

74

![image](assets/assets/artificial-intelligence-intro-011/image-029.jpeg)

<!-- page: 30 -->

改进的条件

• 可采纳性不变
• 不多扩展节点
• 不增加算法的复杂性

75

![image](assets/assets/artificial-intelligence-intro-011/image-030.jpeg)

<!-- page: 31 -->

对h加以限制

• 定义：一个启发函数h，如果对所有节点
ni和nj，其中nj是ni的子节点，满足

h(ni) - h(nj) ≤ c(ni, nj)
h(t) = 0
或
         h(ni) ≤ c(ni, nj) + h(nj)

ni

c(ni,nj)

nj

h(ni)

h(t) = 0
    则称h是单调的。

h(nj)

76

![image](assets/assets/artificial-intelligence-intro-011/image-031.jpeg)

<!-- page: 32 -->

h单调的性质

• 定理1.5：
若h(n)是单调的，则A*扩展了节点n之后，
就已经找到了到达节点n的最佳路径。
即：当A*选n扩展时，有g(n)=g*(n)。

77

![image](assets/assets/artificial-intelligence-intro-011/image-032.jpeg)

<!-- page: 33 -->

定理1.5的证明

• 设n是A*扩展的任一节点。当n＝s时，定
理显然成立。下面考察n ≠s的情况。
• 设P＝(n0=s, n1, n2, …, nk=n)是s到n的最佳
路径
• P中一定有节点在CLOSED中，设P中最
后一个出现在CLOSED中的节点为nj，则
nj+1在OPEN中。

78

![image](assets/assets/artificial-intelligence-intro-011/image-033.jpeg)

<!-- page: 34 -->

定理1.5的证明（续1）

• 由单调限制条件，对P中任意节点ni有：
                  h(ni) ≤             C(ni, ni+1)+h(ni+1)

          g*(ni)+h(ni) ≤ g*(ni)+C(ni, ni+1)+h(ni+1)
• 由于ni 、ni+1在最佳路径上，所以：
       g*(ni+1) = g*(ni)+C(ni, ni+1)
• 带入上式有：
      g*(ni)+h(ni) ≤ g*(ni+1)+h(ni+1)
• 从i=j到i=k-1应用上不等式，有：
      g*(nj+1)+h(nj+1) ≤ g*(nk)+h(nk)
• 即：f(nj+1) ≤ g*(n)+h(n)
    注意：(nj在CLOSED中，nj+1在OPEN中)

79

![image](assets/assets/artificial-intelligence-intro-011/image-034.jpeg)

<!-- page: 35 -->

定理1.5的证明（续2）

• 重写上式：f(nj+1) ≤ g*(n)+h(n)
• 另一方面，A*选n扩展，必有：
        f(n) = g(n)+h(n) ≤ f(nj+1)
• 比较两式，有：
        g(n) ≤ g*(n)
• 但已知g*(n)是最佳路径的耗散值，所以
只有：g(n) = g*(n)。得证。

80

![image](assets/assets/artificial-intelligence-intro-011/image-035.jpeg)

<!-- page: 36 -->

h单调的性质（续）

• 定理1.6：
若h(n)是单调的，则由A*所扩展的节点
序列其f值是非递减的。即f(ni) ≤ f(nj)。

81

![image](assets/assets/artificial-intelligence-intro-011/image-036.jpeg)

<!-- page: 37 -->

定理1.6的证明

• 由单调限制条件，有：
        h(ni) – h(nj) ≤ C(ni, nj)

= f(ni)-g(ni)
= f(nj)-g(nj)

      f(ni)-g(ni) - f(nj)+g(nj) ≤ C(ni, nj)

= g(ni)+C(ni, nj)

      f(ni) - g(ni) - f(nj) + g(ni) + C(ni, nj) ≤ C(ni, nj)
      f(ni) - f(nj) ≤ 0，得证。

82

![image](assets/assets/artificial-intelligence-intro-011/image-037.jpeg)

<!-- page: 38 -->

h单调的例子

• 8数码问题：
– h为“不在位”的将牌数（ nj是ni的子节点）
                                1    （不在位->在位）

h(ni) - h(nj) =       0       (不在位->不在位)
                               -1    （在位->不在位）

h(t) = 0
c(ni, nj) = 1

   满足单调的条件。

83

![image](assets/assets/artificial-intelligence-intro-011/image-038.jpeg)

<!-- page: 39 -->

对算法加以改进

• 一些结论：
– OPEN表上任一具有f(n)< f*(s)的节点定会被

扩展。（推论1.1）
– A*选作扩展的任一节点，定有f(n)≤f*(s)。

（推论1.2）

84

![image](assets/assets/artificial-intelligence-intro-011/image-039.jpeg)

<!-- page: 40 -->

改进的出发点

f*(s)

OPEN = ( … …    … … )

f值小于f*(s)的节点
（NEST）
f值大于等于f*(s)的节点

fm：到目前为止已扩展节点的最大f值，用fm代替f*(s)

85

![image](assets/assets/artificial-intelligence-intro-011/image-040.jpeg)

<!-- page: 41 -->

修正过程A

1, OPEN:=(s), f(s)=g(s)+h(s), fm:=0;
2, LOOP: IF OPEN=( ) THEN EXIT(FAIL);
3, NEST:={ni|f(ni)<fm}
IF NEST ≠ ( ) THEN n:=NEST中g最小的节点(?)
ELSE n:=FIRST(OPEN), fm:=f(n);
4, …, 8: 同过程A。

86

![image](assets/assets/artificial-intelligence-intro-011/image-041.jpeg)

<!-- page: 42 -->

前面的例子：

OPEN表
CLOSED表
fm

s(10)

1

s(0+10)
s(0+10)
10

C(8)

6
3

A(6+1) B(3+5) C(1+8)
s(0+10) C(1+8)
10

1
1

A(6+1) B(2+5)
s(0+10) C(1+8) B(2+5)
10

A(1)
B(5)

A(3+1)
s(0+10)C(1+8)B(2+5)A(3+1)
10

8

G(11+0)

G 目标

87

![image](assets/assets/artificial-intelligence-intro-011/image-042.jpeg)
