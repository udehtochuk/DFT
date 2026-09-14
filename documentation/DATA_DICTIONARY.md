# Data Dictionary

Every field in every released data file. Units are dimensionless unless stated;
the physical units of the recovered baseline are **unknown** (see
`research_integrity_statement.md`, §3).

## Provenance codes

| Code | Meaning |
|---|---|
| **R** | Recovered historical data, reconstructed from the 2013/2014 publication |
| **SD** | Synthetic, deterministic, no randomness involved |
| **SS** | Synthetic, seeded, deterministic given master seed 20260826 |
| **ST** | Stochastic, seeded, repeated random realizations, reproducible |
| **C** | Computed from the above |

---

## `data/recovered_data.txt`, **R**
Plain text, one integer per line, 26 lines. The recovered baseline sequence.

## `data/recovered_data.csv`, **R**

| Field | Type | Units | Description |
|---|---|---|---|
| `n` | int |, | Sample index, 0…25 |
| `x` | int | unknown | Sample value. Physical units unknown. |

## `data/signal_corpus/S*_*.csv`, **SD** (S4: **SS**)

| Field | Type | Description |
|---|---|---|
| `n` | int | Sample index |
| `x` | float | Sample value |

## `data/signal_corpus/S3_offset_sweep.csv`, **SD**

| Field | Type | Description |
|---|---|---|
| `r` | float | Target mean-to-standard-deviation ratio μ/σ |
| `n` | int | Sample index |
| `x` | float | Sample value. AC content identical across all `r`; only the offset differs. |

## `data/signal_corpus/S6_noise/per_realization.csv`, **ST**

| Field | Type | Units | Description |
|---|---|---|---|
| `snr_db` | float | dB | Input SNR, defined on the **AC** power of the baseline |
| `realization` | int |, | Realization index, 0…99 |
| `noise_sigma` | float | signal units | Standard deviation of the added noise |
| `eta_dc` | float | ratio | DC energy share of the noisy realization |
| `eta_total` | float | ratio | Retained energy, total basis, 11-coefficient budget |
| `eta_ac` | float | ratio | Retained energy, AC basis, same budget |
| `eps_l2_vs_clean` | float | ratio | Relative L2 error against the **clean** baseline |
| `eps_l2_ac_vs_clean` | float | ratio | Relative L2 error on the fluctuation, against clean |
| `rmse_vs_clean` | float | signal units | Root-mean-square error against clean |
| `eps_parseval` | float | ratio | Numerical Parseval discrepancy (diagnostic only) |

## `data/spectral_coefficients/S0_unitary_dft.csv`, **C**

| Field | Type | Description |
|---|---|---|
| `k` | int | Frequency bin, 0…25 (normalized; no Hz axis, sampling rate unknown) |
| `re`, `im` | float | Real and imaginary parts under the unitary convention |
| `magnitude` | float | \|X[k]\| |

## `data/spectral_coefficients/S0_legacy_1314_convention.csv`, **C**
Same fields, computed under the **2013/2014 convention** (positive analysis
exponent). Provided solely so the historical coefficient tables can be checked.
Satisfies `legacy[k] == X[(N−k) mod N]`. **Do not use for new analysis.**

## `data/reconstruction_results/S0_11coefficient.csv`, **C**

| Field | Type | Description |
|---|---|---|
| `n` | int | Sample index |
| `x` | float | Original sample |
| `recon_11coef` | float | Reconstruction from 11 coefficients (the historical operating point) |

---

## Shared metric fields (tables 05–08, `data/metrics/*.csv`), **C**

| Field | Units | Definition |
|---|---|---|
| `r` | ratio | μ/σ, mean-to-standard-deviation ratio |
| `eta_dc` | ratio | \|X[0]\|² / E |
| `eta_dc_measured` / `eta_dc_predicted` | ratio | Measured against r²/(1+r²) |
| `abs_error` / `rel_error` | ratio | Deviation of measurement from prediction |
| `eta_total` | ratio | Retained energy / total energy |
| `eta_ac` | ratio | Retained non-DC energy / total non-DC energy |
| `eps_l2` | ratio | ‖x − x̂‖₂ / ‖x‖₂, dimensionless, scale-invariant |
| `rmse` | signal units | Root-mean-square error |
| `snr_db` | dB | 10·log₁₀(Σx² / Σ(x−x̂)²) |
| `n_coeff` | count | Retained coefficients |
| `coeff_ratio` | ratio | Retained / total coefficients |
| `basis` |, | `total` or `ac` |
| `strategy` |, | `lowpass` or `magnitude` |
| `threshold` / `achieved` | ratio | Requested and attained energy fraction |
| `max_imag` |, | Largest imaginary residual; must be negligible |
| `eps_parseval` | ratio | \|E_time − E_freq\| / E_time. **Numerical diagnostic only**, never evidence about Parseval's identity, which is analytic. |

## Leakage and window fields (table 09), **C**

| Field | Units | Definition |
|---|---|---|
| `bin_offset` | bins | Sinusoid frequency in DFT bins; integer = bin-centered |
| `leakage_energy_fraction` | ratio | AC energy outside the strongest conjugate pair |
| `spectral_flatness` | ratio | Geometric / arithmetic mean of AC bin energies |
| `mainlobe_halfwidth_bins` | bins | From a densely zero-padded response (N=26 cannot resolve it) |
| `peak_sidelobe_db` | dB | Peak sidelobe relative to the main lobe |
| `coherent_gain` | ratio | Mean of the window |
| `eta_2pair` | ratio | Retained energy at a 4-coefficient budget |
| `eps_l2_after_2pair_truncation` | ratio | Error at that budget, against the **windowed** signal |

## Noise summary fields (table 10), **C**
For each metric `m`: `m_mean`, `m_sd`, `m_ci_lo`, `m_ci_hi`. Intervals are 95%
confidence intervals **for the mean across realizations**, by normal
approximation with n = 100, *not* prediction intervals for a single
realization.

## Validation fields (table 12), **C**

| Field | Description |
|---|---|
| `check` | Gate name |
| `measured` | Measured deviation |
| `tolerance` | Fixed threshold. **Never relaxed to make a check pass.** |
| `passed` | Boolean; the pipeline aborts if any is false |
| `note` | Explanatory note where the gate needs one |

---

## `data/metadata/dataset_metadata.json`
Dataset name, UTC generation timestamp, Python/NumPy/pandas/Matplotlib versions,
platform, master seed, realization count, N, units statement, sampling-rate
statement, provenance map, and the number of checksummed files.

## `data/metadata/recovery_report.json`
Full recovery-validation evidence: residual statistics against the printed
samples, the DC-rounding prediction, distance to integers, Hermitian and Nyquist
consistency of the printed coefficients, and summary statistics.

## `documentation/FILE_MANIFEST.csv`
Relative path, size in bytes, and SHA-256 for every released file.
