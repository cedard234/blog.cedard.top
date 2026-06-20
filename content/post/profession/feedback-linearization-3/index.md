---
title: 'Feedback Linearization, Part 3'
slug: feedback-linearization-3
date: 2026-06-14T14:51:26+08:00
description: A tutorial on feedback linearization technique, Part 3
math: true
categories:
    - profession
tags:
    - Control Theory
    - Mathematics
---

## Feedback Linearization Theorem
We talked about feedback linearization theorem last time. As a recap:

**Feedback Linearization Theorem**: Nonlinear system $\Sigma: \dot{x} = f(x) + g(x)u$ is feedback linearizable if:
1. $[g(x), ad_fg(x), \ldots, ad_f^{n-1}g(x)]$ has rank $n$ $\forall x$.
2. $\Delta = \text{span}\{g(x), ad_fg(x), \ldots, ad_f^{n-2}g(x)\}$ is involutive.

The first condition guarantees controllability, while the second condition guarantees that we can always find an output $y = h(x)$ that has relative degree equal to the system degree, according to Forbenius theorem. Actually, this is also just observability.

We now look at some examples.

Consider the system
$$ \dot{x} = \begin{pmatrix} a \sin x_2 \\ -x_1^2 \end{pmatrix} + \begin{pmatrix}0 \\ 1 \end{pmatrix}u $$
We would like to ask 2 questions:
1. Is the system feedback linearizable?
2. If so, how shall we find the output $y = h(x)$?

To answer the first question, we first validate if the first condition is met from feedback linearization theorem.
$$
g(x) = \begin{pmatrix}0 \\ 1 \end{pmatrix}
$$
$$ad_fg = [f, g] = \begin{pmatrix} -a \cos x_2 \\ 0 \end{pmatrix}$$
Therefore,
$$
[g(x), ad_fg(x)] = \begin{pmatrix}0 & -a \cos x_2 \\ 1 & 0 \end{pmatrix}
$$
This new matrix is always rank 2, for all $x$, except when $\cos x_2 = 0$. 
The distribution $\Delta = \text{span}\{g(x) \}$ has only one element, so it's trivially involutive. Therefore we conclude the system is feedback linearizable.

Now, how shall we find the output $y$? We would like to find an output $y = h(x)$ such that it has relative degree of $2$, i.e.:

$$\begin{cases}
\begin{align}
\frac{\partial h}{\partial x} g(x) &= 0  \\
\frac{\partial L_f h}{\partial x} g(x) &\neq 0
\end{align}
\end{cases}
$$

The first PDE will give us
$$ \frac{\partial h}{\partial x_2} = 0 $$
meaning $h(x)$ shall be independent of $x_2$. We sub this fact into the second PDE:
$$ \frac{\partial L_f h}{\partial x} g(x) = \frac{\partial L_fh}{\partial x_2} = \frac{\partial h}{\partial x_1}a \cos x_2 \neq 0$$
Therefore, we can pick a few candidate $h(x)$, for example: $x_1$, $x_1^5$, and so forth. If we pick $h(x) = x_1$, then we can linearize the system as
$$ \ddot{y} = v$$
where the state and control transform is given by
$$ \begin{cases}
\begin{align}
y &= x_1 \\
\dot{y} &= a\sin x_2 \\
u &= (x_1^2 + v) \frac{1}{a\cos x_2}
\end{align}
\end{cases}
$$
The audience is encouraged to verify the linearization by substituting the transforms back into the original system.

As a result, we are able to design a linear control between $y$ and $v$ by LQR or pole placement, and we utilize the state and control transform to convert the system back into the original nonlinear system.

## MIMO Feedback Linearization
We now move forward to a more complex and generalized system: the multi-input multi-output nonlinear system. For the sake of simplicity, we limit the MIMO to be the square case (meaning we have the same number of inputs and outputs).

If we have a square MIMO system that looks like:
$$
\begin{align}
\displaystyle \Sigma: \dot{x} &= f(x) + \Sigma_{i=1}^n g_i(x) u_i \quad x \in \mathbb{R}^n \\
&= g(x)u \\
y &= \begin{pmatrix} h_1(x) \\ \vdots \\ h_n(x) \end{pmatrix}
\end{align}
$$
where
$$
\begin{align}
g(x) &= \begin{pmatrix} g_1(x) & \cdots & g_n(x) \end{pmatrix} \\
u &= \begin{pmatrix} u_1 \\ \vdots \\ u_n\end{pmatrix}
\end{align}
$$
The question is now, how shall we define the relative degree of the MIMO system?


### Vector Relative Degree

We introduce the concept of vector relative degree in this case.
**(Definition) Vector Relative Degree**: Nonlinear system $\Sigma$ has relative degree $(r_1, r_2, \ldots, r_n)$ at $x_0$ if:
1. For all $1 \le j \le n, 1 \le i \le n, 0 \le k \le r_i - 2$, 
$$ L_{g_j}L_f^kh_i = 0, \quad \forall x \text{ in a neighborhood of } x_0 $$
2. The $n \times n$ matrix, also known as the **Decoupling Matrix**,
$$
A(x) = \begin{pmatrix}
L_{g_1}L_f^{r_1-1}h_1 & \cdots & L_{g_n}L_f^{r_n-1}h_n \\
\vdots & \cdots & \vdots \\
L_{g_1}L_f^{r_n-1}h_1 & \cdots & L_{g_n}L_f^{r_n-1}h_n
\end{pmatrix}
$$
Then, for the i-th output, we can always express it in terms of
$$
\begin{align}
y_i^{(r_i)} &= L_f^{r_i} h_i(x)+ L_{g_1}L_f^{r_i-1}h_i(x)u_1 + \cdots + L_{g_n}L_f^{r_i-1}h_i(x)u_n \\
&=  L_f^{r_i} h_i(x) + \displaystyle \Sigma_j L_{g_j}L_f^{r_i-1}h_i(x)u_j
\end{align}
$$

If, at least one $L_{g_j}L_f^{r_i-1}h_i(x)$ is non-zero, then the system is feedback linearizable.
Therefore, we can also do IO linearization:

$$
\begin{align}
\begin{pmatrix}
y_1^{(r_1)} \\
\vdots \\
y_n^{(r_n)}
\end{pmatrix}&=\begin{pmatrix}
L_f^{r_1}h_1(x) \\ \vdots \\ L_f^{r_n}h_n
\end{pmatrix} +
\begin{pmatrix}
L_f^{r_1} h_1(x) & \cdots & L_{g_n}L_f^{r_1-1}h_1(x) \\
\vdots & \cdots & \vdots \\
L_f^{r_n} h_n(x) & \cdots & L_{g_n}L_f^{r_n-1}h_n(x)
\end{pmatrix}
\begin{pmatrix}
u_1 \\
\vdots \\
u_n
\end{pmatrix} \\
&= L_fh(x) + A(x) u
\end{align}
$$

where, notice that we implicitly extended the definition of Lie derivative to its vector form.
And the control can be transformed as:
$$
u(x) = A^{-1}(x)(L_fh(x)+ v) \rightarrow \begin{pmatrix} y_1^{(r_1)} \\ \vdots \\ y_n^{(r_n)} \end{pmatrix} = v
$$
.

### MIMO Feedback Linearization Theorem
Now we state the feedback linearization theorem in MIMO form:
**Theorem(MIMO Feedback Linearization)**: A MIMO nonlinear system $\Sigma$ is:
1. feedback linearizable, if its vector relative degree $r = (r_1, r_2, \ldots, r_n)$ satisfies such that
$$ r_1 + \ldots + r_n = \displaystyle \Sigma_{i=1}^n r_i \ge n$$
2. If the sum
$$ r_1 + \ldots + r_n = \displaystyle \Sigma_{i=1}^n r_i < n$$
, then the system can only be IO linearizable, where we have to rely on the internal zero dynamic to be also stable in order for the full system to be stable.

### Examples
Conside a motion of a wheeled vehicle moving in a horizontal plane. The kinematics of the vehicle are given by the differential equations:
$$
\begin{align}
\dot{x} &= V \cos \theta \\
\dot{y} &= V \sin \theta \\
\dot{\theta} &= \omega
\end{align}
$$
Here $(x, y)$ is the location in the horizontal 2D plane, $V$ is the vehicle speed, and $\theta$ denotes the vehicle heading angle, and $\omega$ denotes the vehicle turning rate. 

#### Ill-defined Vector Relative Degree
If we consider the vehicle speed $V$ and the vehicle turning range $\omega$ as two control inputs, and the vehicle locations in the plane as two outputs, the vector relative degree is not well-defined. We notice the system now looks like:
$$
\begin{align}
\frac{d}{dt}\begin{pmatrix} x \\ y \\ \theta \end{pmatrix} &= \begin{pmatrix}u_1 \cos \theta \\ u_1 \sin \theta \\ u_2 \end{pmatrix}
 \\
\begin{pmatrix} y_1 \\ y_2 \end{pmatrix}
&= \begin{pmatrix} x \\ y \end{pmatrix}
\end{align}
$$
If we take the first time derivative of the outputs
$$
\begin{align}
\frac{d}{dt}\begin{pmatrix} y_1 \\ y_2 \end{pmatrix} &= \frac{d}{dt}\begin{pmatrix} x \\ y \end{pmatrix} = \begin{pmatrix} u_1 \cos \theta \\ u_1 \sin \theta \end{pmatrix}
\end{align}
$$
Only the first control input shows up, which is a red flag. If we consider the coupling matrix
$$
A(x) = \begin{pmatrix}
\cos \theta & 0 \\
\sin \theta & 0
\end{pmatrix}
$$
is actually singular. Therefore the relative degree in this case in not well defined.

#### Well-defined Vector Relative Degree
If we now consider the vehicle acceleration and the vehicle turning rate as the two control inputs, and we still use the vehicle position as the two outputs, this time the vehicle relative degree is actually well-defined, so long as $V > 0$ for this 4-th order nonlinear system. We have the original system expressed as:
$$
\begin{align}
\frac{d}{dt} \begin{pmatrix} x \\ y \\ \theta \\ V \end{pmatrix} &= \begin{pmatrix} V \cos \theta \\ V \sin \theta \\ u_2 \\ u_1 \end{pmatrix} \\
\begin{pmatrix} y_1 \\ y_2 \end{pmatrix} &= \begin{pmatrix} x \\ y \end{pmatrix}
\end{align}
$$

If we take the first time derivative of the output vector:
$$
\frac{d}{dt}\begin{pmatrix} y_1 \\ y_2 \end{pmatrix} = \begin{pmatrix} V \cos \theta \\ V \sin \theta \end{pmatrix}
$$
We realize that both inputs don't explicitly show up, therefore we take another round of differentiation:
$$
\frac{d^2}{dt^2}\begin{pmatrix} y_1 \\ y_2 \end{pmatrix} = \begin{pmatrix} u_1 \cos \theta - u_2 V \sin \theta  \\ u_1 \sin \theta + u_2 V \cos \theta  \end{pmatrix}
$$
Now, both inputs show up which is a good sign. We verify this by considering the decoupling matrix:
$$
A(x) = \begin{pmatrix} \cos \theta & -V \sin \theta \\ \sin \theta & V \cos \theta \end{pmatrix} 
$$
And the determinant is given by
$$
\text{det}(A(x)) = V
$$
We now realize that the decoupling matrix is non-sigular, as long as the speed is non-zero. Therefore the vector relative degreee is well-defined.

#### Control Law
Given that $r_1 = r_2 = 2$ in this case, and we satisfy $r_1 + r_2 = 4 = n$, we can find a state transformation and a control transformation so that the original system can be feedback linerized. We consider the control transformation as
$$
\begin{pmatrix}
\xi_1 = y_1 = x\\
\xi_2 = y_2 = y\\
\xi_3 = \dot{y_1} \\
\xi_4 = \dot{y_2}
\end{pmatrix}
$$
And we can derive the control transformation as 
$$
\begin{pmatrix}
v_1 = u_1 \cos \theta - u_2 V \sin \theta \\
v_2 = u_2 \sin \theta + u_2 V \cos \theta 
\end{pmatrix}
$$
and the resulting system now looks like
$$
\begin{align}
\begin{cases}
\dot{\xi_1} &= \xi_3 \\
\dot{\xi_2} &= \xi_4 \\
\dot{\xi_3} &= v_1 \\
\dot{\xi_4} &= v_2 
\end{cases}
\end{align}
$$
Which is happily a double integrator system, thus can be controlled (pole placed, or LQRed) to be stable.
