"""Companion script for "Numerical Methods: Periodic Steady State Simulation".

Integrates the Lorenz system (sigma = 10, rho = 28, beta = 8/3) with the RK4 step from the
previous post, from two initial conditions 1e-8 apart, and saves lorenz-attractor.png:
    left   the attractor in 3D
    middle x(t) of both trajectories
    right  their separation on a log scale, with the fitted exponential growth rate
"""
import numpy as np
import matplotlib.pyplot as plt

SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0


def lorenz(x, t):
    return np.array([SIGMA * (x[1] - x[0]),
                     x[0] * (RHO - x[2]) - x[1],
                     x[0] * x[1] - BETA * x[2]])


def rk4_step(f, x, t, h):
    k1 = f(x, t)
    k2 = f(x + h / 2 * k1, t + h / 2)
    k3 = f(x + h / 2 * k2, t + h / 2)
    k4 = f(x + h * k3, t + h)
    return x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate(step, f, x0, t0, t_end, h):
    n_steps = int(round((t_end - t0) / h))
    t = t0 + h * np.arange(n_steps + 1)
    x = np.zeros((n_steps + 1,) + np.shape(x0))
    x[0] = x0
    for k in range(n_steps):
        x[k + 1] = step(f, x[k], t[k], h)
    return t, x


if __name__ == "__main__":
    h, t_end, delta0 = 0.005, 40.0, 1e-8
    t, xa = integrate(rk4_step, lorenz, np.array([1.0, 1.0, 1.0]), 0.0, t_end, h)
    _, xb = integrate(rk4_step, lorenz, np.array([1.0 + delta0, 1.0, 1.0]), 0.0, t_end, h)
    sep = np.linalg.norm(xa - xb, axis=1)

    # exponential growth rate of the separation, fitted over the growth phase only
    # (before t ~ 13 the trajectory is still settling onto the attractor)
    fit = (t > 13) & (t < 30)
    lam, c = np.polyfit(t[fit], np.log(sep[fit]), 1)
    print(f"fitted growth rate on 13 < t < 30: {lam:.3f}")
    print(f"separation exceeds 1 at t = {t[np.argmax(sep > 1.0)]:.1f}")

    # largest Lyapunov exponent (Benettin): follow a nearby trajectory, renormalize every step
    x, y, d0, acc = xa[-1].copy(), xa[-1] + np.array([1e-9, 0, 0]), 1e-9, 0.0
    n = 200_000                                   # 1000 time units
    for _ in range(n):
        x, y = rk4_step(lorenz, x, 0, h), rk4_step(lorenz, y, 0, h)
        d = np.linalg.norm(y - x); acc += np.log(d / d0); y = x + (y - x) * d0 / d
    print(f"largest Lyapunov exponent over {n*h:.0f} time units: {acc / (n * h):.3f}")

    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
        "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.8,
        "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    })
    INK, BLUE, ORANGE = "#0b0b0b", "#2a78d6", "#eb6834"

    fig = plt.figure(figsize=(15, 4.6))
    ax = fig.add_subplot(1, 3, 1, projection="3d")
    ax.plot(xa[:, 0], xa[:, 1], xa[:, 2], color=BLUE, linewidth=0.5)
    ax.scatter(*xa[0], color=INK, s=12)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.set_title(r"Lorenz attractor ($\sigma=10,\ \rho=28,\ \beta=8/3$)", loc="left", color=INK)
    ax.view_init(elev=20, azim=-60)
    ax.set_facecolor("#fcfcfb")

    ax = fig.add_subplot(1, 3, 2)
    ax.plot(t, xa[:, 0], color=BLUE, linewidth=1.2, label=r"$x_0 = (1, 1, 1)$")
    ax.plot(t, xb[:, 0], color=ORANGE, linewidth=1.2, linestyle="--", label=r"$x_0 = (1 + 10^{-8}, 1, 1)$")
    ax.set_title(r"$x(t)$ from two initial states $10^{-8}$ apart", loc="left", color=INK)
    ax.set(xlabel="t", ylabel="x", xlim=(0, t_end))
    ax.legend(frameon=False, fontsize=8, loc="lower left")

    ax = fig.add_subplot(1, 3, 3)
    ax.semilogy(t, sep, color=INK, linewidth=1.0, label="separation")
    ax.semilogy(t[fit], np.exp(c + lam * t[fit]), color=ORANGE, linewidth=2, linestyle="--",
                label=rf"fit $\propto e^{{{lam:.2f}\,t}}$")
    ax.set_title(r"Separation $\|\mathbf{x}_a(t) - \mathbf{x}_b(t)\|$", loc="left", color=INK)
    ax.set(xlabel="t", xlim=(0, t_end))
    ax.legend(frameon=False, fontsize=8, loc="lower right")

    fig.tight_layout(w_pad=3)
    fig.savefig("lorenz-attractor.png", bbox_inches="tight")
