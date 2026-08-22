---
source_id: web-frontend-fundamentals-016
course_id: web_frontend_fundamentals
title: "Lecture 6 Basic JavaScript"
original_file: "学科资料/web开发前端技术基础/ppt/Lecture 6 Basic JavaScript.ppt"
document_role: note
year: 
locator_type: slide
---

# Lecture 6 Basic JavaScript

<!-- slide: 1 -->

## Lecture 6基础JavaScript

<!-- slide: 2 -->

## 动态Vs. 静态

- 静态网页
  - 客户端/用户的观点 : 一个指向不变的html文件的url
  - 服务器/开发者的观点:一个存储在Web服务器根目录或者子目录下的html文件 …
  - 可以直接在浏览器上显示
- 动态网页
  - 客户端/用户的观点 :一个指向动态的html文件的url (每次请求访问都可能不一样)
  - 服务器/开发者的观点: 一个生成html的程序/脚本
  - 不是 html, 但是程序生成html
  - 不能直接在浏览器上显示
- 动态网页, Dynamic HTML (DHTML), 有何不同?

<!-- slide: 3 -->

## 概要

- JavaScript简介
- JavaScript入门

<!-- slide: 4 -->

## JavaScript简介

- JavaScript 是世界上最流行的编程语言之一。
- 这门语言可用于 HTML 和 web，更可广泛用于服务器、PC、笔记本电脑、平板电脑和智能手机等设备。
- JavaScript 是脚本语言
- JavaScript 是一种轻量级的编程语言。
- JavaScript 是可插入 HTML 页面的编程代码。
- JavaScript 插入 HTML 页面后，可由所有的现代浏览器执行。
- JavaScript 很容易学习。

<!-- slide: 5 -->

- JavaScript 与 Java 是两种完全不同的语言，无论在概念还是设计上。
- Java（由 Sun 发明）是更复杂的编程语言。
- ECMA-262 是 JavaScript 标准的官方名称。
- JavaScript 由 Brendan Eich 发明。它于 1995 年出现在 Netscape 中（该浏览器已停止更新），并于 1997 年被 ECMA（一个标准协会）采纳。

<!-- slide: 6 -->

## Hello, World!

- 以下内容可以放在一个HTML中:
- 脚本代码<scrpt开始，以 /script>结束
- JavaScript语句, 函数声明等放在这两个起始和结束标记之间
- <script>
- document.write(“Hello, World!");
- </script>
- HTML
- Hello, World!

<!-- slide: 7 -->

## 观察JavaScript的输出

- 你的JavaScript代码必须先运行/执行，才能在浏览器输出。
![image](assets/web-frontend-fundamentals-016/image-001.png)
![image](assets/web-frontend-fundamentals-016/image-002.png)

<!-- slide: 8 -->

## JavaScript：对事件作出反应

- alert() 函数在 JavaScript 中并不常用，但它对于代码测试非常方便。
- onclick 事件只是JavaScript中众多事件之一。
- <script>
- <button type="button" onclick="alert('Welcome!')">点击这里</button>
- </script>
- HTML
![image](assets/web-frontend-fundamentals-016/image-003.png)

<!-- slide: 9 -->

## JavaScript：改变 HTML 内容

- 以后会经常看到 document.getElementByID("some id")。这个方法是 HTML DOM 中定义的。
- DOM（文档对象模型）是用以访问 HTML 元素的正式 W3C 标准。
- <script>
- function myFunction()
- {
- x=document.getElementById("demo");  // 找到元素
- x.innerHTML="Hello JavaScript!";    // 改变内容
- }
- </script>
- HTML

<!-- slide: 10 -->

## JavaScript：改变 HTML 图像

- <script>
- function changeImage()
- {
- element=document.getElementById('myimage')
- if (element.src.match("bulbon"))
- {
- element.src="eg_bulboff.gif";
- }
- else
- {
- element.src="eg_bulbon.gif";
- }
- }
- </script>
- <img id="myimage" onclick="changeImage()" src="eg_bulboff.gif">
- HTML

<!-- slide: 11 -->

## JavaScript：改变 HTML 样式

- <p id="demo">
- JavaScript 能改变 HTML 元素的样式。
- </p>
- <script>
- function myFunction()
- {
- x=document.getElementById("demo") // 找到元素
- x.style.color="#ff0000";          // 改变样式
- }
- </script>
- <button type=“button” onclick=“myFunction()”>点击这里</button>
- HTML

<!-- slide: 12 -->

## JavaScript 的使用

![image](assets/web-frontend-fundamentals-016/image-004.png)
![image](assets/web-frontend-fundamentals-016/image-005.png)
![image](assets/web-frontend-fundamentals-016/image-006.png)

<!-- slide: 13 -->

## JavaScript 的使用

![image](assets/web-frontend-fundamentals-016/image-007.png)
![image](assets/web-frontend-fundamentals-016/image-008.png)

<!-- slide: 14 -->

## JavaScript 的使用

![image](assets/web-frontend-fundamentals-016/image-009.png)

<!-- slide: 15 -->

## JavaScript 的使用

![image](assets/web-frontend-fundamentals-016/image-010.png)
![image](assets/web-frontend-fundamentals-016/image-011.png)

<!-- slide: 16 -->

## JavaScript 的使用

![image](assets/web-frontend-fundamentals-016/image-012.png)
![image](assets/web-frontend-fundamentals-016/image-013.png)
![image](assets/web-frontend-fundamentals-016/image-014.png)
![image](assets/web-frontend-fundamentals-016/image-015.png)
![image](assets/web-frontend-fundamentals-016/image-016.png)

<!-- slide: 17 -->

## JavaScript 的使用

![image](assets/web-frontend-fundamentals-016/image-017.png)
![image](assets/web-frontend-fundamentals-016/image-018.png)

<!-- slide: 18 -->

## JavaScript 的使用

![image](assets/web-frontend-fundamentals-016/image-019.png)
![image](assets/web-frontend-fundamentals-016/image-020.png)
![image](assets/web-frontend-fundamentals-016/image-021.png)
![image](assets/web-frontend-fundamentals-016/image-022.png)
![image](assets/web-frontend-fundamentals-016/image-023.png)

<!-- slide: 19 -->

## JS能做什么？

![image](assets/web-frontend-fundamentals-016/image-024.png)
![image](assets/web-frontend-fundamentals-016/image-025.png)
![image](assets/web-frontend-fundamentals-016/image-026.png)
![image](assets/web-frontend-fundamentals-016/image-027.png)

<!-- slide: 20 -->

## JS能做什么？

![image](assets/web-frontend-fundamentals-016/image-028.png)
![image](assets/web-frontend-fundamentals-016/image-029.png)

<!-- slide: 21 -->

## JS能做什么？

![image](assets/web-frontend-fundamentals-016/image-030.png)
![image](assets/web-frontend-fundamentals-016/image-031.png)
![image](assets/web-frontend-fundamentals-016/image-032.png)
![image](assets/web-frontend-fundamentals-016/image-033.png)

<!-- slide: 22 -->

## JS能做什么？

![image](assets/web-frontend-fundamentals-016/image-034.png)
![image](assets/web-frontend-fundamentals-016/image-035.png)
![image](assets/web-frontend-fundamentals-016/image-036.png)

<!-- slide: 23 -->

## JS能做什么？

![image](assets/web-frontend-fundamentals-016/image-037.png)
![image](assets/web-frontend-fundamentals-016/image-038.png)
![image](assets/web-frontend-fundamentals-016/image-039.png)

<!-- slide: 24 -->

## JS能做什么？

![image](assets/web-frontend-fundamentals-016/image-040.png)
![image](assets/web-frontend-fundamentals-016/image-041.png)
![image](assets/web-frontend-fundamentals-016/image-042.png)

<!-- slide: 25 -->

![image](assets/web-frontend-fundamentals-016/image-043.png)
![image](assets/web-frontend-fundamentals-016/image-044.png)
![image](assets/web-frontend-fundamentals-016/image-045.png)

<!-- slide: 26 -->

## JavaScript编程案例-根据日期动态改变

![image](assets/web-frontend-fundamentals-016/image-046.png)
![image](assets/web-frontend-fundamentals-016/image-047.png)
![image](assets/web-frontend-fundamentals-016/image-048.png)

<!-- slide: 27 -->

![image](assets/web-frontend-fundamentals-016/image-049.png)
![image](assets/web-frontend-fundamentals-016/image-050.png)
![image](assets/web-frontend-fundamentals-016/image-051.png)
- 园的半径在JS代码中输入，并把周长和面积结果显示在页面的一个div中
![image](assets/web-frontend-fundamentals-016/image-052.png)
- JavaScript编程案例-用户互动输入

<!-- slide: 28 -->

## 总结

- JavaScript基础

<!-- slide: 29 -->

## 练习题

- 练习今天所讲的JavaScript基础

<!-- slide: 30 -->

![image](assets/web-frontend-fundamentals-016/image-053.png)
- Thank you!
