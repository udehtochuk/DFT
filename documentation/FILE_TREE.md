# File Manifest

Complete listing of the publication package. SHA-256 checksums for all 121
files are in `FILE_MANIFEST.csv`.

```
publication_package/
├── LICENSE                                  MIT, plus a data-provenance note
│
├── manuscript/
│   ├── Retained_Spectral_Energy_Is_Not_Reconstruction_Fidelity.docx   18 pp
│   ├── Retained_Spectral_Energy_Is_Not_Reconstruction_Fidelity.pdf
│   ├── cover_letter.docx / .pdf
│   ├── build_manuscript.js                  builds the .docx from computed values
│   ├── build_cover_letter.js
│   └── manuscript_values.json               95 values; written by the pipeline
│
├── code/
│   ├── src/
│   │   ├── transforms.py                    unitary DFT/IDFT, FFT path, DCT-II
│   │   ├── data_recovery.py                 recovery from published coefficients
│   │   ├── metrics.py                       retention, errors, the exact relations
│   │   ├── coefficient_selection.py         three strategies, conjugate-safe
│   │   ├── signal_generation.py             corpus S0–S6, offset sweep
│   │   ├── dft_analysis.py                  Experiment A, corpus analysis
│   │   ├── dct_comparison.py                DFT vs DCT-II
│   │   ├── leakage_analysis.py              leakage, windows
│   │   ├── noise_experiments.py             S6, 100 realizations per SNR
│   │   ├── validation.py                    32 numerical gates
│   │   ├── plotting.py                      10 figures, house style
│   │   ├── figure_qc.py                     automated figure QC
│   │   └── export_manuscript_values.py      value export with completeness guard
│   ├── tests/test_study.py                  49 tests
│   ├── reproduce_all.py                     ← single entry point
│   ├── requirements.txt · environment.yml · pyproject.toml
│
│
├── data/
│   ├── recovered_data.txt / .csv            RECOVERED HISTORICAL
│   ├── signal_corpus/
│   │   ├── S0_recovered.csv                 RECOVERED HISTORICAL
│   │   ├── S1_bin-centered.csv … S5_damped.csv    SYNTHETIC
│   │   ├── S3_offset_sweep.csv              SYNTHETIC (Experiment A)
│   │   └── S6_noise/per_realization.csv     STOCHASTIC, seed 20260826
│   ├── spectral_coefficients/
│   │   ├── S0_unitary_dft.csv               this study's convention
│   │   └── S0_legacy_1314_convention.csv    the 2013/14 convention, do not reuse
│   ├── reconstruction_results/S0_11coefficient.csv
│   ├── metrics/                             experiment_a, thresholds, selection, noise
│   └── metadata/
│       ├── dataset_metadata.json            versions, seeds, provenance map
│       └── recovery_report.json             full recovery evidence
│
├── figures/                                 10 × (PDF, SVG, 600 dpi PNG)
│   fig01 recovered baseline          fig06 DFT vs DCT
│   fig02 DC energy share sweep       fig07 spectral leakage
│   fig03 redundancy identity         fig08 window comparison
│   fig04 AC retention vs error       fig09 noise robustness
│   fig05 selection strategies        fig10 Parseval precision
│
├── tables/                                  12 × (CSV, Markdown)
│   01 recovered dataset summary      07 selection curves
│   02 historical verification        08 DFT vs DCT
│   03 signal corpus                  09 leakage and windows
│   04 corpus statistics              10 noise summary
│   05 Experiment A                   11 numerical precision
│   06 energy thresholds              12 validation gates
│
├── supplementary/
│   ├── supplementary_methods.pdf            extended methodology
│   ├── mathematical_derivations.pdf         full derivations D1–D7
│   ├── supplementary_tables.pdf             all twelve tables
│   ├── supplementary_figures.pdf            all ten figures
│   ├── extended_results.pdf                 per-realization and full curves
│   └── build_supplementary.py
│
└── documentation/
    ├── README.md                            start here
    ├── REPRODUCIBILITY.md                   how to reproduce, and constraints
    ├── DATA_DICTIONARY.md                   every field in every file
    ├── CHANGELOG.md                         findings and defects, recorded
    ├── citation_audit.csv                   per-reference verification status
    ├── manuscript_claim_audit.csv           33 claims, each with evidence
    ├── research_integrity_statement.md      prior work, provenance, disclosures
    ├── venue_assessment_and_review.md       hostile review + venue analysis
    ├── FILE_MANIFEST.csv                    SHA-256 for all 121 files
    └── FILE_TREE.md                         this file
```

**Totals:** 129 files, ~12 MB. 13 source modules, 49 tests, 32 validation gates,
10 figures, 12 tables, 5 supplementary PDFs.
