# -*- coding: utf-8 -*-
"""
Period vs Length: power-law fit T = k * L^n.
- Terminal prints k, n (±1σ), R^2, reduced chi^2
- Standard plot + residuals
- Log–log plot titled "Length (m) vs Period (s) log-log"
- Legends show ONLY "Data" and "Best fit"
- Log–log legend at upper left
"""

import os
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # ensure plt.show() opens a window on double-click
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pylab import loadtxt

DATA_FILE = "length_period_data.txt"   # header + 4 cols: x y dx dy

def load_data(filename):
    # returns L, T, dL, dT
    return loadtxt(filename, usecols=(0,1,2,3), skiprows=1, unpack=True)

def powerlaw(L, k, n):
    return k * (L ** n)

def ustr(val, err, sig=2):
    """value ± error as text with error to <sig> sig figs, value matched"""
    if err <= 0 or not np.isfinite(err):
        return f"{val:.6g} ± n/a"
    p = int(np.floor(np.log10(abs(err))))
    err_rounded = round(err, -p + (sig - 1))
    decimals = max(0, -int(np.floor(np.log10(err_rounded))) + (sig - 1))
    fmt = f"{{:.{decimals}f}}"
    return f"{fmt.format(round(val, decimals))} ± {fmt.format(err_rounded)}"

def main():
    # ---- load ----
    here = os.path.dirname(__file__)
    L, T, dL, dT = load_data(os.path.join(here, DATA_FILE))

    # ---- fit (weighted by dT) ----
    p0 = (2.0, 0.5)
    popt, pcov = curve_fit(powerlaw, L, T, p0=p0,
                           sigma=dT, absolute_sigma=True, maxfev=20000)
    perr = np.sqrt(np.diag(pcov))
    k, n   = popt
    dk, dn = perr

    # predictions, R^2
    T_hat = powerlaw(L, *popt)
    ss_res = np.sum((T - T_hat)**2)
    ss_tot = np.sum((T - np.mean(T))**2)
    R2 = 1.0 - ss_res/ss_tot if ss_tot > 0 else np.nan

    # reduced chi^2 (if dT provided)
    if dT is not None and np.all(np.isfinite(dT)) and np.all(dT > 0):
        r_std = (T - T_hat)/dT
        chi2  = float(np.sum(r_std**2))
        dof   = max(1, len(T) - len(popt))
        redchi2 = chi2/dof
    else:
        chi2, redchi2 = np.nan, np.nan

    # ---- terminal prints (keep uncertainties here) ----
    print("\nPower-law fit:  T(L) = k * L^n")
    print(f"  k = {ustr(k, dk)}   (s · m^(-n))")
    print(f"  n = {ustr(n, dn)}")
    print(f"  R^2 = {R2:.4f}")
    if np.isfinite(redchi2):
        print(f"  Reduced Chi^2 = {redchi2:.3f}")

    g    = 9.81
    k_th = 2*np.pi/np.sqrt(g)
    print("\nSmall-angle theory:  T = (2π/√g) √L  →  n_theory = 0.5,  k_theory ≈ {:.6f}".format(k_th))

    # ---- figure 1: standard + residuals ----
    xs = np.linspace(0.9*min(L), 1.1*max(L), 1000)
    curve = powerlaw(xs, *popt)

    fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})

    ax1.errorbar(L, T, yerr=dT, xerr=dL, fmt='k.', alpha=0.9, label='Data')
    ax1.plot(xs, curve, 'r-', lw=2, label='Best fit')
    ax1.set_xlabel("Length L (m)")
    ax1.set_ylabel("Period T (s)")
    ax1.set_title("Period vs Length (power-law fit)")
    ax1.legend(loc='upper left')

    resid = T - powerlaw(L, *popt)
    ax2.errorbar(L, resid, yerr=dT, xerr=dL, fmt='k.')
    ax2.axhline(0, color='red', ls='--', lw=1)
    ax2.set_xlabel("Length L (m)")
    ax2.set_ylabel("Residuals")
    fig.tight_layout()

    # ---- figure 2: log–log with legend at upper left; legend shows only labels ----
    Ls = np.linspace(0.9*min(L), 1.1*max(L), 400)
    plt.figure(figsize=(7.2, 5.0))
    plt.errorbar(L, T, yerr=dT, xerr=dL, fmt='k.', alpha=0.9, label='Data')
    plt.plot(Ls, powerlaw(Ls, *popt), 'r-', lw=2, label='Best fit')
    plt.xscale('log'); plt.yscale('log')
    plt.xlabel("Length (m)")
    plt.ylabel("Period (s)")
    plt.title("Length (m) vs Period (s) log-log")
    plt.grid(True, which='both', alpha=0.3)
    plt.legend(loc='upper left')

    plt.show(block=True)
    input("\nDone. Press Enter to close...")

if __name__ == "__main__":
    main()
