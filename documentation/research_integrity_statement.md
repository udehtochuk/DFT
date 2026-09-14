# Research Integrity Statement

For the manuscript *Retained Spectral Energy Is Not Reconstruction Fidelity:
A Verified Re-Analysis of DFT Coefficient Selection*.

Prepared 26 August 2026. This statement records prior work, data provenance,
methodological choices, and every matter that could not be independently
verified during preparation. It is written in neutral language throughout; no
allegation is made against any person.

---

## 1. Prior work and its relationship to this manuscript

This study develops from the author's earlier work:

> Udeh Tochukwu L., "Analysis of Discrete Fourier Transform of a given function
> and verification of Parseval Theorm", coursework/research c. 2013, made
> available through ResearchGate in 2014.

That work is cited in the manuscript abstract, introduction, methods, results,
a dedicated Acknowledgment of Prior Work, and the reference list. It is not
concealed, restated as new, or superseded.

**Inherited from the prior work:** the 26-sample sequence; the real-form
transform pair; the symmetric low-pass retention scheme; the originating
question about how many coefficients recover a given percentage of energy.

**New to this manuscript:** the data recovery; independent verification of all
nine historical quantities; correction of the transform convention,
normalization and terminology; the DC-share analysis; the three exact relations
and their derivations; Experiment A; the AC-basis analysis; the
selection-strategy, DCT, leakage, window, noise and precision experiments; the
reporting protocol; and the entire computational package.

**No text is reproduced from the prior work.** The theory and background
sections of this manuscript were written afresh.

### Self-plagiarism and duplicate-publication assessment

The manuscript materially derives from a work already made publicly available,
and does not claim to be entirely original. The overlap is confined to the
dataset and the originating question, both of which are disclosed at every point
where they appear. The new manuscript's contribution, the exact relations, the
controlled validation, the corrections, and the reproducible package, is not
present in the prior work in any form.

Because the prior work was posted to a preprint/repository service rather than
published in a peer-reviewed venue, this manuscript is not a duplicate
submission. Authors should nonetheless disclose the prior posting in any cover
letter, and this package is written on the assumption that they will.

---

## 2. Textual-similarity matter requiring verification

During the forensic review that preceded this study, passages in the **prior
work** were observed to closely follow the phrasing and structure of
well-known third-party sources without citation. The specific framings noted
were:

- a four-category signal taxonomy (aperiodic/periodic × continuous/discrete)
  and associated introductory material, closely tracking a standard DSP
  textbook treatment;
- a passage on the interpretation of discrete Fourier transforms and Hermitian
  symmetry, closely tracking a widely used online mathematics reference;
- a passage introducing the DFT and its applications, closely tracking a
  general-reference encyclopaedia article;
- a discussion of aliasing and windowing written in the first-person-plural
  voice of a textbook chapter, referring to earlier chapters that do not exist
  in that work;
- two IEEE references that appear in the reference lists of general-reference
  Fourier-transform pages and that are not cited anywhere in the body of the
  prior work.

**Status: requires verification by the original author and, where applicable,
by the venue hosting the prior work.** This assessment rests on textual
familiarity and has not been confirmed against the sources by a formal
similarity-detection process. No allegation of misconduct is made, and none
should be read into this record. The matter is stated because it concerns a
work this manuscript builds on, and because it bears on what may be carried
forward.

**Action taken in this manuscript.** No text from the prior work is reproduced.
The theory and background sections are original to this manuscript. Where the
prior work drew its framing from a standard textbook treatment, that source is
now cited (reference [12]). The two uncited IEEE references were removed rather
than carried forward unused, and the rationale is recorded in
`citation_audit.csv`.

---

## 3. Data provenance

### Recovered historical data

The 26-sample baseline sequence was reconstructed by Hermitian inversion of the
transform coefficients printed in the prior work. **The original data file is
lost and is not available.** The recovered sequence is a reconstruction, not the
original file.

The recovery was validated three independent ways before use: agreement with the
15 sample values printed in the prior work (exact after rounding; the residual
mean matches the DC-rounding prediction to 10⁻⁵); internal Hermitian and Nyquist
consistency of the printed coefficients, neither of which was used in
constructing the recovery; and integrality of the recovered values.

**The physical identity, measurand, units and sampling rate of this signal are
unknown.** They are not stated in the prior work and are not recoverable from
it. *Information required, not available.* No provenance has been inferred,
assumed or invented, and the sequence is analyzed as dimensionless throughout.

### Generated data

Signals S1–S5 and the offset sweep are synthetic and deterministic. S4 uses the
master seed. S6 is stochastic: 100 realizations at each of four SNR levels.
Master seed **20260826**, with a distinct reproducible child stream per level,
both recorded in the code and the metadata.

Recovered, synthetic and stochastic data are stored separately and labeled in
machine-readable metadata. Generated data never overwrite recovered data.

---

## 4. Corrections to the prior work

Recorded so that no historical result is silently replaced.

| Matter | Status |
|---|---|
| All nine reported numerical quantities | **Verified.** Every one reproduces. The prior work made no arithmetic errors. |
| Analysis-kernel sign | **Corrected.** The stated transform used a negative exponent; the computed one used a positive exponent, yielding a frequency-reversed spectrum. Magnitudes and energies unaffected for a real signal; phases and bin indices are not. |
| Normalization | **Corrected.** Three conventions appeared in one document; Parseval was stated in a form valid under only one. |
| "Inverse of the function" | **Corrected.** The operation x1[n] = (−1)ⁿx[n] is modulation producing a circular spectral shift by N/2, not an inverse. |
| Σ(x6[i])² notation | **Corrected** to Σ\|x6[i]\|². Harmless in the original because the retention set is conjugate-symmetric, but not stated there. |
| Interpretation of the 99.175% figure | **Corrected.** The figure is confounded by the DC component. |
| Task left incomplete | The prior work posed the question of how many coefficients recover a given energy percentage and did not report an answer; the variant number K was never stated. *Information required, not available.* Completed here. |

---

## 5. Methodological disclosures

- **No statistical significance is claimed anywhere.** No p-value is reported
  and no hypothesis test is performed. This is a deliberate choice: the
  deterministic experiments have no sampling variability, and the quantity of
  interest in the stochastic experiment is an effect size, reported directly.
  Reported intervals are 95% confidence intervals for the mean across
  realizations, not prediction intervals.
- **No result is presented that was not executed.** Every value in the
  manuscript is regenerated by `reproduce_all.py`. Nothing is labeled
  "proposed" and then reported as a finding.
- **No figure contains illustrative or invented data.**
- **Validation tolerances were fixed in advance** and are documented in
  `validation.py`. No tolerance was relaxed to make a check pass. One check
  (a missing axis label) and one implementation defect (a leakage metric that
  found the conjugate mirror peak) were caught by automated QC during
  development and are recorded in `CHANGELOG.md` rather than quietly fixed.
- **A discrepancy between the informal forensic review and independent
  computation was resolved in favor of the computation.** The review described
  the recovery residual as a constant offset; it is not exactly constant, and
  the more careful statement now used is that its *mean* is explained by DC
  rounding to within 10⁻⁵, with a spread of 1.17 × 10⁻³ from the other printed
  coefficients. The weaker, accurate claim is the one that appears in the
  manuscript.

---

## 6. What could not be independently verified

- **The bibliographic metadata of the prior work.** Supplied by the author;
  marked `[REFERENCE REQUIRES MANUAL VERIFICATION]` in the reference list and
  in `citation_audit.csv`. Must be cleared before submission.
- **Four further references** cited from established knowledge but not confirmed
  at the publisher during preparation, each marked in the reference list and the
  citation audit. Ten references *were* verified against publisher or indexing
  records; the audit records which.
- **One DOI** (reference [7]) could not be independently confirmed and is
  omitted rather than guessed. No DOI in this package is invented.
- **The textual-similarity matter** in Section 2 above.
- **Funding.** *Information required, not available.* No funding information
  was supplied.
- **Author affiliation, email and ORCID.** Placeholders in the manuscript.
  *Information required, not available.*
- **Repository URL.** Placeholder. No repository or archive URL has been
  invented.

---

## 7. Conflict of interest

The author declares **no competing financial interest**.

The author declares a **non-financial interest**: the prior work assessed,
verified and corrected in this manuscript is the author's own, and the
verification was performed by the author. This is a structural limitation on the
independence of the assessment. The complete data and code release, the 49-test
suite and the 32 validation gates exist partly so that third parties can check
that judgment without relying on the author's account of it.

---

## 8. Author contributions

Sole author: conceptualisation, methodology, software, validation, formal
analysis, investigation, data curation, writing (original draft and revision),
visualization.

---

## 9. Ethical approval

Not applicable. No human participants, animal subjects, or personal data are
involved. The study analyzes one recovered numerical sequence of unknown origin
and a set of synthetic signals.
