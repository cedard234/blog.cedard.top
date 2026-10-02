"""Companion script for "Numerical Methods: Periodic Steady State Simulation".

Solves the BVP  x'' + x = 0,  x(0) = 1,  x(pi/2) = 2  (exact: x = cos t + 2 sin t)
with the shooting method and with harmonic balance, and saves shooting.png and harmonic-balance.png.
The time integrator (RK4) is imported from the previous post's script.
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ivp"))
from ivp_methods import integrate, rk4_step  # noqa: E402

T, X0, XT = np.pi / 2, 1.0, 2.0                   # x(0) = 1, x(T) = 2
f = lambda y, t: np.array([y[1], -y[0]])          # y = [x, x']
x_exact = lambda t: np.cos(t) + 2 * np.sin(t)


# ---------------------------------------------------------------- shooting (as in index.md)
def F(s, h=T / 200):
    """Integrate with x(0) = 1, x'(0) = s; return the miss at the far boundary."""
    t, y = integrate(rk4_step, f, np.array([X0, s]), 0.0, T, h)
    return y[-1, 0] - XT


def shoot(s0=0.0, s1=1.0, tol=1e-10):
    F0, F1 = F(s0), F(s1)
    history = [(s0, F0), (s1, F1)]
    while abs(F1) > tol:
        s0, F0, s1 = s1, F1, s1 - F1 * (s1 - s0) / (F1 - F0)   # secant step
        F1 = F(s1)
        history.append((s1, F1))
    return s1, history


# ---------------------------------------------------------------- harmonic balance (as in index.md)
N = 3                                              # number of harmonics


def unpack(p):                                     # p = [w, a0..aN, b1..bN]
    return p[0], p[1:N + 2], np.r_[0.0, p[N + 2:]]


def x_hb(t, a, b, w):
    k = np.arange(N + 1)[:, None]
    return (a[:, None] * np.cos(k * w * t) + b[:, None] * np.sin(k * w * t)).sum(0)


def residual(p):
    w, a, b = unpack(p)
    k = np.arange(N + 1)
    hb = np.r_[(1 - (k * w) ** 2) * a, ((1 - (k * w) ** 2) * b)[1:]]   # each harmonic of x'' + x
    bc = [x_hb(np.array([0.0]), a, b, w)[0] - X0,                      # boundary conditions
          x_hb(np.array([T]), a, b, w)[0] - XT]
    return np.r_[hb, bc]


def gauss_newton(r, p, tol=1e-14, max_iter=100):
    """Least-squares Newton: p <- p - lstsq(J, r(p)), finite-difference Jacobian."""
    for it in range(max_iter):
        rp = r(p)
        J = np.empty((rp.size, p.size))
        for j in range(p.size):
            dp = np.zeros_like(p); dp[j] = 1e-7
            J[:, j] = (r(p + dp) - rp) / dp[j]
        step = np.linalg.lstsq(J, rp, rcond=None)[0]
        p = p - step
        if np.max(np.abs(step)) < tol:
            break
    return p, it + 1


if __name__ == "__main__":
    s, hist = shoot()
    for i, (si, Fi) in enumerate(hist):
        print(f"shooting guess {i}: s = {si:.12f}, F = {Fi:+.3e}")
    print(f"shooting: x'(0) = {s:.12f} (exact 2), secant steps = {len(hist) - 2}")

    p0 = np.r_[0.9, 0.5 * np.ones(N + 1), 0.5 * np.ones(N)]
    p, iters = gauss_newton(residual, p0)
    w, a, b = unpack(p)
    tt = np.linspace(0, T, 1001)
    print(f"HB: {iters} iterations, w = {w:.12f}")
    print("HB: a =", np.array2string(a, precision=6, suppress_small=True))
    print("HB: b =", np.array2string(b, precision=6, suppress_small=True))
    print(f"HB: max |x_HB - x_exact| = {np.max(np.abs(x_hb(tt, a, b, w) - x_exact(tt))):.1e}")

    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
        "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.8,
        "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    })
    INK, MUTED, BLUE, ORANGE, AQUA = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834", "#1baf7a"

    fig, ax = plt.subplots(figsize=(7, 4.2))
    for (si, Fi), c, ls in zip(hist[:3], [BLUE, ORANGE, AQUA], ["-", "-", "-"]):
        t, y = integrate(rk4_step, f, np.array([X0, si]), 0.0, T, T / 200)
        ax.plot(t, y[:, 0], color=c, linewidth=2, linestyle=ls, label=rf"$s = {si:g}$:  $x(\pi/2) = {y[-1, 0]:.3f}$")
    ax.plot(tt, x_exact(tt), color=INK, linewidth=1.2, linestyle="--", label=r"exact $\cos t + 2\sin t$")
    ax.plot([0, T], [X0, XT], "o", color=INK, markersize=7, zorder=5)
    ax.annotate("target $x(\\pi/2) = 2$", (T, XT), xytext=(-120, -30), textcoords="offset points", color=INK)
    ax.set_xticks([0, np.pi / 4, np.pi / 2]); ax.set_xticklabels(["0", r"$\pi/4$", r"$\pi/2$"])
    ax.set_title(r"Shooting: guess $s = \dot{x}(0)$, integrate, correct", loc="left", color=INK)
    ax.set(xlabel="t", ylabel="x(t)", ylim=(-0.2, 2.6))
    ax.legend(frameon=False, fontsize=8, loc="lower left")

    fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shooting.png"), bbox_inches="tight")

    fig, (ax_w, ax) = plt.subplots(1, 2, figsize=(12, 4.2))
    # waveform rebuilt from the HB coefficients vs. the exact solution
    ax_w.plot(tt, x_exact(tt), color=INK, linewidth=1.2, linestyle="--", label=r"exact $\cos t + 2\sin t$", zorder=5)
    ax_w.plot(tt, x_hb(tt, a, b, w), color=AQUA, linewidth=3, alpha=0.7, label=f"HB, N = {N}")
    p_init = np.r_[0.9, 0.5 * np.ones(N + 1), 0.5 * np.ones(N)]
    w_i, a_i, b_i = unpack(p_init)
    ax_w.plot(tt, x_hb(tt, a_i, b_i, w_i), color=MUTED, linewidth=1.2, linestyle=":", label="HB initial guess")
    ax_w.plot([0, T], [X0, XT], "o", color=INK, markersize=7, zorder=6)
    ax_w.set_xticks([0, np.pi / 4, np.pi / 2]); ax_w.set_xticklabels(["0", r"$\pi/4$", r"$\pi/2$"])
    ax_w.set_title("Harmonic balance: waveform from the solved coefficients", loc="left", color=INK)
    ax_w.set(xlabel="t", ylabel="x(t)", ylim=(-0.2, 2.6))
    ax_w.legend(frameon=False, fontsize=8, loc="lower left")
    k = np.arange(N + 1)
    ax.bar(k - 0.18, a, width=0.34, color=BLUE, label=r"$a_k$ (cos)")
    ax.bar(k + 0.18, b, width=0.34, color=ORANGE, label=r"$b_k$ (sin)")
    for kk in k:
        for off, v in [(-0.18, a[kk]), (0.18, b[kk])]:
            if abs(v) > 1e-9:
                ax.annotate(f"{v:.3f}", (kk + off, v), xytext=(0, 3), textcoords="offset points", ha="center", color=INK, fontsize=9)
    ax.set_xticks(k); ax.set_xticklabels([f"{kk}" for kk in k])
    ax.set_title(rf"Fourier coefficients: solved $\omega = {w:.3f}$", loc="left", color=INK)
    ax.set(xlabel=r"harmonic $k$ (frequency $k\omega$)", ylabel="coefficient", ylim=(0, 2.4))
    ax.legend(frameon=False, fontsize=8, loc="upper right")

    fig.tight_layout(w_pad=3)
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "harmonic-balance.png"), bbox_inches="tight")
