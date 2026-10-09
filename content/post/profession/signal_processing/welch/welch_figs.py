"""Companion script for "Periodogram and Welch's Method": Welch averaging and window choice.
Saves welch-random-walk.png and windows.png.
"""
import os
import shutil
import tempfile

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
fs, sigma, N = 1000.0, 1.0, 2 ** 16
S = lambda f: sigma ** 2 / (fs * 2 * np.sin(np.pi * f / fs) ** 2)


def save(fig, name):
    with tempfile.TemporaryDirectory() as tmp:            # write locally, then copy into the synced folder
        p = os.path.join(tmp, name)
        fig.savefig(p, bbox_inches="tight")
        shutil.copyfile(p, os.path.join(HERE, name))


def spread(f, P, fmin):
    k = (f > fmin) & (f < 0.98 * fs / 2)
    db = 10 * np.log10(P[k] / S(f[k]))
    return P[k].mean() / S(f[k]).mean(), np.mean(P[k] / S(f[k])), np.percentile(db, 5), np.percentile(db, 95)


plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
    "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.8,
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
})
INK, MUTED, BLUE, ORANGE, AQUA, YELLOW = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834", "#1baf7a", "#eda100"

if __name__ == "__main__":
    rng = np.random.default_rng(5)
    x = np.cumsum(rng.normal(0, sigma, N))

    # ---------------------------------------------------------------- Welch vs periodogram
    fp, Pp = signal.periodogram(x, fs, window="boxcar", detrend="linear")
    runs = {L: signal.welch(x, fs, window="hann", nperseg=L, noverlap=L // 2, detrend=False) for L in (4096, 1024)}
    _, m, lo, hi = spread(fp, Pp, 0)
    print(f"periodogram N={N}: mean P/S {m:.2f}, 5-95% {lo:+.1f} to {hi:+.1f} dB")
    for L, (f, P) in runs.items():
        _, m, lo, hi = spread(f, P, 4 * fs / L)
        print(f"Welch Hann L={L}, 50% overlap, K={(N - L) // (L // 2) + 1}: mean P/S {m:.2f}, 5-95% {lo:+.1f} to {hi:+.1f} dB, lowest bin {fs / L:.2f} Hz")

    fig, ax = plt.subplots(figsize=(8, 4.6))
    k = fp > 0
    ax.loglog(fp[k], Pp[k], color=MUTED, linewidth=0.4, alpha=0.4, label=f"periodogram, $N = {N}$")
    for (L, (f, P)), c in zip(runs.items(), (BLUE, ORANGE)):
        K = (N - L) // (L // 2) + 1
        ax.loglog(f[3:], P[3:], color=c, linewidth=1.6, label=f"Welch, Hann, $L = {L}$, $K = {K}$ segments")   # bins 1-2 sit in the DC main lobe
    ff = np.logspace(np.log10(fs / N), np.log10(fs / 2), 400)
    ax.loglog(ff, S(ff), color=INK, linewidth=1.4, linestyle="--", label="theory $S(f)$")
    ax.set_title("Welch's method on the same random walk", loc="left", color=INK)
    ax.set(xlabel="frequency (Hz)", ylabel=r"PSD (units$^2$/Hz)", xlim=(fs / N, fs / 2))
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout()
    save(fig, "welch-random-walk.png")

    # ---------------------------------------------------------------- windows
    wins = [("boxcar", "rectangular", MUTED), ("hann", "Hann", BLUE), ("blackmanharris", "Blackman-Harris", ORANGE)]
    L = 1024
    fig, axs = plt.subplots(2, 2, figsize=(12, 7.8))

    ax = axs[0, 0]
    n = np.arange(L)
    for name, lab, c in wins:
        ax.plot(n, signal.get_window(name, L), color=c, linewidth=1.8, label=lab)
    ax.set_title("Window shapes", loc="left", color=INK)
    ax.set(xlabel="sample", ylim=(-0.05, 1.1))
    ax.legend(frameon=False, fontsize=8, loc="lower center")

    ax = axs[0, 1]
    for name, lab, c in wins:
        w = signal.get_window(name, 64)
        W = np.abs(np.fft.fft(w, 64 * 64)); W = np.fft.fftshift(W) / W.max()
        b = np.fft.fftshift(np.fft.fftfreq(64 * 64, 1 / 64))
        ax.plot(b, 20 * np.log10(W + 1e-12), color=c, linewidth=1.3, label=lab)
    ax.set_title("Their spectra: main lobe vs. sidelobes", loc="left", color=INK)
    ax.set(xlabel="frequency offset (bins)", ylabel="dB", xlim=(-12, 12), ylim=(-140, 5))
    ax.legend(frameon=False, fontsize=8, loc="upper right")

    ax = axs[1, 0]
    for name, lab, c in wins[:2]:
        f, P = signal.welch(x, fs, window=name, nperseg=L, noverlap=L // 2, detrend=False)
        _, m, lo, hi = spread(f, P, 4 * fs / L)
        print(f"Welch L={L} {lab}: mean P/S {m:.2f}")
        ax.loglog(f[3:], P[3:], color=c, linewidth=1.6, label=f"Welch, {lab} (mean {m:.2f}× theory)")
    ff = np.logspace(np.log10(3 * fs / L), np.log10(fs / 2), 400)
    ax.loglog(ff, S(ff), color=INK, linewidth=1.4, linestyle="--", label="theory $S(f)$")
    ax.set_title(f"Random walk, Welch with $L = {L}$", loc="left", color=INK)
    ax.set(xlabel="frequency (Hz)", ylabel=r"PSD (units$^2$/Hz)", xlim=(3 * fs / L, fs / 2))
    ax.legend(frameon=False, fontsize=8, loc="lower left")

    # two tones: strong one off-bin, weak one 80 dB down, plus a little white noise
    ax = axs[1, 1]
    t = np.arange(4096) / fs
    y = np.sin(2 * np.pi * 100.3 * t) + 1e-4 * np.sin(2 * np.pi * 120.0 * t) + rng.normal(0, 1e-7, t.size)
    for name, lab, c in wins:
        f, P = signal.periodogram(y, fs, window=name, scaling="spectrum")
        ax.plot(f, 10 * np.log10(P / P.max()), color=c, linewidth=1.1, label=lab)
    ax.annotate("weak tone, -80 dB", (120.0, -80), xytext=(124, -55), color=INK, fontsize=9,
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.8))
    ax.set_title("Two tones: 100.3 Hz and a -80 dB tone at 120 Hz", loc="left", color=INK)
    ax.set(xlabel="frequency (Hz)", ylabel="dB (relative to peak)", xlim=(80, 140), ylim=(-160, 5))
    ax.legend(frameon=False, fontsize=8, loc="upper right")

    fig.tight_layout(h_pad=2, w_pad=3)
    save(fig, "windows.png")
