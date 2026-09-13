# Retained Spectral Energy Is Not Reconstruction Fidelity

**A verified re-analysis of DFT coefficient selection.**

This repository is the complete computational package for the manuscript of the
same name. A new researcher should be able to reproduce every number, table and
figure in the paper without contacting the author. If that turns out not to be
true, it is a defect, please report it.

---

## 1. What the study investigates

When a signal is reconstructed from a subset of its discrete Fourier transform
coefficients, the fraction of spectral energy those coefficients carry is widely
used as a figure of merit. This study shows that the measure is uninformative
about reconstruction fidelity in a specific, quantifiable way, and that the
remedy most likely to be proposed for it does not work.

Three exact relations, all corollaries of Parseval's identity, drive the result:

| Relation | Meaning |
|---|---|
| η_DC = r² / (1 + r²) | The DC coefficient's energy share depends only on r = μ/σ |
| ε_L2 = √(1 − η) | Retained energy and relative L2 error are the same information |
| ε_full = ε_AC / √(1 + r²) | The two reporting bases differ by a factor set by r |

The second is the one that changes practice: because energy retention and
reconstruction error computed on the *same basis* are related by a monotone
transformation, reporting both adds nothing. What matters is the **basis**, and
r is a sufficient statistic for converting between bases.

On the recovered baseline the DC coefficient alone carries **93.183%** of the
total energy, so the earlier finding of 99.175% retention with 11 of 26
coefficients describes the sample mean rather than any spectral concentration.
The relative L2 error at that operating point is **0.0908**, and on the
mean-removed basis the same 11 coefficients retain only 87.9% of the fluctuation
energy.

---

## 2. Data provenance, read this before using any file

Three provenance classes are kept strictly separate and are **never**
overwritten by one another.

### Recovered historical data
`data/recovered_data.txt`, `data/recovered_data.csv`,
`data/signal_corpus/S0_recovered.csv`

The 26-sample sequence of the 2013/2014 study. The original `data.txt` is
**lost**. This sequence was reconstructed by Hermitian inversion of the transform
coefficients printed in that paper, and validated three independent ways
(agreement with the 15 printed samples; internal Hermitian/Nyquist consistency of
the printed coefficients; integrality of the recovered values).

> **It is a reconstruction, not the original file.** The physical identity,
> measurand, units and sampling rate of this signal are **unknown**, they are
> not stated in the source and are not recoverable from it. No provenance has
> been inferred or invented. All analysis treats the sequence as dimensionless.

### Synthetic benchmark data
`data/signal_corpus/S1_*.csv` … `S5_*.csv`, `data/signal_corpus/S3_offset_sweep.csv`

Generated deterministically by `signal_generation.py`. S4 uses the master seed;
the rest involve no randomness. These are designed test signals, not
measurements of anything.

### Stochastic generated data
`data/signal_corpus/S6_noise/per_realization.csv`

The recovered baseline plus zero-mean Gaussian noise, 100 realizations at each of
four SNR levels, under master seed **20260826** with a distinct reproducible
child stream per level.

Machine-readable provenance and software versions:
`data/metadata/dataset_metadata.json`. Recovery evidence:
`data/metadata/recovery_report.json`.

---

## 3. Installation

Requires Python ≥ 3.10. Tested on Python 3.12.3.

```bash
# pip
python -m venv .venv && source .venv/bin/activate
pip install -r code/requirements.txt

# or conda
conda env create -f code/environment.yml
conda activate dft-energy-study
```

Pinned versions used to generate every result in this package: Python 3.12.3,
NumPy 2.4.4, SciPy 1.17.1, Matplotlib 3.10.8, pandas 3.0.2, pytest 9.1.1.
No external FFT library (FFTW etc.) is required, `numpy.fft` is used, and a
direct O(N²) DFT is computed independently and cross-checked against it.

---

## 4. Reproducing the study

One command regenerates everything:

```bash
cd code
python reproduce_all.py
```

Expected runtime: **about 11 seconds** on a modern laptop. Use
`python reproduce_all.py --quick` for a smoke test with 10 noise realizations
instead of 100.

The pipeline runs in six steps and **aborts loudly** if any validation gate
fails:

1. 32 numerical validation gates
2. Data recovery and signal-corpus generation
3. Eight experiments
4. Twelve tables (CSV + Markdown)
5. Ten figures (PDF + SVG + 600 dpi PNG) with automated quality control
6. Metadata and SHA-256 checksums for every file

### Regenerating individual artifacts

```bash
cd notebooks   && python build_notebooks.py      # rebuild the nine notebooks
cd manuscript  && node build_manuscript.js       # rebuild the Word manuscript
cd supplementary && python build_supplementary.py # rebuild the five PDFs
```

Figures and tables alone are regenerated by notebook
`09_generate_publication_figures.ipynb`, which uses the same code path as the
pipeline, a notebook and the pipeline cannot disagree.

---

## 5. Running the tests

```bash
cd code
python -m pytest tests/ -q
```

**49 tests**, runtime under one second. They cover the DFT against analytically
known signals (bin-centered cosine, constant, unit impulse), DFT against inverse
DFT, direct DFT against NumPy's FFT, Hermitian symmetry, Nyquist realness,
real-valued reconstruction, Parseval, all three exact relations, coefficient
selection and its invariants, the DC-energy formula, metric edge cases,
deterministic signal generation, seed reproducibility, and window sidelobe
levels against published values.

> **Tolerances are deliberate.** If a test fails, investigate the cause. Do not
> loosen the tolerance to make it pass.

---

## 6. Executing the notebooks

```bash
cd notebooks
jupyter lab          # or: jupyter notebook
```

All nine execute from a clean environment. To verify:

```bash
for f in 0*.ipynb; do
  python -m nbconvert --to notebook --execute --inplace "$f"
done
```

Each notebook follows the same structure, Objective, Background, Inputs,
Method, Code, Outputs, Interpretation, Limitations, Reproducibility, and
imports the same `code/src` modules the pipeline uses. No calculation is hidden
in a notebook cell.

| Notebook | Content |
|---|---|
| 01 | Recover and verify the 2013/2014 baseline |
| 02 | The DC confound and the three exact relations |
| 03 | Coefficient-selection strategies and threshold ambiguity |
| 04 | Signal corpus and Experiment A (the controlled offset sweep) |
| 05 | DFT against DCT-II |
| 06 | Spectral leakage and window functions |
| 07 | Noise robustness |
| 08 | Numerical precision and what Parseval verification can show |
| 09 | Regenerate all publication figures and tables |

---

## 7. Repository layout

```
publication_package/
├── manuscript/       Word manuscript, PDF, build script, cover letter
├── code/
│   ├── src/          11 modules (transforms, metrics, selection, …)
│   ├── tests/        49 tests
│   ├── reproduce_all.py
│   └── requirements.txt · environment.yml · pyproject.toml
├── notebooks/        9 executable notebooks
├── data/             recovered · synthetic · stochastic · metadata
├── figures/          10 figures × (PDF, SVG, 600 dpi PNG)
├── tables/           12 tables × (CSV, Markdown)
├── supplementary/    5 PDFs
├── documentation/    this file, data dictionary, audits, manifest
└── LICENSE
```

---

## 8. Conventions used throughout

One DFT convention is used in the code, the manuscript, the figures, the tables
and the supplement, without exception:

```
X[k] = (1/√N) Σ x[n] exp(−j2πkn/N)      analysis
x[n] = (1/√N) Σ X[k] exp(+j2πkn/N)      synthesis
Σ|x[n]|² = Σ|X[k]|²                      Parseval
```

Note the **negative** exponent in analysis. The 2013/2014 study stated this
convention but computed the conjugate one, producing a frequency-reversed
spectrum. Magnitudes and energies are unaffected for a real signal, which is
why its arithmetic verifies, but phases and bin indices are not. The legacy
transform is retained in `transforms.legacy_transform_1314` **solely** so the
historical coefficient tables can be reproduced; it is never used for new
analysis.

Retention sets always comprise whole conjugate groups, so every reconstruction
is real. `reconstruct_from_mask` raises rather than silently taking a real part:
a non-conjugate mask is a specification error.

---

## 9. Known limitations

Stated plainly, because they bound what the results support:

- **Only one non-synthetic signal.** S0 is the sole real-world-derived sequence,
  and its physical identity is unknown. No claim is made about any application
  domain.
- **The corpus is designed.** S1–S6 were constructed by the author to exhibit
  the phenomena under study. They show the mechanism operates across signal
  classes; they say nothing about which values of r occur in practice.
- **The practice claim is not evidenced.** The manuscript notes that energy
  figures are sometimes reported on unprocessed data outside transform coding.
  One case is documented. Frequency is not established, and no survey was
  conducted.
- **Recovery is a reconstruction**, from coefficients printed to finite
  precision.
- **N = 26 is short.** Only 14 unique bins, which is why window characterization
  requires dense frequency sampling.
- **No inferential statistics.** Deterministic experiments have no sampling
  variability; the stochastic experiment is reported descriptively with
  confidence intervals for the mean. No significance claim is made anywhere.
- **Limited theoretical novelty.** The three relations are corollaries of
  Parseval. The contribution is methodological, empirical and infrastructural, 
  not theoretical.
- **Author-conducted review of the author's own prior work.** This full release
  exists partly so that third parties can check that judgment independently.

---

## 10. Citation

Cite the manuscript. Please also cite the prior work it develops from, which is
the source of the baseline sequence:

```bibtex
@article{udeh2026retained,
  author  = {Udeh, Tochukwu L.},
  title   = {Retained Spectral Energy Is Not Reconstruction Fidelity:
             A Verified Re-Analysis of {DFT} Coefficient Selection},
  year    = {2026},
  note    = {Data and code: https://github.com/udehtochuk/DFT}
}

@misc{udeh2014analysis,
  author  = {Udeh, Tochukwu L.},
  title   = {Analysis of Discrete {F}ourier Transform of a given function
             and verification of {P}arseval Theorm},
  year    = {2014},
  howpublished = {ResearchGate},
  note    = {Prior work; bibliographic details require verification}
}
```

---

## 11. License and contact

Code and data released under the MIT License (see `LICENSE`).

- Repository: `https://github.com/udehtochuk/DFT`
- Author contact: `[EMAIL TO BE INSERTED]`

See `documentation/research_integrity_statement.md` for prior-work disclosure,
conflict of interest, and matters requiring verification.
