#!/usr/bin/env python3
"""
reproduce_all.py
================
Single entry point reproducing the entire study.

    python reproduce_all.py            # full run
    python reproduce_all.py --quick    # fewer noise realizations (smoke test)

Regenerates, in order:
  1. validation gates (fails loudly if any check fails)
  2. the recovered dataset and the full signal corpus
  3. every experiment result
  4. every table (CSV + Markdown)
  5. every figure (PDF + SVG + 600 dpi PNG)
  6. dataset metadata with SHA-256 checksums

Runtime: approximately 1-3 minutes on a modern laptop for the full run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
ROOT = HERE.parent

import coefficient_selection as cs          # noqa: E402
import dct_comparison as DCT                # noqa: E402
import dft_analysis as ANA                  # noqa: E402
import export_manuscript_values as EXPORT   # noqa: E402
import leakage_analysis as LEAK             # noqa: E402
import metrics as M                         # noqa: E402
import noise_experiments as NOISE           # noqa: E402
import plotting as PLOT                     # noqa: E402
import signal_generation as SG              # noqa: E402
import transforms as T                      # noqa: E402
import validation as VAL                    # noqa: E402
from data_recovery import recovery_report   # noqa: E402

DATA = ROOT / "data"
FIGS = ROOT / "figures"
TABS = ROOT / "tables"


def _banner(text: str) -> None:
    print(f"\n{'=' * 74}\n{text}\n{'=' * 74}")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_table(df: pd.DataFrame, stem: str, caption: str) -> None:
    TABS.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABS / f"{stem}.csv", index=False)
    with open(TABS / f"{stem}.md", "w") as fh:
        fh.write(f"**{caption}**\n\n")
        fh.write(df.to_markdown(index=False, floatfmt=".6g"))
        fh.write("\n")
    print(f"  wrote tables/{stem}.csv and .md  ({len(df)} rows)")


def main(quick: bool = False) -> int:
    started = datetime.now(timezone.utc)
    for d in (DATA, FIGS, TABS, DATA / "signal_corpus" / "S6_noise",
              DATA / "spectral_coefficients", DATA / "reconstruction_results",
              DATA / "metrics", DATA / "metadata"):
        d.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- 1
    _banner("STEP 1  VALIDATION GATES")
    checks = VAL.run_all_checks(verbose=True)
    print(f"\n  {len(checks)} checks, all passed.")

    # ---------------------------------------------------------------- 2
    _banner("STEP 2  DATA RECOVERY AND SIGNAL CORPUS")
    rep = recovery_report()
    x0 = np.array(rep["sequence"], dtype=float)
    print(f"  recovered N={rep['n_samples']}  mean={rep['mean']:.4f}  "
          f"sd={rep['std_population']:.4f}  r={rep['r_mean_over_std']:.4f}")
    print(f"  agreement with printed samples: max |diff| = "
          f"{rep['max_abs_residual_after_rounding']:.1e}")
    print(f"  residual before rounding: mean offset {rep['residual_mean_offset']:.6e}, "
          f"DC-rounding prediction {rep['dc_rounding_predicted_offset']:.6e}")

    np.savetxt(DATA / "recovered_data.txt", x0.astype(int), fmt="%d")
    pd.DataFrame({"n": np.arange(x0.size), "x": x0.astype(int)}).to_csv(
        DATA / "recovered_data.csv", index=False)
    with open(DATA / "metadata" / "recovery_report.json", "w") as fh:
        json.dump(rep, fh, indent=2)

    # Clear previously generated corpus files first. Signal display names feed
    # the filenames, so renaming a signal used to leave an orphan behind (the
    # British/American spelling pass once left S1_bin-centred.csv beside
    # S1_bin-centered.csv). Regenerating into a clean directory makes the
    # written set authoritative.
    for stale in (DATA / "signal_corpus").glob("S*_*.csv"):
        stale.unlink()
    for stale in (DATA / "signal_corpus" / "S6_noise").glob("*.csv"):
        stale.unlink()

    corpus = SG.build_corpus()
    for sig in corpus:
        pd.DataFrame({"n": np.arange(sig.n), "x": sig.samples}).to_csv(
            DATA / "signal_corpus" / f"{sig.ident}_{sig.name.split()[0].lower()}.csv",
            index=False)
    # Offset sweep (Experiment A input).
    sweep_rows = []
    for sig in SG.offset_sweep():
        for n_, v in enumerate(sig.samples):
            sweep_rows.append({"r": sig.params["r"], "n": n_, "x": v})
    pd.DataFrame(sweep_rows).to_csv(
        DATA / "signal_corpus" / "S3_offset_sweep.csv", index=False)
    print(f"  corpus written: {[s.ident for s in corpus]} + S3 sweep")

    spec0 = T.dft_direct(x0)
    pd.DataFrame({"k": np.arange(x0.size), "re": spec0.real, "im": spec0.imag,
                  "magnitude": np.abs(spec0)}).to_csv(
        DATA / "spectral_coefficients" / "S0_unitary_dft.csv", index=False)
    legacy = T.legacy_transform_1314(x0)
    pd.DataFrame({"k": np.arange(x0.size), "re": legacy.real,
                  "im": legacy.imag}).to_csv(
        DATA / "spectral_coefficients" / "S0_legacy_1314_convention.csv", index=False)

    # ---------------------------------------------------------------- 3
    _banner("STEP 3  EXPERIMENTS")

    print("\n[3.1] Historical verification")
    hist = pd.DataFrame(VAL.historical_verification_table())
    print(f"  {(hist['status'] == 'verified').sum()}/{len(hist)} historical "
          f"quantities verified")

    print("\n[3.2] Experiment A - mean-to-std sweep")
    exp_a = ANA.experiment_a_dc_sweep()
    print(f"  max |measured - theory| = {exp_a['abs_error'].max():.3e}")

    print("\n[3.3] Corpus summary and retention thresholds")
    corpus_df = ANA.corpus_analysis(corpus)
    thresholds = ANA.retention_thresholds(corpus)

    print("\n[3.4] Selection-strategy curves")
    selection = ANA.selection_comparison(corpus)

    print("\n[3.5] DFT vs DCT-II")
    dct_curves = DCT.compare_transforms(corpus, mean_removed=True)
    dct_thresholds = DCT.threshold_comparison(corpus)

    print("\n[3.6] Leakage and windows")
    leakage = LEAK.leakage_experiment()
    windows = LEAK.window_experiment()

    print("\n[3.7] Noise robustness")
    n_real = 10 if quick else NOISE.N_REALIZATIONS
    noise_raw = NOISE.noise_experiment(n_realizations=n_real)
    noise_summary = NOISE.summarize_noise(noise_raw)
    noise_raw.to_csv(DATA / "signal_corpus" / "S6_noise" / "per_realization.csv",
                     index=False)
    print(f"  {len(noise_raw)} realization-level records "
          f"({n_real} per SNR level)")

    print("\n[3.8] Numerical precision sweep")
    precision = pd.DataFrame(VAL.precision_sweep(x0))
    agree = VAL.dft_fft_agreement(x0)
    print(f"  direct DFT vs FFT: max abs {agree['max_abs_diff']:.3e}, "
          f"max rel {agree['max_rel_diff']:.3e}")

    # Reference modeling error: the historical 11-coefficient operating point.
    mask11 = cs.lowpass_mask(x0.size, 5)
    rec11 = cs.reconstruct_from_mask(spec0, mask11)
    modeling_error = M.relative_l2_error(x0, rec11)

    # ---------------------------------------------------------------- 4
    _banner("STEP 4  TABLES")
    _write_table(pd.DataFrame([{
        "field": k, "value": (json.dumps(v) if isinstance(v, list) else v)}
        for k, v in rep.items()]),
        "table01_recovered_dataset_summary",
        "Table 1. Recovered dataset summary and recovery validation evidence.")
    _write_table(hist, "table02_historical_verification",
                 "Table 2. Independent verification of the 2013/2014 results.")
    _write_table(pd.DataFrame([{
        "id": s.ident, "name": s.name, "provenance": s.provenance, "N": s.n,
        "mean": s.mean, "std": s.std,
        "r": s.r if np.isfinite(s.r) else None,
        "description": s.description, "params": json.dumps(s.params)}
        for s in corpus]),
        "table03_signal_corpus", "Table 3. Signal corpus definitions.")
    _write_table(corpus_df, "table04_corpus_statistics",
                 "Table 4. Corpus statistics and DC energy share.")
    _write_table(exp_a, "table05_experiment_a_dc_sweep",
                 "Table 5. Experiment A: measured vs analytical DC energy share.")
    _write_table(thresholds, "table06_energy_thresholds",
                 "Table 6. Coefficients required per energy threshold, both bases.")
    _write_table(selection, "table07_selection_curves",
                 "Table 7. Retention curves for all strategy/basis combinations.")
    _write_table(dct_thresholds, "table08_dft_vs_dct",
                 "Table 8. DFT vs DCT-II coefficient counts at fixed thresholds.")
    _write_table(pd.concat([leakage.assign(experiment="leakage"),
                            windows.assign(experiment="windows")],
                           ignore_index=True),
                 "table09_leakage_and_windows",
                 "Table 9. Spectral leakage and window characteristics.")
    _write_table(noise_summary, "table10_noise_summary",
                 f"Table 10. Noise robustness, mean +/- SD and 95% CI, n={n_real} per SNR.")
    _write_table(precision, "table11_numerical_precision",
                 "Table 11. Parseval discrepancy vs transform length and precision.")
    _write_table(pd.DataFrame([{"check": c.name, "measured": c.measured,
                                "tolerance": c.tolerance,
                                "passed": c.passed, "note": c.note}
                               for c in checks]),
                 "table12_validation_checks",
                 "Table 12. Numerical validation gates.")

    for name, df in (("experiment_a", exp_a), ("thresholds", thresholds),
                     ("selection", selection), ("noise_summary", noise_summary)):
        df.to_csv(DATA / "metrics" / f"{name}.csv", index=False)
    pd.DataFrame({"n": np.arange(x0.size), "x": x0,
                  "recon_11coef": rec11}).to_csv(
        DATA / "reconstruction_results" / "S0_11coefficient.csv", index=False)

    # ---------------------------------------------------------------- 5
    _banner("STEP 5  FIGURES")
    ctx = {
        "S0": x0, "exp_a": exp_a, "selection": selection, "dct": dct_curves,
        "leakage": leakage, "windows": windows,
        "noise_summary": noise_summary, "precision": precision,
        "modeling_error_reference": modeling_error,
    }
    written = PLOT.build_all_figures(ctx, FIGS)
    for name in written:
        print(f"  {name}: pdf + svg + png(600dpi)")

    import figure_qc as FQC
    problems = FQC.run_figure_qc(ctx, FIGS, verbose=True)
    if problems:
        raise AssertionError(
            f"figure QC failed with {len(problems)} problem(s):\n" +
            "\n".join(f"  - {p}" for p in problems))

    # ---------------------------------------------------------------- 5b
    _banner("STEP 5b  MANUSCRIPT VALUES")
    vals = EXPORT.export(noise_summary, ROOT / "manuscript" / "manuscript_values.json")
    print(f"  exported {len(vals)} values; all {len(EXPORT.REQUIRED_KEYS)} "
          "required keys present and finite")

    # ---------------------------------------------------------------- 6
    _banner("STEP 6  METADATA AND CHECKSUMS")
    files = sorted(p for p in ROOT.rglob("*")
                   if p.is_file() and p.suffix in
                   {".csv", ".txt", ".png", ".pdf", ".svg", ".py", ".json",
                    ".md", ".docx", ".toml", ".yml"}
                   and not any(part in {"__pycache__", ".ipynb_checkpoints",
                                        ".pytest_cache", ".git", ".venv"}
                               for part in p.parts))
    manifest = [{"path": str(p.relative_to(ROOT)),
                 "bytes": p.stat().st_size, "sha256": _sha256(p)} for p in files]
    pd.DataFrame(manifest).to_csv(ROOT / "documentation" / "FILE_MANIFEST.csv",
                                  index=False)

    meta = {
        "dataset_name": "DFT spectral-energy retention study",
        "generated_utc": started.isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "matplotlib": PLOT.matplotlib.__version__,
        "platform": platform.platform(),
        "master_seed": SG.MASTER_SEED,
        "n_noise_realizations": n_real,
        "N_baseline": int(x0.size),
        "units": "dimensionless; physical units of S0 are unknown",
        "sampling_rate": "unknown - not stated in the 2013/2014 source",
        "provenance": {
            "recovered_historical": ["data/recovered_data.txt",
                                     "data/recovered_data.csv",
                                     "data/signal_corpus/S0_recovered.csv"],
            "synthetic_deterministic": ["S1", "S2", "S3", "S5",
                                        "data/signal_corpus/S3_offset_sweep.csv"],
            "synthetic_seeded": ["S4"],
            "stochastic_seeded": ["S6 (data/signal_corpus/S6_noise/)"],
        },
        "n_files_checksummed": len(manifest),
    }
    with open(DATA / "metadata" / "dataset_metadata.json", "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"  {len(manifest)} files checksummed (SHA-256)")

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    _banner(f"COMPLETE in {elapsed:.1f} s")
    print("  Key results:")
    print(f"    DC energy share of S0            : {M.dc_energy_share(spec0)*100:.3f} %")
    print(f"    eta_total at 11 coefficients     : "
          f"{M.energy_retention_total(spec0, mask11)*100:.3f} %")
    print(f"    eps_L2 at that operating point   : {modeling_error:.4f}")
    print(f"    Experiment A max theory error    : {exp_a['abs_error'].max():.3e}")
    print(f"    Parseval eps_P (float64, N=26)   : "
          f"{M.parseval_discrepancy(x0, spec0):.3e}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true",
                    help="10 noise realizations instead of 100 (smoke test)")
    raise SystemExit(main(**vars(ap.parse_args())))
