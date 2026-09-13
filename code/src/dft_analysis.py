"""
dft_analysis.py
===============
Experiment A (mean-to-standard-deviation sweep) and the corpus-wide
energy/fidelity analysis.

Experiment A is the study's central controlled test. The AC content of the
signal is held fixed and only the constant offset is varied, so that the DC
bin is the sole quantity that changes. Any variation in eta_total is therefore
attributable to the offset alone, and can be compared against the analytical
prediction eta_DC = r^2/(1+r^2).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import coefficient_selection as cs
import metrics as M
import transforms as T
from signal_generation import (R_SWEEP_VALUES, Signal, build_corpus,
                               offset_sweep)

__all__ = ["experiment_a_dc_sweep", "corpus_analysis", "retention_thresholds",
           "selection_comparison", "ENERGY_THRESHOLDS"]

#: Energy thresholds used for the coefficient-count tables.
ENERGY_THRESHOLDS: tuple[float, ...] = (0.50, 0.75, 0.80, 0.90, 0.95,
                                        0.99, 0.995, 0.999)


def experiment_a_dc_sweep(r_values: tuple[float, ...] = R_SWEEP_VALUES,
                          n: int = 26) -> pd.DataFrame:
    """
    Experiment A. For each r: measured DC share, analytical prediction,
    absolute and relative error, plus the eta_total / eps_L2 pair obtained by
    retaining a fixed number of coefficients.

    The fixed-budget columns test H2 directly: with the AC content held
    constant, eps_L2 on the fluctuation cannot change with r, while eta_total
    rises toward 1. Any gap between them is the confound.
    """
    rows = []
    for sig in offset_sweep(n=n, r_values=r_values):
        r = sig.params["r"]
        spec = T.dft_direct(sig.samples)
        measured = M.dc_energy_share(spec)
        predicted = M.dc_share_theoretical(r)

        # Fixed budget of 7 coefficients (DC + 3 conjugate pairs).
        mask = cs.lowpass_mask(n, 3)
        x_hat = cs.reconstruct_from_mask(spec, mask)
        ac_ref = sig.samples - sig.samples.mean()
        mask_ac = mask.copy(); mask_ac[0] = False
        x_hat_ac = cs.reconstruct_from_mask(spec, mask_ac)

        rows.append({
            "r": r,
            "mean": sig.mean, "std": sig.std,
            "eta_dc_measured": measured,
            "eta_dc_predicted": predicted,
            "abs_error": abs(measured - predicted),
            "rel_error": abs(measured - predicted) / predicted if predicted else np.nan,
            "eta_total_7coef": M.energy_retention_total(spec, mask),
            "eta_ac_7coef": M.energy_retention_ac(spec, mask),
            "eps_l2_full_7coef": M.relative_l2_error(sig.samples, x_hat),
            "eps_l2_ac_7coef": M.relative_l2_error(ac_ref, x_hat_ac),
        })
    return pd.DataFrame(rows)


def corpus_analysis(corpus: list[Signal] | None = None) -> pd.DataFrame:
    """Descriptive statistics and DC share for every deterministic corpus member."""
    corpus = corpus or build_corpus()
    rows = []
    for sig in corpus:
        spec = T.dft_direct(sig.samples)
        rows.append({
            "id": sig.ident, "name": sig.name, "provenance": sig.provenance,
            "N": sig.n, "mean": sig.mean, "std": sig.std,
            "r": sig.r if np.isfinite(sig.r) else np.nan,
            "energy": M.total_energy(sig.samples),
            "eta_dc": M.dc_energy_share(spec),
            "eps_parseval": M.parseval_discrepancy(sig.samples, spec),
        })
    return pd.DataFrame(rows)


def retention_thresholds(corpus: list[Signal] | None = None,
                         thresholds: tuple[float, ...] = ENERGY_THRESHOLDS
                         ) -> pd.DataFrame:
    """
    Coefficients required to reach each energy threshold, on both bases, with
    the reconstruction error actually achieved at that point.

    The point of the table is the pairing: a threshold on its own is an
    accounting statement, and only the accompanying eps_L2 makes it a fidelity
    statement.
    """
    corpus = corpus or build_corpus()
    rows = []
    for sig in corpus:
        spec = T.dft_direct(sig.samples)
        ac_ref = sig.samples - sig.samples.mean()
        has_ac = float(np.sum(ac_ref ** 2)) > 1e-20
        for basis in ("total", "ac"):
            if basis == "ac" and not has_ac:
                continue
            for thr in thresholds:
                mask, achieved = cs.cumulative_energy_mask(spec, thr, basis=basis)
                if mask.sum() == 0:
                    continue
                x_hat = cs.reconstruct_from_mask(spec, mask)
                ref = ac_ref if basis == "ac" else sig.samples
                rows.append({
                    "id": sig.ident, "basis": basis, "threshold": thr,
                    "achieved": achieved, "n_coeff": int(mask.sum()),
                    "coeff_ratio": M.compression_ratio(mask),
                    "eps_l2": M.relative_l2_error(ref, x_hat),
                    "rmse": M.rmse(ref, x_hat),
                    "snr_db": M.reconstruction_snr_db(ref, x_hat),
                })
    return pd.DataFrame(rows)


def selection_comparison(corpus: list[Signal] | None = None) -> pd.DataFrame:
    """Full retention curves: {lowpass, magnitude} x {total, ac} for every signal."""
    corpus = corpus or build_corpus()
    rows = []
    for sig in corpus:
        spec = T.dft_direct(sig.samples)
        has_ac = float(np.sum((sig.samples - sig.samples.mean()) ** 2)) > 1e-20
        for strategy in ("lowpass", "magnitude"):
            for basis in ("total", "ac"):
                if basis == "ac" and not has_ac:
                    continue
                for row in cs.retention_curve(sig.samples, spec, strategy, basis):
                    row["id"] = sig.ident
                    rows.append(row)
    return pd.DataFrame(rows)
