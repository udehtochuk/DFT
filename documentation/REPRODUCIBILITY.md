# Reproducibility Guide

Everything needed to reproduce the study, and everything known to constrain it.

## One command

```bash
cd code && python reproduce_all.py
```

Runtime ~11 s. Regenerates: 32 validation gates, the recovered dataset, the
signal corpus, eight experiments, twelve tables, ten figures in three formats,
the manuscript values, dataset metadata and SHA-256 checksums. **Aborts on any
gate failure.**

`--quick` reduces noise realizations from 100 to 10 for a smoke test.

## Full release check

```bash
cd code         && python -m pytest tests/ -q          # 49 tests
cd code         && python reproduce_all.py             # pipeline + QC
cd notebooks    && python build_notebooks.py
```

## Determinism

| Component | Determinism |
|---|---|
| Data recovery | Fully deterministic; no RNG |
| Transforms, metrics, selection | Fully deterministic |
| S1, S2, S3, S5, offset sweep | Fully deterministic; no RNG |
| S4 (broadband) | Seeded from master seed 20260826 |
| S6 (noise) | Master seed 20260826, distinct child stream per SNR level |
| Precision sweep | Seeded 20260826 |

`numpy.random.default_rng` (PCG64) is used throughout; it is stable across NumPy
versions in a way the legacy `RandomState` is not.

Bit-identical reproduction of floating-point results requires the same NumPy
build and BLAS. Expect agreement to ~1e-12 across platforms, comfortably inside
every tolerance.

## Environment

Generated with Python 3.12.3, NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.8,
pandas 3.0.2, pytest 9.1.1. Pinned in `code/requirements.txt`,
`code/environment.yml`, `code/pyproject.toml`.

No external FFT library is required. `numpy.fft` is used, and an independent
direct O(N²) DFT is computed and cross-checked against it (max abs difference
1.9e-12, max relative 1.5e-15). Document any substitution: Schatzman (1996)
shows FFT accuracy depends materially on the library, especially on
twiddle-factor generation.

Optional: Node.js with `docx` (manuscript), LibreOffice (PDF rendering).
Neither is needed to reproduce any scientific result.

## Validation gates

32 gates run before anything else; the pipeline aborts if any fails. Coverage:

- direct DFT vs FFT, absolute and relative
- IDFT(DFT(x)) round-trip
- Hermitian symmetry; Nyquist and DC realness
- the 2013/14 convention discrepancy (asserted as an expected finding)
- Parseval at float64
- η_DC against r²/(1+r²)
- DCT-II orthonormality and round-trip
- real-valued reconstruction; exact full-mask reconstruction
- all nine historical quantities
- the three exact relations
- window sidelobes against published values (external check)
- cumulative-mask threshold attainment and conjugate symmetry

**Tolerances are fixed in `validation.py` and must never be relaxed to make a
check pass.** If a gate fails, the cause is a defect, in the code, the
environment, or an assumption. Two real defects were caught this way during
development; both are recorded in `CHANGELOG.md`.

## Figure quality control

Automated, and a hard gate. Checks existence in PDF/SVG/PNG, ≥600 dpi raster
resolution, genuine vector output, absence of un-rendered TeX escapes, presence
of axis labels, minimum tick font size, and redundant (non-color-only) encoding
of every series. It has already failed the build once, on a missing axis label.

## Manuscript value export

Every number in the manuscript is read from `manuscript/manuscript_values.json`,
written by the pipeline. The exporter validates that all 71 required keys are
present and finite, and the manuscript build wraps the JSON in a proxy that
throws on any missing key.

Both guards exist because an early build shipped the word "undefined" into the
rendered PDF: a pandas DataFrame column was read by attribute (`df.transform`),
which resolves to a *method*, so the comparison silently returned all-False.
Column access is now always by bracket.

## Known constraints

- Bit-identical floating point requires an identical NumPy/BLAS build.
- Matplotlib ≥3.8 assumed; older versions may differ in default layout.
- Notebook execution needs `nbconvert` and a Python 3 kernel.
- The Word manuscript needs Node.js and the `docx` package; the PDF needs
  LibreOffice. Neither affects any scientific result.
- The recovered baseline is a reconstruction from coefficients printed to finite
  precision, not the original file.

## If reproduction fails

1. Check versions against `requirements.txt`.
2. Run `pytest tests/ -q` first, it localises failures better than the pipeline.
3. Read the failing gate's `measured` and `tolerance` values; the gate names the
   quantity that disagrees.
4. Verify SHA-256 checksums against `documentation/FILE_MANIFEST.csv`.
5. **Do not raise a tolerance to make a check pass.** A failure is a result.
