"""
noise_experiments.py
====================
S6: the recovered baseline plus additive zero-mean Gaussian noise at
SNR = 30, 20, 10, 0 dB, with >= 100 independent realizations per level.

Statistical policy (stated so it can be checked):
  * Descriptive statistics only -- mean, standard deviation, and a 95%
    confidence interval for the mean via the normal approximation
    (n = 100 per level, so the CLT approximation is reasonable for these
    smooth functionals).
  * NO inferential test is performed and no p-value is reported, because no
    hypothesis here takes the form of a comparison against a null that a test
    would illuminate. The quantity of interest is an effect size -- the gap
    between eta_total and eps_L2 -- which is reported directly.
  * The CI is a CI for the MEAN across realizations, not a prediction
    interval for a single realization. It is labeled as such everywhere.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import coefficient_selection as cs
import metrics as M
import transforms as T
from signal_generation import (MASTER_SEED, SNR_LEVELS_DB,
                               make_S6_realizations, make_S0)

__all__ = ["noise_experiment", "summarize_noise", "N_REALIZATIONS"]

N_REALIZATIONS = 100


def noise_experiment(snr_levels: tuple[float, ...] = SNR_LEVELS_DB,
                     n_realizations: int = N_REALIZATIONS,
                     n_coeff_k: int = 5,
                     seed: int = MASTER_SEED) -> pd.DataFrame:
    """
    Per-realization metrics at each SNR, using the low-pass budget of the
    2013/2014 study (k = 5, i.e. 11 coefficients) so the comparison is with
    the historical operating point.

    Errors are measured against the CLEAN baseline: the task is recovering the
    underlying signal, not the noisy observation.
    """
    clean = make_S0().samples
    clean_ac = clean - clean.mean()
    rows = []
    for snr in snr_levels:
        realizations, params = make_S6_realizations(snr, n_realizations, seed)
        for i, noisy in enumerate(realizations):
            spec = T.dft_direct(noisy)
            mask = cs.lowpass_mask(noisy.size, n_coeff_k)
            x_hat = cs.reconstruct_from_mask(spec, mask)
            mask_ac = mask.copy(); mask_ac[0] = False
            x_hat_ac = cs.reconstruct_from_mask(spec, mask_ac)
            rows.append({
                "snr_db": snr, "realization": i,
                "noise_sigma": params["noise_sigma"],
                "eta_dc": M.dc_energy_share(spec),
                "eta_total": M.energy_retention_total(spec, mask),
                "eta_ac": M.energy_retention_ac(spec, mask),
                "eps_l2_vs_clean": M.relative_l2_error(clean, x_hat),
                "eps_l2_ac_vs_clean": M.relative_l2_error(clean_ac, x_hat_ac),
                "rmse_vs_clean": M.rmse(clean, x_hat),
                "eps_parseval": M.parseval_discrepancy(noisy, spec),
            })
    return pd.DataFrame(rows)


def summarize_noise(df: pd.DataFrame, confidence: float = 0.95) -> pd.DataFrame:
    """Mean, SD, n, and a normal-approximation CI for the mean, per SNR."""
    from scipy import stats

    z = float(stats.norm.ppf(0.5 + confidence / 2))
    metrics = ["eta_dc", "eta_total", "eta_ac",
               "eps_l2_vs_clean", "eps_l2_ac_vs_clean", "rmse_vs_clean",
               "eps_parseval"]
    rows = []
    for snr, grp in df.groupby("snr_db"):
        rec = {"snr_db": snr, "n": int(len(grp)), "confidence": confidence}
        for m in metrics:
            vals = grp[m].to_numpy(dtype=float)
            mean = float(vals.mean())
            sd = float(vals.std(ddof=1))
            half = z * sd / np.sqrt(len(vals))
            rec[f"{m}_mean"] = mean
            rec[f"{m}_sd"] = sd
            rec[f"{m}_ci_lo"] = mean - half
            rec[f"{m}_ci_hi"] = mean + half
        rows.append(rec)
    return pd.DataFrame(rows).sort_values("snr_db", ascending=False)
