"""Companion script for "Periodogram and Welch's Method".

Random walk x[n] = x[n-1] + w[n], w ~ N(0, sigma^2), sampled at fs. Computes the periodogram of one
realization (rectangular window, no detrending) and compares it with the theoretical PSD
    S(f) = sigma^2 / (fs * 2 sin^2(pi f / fs))     (one-sided)
Saves periodogram-random-walk.png.
"""
import os
import shutil
import tempfile

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))

fs, sigma = 1000.0, 1.0                    # 1 kHz sampling, unit step noise
rng = np.random.default_rng(3)


def random_walk(N):
    return np.cumsum(rng.normal(0, sigma, N))


def periodogram(x):
    """One-sided periodogram: P[k] = 2 |X[k]|^2 / (N fs), DC and Nyquist not doubled."""
    N = len(x)
    X = np.fft.rfft(x)
    P = np.abs(X) ** 2 / (N * fs)
    P[1:-1] *= 2 if N % 2 == 0 else 1
    if N % 2:                              # odd N: no Nyquist bin
        P[1:] *= 2
    return np.fft.rfftfreq(N, 1 / fs), P


def S_theory(f):
    return sigma ** 2 / (fs * 2 * np.sin(np.pi * f / fs) ** 2)


def remove_endpoint_line(x):
    """Subtract the straight line joining the first and last samples (kills the wrap-around jump)."""
    n = np.arange(len(x))
    return x - x[0] - (x[-1] - x[0]) * n / (len(x) - 1)


if __name__ == "__main__":
    # bias check over many realizations
    N, M = 2 ** 12, 400
    raw, fixed = [], []
    for _ in range(M):
        x = random_walk(N)
        f, P = periodogram(x)
        k = (f > 0) & (f < fs / 2)
        raw.append(P[k] / S_theory(f[k]))
        fixed.append(periodogram(remove_endpoint_line(x))[1][k] / S_theory(f[k]))
    raw, fixed = np.array(raw), np.array(fixed)
    print(f"mean P/S over {M} realizations: raw {raw.mean():.2f}, end-point line removed {fixed.mean():.2f}")
    print(f"single-realization scatter std/mean: raw {np.mean(raw.std(0) / raw.mean(0)):.2f}, fixed {np.mean(fixed.std(0) / fixed.mean(0)):.2f}")

    results = {}
    for N in (2 ** 12, 2 ** 16):
        x = random_walk(N)
        f, P = periodogram(x)
        f_s, P_s = signal.periodogram(x, fs=fs, window="boxcar", detrend=False, scaling="density")
        assert np.allclose(P, P_s), "hand-rolled periodogram should match scipy"
        _, Pf = periodogram(remove_endpoint_line(x))
        k = (f > 0) & (f < fs / 2)
        db = 10 * np.log10(Pf[k] / S_theory(f[k]))
        print(f"N = {N:6d}: bin spacing {fs / N:.3f} Hz, end-fixed 10log10(P/S) 5-95%: {np.percentile(db, 5):.1f} to {np.percentile(db, 95):.1f} dB")
        results[N] = (x, f, P, Pf)

    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
        "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.8,
        "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    })
    INK, MUTED, BLUE, ORANGE = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834"

    fig, axs = plt.subplots(1, 3, figsize=(16, 4.4))
    x, f, P, Pf = results[2 ** 12]
    t = np.arange(len(x)) / fs
    ax = axs[0]
    ax.plot(t, x, color=BLUE, linewidth=1.0, label="random walk")
    ax.plot([t[0], t[-1]], [x[0], x[-1]], color=ORANGE, linewidth=1.6, linestyle="--", label="line joining the end points")
    ax.set_title(r"Random walk $x[n] = x[n-1] + w[n]$, $N = 4096$", loc="left", color=INK)
    ax.set(xlabel="time (s)", ylabel="x")
    ax.legend(frameon=False, fontsize=8, loc="best")

    ff = np.logspace(np.log10(fs / 2 ** 16), np.log10(fs / 2), 400)
    k = f > 0
    ax = axs[1]
    ax.loglog(f[k], P[k], color=BLUE, linewidth=0.7, label="raw periodogram, $N = 4096$")
    ax.loglog(ff, S_theory(ff), color=INK, linewidth=1.6, linestyle="--", label="theory $S(f)$")
    ax.loglog(ff, 2 * S_theory(ff), color=MUTED, linewidth=1.0, linestyle=":", label="$2 S(f)$")
    ax.set_title("Raw periodogram: biased by the end-point jump", loc="left", color=INK)
    ax.set(xlabel="frequency (Hz)", ylabel=r"PSD (units$^2$/Hz)", xlim=(fs / 2 ** 12, fs / 2))
    ax.legend(frameon=False, fontsize=8, loc="lower left")

    ax = axs[2]
    x2, f2, P2, Pf2 = results[2 ** 16]
    k2 = f2 > 0
    ax.loglog(f2[k2], Pf2[k2], color=ORANGE, linewidth=0.4, alpha=0.6, label="end points fixed, $N = 65536$")
    ax.loglog(f[k], Pf[k], color=BLUE, linewidth=0.7, label="end points fixed, $N = 4096$")
    ax.loglog(ff, S_theory(ff), color=INK, linewidth=1.6, linestyle="--", label="theory $S(f)$")
    ax.set_title("Unbiased, but a longer record is no less noisy", loc="left", color=INK)
    ax.set(xlabel="frequency (Hz)", xlim=(fs / 2 ** 16, fs / 2))
    ax.legend(frameon=False, fontsize=8, loc="lower left")

    fig.tight_layout(w_pad=2.5)
    out = os.path.join(HERE, "periodogram-random-walk.png")
    with tempfile.TemporaryDirectory() as tmp:            # write locally, then copy into the synced folder
        tmp_png = os.path.join(tmp, "fig.png")
        fig.savefig(tmp_png, bbox_inches="tight")
        shutil.copyfile(tmp_png, out)
