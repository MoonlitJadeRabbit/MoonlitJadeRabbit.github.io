# print_tau_and_cycles.py — prints only tau; writes t, angle, cycles (tab-delimited)

import numpy as np
from scipy.optimize import curve_fit

INFILE  = "ringdown_t_theta.txt"                 # expects header: t<TAB>angle
OUTFILE = "ringdown_t_theta_with_cycles.txt"     # t<TAB>angle<TAB>cycles

# ---- model ----
def damped_cos(t, C, A, tau, omega, phi):
    return C + A*np.exp(-t/tau)*np.cos(omega*t + phi)

def first_peak_index(y):
    for i in range(1, len(y)-1):
        if y[i-1] < y[i] > y[i+1]:
            return i
    return 0

def rough_guesses(t, y):
    C0 = float(np.median(y))
    y0 = y - C0
    A0 = max(0.5*(y0.max() - y0.min()), 1e-8)

    # period guess from zero crossings
    s = np.sign(y0)
    zc = np.where(s[:-1] * s[1:] < 0)[0]
    if len(zc) >= 2:
        half = np.diff(t[zc])
        T0 = max(2*np.median(half), 1e-3)
    else:
        T0 = max((t[-1]-t[0])/8.0, 1e-2)
    w0 = 2*np.pi / T0

    # tau guess from envelope of peaks
    peaks = [i for i in range(1, len(y0)-1) if y0[i-1] < y0[i] > y0[i+1]]
    if len(peaks) >= 2:
        tp = t[peaks]
        ap = np.abs(y0[peaks]); ap[ap <= 1e-12] = 1e-12
        m, _ = np.polyfit(tp, np.log(ap), 1)     # log(ap) ≈ -t/tau + const
        tau0 = -1.0/m if m < 0 else max(t[-1]-t[0], 1e-2)
    else:
        tau0 = max(t[-1]-t[0], 1e-2)

    return C0, A0, tau0, w0, 0.0

def load_t_theta(fname):
    # robust to tabs/spaces; requires header with names (e.g., "t\tangle")
    try:
        arr = np.genfromtxt(fname, names=True, dtype=float, comments=None)
        names = [n.lower().strip() for n in arr.dtype.names]
        def find(options):
            for k in options:
                if k in names: return names.index(k)
            return None
        i_t = find(["t", "time"])
        i_y = find(["angle", "theta", "y"])
        if i_t is None or i_y is None:
            # fallback to first two columns
            cols = [arr[n] for n in arr.dtype.names[:2]]
            data = np.vstack(cols).T
        else:
            data = np.vstack([arr[arr.dtype.names[i_t]], arr[arr.dtype.names[i_y]]]).T
    except Exception:
        # plain load: skip header, take first two columns
        data = np.loadtxt(fname, skiprows=1, usecols=(0,1))
    data = np.atleast_2d(data)
    t = np.asarray(data[:,0], float)
    y = np.asarray(data[:,1], float)
    good = np.isfinite(t) & np.isfinite(y)
    t, y = t[good], y[good]
    order = np.argsort(t)
    return t[order], y[order]

def main():
    # load original data
    t0_all, y_all = load_t_theta(INFILE)
    if t0_all.size < 5:
        print("0.0")
        return

    # align fit to first peak (for robust phase)
    i0 = first_peak_index(y_all)
    t_shift = t0_all[i0]
    t_fit   = t0_all[i0:] - t_shift
    y_fit   = y_all[i0:]

    # fit
    p0 = rough_guesses(t_fit, y_fit)
    try:
        popt, pcov = curve_fit(damped_cos, t_fit, y_fit, p0=p0, maxfev=20000)
        tau   = float(popt[2])
        omega = float(popt[3])
    except Exception:
        # fallback
        tau   = float(p0[2])
        omega = float(2*np.pi / max((t_fit[-1]-t_fit[0])/4.0, 1e-2))

    # print ONLY tau (s)
    print(f"{tau:.6f}")

    # compute cycles for *all* original samples, relative to first peak time
    T = 2*np.pi / omega if omega > 0 else np.inf
    dt_all = np.clip(t0_all - t_shift, 0.0, None)
    cycles = np.floor(dt_all / T).astype(int)

    # write augmented file (tab-delimited)
    with open(OUTFILE, "w") as f:
        f.write("t\tangle\tcycles\n")
        for ti, yi, ci in zip(t0_all, y_all, cycles):
            f.write(f"{ti:.9f}\t{yi:.9f}\t{ci:d}\n")

if __name__ == "__main__":
    main()
