---
title: "相位噪声与抖动的关系"
description: "Relationship between Phase Noise and Jitter: Theoretical Analysis and Engineering Applications"
slug: phase-noise-jitter
date: 2025-07-07 20:42:16+0800
categories:
    - profession
tags:
    - PLL
    - Phase Noise
    - Jitter
    - Mathematics
    - Signal Processing
math: true
---

在现代数字通信系统和时钟生成电路中，相位噪声和抖动是两个关键的性能指标。本文将从理论基础出发，深入分析相位噪声与抖动之间的数学关系，并探讨其在工程实践中的应用意义。

## 1. 理论基础

### 随机过程与平稳性

在分析相位噪声与抖动的关系之前，需要建立必要的随机过程理论基础。

#### 平稳过程的定义

**平稳过程（Stationary Process）** 是指其统计特性不随时间变化的随机过程。对于平稳过程，其均值和方差在时间上保持恒定。

**宽平稳过程（Wide-Sense Stationary Process）** 是平稳过程的一个重要特例，其定义为：
- 均值恒定：$E[X(t)] = \mu_X$（常数）
- 自相关函数仅依赖于时间差：$R_X(t_1, t_2) = R_X(t_2 - t_1)$

白噪声是宽平稳过程的典型例子。

#### 自相关函数

**自相关函数（Autocorrelation Function）** 描述了随机过程在不同时间点之间的相关性：

$$R_x(\tau) = E[X(t)X(t+\tau)]$$

对于白噪声，自相关函数具有以下特性：
$$R_{\text{white}}(\tau) = \sigma^2 \delta(\tau)$$

其中$\sigma^2$为噪声功率，$\delta(\tau)$为狄拉克函数。

### 频域分析理论

#### 功率谱密度

**功率谱密度（Power Spectral Density, PSD）** 描述了随机过程在频域中的功率分布：

$$S_x(f) = \lim_{T \to \infty} \frac{1}{T} E[|X_T(f)|^2]$$

#### 维纳-辛钦定理

**维纳-辛钦定理（Wiener-Khinchin Theorem）** 建立了时域自相关函数与频域功率谱密度之间的重要关系：

$$S_x(f) = \int_{-\infty}^{\infty} R_x(\tau) e^{-j2\pi f\tau} d\tau$$

$$R_x(\tau) = \int_{-\infty}^{\infty} S_x(f) e^{j2\pi f\tau} df$$

这表明功率谱密度是自相关函数的傅里叶变换。

#### 帕萨瓦尔定理

**帕萨瓦尔定理（Parseval's Theorem）** 给出了时域和频域能量的等价关系：

$$\int_{-\infty}^{\infty} |x(t)|^2 dt = \int_{-\infty}^{\infty} S_x(f) df$$

对于周期信号，有：
$$\int_{-\infty}^{\infty} S_x(f) df = T \int_{-\frac{1}{2T}}^{\frac{1}{2T}} |x(t)|^2 dt$$

其中$T$为信号周期。

### 时间与相位关系

相位与时间的基本关系由下式给出：
$$\Delta \phi = \omega \Delta t$$

其中：
- $\Delta \phi$：相位变化
- $\omega$：角频率
- $\Delta t$：时间间隔

## 2. 抖动标准差与相位噪声的数学关系

### 绝对抖动的定义

对于矩形波信号，**绝对抖动（Absolute Jitter）** 定义为信号边沿相对于理想时刻的偏移。

考虑第$k$个周期，如果相位噪声的时域表示为$\phi_n(t_k)$，则实际的相位满足：

$$\omega_0 t_k + \phi_n(t_k) = 2\pi k$$

因此，绝对抖动可以表示为：

$$
\begin{aligned}
a_k &= t_k - \frac{2\pi k}{\omega_0} \\
&= \frac{\phi_n(t_k)}{\omega_0}
\end{aligned}
$$

### 小信号近似分析

基于以下工程假设：
1. 绝对抖动是小量
2. 相位噪声在$kT_0$附近缓慢变化

对相位噪声进行一阶泰勒展开：

$$
\begin{aligned}
\phi_n(t_k) &\approx \phi_n(kT_0 + a_k) \\
&= \phi_n(kT_0) + \frac{d\phi_n(t)}{dt}\bigg|_{t=kT_0} a_k
\end{aligned}
$$

将此式代入绝对抖动的表达式：

$$
a_k = \frac{\phi_n(kT_0)}{\omega_0 - \frac{d\phi_n(t)}{dt}\bigg|_{t=kT_0}}
$$

在小信号近似下，$\frac{d\phi_n(t)}{dt} \ll \omega_0$，因此：

$$a_k \approx \frac{\phi_n(kT_0)}{\omega_0}$$

### 统计特性分析

#### 自相关函数关系

将相位噪声视为宽平稳过程，其自相关函数为：
$$R_{\phi}(\tau) = E[\phi_n(t)\phi_n(t+\tau)]$$

相应地，抖动的自相关函数为：
$$R_{a}(m) = E[a_k a_{k+m}]$$

由于抖动是相位噪声的比例采样结果，可得：

$$R_{a}(m) = \frac{1}{\omega_0^2} R_{\phi}(mT_0)$$

#### 功率谱密度关系

应用维纳-辛钦定理，抖动的功率谱密度与相位噪声功率谱密度之间存在以下关系：

$$S_a(f) = \frac{1}{\omega_0^2} S_{\phi}(f)$$

### 抖动方差的计算

假设抖动为零均值过程，其方差（即均方根抖动）可通过以下方式计算：

$$
\begin{aligned}
\sigma_a^2 &= R_a(0) \\
&= \frac{1}{\omega_0^2} R_{\phi}(0) \\
&= \frac{1}{\omega_0^2} \int_{-\infty}^{\infty} S_{\phi}(f) df
\end{aligned}
$$

这是相位噪声与抖动关系的核心结论：

> **随机抖动的方差等于相位噪声功率谱密度的积分除以角频率的平方。**
