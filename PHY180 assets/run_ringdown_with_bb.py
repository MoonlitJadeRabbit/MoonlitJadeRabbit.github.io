# run_ringdown_with_bb.py — red damped-cosine best fit + GREEN envelope from the SAME fit (no autosave)
import sys, traceback
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ------------- settings you can tweak -------------
DATA_FILE     = "ringdown_data.txt"   # header + 4 cols: t theta dt dtheta
SKIP_CYCLES   = 2                     # drop first N fitted periods from residuals
OUTLIER_SIGMA = 3.0                   # robust residual cull (MAD-sigmas)
RESID_YLIM    = (-0.4, 0.4)
LEGEND_LOC    = "upper right"
DOT_SIZE      = 1.6
DOT_ALPHA     = 0.35
# --------------------------------------------------

# ---------- helper: format without e-notation ----------
def fmt_pm(value, err, digits=3):
    """
    Format value ± err without using 'e' notation.
    Example: (1.23 ± 0.04)×10^(-3) or 0.123000 ± 0.004000
    """
    if not np.isfinite(value) or not np.isfinite(err):
        return f"{value} ± {err}"

    if err == 0 or value == 0:
        return f"{value:.6f} ± {err:.6f}"

    exponent = int(np.floor(np.log10(abs(err))))
    scale = 10.0 ** exponent
    v_scaled = value / scale
    e_scaled = err / scale

    # If exponent is small, just print normally (no ×10^n)
    if -3 <= exponent <= 3:
        return f"{value:.6f} ± {err:.6f}"

    return f"({v_scaled:.{digits}f} ± {e_scaled:.{digits}f})×10^{exponent}"
# --------------------------------------------------

# Import your prof's loader
try:
    import fit_black_box as bb
except Exception as e:
    print("Could not import fit_black_box.py. Make sure it is in the same folder.")
    print("Error:", e)
    input("\nPress Enter to close...")
    sys.exit(1)

def damped_cos(t, C, A, tau, omega, phi):
    return C + A*np.exp(-t/tau)*np.cos(omega*t + phi)

def first_peak_index(theta):
    for i in range(1, len(theta)-1):
        if theta[i-1] < theta[i] > theta[i+1]:
            return i
    return 0

def rough_guesses(t, y):
    C0 = float(np.median(y)); y0 = y - C0
    A0 = max(0.5*(y0.max()-y0.min()), 1e-3)

    # omega from zero-crossings
    s = np.sign(y0); zc = np.where(s[:-1]*s[1:] < 0)[0]
    if len(zc) >= 2: 
        T0 = 2*np.median(np.diff(t[zc]))
    else:            
        T0 = max((t[-1]-t[0])/8.0, 1e-2)
    w0 = 2*np.pi/T0

    # tau from crude envelope slope (fallback)
    peaks = [i for i in range(1,len(y0)-1) if y0[i-1] < y0[i] > y0[i+1]]
    if len(peaks) >= 2:
        tp = t[peaks]; ap = np.abs(y0[peaks]); ap[ap<=0]=1e-6
        m,_ = np.polyfit(tp, np.log(ap), 1)
        tau0 = -1/m if m < 0 else (t[-1]-t[0])
    else:
        tau0 = (t[-1]-t[0])
    return C0, A0, tau0, w0, 0.0

def main():
    # Load data
    t, th, dt, dth = bb.load_data(DATA_FILE)

    # Align so first clear peak is at t=0
    i0 = first_peak_index(th)
    t, th, dt, dth = t[i0:] - t[i0], th[i0:], dt[i0:], dth[i0:]

    # Fit the damped cosine
    init = rough_guesses(t, th)
    popt, pcov = curve_fit(damped_cos, t, th, sigma=dth, p0=init,
                           absolute_sigma=True, maxfev=20000)
    perr = np.sqrt(np.diag(pcov))

    # --- Inflate uncertainties using reduced chi-squared ---
    resid_all = th - damped_cos(t, *popt)
    chi2 = np.sum((resid_all / dth)**2)
    dof = max(len(t) - len(popt), 1)
    chi2_red = chi2 / dof

    # scale uncertainties by sqrt(chi2_red) but never shrink them below the raw value
    scale_factor = np.sqrt(max(chi2_red, 1.0))
    perr = perr * scale_factor
    # --------------------------------------------------------

    C, A, tau, omega, phi = popt
    sigma_C, sigma_A, sigma_tau, sigma_omega, sigma_phi = perr

    # ------------ Derived quantities ------------
    T = 2*np.pi/omega
    sigma_T_raw = 2*np.pi * sigma_omega / omega**2

    # Estimate how many cycles were actually observed
    duration = t.max() - t.min()
    # make sure we don't divide by zero or go below one cycle
    n_cycles = max(duration / T, 1.0)

    # Set a floor for the period uncertainty: cannot be smaller than T/sqrt(N_cycles)
    sigma_T_floor = T / np.sqrt(n_cycles)
    sigma_T = max(sigma_T_raw, sigma_T_floor)

    Q = np.pi * tau / T
    sigma_Q = Q * np.sqrt((sigma_tau / tau)**2 + (sigma_T / T)**2)
    # -------------------------------------------

    print("\nBest-fit parameters (±1σ):")
    for name, v, e in zip(["C","A","tau (s)","omega (rad/s)","phi (rad)"], popt, perr):
        print(f"  {name:14s} = {fmt_pm(v, e)}")

    print("\nDerived:")
    print(f"  Period T       = {fmt_pm(T, sigma_T)} s")
    print(f"  Q = π·tau/T    = {fmt_pm(Q, sigma_Q)}")

    # Residuals (skip early cycles; robust outlier cull)
    keep = t >= (SKIP_CYCLES * T)
    t_res, th_res = t[keep], th[keep]
    resid = th_res - damped_cos(t_res, *popt)
    med = np.median(resid); mad = np.median(np.abs(resid - med)) or 1e-9
    thr = OUTLIER_SIGMA * 1.4826 * mad
    good = np.abs(resid - med) <= thr
    t_res, resid = t_res[good], resid[good]

    # Smooth curves
    ts = np.linspace(0.0, t.max(), 3000)
    fit = damped_cos(ts, *popt)

    # GREEN envelope taken DIRECTLY from the cosine fit (identical A, tau)
    env_mag = np.abs(A) * np.exp(-ts / tau)      # |A| e^{-t/tau}
    upper   = C + env_mag
    lower   = C - env_mag

    # ---- Plot ----
    import matplotlib.gridspec as gridspec
    fig = plt.figure(figsize=(10, 6), constrained_layout=True)
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1])
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])

    # data
    ax1.plot(t, th, 'k.', ms=DOT_SIZE, alpha=DOT_ALPHA, zorder=2, label='data')

    # red damped-cosine fit
    ax1.plot(ts, fit, '-', color='red', lw=1.6, zorder=3, label='best fit')

    # GREEN envelope (from the SAME fit) — upper and lower
    ax1.plot(ts, upper, color='green', lw=2.0, zorder=3, label='exp envelope (from best fit)')
    ax1.plot(ts, lower, color='green', lw=2.0, zorder=3)

    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Angle (rad)")
    ax1.set_title("Amplitude Decay")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc=LEGEND_LOC)

    # residuals
    ax2.plot(t_res, resid, 'k.', ms=DOT_SIZE)
    ax2.axhline(0, color='red', ls='--', lw=1)
    ax2.set_ylim(*RESID_YLIM)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Residuals (rad)")
    ax2.grid(True, alpha=0.3)

    plt.show(block=True)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n--- An error occurred ---")
        traceback.print_exc()
    finally:
        input("\nDone. Press Enter to close...")
