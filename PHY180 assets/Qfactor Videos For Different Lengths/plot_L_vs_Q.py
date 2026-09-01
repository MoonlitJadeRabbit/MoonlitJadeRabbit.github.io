# -*- coding: utf-8 -*-
"""
Cubic best fit for Q vs Length:
    Q(L) = a + b L + c L^2 + d L^3

- Reads LQ_data.txt (columns: L Q dL dQ, with header)
- By default, fits UNWEIGHTED (recommended here to avoid dQ=1 dominating).
- If you want a weighted fit, set USE_WEIGHTS=True; the code clamps sigma
  from below to avoid extreme leverage: sigma = max(dQ, SIGMA_FLOOR).

Prints: a,b,c,d (±1σ), R^2, reduced chi^2 (if weighted), plus LaTeX.
Plots error bars + cubic best-fit curve.
"""

import os
import numpy as np
import warnings
import matplotlib
matplotlib.use("TkAgg")   # so a window pops up on double-click (Windows)
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

DATA_FILE     = "LQ_data.txt"
USE_WEIGHTS   = False     # <- set True to use dQ as sigma with a floor
SIGMA_FLOOR   = 8.0       # avoid a single tiny dQ dominating the fit

def f_cubic(L, a, b, c, d):
    return a + b*L + c*L**2 + d*L**3

def load_data(path):
    arr = np.loadtxt(path, skiprows=1)
    if arr.ndim == 1:
        arr = arr[None, :]
    return arr[:,0], arr[:,1], arr[:,2], arr[:,3]  # L, Q, dL, dQ

def ustr(val, err, sig=2):
    """Format value ± error with <sig> significant digits on the error."""
    if not np.isfinite(err) or err <= 0:
        return f"{val:.6g} ± n/a"
    p = int(np.floor(np.log10(abs(err))))
    err_rounded = round(err, -p + (sig - 1))
    decimals = max(0, -int(np.floor(np.log10(err_rounded))) + (sig - 1))
    v = round(val, decimals)
    fmt = f"{{:.{decimals}f}}"
    return f"{fmt.format(v)} ± {fmt.format(err_rounded)}"

def r2(y, yhat):
    ss_res = np.sum((y - yhat)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    return 1.0 - ss_res/ss_tot if ss_tot > 0 else np.nan

def main():
    here = os.path.dirname(__file__) or "."
    path = os.path.join(here, DATA_FILE)

    try:
        L, Q, dL, dQ = load_data(path)
    except Exception as e:
        print(f"Could not read {DATA_FILE}. Make sure it has columns L Q dL dQ and is next to this script.")
        print("Error:", e); input("\nPress Enter to close..."); return

    # initial guess: fit a quick least-squares polynomial to get p0
    p_lin = np.polyfit(L, Q, 3)  # returns [d, c, b, a] in descending powers
    a0 = p_lin[3]; b0 = p_lin[2]; c0 = p_lin[1]; d0 = p_lin[0]
    p0 = (a0, b0, c0, d0)

    sigma = None
    if USE_WEIGHTS:
        sigma = np.maximum(dQ, SIGMA_FLOOR)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        popt, pcov = curve_fit(
            f_cubic, L, Q, p0=p0,
            sigma=sigma if USE_WEIGHTS else None,
            absolute_sigma=True, maxfev=20000
        )
    perr = np.sqrt(np.diag(pcov))
    a, b, c, d = popt
    da, db, dc, dd = perr

    # Diagnostics
    Qhat = f_cubic(L, *popt)
    R2 = r2(Q, Qhat)
    if USE_WEIGHTS:
        r   = (Q - Qhat)/sigma
        chi2 = float(np.sum(r**2))
        dof  = max(1, len(Q) - len(popt))
        redchi2 = chi2/dof
    else:
        redchi2 = np.nan

    # Print summary
    print("\nCubic best fit:  Q(L) = a + b L + c L^2 + d L^3")
    print(f"  a = {ustr(a, da)}")
    print(f"  b = {ustr(b, db)}")
    print(f"  c = {ustr(c, dc)}")
    print(f"  d = {ustr(d, dd)}")
    print(f"  R^2 = {R2:.4f}")
    if np.isfinite(redchi2):
        print(f"  Reduced Chi^2 = {redchi2:.3f}")

    # LaTeX to paste into your report
    print("\nLaTeX:")
    print(fr"  Q(L) = ({ustr(a,da)}) + ({ustr(b,db)})\,L + ({ustr(c,dc)})\,L^2 + ({ustr(d,dd)})\,L^3")

    # Plot
    Ls = np.linspace(min(L)*0.95, max(L)*1.05, 600)
    plt.figure(figsize=(9.0, 6.0))
    plt.errorbar(L, Q, xerr=dL, yerr=dQ, fmt='k.', alpha=0.9, label="Data")
    plt.plot(Ls, f_cubic(Ls, *popt), 'r-', lw=2.2, label="Best fit (cubic)")
    plt.title("Length (m) vs Q")
    plt.xlabel("Length L (m)")
    plt.ylabel("Quality factor Q")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.show()
    input("\nDone. Press Enter to close...")

if __name__ == "__main__":
    main()
