# run_ringdown_with_bb.py
# Use professor's fit_black_box.py to fit a damped pendulum ring-down.

import os, sys
import numpy as np
from scipy.optimize import curve_fit

# --- import prof's black-box module (must be in the same folder) ---
try:
    import fit_black_box as bb
except Exception as e:
    print("Could not import fit_black_box.py. Make sure it is in the SAME folder.")
    print("Error:", e)
    input("\nPress Enter to close...")
    sys.exit(1)

DATA_FILE = "ringdown_data.txt"  # 4 columns: t theta dt dtheta (header line first)

# --- model: offset + exponentially decaying cosine ---
def damped_cos(t, C, A, tau, omega, phi):
    return C + A * np.exp(-t / tau) * np.cos(omega * t + phi)

# --- make decent initial guesses for curve_fit ---
def rough_guesses(t, y):
    C0 = float(np.median(y))
    y0 = y - C0
    A0 = max(0.5 * (y0.max() - y0.min()), 1e-3)

    # zero-crossings -> half period → T0
    s = np.sign(y0)
    zc = np.where(s[:-1] * s[1:] < 0)[0]
    if len(zc) >= 2:
        half = np.diff(t[zc])
        T0 = 2 * np.median(half)
    else:
        T0 = max((t[-1] - t[0]) / 8.0, 1e-2)
    w0 = 2 * np.pi / T0

    # envelope for tau from local maxima
    peaks = [i for i in range(1, len(y0) - 1) if y0[i - 1] < y0[i] > y0[i + 1]]
    if len(peaks) >= 2:
        tp = t[peaks]
        ap = np.abs(y0[peaks])
        ap[ap <= 0] = 1e-6
        m, _ = np.polyfit(tp, np.log(ap), 1)  # ln(A) ~ -t/tau + const
        tau0 = -1 / m if m < 0 else (t[-1] - t[0])
    else:
        tau0 = (t[-1] - t[0])

    return C0, A0, tau0, w0, 0.0

def main():
    # --- load data (prof's loader expects 4 columns after one header line) ---
    try:
        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"{DATA_FILE} not found in {os.getcwd()}")
        t, theta, dt, dtheta = bb.load_data(DATA_FILE)  # uses skiprows=1 under the hood
    except Exception as e:
        print("Failed to load data. Your file MUST look like:\n"
              "t theta dt dtheta\n"
              "0.0000 0.6800 0.0083 0.0050\n"
              "...\n(Spaces/tabs only; no commas.)")
        print("Error:", e)
        input("\nPress Enter to close...")
        return

    # --- fit once here to print T and Q nicely ---
    try:
        C0, A0, tau0, w0, phi0 = rough_guesses(t, theta)
        init = (C0, A0, tau0, w0, phi0)

        popt, pcov = curve_fit(
            damped_cos, t, theta, sigma=dtheta, p0=init,
            absolute_sigma=True, maxfev=20000
        )
        perr = np.sqrt(np.diag(pcov))
        C, A, tau, omega, phi = popt
        T = 2 * np.pi / omega
        Q = np.pi * tau / T

        print("\nBest-fit parameters (±1σ):")
        labels = ["C (offset)", "A (amp)", "tau (s)", "omega (rad/s)", "phi (rad)"]
        for name, v, e in zip(labels, popt, perr):
            print(f"  {name:15s} = {v:.6g} ± {e:.6g}")

        print("\nDerived:")
        print(f"  Period T = {T:.6g} s")
        print(f"  Q = π·tau/T = {Q:.6g}")

        # --- make the publication-style plot using prof's black-box plotter ---
        bb.plot_fit(
            damped_cos, t, theta,
            xerror=dt, yerror=dtheta,
            init_guess=init,
            xlabel="Time (s)", ylabel="Angle (rad)",
            title="Damped Pendulum (Tracker ring-down)"
        )

    except Exception as e:
        print("Fitting/plotting failed:", e)

    # keep window open if you double-click the .py on Windows
    input("\nDone. Press Enter to close...")

if __name__ == "__main__":
    main()
