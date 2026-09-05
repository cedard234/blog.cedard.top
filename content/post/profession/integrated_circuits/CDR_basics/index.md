---
title: "CDR Basics"
date: 2026-08-26T14:23:10-07:00
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

This is a paraphrase of the tutorial talk by Prof. Pavan Hanumolu from UIUC on Clock and Data Recovery (CDR) basics. The talk was given at the 2015 IEEE International Conference on Solid-State Circuits (ISSCC) in San Francisco, CA. 

I made some annotations to the slides. You can find the combined slides and my annotations below.

<iframe src="SSCSTUT20150091_CDR_architectures_and_circuits.pdf" width="100%" height="600px">
  <p>Your browser does not support PDFs. <a href="/files/document.pdf">Download the PDF</a>.</p>
</iframe>

## From Asynchronous Link to Synchronous Link

I discussed the implementation of the UART protocol in an antient post. UART is an asynchronous protocol, which means that the transmitter and receiver do not share a common clock. However, since the data stream is slow enough, the receiver can sample the data stream at a rate that is close enough to the transmitter's clock. 

However, as we push the data rate higher, the sampling precision required to recover the data stream becomes more stringent. For example, at 1 Gbps, the bit period is 1 ns. If we want to sample the data stream in the middle of the bit period, we need to sample with a precision of 0.5 ns. This is not feasible with an asynchronous protocol like UART. 

From an encoded data stream, it's then interesting how we shall retreieve the clock information from the data stream. This is where Clock and Data Recovery (CDR) comes into play. CDR is a technique used to recover the clock signal from a data stream, allowing for synchronous communication even when the transmitter and receiver do not share a common clock.

CDR is used in multiple protocols, including PCIe and SATA. One advantage to use CDR is that it allows for only data streams to be sent over, thus ensuring the minimum number of wires are used (we are not building simultaneous bi-directional links, unfortunately). The system that utilizes CDR is also sometimes referred to as a "embedded clock" system.

Unlike embdeed clock system, the counterpart is usually referred to as the "forwarded clock" system, which most of the time finds its application in massive parallel links, such as die-to-die interconnects where we can amortize the cost of sending one more clock over many data lanes, which is part of my PhD research. I'll dedicate another post to discuss the forwarded clock system in more detail, but in this post we will focus on the embedded clock system and CDR.

## CDR Metrics

![CDR Metrics](https://images.blog.cedard.top/post/profession/integrated_circuits/CDR_basics/image.png)

Like any other AMS system, we want to build CDR with scalability, low power, low area, high operating range, and immune to supply noise. However, aside from all these conventional PPA (power, performance, area) metrics, there are 3 more metrics that are specific to CDR. They are:
1. **Jitter Tolerance**: The ability of the CDR to tolerate jitter in the incoming data stream. 
2. **Jitter Generation**: The amount of jitter that the CDR adds to the recovered clock.
3. **Jitter Transfer**: The ability of the CDR to transfer jitter from the incoming data stream to the recovered clock.

Among all these, usually jitter tolerance is the main metric that we would like to optimize for. 

### JTOL

Jitter Tolerance (JTOL) measures how much jitter the CDR can tolerate in the incoming data stream before a bit error is sampled. JTOL is usually measured in terms of a "JTOL mask" which looks like:

![JTOL mask](https://images.blog.cedard.top/post/profession/integrated_circuits/CDR_basics/image-1.png)

Usually a closed loop clocking system is able to tracks the low frequency drifting, while fails to track the high frequency jitter. Therefore the JTOL mask is such that a CDR can usually tolerate large jitter when the jitter frequency is low, but can only tolerate small jitter when the jitter frequency is high. In actual measurements, we applies sinusoidal jitter to the incoming data stream and measure if a bit error happened, which defines the JTOL boundary. We would like the actual measured JTOL curve to be above the JTOL mask.

The JTOL mask also defines the jitter tolerance bandwidth, which we will discuss in more details later.

### JTRAN

Jitter transfer (JTRAN) measures how much jitter is transferred from the incoming data stream. This metric is sometimes a little trickier to deal with, as it's not always good to transfer all jitter, or no jitter, to the recovered clock.

We also measure JTRAN in terms of a "JTRAN mask" which looks like:

![JTRAN mask](https://images.blog.cedard.top/post/profession/integrated_circuits/CDR_basics/image-2.png)

This transfer function looks a lot like a low pass filter, or in more precise terms, the reference-to-output transfer function of a closed loop PLL. 

### JGEN

Jitter generation is a simpler metric. Usually the smaller the jitter generation, the better. It measures how much jitter from the CDR itself is added to the recovered clock. 

It's worth to note that JGEN is not always decoupled from the input clock jitter; sometimes JGEN can be a function of the input clock jitter. The reason is that the system bandwidth can sometimes be determined by the input jitter if we have for example a BBPD whose gain is a function of the input jitter.

## CDR Architectures

One can think of CDR as something that generates a clock from the incoming data stream. If the input clock drifts, the CDR also drifts. In that sense a CDR can be thought of just a PLL. Then, why don't we use a traditional PLL to recover the clock?

![Naive way to implement PLL-CDR](https://images.blog.cedard.top/post/profession/integrated_circuits/CDR_basics/image-3.png)

In the illustration, we have two "identical" crystal oscillators, one at the TX and the other at the RX. We use two oscillators to clock the two identical PLLs, hoping to generate two clocks that are the same. However in reality, the two crystal oscillators are not pure identical: any small ppm will lead to a random-walk based phase drift which can be modeled as a Brownian motion. The phase drift will accumulate over time, and the two clocks will eventually drift apart, and cause bit errors in the data stream.

It's worth to note that if the PLL's output clock is **SUFFICIENTLY SLOW**, this scheme can actually work, and we are falling back to the UART case. However, for a higher speed case, we'll have to make sure the generated clock is based off the incoming data, instead of some other asynchronous sources. In other words:

![PLL based CDR](https://images.blog.cedard.top/post/profession/integrated_circuits/CDR_basics/image-4.png)

- The generated clock should compare the clock from itself with the incoming data stream.
- If there is no transition in the data, we don't have any information about the clock, and we should not change the generated clock.
- The resulting clock should be such that the rising edge aligns to the middle of the data eye, and the falling edge aligns to the transition, if the eye is symmtetric.

With all these requirements, one can see that we just need a special phase detector to tell if we are "fast" or "slow". Indeed, the type of phase detector used will define how our CDR system behaves. 

### Linear CDR with Hogge PD

![Hogge PD](https://images.blog.cedard.top/post/profession/integrated_circuits/CDR_basics/image-5.png)

The first candidate is what is known as the "Hogge Phase Detector" published by [Charles Hogge in 1985 on  IEEE Transactions on Electron Devices.](https://ieeexplore.ieee.org/document/1485148) 

The Hogge PD is a linear phase detector, whose operating principle is to substrack the results of $D_E$ and $D_R$. 

Whenever there is a transition in the data, $D_E$ will generate a up-pulse whose width is proportional to the phase difference between the generated clock and the incoming data. Right after $D_E$ falls back, $D_R$ will generate another up-pulse, but whose width will always be half of the generated clock period. Therefore, by comparing with the relative width of the two pulses, we can determine if the generated clock is "fast" or "slow".

It's easy to post-process the output of the Hogge PD by simpling using a charge-pump circuit, just like what we will do for a PFD-based PLL:

![CP](https://images.blog.cedard.top/post/profession/integrated_circuits/CDR_basics/image-6.png)

As can be seen, the resulting voltage at $V_C$ will get high if the data leads the clock edge, and low if the data lags the clock edge. This voltage can then be used to control a VCO, which will generate a clock that is aligned with the incoming data stream.

