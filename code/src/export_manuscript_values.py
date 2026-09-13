"""
export_manuscript_values.py
===========================
Exports every numeric value quoted in the manuscript to
`manuscript/manuscript_values.json`, so that no number in the paper is typed by
hand.

Two hard guards, both learned from real failures:

  * Column access is ALWAYS by bracket, never by attribute. `df.transform` is a
    pandas DataFrame *method*, so `df.transform == "DFT"` silently compares a
    bound method to a string and yields all-False. That produced a manuscript
    containing the word "undefined" before it was caught.
  * `REQUIRED_KEYS` lists every key the manuscript build consumes. If any is
    missing or non-finite, this module raises rather than writing a partial
    file.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import coefficient_selection as cs
import dct_comparison as DCT
import dft_analysis as ANA
import leakage_analysis as LEAK
import metrics as M
import transforms as T
import validation as VAL
from data_recovery import recovery_report

__all__ = ["build_values", "export", "REQUIRED_KEYS"]

#: Every key the manuscript build script reads. Kept explicit so a silent
#: export failure becomes a loud one.
REQUIRED_KEYS = (
    "N mean std r sqrt1r2 minv maxv sum energy eta_dc eta_dc_theory ac_energy "
    "eta_total_11 eta_ac_11 eps_l2_11 rmse_11 snr_11 eps_l2_ac_11 "
    "eps_parseval_f64 exp_a_max_err exp_a_eta_total_r16 exp_a_eta_total_r0 "
    "exp_a_eps_ac exp_a_eps_ac_std exp_a_eta_ac_std dft_fft_abs dft_fft_rel "
    "prec_f32_26 prec_f64_26 prec_f32_4096 prec_f64_4096 "
    "residual_mean residual_pred residual_ptp "
    "ac_lowpass_at90 ac_magnitude_at90 ac_lowpass_at95 ac_magnitude_at95 "
    "ac_lowpass_at90_eps ac_magnitude_at90_eps ac_lowpass_at95_eps ac_magnitude_at95_eps "
    "ac_lowpass_at90_eta ac_magnitude_at90_eta ac_lowpass_at95_eta ac_magnitude_at95_eta "
    "leak_35 leak_30 n_checks sequence "
    "dct_S0_DFT_99 dct_S0_DCTII_99 dct_S1_DFT_99 dct_S1_DCTII_99 "
    "dct_S2_DFT_99 dct_S2_DCTII_99 dct_S5_DFT_99 dct_S5_DCTII_99 "
    "win_rectangular_sl win_hann_sl win_hamming_sl win_blackman_sl "
    "win_rectangular_eta win_hamming_eta win_rectangular_eps win_hamming_eps "
    "win_blackman_eps "
    "noise_30_eta_total noise_20_eta_total noise_10_eta_total noise_0_eta_total "
    "noise_30_eta_ac noise_20_eta_ac noise_10_eta_ac noise_0_eta_ac "
    "noise_30_eps_ac noise_20_eps_ac noise_10_eps_ac noise_0_eps_ac"
).split()


def build_values(noise_summary: pd.DataFrame) -> dict:
    """Compute every manuscript value. `noise_summary` comes from the pipeline."""
    rep = recovery_report()
    x = np.array(rep["sequence"], dtype=float)
    n = x.size
    spec = T.dft_direct(x)
    r = float(x.mean() / x.std())
    ac = x - x.mean()

    mask11 = cs.lowpass_mask(n, 5)
    rec11 = cs.reconstruct_from_mask(spec, mask11)
    mask11_ac = mask11.copy()
    mask11_ac[0] = False
    rec11_ac = cs.reconstruct_from_mask(spec, mask11_ac)

    exp_a = ANA.experiment_a_dc_sweep()
    thresholds = ANA.retention_thresholds()
    selection = ANA.selection_comparison()
    dct_thr = DCT.threshold_comparison()
    windows = LEAK.window_experiment()
    leakage = LEAK.leakage_experiment()
    precision = pd.DataFrame(VAL.precision_sweep(x))
    agree = VAL.dft_fft_agreement(x)

    def n_at(basis: str, thr: float, sig: str = "S0") -> list:
        q = thresholds[(thresholds["id"] == sig)
                       & (thresholds["basis"] == basis)
                       & (np.isclose(thresholds["threshold"], thr))]
        if q.empty:
            raise KeyError(f"no threshold row for {sig}/{basis}/{thr}")
        return [int(q["n_coeff"].iloc[0]), float(q["eps_l2"].iloc[0])]

    def prec(n_len: int, kind: str) -> float:
        q = precision[(precision["N"] == n_len) & (precision["precision"] == kind)]
        return float(q["eps_parseval"].iloc[0])

    V: dict = {
        "N": int(n), "mean": float(x.mean()), "std": float(x.std()), "r": r,
        "sqrt1r2": M.l2_scaling_factor(r),
        "minv": float(x.min()), "maxv": float(x.max()), "sum": int(x.sum()),
        "energy": M.total_energy(x), "ac_energy": M.total_energy(ac),
        "eta_dc": M.dc_energy_share(spec),
        "eta_dc_theory": M.dc_share_theoretical(r),
        "eta_total_11": M.energy_retention_total(spec, mask11),
        "eta_ac_11": M.energy_retention_ac(spec, mask11),
        "eps_l2_11": M.relative_l2_error(x, rec11),
        "rmse_11": M.rmse(x, rec11),
        "snr_11": M.reconstruction_snr_db(x, rec11),
        "eps_l2_ac_11": M.relative_l2_error(ac, rec11_ac),
        "eps_parseval_f64": M.parseval_discrepancy(x, spec),
        "exp_a_max_err": float(exp_a["abs_error"].max()),
        "exp_a_eta_total_r0": float(
            exp_a.loc[exp_a["r"] == 0, "eta_total_7coef"].iloc[0]),
        "exp_a_eta_total_r16": float(
            exp_a.loc[exp_a["r"] == 16, "eta_total_7coef"].iloc[0]),
        "exp_a_eps_ac": float(exp_a["eps_l2_ac_7coef"].iloc[0]),
        "exp_a_eps_ac_std": float(exp_a["eps_l2_ac_7coef"].std()),
        "exp_a_eta_ac_std": float(exp_a["eta_ac_7coef"].std()),
        "dft_fft_abs": agree["max_abs_diff"], "dft_fft_rel": agree["max_rel_diff"],
        "prec_f32_26": prec(26, "float32"), "prec_f64_26": prec(26, "float64"),
        "prec_f32_4096": prec(4096, "float32"),
        "prec_f64_4096": prec(4096, "float64"),
        "residual_mean": rep["residual_mean_offset"],
        "residual_pred": rep["dc_rounding_predicted_offset"],
        "residual_ptp": rep["residual_spread_ptp"],
        "sequence": rep["sequence"],
        "n_checks": len(VAL.run_all_checks(verbose=False)),
        "leak_30": float(leakage.loc[np.isclose(leakage["bin_offset"], 3.0),
                                     "leakage_energy_fraction"].iloc[0]),
        "leak_35": float(leakage.loc[np.isclose(leakage["bin_offset"], 3.5),
                                     "leakage_energy_fraction"].iloc[0]),
    }

    for thr in (0.50, 0.80, 0.95, 0.99):
        V[f"n{int(thr * 100)}_total"] = n_at("total", thr)
        V[f"n{int(thr * 100)}_ac"] = n_at("ac", thr)
    V["n90_ac"] = n_at("ac", 0.90)

    # AC-basis strategy comparison at matched thresholds.
    ac_sel = selection[(selection["id"] == "S0") & (selection["basis"] == "ac")]
    for strategy in ("lowpass", "magnitude"):
        q = ac_sel[ac_sel["strategy"] == strategy].sort_values("n_coeff")
        for target in (0.90, 0.95):
            hit = q[q["eta_ac"] >= target]
            if hit.empty:
                raise KeyError(f"no AC row reaching {target} for {strategy}")
            row = hit.iloc[0]
            V[f"ac_{strategy}_at{int(target * 100)}"] = int(row["n_coeff"])
            # Table 3 reports the error achieved for every row, not only the
            # cumulative-threshold ones. Under (7) it is sqrt(1 - eta), so it
            # is always available and there is no reason to leave cells blank.
            V[f"ac_{strategy}_at{int(target * 100)}_eps"] = float(row["eps_l2"])
            V[f"ac_{strategy}_at{int(target * 100)}_eta"] = float(row["eta_ac"])

    # DCT comparison. Bracket access only -- see the module docstring.
    for sig in ("S0", "S1", "S2", "S5"):
        for transform in ("DFT", "DCT-II"):
            q = dct_thr[(dct_thr["id"] == sig)
                        & (dct_thr["transform"] == transform)
                        & (np.isclose(dct_thr["threshold"], 0.99))]
            if q.empty:
                raise KeyError(f"no DCT-comparison row for {sig}/{transform}")
            V[f"dct_{sig}_{transform.replace('-', '')}_99"] = int(
                q["n_coeff"].iloc[0])

    for _, row in windows.iterrows():
        name = row["window"]
        V[f"win_{name}_sl"] = float(row["peak_sidelobe_db"])
        V[f"win_{name}_hw"] = float(row["mainlobe_halfwidth_bins"])
        V[f"win_{name}_eta"] = float(row["eta_2pair"])
        V[f"win_{name}_eps"] = float(row["eps_l2_after_2pair_truncation"])

    for snr in (30, 20, 10, 0):
        q = noise_summary[noise_summary["snr_db"] == snr]
        if q.empty:
            raise KeyError(f"no noise summary row for SNR {snr}")
        row = q.iloc[0]
        V[f"noise_{snr}_eta_total"] = float(row["eta_total_mean"])
        V[f"noise_{snr}_eta_ac"] = float(row["eta_ac_mean"])
        V[f"noise_{snr}_eps_ac"] = float(row["eps_l2_ac_vs_clean_mean"])
        V[f"noise_{snr}_eps_ac_lo"] = float(row["eps_l2_ac_vs_clean_ci_lo"])
        V[f"noise_{snr}_eps_ac_hi"] = float(row["eps_l2_ac_vs_clean_ci_hi"])

    _validate(V)
    return V


def _validate(V: dict) -> None:
    """Fail loudly on a missing or non-finite value."""
    missing = [k for k in REQUIRED_KEYS if k not in V]
    if missing:
        raise AssertionError(
            "manuscript value export is incomplete; the manuscript would "
            f"contain 'undefined'. Missing keys: {missing}")
    bad = [k for k, v in V.items()
           if isinstance(v, float) and not math.isfinite(v)]
    if bad:
        raise AssertionError(f"non-finite manuscript values: {bad}")


def export(noise_summary: pd.DataFrame, out_path: Path) -> dict:
    """Compute, validate and write the manuscript values."""
    V = build_values(noise_summary)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(V, fh, indent=1, sort_keys=True)
    return V
