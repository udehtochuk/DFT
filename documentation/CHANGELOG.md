# Changelog

## 1.0.0, 26 August 2026

First complete release: manuscript, code, tests, data, figures,
tables, supplementary material and documentation.

### Findings relative to the preceding informal forensic review

The review was used as a specification, not as a source of results. Everything
was recomputed from scratch, and three of its statements did not survive.

- **Added: the redundancy identity.** ε_L2 = √(1 − η) holds exactly for any
  orthonormal transform, verified against 324 independent retention
  measurements (max deviation 1.0 × 10⁻¹⁴). **This invalidates the review's
  central recommendation.** The review advised reporting a reconstruction error
  alongside every energy figure; on the same basis those are the same number
  under a monotone transformation. The corrected recommendation is to report
  the **basis**, or equivalently r.
- **Added: the basis-conversion and error-scaling laws.**
  1 − η_total = (1 − η_AC)(1 − η_DC) = (1 − η_AC)/(1 + r²), and
  ε_full = ε_AC/√(1 + r²). Both verified to ~2 × 10⁻¹⁶. Together they make r a
  sufficient statistic for converting between reporting conventions.
- **Corrected: the recovery residual is not a constant offset.** The review
  described it as constant at −0.0625. It is not: mean −0.0627394 against
  −0.0627497 predicted from DC rounding, with a spread of 1.17 × 10⁻³ from the
  other printed coefficients. The weaker, accurate claim is the one used.
- **Corrected: order-of-magnitude claim.** The review stated the modeling error
  exceeded the numerical error by "eight orders of magnitude". Measured: nearly
  seven in single precision, roughly fifteen in double.
- **Resolved: the review's evidence base of N = 1.** Experiment A sweeps
  r ∈ {0, 0.5, 1, 2, 4, 8, 16} with the fluctuation held exactly fixed,
  confirming η_DC = r²/(1+r²) to 1.9 × 10⁻¹⁶ and showing η_total rising to
  99.88% while the error on the fluctuation is constant to 9 × 10⁻¹⁷.

### Defects found and fixed during development

Recorded rather than quietly corrected.

- **Leakage metric found the conjugate mirror peak.** For a real signal the
  spectrum is symmetric, so searching the full spectrum for a "peak sidelobe"
  returned the mirror of the main lobe and reported ≈ 0 dB. Fixed by restricting
  to the non-negative-frequency half. Caught by comparison against published
  window values.
- **N = 26 cannot resolve lobe structure.** After the fix above, the descent
  ran to the spectrum edge: 14 unique bins is too few. Window characterization
  moved to a densely zero-padded response (oversampling 512). Measured sidelobes
  then matched the published catalog to within 1.5 dB for all four windows, 
  now a validation gate.
- **Automated figure QC failed the build** on a missing x-axis label in the
  window comparison. Fixed the figure, not the check.
- **A test caught a degenerate-input bug.** `energy_retention_ac` guarded
  against exactly-zero AC energy, but a constant signal has AC energy ~10⁻³²
  from rounding. The guard is now relative to total energy.
- **`\%` rendered literally in figure labels** because Matplotlib was not using
  LaTeX. Fixed and added to the QC checks.
- **Equations bypassed the manuscript markup parser**, rendering `ε_{L2}` with
  literal braces. Fixed; subscripts normalized throughout.

### References

Ten references verified against publisher or indexing records. Four marked
`[REFERENCE REQUIRES MANUAL VERIFICATION]`. One DOI omitted rather than guessed.
Three references from the prior work's list removed as decorative, they were
bibliographically correct but never cited in its body, with rationale recorded
in `citation_audit.csv`.
