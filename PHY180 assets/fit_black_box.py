# -*- coding: utf-8 -*-
"""
Fit and plot period vs angle for a pendulum, including uncertainties.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pylab import loadtxt

# -----------------------------
# Load data function
# -----------------------------
def load_data(filename):
    data = loadtxt(filename, usecols=(0,1,2,3), skiprows=1, unpack=True)
    return data

# -----------------------------
# Define model function
# -----------------------------
# Quadratic correction: T = a + b*x^2 + c*x^4
def my_func(x, a, b, c):
    return a + c*x**2 + b*x

# -----------------------------
# # Fit and plot function
# -----------------------------
def plot_fit(my_func, xdata, ydata, xerror=None, yerror=None,
             xlabel="Angle (rad)", ylabel="Period (s)",
             title="Period vs Angle (Damped Pendulum)"):

    plt.rcParams.update({'font.size': 14})
    plt.rcParams['figure.figsize'] = 10, 9

    # Curve fitting
    popt, pcov = curve_fit(my_func, xdata, ydata, sigma=yerror,
                           absolute_sigma=True, maxfev=5000)
    perr = np.sqrt(np.diag(pcov))

    def ustr(val, err, sig=2):
        """Return 'value ± error' with error to <sig> sig figs, value matched."""
        if err <= 0 or not np.isfinite(err):
            return f"{val:.6g} ± n/a"
        # digits after decimal for the rounded error
        p = int(np.floor(np.log10(abs(err))))
        err_rounded = round(err, -p + (sig-1))
        # decimals to show after rounding
        decimals = max(0, -int(np.floor(np.log10(err_rounded))) + (sig-1))
        fmt = f"{{:.{decimals}f}}"
        return f"{fmt.format(round(val, decimals))} ± {fmt.format(err_rounded)}"

    a, b, c   = popt
    da, db, dc = perr

    # --- core prints ---
    print("\nBest-fit parameters (1σ):")
    print(f"  a = {ustr(a, da)}")
    print(f"  b = {ustr(b, db)}")
    print(f"  c = {ustr(c, dc)}")

    print("\nBest-fit function (numeric):")
    print(f"  T(theta) = {a:.6g} + {b:.6g}*theta + {c:.6g}*theta**2")

    print("\nBest-fit function with 1σ uncertainties:")
    print(f"  T(theta) = ({ustr(a,da)}) + ({ustr(b,db)})*theta + ({ustr(c,dc)})*theta**2")

    # LaTeX / Excel helpers
    print("\nLaTeX:")
    print(rf"  T(\theta) = ({ustr(a,da)}) + ({ustr(b,db)})\,\theta + ({ustr(c,dc)})\,\theta^2")

    print("\nExcel (theta in A2):")
    print(f"  = {a:.10g} + {b:.10g}*A2 + {c:.10g}*A2^2")

    # Goodness-of-fit (only meaningful if yerror provided)
    if yerror is not None and np.all(np.isfinite(yerror)) and np.all(yerror>0):
        resid = (ydata - my_func(xdata, *popt)) / yerror
        chi2 = float(np.sum(resid**2))
        dof  = max(1, len(xdata) - len(popt))
        print(f"\nChi^2 = {chi2:.3f}  (dof = {dof})   Reduced Chi^2 = {chi2/dof:.3f}")

    # Parameter correlation matrix
    with np.errstate(invalid='ignore', divide='ignore'):
        denom = np.outer(perr, perr)
        corr = pcov / denom
        np.fill_diagonal(corr, 1.0)
    print("\nCorrelation matrix:")
    for row in corr:
        print("  " + " ".join(f"{v:7.3f}" if np.isfinite(v) else "   n/a" for v in row))

    # Smooth curve for plotting
    xs = np.linspace(min(xdata), max(xdata), 1000)
    curve = my_func(xs, *popt)

    # Make plots
    fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [2, 1]})

    # Data with error bars
    ax1.errorbar(xdata, ydata, yerr=yerror, xerr=xerror, fmt=".",
                 label="Data", color="black")
    ax1.plot(xs, curve, label="Best fit", color="red")
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_title(title)
    ax1.legend(loc="upper right")

    # Residuals
    residuals = ydata - my_func(xdata, *popt)
    ax2.errorbar(xdata, residuals, yerr=yerror, xerr=xerror, fmt=".", color="black")
    ax2.axhline(y=0, color="red", linestyle="--")
    ax2.set_xlabel(xlabel)
    ax2.set_ylabel("Residuals")

    fig.tight_layout()
    plt.show()
    fig.savefig("pendulum_fit.png")

# -----------------------------
# Main program
# -----------------------------
if __name__ == "__main__":
    # Load your dataset
    xdata, ydata, xerr, yerr = load_data("pendulum_data.txt")

    # Run the fit and plot
    plot_fit(my_func, xdata, ydata, xerror=xerr, yerror=yerr)
