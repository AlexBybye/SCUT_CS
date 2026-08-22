---
source_id: artificial-intelligence-intro-021
course_id: artificial_intelligence_intro
title: "第7章 深度学习（4）-神经网络"
original_file: "学科资料/人工智能导论/神之华工官方PPT，爱来自密歇根大学/第7章 深度学习（4）-神经网络.pdf"
document_role: note
year: 
locator_type: page
---

# 第7章 深度学习（4）-神经网络

<!-- page: 1 -->

Lecture 5:
Neural Networks

Justin Johnson
September 18, 2019

Lecture 5 - 1

<!-- page: 2 -->

Waitlist update

I was confused about the way waitlists work on Monday =(

We have set enrollment sizes of 35 / 85 for 498 / 598

Each day overrides will be sent automatically in waitlist order to fill up
to capacity

If you don’t enroll within a day of getting an override you will be
dropped from the waitlist

Justin Johnson
September 18, 2019

Lecture 5 - 2

<!-- page: 3 -->

Assignment 1

Was due on Sunday

If you use all 3 late days then you can turn it in today with no penalty

If you enrolled late, your A1 will be due one week from the time you
enrolled

Justin Johnson
September 18, 2019

Lecture 5 - 3

<!-- page: 4 -->

Assignment 2

Due Monday, September 30

Much longer than A1 – Start early

Your submission must pass the validation script to be graded!

We will be lenient on A1 submissions, but starting with A2 we will not
grade your assignment if it does not pass the validation script

Justin Johnson
September 18, 2019

Lecture 5 - 4

<!-- page: 5 -->

Where we are:

1. Use Linear Models for image
classification problems

2. Use Loss Functions to express
preferences over different
choices of weights

Softmax
SVM

3. Use Stochastic Gradient
Descent to minimize our loss
functions and train the model

Justin Johnson
September 18, 2019

Lecture 5 - 5

![image](assets/assets/artificial-intelligence-intro-021/image-001.png)

![image](assets/assets/artificial-intelligence-intro-021/image-002.png)

![image](assets/assets/artificial-intelligence-intro-021/image-003.png)

![image](assets/assets/artificial-intelligence-intro-021/image-004.png)

![image](assets/assets/artificial-intelligence-intro-021/image-005.png)

![image](assets/assets/artificial-intelligence-intro-021/image-006.png)

![image](assets/assets/artificial-intelligence-intro-021/image-007.png)

![image](assets/assets/artificial-intelligence-intro-021/image-008.png)

![image](assets/assets/artificial-intelligence-intro-021/image-009.png)

<!-- page: 6 -->

Problem: Linear Classifiers aren’t that powerful

y
Geometric Viewpoint
Visual Viewpoint

One template per class:
Can’t recognize different

modes of a class

x

Justin Johnson
September 18, 2019

Lecture 5 - 6

![image](assets/assets/artificial-intelligence-intro-021/image-010.png)

![image](assets/assets/artificial-intelligence-intro-021/image-011.png)

<!-- page: 7 -->

One solution: Feature Transforms

Original space

y

r = (x2 + y2)1/2
θ = tan-1(y/x)

x

Feature
transform

Justin Johnson
September 18, 2019

Lecture 5 - 7

<!-- page: 8 -->

One solution: Feature Transforms

Original space

Feature space

θ

y

r = (x2 + y2)1/2
θ = tan-1(y/x)

r

x

Feature
transform

Justin Johnson
September 18, 2019

Lecture 5 - 8

<!-- page: 9 -->

One solution: Feature Transforms

Original space

Feature space

θ

y

r = (x2 + y2)1/2
θ = tan-1(y/x)

r

x

Feature
transform

Linear classifier
in feature space

Justin Johnson
September 18, 2019

Lecture 5 - 9

<!-- page: 10 -->

One solution: Feature Transforms

Original space

Feature space

θ

y

r = (x2 + y2)1/2
θ = tan-1(y/x)

r

x

Feature
transform

Linear classifier
in feature space
Nonlinear classifier
in original space!

Justin Johnson
September 18, 2019

Lecture 5 - 10

<!-- page: 11 -->

Image Features: Color Histogram

+1
Ignores texture,
spatial positions

Frog image is in the public domain

Justin Johnson
September 18, 2019

Lecture 5 - 11

![image](assets/assets/artificial-intelligence-intro-021/image-012.png)

![image](assets/assets/artificial-intelligence-intro-021/image-013.png)

<!-- page: 12 -->

Image Features: Histogram of Oriented Gradients (HoG)

1.
Compute edge direction /
strength at each pixel
2.
Divide image into 8x8 regions
3.
Within each region compute a
histogram of edge directions
weighted by edge strength

Lowe, “Object recognition from local scale-invariant features”, ICCV 1999
Dalal and Triggs, "Histograms of oriented gradients for human detection," CVPR 2005

Justin Johnson
September 18, 2019

Lecture 5 - 12

![image](assets/assets/artificial-intelligence-intro-021/image-014.png)

<!-- page: 13 -->

Image Features: Histogram of Oriented Gradients (HoG)

1.
Compute edge direction /
strength at each pixel
2.
Divide image into 8x8 regions
3.
Within each region compute a
histogram of edge directions
weighted by edge strength

Example: 320x240 image gets
divided into 40x30 bins; 8
directions per bin; feature vector
has 30*40*9 = 10,800 numbers

Lowe, “Object recognition from local scale-invariant features”, ICCV 1999
Dalal and Triggs, "Histograms of oriented gradients for human detection," CVPR 2005

Justin Johnson
September 18, 2019
Lecture 5 - 13

![image](assets/assets/artificial-intelligence-intro-021/image-015.png)

![image](assets/assets/artificial-intelligence-intro-021/image-016.png)

<!-- page: 14 -->

Weak edges
Image Features: Histogram of Oriented Gradients (HoG)

Strong diagonal

edges

Edges in all

directions

1.
Compute edge direction /
strength at each pixel
2.
Divide image into 8x8 regions
3.
Within each region compute a
histogram of edge directions
weighted by edge strength

Example: 320x240 image gets
divided into 40x30 bins; 8
directions per bin; feature vector
has 30*40*9 = 10,800 numbers

Lowe, “Object recognition from local scale-invariant features”, ICCV 1999
Dalal and Triggs, "Histograms of oriented gradients for human detection," CVPR 2005

Justin Johnson
September 18, 2019
Lecture 5 - 14

![image](assets/assets/artificial-intelligence-intro-021/image-017.png)

![image](assets/assets/artificial-intelligence-intro-021/image-018.png)

<!-- page: 15 -->

Image Features: Histogram of Oriented Gradients (HoG)

Weak edges

Strong diagonal

edges

Edges in all

directions

Captures
texture and
position,
robust to
small image
changes

1.
Compute edge direction /
strength at each pixel
2.
Divide image into 8x8 regions
3.
Within each region compute a
histogram of edge directions
weighted by edge strength

Example: 320x240 image gets
divided into 40x30 bins; 8
directions per bin; feature vector
has 30*40*9 = 10,800 numbers

Lowe, “Object recognition from local scale-invariant features”, ICCV 1999
Dalal and Triggs, "Histograms of oriented gradients for human detection," CVPR 2005

Justin Johnson
September 18, 2019
Lecture 5 - 15

![image](assets/assets/artificial-intelligence-intro-021/image-019.png)

![image](assets/assets/artificial-intelligence-intro-021/image-020.png)

<!-- page: 16 -->

Image Features: Bag of Words (Data-Driven!)

Step 1: Build codebook

Cluster patches to
form “codebook”
of “visual words”

Extract random

patches

Fei-Fei and Perona, “A bayesian hierarchical model for learning natural scene categories”, CVPR 2005

Car image is CC0 1.0 public domain

Justin Johnson
September 18, 2019

Lecture 5 - 16

![image](assets/assets/artificial-intelligence-intro-021/image-021.png)

![image](assets/assets/artificial-intelligence-intro-021/image-022.png)

![image](assets/assets/artificial-intelligence-intro-021/image-023.png)

![image](assets/assets/artificial-intelligence-intro-021/image-024.png)

![image](assets/assets/artificial-intelligence-intro-021/image-025.png)

![image](assets/assets/artificial-intelligence-intro-021/image-026.png)

![image](assets/assets/artificial-intelligence-intro-021/image-027.png)

<!-- page: 17 -->

Image Features: Bag of Words (Data-Driven!)

Step 1: Build codebook

Cluster patches to
form “codebook”
of “visual words”

Extract random

patches

Step 2: Encode images

Fei-Fei and Perona, “A bayesian hierarchical model for learning natural scene categories”, CVPR 2005

Justin Johnson
September 18, 2019

Lecture 5 - 17

![image](assets/assets/artificial-intelligence-intro-021/image-028.png)

![image](assets/assets/artificial-intelligence-intro-021/image-029.png)

![image](assets/assets/artificial-intelligence-intro-021/image-030.png)

![image](assets/assets/artificial-intelligence-intro-021/image-031.png)

![image](assets/assets/artificial-intelligence-intro-021/image-032.png)

![image](assets/assets/artificial-intelligence-intro-021/image-033.png)

![image](assets/assets/artificial-intelligence-intro-021/image-034.png)

![image](assets/assets/artificial-intelligence-intro-021/image-035.png)

![image](assets/assets/artificial-intelligence-intro-021/image-036.png)

![image](assets/assets/artificial-intelligence-intro-021/image-037.png)

![image](assets/assets/artificial-intelligence-intro-021/image-038.png)

![image](assets/assets/artificial-intelligence-intro-021/image-039.png)

![image](assets/assets/artificial-intelligence-intro-021/image-040.png)

![image](assets/assets/artificial-intelligence-intro-021/image-041.png)

<!-- page: 18 -->

Image Features

Justin Johnson
September 18, 2019

Lecture 5 - 18

![image](assets/assets/artificial-intelligence-intro-021/image-042.png)

<!-- page: 19 -->

Example: Winner of 2011 ImageNet challenge

F. Perronnin, J. Sánchez, “Compressed Fisher vectors for LSVRC”, PASCAL VOC / ImageNet workshop, ICCV, 2011.

Justin Johnson
September 18, 2019

Lecture 5 - 19

![image](assets/assets/artificial-intelligence-intro-021/image-043.png)

<!-- page: 20 -->

Image Features

f

Feature Extraction

10 numbers giving
scores for classes

training

Justin Johnson
September 18, 2019

Lecture 5 - 20

![image](assets/assets/artificial-intelligence-intro-021/image-044.png)

<!-- page: 21 -->

Image Features vs Neural Networks

f

Feature Extraction

10 numbers giving
scores for classes

training

Krizhevsky, Sutskever, and Hinton, “Imagenet classification
with deep convolutional neural networks”, NIPS 2012.
Figure copyright Krizhevsky, Sutskever, and Hinton, 2012.
Reproduced with permission.

10 numbers giving
scores for classes

training

Justin Johnson
September 18, 2019

Lecture 5 - 21

![image](assets/assets/artificial-intelligence-intro-021/image-045.png)

![image](assets/assets/artificial-intelligence-intro-021/image-046.png)

![image](assets/assets/artificial-intelligence-intro-021/image-047.png)

<!-- page: 22 -->

Neural Networks

(Before) Linear score function:

Justin Johnson
September 18, 2019

Lecture 5 - 22

<!-- page: 23 -->

Neural Networks

(Before) Linear score function:

(Now) 2-layer Neural Network

(In practice we will usually add a learnable bias at each layer as well)

Justin Johnson
September 18, 2019

Lecture 5 - 23

![image](assets/assets/artificial-intelligence-intro-021/image-048.png)

<!-- page: 24 -->

Neural Networks

(Before) Linear score function:

(Now) 2-layer Neural Network

or 3-layer Neural Network

(In practice we will usually add a learnable bias at each layer as well)

Justin Johnson
September 18, 2019

Lecture 5 - 24

![image](assets/assets/artificial-intelligence-intro-021/image-049.png)

![image](assets/assets/artificial-intelligence-intro-021/image-050.png)

<!-- page: 25 -->

Neural Networks

(Before) Linear score function:

(Now) 2-layer Neural Network

x
h
W1
s
W2
Input:

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019

Lecture 5 - 25

![image](assets/assets/artificial-intelligence-intro-021/image-051.png)

![image](assets/assets/artificial-intelligence-intro-021/image-052.png)

<!-- page: 26 -->

Neural Networks

(Before) Linear score function:

(Now) 2-layer Neural Network

Element (i, j)
of W2 gives
the effect on
si from hj

Element (i, j)
of W1 gives
the effect on
hi from xj

x
h
s
Input:

W1
W2

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019

Lecture 5 - 26

![image](assets/assets/artificial-intelligence-intro-021/image-053.png)

![image](assets/assets/artificial-intelligence-intro-021/image-054.png)

<!-- page: 27 -->

Neural Networks

(Before) Linear score function:

(Now) 2-layer Neural Network

Element (i, j) of W2
gives the effect on
si from hj

Element (i, j) of W1
gives the effect on
hi from xj

x
h
W1
s
W2
Input:

3072

All elements
of h affect all
elements of s
Fully-connected neural network
Also “Multi-Layer Perceptron” (MLP)

All elements
of x affect all
elements of h

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019

Lecture 5 - 27

![image](assets/assets/artificial-intelligence-intro-021/image-055.png)

<!-- page: 28 -->

Neural Networks

(Before) Linear score function:

(Now) 2-layer Neural Network

Linear classifier: One template per class

x
h
W1
s
W2
Input:

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019

Lecture 5 - 28

![image](assets/assets/artificial-intelligence-intro-021/image-056.png)

![image](assets/assets/artificial-intelligence-intro-021/image-057.png)

![image](assets/assets/artificial-intelligence-intro-021/image-058.png)

<!-- page: 29 -->

Neural Networks

Neural net: first layer is bank of templates;
Second layer recombines templates

(Before) Linear score function:

(Now) 2-layer Neural Network

x
h
s
Input:

W1
W2

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019

Lecture 5 - 29

![image](assets/assets/artificial-intelligence-intro-021/image-059.png)

![image](assets/assets/artificial-intelligence-intro-021/image-060.png)

<!-- page: 30 -->

Neural Networks

Can use different templates to
cover multiple modes of a class!

(Before) Linear score function:

(Now) 2-layer Neural Network

x
h
s
Input:

W1
W2

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019

Lecture 5 - 30

![image](assets/assets/artificial-intelligence-intro-021/image-061.png)

![image](assets/assets/artificial-intelligence-intro-021/image-062.png)

<!-- page: 31 -->

Neural Networks

“Distributed representation”:
Most templates not interpretable!

(Before) Linear score function:

(Now) 2-layer Neural Network

x
h
s
Input:

W1
W2

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019

Lecture 5 - 31

![image](assets/assets/artificial-intelligence-intro-021/image-063.png)

![image](assets/assets/artificial-intelligence-intro-021/image-064.png)

<!-- page: 32 -->

Deep Neural Networks

Depth = number of layers

Width:
Size of
each
layer

x
h1
W1
s
W6

h2
h3
h4
h5
W2
W3
W4
W5

Output: 10

Input:

3072

Justin Johnson
September 18, 2019

Lecture 5 - 32

<!-- page: 33 -->

Activation Functions

2-layer Neural Network

The function
is called “Rectified Linear Unit”

This is called the activation function of
the neural network

Justin Johnson
September 18, 2019

Lecture 5 - 33

![image](assets/assets/artificial-intelligence-intro-021/image-065.png)

![image](assets/assets/artificial-intelligence-intro-021/image-066.png)

<!-- page: 34 -->

Activation Functions

2-layer Neural Network

The function
is called “Rectified Linear Unit”

This is called the activation function of
the neural network

Q: What happens if we build a neural
network with no activation function?

Justin Johnson
September 18, 2019

Lecture 5 - 34

![image](assets/assets/artificial-intelligence-intro-021/image-067.png)

![image](assets/assets/artificial-intelligence-intro-021/image-068.png)

<!-- page: 35 -->

Activation Functions

2-layer Neural Network

The function
is called “Rectified Linear Unit”

This is called the activation function of
the neural network

Q: What happens if we build a neural
network with no activation function?

A: We end up with a linear classifier!

Justin Johnson
September 18, 2019

Lecture 5 - 35

![image](assets/assets/artificial-intelligence-intro-021/image-069.png)

![image](assets/assets/artificial-intelligence-intro-021/image-070.png)

<!-- page: 36 -->

Activation Functions

Leaky ReLU

Sigmoid

tanh

Maxout

ELU

ReLU

Justin Johnson
September 18, 2019

Lecture 5 - 36

![image](assets/assets/artificial-intelligence-intro-021/image-071.png)

![image](assets/assets/artificial-intelligence-intro-021/image-072.png)

![image](assets/assets/artificial-intelligence-intro-021/image-073.png)

![image](assets/assets/artificial-intelligence-intro-021/image-074.png)

![image](assets/assets/artificial-intelligence-intro-021/image-075.png)

<!-- page: 37 -->

Activation Functions

ReLU is a good default choice
for most problems

Leaky ReLU

Sigmoid

tanh

Maxout

ELU

ReLU

Justin Johnson
September 18, 2019

Lecture 5 - 37

![image](assets/assets/artificial-intelligence-intro-021/image-076.png)

![image](assets/assets/artificial-intelligence-intro-021/image-077.png)

![image](assets/assets/artificial-intelligence-intro-021/image-078.png)

![image](assets/assets/artificial-intelligence-intro-021/image-079.png)

![image](assets/assets/artificial-intelligence-intro-021/image-080.png)

<!-- page: 38 -->

Neural Net in <20 lines!

Justin Johnson
September 18, 2019

Lecture 5 - 38

![image](assets/assets/artificial-intelligence-intro-021/image-081.png)

![image](assets/assets/artificial-intelligence-intro-021/image-082.png)

<!-- page: 39 -->

Neural Net in <20 lines!

Initialize weights
and data

Justin Johnson
September 18, 2019

Lecture 5 - 39

![image](assets/assets/artificial-intelligence-intro-021/image-083.png)

![image](assets/assets/artificial-intelligence-intro-021/image-084.png)

<!-- page: 40 -->

Neural Net in <20 lines!

Initialize weights
and data

Compute loss
(sigmoid activation,
L2 loss)

Justin Johnson
September 18, 2019

Lecture 5 - 40

![image](assets/assets/artificial-intelligence-intro-021/image-085.png)

![image](assets/assets/artificial-intelligence-intro-021/image-086.png)

<!-- page: 41 -->

Neural Net in <20 lines!

Initialize weights
and data

Compute loss
(sigmoid activation,
L2 loss)

Compute
gradients

Justin Johnson
September 18, 2019

Lecture 5 - 41

![image](assets/assets/artificial-intelligence-intro-021/image-087.png)

![image](assets/assets/artificial-intelligence-intro-021/image-088.png)

<!-- page: 42 -->

Neural Net in <20 lines!

Initialize weights
and data

Compute loss
(sigmoid activation,
L2 loss)

Compute
gradients

SGD
step

Justin Johnson
September 18, 2019

Lecture 5 - 42

![image](assets/assets/artificial-intelligence-intro-021/image-089.png)

![image](assets/assets/artificial-intelligence-intro-021/image-090.png)

<!-- page: 43 -->

This image by Fotis Bobolas is

licensed under CC-BY 2.0

Justin Johnson
September 18, 2019
Lecture 5 - 43

![image](assets/assets/artificial-intelligence-intro-021/image-091.png)

<!-- page: 44 -->

Our brains are made of Neurons

Presynaptic
terminal

Axon

Cell
body

Dendrite

Neuron image by Felipe Perucho

is licensed under CC-BY 3.0

Justin Johnson
September 18, 2019

Lecture 5 - 44

<!-- page: 45 -->

Our brains are made of Neurons

Presynaptic
terminal

Axon

Synapse

Cell
body

Dendrite

Justin Johnson
September 18, 2019

Lecture 5 - 45

<!-- page: 46 -->

Our brains are made of Neurons

Presynaptic
terminal

Axon

Impulses carried
away from cell body

Synapse

Cell
body

Impulses
carried toward
cell body

Dendrite

Justin Johnson
September 18, 2019

Lecture 5 - 46

<!-- page: 47 -->

Our brains are made of Neurons

Presynaptic
terminal

Axon

Impulses carried
away from cell body

Synapse

Cell
body

Firing rate is a
nonlinear function
of inputs

Impulses
carried toward
cell body

Dendrite

Justin Johnson
September 18, 2019

Lecture 5 - 47

![image](assets/assets/artificial-intelligence-intro-021/image-092.png)

<!-- page: 48 -->

terminal
Biological Neuron

presynaptic

Artificial Neuron

dendrite

axon

cell
body

Neuron image by Felipe Perucho

is licensed under CC-BY 3.0

Justin Johnson
September 18, 2019
Lecture 5 - 48

![image](assets/assets/artificial-intelligence-intro-021/image-093.png)

![image](assets/assets/artificial-intelligence-intro-021/image-094.png)

<!-- page: 49 -->

Biological Neurons:
Complex connectivity patterns

Neurons in a neural network:
Organized into regular layers for
computational efficiency

This image is CC0 Public Domain

Justin Johnson
September 18, 2019
Lecture 5 - 49

![image](assets/assets/artificial-intelligence-intro-021/image-095.png)

![image](assets/assets/artificial-intelligence-intro-021/image-096.png)

<!-- page: 50 -->

Biological Neurons:
Complex connectivity patterns

But neural networks with random
connections can work too!

This image is CC0 Public Domain

Xie et al, “Exploring Randomly Wired Neural Networks for Image Recognition”, ICCV 2019

Justin Johnson
September 18, 2019
Lecture 5 - 50

![image](assets/assets/artificial-intelligence-intro-021/image-097.png)

![image](assets/assets/artificial-intelligence-intro-021/image-098.png)

<!-- page: 51 -->

Be very careful with brain analogies!

Biological Neurons:

●
Many different types

●
Dendrites can perform complex non-linear computations

●
Synapses are not a single weight but a complex non-
linear dynamical system

●
Rate code may not be adequate

[Dendritic Computation. London and Hausser]

Justin Johnson
September 18, 2019

Lecture 5 - 51

<!-- page: 52 -->

Space Warping

Consider a linear transform: h = Wx
Where x, h are both 2-dimensional

x2

x1

Justin Johnson
September 18, 2019

Lecture 5 - 52

<!-- page: 53 -->

Space Warping

Consider a linear transform: h = Wx
Where x, h are both 2-dimensional

x2

h2

Feature transform:

h = Wx

h1

x1

Justin Johnson
September 18, 2019

Lecture 5 - 53

<!-- page: 54 -->

Space Warping

Consider a linear transform: h = Wx
Where x, h are both 2-dimensional

x2

h2

A
A
B
B

Feature transform:

h = Wx

D

h1

x1

C
C
D

Justin Johnson
September 18, 2019

Lecture 5 - 54

<!-- page: 55 -->

Space Warping

Consider a linear transform: h = Wx
Where x, h are both 2-dimensional
Points not linearly
separable in original space

x2

x1

Justin Johnson
September 18, 2019

Lecture 5 - 55

<!-- page: 56 -->

Space Warping

Consider a linear transform: h = Wx
Where x, h are both 2-dimensional
Points not linearly
separable in original space
Not linearly separable
in feature space

x2

h2

Feature transform:

h = Wx

h1

x1

Justin Johnson
September 18, 2019

Lecture 5 - 56

<!-- page: 57 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

x2

h2

Feature transform:

h = ReLU(Wx)

h1

x1

Justin Johnson
September 18, 2019

Lecture 5 - 57

![image](assets/assets/artificial-intelligence-intro-021/image-099.png)

<!-- page: 58 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

x2

h2

h = ReLU(Wx)
A
A

Feature transform:

h1

x1

Justin Johnson
September 18, 2019

Lecture 5 - 58

![image](assets/assets/artificial-intelligence-intro-021/image-100.png)

<!-- page: 59 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

x2

h2

h = ReLU(Wx)
A
A
B
B
B is “collapsed”
onto +h2 axis

Feature transform:

h1

x1

Justin Johnson
September 18, 2019

Lecture 5 - 59

![image](assets/assets/artificial-intelligence-intro-021/image-101.png)

<!-- page: 60 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

x2

h2

h = ReLU(Wx)
A
A
B
B
B is “collapsed”
onto +h2 axis

Feature transform:

D

h1

x1

D

D “collapsed”
onto +h1 axis

Justin Johnson
September 18, 2019

Lecture 5 - 60

![image](assets/assets/artificial-intelligence-intro-021/image-102.png)

<!-- page: 61 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

x2

h2

h = ReLU(Wx)
A
A
B
B
B is “collapsed”
onto +h2 axis

Feature transform:

D

h1

x1

D “collapsed”
onto +h1 axis
C
C

D

C “collapsed”
onto origin

Justin Johnson
September 18, 2019

Lecture 5 - 61

![image](assets/assets/artificial-intelligence-intro-021/image-103.png)

<!-- page: 62 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

Points not linearly
separable in original space

x2

h2

Feature transform:

h = Wx

h1

x1

Justin Johnson
September 18, 2019

Lecture 5 - 62

<!-- page: 63 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

Points not linearly
separable in original space

x2

h2

Feature transform:

h = ReLU(Wx)

h1

x1

Justin Johnson
September 18, 2019

Lecture 5 - 63

![image](assets/assets/artificial-intelligence-intro-021/image-104.png)

<!-- page: 64 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

Points not linearly
separable in original space

x2

h2

Feature transform:

h = ReLU(Wx)

h1

x1

Points are linearly
separable in features space!

Justin Johnson
September 18, 2019

Lecture 5 - 64

![image](assets/assets/artificial-intelligence-intro-021/image-105.png)

<!-- page: 65 -->

Space Warping

Consider a neural net hidden layer:
h = ReLU(Wx) = max(0, Wx)
Where x, h are both 2-dimensional

Points not linearly
separable in original space

x2

h2

Feature transform:

h = ReLU(Wx)

h1

x1

Points are linearly
separable in features space!

Linear classifier in feature
space gives nonlinear
classifier in original space

Justin Johnson
September 18, 2019

Lecture 5 - 65

![image](assets/assets/artificial-intelligence-intro-021/image-106.png)

<!-- page: 66 -->

Setting the number of layers and their sizes

3 hidden units
6 hidden units
20 hidden units

More hidden units = more capacity

Justin Johnson
September 18, 2019

Lecture 5 - 66

![image](assets/assets/artificial-intelligence-intro-021/image-107.png)

<!-- page: 67 -->

Don’t regularize with size; instead use stronger L2

(Web demo with ConvNetJS:
http://cs.stanford.edu/people/karpathy/convnetjs/demo/classify2d.html)

Justin Johnson
September 18, 2019

Lecture 5 - 67

![image](assets/assets/artificial-intelligence-intro-021/image-108.png)

<!-- page: 68 -->

Universal Approximation

A neural network with one hidden layer can approximate
any function f: RN -> RM with arbitrary precision*

*Many technical conditions: Only holds on compact subsets of RN; function must be continuous; need to define “arbitrary precision”; etc

Justin Johnson
September 18, 2019

Lecture 5 - 68

<!-- page: 69 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

h1

u1

w1

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

Justin Johnson
September 18, 2019

Lecture 5 - 69

<!-- page: 70 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

h1

u1

w1

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

Justin Johnson
September 18, 2019

Lecture 5 - 70

<!-- page: 71 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

h1

u1

w1

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

Justin Johnson
September 18, 2019

Lecture 5 - 71

<!-- page: 72 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

h1

u1

w1

Output is a sum of shifted, scaled ReLUs:

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

Justin Johnson
September 18, 2019

Lecture 5 - 72

![image](assets/assets/artificial-intelligence-intro-021/image-109.png)

<!-- page: 73 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

h1

u1

w1

Output is a sum of shifted, scaled ReLUs:

w2

u2

Output:

h2

y

x

u3
Input:

Flip left / right based on sign of wi

y (1,)

x (1,)

w3

h3

Slope is given
by ui * wi

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

Position of
“bend” given by bi

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

Justin Johnson
September 18, 2019

Lecture 5 - 73

![image](assets/assets/artificial-intelligence-intro-021/image-110.png)

<!-- page: 74 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

We can build a “bump function”
using four hidden units

h1

u1

y

w1

t

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

x

s1 s2
s3 s4

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

Justin Johnson
September 18, 2019

Lecture 5 - 74

<!-- page: 75 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

We can build a “bump function”
using four hidden units

h1

u1

y

w1

t

m1 = t / (s2 – s1)
m2 = t / (s4 – s3)
m2
m1

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

x

s1 s2
s3 s4

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

Justin Johnson
September 18, 2019

Lecture 5 - 75

<!-- page: 76 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

We can build a “bump function”
using four hidden units

h1

u1

y

w1

t

m1 = t / (s2 – s1)
m2 = t / (s4 – s3)

w2

u2

Output:

h2

y

x

u3
Input:

m2
m1

y (1,)

x (1,)

w3

h3

x

s1 s2
s3

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

m1 * max(0, x – s1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

Justin Johnson
September 18, 2019

Lecture 5 - 76

<!-- page: 77 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

We can build a “bump function”
using four hidden units

h1

u1

y

w1

t

m1 = t / (s2 – s1)
m2 = t / (s4 – s3)

w2

u2

Output:

h2

y

x

u3
Input:

m2
m1

y (1,)

x (1,)

w3

h3

x

s1 s2
s3 s4

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

m1 * max(0, x – s1)
-m1 * max(0, x – s2)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

Justin Johnson
September 18, 2019

Lecture 5 - 77

<!-- page: 78 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

We can build a “bump function”
using four hidden units

h1

u1

y

w1

t

m1 = t / (s2 – s1)
m2 = t / (s4 – s3)

w2

u2

Output:

h2

y

x

u3
Input:

m2
m1

y (1,)

x (1,)

w3

h3

x

s1 s2
s3 s4

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

m1 * max(0, x – s1)
-m1 * max(0, x – s2)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

-m2 * max(0, x – s3)

Justin Johnson
September 18, 2019

Lecture 5 - 78

<!-- page: 79 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

We can build a “bump function”
using four hidden units

h1

u1

y

w1

t

m1 = t / (s2 – s1)
m2 = t / (s4 – s3)

w2

u2

Output:

h2

y

x

u3
Input:

m2
m1

y (1,)

x (1,)

w3

h3

x

s1 s2
s3 s4

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

m1 * max(0, x – s1)
-m1 * max(0, x – s2)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

-m2 * max(0, x – s3)
m2 * max(0, x – s4)

Justin Johnson
September 18, 2019

Lecture 5 - 79

<!-- page: 80 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

We can build a “bump function”
using four hidden units

h1

u1

y

w1

t

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

x

s1 s2
s3 s4

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

With 4K hidden units we can
build a sum of K bumps

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

x

Justin Johnson
September 18, 2019

Lecture 5 - 80

<!-- page: 81 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

We can build a “bump function”
using four hidden units

h1

u1

y

w1

t

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

x

s1 s2
s3 s4

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

With 4K hidden units we can
build a sum of K bumps

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p

x

Approximate functions with bumps!

Justin Johnson
September 18, 2019

Lecture 5 - 81

![image](assets/assets/artificial-intelligence-intro-021/image-111.png)

<!-- page: 82 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

h1

What about…
- Gaps between bumps?
- Other nonlinearities?
- Higher-dimensional functions?

u1

w1

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

First layer weights: w (3,1)

Second layer weights: u (1,3)

See Nielsen, Chapter 4

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p
x
Approximate functions with bumps!

Justin Johnson
September 18, 2019

Lecture 5 - 82

![image](assets/assets/artificial-intelligence-intro-021/image-112.png)

<!-- page: 83 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

Reality check: Networks don’t really learn bumps!

h1

u1

w1

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

First layer weights: w (3,1)

Second layer weights: u (1,3)

First layer bias: b (3,)

First layer bias: p (1,)

h1 = max(0, w1 * x + b1)
h2 = max(0, w2 * x + b2)
h3 = max(0, w3 * x + b3)
y = u1 * h1 + u2 * h2 + u3 * h3 + p

y = u1 * max(0, w1 * x + b1)

+ u2 * max(0, w2 * x + b2)
+ u3 * max(0, w3 * x + b3)
+ p
x
Approximate functions with bumps!

Justin Johnson
September 18, 2019

Lecture 5 - 83

![image](assets/assets/artificial-intelligence-intro-021/image-113.png)

![image](assets/assets/artificial-intelligence-intro-021/image-114.png)

<!-- page: 84 -->

Universal Approximation

Example: Approximating a function f: R -> R with a two-layer ReLU network

Reality check: Networks don’t really learn bumps!

h1

u1

w1

w2

u2

Output:

h2

y

x

u3
Input:

y (1,)

x (1,)

w3

h3

Universal approximation tells us:
-
Neural nets can represent any function

Universal approximation DOES NOT tell us:
-
Whether we can actually learn any function with SGD
-
How much data we need to learn a function

x
Approximate functions with bumps!

Remember: kNN is also a universal approximator!

Justin Johnson
September 18, 2019

Lecture 5 - 84

![image](assets/assets/artificial-intelligence-intro-021/image-115.png)

![image](assets/assets/artificial-intelligence-intro-021/image-116.png)

<!-- page: 85 -->

Convex Functions

A function                                      is convex if for all                                     ,

Justin Johnson
September 18, 2019

Lecture 4 - 85

<!-- page: 86 -->

Convex Functions

A function                                      is convex if for all                                     ,

Example:                          is convex:

Justin Johnson
September 18, 2019

Lecture 4 - 86

![image](assets/assets/artificial-intelligence-intro-021/image-117.png)

<!-- page: 87 -->

Convex Functions

A function                                      is convex if for all                                     ,

Example:                          is convex:

x1
x2

Justin Johnson
September 18, 2019

Lecture 4 - 87

![image](assets/assets/artificial-intelligence-intro-021/image-118.png)

<!-- page: 88 -->

Convex Functions

A function                                      is convex if for all                                     ,

Example:                          is convex:

x1
x2

Justin Johnson
September 18, 2019

Lecture 4 - 88

![image](assets/assets/artificial-intelligence-intro-021/image-119.png)

<!-- page: 89 -->

Convex Functions

A function                                      is convex if for all                                     ,

x1
x2

Example:
is not convex:

Justin Johnson
September 18, 2019

Lecture 4 - 89

![image](assets/assets/artificial-intelligence-intro-021/image-120.png)

<!-- page: 90 -->

Convex Functions

A function                                      is convex if for all                                     ,

Intuition: A convex function
is a (multidimensional) bowl

*Many technical details! See e.g. IOE 661 / MATH 663

Justin Johnson
September 18, 2019

Lecture 4 - 90

![image](assets/assets/artificial-intelligence-intro-021/image-121.png)

<!-- page: 91 -->

Convex Functions

A function                                      is convex if for all                                     ,

Intuition: A convex function
is a (multidimensional) bowl

Generally speaking, convex
functions are easy to optimize: can
derive theoretical guarantees about
converging to global minimum*

*Many technical details! See e.g. IOE 661 / MATH 663

Justin Johnson
September 18, 2019

Lecture 4 - 91

![image](assets/assets/artificial-intelligence-intro-021/image-122.png)

<!-- page: 92 -->

Convex Functions

A function                                      is convex if for all                                     ,

Linear classifiers optimize
a convex function!

Intuition: A convex function
is a (multidimensional) bowl

Generally speaking, convex
functions are easy to optimize: can
derive theoretical guarantees about
converging to global minimum*

Softmax

SVM

R(W) = L2 or L1 regularization

*Many technical details! See e.g. IOE 661 / MATH 663

Justin Johnson
September 18, 2019

Lecture 4 - 92

![image](assets/assets/artificial-intelligence-intro-021/image-123.png)

![image](assets/assets/artificial-intelligence-intro-021/image-124.png)

![image](assets/assets/artificial-intelligence-intro-021/image-125.png)

![image](assets/assets/artificial-intelligence-intro-021/image-126.png)

<!-- page: 93 -->

Convex Functions

A function                                      is convex if for all                                     ,

Neural net losses sometimes look
convex-ish:

Intuition: A convex function
is a (multidimensional) bowl

Generally speaking, convex
functions are easy to optimize: can
derive theoretical guarantees about
converging to global minimum*

1D slice of loss landscape for a 4-layer ReLU network with 10 input features, 32 units
per hidden layer, 10 categories, with softmax loss

*Many technical details! See e.g. IOE 661 / MATH 663

Justin Johnson
September 18, 2019

Lecture 4 - 93

![image](assets/assets/artificial-intelligence-intro-021/image-127.png)

<!-- page: 94 -->

Convex Functions

A function                                      is convex if for all                                     ,

But often clearly nonconvex:

Intuition: A convex function
is a (multidimensional) bowl

Generally speaking, convex
functions are easy to optimize: can
derive theoretical guarantees about
converging to global minimum*

1D slice of loss landscape for a 4-layer ReLU network with 10 input features, 32 units
per hidden layer, 10 categories, with softmax loss

*Many technical details! See e.g. IOE 661 / MATH 663

Justin Johnson
September 18, 2019

Lecture 4 - 94

![image](assets/assets/artificial-intelligence-intro-021/image-128.png)

<!-- page: 95 -->

Convex Functions

A function                                      is convex if for all                                     ,

With local minima:

Intuition: A convex function
is a (multidimensional) bowl

Generally speaking, convex
functions are easy to optimize: can
derive theoretical guarantees about
converging to global minimum*

1D slice of loss landscape for a 4-layer ReLU network with 10 input features, 32 units
per hidden layer, 10 categories, with softmax loss

*Many technical details! See e.g. IOE 661 / MATH 663

Justin Johnson
September 18, 2019

Lecture 4 - 95

![image](assets/assets/artificial-intelligence-intro-021/image-129.png)

<!-- page: 96 -->

Convex Functions

A function                                      is convex if for all                                     ,

Can get very wild!

Intuition: A convex function
is a (multidimensional) bowl

Generally speaking, convex
functions are easy to optimize: can
derive theoretical guarantees about
converging to global minimum*

1D slice of loss landscape for a 4-layer ReLU network with 10 input features, 32 units
per hidden layer, 10 categories, with softmax loss

*Many technical details! See e.g. IOE 661 / MATH 663

Justin Johnson
September 18, 2019

Lecture 4 - 96

![image](assets/assets/artificial-intelligence-intro-021/image-130.png)

<!-- page: 97 -->

Convex Functions

A function                                      is convex if for all                                     ,

Most neural networks need
nonconvex optimization
-
Few or no guarantees
about convergence
-
Empirically it seems to
work anyway
-
Active area of research

Intuition: A convex function
is a (multidimensional) bowl

Generally speaking, convex
functions are easy to optimize: can
derive theoretical guarantees about
converging to global minimum*

*Many technical details! See e.g. IOE 661 / MATH 663

Justin Johnson
September 18, 2019

Lecture 4 - 97

<!-- page: 98 -->

Summary

Feature transform + Linear classifier
allows nonlinear decision boundaries

Neural Networks as learnable feature transforms

Original space

Feature space

Feature Extraction

θ

10 numbers giving
scores for classes

y

r = (x2 + y2)1/2
θ = tan-1(y/x)

training

r

x

Feature
transform

Krizhevsky, Sutskever, and Hinton, “Imagenet classification
with deep convolutional neural networks”, NIPS 2012.
Figure copyright Krizhevsky, Sutskever, and Hinton, 2012.
Reproduced with permission.

Linear classifier
in feature space
Nonlinear classifier
in original space!

10 numbers giving
scores for classes

training

Justin Johnson
September 18, 2019

Lecture 5 - 98

![image](assets/assets/artificial-intelligence-intro-021/image-131.png)

![image](assets/assets/artificial-intelligence-intro-021/image-132.png)

![image](assets/assets/artificial-intelligence-intro-021/image-133.png)

<!-- page: 99 -->

Summary

Linear classifier: One template per class

From linear classifiers to
fully-connected networks

Neural networks: Many reusable templates

x
h
W1
s
W2
Input:

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019

Lecture 5 - 99

![image](assets/assets/artificial-intelligence-intro-021/image-134.png)

![image](assets/assets/artificial-intelligence-intro-021/image-135.png)

![image](assets/assets/artificial-intelligence-intro-021/image-136.png)

![image](assets/assets/artificial-intelligence-intro-021/image-137.png)

<!-- page: 100 -->

Summary

From linear classifiers to
fully-connected networks

Neural networks loosely inspired by biological
neurons but be careful with analogies

x
h
W1
s
W2
Input:

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019
Lecture 5 - 100

![image](assets/assets/artificial-intelligence-intro-021/image-138.png)

<!-- page: 101 -->

Summary
Space Warping
Universal Approximation

From linear classifiers to
fully-connected networks

Nonconvex

x
h
W1
s
W2
Input:

3072

Output: 10

Hidden layer:

100

Justin Johnson
September 18, 2019
Lecture 5 - 101

![image](assets/assets/artificial-intelligence-intro-021/image-139.png)

![image](assets/assets/artificial-intelligence-intro-021/image-140.png)

![image](assets/assets/artificial-intelligence-intro-021/image-141.png)

![image](assets/assets/artificial-intelligence-intro-021/image-142.png)

<!-- page: 102 -->

Problem: How to compute gradients?

Nonlinear score function

SVM Loss on predictions

Regularization

Total loss: data loss + regularization

If we can compute                     then we can learn W1 and W2

Justin Johnson
September 18, 2019

Lecture 5 - 102

![image](assets/assets/artificial-intelligence-intro-021/image-143.png)

![image](assets/assets/artificial-intelligence-intro-021/image-144.png)

<!-- page: 103 -->

Next time:
Backpropagation

Justin Johnson
September 18, 2019

Lecture 5 - 103
