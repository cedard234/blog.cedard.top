"""Companion script for "Numerical Methods, part 1: Transient Simulation".

Implements Forward Euler, Backward Euler, Trapezoidal, Heun and RK4 (the same code as the
snippets in index.md), runs them on two circuits with closed-form solutions, and saves:
    lc-tank-methods.png      LC tank: waveform and stored energy, all methods, h = T/16
    rc-stiff-convergence.png RC step with h = 2.5*tau, and global error vs step size (LC tank)
"""
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------- methods (as in index.md)
def integrate(step, f, x0, t0, t_end, h):
    """March x_{k+1} = step(f, x_k, t_k, h) from t0 to t_end."""
    n_steps = int(round((t_end - t0) / h))
    t = t0 + h * np.arange(n_steps + 1)
    x = np.zeros((n_steps + 1,) + np.shape(x0))
    x[0] = x0
    for k in range(n_steps):
        x[k + 1] = step(f, x[k], t[k], h)
    return t, x


def forward_euler_step(f, x, t, h):
    return x + h * f(x, t)


def newton(g, x, tol=1e-12, max_iter=50):
    """Solve g(x) = 0 with Newton-Raphson and a finite-difference Jacobian."""
    x = np.atleast_1d(np.asarray(x, dtype=float)).copy()
    for _ in range(max_iter):
        gx = np.atleast_1d(g(x))
        J = np.empty((x.size, x.size))
        for j in range(x.size):
            dx = np.zeros_like(x)
            dx[j] = 1e-8 * max(1.0, abs(x[j]))
            J[:, j] = (np.atleast_1d(g(x + dx)) - gx) / dx[j]
        delta = np.linalg.solve(J, -gx)
        x += delta
        if np.max(np.abs(delta)) < tol * max(1.0, np.max(np.abs(x))):
            break
    return x


def backward_euler_step(f, x, t, h):
    g = lambda y: y - x - h * f(y, t + h)        # x_{k+1} appears on both sides
    return newton(g, x).reshape(np.shape(x))


def trapezoidal_step(f, x, t, h):
    fk = f(x, t)
    g = lambda y: y - x - h / 2 * (fk + f(y, t + h))
    return newton(g, x).reshape(np.shape(x))


def heun_step(f, x, t, h):
    k1 = f(x, t)
    x_pred = x + h * k1                           # predictor: one Forward Euler step
    k2 = f(x_pred, t + h)
    return x + h / 2 * (k1 + k2)                  # corrector: average the two slopes


def rk4_step(f, x, t, h):
    k1 = f(x, t)
    k2 = f(x + h / 2 * k1, t + h / 2)
    k3 = f(x + h / 2 * k2, t + h / 2)
    k4 = f(x + h * k3, t + h)
    return x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


METHODS = {
    "Forward Euler": forward_euler_step,
    "Backward Euler": backward_euler_step,
    "Trapezoidal": trapezoidal_step,
    "Heun": heun_step,
    "RK4": rk4_step,
}

# ---------------------------------------------------------------- example circuits
# LC tank: C dv/dt = -i, L di/dt = v, v(0) = 1 V, i(0) = 0  ->  v = cos(w0 t)
L_, C_ = 1e-9, 1e-12                              # 1 nH, 1 pF
w0 = 1 / np.sqrt(L_ * C_)
T0 = 2 * np.pi / w0
f_lc = lambda x, t: np.array([-x[1] / C_, x[0] / L_])
energy = lambda x: 0.5 * C_ * x[..., 0] ** 2 + 0.5 * L_ * x[..., 1] ** 2

# RC step: C dv/dt = I - v/R, v(0) = 0  ->  v = IR (1 - exp(-t/tau))
R, C, I = 10e3, 1e-12, 100e-6
tau = R * C
f_rc = lambda v, t: (I - v / R) / C
v_rc = lambda t: I * R * (1 - np.exp(-t / tau))

if __name__ == "__main__":
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
        "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.8,
        "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    })
    INK, MUTED = "#0b0b0b", "#52514e"
    COLORS = {"Forward Euler": "#2a78d6", "Backward Euler": "#eb6834", "Trapezoidal": "#1baf7a",
              "Heun": "#eda100", "RK4": "#4a3aa7"}

    # FE snippet from the post
    t, v = integrate(forward_euler_step, f_rc, 0.0, 0.0, 50e-9, 0.1 * tau)
    print(f"[FE snippet] final {v[-1]:.4f} V (exact {v_rc(t[-1]):.4f}), "
          f"max err {np.max(np.abs(v - v_rc(t))) * 1e3:.2f} mV")

    # ---- LC tank, h = T0/16, 5 periods
    h = T0 / 16
    tt = np.linspace(0, 5 * T0, 2000)
    E0 = energy(np.array([1.0, 0.0]))
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    axs[0].plot(tt / T0, np.cos(w0 * tt), color=INK, linewidth=1.2, linestyle="--", label="exact")
    print(f"\n[LC tank] h = T0/16, after 5 periods:")
    for name, step in METHODS.items():
        t, x = integrate(step, f_lc, np.array([1.0, 0.0]), 0.0, 5 * T0, h)
        E = energy(x) / E0
        axs[0].plot(t / T0, x[:, 0], color=COLORS[name], linewidth=1.6, marker="o", markersize=2.5, label=name)
        axs[1].plot(t / T0, E, color=COLORS[name], linewidth=2, label=name)
        print(f"  {name:15s} v(5T) = {x[-1, 0]:+.4f} (exact +1.0000)   energy = {E[-1]:.4f} x E0")
    axs[0].set_title("LC tank voltage, $h = T_0/16$", loc="left", color=INK); axs[0].set(xlabel="time ($T_0$)", ylabel="v (V)", ylim=(-2.6, 2.6))
    axs[1].set_title("Stored energy, normalized to $E_0$", loc="left", color=INK); axs[1].set(xlabel="time ($T_0$)", ylabel="$E / E_0$", yscale="log")
    axs[0].legend(frameon=False, ncol=3, fontsize=8, loc="lower left")
    axs[1].legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(w_pad=3)
    fig.savefig("lc-tank-methods.png", bbox_inches="tight")

    # ---- RC step with a large step size, and convergence order on the LC tank
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2))
    h = 2.5 * tau
    t_end = 250e-9
    tt = np.linspace(0, t_end, 500)
    axs[0].plot(tt * 1e9, v_rc(tt), color=INK, linewidth=1.2, linestyle="--", label="exact")
    print(f"\n[RC step] h = 2.5 tau (exact final {v_rc(t_end):.4f} V):")
    for name, step in METHODS.items():
        t, v = integrate(step, f_rc, 0.0, 0.0, t_end, h)
        axs[0].plot(t * 1e9, v, color=COLORS[name], linewidth=1.6, marker="o", markersize=4, label=name)
        print(f"  {name:15s} {np.array2string(v, precision=3, floatmode='fixed')}")
    axs[0].set_title(r"RC step response, $h = 2.5\,\tau$", loc="left", color=INK); axs[0].set(xlabel="time (ns)", ylabel="v (V)", ylim=(-2.0, 4.0))
    axs[0].legend(frameon=False, ncol=2, fontsize=8, loc="upper left")

    hs = T0 / np.array([32, 64, 128, 256, 512, 1024, 2048])
    print("\n[convergence] LC tank, max_k |v_k - cos(w0 t_k)| over one period, observed order from last two points:")
    for name, step in METHODS.items():
        err = []
        for hh in hs:
            t, x = integrate(step, f_lc, np.array([1.0, 0.0]), 0.0, T0, hh)
            err.append(np.max(np.abs(x[:, 0] - np.cos(w0 * t))))
        err = np.array(err)
        p = np.log(err[-2] / err[-1]) / np.log(hs[-2] / hs[-1])
        axs[1].loglog(hs / T0, err, color=COLORS[name], linewidth=2, marker="o", markersize=4, label=f"{name} (slope {p:.1f})")
        print(f"  {name:15s} order ~ {p:.2f}")
    axs[1].set_title("LC tank: global error over one period vs. step size", loc="left", color=INK); axs[1].set(xlabel="$h / T_0$", ylabel=r"$\max_k |v_k - v_{exact}(t_k)|$")
    axs[1].legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout(w_pad=3)
    fig.savefig("rc-stiff-convergence.png", bbox_inches="tight")
