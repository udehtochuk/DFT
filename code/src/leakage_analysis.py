"""
leakage_analysis.py
===================
Spectral leakage for bin-centered vs non-bin-centered sinusoids, and the effect
of four window functions.

Which research question does this address? RQ5, specifically the competing
explanation for poor compaction. Leakage and DC dominance BOTH inflate the
apparent spread of spectral energy, but for different reasons and with
different remedies. If leakage were the cause of low compaction in the
baseline, windowing would fix it; if the DC offset is the cause, windowing
would not. Running the experiment discriminates between them, which is the
only reason it is here. Windows are not applied simply because it is
conventional to apply them.

Window definitions follow the standard symmetric forms cataloged by
Harris (1978). Note that windowing is NOT applied to the baseline analysis
elsewhere in this study: it alters the signal and would break comparability
with the 2013/2014 results.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import metrics as M
import transforms as T

__all__ = ["WINDOWS", "window", "window_response", "leakage_metrics",
           "leakage_experiment", "window_experiment"]

#: Window functions, periodic form (sym=False convention), by name.
WINDOWS: tuple[str, ...] = ("rectangular", "hann", "hamming", "blackman")


def window(name: str, n: int) -> np.ndarray:
    """Window of length n. Periodic (DFT-symmetric) definitions."""
    k = np.arange(n)
    if name == "rectangular":
        return np.ones(n)
    if name == "hann":
        return 0.5 - 0.5 * np.cos(2 * np.pi * k / n)
    if name == "hamming":
        return 0.54 - 0.46 * np.cos(2 * np.pi * k / n)
    if name == "blackman":
        return (0.42 - 0.5 * np.cos(2 * np.pi * k / n)
                + 0.08 * np.cos(4 * np.pi * k / n))
    raise ValueError(f"unknown window: {name!r}")


def window_response(name: str, n: int, oversample: int = 512
                    ) -> tuple[float, float]:
    """
    Main-lobe half-width (in DFT bins of the length-n transform) and peak
    sidelobe level (dB) for a window, measured from a densely sampled
    frequency response.

    Dense sampling by zero-padding is REQUIRED here. With n = 26 the DFT has
    only 14 unique bins, which cannot resolve a main lobe a few bins wide, let
    alone the sidelobe structure. This is the standard characterization used
    by Harris (1978): pad the window heavily and read the continuous response.
    """
    w = window(name, n)
    padded = np.zeros(n * oversample)
    padded[:n] = w
    mag = np.abs(np.fft.rfft(padded))
    if mag[0] == 0:
        return float("nan"), float("nan")
    # Descend from the DC peak to the first local minimum (the main-lobe null).
    i = 1
    while i < mag.size - 1 and mag[i] < mag[i - 1]:
        i += 1
    halfwidth_bins = i / oversample          # convert samples -> length-n bins
    sidelobe = mag[i:].max() if i < mag.size else 0.0
    peak_sidelobe_db = float(20 * np.log10(sidelobe / mag[0] + 1e-300))
    return float(halfwidth_bins), peak_sidelobe_db


def leakage_metrics(x: np.ndarray, n_peak_bins: int = 2) -> dict[str, float]:
    """
    Leakage descriptors for a real sequence.

    `leakage_energy_fraction` is the share of AC energy lying outside the
    strongest `n_peak_bins` conjugate groups: for an exactly bin-centered tone
    with n_peak_bins=1 this is ~0, and it grows as the tone moves off-bin.

    Main-lobe width and sidelobe level are deliberately NOT reported here:
    with n = 26 the transform has only 14 unique bins, too few to resolve lobe
    structure. Those descriptors belong to `window_response`, which uses dense
    frequency sampling.
    """
    x = np.asarray(x, dtype=float)
    spec = T.dft_direct(x)
    energies = np.abs(spec) ** 2
    ac = energies.copy()
    ac[0] = 0.0
    groups = [g for g in T.conjugate_pairs(x.size) if 0 not in g]
    groups.sort(key=lambda g: -sum(ac[k] for k in g))
    kept = [k for g in groups[:n_peak_bins] for k in g]
    total_ac = float(ac.sum())
    in_peak = float(sum(ac[k] for k in kept))
    return {
        "leakage_energy_fraction": (total_ac - in_peak) / total_ac if total_ac else 0.0,
        "spectral_flatness": float(
            np.exp(np.mean(np.log(ac[ac > 0]))) / np.mean(ac[ac > 0]))
        if np.any(ac > 0) else 0.0,
    }


def leakage_experiment(n: int = 26,
                       offsets: tuple[float, ...] = (3.0, 3.125, 3.25, 3.5)
                       ) -> pd.DataFrame:
    """Leakage as a sinusoid's frequency moves off a DFT bin."""
    rows = []
    t = np.arange(n)
    for off in offsets:
        x = np.cos(2 * np.pi * off * t / n)
        x = x - x.mean()
        m = leakage_metrics(x, n_peak_bins=1)
        m.update({"bin_offset": off,
                  "bin_centered": float(off).is_integer(),
                  "eta_dc": M.dc_energy_share(T.dft_direct(x))})
        rows.append(m)
    return pd.DataFrame(rows)


def window_experiment(n: int = 26, bin_offset: float = 3.5) -> pd.DataFrame:
    """
    Window comparison on the worst-case (half-bin offset) sinusoid.

    `eps_l2_after_2pair_truncation` reconstructs from the two strongest
    conjugate pairs of the WINDOWED signal and compares against the windowed
    signal, so the comparison is internally consistent: windowing changes the
    target, and pretending otherwise would confound leakage with amplitude
    modification.
    """
    from coefficient_selection import (magnitude_ranked_masks,
                                       reconstruct_from_mask)

    t = np.arange(n)
    base = np.cos(2 * np.pi * bin_offset * t / n)
    rows = []
    for name in WINDOWS:
        w = window(name, n)
        xw = base * w
        xw = xw - xw.mean()
        spec = T.dft_direct(xw)
        m = leakage_metrics(xw, n_peak_bins=1)
        halfwidth, sidelobe = window_response(name, n)
        m.update({"mainlobe_halfwidth_bins": halfwidth,
                  "peak_sidelobe_db": sidelobe})
        masks = magnitude_ranked_masks(spec, basis="total")
        mask = masks[min(1, len(masks) - 1)]      # two strongest groups
        x_hat = reconstruct_from_mask(spec, mask)
        m.update({
            "window": name, "bin_offset": bin_offset,
            "coherent_gain": float(w.mean()),
            "n_coeff_2pair": int(mask.sum()),
            "eta_2pair": M.energy_retention_total(spec, mask),
            "eps_l2_after_2pair_truncation": M.relative_l2_error(xw, x_hat),
        })
        rows.append(m)
    return pd.DataFrame(rows)
