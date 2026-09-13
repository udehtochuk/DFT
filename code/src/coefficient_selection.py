"""
coefficient_selection.py
========================
Three coefficient-retention strategies, all operating on whole conjugate
groups so that every reconstruction is real-valued.

  Method 1  symmetric low-pass    {0..k} U {N-k..N-1}   (the 2013/2014 scheme)
  Method 2  largest-magnitude     rank groups by |X[k]|
  Method 3  cumulative-energy     add groups by descending energy until a
                                  threshold on a specified energy basis is met

The `basis` argument ("total" or "ac") controls BOTH which energy the
threshold is measured against and whether the DC group is eligible for
selection. On the AC basis the DC bin is excluded from selection, because the
question being asked is how well the *varying* component is represented.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from transforms import conjugate_pairs, idft_direct

__all__ = [
    "lowpass_mask", "magnitude_ranked_masks", "lowpass_masks",
    "cumulative_energy_mask", "reconstruct_from_mask", "retention_curve",
]


def _group_energy(spectrum: NDArray, group: tuple[int, ...]) -> float:
    return float(sum(abs(spectrum[k]) ** 2 for k in group))


def lowpass_mask(n_samples: int, k: int) -> NDArray[np.bool_]:
    """Retain {0..k} U {N-k..N-1}. k=0 retains DC only."""
    if not 0 <= k < n_samples:
        raise ValueError(f"k must lie in [0, {n_samples})")
    mask = np.zeros(n_samples, dtype=bool)
    mask[0:k + 1] = True
    if k > 0:
        mask[n_samples - k:] = True
    return mask


def lowpass_masks(spectrum: NDArray, basis: str = "total") -> list[NDArray[np.bool_]]:
    """Nested low-pass masks of increasing k, as a retention sequence."""
    n = np.asarray(spectrum).size
    masks = []
    for k in range(0, n // 2 + 1):
        m = lowpass_mask(n, k)
        if basis == "ac":
            m = m.copy()
            m[0] = False
            if not m.any():
                continue
        masks.append(m)
    return masks


def magnitude_ranked_masks(spectrum: NDArray,
                           basis: str = "total") -> list[NDArray[np.bool_]]:
    """Nested masks adding conjugate groups in descending |X[k]| order."""
    spectrum = np.asarray(spectrum)
    n = spectrum.size
    groups = conjugate_pairs(n)
    if basis == "ac":
        groups = [g for g in groups if 0 not in g]
    elif basis != "total":
        raise ValueError("basis must be 'total' or 'ac'")
    groups = sorted(groups, key=lambda g: -_group_energy(spectrum, g))

    masks, mask = [], np.zeros(n, dtype=bool)
    for g in groups:
        mask = mask.copy()
        mask[list(g)] = True
        masks.append(mask)
    return masks


def cumulative_energy_mask(spectrum: NDArray, threshold: float,
                           basis: str = "total") -> tuple[NDArray[np.bool_], float]:
    """
    Smallest descending-energy set of conjugate groups reaching `threshold`
    (a fraction in [0, 1]) of the energy on `basis`.

    Returns (mask, achieved_fraction). If the threshold cannot be reached
    (only possible through floating-point shortfall at 1.0), all eligible
    groups are returned.
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must lie in [0, 1]")
    spectrum = np.asarray(spectrum)
    n = spectrum.size
    energies = np.abs(spectrum) ** 2

    groups = conjugate_pairs(n)
    if basis == "ac":
        groups = [g for g in groups if 0 not in g]
        denom = float(energies.sum() - energies[0])
    elif basis == "total":
        denom = float(energies.sum())
    else:
        raise ValueError("basis must be 'total' or 'ac'")
    if denom <= 0:
        raise ZeroDivisionError("no energy available on the requested basis")

    groups = sorted(groups, key=lambda g: -_group_energy(spectrum, g))
    mask = np.zeros(n, dtype=bool)
    acc = 0.0
    for g in groups:
        if acc / denom >= threshold - 1e-15:
            break
        mask[list(g)] = True
        acc += _group_energy(spectrum, g)
    return mask, acc / denom


def reconstruct_from_mask(spectrum: NDArray, mask: NDArray,
                          add_back_mean: float | None = None) -> NDArray[np.float64]:
    """
    Inverse-transform the masked spectrum.

    `add_back_mean` is for AC-basis work: the fluctuation is reconstructed from
    non-DC bins and the (exactly known, cheaply stored) mean is added back.
    Returns the real part; the imaginary residual is checked to be negligible.
    """
    spectrum, mask = np.asarray(spectrum), np.asarray(mask, dtype=bool)
    out = idft_direct(spectrum * mask)
    if np.max(np.abs(out.imag)) > 1e-6 * max(1.0, np.max(np.abs(out.real))):
        raise AssertionError(
            "reconstruction has a non-negligible imaginary part: the retention "
            "set is not conjugate-symmetric")
    real = out.real
    return real + add_back_mean if add_back_mean is not None else real


def retention_curve(x: NDArray, spectrum: NDArray, strategy: str,
                    basis: str = "total") -> list[dict[str, float]]:
    """
    Full retention curve for one strategy/basis combination.

    On the AC basis, x is compared against the mean-removed signal and the
    reconstruction uses only non-DC bins.
    """
    from metrics import summarize_reconstruction

    x = np.asarray(x, dtype=float)
    if strategy == "lowpass":
        masks = lowpass_masks(spectrum, basis)
    elif strategy == "magnitude":
        masks = magnitude_ranked_masks(spectrum, basis)
    else:
        raise ValueError("strategy must be 'lowpass' or 'magnitude'")

    reference = x - x.mean() if basis == "ac" else x
    rows = []
    for m in masks:
        x_hat = reconstruct_from_mask(spectrum, m)
        row = summarize_reconstruction(reference, x_hat, spectrum, m)
        row["strategy"], row["basis"] = strategy, basis
        rows.append(row)
    return rows
