### 部署在竞赛，名称“模拟测试1”，时间：11月10日20:00-11月12日20:00

### 图像相似度

### 【题目描述】

[]()给出两幅相同大小的黑白图像（用0-1矩阵）表示，求它们的相似度。说明：若两幅图像在相同位置上的像素点颜色相同，则称它们在该位置具有相同的像素点。两幅图像的相似度定义为相同像素点数占总像素点数的百分比。

### 【输入】

第一行包含两个整数m和n，表示图像的行数和列数，中间用单个空格隔开。1≤m≤100, 1≤n≤100。

之后m行，每行n个整数0或1，表示第一幅黑白图像上各像素点的颜色。相邻两个数之间用单个空格隔开。

之后m行，每行n个整数0或1，表示第二幅黑白图像上各像素点的颜色。相邻两个数之间用单个空格隔开。

### 【输出】

- 一个实数，表示相似度（以百分比的形式给出），精确到小数点后两位。

### 【输入样例】

- 3 3
- 1 0 1
- 0 0 1
- 1 1 0
- 1 1 0
- 0 0 1
- 0 0 1

### 【输出样例】

- 44

### 【测试输入】

- 5 5
- 1 0 1 0 1
- 0 1 0 1 0
- 1 1 1 1 1
- 0 0 0 0 0
- 1 1 0 1 1
- 0 1 1 1 0
- 1 0 0 0 1
- 1 1 1 1 1
- 0 1 1 0 1
- 1 1 1 0 0

### []()【测试输出】

- 00

### []()【提示】

### 支持多组测试数据。

### 【参考代码】

- #include`iostream`
- #include`iomanip`
- using namespace std;

int main()

{

int m,n;

while(cin>>m>>n)

{

int a[m][n], b[m][n], count=0;

double sim;

for(int i=0;i<m;i++)

{

for(int j=0;j<n;j++)cin>>a[i][j];

}

for(int i=0;i<m;i++)

{

for(int j=0;j<n;j++)cin>>b[i][j];

}

for(int i=0;i<m;i++)

{

for(int j=0;j<n;j++)

{

if(a[i][j]==b[i][j])count++;

}

}

sim=100*double(count)/(m*n);

cout<<fixed<<setprecision(2)<<sim<<endl;

}

return 0;

}

### B Lucky Word

### 【题目描述】

对于输入单词，假设maxn是单词中出现次数最多的字母的出现次数，minn是单词中出现次数最少的字母的出现次数，如果maxn-minn是一个质数，那么这个单词是Lucky Word。

### 【输入】

只有一行，是一个单词，其中只可能出现小写字母，并且长度小于100。

### 【输出】

共两行，第一行是一个字符串，假设输入的的单词是Lucky Word，那么输出“Lucky Word”，否则输出“No Answer”；

[]()第二行是一个整数，如果输入单词是Lucky Word，输出maxn-minn的值，否则输出0。

### 【输入样例】

error

olympic

### 【输出样例】

Lucky Word

2

No Answer

0

### 【测试输入】

a

Hello

possess

### 【输出样例】

No Answer

0

No Answer

0

Lucky Word

3

### []()【提示】

### 支持多组测试数据。

### 【参考代码】

#include`iostream`

using namespace std;

bool check(int number)

{

if(number<=1)return false;

for(int j=2;j<number;j++)

{

if(number%j==0)return false;

}

return true;

}

int main()

{

string word;

while(cin>>word)

{

char letter[26];

for(int i=0;i<26;i++)letter[i]=0;

for(int i=0;i<100;i++)

{

if(int(word[i])>122||int(word[i])<97)break;

int num=int(word[i])-97;

letter[num]++;

}

int min=0,max=0;

bool s=true;

for(int i=0;i<26;i++)

{

if(letter[i]==0)continue;

if(s)

{

min=letter[i];

s=false;

}

if(letter[i]>max)max=letter[i];

else if(letter[i]<min)min=letter[i];

}

if (check(max-min))cout<<"Lucky Word"<<endl<<max-min<<endl;

else cout<<"No Answer"<<endl<<0<<endl;

}

return 0;

}

### 

### C 整数去重

### 【题目描述】

给定含有n个整数的序列，要求对这个序列进行去重操作。所谓去重，是指对这个序列中每个重复出现的数，只保留该数第一次出现的位置，删除其余位置。

### 【输入】

输入包含两行：

第一行包含一个正整数n（1≤n≤20000），表示第二行序列中数字的个数；

第二行包含n个整数，整数之间以一个空格分开。每个整数大于等于10、小于等于5000。

### 【输出】

输出只有一行，按照输入的顺序输出其中不重复的数字，整数之间用一个空格分开。

### 【输入样例】

- 5
- 10 12 93 12 75

### 【输出样例】

- 10 12 93 75

### 

- **【参考代码】**
- []()#include`iostream`
- using namespace std;

int main()

{

int n;

bool flag;

cin>>n;

int a[n];

for(int i=0;i<n;i++) cin>>a[i];

for(int i=0;i<n;i++)

{ flag=0;

for (int j=i-1;j>=0;j--)

if (a[i]==a[j]) flag=1;

if (flag==0)

cout<<a[i]<<" ";

}

return 0;

}

%%%%%%%%%%%%%%

#include`iostream`

using namespace std;

int main()

{

int n,max=0;

cin>>n;

int a[n],b[n];

for(int i=0;i<n;i++)

{

cin>>a[i];

bool s=false;

for(int j=0;j<max;j++)

{

if(a[i]==b[j])

{

s=true;

break;

}

}

if(s)continue;

b[max]=a[i];

max++;

[]()cout<<a[i]<<" ";

}

return 0;

}

## D 句子逆序

## Description

输入一个条英文语句，逆序输出句子中的单词，句子中的单词都由空格隔开。

## Input

第一行为整数T代表接下来输入的句子数量，接下来T行表示T条句子，句子中的单词用空格隔开。

## Output

输出每个句子逆序的结果，单词之间用空格隔开，每组输出用换行符隔开。

## Sample Input

3

oiwe dsdjk HELL OLOL

Hello World hello world OOO sdsd

po op my news lk lks

## Sample Output

OLOL HELL dsdjk oiwe

sdsd OOO world hello World Hello

lks lk news my op po

## TestInput

10

- KKL oksd lll lpr rid
- z l b d c a
- PLOE dsdsk HELLo hells heLLk
- plwe ddf LPsd lpfff array
- hao pw LPLP killl
- plo MMM aad alpe ALO ppls lolo lolol
- PLS PLSW PLSwr plswwe Plseee
- lps alal ffff lke fdfd lpe
- lm LMP mlss rrr oit oip oiddd oiq
- plro fdfd jke lgsd klr klggg klweee

## TestOutput

- rid lpr lll oksd KKL
- a c d b l z
- heLLk hells HELLo dsdsk PLOE
- array lpfff LPsd ddf plwe
- killl LPLP pw hao
- lolol lolo ppls ALO alpe aad MMM plo
- Plseee plswwe PLSwr PLSW PLS
- lpe fdfd lke ffff alal lps
- oiq oiddd oip oit rrr mlss LMP lm
- klweee klggg klr lgsd jke fdfd plro

## Source Code

#include `iostream`

using namespace std;

int main()

{

char *str = new char[100];

int length = 0;

int T;

cin>>T;

cin.get();

while(T--)

{

while((str[length] = getchar()))

{

length++;

if(str[length-1] == '\n')

{

length--;

char vb[100]={0};

int num = 0;

for(int i = length-1;i >= 0;i--)

{

if((str[i] >= 'a' && str[i] <= 'z') || (str[i] >= 'A' && str[i] <= 'Z'))

{

vb[num] = str[i];

num++;

}

else

{

for(int j = num-1;j >= 0;j--)

{

cout<<vb[j];

}

cout<<" ";

num = 0;

}

if(i == 0)

{

for(int k = num-1;k >= 0;k--)

{

cout<<vb[k];

}

}

}

cout<<endl;

length = 0;

break;

}

}

}

return 0;

}

## 

## E 放大的“X”

## Description

设计一个函数，在屏幕上打印出一个放大的“X”，输入输出示例如sample。

## Input

输入第一行为一个整数T，代表接下来T组测试数据。

接下来有T行，每一行有一个正奇数（3=<n<=79）表示放大的规格。

## Output

输出放大之后的“X”，每组数据用换行符隔开。

## Sample Input

2

3

- 5

## Sample Output

- X X
- X
- X X
- X X
- X X
- X
- X X
- X X

## TestInput

- 10
- 3
- 5
- 9
- 15
- 13
- 7
- 15
- 11
- 19
- 21

## TestOutput

- X X
- X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X
- X X

## Source Code

#include `iostream`

#include `cstdio`

using namespace std;

void X_Draw(const int &, const int *n);

int main() {

int T;

cin >> T;

int n[T];

for (int i = 0; i < T; i++)

cin >> n[i];

X_Draw(T, n);

return 0;

}

void X_Draw(const int &T, const int *n) {

for (int t = 0; t < T; ++t){

int len = n[t];

for (int i = 0; i < len; ++i){

for (int j = 0; j < len; ++j){

if ((j == i) || ((i + j) == (len - 1))){

printf("X");

}

else{

//右半部分空格不需要打印(即右半边i<j区域)，否则PE输出格式错误

//printf(" ");

//左半边空格打印

if(i*2 <len-1){

if(i+j<len){

printf(" ");

}

}

//右半边上下两个三角形区域空格打印

else{

if( i>=j ){

printf(" ");

}

}

}

}

printf("\n");

}

}

}

## F 孪生数字

## Description

如果一个整数，乘以2之后，得到的另一个整数中的每一位的数字以及出现的次数都与原来的数字相同，只是排序不同，那么我们说这两个数是孪生数字。比如整数123456789，乘以2之后得到246913578，两个整数中每一位出现的次数都一致，现在输入一个整数，判断是不是孪生数字。

## Input

输入第一行为整数T，代表接下来的T组数据，接着输入T个整数，每个整数都不会超过20位。

## Output

如果该整数是孪生数字，则输出Yes，否则输出No，每组整数的结果用换行符隔开。

## Sample Input

3

123456789

1234567899

11111111221122111232

## Sample Output

Yes

Yes

No

## TestInput

14

456789123

1234567899999

12345678999124567893

246913578

493827156

46935781212345678999

483925617124567893

135782469493815627

12354521254787852546

4254789854525

12365254587852356985

12365452541252369587

1252221121214141

123

## TestOutput

Yes

Yes

Yes

Yes

Yes

Yes

Yes

Yes

No

No

No

No

No

No

## Source Code

#include<stdio.h>

#include`iostream`

#include`string`

using namespace std;

int main()

{

int ans[10]={0};

char num1[22]={0};

char num2[22]={0};

int T;

cin>>T;

while(T--)

{

cin>>num1;

int i,di = 0, jin = 0,ji = 0;

for (i = 21; num1[i] == 0; i--);

for ( ; i >= 0; i -- )

{

ji = (num1[i] - '0') * 2; //ji是翻倍后的结果

ans[num1[i] - '0'] ++;//ans对原数相应位的个数++

di = ji % 10;//*2后的当前位的数字

num2[i] = di + jin + '0';

ans[num2[i] - '0'] --;//ans对结果数的相应位的个数--

jin = (ji + jin) / 10;

}

if (jin != 0) ans[jin] ++;

for (i = 1; i < 10; i++)if (ans[i] != 0)break;//判断ans是否全部都为0，若是，则说明原数和结果数是相同的排列

if (i == 10)

{

cout<<"Yes"<<endl;

}

else

{

cout<<"No"<<endl;

}

for(int k = 0;k<22;k++)

{

num1[k] = 0;

num2[k] = 0;

if(k<10)

{

ans[k] = 0;

}

}

}

}

%%%%%%%%%%%%%%%%%%%%%%%%%

#include`iostream`

#include`string`

using namespace std;

int main()

{

int T,i,n1,n2,temp,len;

char num1[100];

int count1[10]={0};

int count2[10]={0};

bool flag;

cin>>T;

while(T--)

{

cin>>num1;

temp=0;

for ( i=0; num1[i]!='\0';i++);

len=i;

cout<<len<<endl;

for (i=len-1; i>=0;i--)

{

n1=num1[i]-'0';

count1[n1]++;

n2=n1*2+temp;

if (n2>10)

temp=1;

else

temp=0;

count2[n2%10]++;

}

if (temp)

{

count2[temp]++;

}

flag=1;

for (int i=0;i<10;i++)

{

if (count1[i]!=count2[i])

{

flag=0;//break;

}

}

if (flag)

cout<<"Yes"<<endl;

else

cout<<"No"<<endl;

for (int i=0;i<10;i++)

{

count1[i]=0;

count2[i]=0;

}

}

return 0;

}
