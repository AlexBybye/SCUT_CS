---
source_id: artificial-intelligence-intro-020
course_id: artificial_intelligence_intro
title: "第7章 深度学习（2）-线性分类器"
original_file: "学科资料/人工智能导论/神之华工官方PPT，爱来自密歇根大学/第7章 深度学习（2）-线性分类器.pdf"
document_role: note
year: 
locator_type: page
---

# 第7章 深度学习（2）-线性分类器

<!-- page: 1 -->

Lecture 3:
Linear Classifiers

Justin Johnson
September 11, 2019

Lecture 3 - 1

<!-- page: 2 -->

Reminder: Assignment 1

• http://web.eecs.umich.edu/~justincj/teaching/eecs498/assignment1.html
• Due Sunday September 15, 11:59pm EST
• We have written a homework validation script to check the
format of your .zip file before you submit to Canvas:
• https://github.com/deepvision-class/tools#homework-
validation
• This script ensures that your .zip and .ipynb files are properly
structured; they do not check correctness
• It is your responsibility to make sure your submitted .zip file
passes the validation script

Justin Johnson
September 11, 2019

Lecture 3 - 2

<!-- page: 3 -->

Last time: Image Classification

Input: image

Output: Assign image to one
of a fixed set of categories

cat
bird
deer
dog
truck

This image by Nikita is
licensed under CC-BY 2.0

Justin Johnson
September 11, 2019

Lecture 3 - 3

![image](assets/artificial-intelligence-intro-020/image-001.png)

<!-- page: 4 -->

Last Time: Challenges of Recognition

Illumination
Deformation
Occlusion

Viewpoint

This image is CC0 1.0 public domain
This image by Umberto Salvagnin is

licensed under CC-BY 2.0
This image by jonsson is licensed

under CC-BY 2.0

Clutter

Intraclass Variation

This image is CC0 1.0 public domain

This image is CC0 1.0 public domain

Justin Johnson
September 11, 2019

Lecture 3 - 4

![image](assets/artificial-intelligence-intro-020/image-002.png)

![image](assets/artificial-intelligence-intro-020/image-003.png)

![image](assets/artificial-intelligence-intro-020/image-004.png)

![image](assets/artificial-intelligence-intro-020/image-005.png)

![image](assets/artificial-intelligence-intro-020/image-006.png)

![image](assets/artificial-intelligence-intro-020/image-007.png)

<!-- page: 5 -->

Last time: Data-Drive Approach, kNN

1-NN classifier
5-NN classifier

train
test

train
test
validation

Justin Johnson
September 11, 2019

Lecture 3 - 5

![image](assets/artificial-intelligence-intro-020/image-008.png)

![image](assets/artificial-intelligence-intro-020/image-009.png)

![image](assets/artificial-intelligence-intro-020/image-010.png)

![image](assets/artificial-intelligence-intro-020/image-011.png)

<!-- page: 6 -->

Today: Linear Classifiers

Justin Johnson
September 11, 2019

Lecture 3 - 6

<!-- page: 7 -->

Neural Network

Linear
classifiers

This image is CC0 1.0 public domain

Justin Johnson
September 11, 2019
Lecture 3 - 7

![image](assets/artificial-intelligence-intro-020/image-012.png)

<!-- page: 8 -->

Recall CIFAR10

50,000 training images
each image is 32x32x3

10,000 test images.

Justin Johnson
September 11, 2019

Lecture 3 - 8

![image](assets/artificial-intelligence-intro-020/image-013.png)

<!-- page: 9 -->

Parametric Approach

Image

f(x,W)
10 numbers giving
class scores

Array of 32x32x3 numbers
(3072 numbers total)

W

parameters

or weights

Justin Johnson
September 11, 2019

Lecture 3 - 9

![image](assets/artificial-intelligence-intro-020/image-014.png)

<!-- page: 10 -->

Parametric Approach: Linear Classifier

f(x,W) = Wx

Image

f(x,W)
10 numbers giving
class scores

Array of 32x32x3 numbers
(3072 numbers total)

W

parameters

or weights

Justin Johnson
September 11, 2019

Lecture 3 - 10

![image](assets/artificial-intelligence-intro-020/image-015.png)

<!-- page: 11 -->

Parametric Approach: Linear Classifier

(3072,)

f(x,W) = Wx

Image

(10,)
(10, 3072)

f(x,W)
10 numbers giving
class scores

Array of 32x32x3 numbers
(3072 numbers total)

W

parameters

or weights

Justin Johnson
September 11, 2019

Lecture 3 - 11

![image](assets/artificial-intelligence-intro-020/image-016.png)

<!-- page: 12 -->

Parametric Approach: Linear Classifier

(3072,)

f(x,W) = Wx + b

(10,)

Image

(10,)
(10, 3072)

f(x,W)
10 numbers giving
class scores

Array of 32x32x3 numbers
(3072 numbers total)

W

parameters

or weights

Justin Johnson
September 11, 2019

Lecture 3 - 12

![image](assets/artificial-intelligence-intro-020/image-017.png)

<!-- page: 13 -->

Example for 2x2 image, 3 classes (cat/dog/ship)

Stretch pixels into column

f(x,W) = Wx + b

56

56
231

231

24
2

24

Input image

2

(2, 2)

(4,)

Justin Johnson
September 11, 2019

Lecture 3 - 13

![image](assets/artificial-intelligence-intro-020/image-018.png)

<!-- page: 14 -->

Example for 2x2 image, 3 classes (cat/dog/ship)

Stretch pixels into column

f(x,W) = Wx + b

56

0.2
-0.5
0.1
2.0

1.1

-96.8

56
231

231

-1.2
+

61.95
=

1.5
1.3
2.1
0.0

3.2

437.9

24
2

24

0
0.25
0.2
-0.3
W

Input image

2

(2, 2)

b
(4,)
(3, 4)

(3,)

(3,)

Justin Johnson
September 11, 2019

Lecture 3 - 14

![image](assets/artificial-intelligence-intro-020/image-019.png)

<!-- page: 15 -->

Linear Classifier: Algebraic Viewpoint

Stretch pixels into column

f(x,W) = Wx + b

56

0.2
-0.5
0.1
2.0

1.1

-96.8

56
231

231

-1.2
+

61.95
=

1.5
1.3
2.1
0.0

3.2

437.9

24
2

24

0
0.25
0.2
-0.3
W

Input image

2

(2, 2)

b
(4,)
(3, 4)

(3,)

(3,)

Justin Johnson
September 11, 2019

Lecture 3 - 15

![image](assets/artificial-intelligence-intro-020/image-020.png)

<!-- page: 16 -->

Add extra one to data vector;
bias is absorbed into last
column of weight matrix

Linear Classifier: Bias Trick

Stretch pixels into column

56

0.2
-0.5
0.1
2.0

1.1

-96.8

56
231

231

61.95
=

1.5
1.3
2.1
0.0

3.2

437.9

24
2

24

0
0.25
0.2
-0.3
W

-1.2

Input image

2

(2, 2)

(5,)
(3, 5)
(3,)

1

Justin Johnson
September 11, 2019

Lecture 3 - 16

![image](assets/artificial-intelligence-intro-020/image-021.png)

<!-- page: 17 -->

Linear Classifier: Predictions are Linear!

f(x, W) = Wx
(ignore bias)

f(cx, W) = W(cx) = c * f(x, W)

Justin Johnson
September 11, 2019

Lecture 3 - 17

<!-- page: 18 -->

Linear Classifier: Predictions are Linear!

f(x, W) = Wx
(ignore bias)

f(cx, W) = W(cx) = c * f(x, W)

Image
0.5 * Image
Scores

0.5 * Scores

-48.4

-96.8

218.9

437.8

31.0

62.0

Justin Johnson
September 11, 2019

Lecture 3 - 18

![image](assets/artificial-intelligence-intro-020/image-022.png)

![image](assets/artificial-intelligence-intro-020/image-023.png)

<!-- page: 19 -->

Interpreting a Linear Classifier

Algebraic Viewpoint

f(x,W) = Wx + b

Stretch pixels into column

56

0.2
-0.5
0.1
2.0

1.1

-96.8

56
231

231

-1.2
+

61.95
=

1.5
1.3
2.1
0.0

3.2

437.9

24
2

24

0
0.25
0.2
-0.3
W

Input image

2

(2, 2)

b
(4,)
(3, 4)

(3,)

(3,)

Justin Johnson
September 11, 2019
Lecture 3 - 19

![image](assets/artificial-intelligence-intro-020/image-024.png)

<!-- page: 20 -->

Interpreting a Linear Classifier

Algebraic Viewpoint

f(x,W) = Wx + b

Stretch pixels into column

0.2
-0.5

1.5
1.3

0
.25

W

56

0.2
-0.5
0.1
2.0

1.1

-96.8

56
231

0.1
2.0

2.1
0.0

0.2
-0.3

231

-1.2
+

61.95
=

1.5
1.3
2.1
0.0

3.2

437.9

24
2

24

0
0.25
0.2
-0.3
W

Input image

2

b

(2, 2)

1.1
3.2
-1.2

b
(4,)
(3, 4)

(3,)

(3,)

-96.8
437.9
61.95

Justin Johnson
September 11, 2019
Lecture 3 - 20

![image](assets/artificial-intelligence-intro-020/image-025.png)

![image](assets/artificial-intelligence-intro-020/image-026.png)

<!-- page: 21 -->

Interpreting an Linear Classifier

0.2
-0.5

1.5
1.3

0
.25

W

0.1
2.0

2.1
0.0

0.2
-0.3

b

1.1
3.2
-1.2

-96.8
437.9
61.95

Justin Johnson
September 11, 2019
Lecture 3 - 21

![image](assets/artificial-intelligence-intro-020/image-027.png)

![image](assets/artificial-intelligence-intro-020/image-028.png)

<!-- page: 22 -->

Interpreting an Linear Classifier: Visual Viewpoint

0.2
-0.5

1.5
1.3

0
.25

W

0.1
2.0

2.1
0.0

0.2
-0.3

b

1.1
3.2
-1.2

-96.8
437.9
61.95

Justin Johnson
September 11, 2019
Lecture 3 - 22

![image](assets/artificial-intelligence-intro-020/image-029.png)

![image](assets/artificial-intelligence-intro-020/image-030.png)

![image](assets/artificial-intelligence-intro-020/image-031.png)

<!-- page: 23 -->

Interpreting an Linear Classifier: Visual Viewpoint

Linear classifier has one
“template” per category

0.2
-0.5

1.5
1.3

0
.25

W

0.1
2.0

2.1
0.0

0.2
-0.3

b

1.1
3.2
-1.2

-96.8
437.9
61.95

Justin Johnson
September 11, 2019
Lecture 3 - 23

![image](assets/artificial-intelligence-intro-020/image-032.png)

![image](assets/artificial-intelligence-intro-020/image-033.png)

<!-- page: 24 -->

Interpreting an Linear Classifier: Visual Viewpoint

Linear classifier has one
“template” per category

0.2
-0.5

1.5
1.3

0
.25

W

A single template cannot capture
multiple modes of the data

0.1
2.0

2.1
0.0

0.2
-0.3

b

1.1
3.2
-1.2

e.g. horse template has 2 heads!

-96.8
437.9
61.95

Justin Johnson
September 11, 2019
Lecture 3 - 24

![image](assets/artificial-intelligence-intro-020/image-034.png)

![image](assets/artificial-intelligence-intro-020/image-035.png)

<!-- page: 25 -->

Interpreting a Linear Classifier: Geometric Viewpoint

f(x,W) = Wx + b

Airplane

Score

Deer Score
Classifier

score

Car Score

Array of 32x32x3 numbers
(3072 numbers total)
Value of pixel (15, 8, 0)

Justin Johnson
September 11, 2019

Lecture 3 - 25

![image](assets/artificial-intelligence-intro-020/image-036.png)

<!-- page: 26 -->

Interpreting a Linear Classifier: Geometric Viewpoint

Pixel
(11, 11, 0)

f(x,W) = Wx + b

Car score
increases
this way

Pixel
(15, 8, 0)

Array of 32x32x3 numbers
(3072 numbers total)

Car Score
= 0

Justin Johnson
September 11, 2019

Lecture 3 - 26

![image](assets/artificial-intelligence-intro-020/image-037.png)

<!-- page: 27 -->

Interpreting a Linear Classifier: Geometric Viewpoint

Car template
on this line

Pixel
(11, 11, 0)

f(x,W) = Wx + b

Car score
increases
this way

Pixel
(15, 8, 0)

Array of 32x32x3 numbers
(3072 numbers total)

Car Score
= 0

Justin Johnson
September 11, 2019

Lecture 3 - 27

![image](assets/artificial-intelligence-intro-020/image-038.png)

![image](assets/artificial-intelligence-intro-020/image-039.png)

<!-- page: 28 -->

Interpreting a Linear Classifier: Geometric Viewpoint

Car template
on this line

Airplane

Pixel
(11, 11, 0)

f(x,W) = Wx + b

Score

Car score
increases
this way

Pixel (15, 8, 0)

Array of 32x32x3 numbers
(3072 numbers total)

Car Score
= 0

Deer
Score

Justin Johnson
September 11, 2019

Lecture 3 - 28

![image](assets/artificial-intelligence-intro-020/image-040.png)

![image](assets/artificial-intelligence-intro-020/image-041.png)

![image](assets/artificial-intelligence-intro-020/image-042.png)

![image](assets/artificial-intelligence-intro-020/image-043.png)

<!-- page: 29 -->

Interpreting a Linear Classifier: Geometric Viewpoint

Car template
on this line

Airplane

Pixel
(11, 11, 0)

Hyperplanes carving up a
high-dimensional space

Score

Car score
increases
this way

Pixel (15, 8, 0)

Car Score
= 0

Deer
Score

Plot created using Wolfram Cloud

Justin Johnson
September 11, 2019

Lecture 3 - 29

![image](assets/artificial-intelligence-intro-020/image-044.png)

![image](assets/artificial-intelligence-intro-020/image-045.png)

![image](assets/artificial-intelligence-intro-020/image-046.png)

![image](assets/artificial-intelligence-intro-020/image-047.png)

<!-- page: 30 -->

Hard Cases for a Linear Classifier

Class 1:
First and third quadrants

Class 1:
1 <= L2 norm <= 2

Class 1:
Three modes

Class 2:
Everything else

Class 2:
Everything else

Class 2:
Second and fourth quadrants

Justin Johnson
September 11, 2019

Lecture 3 - 30

<!-- page: 31 -->

Recall: Perceptron couldn’t learn XOR

y

X
Y
F(x,y)

0
0
0

0
1
1

1
0
1

1
1
0
x

Justin Johnson
September 11, 2019

Lecture 3 - 31

![image](assets/artificial-intelligence-intro-020/image-048.png)

<!-- page: 32 -->

Linear Classifier: Three Viewpoints

Algebraic Viewpoint
Visual Viewpoint
Geometric Viewpoint

One template

Hyperplanes
cutting up space

f(x,W) = Wx

per class

Justin Johnson
September 11, 2019

Lecture 3 - 32

![image](assets/artificial-intelligence-intro-020/image-049.png)

![image](assets/artificial-intelligence-intro-020/image-050.png)

![image](assets/artificial-intelligence-intro-020/image-051.png)

![image](assets/artificial-intelligence-intro-020/image-052.png)

<!-- page: 33 -->

f(x,W) = Wx + b

So Far: Defined a linear score function

Given a W, we can
compute class scores
for an image x.

-3.45
-8.87

-0.51

3.42
4.64
2.65
5.1
2.64
5.55
-4.34

6.04
5.31
-4.22
-4.19

0.09
2.9
4.48
8.02
3.78
1.06
-0.36
-0.72

But how can we
actually choose a
good W?

3.58
4.49
-4.37
-2.09
-2.93

-1.5
-4.79

6.14

Cat image by Nikita is licensed under CC-BY 2.0; Car image is CC0 1.0 public domain; Frog image is in the public domain

Justin Johnson
September 11, 2019

Lecture 3 - 33

![image](assets/artificial-intelligence-intro-020/image-053.png)

![image](assets/artificial-intelligence-intro-020/image-054.png)

![image](assets/artificial-intelligence-intro-020/image-055.png)

![image](assets/artificial-intelligence-intro-020/image-056.png)

<!-- page: 34 -->

f(x,W) = Wx + b

Choosing a good W

TODO:

1. Use a loss function to
quantify how good a
value of W is

-3.45
-8.87

-0.51

3.42
4.64
2.65
5.1
2.64
5.55
-4.34

6.04
5.31
-4.22
-4.19

0.09
2.9
4.48
8.02
3.78
1.06
-0.36
-0.72

2. Find a W that minimizes
the loss function
(optimization)

3.58
4.49
-4.37
-2.09
-2.93

-1.5
-4.79

6.14

Justin Johnson
September 11, 2019

Lecture 3 - 34

![image](assets/artificial-intelligence-intro-020/image-057.png)

![image](assets/artificial-intelligence-intro-020/image-058.png)

![image](assets/artificial-intelligence-intro-020/image-059.png)

![image](assets/artificial-intelligence-intro-020/image-060.png)

<!-- page: 35 -->

Loss Function

A loss function tells how good our
current classifier is

Low loss = good classifier
High loss = bad classifier

(Also called: objective function;
cost function)

Justin Johnson
September 11, 2019

Lecture 3 - 35

<!-- page: 36 -->

Loss Function

A loss function tells how good our
current classifier is

Low loss = good classifier
High loss = bad classifier

(Also called: objective function;
cost function)

Negative loss function sometimes
called reward function, profit
function, utility function, fitness
function, etc

Justin Johnson
September 11, 2019

Lecture 3 - 36

<!-- page: 37 -->

Loss Function

Given a dataset of examples

A loss function tells how good our
current classifier is

Where       is image and

is (integer) label

Low loss = good classifier
High loss = bad classifier

(Also called: objective function;
cost function)

Negative loss function sometimes
called reward function, profit
function, utility function, fitness
function, etc

Justin Johnson
September 11, 2019

Lecture 3 - 37

![image](assets/artificial-intelligence-intro-020/image-061.png)

<!-- page: 38 -->

Loss Function

Given a dataset of examples

A loss function tells how good our
current classifier is

Where       is image and

is (integer) label

Low loss = good classifier
High loss = bad classifier

Loss for a single example is

(Also called: objective function;
cost function)

Negative loss function sometimes
called reward function, profit
function, utility function, fitness
function, etc

Justin Johnson
September 11, 2019

Lecture 3 - 38

![image](assets/artificial-intelligence-intro-020/image-062.png)

![image](assets/artificial-intelligence-intro-020/image-063.png)

<!-- page: 39 -->

Loss Function

Given a dataset of examples

A loss function tells how good our
current classifier is

Where       is image and

is (integer) label

Low loss = good classifier
High loss = bad classifier

Loss for a single example is

(Also called: objective function;
cost function)

Loss for the dataset is average of
per-example losses:

Negative loss function sometimes
called reward function, profit
function, utility function, fitness
function, etc

Justin Johnson
September 11, 2019

Lecture 3 - 39

![image](assets/artificial-intelligence-intro-020/image-064.png)

![image](assets/artificial-intelligence-intro-020/image-065.png)

![image](assets/artificial-intelligence-intro-020/image-066.png)

<!-- page: 40 -->

Multiclass SVM Loss

”The score of the correct class should
be higher than all the other scores”

Loss

Score for
correct class

Justin Johnson
September 11, 2019

Lecture 3 - 40

<!-- page: 41 -->

Multiclass SVM Loss

”The score of the correct class should
be higher than all the other scores”

Loss

Score for
correct class

Highest score
among other classes

Justin Johnson
September 11, 2019

Lecture 3 - 41

<!-- page: 42 -->

Multiclass SVM Loss

”The score of the correct class should
be higher than all the other scores”

Loss

“Hinge Loss”

Score for
correct class

Highest score
among other classes

“Margin”

Justin Johnson
September 11, 2019

Lecture 3 - 42

<!-- page: 43 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

”The score of the correct class should
be higher than all the other scores”

Let                             be scores

Loss

Then the SVM loss has the form:
“Hinge Loss”

Score for
correct class

Highest score
among other classes

“Margin”

Justin Johnson
September 11, 2019

Lecture 3 - 43

![image](assets/artificial-intelligence-intro-020/image-067.png)

![image](assets/artificial-intelligence-intro-020/image-068.png)

![image](assets/artificial-intelligence-intro-020/image-069.png)

<!-- page: 44 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

frog

-1.7

2.0

-3.1

Justin Johnson
September 11, 2019

Lecture 3 - 44

![image](assets/artificial-intelligence-intro-020/image-070.png)

![image](assets/artificial-intelligence-intro-020/image-071.png)

![image](assets/artificial-intelligence-intro-020/image-072.png)

![image](assets/artificial-intelligence-intro-020/image-073.png)

![image](assets/artificial-intelligence-intro-020/image-074.png)

![image](assets/artificial-intelligence-intro-020/image-075.png)

<!-- page: 45 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

= max(0, 5.1 - 3.2 + 1)

+ max(0, -1.7 - 3.2 + 1)
= max(0, 2.9) + max(0, -3.9)
= 2.9 + 0
= 2.9
Loss
2.9

frog

-1.7

2.0

-3.1

Justin Johnson
September 11, 2019

Lecture 3 - 45

![image](assets/artificial-intelligence-intro-020/image-076.png)

![image](assets/artificial-intelligence-intro-020/image-077.png)

![image](assets/artificial-intelligence-intro-020/image-078.png)

![image](assets/artificial-intelligence-intro-020/image-079.png)

![image](assets/artificial-intelligence-intro-020/image-080.png)

![image](assets/artificial-intelligence-intro-020/image-081.png)

<!-- page: 46 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

= max(0, 1.3 - 4.9 + 1)

+max(0, 2.0 - 4.9 + 1)
= max(0, -2.6) + max(0, -1.9)
= 0 + 0
= 0

frog

-1.7

2.0

-3.1

Loss
2.9
0

Justin Johnson
September 11, 2019

Lecture 3 - 46

![image](assets/artificial-intelligence-intro-020/image-082.png)

![image](assets/artificial-intelligence-intro-020/image-083.png)

![image](assets/artificial-intelligence-intro-020/image-084.png)

![image](assets/artificial-intelligence-intro-020/image-085.png)

![image](assets/artificial-intelligence-intro-020/image-086.png)

![image](assets/artificial-intelligence-intro-020/image-087.png)

<!-- page: 47 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

= max(0, 2.2 - (-3.1) + 1)

+max(0, 2.5 - (-3.1) + 1)
= max(0, 6.3) + max(0, 6.6)
= 6.3 + 6.6
= 12.9

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 47

![image](assets/artificial-intelligence-intro-020/image-088.png)

![image](assets/artificial-intelligence-intro-020/image-089.png)

![image](assets/artificial-intelligence-intro-020/image-090.png)

![image](assets/artificial-intelligence-intro-020/image-091.png)

![image](assets/artificial-intelligence-intro-020/image-092.png)

![image](assets/artificial-intelligence-intro-020/image-093.png)

<!-- page: 48 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

Loss over the dataset is:

frog

-1.7

2.0

-3.1

L = (2.9 + 0.0 + 12.9) / 3

= 5.27

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 48

![image](assets/artificial-intelligence-intro-020/image-094.png)

![image](assets/artificial-intelligence-intro-020/image-095.png)

![image](assets/artificial-intelligence-intro-020/image-096.png)

![image](assets/artificial-intelligence-intro-020/image-097.png)

![image](assets/artificial-intelligence-intro-020/image-098.png)

![image](assets/artificial-intelligence-intro-020/image-099.png)

<!-- page: 49 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

Q: What happens to the
loss if the scores for the
car image change a bit?

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 49

![image](assets/artificial-intelligence-intro-020/image-100.png)

![image](assets/artificial-intelligence-intro-020/image-101.png)

![image](assets/artificial-intelligence-intro-020/image-102.png)

![image](assets/artificial-intelligence-intro-020/image-103.png)

![image](assets/artificial-intelligence-intro-020/image-104.png)

![image](assets/artificial-intelligence-intro-020/image-105.png)

<!-- page: 50 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

Q2: What are the min
and max possible loss?

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 50

![image](assets/artificial-intelligence-intro-020/image-106.png)

![image](assets/artificial-intelligence-intro-020/image-107.png)

![image](assets/artificial-intelligence-intro-020/image-108.png)

![image](assets/artificial-intelligence-intro-020/image-109.png)

![image](assets/artificial-intelligence-intro-020/image-110.png)

![image](assets/artificial-intelligence-intro-020/image-111.png)

<!-- page: 51 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

Q3: If all the scores
were random, what
loss would we expect?

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 51

![image](assets/artificial-intelligence-intro-020/image-112.png)

![image](assets/artificial-intelligence-intro-020/image-113.png)

![image](assets/artificial-intelligence-intro-020/image-114.png)

![image](assets/artificial-intelligence-intro-020/image-115.png)

![image](assets/artificial-intelligence-intro-020/image-116.png)

![image](assets/artificial-intelligence-intro-020/image-117.png)

<!-- page: 52 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

Q4: What would happen
if the sum were over all
classes? (including i = yi)

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 52

![image](assets/artificial-intelligence-intro-020/image-118.png)

![image](assets/artificial-intelligence-intro-020/image-119.png)

![image](assets/artificial-intelligence-intro-020/image-120.png)

![image](assets/artificial-intelligence-intro-020/image-121.png)

![image](assets/artificial-intelligence-intro-020/image-122.png)

![image](assets/artificial-intelligence-intro-020/image-123.png)

<!-- page: 53 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

Q5: What if the loss used
a mean instead of a sum?

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 53

![image](assets/artificial-intelligence-intro-020/image-124.png)

![image](assets/artificial-intelligence-intro-020/image-125.png)

![image](assets/artificial-intelligence-intro-020/image-126.png)

![image](assets/artificial-intelligence-intro-020/image-127.png)

![image](assets/artificial-intelligence-intro-020/image-128.png)

![image](assets/artificial-intelligence-intro-020/image-129.png)

<!-- page: 54 -->

Multiclass SVM Loss

Given an example
(       is image,
is label)

Let                             be scores

Then the SVM loss has the form:

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

Q6: What if we used
this loss instead?

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 54

![image](assets/artificial-intelligence-intro-020/image-130.png)

![image](assets/artificial-intelligence-intro-020/image-131.png)

![image](assets/artificial-intelligence-intro-020/image-132.png)

![image](assets/artificial-intelligence-intro-020/image-133.png)

![image](assets/artificial-intelligence-intro-020/image-134.png)

![image](assets/artificial-intelligence-intro-020/image-135.png)

![image](assets/artificial-intelligence-intro-020/image-136.png)

<!-- page: 55 -->

Multiclass SVM Loss

Q: Suppose we found some W with L = 0. Is it unique?

Justin Johnson
September 11, 2019

Lecture 3 - 55

![image](assets/artificial-intelligence-intro-020/image-137.png)

![image](assets/artificial-intelligence-intro-020/image-138.png)

<!-- page: 56 -->

Multiclass SVM Loss

Q: Suppose we found some W with L = 0. Is it unique?

No! 2W is also has L = 0!

Justin Johnson
September 11, 2019

Lecture 3 - 56

![image](assets/artificial-intelligence-intro-020/image-139.png)

![image](assets/artificial-intelligence-intro-020/image-140.png)

<!-- page: 57 -->

Multiclass SVM Loss

Original W:
= max(0, 1.3 - 4.9 + 1)

+max(0, 2.0 - 4.9 + 1)
= max(0, -2.6) + max(0, -1.9)
= 0 + 0
= 0

3.2
cat

1.3

2.2

Using 2W instead:
= max(0, 2.6 - 9.8 + 1)

car

5.1

4.9

2.5

+max(0, 4.0 - 9.8 + 1)
= max(0, -6.2) + max(0, -4.8)
= 0 + 0
= 0

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 57

![image](assets/artificial-intelligence-intro-020/image-141.png)

![image](assets/artificial-intelligence-intro-020/image-142.png)

![image](assets/artificial-intelligence-intro-020/image-143.png)

![image](assets/artificial-intelligence-intro-020/image-144.png)

![image](assets/artificial-intelligence-intro-020/image-145.png)

<!-- page: 58 -->

Multiclass SVM Loss

How should we choose between
W and 2W if they both perform
the same on the training data?

3.2
cat

1.3

2.2

car

5.1

4.9

2.5

frog

-1.7

2.0

-3.1

Loss
2.9
0
12.9

Justin Johnson
September 11, 2019

Lecture 3 - 58

![image](assets/artificial-intelligence-intro-020/image-146.png)

![image](assets/artificial-intelligence-intro-020/image-147.png)

![image](assets/artificial-intelligence-intro-020/image-148.png)

![image](assets/artificial-intelligence-intro-020/image-149.png)

![image](assets/artificial-intelligence-intro-020/image-150.png)

<!-- page: 59 -->

Regularization: Beyond Training Error

Data loss: Model predictions
should match training data

Justin Johnson
September 11, 2019

Lecture 3 - 59

![image](assets/artificial-intelligence-intro-020/image-151.png)

<!-- page: 60 -->

Regularization: Beyond Training Error

Data loss: Model predictions
should match training data

Regularization: Prevent the model
from doing too well on training data

Justin Johnson
September 11, 2019

Lecture 3 - 60

![image](assets/artificial-intelligence-intro-020/image-152.png)

<!-- page: 61 -->

Regularization: Beyond Training Error

= regularization strength
(hyperparameter)

Data loss: Model predictions
should match training data

Regularization: Prevent the model
from doing too well on training data

Justin Johnson
September 11, 2019

Lecture 3 - 61

![image](assets/artificial-intelligence-intro-020/image-153.png)

<!-- page: 62 -->

Regularization: Beyond Training Error

= regularization strength
(hyperparameter)

Data loss: Model predictions
should match training data

Regularization: Prevent the model
from doing too well on training data

Simple examples
L2 regularization:
L1 regularization:
Elastic net (L1 + L2):

More complex:
Dropout
Batch normalization
Cutout, Mixup, Stochastic depth, etc…

Justin Johnson
September 11, 2019

Lecture 3 - 62

![image](assets/artificial-intelligence-intro-020/image-154.png)

![image](assets/artificial-intelligence-intro-020/image-155.png)

![image](assets/artificial-intelligence-intro-020/image-156.png)

![image](assets/artificial-intelligence-intro-020/image-157.png)

<!-- page: 63 -->

Regularization: Beyond Training Error

= regularization strength
(hyperparameter)

Data loss: Model predictions
should match training data

Regularization: Prevent the model
from doing too well on training data

Purpose of Regularization:
-
Express preferences in among models beyond ”minimize training error”
-
Avoid overfitting: Prefer simple models that generalize better
-
Improve optimization by adding curvature

Justin Johnson
September 11, 2019

Lecture 3 - 63

![image](assets/artificial-intelligence-intro-020/image-158.png)

<!-- page: 64 -->

Regularization: Expressing Preferences

L2 Regularization

Justin Johnson
September 11, 2019

Lecture 3 - 64

![image](assets/artificial-intelligence-intro-020/image-159.png)

![image](assets/artificial-intelligence-intro-020/image-160.png)

![image](assets/artificial-intelligence-intro-020/image-161.png)

![image](assets/artificial-intelligence-intro-020/image-162.png)

![image](assets/artificial-intelligence-intro-020/image-163.png)

<!-- page: 65 -->

Regularization: Expressing Preferences

L2 Regularization

L2 regularization likes to
“spread out” the weights

Justin Johnson
September 11, 2019

Lecture 3 - 65

![image](assets/artificial-intelligence-intro-020/image-164.png)

![image](assets/artificial-intelligence-intro-020/image-165.png)

![image](assets/artificial-intelligence-intro-020/image-166.png)

![image](assets/artificial-intelligence-intro-020/image-167.png)

![image](assets/artificial-intelligence-intro-020/image-168.png)

<!-- page: 66 -->

Regularization: Prefer Simpler Models

y

x

Justin Johnson
September 11, 2019

Lecture 3 - 66

<!-- page: 67 -->

Regularization: Prefer Simpler Models

y
f2
f1

x

The model f1 fits the training data perfectly
The model f2 has training error, but is simpler

Justin Johnson
September 11, 2019

Lecture 3 - 67

<!-- page: 68 -->

Regularization: Prefer Simpler Models

f1
f2

y

F1 is not a linear model; could
be polynomial regression, etc

x

Regularization pushes against fitting the data
too well so we don’t fit noise in the data

Justin Johnson
September 11, 2019

Lecture 3 - 68

<!-- page: 69 -->

Regularization: Prefer Simpler Models

f1
f2

Regularization is
important! You should
(usually) use it.

y

F1 is not a linear model; could
be polynomial regression, etc

x

Regularization pushes against fitting the data
too well so we don’t fit noise in the data

Justin Johnson
September 11, 2019

Lecture 3 - 69

<!-- page: 70 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

3.2
cat

car

5.1

frog

-1.7

Justin Johnson
September 11, 2019

Lecture 3 - 70

![image](assets/artificial-intelligence-intro-020/image-169.png)

<!-- page: 71 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

3.2
cat

car

5.1

frog

-1.7

Justin Johnson
September 11, 2019

Lecture 3 - 71

![image](assets/artificial-intelligence-intro-020/image-170.png)

![image](assets/artificial-intelligence-intro-020/image-171.png)

![image](assets/artificial-intelligence-intro-020/image-172.png)

<!-- page: 72 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

3.2
cat

car

5.1

frog

-1.7

Unnormalized log-
probabilities / logits

Justin Johnson
September 11, 2019

Lecture 3 - 72

![image](assets/artificial-intelligence-intro-020/image-173.png)

![image](assets/artificial-intelligence-intro-020/image-174.png)

![image](assets/artificial-intelligence-intro-020/image-175.png)

<!-- page: 73 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Probabilities
must be >= 0

3.2
cat

24.5

exp

car

5.1

164.0

frog

-1.7

0.18

unnormalized

probabilities
Unnormalized log-
probabilities / logits

Justin Johnson
September 11, 2019

Lecture 3 - 73

![image](assets/artificial-intelligence-intro-020/image-176.png)

![image](assets/artificial-intelligence-intro-020/image-177.png)

![image](assets/artificial-intelligence-intro-020/image-178.png)

<!-- page: 74 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Probabilities
must be >= 0

Probabilities
must sum to 1

3.2
cat

24.5

0.13

exp
normalize

car

5.1

164.0

0.87

frog

-1.7

0.18

0.00

unnormalized

probabilities
probabilities
Unnormalized log-
probabilities / logits

Justin Johnson
September 11, 2019

Lecture 3 - 74

![image](assets/artificial-intelligence-intro-020/image-179.png)

![image](assets/artificial-intelligence-intro-020/image-180.png)

![image](assets/artificial-intelligence-intro-020/image-181.png)

<!-- page: 75 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Probabilities
must be >= 0

Probabilities
must sum to 1

3.2
cat

24.5

0.13

Li = -log(0.13)

exp
normalize

= 2.04

car

5.1

164.0

0.87

frog

-1.7

0.18

0.00

unnormalized

probabilities
probabilities
Unnormalized log-
probabilities / logits

Justin Johnson
September 11, 2019

Lecture 3 - 75

![image](assets/artificial-intelligence-intro-020/image-182.png)

![image](assets/artificial-intelligence-intro-020/image-183.png)

![image](assets/artificial-intelligence-intro-020/image-184.png)

![image](assets/artificial-intelligence-intro-020/image-185.png)

<!-- page: 76 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Probabilities
must be >= 0

Probabilities
must sum to 1

3.2
cat

24.5

0.13

Li = -log(0.13)

exp
normalize

= 2.04

car

5.1

164.0

0.87

Maximum Likelihood Estimation
Choose weights to maximize the
likelihood of the observed data
(See EECS 445 or EECS 545)
unnormalized

frog

-1.7

0.18

0.00

probabilities
probabilities
Unnormalized log-
probabilities / logits

Justin Johnson
September 11, 2019

Lecture 3 - 76

![image](assets/artificial-intelligence-intro-020/image-186.png)

![image](assets/artificial-intelligence-intro-020/image-187.png)

![image](assets/artificial-intelligence-intro-020/image-188.png)

![image](assets/artificial-intelligence-intro-020/image-189.png)

<!-- page: 77 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Probabilities
must be >= 0

Probabilities
must sum to 1

3.2
cat

24.5

0.13

1.00

Compare

exp
normalize

car

5.1

164.0

0.87

0.00

frog

-1.7

0.18

0.00

0.00
Correct

unnormalized

probabilities
probabilities
Unnormalized log-
probabilities / logits

probs

Justin Johnson
September 11, 2019

Lecture 3 - 77

![image](assets/artificial-intelligence-intro-020/image-190.png)

![image](assets/artificial-intelligence-intro-020/image-191.png)

![image](assets/artificial-intelligence-intro-020/image-192.png)

![image](assets/artificial-intelligence-intro-020/image-193.png)

<!-- page: 78 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Probabilities
must be >= 0

Probabilities
must sum to 1

3.2
cat

24.5

0.13

1.00

Compare

exp
normalize

Kullback–Leibler

car

5.1

164.0

0.87

0.00

divergence

frog

-1.7

0.18

0.00

0.00
Correct

unnormalized

probabilities
probabilities
Unnormalized log-
probabilities / logits

probs

Justin Johnson
September 11, 2019

Lecture 3 - 78

![image](assets/artificial-intelligence-intro-020/image-194.png)

![image](assets/artificial-intelligence-intro-020/image-195.png)

![image](assets/artificial-intelligence-intro-020/image-196.png)

![image](assets/artificial-intelligence-intro-020/image-197.png)

![image](assets/artificial-intelligence-intro-020/image-198.png)

![image](assets/artificial-intelligence-intro-020/image-199.png)

<!-- page: 79 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Probabilities
must be >= 0

Probabilities
must sum to 1

3.2
cat

24.5

0.13

1.00

Compare

exp
normalize

car

5.1

164.0

0.87

0.00

Cross Entropy

frog

-1.7

0.18

0.00

0.00
Correct

unnormalized

probabilities
probabilities
Unnormalized log-
probabilities / logits

probs

Justin Johnson
September 11, 2019

Lecture 3 - 79

![image](assets/artificial-intelligence-intro-020/image-200.png)

![image](assets/artificial-intelligence-intro-020/image-201.png)

![image](assets/artificial-intelligence-intro-020/image-202.png)

![image](assets/artificial-intelligence-intro-020/image-203.png)

![image](assets/artificial-intelligence-intro-020/image-204.png)

![image](assets/artificial-intelligence-intro-020/image-205.png)

<!-- page: 80 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Maximize probability of correct class
Putting it all together:

3.2
cat

car

5.1

frog

-1.7

Justin Johnson
September 11, 2019

Lecture 3 - 80

![image](assets/artificial-intelligence-intro-020/image-206.png)

![image](assets/artificial-intelligence-intro-020/image-207.png)

![image](assets/artificial-intelligence-intro-020/image-208.png)

![image](assets/artificial-intelligence-intro-020/image-209.png)

![image](assets/artificial-intelligence-intro-020/image-210.png)

<!-- page: 81 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Maximize probability of correct class
Putting it all together:

3.2
cat

car

5.1

Q: What is the min /
max possible loss Li?

frog

-1.7

Justin Johnson
September 11, 2019

Lecture 3 - 81

![image](assets/artificial-intelligence-intro-020/image-211.png)

![image](assets/artificial-intelligence-intro-020/image-212.png)

![image](assets/artificial-intelligence-intro-020/image-213.png)

![image](assets/artificial-intelligence-intro-020/image-214.png)

![image](assets/artificial-intelligence-intro-020/image-215.png)

<!-- page: 82 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Maximize probability of correct class
Putting it all together:

3.2
cat

car

5.1

Q: What is the min /
max possible loss Li?
A: Min 0, max +infinity

frog

-1.7

Justin Johnson
September 11, 2019

Lecture 3 - 82

![image](assets/artificial-intelligence-intro-020/image-216.png)

![image](assets/artificial-intelligence-intro-020/image-217.png)

![image](assets/artificial-intelligence-intro-020/image-218.png)

![image](assets/artificial-intelligence-intro-020/image-219.png)

![image](assets/artificial-intelligence-intro-020/image-220.png)

<!-- page: 83 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Maximize probability of correct class
Putting it all together:

3.2
cat

car

5.1

Q: If all scores are
small random values,
what is the loss?

frog

-1.7

Justin Johnson
September 11, 2019

Lecture 3 - 83

![image](assets/artificial-intelligence-intro-020/image-221.png)

![image](assets/artificial-intelligence-intro-020/image-222.png)

![image](assets/artificial-intelligence-intro-020/image-223.png)

![image](assets/artificial-intelligence-intro-020/image-224.png)

![image](assets/artificial-intelligence-intro-020/image-225.png)

<!-- page: 84 -->

Cross-Entropy Loss (Multinomial Logistic Regression)

Want to interpret raw classifier scores as probabilities

Softmax
function

Maximize probability of correct class
Putting it all together:

3.2
cat

car

5.1

Q: If all scores are
small random values,
what is the loss?

A: -log(C)

frog

-1.7

log(10) ≈ 2.3

Justin Johnson
September 11, 2019

Lecture 3 - 84

![image](assets/artificial-intelligence-intro-020/image-226.png)

![image](assets/artificial-intelligence-intro-020/image-227.png)

![image](assets/artificial-intelligence-intro-020/image-228.png)

![image](assets/artificial-intelligence-intro-020/image-229.png)

![image](assets/artificial-intelligence-intro-020/image-230.png)

<!-- page: 85 -->

Cross-Entropy vs SVM Loss

Q: What is cross-entropy loss?

assume scores:
[10, -2, 3]
[10, 9, 9]
[10, -100, -100]
and

What is SVM loss?

A: Cross-entropy loss > 0

SVM loss = 0

Justin Johnson
September 11, 2019

Lecture 3 - 85

![image](assets/artificial-intelligence-intro-020/image-231.png)

![image](assets/artificial-intelligence-intro-020/image-232.png)

<!-- page: 86 -->

Cross-Entropy vs SVM Loss

Q: What is cross-entropy loss?

assume scores:
[10, -2, 3]
[10, 9, 9]
[10, -100, -100]
and

What is SVM loss?

A: Cross-entropy loss > 0

SVM loss = 0

Justin Johnson
September 11, 2019

Lecture 3 - 86

![image](assets/artificial-intelligence-intro-020/image-233.png)

![image](assets/artificial-intelligence-intro-020/image-234.png)

<!-- page: 87 -->

Cross-Entropy vs SVM Loss

Q: What happens to each loss if I
slightly change the scores of the last
datapoint?

assume scores:
[10, -2, 3]
[10, 9, 9]
[10, -100, -100]
and

A: Cross-entropy loss will change;

SVM loss will stay the same

Justin Johnson
September 11, 2019

Lecture 3 - 87

![image](assets/artificial-intelligence-intro-020/image-235.png)

![image](assets/artificial-intelligence-intro-020/image-236.png)

<!-- page: 88 -->

Cross-Entropy vs SVM Loss

Q: What happens to each loss if I
slightly change the scores of the last
datapoint?

assume scores:
[10, -2, 3]
[10, 9, 9]
[10, -100, -100]
and

A: Cross-entropy loss will change;

SVM loss will stay the same

Justin Johnson
September 11, 2019

Lecture 3 - 88

![image](assets/artificial-intelligence-intro-020/image-237.png)

![image](assets/artificial-intelligence-intro-020/image-238.png)

<!-- page: 89 -->

Cross-Entropy vs SVM Loss

Q: What happens to each loss if I
double the score of the correct class
from 10 to 20?

assume scores:
[10, -2, 3]
[10, 9, 9]
[10, -100, -100]
and

A: Cross-entropy loss will decrease,

SVM loss still 0

Justin Johnson
September 11, 2019

Lecture 3 - 89

![image](assets/artificial-intelligence-intro-020/image-239.png)

![image](assets/artificial-intelligence-intro-020/image-240.png)

<!-- page: 90 -->

Cross-Entropy vs SVM Loss

Q: What happens to each loss if I
double the score of the correct class
from 10 to 20?

assume scores:
[10, -2, 3]
[10, 9, 9]
[10, -100, -100]
and

A: Cross-entropy loss will decrease,

SVM loss still 0

Justin Johnson
September 11, 2019

Lecture 3 - 90

![image](assets/artificial-intelligence-intro-020/image-241.png)

![image](assets/artificial-intelligence-intro-020/image-242.png)

<!-- page: 91 -->

Recap: Three ways to think about linear classifiers

Algebraic Viewpoint
Visual Viewpoint
Geometric Viewpoint

One template

Hyperplanes
cutting up space

f(x,W) = Wx

per class

Justin Johnson
September 11, 2019

Lecture 3 - 91

![image](assets/artificial-intelligence-intro-020/image-243.png)

![image](assets/artificial-intelligence-intro-020/image-244.png)

![image](assets/artificial-intelligence-intro-020/image-245.png)

![image](assets/artificial-intelligence-intro-020/image-246.png)

<!-- page: 92 -->

Recap: Loss Functions quantify preferences

-
We have some dataset of (x, y)

-
We have a score function:

-
We have a loss function:

Linear classifier

Softmax

SVM

Full loss

Justin Johnson
September 11, 2019

Lecture 3 - 92

![image](assets/artificial-intelligence-intro-020/image-247.png)

![image](assets/artificial-intelligence-intro-020/image-248.png)

![image](assets/artificial-intelligence-intro-020/image-249.png)

![image](assets/artificial-intelligence-intro-020/image-250.png)

![image](assets/artificial-intelligence-intro-020/image-251.png)

<!-- page: 93 -->

Recap: Loss Functions quantify preferences

Q: How do we find the best W?

-
We have some dataset of (x, y)

-
We have a score function:

-
We have a loss function:

Linear classifier

Softmax

SVM

Full loss

Justin Johnson
September 11, 2019

Lecture 3 - 93

![image](assets/artificial-intelligence-intro-020/image-252.png)

![image](assets/artificial-intelligence-intro-020/image-253.png)

![image](assets/artificial-intelligence-intro-020/image-254.png)

![image](assets/artificial-intelligence-intro-020/image-255.png)

![image](assets/artificial-intelligence-intro-020/image-256.png)

<!-- page: 94 -->

Next time:
Optimization

Justin Johnson
September 11, 2019

Lecture 3 - 94
