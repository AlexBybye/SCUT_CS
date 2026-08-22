---
source_id: mathematical-modeling-042
course_id: mathematical_modeling
title: "C语言程序"
original_file: "学科资料/数学建模[包括课外]/Matlab/材料选择/C语言程序.cpp"
document_role: exercise_solution
year: 
locator_type: none
---

# C语言程序

```cpp
#include<stdio.h>
void main()
{
   /*���ֲ����������ݵ�¼�루�ɳ���Ա���У�*/
	int a,b,c,i,j,k=0,l,m,n;
    int d[9]={412,529,570,598,630,696,380,470,490};
	int e[9]={522,639,689,698,740,799,450,570,590};
	int f[9]={365,365,730,365,547,730,365,547,547};
	int g[9]={100,150,200,200,100,150,200,150,200};
	int h[9]={2000,2500,4100,3000,3446,5080,1500,3000,2790};
	int y[9];
	int z[9];
    /*�û�������������루�ɲ�ѯ�û����У�*/
	printf("������������Ҫ���ϵ���Ӧ��ǿ��(Mpa)��\n");
    scanf("%d",&a);
	printf("������������Ҫ���ϵ���Ӧ��ǿ��(Mpa)��\n");
    scanf("%d",&b);
    printf("������������Ҫ���ϵĵ���ģ��(Mpa)��\n");
    scanf("%d",&c);
    /*ģ�ͼ���ѭ��*/
    for(j=0;j<=8;j++) z[j]=(h[j])/(f[j]);
    /*ɸѡ�������ܣ�ѡ�����ܿ��õĲ��ϣ�ѭ��*/
	for(n=0;n<=8;n++)
	{
	if((d[n]>=a)&&(e[n]>=b)&&(g[n]>=c)) 
	{
		y[k]=n;
	    k++;
     
	}
	}
    
	/*�ȽϿ��ò��Ͼ�����ѭ��*/
  for(l=0,m=z[(y[0])];l<=k-1;l++)
    {
		if(m>=z[(y[l])])
		{
			i=y[l];
			m=z[(y[l])];
	}
	}
    /*���������㣬��������õĲ����ƺŽ�����ѯ�û�*/
  switch(i)
    {
	case 0: printf("������ѡ��Y20��\n"); break;
    case 1: printf("������ѡ��Y35��\n"); break;
	case 2: printf("������ѡ��Y40��\n"); break;
	case 3: printf("������ѡ��Y45��\n"); break;
	case 4: printf("������ѡ��Y50��\n"); break;
	case 5: printf("������ѡ��Y65��\n"); break;
	case 6: printf("������ѡ��Q235��\n"); break;
	case 7: printf("������ѡ��Q255��\n"); break;
	case 8: printf("������ѡ��Q275��\n"); break;
    default:printf("û�к��ʲ���\n");
	}
}

```
