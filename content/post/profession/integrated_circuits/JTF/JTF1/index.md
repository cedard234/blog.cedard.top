---
title: "Jitter Generation, Transfer, and Tolerance, Part 1"
date: 2026-10-10T16:50:01-07:00
image: 
description: Part 1 - Jitter Generation and Fundamentals
categories:
    - Integrated Circuits
tags:
    - Clocking
    - Jitter
    - Mathematics
    - Stochastic Process
    - Signal Processing
    - Integrated Circuits
math: true
---

## Motivation

Back in the era when Galileo was still alive, he was fascinated by the motion of pendulums. People often say he observed the swinging of a chandelier in the Pisa Cathedral, which led to his groundbreaking studies on the periodicity of pendulums. However, that was pretty much a time when there was no precise measurement of time; how did he know the period of the pendulum accurately? We know later that he used his own pulse as a makeshift timer, which was surprisingly effective for his time -- and also surprisingly inaccurate. If his pulse rate varied, the measured period would be correspondingly inaccurate, and leading to significant errors in his observations. You can read more about his experiments with pendulums in this [website](https://galileo.library.rice.edu/lib/student_work/experiment95/galileo_pendulum.html).

Nonetheless, the period of a pendulum that he established, assuming a small-angle approximation, is remarkably accurate and forms the foundation for understanding the dynamics of pendulums:

$$ T = 2\pi \sqrt{\frac{L}{g}} $$

where \(T\) is the period of the pendulum, \(L\) is the length of the pendulum, and \(g\) is the acceleration due to gravity. This formula assumes that the amplitude of the pendulum's swing is small, so that the small-angle approximation holds.

We know later that the pendulum-based timekeeping devices, such as the grandfather clock, relied on this principle. The accuracy of these clocks was limited by the precision of the pendulum's period, which in turn depended on the length of the pendulum and the local gravitational acceleration. Let's say we calibrate the clock at a specific time of day, say 12 noon, and we observe the time the second day. Depending on the **quality factor** (Q factor) of the pendulum, the clock may drift slightly, leading to a discrepancy between the observed time and the actual time. 

The Q factor of a pendulum is given by:

$$ Q = \frac{2\pi \times \text{Energy Stored}}{\text{Energy Lost per Cycle}} $$

where "Energy Stored" refers to the maximum potential energy of the pendulum, and "Energy Lost per Cycle" accounts for the energy dissipated due to air resistance and friction at the pivot point. A higher Q factor indicates a pendulum that loses less energy per cycle, resulting in more accurate timekeeping.

We know later that people managed to inventories of more precise timekeeping devices, such as the quartz crystal oscillator, which significantly improved the accuracy of clocks and watches. The quartz crystal oscillator operates based on the piezoelectric effect, where a quartz crystal vibrates at a very stable frequency when an electric voltage is applied. This frequency can be used to drive a clock mechanism with much higher precision than pendulum-based clocks. However, quartz crystal oscillators are still subject to environmental factors such as temperature changes, which can slightly alter their frequency and, consequently, the accuracy of the timekeeping. The inaccuracy of different kinds of clocks is generalized as the concept of **jitter**, and we will study how jitter is generated, transfered and tolerated in a modern serial link application through this series of blogs.

## Definitions of Different Jitters

This part reflects what Dr. Nicola Da Dalt had in his ISSCC [tutorial](nicola.pdf) and Prof. Ali Sheikhoslami had in his ESSERC [tutorial](ali.pdf). They co-authored a book, [Understanding Jitter and Phase Noise: A Circuits and Systems Perspective](https://www.mathworks.com/academia/books/understanding-jitter-and-phase-noise-da-dalt.html). We are just giving some convenient definitions from this book.

### Absolute Jitter

Suppose we have a periodic signal:
$$ v(t) = A \sin(2\pi f t + \phi(t)) $$
