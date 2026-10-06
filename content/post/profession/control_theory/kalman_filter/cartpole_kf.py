"""Inverted pendulum on a cart (EE222 HW1 model), stabilized by the same controller fed by three
state estimates:
   1. prediction only    (model propagation, measurements ignored)
   2. measurement only   (raw angle/position, velocities by finite difference)
   3. Kalman filter
State x = [theta, s, theta_dot, s_dot]. The plant is the nonlinear model, integrated with RK4;
LQR and KF use the linearized model. All three runs share the same gust and sensor-noise
realization. Saves cartpole-kf.png.
"""
import os

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm, solve_continuous_are

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- plant (HW1, eq. 1)
M, m, L, g = 25.0, 20.0, 9.81, 9.81
J = m * L ** 2 / 3
dt, T_END = 0.01, 30.0                     # 100 Hz control and measurement
F_MAX = 1000.0                             # actuator limit, N


def f_nl(x, F):
    th, s, thd, sd = x
    c, sn = np.cos(th), np.sin(th)
    Mass = np.array([[m * L ** 2 + J, -m * L * c],
                     [-m * L * c, M + m]])
    rhs = -np.array([-m * g * L * sn, m * L * sn * thd ** 2]) + np.array([0.0, F])
    thdd, sdd = np.linalg.solve(Mass, rhs)
    return np.array([thd, sd, thdd, sdd])


def rk4(x, F, h):
    k1 = f_nl(x, F); k2 = f_nl(x + h / 2 * k1, F); k3 = f_nl(x + h / 2 * k2, F); k4 = f_nl(x + h * k3, F)
    return x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


# linearization at the origin:  (J + mL^2) th'' - mgL th = mL s'',   (M + m) s'' - mL th'' = F
D = (J + m * L ** 2) * (M + m) - (m * L) ** 2
A = np.array([[0, 0, 1, 0],
              [0, 0, 0, 1],
              [(M + m) * m * g * L / D, 0, 0, 0],
              [(m * L) ** 2 * g / D, 0, 0, 0]])
B = np.array([[0], [0], [m * L / D], [(J + m * L ** 2) / D]])
Phi = expm(np.block([[A, B], [np.zeros((1, 5))]]) * dt)       # zero-order hold
Fd, Gd = Phi[:4, :4], Phi[:4, 4:]

# ---------------------------------------------------------------- controller (HW8 problem 4 structure)
# LQR gains with real weight on the cart, so the cart is brought back to s = 0
Q_lqr = np.diag([1e4, 1e2, 1e2, 1e2])
R_lqr = np.array([[0.1]])
P_are = solve_continuous_are(A, B, Q_lqr, R_lqr)
K_lqr = np.linalg.solve(R_lqr, B.T @ P_are)
K1 = K2 = 0.05


def controller(xh):
    """u = (-k_th th - k_thd thd)/cos(th) - k_s s/(1+K1|s|) - k_sd sd/(1+K2|sd|), saturated."""
    k_th, k_s, k_thd, k_sd = K_lqr.ravel()
    th, s, thd, sd = xh
    u = (-k_th * th - k_thd * thd) / np.cos(th) - k_s * s / (1 + K1 * abs(s)) - k_sd * sd / (1 + K2 * abs(sd))
    return float(np.clip(u, -F_MAX, F_MAX))

# ---------------------------------------------------------------- noise
SIGMA_W = 20.0                             # random gust force on the cart, N (held over each step)
SIGMA_TH, SIGMA_S = 0.002, 0.01            # sensors: 2 mrad (~0.11 deg) angle, 1 cm position
H = np.array([[1.0, 0, 0, 0],
              [0, 1.0, 0, 0]])
Q_kf = Gd @ Gd.T * SIGMA_W ** 2            # gust enters through the same path as F
R_kf = np.diag([SIGMA_TH ** 2, SIGMA_S ** 2])

N = int(round(T_END / dt))
rng = np.random.default_rng(1)
W = rng.normal(0, SIGMA_W, N)
V = rng.normal(0, 1, (N + 1, 2)) * [SIGMA_TH, SIGMA_S]


def run(mode):
    x = np.array([0.3, 2.0, 0.0, 0.0])     # true initial state: 0.3 rad (17 deg), cart 2 m from home
    z = H @ x + V[0]
    xh = np.array([z[0], z[1], 0.0, 0.0])  # every estimator starts from the first measurement
    P = np.diag([SIGMA_TH ** 2, SIGMA_S ** 2, 0.1, 0.1])
    z_prev = z
    xs, xhs, us = [x], [xh], []
    for n in range(N):
        u = controller(xh)
        x = rk4(x, u + W[n], dt)            # true plant: control + gust
        z = H @ x + V[n + 1]
        if mode == "prediction":
            xh = Fd @ xh + Gd[:, 0] * u
        elif mode == "measurement":
            xh = np.array([z[0], z[1], (z[0] - z_prev[0]) / dt, (z[1] - z_prev[1]) / dt])
        else:
            xh = Fd @ xh + Gd[:, 0] * u
            P = Fd @ P @ Fd.T + Q_kf
            S = H @ P @ H.T + R_kf
            K = P @ H.T @ np.linalg.inv(S)
            xh = xh + K @ (z - H @ xh)
            I_KH = np.eye(4) - K @ H
            P = I_KH @ P @ I_KH.T + K @ R_kf @ K.T
        z_prev = z
        xs.append(x); xhs.append(xh); us.append(u)
        if abs(x[0]) > np.pi / 2:           # fell over
            break
    return np.array(xs), np.array(xhs), np.array(us)


if __name__ == "__main__":
    print("A =\n", np.round(A, 4)); print("B =", np.round(B.ravel(), 5))
    print("LQR K =", np.array2string(K_lqr, precision=1), " closed-loop poles:", np.round(np.linalg.eigvals(A - B @ K_lqr), 2))
    res = {mode: run(mode) for mode in ("prediction", "measurement", "kalman")}
    for mode, (xs, xhs, us) in res.items():
        fell = abs(xs[-1, 0]) > np.pi / 2
        e = xhs - xs
        msg = f"fell at t = {len(us) * dt:.2f} s" if fell else \
              f"balanced {T_END:.0f} s, final |s| = {abs(xs[-1, 1]):.3f} m, rms theta (last 10 s) = {np.degrees(np.sqrt(np.mean(xs[-1000:, 0] ** 2))):.2f} deg"
        print(f"{mode:12s} {msg}; rms est. error theta = {np.degrees(np.sqrt(np.mean(e[:, 0] ** 2))):.3f} deg, "
              f"theta_dot = {np.degrees(np.sqrt(np.mean(e[:, 2] ** 2))):.2f} deg/s; "
              f"rms F = {np.sqrt(np.mean(us ** 2)):.0f} N, saturated {100 * np.mean(np.abs(us) >= F_MAX - 1e-9):.0f}% of the time")

    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e",
        "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.8,
        "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    })
    INK = "#0b0b0b"
    STYLE = {"prediction": ("#eb6834", "prediction only"),
             "measurement": ("#2a78d6", "measurement only"),
             "kalman": ("#1baf7a", "Kalman filter")}

    fig, axs = plt.subplots(2, 2, figsize=(12, 7.5))
    for mode, (xs, xhs, us) in res.items():
        c, lab = STYLE[mode]
        t = np.arange(len(xs)) * dt
        axs[0, 0].plot(t, np.degrees(xs[:, 0]), color=c, linewidth=1.4, label=lab)
        axs[0, 1].plot(t, xs[:, 1], color=c, linewidth=1.4, label=lab)
        axs[1, 0].plot(t[:-1], us / 1e3, color=c, linewidth=0.6 if mode == "measurement" else 1.6, label=lab,
                       alpha=0.5 if mode == "measurement" else 1.0, zorder=1 if mode == "measurement" else 3)
    axs[0, 0].set_title(r"True pendulum angle $\theta$", loc="left", color=INK)
    axs[0, 0].set(xlabel="time (s)", ylabel="degrees", ylim=(-30, 30))
    axs[0, 1].set_title("True cart position $s$", loc="left", color=INK)
    axs[0, 1].set(xlabel="time (s)", ylabel="m", ylim=(-10, 5))
    axs[1, 0].set_title(r"Control force $F$ (same controller, $\pm$1 kN limit)", loc="left", color=INK)
    axs[1, 0].set(xlabel="time (s)", ylabel="kN", ylim=(-1.15, 1.15))
    for lim in (-F_MAX / 1e3, F_MAX / 1e3):
        axs[1, 0].axhline(lim, color=INK, linewidth=0.8, linestyle=":")
    axs[0, 0].legend(frameon=False, fontsize=9, loc="upper right")

    ax = axs[1, 1]
    xs_k, xhs_k, _ = res["kalman"]
    _, xhs_m, _ = res["measurement"]
    t = np.arange(len(xs_k)) * dt
    tm = np.arange(len(xhs_m)) * dt
    sel, selm = (t >= 6) & (t <= 8), (tm >= 6) & (tm <= 8)
    ax.plot(tm[selm], np.degrees(xhs_m[selm, 2]), color=STYLE["measurement"][0], linewidth=0.6, alpha=0.5, label="finite difference of measurement")
    ax.plot(t[sel], np.degrees(xhs_k[sel, 2]), color=STYLE["kalman"][0], linewidth=2, label="Kalman estimate")
    ax.plot(t[sel], np.degrees(xs_k[sel, 2]), color=INK, linewidth=1.2, linestyle="--", label="true (Kalman run)")
    ax.set_title(r"Angular velocity $\dot{\theta}$ fed to the controller (zoom)", loc="left", color=INK)
    e_m = np.degrees(np.sqrt(np.mean((xhs_m[:, 2] - res["measurement"][0][:, 2]) ** 2)))
    ax.set(xlabel="time (s)", ylabel="deg/s", ylim=(-15, 15))
    ax.text(0.02, 0.04, f"finite difference: {e_m:.0f} deg/s rms error, mostly off scale",
            transform=ax.transAxes, color=STYLE["measurement"][0], fontsize=9)
    ax.legend(frameon=False, fontsize=8, loc="upper right")

    fig.tight_layout(h_pad=2, w_pad=3)
    fig.savefig(os.path.join(HERE, "cartpole-kf.png"), bbox_inches="tight")

    # ---------------------------------------------------------------- animation: all three estimators, one shared clock
    from matplotlib.animation import FuncAnimation, PillowWriter
    from matplotlib.patches import Rectangle, Circle, FancyArrow

    STEP = 7                                   # animate every 7th sample -> ~14 fps, real time
    CART_W, CART_H = 3.0, 1.2
    ARROW_SCALE = 6.0 / F_MAX                  # full-scale force -> 6 m long arrow
    n_total = max(len(xs) for xs, _, _ in res.values())
    frames = list(range(0, n_total, STEP)) + [n_total - 1] * int(1.0 / (STEP * dt))   # hold the end 1 s

    # LQR Lyapunov function V(x) = x^T P x, with P from the Riccati equation, evaluated on the true state
    Vs = {mode: np.einsum("ni,ij,nj->n", xs, P_are, xs) for mode, (xs, _, _) in res.items()}
    v_lo = min(v.min() for v in Vs.values()) * 0.5
    v_hi = max(Vs["kalman"].max(), Vs["measurement"].max()) * 20

    fig = plt.figure(figsize=(11.5, 10.0))
    gs = fig.add_gridspec(3, 2, width_ratios=[1.5, 1])
    axs = [fig.add_subplot(gs[r, 0]) for r in range(3)]
    vaxs = [fig.add_subplot(gs[r, 1]) for r in range(3)]
    clock = fig.suptitle("", x=0.02, ha="left", fontsize=12, family="monospace", color=INK)
    panels = []
    for ax, vax, (mode, (xs, xhs, us)) in zip(axs, vaxs, res.items()):
        c, lab = STYLE[mode]
        ax.set_xlim(-14, 10); ax.set_ylim(-1.0, 12.0); ax.set_aspect("equal")
        ax.set_yticks([]); ax.set_xlabel("cart position s (m)", fontsize=9)
        ax.axhline(0, color="#52514e", linewidth=1.5)
        ax.axvline(0, color="#52514e", linewidth=0.8, linestyle=":")
        ax.set_title(lab, loc="left", color=c, fontweight="bold")
        cart = Rectangle((0, 0), CART_W, CART_H, color=c, zorder=3); ax.add_patch(cart)
        rod, = ax.plot([], [], color=INK, linewidth=3, zorder=4)
        bob = Circle((0, 0), 0.45, color=INK, zorder=5); ax.add_patch(bob)
        info = ax.text(1.0, 1.02, "", transform=ax.transAxes, ha="right", va="bottom", fontsize=9, family="monospace", color=INK)
        tv = np.arange(len(xs)) * dt
        vax.semilogy(tv, Vs[mode], color=c, linewidth=1.0, alpha=0.2)          # faint full trace
        vline, = vax.semilogy([], [], color=c, linewidth=1.6)                    # drawn up to now
        vdot, = vax.semilogy([], [], "o", color=c, markersize=5)
        vax.set_xlim(0, T_END); vax.set_ylim(v_lo, v_hi)
        vax.set_title(r"Lyapunov function $V = \mathbf{x}^\top \mathbf{P} \mathbf{x}$", loc="left", fontsize=10, color=INK)
        vax.set_xlabel("time (s)", fontsize=9)
        panels.append(dict(ax=ax, xs=xs, us=us, cart=cart, rod=rod, bob=bob, info=info, arrow=None,
                           V=Vs[mode], tv=tv, vline=vline, vdot=vdot))

    def draw(k):
        clock.set_text(f"t = {k * dt:4.1f} s     (gray arrow = control force)")
        for P in panels:
            xs, us = P["xs"], P["us"]
            j = min(k, len(xs) - 1)            # a run that fell stays frozen in its last state
            th, s_ = xs[j, 0], xs[j, 1]
            P["cart"].set_xy((s_ - CART_W / 2, 0.15))
            px, py = s_, 0.15 + CART_H
            bx, by = px - L * np.sin(th), py + L * np.cos(th)   # HW1 convention: theta > 0 leans toward -s
            P["rod"].set_data([px, bx], [py, by]); P["bob"].center = (bx, by)
            fell = abs(th) > np.pi / 2
            F = 0.0 if fell else us[min(j, len(us) - 1)]
            P["info"].set_text(f"θ = {np.degrees(th):6.1f}°   F = {F:6.0f} N" + ("   FELL" if fell else ""))
            if P["arrow"] is not None:
                P["arrow"].remove()
            P["arrow"] = FancyArrow(s_, 0.15 + CART_H / 2, F * ARROW_SCALE, 0, width=0.25, head_width=0.7,
                                    head_length=min(0.8, abs(F * ARROW_SCALE) + 1e-6), length_includes_head=True,
                                    color="#52514e", zorder=6)
            P["ax"].add_patch(P["arrow"])
            P["vline"].set_data(P["tv"][:j + 1], P["V"][:j + 1])
            P["vdot"].set_data([P["tv"][j]], [P["V"][j]])
        return []

    fig.tight_layout(rect=(0, 0, 1, 0.97), h_pad=1.5, w_pad=2.5)
    anim = FuncAnimation(fig, draw, frames=frames, blit=False)
    # render locally first: writing a multi-MB GIF straight into a synced (Google Drive) folder can time out
    import shutil, tempfile
    out = os.path.join(HERE, "cartpole-kf.gif")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_gif = os.path.join(tmp, "cartpole-kf.gif")
        anim.save(tmp_gif, writer=PillowWriter(fps=round(1 / (STEP * dt))), dpi=80)
        shutil.copyfile(tmp_gif, out)
    plt.close(fig)
    print(f"saved {os.path.basename(out)}: {len(frames)} frames, {os.path.getsize(out) / 1e6:.1f} MB")
