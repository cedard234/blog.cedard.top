---
title: 'Feedback Linearization, Part 1'
slug: feedback-linearization-1
date: 2026-06-11T21:38:58+08:00
description: A tutorial on feedback linearization technique, Part 1
math: true
categories:
    - Control Theory
tags:
    - Control Theory
    - Mathematics
    - Profession
---

Feedback linearization is a seemingly obvious but powerful technique in control theory that transforms a nonlinear system into a linear one through state and input feedback.

I learned this technique when I was taking MEC237 from Berkeley, and I later realized it's actually pretty useful and one of the most universal techniques in nonlinear control.

## Motivation

Let's consider a first-order nonlinear system:

$$
\dot{x} = x^3 + u
$$

Where $x$ is our internal state, and $u$ is our control input. If the system has no control, state $x$ is unstable. Intuitively, if $x$ is greater than 0, $\dot{x}$ is also greater, pushing it away from the equilibrium point, and vice versa if $x < 0$. 

One caveat here is that, we can't use Lyapunov indirect method to conclude instability, because the Jacobian matrix is 0, and nothing can be concluded from a both non-positive and non-negative Jacobian matrix eigenvalue.

How shall we use the control input to stabilize the system? Let's consider the input $u = -x^3 - x$, where if we sub-into the original system:

$$ \dot{x} = x^3 + (-x^3 - x) = -x $$

This is now a negative feedback system with eigenvalue strictly negative, and we can therefore conclude stability. 

What did we make the control input do? We use a nonlinear term $-x^3$ in the control input to cancel the original system's unstable term, and introduce another stabilizing linear term $-x$ to ensure stability. The mechanism where we use feedback to achieve a stable linear system is called **Feedback Linearization**.

However, is this technique universal? The answer is no. Look at the following system:

$$
\begin{align}
\begin{cases}
\dot{x}_1 = a \sin x_2 \\
\dot{x}_2 = -x_1^2 + u
\end{cases}
\end{align}
$$

In fact, any input $u$ can't linearize both states $x_1$ and $x_2$. However, if we do a **state transformation** like below:

$$
\begin{align}
z_1 &= x_1 \\
z_2 &= a \sin x_2 
\end{align}
$$

Then it's not too hard to verify that the transformed system can actually be linearized. Thus by combining state transform and control transform, we are able to achieve feedback linearization.

## Some Definitions

We now give some useful definitions to help understand the feedback linearization technique.

### Control-Affine System

A system that has the following form is called a **Control-Affine System**:

$$
\dot{x} = f(x) + g(x)u
$$

where $f(x)$ and $g(x)$ are smooth vector fields.

An example of a system that's not control-affine is:
$$
\dot{x} = f(x) + g(x)u^2
$$

### Diffeomorphism

In differential geometry, a **diffeomorphism** is a smooth invertible map between differentiable manifolds, whose inverse is also smooth. To express in mathematical language, such mapping $T$ satisfies $T \in C^1$ and $T^{-1} \in C^1$.

### Feedback Linearizable

A nonlinear control-affine system $\Sigma: \dot{x} = f(x) + g(x)u$ is said to be **feedback linearizable** if there exists a control law $u = \alpha (x) + \beta (x)v$ and state transform $z = T(x)$, where $T$ is a diffeomorphism, such that the transformed system $\dot{z} = Az + Bv$ satisfies $(A, B)$ is controllable.

### Lie Derivative

The **Lie Derivative** is an operator such that:

$$ 
L_f u = \frac{\partial u}{\partial x} f(x)
$$

We will see how Lie derivative helps us simplify some notations later.

### Input-Output Linearization

There are cases that we can't perform full feedback linearization, but we can still achieve input-output linearization. 

Consider the same system that we defined earlier:

$$
\begin{cases}
\dot{x}_1 = a \sin x_2 \\
\dot{x}_2 = -x_1^2 + u \\
y = x_2
\end{cases}
$$

Note that now we assign the output $y$ to be only a function of $x_2$. Now, we can perform **Input-Output Linearization** $ u = x_1^2 + v$ such that:

$$ y = x_2 = -x_1^2 + x_1^2 +v = v$$

from there, we manage to achieve a linear relationship between the new control law $v$ and output $y$. However, since $x_1$ is an unobservable state from $y$, we can't tell just from $y$ whether the inner system is stable -- therefore it's possible for the inner state to explode while the output shows nothing, causing system failure.

---

Now with all these definitions, we would like to answer the following questions:
1. When is a system feedback linearizable?
2. If not feedback linearizable, when is the system IO linearizable?
3. Is there connection between IO linearization and system linearization?

## Relative Degree of Output $y$

Let's consider the following system that is a generalization of a SISO control-affine system:

$$
\begin{align}
\dot{x} &= f(x) + g(x)u \\
y &= h(x)
\end{align}
$$
Where $f, g, h$ are sufficiently smooth.

We notice that $y$ is not a function of $u$, to the first order because there is no direct control term in $y$. Let's try to take the derivative of $y$:

$$
\begin{align}
\dot{y} &= \frac{\partial h(x)}{\partial x} \dot{x} \\
&= \frac{\partial h(x)}{\partial x} (f(x) + g(x)u) \\
&= L_f h(x) + L_g h(x) u
\end{align}
$$
Note that we used the Lie derivation notation. 

Now assume that $L_g h(x) \neq 0$, then we have a direct term $u$ in $\dot{y}$. We can therefore make $u$ such that:

$$
u = L_g h(x) ^ {-1} (-L_f h(x) + v)
$$

and so that:

$$
\dot{y} = v
$$

What if $L_g h(x) = 0$? In that case, $u$ doesn't appear in the first derivative of $y$:

$$
\dot{y} = L_f h(x)
$$

But no worries, we can take another derivative operation:
$$
\ddot{y} = L_f^2 h(x) + L_gL_fh(x)u
$$
Note that, $L_aL_bc(x) = L_a(L_b c(x))$.
Suppose we have $L_gL_fh(x) \neq 0$, then we can again IO linearize the system as:

$$
u = L_gL_f h(x)^{-1}[-L_f^2 h(x) + v]
$$
and thus:
$$
\ddot{y} = v
$$
If we continue doing this, we will arrive at step $r$:
$$
y^{(r)} = L_f^rh(x) +L_gL_f^{r-1}h(x)u
$$
And if we have $L_gL_f^{r-1}h(x) \neq 0$, we can make it such that:
$$
u = L_gL_f^{r-1}h(x)^{-1}[-L_f^r h(x) + v]
$$ 
and therefore
$$
y^{r} = v
$$
In this case, the IO linearized system is a $r^{th}$ order linear system. 

We now give the definition of $r$:

A SISO system $\dot{x} = f(x) + g(x)u, y = h(x)$ has **relative degree** $r$ with respect to the output $y = h(x)$ around $x_0$ if:
1. $\forall 0 \le k < r-1$, $L_gL_f^kh(x) = 0$, $\forall x \in $ neighborhood of $x_0$.
2. $L_gL_f^{r-1}h(x) \neq 0$, $\forall x \in $ neighborhood of $x_0$.
Let's look at some examples.

$$
\begin{align}
\dot{x}_1 &= x_2 \\
\dot{x}_2 &= -x_1^3 + u \\
y &= x_1
\end{align}
$$
It's obvious that the relative degree is not 0 because $u$ doesn't show up directly in $y$. We take the first derivative of $y$:
$$ \dot{y} = x_2$$
Still no $u$. Differentiate again:
$$ \ddot{y}= -x_1^3 + u$$
Now $u$ shows up, therefore the relative degree of $y$ is 2. 
Note that the coefficient of $u$ is always a well-defined 1, therefore output $y$ always has relative degree of 2 anywhere in $\mathbb{R}$.

$$
\begin{align}
\dot{x}_1 &= x_2 + x_3^3 \\
\dot{x}_2 &=  x_3 \\
\dot{x}_3 &= u \\
y &= x_1
\end{align}
$$
We differentiate $y$ twice:
$$
\ddot{y} = x_3 + 3x_3 u
$$
Now we realize that $y$ doesn't have a well-defined degree around $x_3 = 0$, and has a relative degree of 2 anywhere else.

Let's try to apply the concept to our familiar linear system:
$$
\begin{align}
\dot{x} &= Ax + Bu \\
y &= Cx
\end{align}
$$
If we differentiate $y$:
$$
\dot{y} = CAx + CBu
$$
Now, if $CB = 0$, we'll have to differentiate again:
$$
\ddot{y} = CA^2x + CAB u
$$
continue doing this, we have relative degree $r$ if 
1. $ CB = CAB = \ldots = CA^{r-2}B = 0$
2. $ CA^{r-1}B \neq 0$

Isn't the quantity $CA^{r-1}B$ familiar? It's a composite of the controllability matrix and observability matrix. In fact, this conclusion leads directly to the concept of [Kalman decomposition](https://en.wikipedia.org/wiki/Kalman_decomposition).

## Zero Dynamics

A fact regarding the relative degree $r$:
> $r$ is always less than or equal to the order of the system $n$, and cannot be greater than $n$. If we keep differentiating without getting $u$ show up in $y$, the relative degree is usually undefined.

Now, for the IO linearized system $y^{(r)} = v$, we can choose the state vector:

$$ 
z = \begin{pmatrix} 
y \\
\dot{y} \\
\vdots \\
y^{(r-1)}
\end{pmatrix} \in \mathbb{R}^r
$$
Thus, we will arrive at:
$$
\dot{z} = \begin{pmatrix}
  0 & 1 & 0 & \cdots & 0 \\
  0 & 0 & 1 & \cdots & 0 \\
  \vdots & \vdots & \vdots & \ddots & \vdots \\
  0 & 0 & 0 & \cdots & 1 \\
  0 & 0 & 0 & \cdots & 0 
\end{pmatrix} z + \begin{pmatrix}
  0 \\
  0 \\
  \vdots \\
  0 \\
 1 
\end{pmatrix} v
$$
If you have read another article of mine: [Mason's Gain Formula and Control Canonical Forms]({{< relref "/post/profession/control_theory/masons-gain-formula" >}}), you'll realize system follows the controllability canonical form, thus $z$ is always controllable, given matrix $A$ is a complete Jordan block. Therefore, we can always define a feedback control mechanism 
$$ v = -Kz$$
such that
$$ \dot{z} = (A - BK)z $$
is always stable, or $$\Re(\lambda(A - BK)) < 0$$
If we convert $v$ back in terms of $x$, we will get
$$ v = -k_1 h(x) - k_2 L_f h(x) - \ldots - k_r L_f^{r-1} h(x) $$
Now that if we have $z(t) \to 0$ as $ t \to \infty$, $y \to 0$, $\dot{y} \to 0$, etc. We can guarantee the output $y$ is stable. But, how about $x$? Is the original system stable? This leads to the discussion of **zero dynamics**.

If we define the set $Z = \{x \in \mathbb{R}^n : h(x) = \dot{h}(x) = \ldots = h^{(r-1)}(x) = 0\}$, then $Z$ is called the **zero dynamics** of the system. It stands for the part of the system where it's not shown explicitly on the output $y$, or it's unobservable. 

Note that the dimension of the zero dynamics set is $n - r$. 

What we did for IO linearization are the following:
1. We construct the surface $Z$ with dimension $n - r$.
2. We make $Z$ attractive, i.e. we let $x$ approach the surface asymptotically.
3. We also make $Z$ invariant, i.e. $x$ never leaves the surface once it's on the surface.

However, whether the dynamics *on* the surface is stable dictates whether the original system $x$ is stable. The dynamic on the surface is also known as the **zero dynamics**.
Let's take an example to illustrate the zero dynamics. Consider the following system:
$$
\begin{align}
\dot{x}_1 &= x_2 \\
\dot{x}_2 &= \alpha x_3 + u \\
\dot{x}_3 &= \beta x_3 - u \\
y &= x_1
\end{align}
$$
It's easy to get relative degree of 2 for output $y$ because 
$$
\ddot{y} = \alpha x_3 + u
$$
Now, suppose when $t \to \infty$, both $y$ and $\dot{y}$ approach zero. What happens to the state $x$? 
If $y = 0, \dot{y} = 0$, then $x_1 = x_2 = 0$, and we have
$$ \dot{x}_3 = (\beta + \alpha) x_3 $$
Therefore, the zero dynamic on $x_3$ is stable if and only if $\beta + \alpha < 0$. 

In fact, in this case $x_3$ is the uncontrollable state of the nonlinear system. Just like linear system theory, if the uncontrollable state is stable, the entire system can be stabilized.

---

We discussed IO linearization in this article. In part 2, we are going to talk about actual feedback linearization.
