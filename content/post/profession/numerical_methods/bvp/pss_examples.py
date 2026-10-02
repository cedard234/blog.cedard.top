"""Companion script for "Numerical Methods: Periodic Steady State Simulation".

Periodic steady state (PSS) with shooting and harmonic balance in two scenarios:
  1. driven circuit, unknown initial state: RC (tau = 10 ns) driven by a 1 GHz square-wave current
  2. autonomous circuit, unknown period:   Van der Pol oscillator, mu = 1
Saves pss-driven.png and pss-autonomous.png. Integrator and Newton solver are imported from the previous post.
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ivp"))
from ivp_methods import integrate, rk4_step, newton  # noqa: E402

# ================================================================ 1. driven RC, unknown initial state
R, C, I = 10e3, 1e-12, 100e-6                     # tau = 10 ns, IR = 1 V
tau, T_clk = R * C, 1e-9                          # 1 GHz clock
f_hi = lambda v, t: (I - v / R) / C               # source high
f_lo = lambda v, t: (0.0 - v / R) / C             # source low
H_RC = T_clk / 200

# closed-form periodic solution: exponential segments between v_min and v_max
a = T_clk / (2 * tau)
v_min, v_max = I * R * np.exp(-a) / (1 + np.exp(-a)), I * R / (1 + np.exp(-a))


def v_exact(t):
    t = np.mod(t, T_clk)
    return np.where(t < T_clk / 2, I * R + (v_min - I * R) * np.exp(-t / tau),
                    v_max * np.exp(-(t - T_clk / 2) / tau))


def period_rc(v0):
    """One period from v0. The source edge at T/2 is a breakpoint: integrate each half
    separately, so no RK4 step straddles the discontinuity."""
    t1, v1 = integrate(rk4_step, f_hi, v0, 0.0, T_clk / 2, H_RC)
    t2, v2 = integrate(rk4_step, f_lo, v1[-1], T_clk / 2, T_clk, H_RC)
    return np.r_[t1, t2[1:]], np.r_[v1, v2[1:]]


def psi_rc(v0):                                   # state after one period
    return period_rc(v0)[1][-1]


def shoot_rc(v0=0.0):
    n_calls = [0]
    def F(v):
        n_calls[0] += 1
        return psi_rc(float(v[0])) - v[0]
    v = newton(F, v0)
    return float(v[0]), n_calls[0]


def hb_rc(N, t):
    """Linear circuit: each harmonic is just an AC analysis, V_k = Z(j k w) I_k."""
    w = 2 * np.pi / T_clk
    v = np.full_like(t, I / 2 * R)                # DC: I/2 through R
    for k in range(1, N + 1, 2):                  # square wave: odd harmonics only
        Ik = 2 * I / (k * np.pi)                  # i(t) = I/2 + sum Ik sin(k w t)
        Z = R / (1 + 1j * k * w * tau)
        v += np.abs(Z) * Ik * np.sin(k * w * t + np.angle(Z))
    return v


# ================================================================ 2. Van der Pol, unknown period
MU = 1.0
f_vdp = lambda y, t: np.array([y[1], MU * (1 - y[0] ** 2) * y[1] - y[0]])   # y = [x, x']
N_STEPS = 2000


def shoot_vdp(A0=1.5, T0=2 * np.pi):
    """Unknowns [A, T]; phase condition x'(0) = 0, i.e. start the period at a peak x(0) = A."""
    def F(p):
        A, T = p
        y_end = integrate(rk4_step, f_vdp, np.array([A, 0.0]), 0.0, T, T / N_STEPS)[1][-1]
        return np.array([y_end[0] - A, y_end[1] - 0.0])
    return newton(F, np.array([A0, T0]))


def hb_vdp(N, w0=1.0, a1=2.0):
    """Unknowns [w, a0..aN, b2..bN]; phase condition b1 = 0. Nonlinear term via collocation + FFT."""
    M = 8 * N + 8                                 # time samples per period
    th = 2 * np.pi * np.arange(M) / M
    k = np.arange(N + 1)[:, None]
    cos_kt, sin_kt = np.cos(k * th), np.sin(k * th)

    def unpack(p):
        return p[0], p[1:N + 2], np.r_[0.0, 0.0, p[N + 2:]]      # b0 = 0, b1 = 0 (phase)

    def residual(p):
        w, ak, bk = unpack(p)
        with np.errstate(all="ignore"):           # macOS Accelerate raises spurious FP flags in matmul
            return _residual(w, ak, bk)

    def _residual(w, ak, bk):
        x = ak @ cos_kt + bk @ sin_kt
        xd = w * ((k[:, 0] * bk) @ cos_kt - (k[:, 0] * ak) @ sin_kt)
        xdd = -w ** 2 * ((k[:, 0] ** 2 * ak) @ cos_kt + (k[:, 0] ** 2 * bk) @ sin_kt)
        r = xdd - MU * (1 - x ** 2) * xd + x      # residual in the time domain
        rc, rs = 2 / M * cos_kt @ r, 2 / M * sin_kt @ r            # back to harmonics
        rc[0] /= 2
        return np.r_[rc, rs[1:]]                  # DC, cos 1..N, sin 1..N  (2N+1 equations)

    p0 = np.r_[w0, 0.0, a1, np.zeros(N - 1), np.zeros(N - 1)]
    p = newton(residual, p0)
    w, ak, bk = unpack(p)
    return w, ak, bk


def x_from_hb(t, w, ak, bk):
    k = np.arange(len(ak))[:, None]
    return (ak[:, None] * np.cos(k * w * t) + bk[:, None] * np.sin(k * w * t)).sum(0)


if __name__ == "__main__":
    # ---- 1. driven RC
    v0_pss, calls = shoot_rc()
    print(f"[RC] exact v_min = {v_min:.6f} V, v_max = {v_max:.6f} V, ripple = {(v_max - v_min) * 1e3:.2f} mV")
    print(f"[RC] shooting: v(0) = {v0_pss:.6f} V, error {abs(v0_pss - v_min):.1e}, periods integrated = {calls}")
    # transient for comparison: periods until v(kT) is within 1e-6 V of the periodic value
    v, k_settle = 0.0, 0
    while abs(v - v0_pss) > 1e-6 and k_settle < 5000:
        v = psi_rc(v); k_settle += 1
    print(f"[RC] plain transient from v = 0 needs {k_settle} periods to settle within 1 uV")
    t1 = np.linspace(0, T_clk, 2001)
    for N in (1, 5, 25, 101):
        print(f"[RC] HB N = {N:3d}: max error over one period = {np.max(np.abs(hb_rc(N, t1) - v_exact(t1))) * 1e3:.3f} mV")

    # ---- 2. Van der Pol
    A, T_shoot = shoot_vdp()
    print(f"\n[VdP] shooting: amplitude A = {A:.6f}, period T = {T_shoot:.6f}")
    hb = {}
    for N in (1, 3, 5, 7, 9, 11):
        w, ak, bk = hb_vdp(N)
        hb[N] = (w, ak, bk)
        print(f"[VdP] HB N = {N:2d}: T = {2 * np.pi / w:.6f}  (|T - T_shoot| = {abs(2 * np.pi / w - T_shoot):.1e}),"
              f"  |c1| = {np.hypot(ak[1], bk[1]):.4f}")

    # ---- figures
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
        "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.8,
        "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    })
    INK, MUTED, BLUE, ORANGE, AQUA, YELLOW = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834", "#1baf7a", "#eda100"

    # driven RC: source current on top, capacitor voltage below (whole period + zoom on the corner)
    fig = plt.figure(figsize=(12, 6.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 2.2], width_ratios=[1.6, 1])
    ax_i = fig.add_subplot(gs[0, :])
    t2 = np.linspace(0, 2 * T_clk, 4001)
    ax_i.step(t2 * 1e9, np.where(np.mod(t2, T_clk) < T_clk / 2, I, 0) * 1e6, where="post", color=INK, linewidth=1.8)
    ax_i.set_title("Source: 1 GHz square-wave current into the RC ($\\tau = 10$ ns)", loc="left", color=INK)
    ax_i.set(ylabel="i (µA)", xlim=(0, 2), ylim=(-15, 115))
    t_s, v_s = period_rc(v0_pss)
    t_s2, v_s2 = np.r_[t_s, t_s[1:] + T_clk], np.r_[v_s, v_s[1:]]
    for col, (xl, yl, ttl) in enumerate([((0, 2), None, "Capacitor voltage in steady state"),
                                         ((0.9, 1.1), (486, 492), "Zoom on the corner at the source edge")]):
        ax = fig.add_subplot(gs[1, col])
        ax.plot(t2 * 1e9, v_exact(t2) * 1e3, color=INK, linewidth=1.2, linestyle="--", label="exact PSS", zorder=5)
        ax.plot(t_s2 * 1e9, v_s2 * 1e3, color=BLUE, linewidth=3, alpha=0.6, label="shooting")
        for N, c in [(1, ORANGE), (5, AQUA), (25, YELLOW)]:
            ax.plot(t2 * 1e9, hb_rc(N, t2) * 1e3, color=c, linewidth=1.3, label=f"HB, N = {N}")
        ax.set_title(ttl, loc="left", color=INK)
        ax.set(xlabel="time (ns)", ylabel="v (mV)", xlim=xl)
        if yl: ax.set_ylim(*yl)
        if col == 0: ax.legend(frameon=False, fontsize=8, loc="upper center", ncol=3)
    fig.tight_layout(h_pad=1.5, w_pad=3)
    fig.savefig(os.path.join(HERE, "pss-driven.png"), bbox_inches="tight")

    # Van der Pol: waveform from both methods, and HB period error vs N
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    ax = axs[0]
    tt = np.linspace(0, T_shoot, 1001)
    t_v, y_v = integrate(rk4_step, f_vdp, np.array([A, 0.0]), 0.0, T_shoot, T_shoot / N_STEPS)
    ax.plot(t_v, y_v[:, 0], color=BLUE, linewidth=3, alpha=0.6, label=f"shooting, T = {T_shoot:.3f}")
    for N, c in [(1, ORANGE), (7, AQUA)]:
        w, ak, bk = hb[N]
        # HB's phase condition (b1 = 0) differs from shooting's (x'(0) = 0): align the peaks for plotting
        fine = np.linspace(0, 2 * np.pi / w, 20001)
        t_pk = fine[np.argmax(x_from_hb(fine, w, ak, bk))]
        ax.plot(tt, x_from_hb(tt + t_pk, w, ak, bk), color=c, linewidth=1.3,
                label=f"HB, N = {N}, T = {2 * np.pi / w:.3f}")
    ax.set_title(r"Van der Pol oscillator ($\mu = 1$), one period", loc="left", color=INK)
    ax.set(xlabel="t", ylabel="x(t)")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax = axs[1]
    Ns = sorted(hb)
    ax.semilogy(Ns, [abs(2 * np.pi / hb[N][0] - T_shoot) for N in Ns], color=INK, marker="o", linewidth=2)
    ax.set_title("HB period error vs. number of harmonics", loc="left", color=INK)
    ax.set(xlabel="number of harmonics N", ylabel=r"$|T_{HB} - T_{shooting}|$", xticks=Ns)
    fig.tight_layout(w_pad=3)
    fig.savefig(os.path.join(HERE, "pss-autonomous.png"), bbox_inches="tight")
