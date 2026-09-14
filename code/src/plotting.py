"""
plotting.py
===========
All publication figures. Every figure is generated from computed data; none
contains illustrative or invented values.

House style
-----------
* Okabe-Ito colorblind-safe palette; no information carried by color alone
  (markers and line styles are always redundant with color).
* Vector output (PDF + SVG) plus 600 dpi PNG.
* Serif text matching typical journal body type, >= 8 pt at final size.
* Panel labels (a), (b)... on multi-panel figures.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

__all__ = ["OKABE_ITO", "apply_style", "save_figure", "FIGURE_BUILDERS",
           "build_all_figures"]

#: Okabe-Ito qualitative palette (colorblind-safe).
OKABE_ITO = {
    "black": "#000000", "orange": "#E69F00", "skyblue": "#56B4E9",
    "green": "#009E73", "yellow": "#F0E442", "blue": "#0072B2",
    "vermillion": "#D55E00", "purple": "#CC79A7", "gray": "#666666",
}

_SINGLE = (3.5, 2.7)      # single-column
_DOUBLE = (7.16, 3.0)     # double-column


def apply_style() -> None:
    """
    Journal-style rcParams. Called once by `build_all_figures`.

    Also pins figure output to be BYTE-REPRODUCIBLE. By default Matplotlib
    stamps a creation date into PDF and SVG output and generates random element
    IDs for SVG clip paths, so two runs of identical code produce different
    files. That made `git status` permanently dirty and made release-to-release
    diffs meaningless. SOURCE_DATE_EPOCH fixes the timestamp (Matplotlib honours
    the reproducible-builds convention) and svg.hashsalt fixes the IDs.
    """
    import os
    os.environ.setdefault("SOURCE_DATE_EPOCH", "1756166400")  # 2025-08-26 UTC
    plt.rcParams["svg.hashsalt"] = "dft-energy-study"
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "mathtext.fontset": "dejavuserif",
        "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.8,
        "axes.linewidth": 0.7, "lines.linewidth": 1.2, "lines.markersize": 3.4,
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.major.width": 0.7, "ytick.major.width": 0.7,
        "legend.frameon": True, "legend.framealpha": 0.92,
        "legend.edgecolor": "0.7", "legend.borderpad": 0.35,
        "grid.linewidth": 0.4, "grid.alpha": 0.3,
        "figure.dpi": 150, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    })


def save_figure(fig: plt.Figure, name: str, outdir: Path) -> dict[str, Path]:
    """Write PDF, SVG and 600 dpi PNG. Returns the paths written."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for ext, kwargs in (("pdf", {}), ("svg", {}), ("png", {"dpi": 600})):
        p = outdir / f"{name}.{ext}"
        fig.savefig(p, **kwargs)
        paths[ext] = p
    plt.close(fig)
    return paths


def _panel_label(ax, text: str) -> None:
    ax.text(-0.155, 1.04, text, transform=ax.transAxes,
            fontsize=8.5, fontweight="bold", va="bottom", ha="left")


# ---------------------------------------------------------------------------
# Figure 1 - recovered baseline and reconstructions
# ---------------------------------------------------------------------------
def figure_01_baseline(ctx: dict) -> plt.Figure:
    import coefficient_selection as cs
    import metrics as M
    import transforms as T

    x = ctx["S0"]
    spec = T.dft_direct(x)
    n = x.size
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=_DOUBLE)

    m11 = cs.lowpass_mask(n, 5)
    r11 = cs.reconstruct_from_mask(spec, m11)
    mdc = np.zeros(n, bool); mdc[0] = True
    rdc = cs.reconstruct_from_mask(spec, mdc)

    idx = np.arange(n)
    ax1.plot(idx, x, color=OKABE_ITO["black"], marker="o", ls="-",
             label="recovered $x[n]$", zorder=3)
    ax1.plot(idx, r11, color=OKABE_ITO["vermillion"], marker="s", ls="--",
             label=(rf"11 coeff.: $\eta_{{\rm total}}$={M.energy_retention_total(spec,m11)*100:.2f}%, "
                    rf"$\varepsilon_{{L2}}$={M.relative_l2_error(x,r11):.3f}"))
    ax1.plot(idx, rdc, color=OKABE_ITO["blue"], ls=":", lw=1.6,
             label=(rf"DC only: $\eta_{{\rm total}}$={M.dc_energy_share(spec)*100:.2f}%, "
                    rf"$\varepsilon_{{L2}}$={M.relative_l2_error(x,rdc):.3f}"))
    ax1.set_xlabel("sample index $n$ (dimensionless)")
    ax1.set_ylabel("amplitude (arbitrary units)")
    ax1.legend(loc="upper left"); ax1.grid(True)
    _panel_label(ax1, "(a)")

    mag = np.abs(spec)
    half = np.arange(n // 2 + 1)
    ax2.stem(half, mag[half], basefmt=" ",
             linefmt=OKABE_ITO["gray"], markerfmt="o")
    for line in ax2.get_children():
        pass
    ax2.set_yscale("log")
    ax2.set_xlabel("frequency bin $k$ (normalized)")
    ax2.set_ylabel(r"$|X[k]|$")
    ax2.annotate(f"DC: {M.dc_energy_share(spec)*100:.1f}% of $E$",
                 xy=(0, mag[0]), xytext=(3.0, mag[0] * 0.55),
                 fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.7,
                                             color=OKABE_ITO["vermillion"]),
                 color=OKABE_ITO["vermillion"])
    ax2.grid(True, which="both")
    _panel_label(ax2, "(b)")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 2 - DC energy share vs r (Experiment A)
# ---------------------------------------------------------------------------
def figure_02_dc_sweep(ctx: dict) -> plt.Figure:
    df = ctx["exp_a"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=_DOUBLE)

    r_dense = np.linspace(0, 17, 600)
    ax1.plot(r_dense, r_dense ** 2 / (1 + r_dense ** 2) * 100,
             color=OKABE_ITO["black"], lw=1.1,
             label=r"theory $\eta_{\rm DC}=r^{2}/(1+r^{2})$")
    ax1.plot(df["r"], df["eta_dc_measured"] * 100, ls="none", marker="o",
             mfc="none", mec=OKABE_ITO["vermillion"], mew=1.1, ms=6,
             label="measured (Exp. A)")
    ax1.set_xlabel(r"mean-to-standard-deviation ratio $r=\mu/\sigma$")
    ax1.set_ylabel(r"DC energy share $\eta_{\rm DC}$ (%)")
    ax1.legend(loc="lower right"); ax1.grid(True)
    ax1.set_ylim(-4, 104)
    _panel_label(ax1, "(a)")

    ax2.plot(df["r"], df["eta_total_7coef"] * 100, marker="o",
             color=OKABE_ITO["vermillion"],
             label=r"$\eta_{\rm total}$, fixed 7-coeff. budget")
    ax2.plot(df["r"], df["eta_ac_7coef"] * 100, marker="s", ls="--",
             color=OKABE_ITO["green"], label=r"$\eta_{\rm AC}$, same budget")
    ax2.plot(df["r"], df["eps_l2_ac_7coef"] * 100, marker="^", ls=":",
             color=OKABE_ITO["blue"],
             label=r"$\varepsilon_{L2}$ on the fluctuation")
    ax2.set_xlabel(r"mean-to-standard-deviation ratio $r=\mu/\sigma$")
    ax2.set_ylabel(r"percentage (%)")
    ax2.legend(loc="center right"); ax2.grid(True)
    ax2.set_ylim(-4, 104)
    _panel_label(ax2, "(b)")
    fig.tight_layout()
    return fig


def _curve(df, sig, strategy, basis):
    q = df[(df["id"] == sig) & (df["strategy"] == strategy) & (df["basis"] == basis)]
    return q.sort_values("n_coeff")


# ---------------------------------------------------------------------------
# Figures 3 and 4 - retention vs error, both bases
# ---------------------------------------------------------------------------
def _retention_vs_error(ctx, basis, eta_col, xlabel):
    df = ctx["selection"]
    fig, ax = plt.subplots(figsize=_SINGLE)
    styles = [("S0", OKABE_ITO["black"], "o", "-"),
              ("S1", OKABE_ITO["blue"], "s", "--"),
              ("S2", OKABE_ITO["vermillion"], "^", "-."),
              ("S4", OKABE_ITO["green"], "D", ":"),
              ("S5", OKABE_ITO["purple"], "v", "-")]
    for sig, color, marker, ls in styles:
        c = _curve(df, sig, "lowpass", basis)
        if c.empty:
            continue
        ax.plot(c[eta_col] * 100, c["eps_l2"], color=color, marker=marker,
                ls=ls, label=sig, ms=3.0)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(r"relative $L_2$ error $\varepsilon_{L2}$")
    ax.legend(ncol=2, loc="upper right"); ax.grid(True)
    fig.tight_layout()
    return fig


def figure_03_total_vs_error(ctx: dict) -> plt.Figure:
    """
    The redundancy result. Panel (a): every corpus curve, on either basis,
    lies exactly on eps_L2 = sqrt(1 - eta). Panel (b): the two error measures
    differ by exactly sqrt(1 + r^2).
    """
    import metrics as M

    df = ctx["selection"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=_DOUBLE)

    eta_dense = np.linspace(0, 1, 400)
    ax1.plot(eta_dense * 100, np.sqrt(1 - eta_dense), color=OKABE_ITO["black"],
             lw=1.3, zorder=1, label=r"identity $\varepsilon_{L2}=\sqrt{1-\eta}$")
    styles = [("S0", "total", OKABE_ITO["vermillion"], "o"),
              ("S2", "total", OKABE_ITO["orange"], "^"),
              ("S4", "total", OKABE_ITO["green"], "D"),
              ("S0", "ac", OKABE_ITO["blue"], "s"),
              ("S5", "ac", OKABE_ITO["purple"], "v")]
    for sig, basis, color, marker in styles:
        c = _curve(df, sig, "lowpass", basis)
        if c.empty:
            continue
        eta = c["eta_total"] if basis == "total" else c["eta_ac"]
        ax1.plot(eta * 100, c["eps_l2"], ls="none", marker=marker, mfc="none",
                 mec=color, mew=0.9, ms=4.2, label=f"{sig}, {basis} basis")
    ax1.set_xlabel(r"retained energy $\eta$ on its own basis (%)")
    ax1.set_ylabel(r"relative $L_2$ error $\varepsilon_{L2}$")
    ax1.legend(loc="upper right", ncol=1); ax1.grid(True)
    _panel_label(ax1, "(a)")

    a = ctx["exp_a"]
    r = a["r"].to_numpy(dtype=float)
    ax2.plot(r, a["eps_l2_ac_7coef"] * 100, marker="s", ls="--",
             color=OKABE_ITO["blue"],
             label=r"$\varepsilon_{L2}$ on the fluctuation")
    ax2.plot(r, a["eps_l2_full_7coef"] * 100, marker="o", ls="-",
             color=OKABE_ITO["vermillion"],
             label=r"$\varepsilon_{L2}$ on the full signal")
    predicted = a["eps_l2_ac_7coef"].to_numpy(dtype=float) / np.sqrt(1 + r ** 2)
    ax2.plot(r, predicted * 100, ls=":", lw=1.4, color=OKABE_ITO["black"],
             marker="x", ms=4,
             label=r"prediction $\varepsilon_{\rm AC}/\sqrt{1+r^{2}}$")
    ax2.set_xlabel(r"mean-to-standard-deviation ratio $r=\mu/\sigma$")
    ax2.set_ylabel(r"relative $L_2$ error (%)")
    ax2.legend(loc="upper right"); ax2.grid(True)
    _panel_label(ax2, "(b)")
    fig.tight_layout()
    return fig


def figure_04_ac_vs_error(ctx: dict) -> plt.Figure:
    return _retention_vs_error(ctx, "ac", "eta_ac",
                               r"retained AC energy $\eta_{\rm AC}$ (%)")


# ---------------------------------------------------------------------------
# Figure 5 - coefficient count vs error, all selection methods
# ---------------------------------------------------------------------------
def figure_05_selection(ctx: dict) -> plt.Figure:
    df = ctx["selection"]
    fig, axes = plt.subplots(1, 2, figsize=_DOUBLE, sharey=True)
    for ax, sig, label in ((axes[0], "S0", "S0 (recovered baseline)"),
                           (axes[1], "S4", "S4 (broadband)")):
        for strat, basis, color, marker, ls in (
                ("lowpass", "total", OKABE_ITO["vermillion"], "o", "-"),
                ("magnitude", "total", OKABE_ITO["orange"], "s", "--"),
                ("lowpass", "ac", OKABE_ITO["blue"], "^", "-."),
                ("magnitude", "ac", OKABE_ITO["green"], "D", ":")):
            c = _curve(df, sig, strat, basis)
            if c.empty:
                continue
            ax.plot(c["n_coeff"], c["eps_l2"], color=color, marker=marker,
                    ls=ls, label=f"{strat}, {basis} basis", ms=3.0)
        ax.set_xlabel("retained coefficients")
        ax.set_title(label, fontsize=8)
        ax.grid(True)
    axes[0].set_ylabel(r"relative $L_2$ error $\varepsilon_{L2}$")
    axes[0].legend(loc="upper right")
    _panel_label(axes[0], "(a)"); _panel_label(axes[1], "(b)")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 6 - DFT vs DCT compaction
# ---------------------------------------------------------------------------
def figure_06_dft_vs_dct(ctx: dict) -> plt.Figure:
    df = ctx["dct"]
    panels = [("S0", "(a) S0 recovered baseline"),
              ("S2", "(b) S2 leaky sinusoid"),
              ("S5", "(c) S5 transient")]
    fig, axes = plt.subplots(1, 3, figsize=(7.16, 2.5), sharey=True)
    for ax, (sig, title) in zip(axes, panels):
        for tf, color, marker, ls in (("DFT", OKABE_ITO["vermillion"], "o", "-"),
                                       ("DCT-II", OKABE_ITO["blue"], "s", "--")):
            c = df[(df["id"] == sig) & (df["transform"] == tf)].sort_values("n_coeff")
            if c.empty:
                continue
            ax.plot(c["n_coeff"], c["eta"] * 100, color=color, marker=marker,
                    ls=ls, label=tf, ms=3.0)
        ax.set_xlabel("retained coefficients")
        ax.set_title(title, fontsize=7.6)
        ax.grid(True); ax.set_ylim(-4, 104)
    axes[0].set_ylabel(r"retained energy (%)")
    axes[0].legend(loc="lower right")
    fig.suptitle("mean-removed signals; both transforms orthonormal",
                 fontsize=7.4, y=1.02)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 7 - spectral leakage
# ---------------------------------------------------------------------------
def figure_07_leakage(ctx: dict) -> plt.Figure:
    import transforms as T
    n = 26
    t = np.arange(n)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=_DOUBLE)
    half = np.arange(n // 2 + 1)
    for off, color, marker, ls, lab in ((3.0, OKABE_ITO["blue"], "o", "-",
                                          "bin-centered ($k_0=3$)"),
                                         (3.5, OKABE_ITO["vermillion"], "s", "--",
                                          "half-bin offset ($k_0=3.5$)")):
        x = np.cos(2 * np.pi * off * t / n)
        x = x - x.mean()
        mag = np.abs(T.dft_direct(x))
        ax1.plot(half, np.maximum(mag[half], 1e-16), color=color, marker=marker,
                 ls=ls, label=lab, ms=3.2)
    ax1.set_yscale("log"); ax1.set_ylim(1e-17, 1e1)
    ax1.set_xlabel("frequency bin $k$ (normalized)")
    ax1.set_ylabel(r"$|X[k]|$")
    ax1.legend(loc="lower right"); ax1.grid(True, which="both")
    _panel_label(ax1, "(a)")

    df = ctx["leakage"]
    ax2.plot(df["bin_offset"], df["leakage_energy_fraction"] * 100,
             color=OKABE_ITO["vermillion"], marker="o")
    ax2.set_xlabel("sinusoid frequency (bins)")
    ax2.set_ylabel(r"AC energy outside strongest pair (%)")
    ax2.grid(True)
    _panel_label(ax2, "(b)")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 8 - window comparison
# ---------------------------------------------------------------------------
def figure_08_windows(ctx: dict) -> plt.Figure:
    import leakage_analysis as LA
    df = ctx["windows"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=_DOUBLE)

    colors = [OKABE_ITO["black"], OKABE_ITO["blue"],
               OKABE_ITO["vermillion"], OKABE_ITO["green"]]
    lss = ["-", "--", "-.", ":"]
    over, n = 512, 26
    for name, color, ls in zip(LA.WINDOWS, colors, lss):
        w = LA.window(name, n)
        padded = np.zeros(n * over); padded[:n] = w
        mag = np.abs(np.fft.rfft(padded))
        freq = np.arange(mag.size) / over
        ax1.plot(freq, 20 * np.log10(mag / mag[0] + 1e-300),
                 color=color, ls=ls, label=name, lw=1.0)
    ax1.set_xlim(0, 6); ax1.set_ylim(-100, 5)
    ax1.set_xlabel("frequency offset (bins)")
    ax1.set_ylabel("normalized response (dB)")
    ax1.legend(loc="upper right"); ax1.grid(True)
    _panel_label(ax1, "(a)")

    xpos = np.arange(len(df))
    ax2.bar(xpos - 0.2, df["eta_2pair"] * 100, width=0.4,
            color=OKABE_ITO["skyblue"], edgecolor="black", lw=0.5,
            label=r"$\eta_{\rm total}$, 4 coeff. (%)", hatch="//")
    ax2.bar(xpos + 0.2, df["eps_l2_after_2pair_truncation"] * 100, width=0.4,
            color=OKABE_ITO["orange"], edgecolor="black", lw=0.5,
            label=r"$\varepsilon_{L2}$, 4 coeff. (%)")
    ax2.set_xticks(xpos); ax2.set_xticklabels(df["window"], rotation=15)
    ax2.set_xlabel("window function")
    ax2.set_ylabel(r"percentage (%)")
    ax2.legend(loc="center right"); ax2.grid(True, axis="y")
    _panel_label(ax2, "(b)")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 9 - noise robustness
# ---------------------------------------------------------------------------
def figure_09_noise(ctx: dict) -> plt.Figure:
    s = ctx["noise_summary"].sort_values("snr_db")
    fig, ax = plt.subplots(figsize=_SINGLE)
    for col, color, marker, ls, lab in (
            ("eta_total", OKABE_ITO["vermillion"], "o", "-", r"$\eta_{\rm total}$"),
            ("eta_ac", OKABE_ITO["green"], "s", "--", r"$\eta_{\rm AC}$"),
            ("eps_l2_ac_vs_clean", OKABE_ITO["blue"], "^", ":",
             r"$\varepsilon_{L2}$ (fluctuation vs clean)")):
        mean = s[f"{col}_mean"] * 100
        lo, hi = s[f"{col}_ci_lo"] * 100, s[f"{col}_ci_hi"] * 100
        ax.plot(s["snr_db"], mean, color=color, marker=marker, ls=ls, label=lab)
        ax.fill_between(s["snr_db"], lo, hi, color=color, alpha=0.25, lw=0)
    ax.set_xlabel("input SNR (dB)")
    ax.set_ylabel(r"percentage (%)")
    ax.legend(loc="center right"); ax.grid(True)
    ax.set_title(r"11-coefficient budget; mean of $n=100$, shaded 95% CI",
                 fontsize=7.2)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Figure 10 - Parseval discrepancy vs N and precision
# ---------------------------------------------------------------------------
def figure_10_precision(ctx: dict) -> plt.Figure:
    df = ctx["precision"]
    fig, ax = plt.subplots(figsize=_SINGLE)
    for prec, color, marker, ls in (("float32", OKABE_ITO["vermillion"], "o", "-"),
                                     ("float64", OKABE_ITO["blue"], "s", "--")):
        c = df[df["precision"] == prec].sort_values("N")
        ax.plot(c["N"], np.maximum(c["eps_parseval"], 1e-20), color=color,
                marker=marker, ls=ls, label=prec)
    ref = float(ctx["modeling_error_reference"])
    ax.axhline(ref, color=OKABE_ITO["black"], ls=":", lw=1.1)
    ax.text(0.97, ref * 1.6, "modeling error of Fig. 3", fontsize=6.5,
            ha="right", transform=ax.get_yaxis_transform())
    ax.set_xscale("log", base=2); ax.set_yscale("log")
    ax.set_xlabel("transform length $N$")
    ax.set_ylabel(r"Parseval discrepancy $\varepsilon_P$")
    ax.legend(loc="center left"); ax.grid(True, which="both")
    fig.tight_layout()
    return fig


FIGURE_BUILDERS = {
    "fig01_recovered_baseline": figure_01_baseline,
    "fig02_dc_energy_share_sweep": figure_02_dc_sweep,
    "fig03_total_energy_vs_error": figure_03_total_vs_error,
    "fig04_ac_energy_vs_error": figure_04_ac_vs_error,
    "fig05_selection_strategies": figure_05_selection,
    "fig06_dft_vs_dct": figure_06_dft_vs_dct,
    "fig07_spectral_leakage": figure_07_leakage,
    "fig08_window_comparison": figure_08_windows,
    "fig09_noise_robustness": figure_09_noise,
    "fig10_parseval_precision": figure_10_precision,
}


def build_all_figures(ctx: dict, outdir: Path) -> dict[str, dict[str, Path]]:
    """Build every figure. Any builder that raises is a hard failure."""
    apply_style()
    written = {}
    for name, builder in FIGURE_BUILDERS.items():
        fig = builder(ctx)
        written[name] = save_figure(fig, name, outdir)
    return written
