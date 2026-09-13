"""
dct_comparison.py
=================
Controlled DFT vs orthonormal DCT-II comparison.

Purpose (RQ6). The transform-coding literature established decades ago that
the DCT compacts better than the DFT for correlated sources, approaching the
KLT [Ahmed/Natarajan/Rao 1974]. Nothing here rediscovers that. The comparison
is included because it isolates a competing explanation: if the baseline
signal reconstructs poorly under coefficient truncation, is that because the
energy metric is misleading, or merely because the DFT is the wrong transform?
Running both under identical evaluation conditions separates the two.

Both transforms are orthonormal, so retained-energy fractions are directly
comparable and Parseval holds in both domains.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import metrics as M
import transforms as T
from signal_generation import Signal, build_corpus

__all__ = ["dct_retention_curve", "compare_transforms", "threshold_comparison"]


def _dct_masks(coeffs: np.ndarray) -> list[np.ndarray]:
    """Nested masks adding DCT coefficients in descending magnitude order."""
    order = np.argsort(-np.abs(coeffs))
    masks, mask = [], np.zeros(coeffs.size, dtype=bool)
    for idx in order:
        mask = mask.copy()
        mask[idx] = True
        masks.append(mask)
    return masks


def dct_retention_curve(x: np.ndarray, mean_removed: bool = False) -> pd.DataFrame:
    """Retained energy and reconstruction error vs coefficient count, DCT-II."""
    x = np.asarray(x, dtype=float)
    ref = x - x.mean() if mean_removed else x
    coeffs = T.dct2_ortho(ref)
    total = float(np.sum(coeffs ** 2))
    rows = []
    for mask in _dct_masks(coeffs):
        x_hat = T.idct2_ortho(coeffs * mask)
        rows.append({
            "transform": "DCT-II", "n_coeff": int(mask.sum()),
            "eta": float(np.sum(coeffs[mask] ** 2) / total),
            "eps_l2": M.relative_l2_error(ref, x_hat),
            "rmse": M.rmse(ref, x_hat),
        })
    return pd.DataFrame(rows)


def _dft_magnitude_curve(x: np.ndarray, mean_removed: bool = False) -> pd.DataFrame:
    """DFT counterpart: conjugate groups added in descending energy order."""
    from coefficient_selection import magnitude_ranked_masks, reconstruct_from_mask

    x = np.asarray(x, dtype=float)
    ref = x - x.mean() if mean_removed else x
    spec = T.dft_direct(ref)
    total = float(np.sum(np.abs(spec) ** 2))
    rows = []
    for mask in magnitude_ranked_masks(spec, basis="total"):
        x_hat = reconstruct_from_mask(spec, mask)
        rows.append({
            "transform": "DFT", "n_coeff": int(mask.sum()),
            "eta": float(np.sum(np.abs(spec[mask]) ** 2) / total),
            "eps_l2": M.relative_l2_error(ref, x_hat),
            "rmse": M.rmse(ref, x_hat),
        })
    return pd.DataFrame(rows)


def compare_transforms(corpus: list[Signal] | None = None,
                       mean_removed: bool = True) -> pd.DataFrame:
    """Compaction curves for both transforms across the corpus."""
    corpus = corpus or build_corpus()
    frames = []
    for sig in corpus:
        if float(np.sum((sig.samples - sig.samples.mean()) ** 2)) <= 1e-20:
            continue
        for frame in (_dft_magnitude_curve(sig.samples, mean_removed),
                      dct_retention_curve(sig.samples, mean_removed)):
            frame = frame.copy()
            frame["id"] = sig.ident
            frame["mean_removed"] = mean_removed
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def threshold_comparison(corpus: list[Signal] | None = None,
                         thresholds: tuple[float, ...] = (0.90, 0.95, 0.99),
                         mean_removed: bool = True) -> pd.DataFrame:
    """Coefficients needed to reach each threshold, per transform, per signal."""
    curves = compare_transforms(corpus, mean_removed)
    rows = []
    for (sig_id, transform), grp in curves.groupby(["id", "transform"]):
        grp = grp.sort_values("n_coeff")
        for thr in thresholds:
            hit = grp[grp["eta"] >= thr - 1e-12]
            if hit.empty:
                continue
            first = hit.iloc[0]
            rows.append({
                "id": sig_id, "transform": transform, "threshold": thr,
                "n_coeff": int(first["n_coeff"]), "eps_l2": float(first["eps_l2"]),
                "mean_removed": mean_removed,
            })
    return pd.DataFrame(rows).sort_values(["id", "threshold", "transform"])
