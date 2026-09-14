#!/usr/bin/env python3
"""
build_supplementary.py
======================
Generates the five supplementary PDFs from computed results.

    supplementary_methods.pdf       extended methodological detail
    mathematical_derivations.pdf    full derivations of equations (4), (7)-(9)
    supplementary_tables.pdf        all twelve tables in full
    supplementary_figures.pdf       all ten figures at publication resolution
    extended_results.pdf            per-realization and full-curve results

Run:  python build_supplementary.py    (from publication_package/supplementary/)
"""

from __future__ import annotations

import base64
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "code" / "src"))

CSS = """
@page { size: A4; margin: 22mm 20mm; }
body { font-family: "DejaVu Serif", serif; font-size: 9.5pt; line-height: 1.42; }
h1 { font-size: 15pt; border-bottom: 1.2px solid #333; padding-bottom: 4px;
     margin-top: 0; }
h2 { font-size: 11.5pt; margin-top: 16px; }
h3 { font-size: 10pt; margin-top: 12px; font-style: italic; }
table { border-collapse: collapse; font-size: 7.2pt; margin: 8px 0; width: 100%; }
th, td { border: 0.5px solid #bbb; padding: 2.5px 4px; text-align: right; }
th { background: #ececec; font-weight: bold; text-align: center; }
td:first-child, th:first-child { text-align: left; }
.eq { margin: 9px 0 9px 20px; font-style: italic; }
.note { background: #f6f6f6; border-left: 2.5px solid #888; padding: 6px 10px;
        margin: 9px 0; font-size: 9pt; }
figure { margin: 20px 0 26px 0; page-break-inside: avoid; text-align: center;
         display: block; clear: both; width: 100%; }
figure.pb { page-break-after: always; }
figure img { width: 96%; display: block; margin: 0 auto; }
figcaption { font-size: 8pt; text-align: left; margin-top: 4px;
             display: block; clear: both; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; }
"""


def _soffice() -> str:
    """
    Locate LibreOffice portably.

    Order: the SOFFICE_BIN environment variable, then whatever is on PATH.
    No absolute path is hard-coded, so the script runs on any machine that has
    LibreOffice installed. PDF rendering is a convenience step for the
    supplementary material only; no scientific result depends on it.
    """
    import os
    import shutil
    candidate = os.environ.get("SOFFICE_BIN")
    if candidate and shutil.which(candidate):
        return candidate
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError(
        "LibreOffice not found. Install it, or set SOFFICE_BIN to its "
        "executable. This affects only the supplementary PDFs.")


def html_to_pdf(html: str, stem: str) -> Path:
    """Render HTML to PDF via LibreOffice (available in this environment)."""
    src = HERE / f"{stem}.html"
    src.write_text(f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                   f"<style>{CSS}</style></head><body>{html}</body></html>",
                   encoding="utf-8")
    subprocess.run(
        [_soffice(), "--headless", "--convert-to", "pdf",
         "--outdir", str(HERE), str(src)],
        check=True, capture_output=True)
    src.unlink(missing_ok=True)
    return HERE / f"{stem}.pdf"


def table_html(stem: str, max_rows: int | None = None) -> str:
    df = pd.read_csv(ROOT / "tables" / f"{stem}.csv")
    note = ""
    if max_rows and len(df) > max_rows:
        note = (f"<p><em>Showing the first {max_rows} of {len(df)} rows; the "
                f"complete table is in <code>tables/{stem}.csv</code>.</em></p>")
        df = df.head(max_rows)
    return df.to_html(index=False, float_format=lambda v: f"{v:.6g}",
                      border=0) + note


# --------------------------------------------------------------------------
def methods() -> str:
    return """
<h1>Supplementary Methods</h1>
<p>Extended methodological detail for <em>Retained Spectral Energy Is Not
Reconstruction Fidelity: A Verified Re-Analysis of DFT Coefficient
Selection</em>. Section numbers refer to the main manuscript.</p>

<h2>S1. Data recovery in full</h2>
<p>The source data of the 2013/2014 study are unavailable. That work prints the
real and imaginary parts of its transform coefficients for k = 0,&nbsp;&hellip;,&nbsp;14
of a real sequence with N&nbsp;=&nbsp;26. The degree-of-freedom count is exact:
bin&nbsp;0 is real (1), bins 1&ndash;12 are complex (24), and bin&nbsp;13 is real
because N is even and 13 = N/2 is the Nyquist bin (1), totalling 26. Hermitian
symmetry X[N&minus;k] = X*[k] supplies bins 14&ndash;25.</p>
<p>The coefficients are expressed in the earlier work's own convention, which
uses a <em>positive</em> analysis exponent with 1/&radic;N scaling. The recovery
therefore applies the synthesis matrix of <em>that</em> convention, not of the
convention adopted for the present study. Applying the wrong one yields a
time-reversed sequence, which is a useful self-check: it does not match the
printed samples.</p>

<h3>Validation evidence</h3>
<p>Three independent conditions were checked before the recovered data were
used for anything.</p>
<p><strong>(i) Agreement with printed samples.</strong> The 15 sample values
printed in the earlier work are reproduced exactly after rounding. Before
rounding, the residual has mean &minus;0.0627394 against &minus;0.0627497
predicted from the DC coefficient being printed to four significant figures.
The residual is <em>not</em> exactly constant: its spread is
1.17&nbsp;&times;&nbsp;10<sup>&minus;3</sup>, attributable to the remaining
coefficients being printed to three decimals. This distinction is recorded
because an earlier informal analysis described the residual as a constant
offset, and the more careful statement is that its <em>mean</em> is explained
by DC rounding to within 10<sup>&minus;5</sup>.</p>
<p><strong>(ii) Internal consistency of the printed coefficients.</strong> The
printed coefficient at k&nbsp;=&nbsp;14 equals the conjugate of that at
k&nbsp;=&nbsp;12, and the printed imaginary part at the Nyquist bin is
2.154&nbsp;&times;&nbsp;10<sup>&minus;12</sup>. Both are conditions that a real
length-26 sequence must satisfy, and neither was used in constructing the
recovery, so they are genuine checks.</p>
<p><strong>(iii) Integrality.</strong> Recovered values lie within 0.064 of
integers throughout, consistent with integer-valued source data and with the
magnitude of the DC-rounding offset.</p>
<div class="note"><strong>What the recovery is not.</strong> It is a
reconstruction of the source data, not the original file. The physical
identity, measurand, units and sampling rate of the signal are not stated in
the earlier work and are not recoverable from it. No provenance is inferred or
invented, and all analysis treats the sequence as dimensionless.</div>

<h2>S2. Transform conventions</h2>
<p>One convention is used throughout the manuscript, its figures, tables, code
and this supplement: the unitary pair with a negative analysis exponent and
1/&radic;N scaling on both directions. The legacy transform of the earlier work
is retained in the code solely so that its published coefficient tables can be
reproduced exactly; it is never used for new analysis. It satisfies
ye[k] = X[(N&minus;k) mod N], i.e. it is the frequency-reversed conjugate of the
standard DFT, which is asserted as a validation gate.</p>

<h2>S3. Conjugate-group retention</h2>
<p>All retention sets are built from whole conjugate groups. For N&nbsp;=&nbsp;26
the groups are {0}, {13} (both self-conjugate) and the twelve pairs
{k,&nbsp;26&minus;k} for k&nbsp;=&nbsp;1,&nbsp;&hellip;,&nbsp;12. Retaining whole
groups guarantees a real-valued reconstruction. The reconstruction function
asserts this and raises if the imaginary residual is not negligible, rather
than silently taking a real part &mdash; a non-conjugate mask is a specification
error, not a rounding issue.</p>

<h2>S4. Noise experiment design</h2>
<p>SNR is defined on the mean-removed power of the baseline. Scaling noise to
the DC-inflated total power would make the nominal SNR meaningless for exactly
the reason this study documents: at r&nbsp;=&nbsp;3.70 the total power is 14.7
times the fluctuation power, so a nominal "0&nbsp;dB" defined on total power
would in fact be about +11.7&nbsp;dB on the quantity of interest.</p>
<p>Errors are measured against the <em>clean</em> baseline rather than the noisy
observation, because the task is recovery of the underlying signal. Each SNR
level draws from a distinct reproducible child stream derived from the master
seed, so levels are independent yet exactly reproducible.</p>

<h2>S5. Statistical policy</h2>
<p>Deterministic experiments are reported as exact values with no dispersion,
because they have none: repeating them yields bit-identical results.</p>
<p>The noise experiment uses 100 realizations per level and is reported as mean,
standard deviation and a 95% confidence interval for the mean under the normal
approximation. No p-value is reported and no significance test is performed.
This is a deliberate choice, not an omission: no hypothesis in this study takes
the form of a comparison against a null that a test would illuminate. The
quantity of interest is an effect size &mdash; the gap between retained energy
and reconstruction error &mdash; and it is reported directly, in the units in
which it matters. Normality tests were likewise not performed, as they would
serve the appearance of rigor rather than any inference actually drawn.</p>
<div class="note">The reported intervals are confidence intervals for the
<em>mean across realizations</em>. They are not prediction intervals for a
single realization and must not be read as such.</div>

<h2>S6. Window characterization</h2>
<p>Main-lobe widths and sidelobe levels are measured from a densely zero-padded
frequency response (oversampling factor 512), not from the length-26 transform.
With N&nbsp;=&nbsp;26 the transform has only 14 unique bins, which cannot resolve
a main lobe a few bins wide, let alone sidelobe structure. An earlier
implementation that measured lobes on the native transform reported spurious
0&nbsp;dB sidelobes, because for a real signal it found the conjugate mirror of
the main lobe; the defect was caught by comparison against published values and
is recorded here because the failure mode is easy to reproduce.</p>
<p>Measured peak sidelobe levels agree with the published catalog to within
1.5&nbsp;dB for all four windows, providing an external check on the
implementation that does not depend on any code in this package.</p>

<h2>S7. Provenance of each element</h2>
<p>Referenced from Appendix C of the manuscript. Material inherited from the
2013/2014 work, results recomputed and confirmed, corrections made, and results
new to this study.</p>
<table>
<tr><th>Category</th><th>Content</th></tr>
<tr><td>Inherited from [11]</td><td>The 26-sample sequence; the real-form transform pair; the low-pass retention scheme; the originating question about coefficients per energy percentage</td></tr>
<tr><td>Recomputed and confirmed</td><td>E, H, E1, 100&middot;E1/E, E2, 100&middot;E2/E, 0.95E, and the coefficient tables for k = 0&ndash;14. All nine reproduce; see manuscript Table 2</td></tr>
<tr><td>Corrected</td><td>Analysis-kernel sign and spectrum orientation; normalization convention; &ldquo;inverse of the function&rdquo; &rarr; modulation / N/2 spectral shift; (x6)&sup2; &rarr; |x6|&sup2;; the interpretation of the retention figure</td></tr>
<tr><td>New to this study</td><td>Data recovery with existence and uniqueness; equations (4) and (7)&ndash;(10); Experiment A; the AC-basis analysis; the selection comparison with exhaustive optimality check; the DCT comparison; leakage and window experiments; the noise study; the precision sweep; the reporting protocol</td></tr>
<tr><td>Not claimed</td><td>Any new transform theory; identification of the DC-dominance phenomenon, which is established in the biomedical compression literature; any prevalence estimate; any claim about a specific application domain</td></tr>
</table>

<h2>S7. Validation gates</h2>
<p>The pipeline runs 32 numerical gates and aborts if any fails. Tolerances are
fixed in <code>validation.py</code> and are never relaxed to make a check pass.
The gates cover transform correctness, direct-DFT/FFT agreement, Hermitian and
Nyquist structure, the convention discrepancy, Parseval at double precision,
the DC-share identity, DCT orthonormality, reconstruction realness, all nine
historical quantities, the three exact relations, window sidelobes against the
literature, and selection-mask sanity.</p>
"""


def derivations() -> str:
    return """
<h1>Mathematical Derivations</h1>
<p>Full derivations of the four relations stated in Section&nbsp;V of the
manuscript. All four are corollaries of Parseval's identity for a unitary
transform. They are elementary; they are set out in full because their
<em>interpretive</em> consequences drive the paper's conclusions.</p>

<h2>D1. Preliminaries</h2>
<p>Let x[n] be real, n = 0,&nbsp;&hellip;,&nbsp;N&minus;1, with sample mean
&mu; = (1/N)&sum;x[n] and population variance
&sigma;<sup>2</sup> = (1/N)&sum;(x[n]&minus;&mu;)<sup>2</sup>. Under the unitary
convention</p>
<p class="eq">X[k] = (1/&radic;N) &sum;<sub>n</sub> x[n] exp(&minus;j2&pi;kn/N),</p>
<p>the transform matrix is unitary, hence
E = &sum;<sub>n</sub>|x[n]|<sup>2</sup> = &sum;<sub>k</sub>|X[k]|<sup>2</sup>.</p>

<h2>D2. The DC energy share (Equation 4)</h2>
<p>Setting k = 0 in the analysis equation gives
X[0] = (1/&radic;N)&sum;<sub>n</sub>x[n] = &radic;N&nbsp;&mu;, so
|X[0]|<sup>2</sup> = N&mu;<sup>2</sup>.</p>
<p>For the total energy, expand about the mean:</p>
<p class="eq">E = &sum;<sub>n</sub>x[n]<sup>2</sup>
= &sum;<sub>n</sub>((x[n]&minus;&mu;) + &mu;)<sup>2</sup>
= &sum;<sub>n</sub>(x[n]&minus;&mu;)<sup>2</sup>
+ 2&mu;&sum;<sub>n</sub>(x[n]&minus;&mu;) + N&mu;<sup>2</sup>.</p>
<p>The cross term vanishes because &sum;(x[n]&minus;&mu;) = 0 by definition of
the mean, leaving E = N&sigma;<sup>2</sup> + N&mu;<sup>2</sup>
= N(&mu;<sup>2</sup>+&sigma;<sup>2</sup>). Therefore</p>
<p class="eq">&eta;<sub>DC</sub> = |X[0]|<sup>2</sup>/E
= N&mu;<sup>2</sup> / N(&mu;<sup>2</sup>+&sigma;<sup>2</sup>)
= &mu;<sup>2</sup>/(&mu;<sup>2</sup>+&sigma;<sup>2</sup>).</p>
<p>Dividing numerator and denominator by &sigma;<sup>2</sup> and writing
r = &mu;/&sigma; gives
<strong>&eta;<sub>DC</sub> = r<sup>2</sup>/(1+r<sup>2</sup>)</strong>. &#9633;</p>
<p>The function is monotone increasing in |r| with
&eta;<sub>DC</sub>(0) = 0, &eta;<sub>DC</sub>(1) = 1/2,
&eta;<sub>DC</sub>(3) = 0.9 and &eta;<sub>DC</sub>(10) = 0.990. It also shows
that the AC share is 1/(1+r<sup>2</sup>), which decays as r<sup>&minus;2</sup>.
For the recovered baseline, r = 3.6973 gives
&eta;<sub>DC</sub> = 0.9318337, matching the measured value to
3&nbsp;&times;&nbsp;10<sup>&minus;16</sup>.</p>

<h2>D3. Error from retention (Equation 7)</h2>
<p>Let K be a retention set and x&#770; the inverse transform of the masked
spectrum. By linearity of the inverse transform and unitarity,</p>
<p class="eq">&#8214;x &minus; x&#770;&#8214;<sup>2</sup>
= &#8214;X &minus; X&#770;&#8214;<sup>2</sup>
= &sum;<sub>k&notin;K</sub>|X[k]|<sup>2</sup>
= E &minus; &sum;<sub>k&isin;K</sub>|X[k]|<sup>2</sup>
= (1&minus;&eta;)E,</p>
<p>where the second equality holds because the retained and discarded index sets
are disjoint, so the corresponding subspaces are orthogonal. Dividing by
&#8214;x&#8214;<sup>2</sup> = E and taking the square root:</p>
<p class="eq"><strong>&epsilon;<sub>L2</sub> = &radic;(1 &minus; &eta;).</strong> &#9633;</p>
<div class="note"><strong>Interpretive consequence.</strong> The relation holds
for <em>any</em> orthonormal transform and for &eta; and &epsilon; computed on
the same basis. It follows that retained energy and relative L2 error are the
same information under a monotone transformation. Reporting both therefore
cannot corroborate either, and the remedy of "quoting a reconstruction error
alongside the energy figure" is ineffective. Verified against 324 independent
retention measurements; maximum deviation
1.0&nbsp;&times;&nbsp;10<sup>&minus;14</sup>.</div>

<h2>D4. Basis conversion (Equation 8)</h2>
<p>Suppose the DC bin is retained, K &ni; 0. Write
E<sub>DC</sub> = |X[0]|<sup>2</sup> and
E<sub>AC</sub> = E &minus; E<sub>DC</sub>. The retained energy splits as</p>
<p class="eq">&sum;<sub>k&isin;K</sub>|X[k]|<sup>2</sup>
= E<sub>DC</sub> + &sum;<sub>k&isin;K, k&ne;0</sub>|X[k]|<sup>2</sup>
= E<sub>DC</sub> + &eta;<sub>AC</sub>&nbsp;E<sub>AC</sub>,</p>
<p>by definition of &eta;<sub>AC</sub>. Hence</p>
<p class="eq">1 &minus; &eta;<sub>total</sub>
= (E &minus; E<sub>DC</sub> &minus; &eta;<sub>AC</sub>E<sub>AC</sub>)/E
= E<sub>AC</sub>(1&minus;&eta;<sub>AC</sub>)/E
= (1&minus;&eta;<sub>AC</sub>)(1&minus;&eta;<sub>DC</sub>),</p>
<p>and substituting D2 gives</p>
<p class="eq"><strong>1 &minus; &eta;<sub>total</sub>
= (1 &minus; &eta;<sub>AC</sub>)/(1 + r<sup>2</sup>).</strong> &#9633;</p>
<p>The two reporting bases are therefore related by a factor determined entirely
by r. This is why the reporting protocol requires r to be stated: it is a
<em>sufficient statistic</em> for converting a published retention figure into
the other convention. Maximum deviation over the corpus and offset sweep:
2.2&nbsp;&times;&nbsp;10<sup>&minus;16</sup>.</p>

<h2>D5. Error scaling (Equation 9)</h2>
<p>Apply D3 on each basis: &epsilon;<sub>full</sub> =
&radic;(1&minus;&eta;<sub>total</sub>) and &epsilon;<sub>AC</sub> =
&radic;(1&minus;&eta;<sub>AC</sub>). Substituting D4,</p>
<p class="eq">&epsilon;<sub>full</sub>
= &radic;((1&minus;&eta;<sub>AC</sub>)/(1+r<sup>2</sup>))
= &epsilon;<sub>AC</sub>/&radic;(1+r<sup>2</sup>). &#9633;</p>
<p>For the recovered baseline &radic;(1+r<sup>2</sup>) = 3.8301: an error of
34.80% on the fluctuation is reported as 9.08% on the full signal. Maximum
deviation: 1.1&nbsp;&times;&nbsp;10<sup>&minus;16</sup>.</p>

<h2>D6. Why the modulation operation is not an inverse</h2>
<p>The earlier work labels x1[n] = (&minus;1)<sup>n</sup>x[n] as "the inverse of
the function". Since (&minus;1)<sup>n</sup> = exp(j&pi;n) = exp(j2&pi;(N/2)n/N)
for even N, this is modulation by the Nyquist frequency. By the modulation
theorem,</p>
<p class="eq">X<sub>1</sub>[k] = (1/&radic;N)&sum;<sub>n</sub>x[n]
exp(j2&pi;(N/2)n/N) exp(&minus;j2&pi;kn/N)
= X[(k &minus; N/2) mod N],</p>
<p>a circular shift of the spectrum by N/2 = 13 bins. This was confirmed
numerically: the coefficient table of the earlier work is its own earlier table
rolled by exactly 13 positions. The operation is correct and instructive; it is
not an inverse of anything, and the DFT, the inverse DFT, modulation, spectral
shift and reconstruction are distinguished strictly throughout the manuscript.</p>

<h2>D7. On "verifying" Parseval's identity</h2>
<p>Under a unitary transform, E = H is an algebraic consequence of unitarity and
holds for every input. A numerical procedure that computes both sides and
compares them therefore <em>cannot produce a negative result</em>, and has no
empirical content: it discriminates between no hypotheses. What such a
computation does measure is the accumulation of floating-point error, which is
a property of the arithmetic and the implementation rather than of the theorem.
That quantity is reported in Section&nbsp;VIII-J as
&epsilon;<sub>P</sub>, and its scale relative to the modeling error is the
substantive finding.</p>
"""


def tables_doc() -> str:
    specs = [
        ("table01_recovered_dataset_summary", "Table S1. Recovered dataset summary and recovery validation evidence.", None),
        ("table02_historical_verification", "Table S2. Independent verification of the 2013/2014 results.", None),
        ("table03_signal_corpus", "Table S3. Signal corpus definitions and generating parameters.", None),
        ("table04_corpus_statistics", "Table S4. Corpus statistics and DC energy share.", None),
        ("table05_experiment_a_dc_sweep", "Table S5. Experiment A: measured against analytical DC energy share.", None),
        ("table06_energy_thresholds", "Table S6. Coefficients required per energy threshold, both bases, all corpus members.", 40),
        ("table07_selection_curves", "Table S7. Retention curves for all strategy and basis combinations.", 40),
        ("table08_dft_vs_dct", "Table S8. DFT against DCT-II coefficient counts at fixed thresholds.", None),
        ("table09_leakage_and_windows", "Table S9. Spectral leakage and window characteristics.", None),
        ("table10_noise_summary", "Table S10. Noise robustness summary, 100 realizations per level.", None),
        ("table11_numerical_precision", "Table S11. Parseval discrepancy against transform length and precision.", None),
        ("table12_validation_checks", "Table S12. All numerical validation gates, measured values and tolerances.", None),
    ]
    out = ["<h1>Supplementary Tables</h1>",
           "<p>All twelve tables produced by the analysis pipeline. Every table is "
           "regenerated by <code>code/reproduce_all.py</code> and is also available "
           "as CSV and Markdown in <code>tables/</code>. Units are dimensionless "
           "unless stated; energies are in squared signal units; &epsilon; and "
           "&eta; are ratios; SNR is in dB; abbreviations follow the manuscript "
           "(&eta; retained energy, &epsilon;<sub>L2</sub> relative L2 error, "
           "&epsilon;<sub>P</sub> Parseval discrepancy, AC mean-removed basis).</p>"]
    for stem, cap, cap_rows in specs:
        out.append(f"<h2>{cap}</h2>")
        out.append(f"<p><em>Source: tables/{stem}.csv</em></p>")
        out.append(table_html(stem, cap_rows))
    return "\n".join(out)


def figures_doc() -> str:
    caps = [
        ("fig01_recovered_baseline", "Figure S1. Recovered baseline sequence, its 11-coefficient and DC-only reconstructions, and the magnitude spectrum."),
        ("fig02_dc_energy_share_sweep", "Figure S2. Experiment A: measured DC energy share against the analytical prediction, and the divergence of retention from fidelity as the offset grows."),
        ("fig03_total_energy_vs_error", "Figure S3. The redundancy result: all retention curves lie exactly on the identity, and the two error measures differ by a fixed factor."),
        ("fig04_ac_energy_vs_error", "Figure S4. AC-basis retention against reconstruction error across the corpus."),
        ("fig05_selection_strategies", "Figure S5. Coefficient count against reconstruction error for all strategy and basis combinations."),
        ("fig06_dft_vs_dct", "Figure S6. DFT against orthonormal DCT-II compaction, mean-removed."),
        ("fig07_spectral_leakage", "Figure S7. Spectral leakage for bin-centered and off-bin sinusoids."),
        ("fig08_window_comparison", "Figure S8. Window frequency responses and their effect at a fixed coefficient budget."),
        ("fig09_noise_robustness", "Figure S9. Retention and fidelity against input SNR, with 95% confidence intervals for the mean."),
        ("fig10_parseval_precision", "Figure S10. Parseval discrepancy against transform length and floating-point precision."),
    ]
    out = ["<h1>Supplementary Figures</h1>",
           "<p>All ten figures at publication resolution. Vector originals (PDF, SVG) "
           "and 600&nbsp;dpi raster versions are in <code>figures/</code>. Every "
           "figure is generated from computed data by <code>plotting.py</code>; none "
           "contains illustrative or invented values. The palette is Okabe&ndash;Ito "
           "and every series carries a redundant marker or line style, so no "
           "information is conveyed by color alone.</p>"]
    for stem, cap in caps:
        # LibreOffice cannot resolve filesystem paths in <img src>; embed the
        # image directly so the PDF is self-contained.
        png = (ROOT / "figures" / f"{stem}.png").read_bytes()
        uri = "data:image/png;base64," + base64.b64encode(png).decode()
        out.append(f'<figure><img src="{uri}">'
                   f'<figcaption>{cap}</figcaption></figure>')
    return "\n".join(out)


def extended() -> str:
    noise = pd.read_csv(ROOT / "data" / "signal_corpus" / "S6_noise" /
                        "per_realization.csv")
    desc = noise.groupby("snr_db")[
        ["eta_total", "eta_ac", "eps_l2_vs_clean", "eps_l2_ac_vs_clean"]
    ].describe().T
    sel = pd.read_csv(ROOT / "tables" / "table07_selection_curves.csv")
    thr = pd.read_csv(ROOT / "tables" / "table06_energy_thresholds.csv")
    return f"""
<h1>Extended Results</h1>
<p>Results too voluminous for the main manuscript. All are regenerated by
<code>code/reproduce_all.py</code>.</p>

<h2>E1. Noise experiment: full distributional summary</h2>
<p>Per-realization records: {len(noise)} rows
({len(noise) // noise['snr_db'].nunique()} realizations at each of
{noise['snr_db'].nunique()} SNR levels), master seed 20260826. The complete
record is in <code>data/signal_corpus/S6_noise/per_realization.csv</code>.
Quartiles are given so that the distribution can be inspected directly rather
than summarized only by mean and standard deviation.</p>
{desc.to_html(float_format=lambda v: f"{v:.5g}", border=0)}

<h2>E2. Complete retention curves</h2>
<p>All {len(sel)} retention measurements across corpus members, strategies and
bases. These are the measurements against which the identity
&epsilon;<sub>L2</sub> = &radic;(1&minus;&eta;) was tested.</p>
{sel.head(60).to_html(index=False, float_format=lambda v: f"{v:.6g}", border=0)}
<p><em>First 60 of {len(sel)} rows; the complete table is in
<code>tables/table07_selection_curves.csv</code>.</em></p>

<h2>E3. Energy thresholds, all corpus members</h2>
<p>All {len(thr)} threshold measurements. The comparison between the two bases
for any single signal is the practical statement of the confound.</p>
{thr.to_html(index=False, float_format=lambda v: f"{v:.6g}", border=0)}
"""


def main() -> None:
    for stem, builder in (("supplementary_methods", methods),
                          ("mathematical_derivations", derivations),
                          ("supplementary_tables", tables_doc),
                          ("supplementary_figures", figures_doc),
                          ("extended_results", extended)):
        p = html_to_pdf(builder(), stem)
        print(f"wrote {p.name}  ({p.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
