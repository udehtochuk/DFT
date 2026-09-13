# Venue Assessment and Hostile Review

Prepared 26 August 2026, after the study was completed. Written to be
uncomfortable rather than reassuring: the point of the exercise is to find the
objections before a reviewer does.

---

## Part 1, Hostile peer review

### Challenge 1: "Isn't DC dominance obvious?"

**Partly conceded.** That a large mean produces a large DC coefficient is
obvious to anyone who has written down the transform. Nobody should be told
that as news, and the manuscript does not present it as news.

What is not obvious, and what the paper contributes, is the rest:

- The relationship is exact and has a closed form, η_DC = r²/(1+r²), so the
  effect is *predictable* from two summary statistics rather than something to
  be checked case by case. At r = 3, 90% of the energy is already in the mean.
- The magnitude is larger than intuition suggests. An ordinary offset signal, 
  r = 3.7, nothing extreme, puts 93.2% of its energy in one coefficient of 26.
- The consequence for reporting is genuinely counter-intuitive: because
  ε = √(1−η) exactly, an author who notices the problem and adds a
  reconstruction error to the report has added nothing. **That** is not obvious,
  and it is the paper's substantive point.

If a reviewer accepts only the first sentence of this reply, the paper is worth
less. The manuscript says so in its limitations rather than hoping the reviewer
will not notice.

### Challenge 2: "Isn't mean removal standard practice?"

**Yes, in transform coding, conceded without qualification.** Ahmed, Natarajan
and Rao benchmark against first-order Markov sources that are zero-mean by
construction, and the fiftieth-anniversary retrospective restates the framework
unchanged. This paper does not propose mean removal as a discovery, and it cites
that literature as establishing the state of the art.

The contribution concerns metric *interpretation* and *reporting* outside that
context. In transform coding the assumption is structural: the analysis simply
is not performed on offset data. Where retention percentages are quoted as
fidelity figures in instructional and applied work, that structural guarantee is
absent and nothing in the standard treatments flags it, because within those
treatments it never needs flagging.

A reviewer is entitled to respond that a gap in *transfer* is a weaker
contribution than a gap in *theory*. That is correct, and it drives the venue
recommendation below.

### Challenge 3: "What is new?"

Precisely this, and nothing beyond it:

1. **The redundancy result.** ε = √(1−η) on a common basis, so energy retention
   and reconstruction error cannot corroborate each other. The obvious remedy is
   ineffective. I have not seen this stated.
2. **The basis-conversion law**, making r a sufficient statistic for translating
   between reporting conventions, which converts "report more carefully" into a
   specific, checkable instruction.
3. **A verified, corrected, fully reproducible case study**, including recovery
   of data that had been lost.
4. **The recovery technique itself**: Hermitian inversion of published
   coefficients, transferable to any lost-data paper whose real-signal spectrum
   was printed.

Not new, and not claimed: DC dominance; mean removal; DCT superiority; sparse
Fourier theory; anything about Parseval's identity itself.

### Challenge 4: "Why only N = 26?"

Because that is the length of the recovered historical record, and the
replication component requires exactly it.

The generality objection was valid against an earlier draft and is answered by
Experiment A, which is not a robustness afterthought but the study's central
controlled test. Seven signals spanning r ∈ {0, 0.5, 1, 2, 4, 8, 16}, with the
fluctuation held *exactly* fixed so that only the DC bin varies, verified as a
precondition, not assumed. The corpus adds five further signal classes, four
noise levels with 100 realizations each, and a transform-length sweep to
N = 4096 in the precision experiment.

The honest residual limitation is different from the one the challenge names:
the corpus is *synthetic and designed by the author*. It shows the mechanism
operates across signal classes. It cannot show which values of r occur in any
real application domain, and the manuscript does not claim otherwise.

### Challenge 5: "Why should anyone care?"

Quantitatively:

- The same signal, the same nominal question, "how many coefficients for 95% of
  the energy?", answers **3 or 17** depending on an unstated convention. A
  factor of 5.7 in a compression figure of merit.
- A reconstruction reported as **99.175% of energy retained** has a **9.08%**
  relative error on the full signal and **34.8%** on the component of interest.
- Under noise the metric becomes *more* misleading, not less: at 0 dB SNR it
  still reads **95.8%** while the fluctuation is **71.5%** wrong. Noise is
  zero-mean, so it lands in exactly the bins the metric ignores.

A reader who does not care about compression ratios being wrong by a factor of
five need not read further.

### Challenge 6: "Why not just use reconstruction error?"

This is the best objection, and answering it is the paper's contribution.

The intuitive answer is "yes, just use error." But by ε = √(1−η), reconstruction
error on the total basis *is* the energy figure, re-expressed. Substituting one
for the other changes nothing, and an author who does so may reasonably believe
the problem is fixed when it is not.

Retained energy is worth keeping for two reasons. It is additive over
coefficients, so it supports incremental selection in a way error does not; and
it is the quantity in which rate-distortion arguments are conventionally posed.
The paper therefore proposes reporting both *with the basis stated*, and reports
r so a reader can convert. That is not "add a metric", it is "state which
question you answered."

### Challenge 7: "Is this appropriate for IEEE Transactions on Signal Processing?"

**No.** It should not be submitted there and would be correctly rejected.

TSP's threshold is a methodological or theoretical advance in signal processing.
This paper contributes no new transform, no new algorithm, no new bound and no
new theory: its four relations are corollaries of Parseval that fit on one page.
A TSP reviewer would ask what the paper adds beyond 1974, and the honest answer, 
a reporting protocol and a reproducible case study, does not meet that bar.

Submitting it there would waste reviewer time and invite a rejection that the
author would have no grounds to contest.

---

## Part 2, Venue assessment

### IEEE Transactions on Signal Processing

| | |
|---|---|
| Scope fit | Good |
| Novelty required | High: new theory, algorithms or bounds |
| Likely objections | "Corollary of Parseval"; "mean removal is standard"; "N = 26 baseline"; "no algorithmic contribution" |
| Strengths here | Mathematical rigor; full reproducibility; verified corrections |
| Weaknesses here | No theoretical novelty whatsoever; contribution is a reporting protocol |
| **Realistic suitability** | **Unsuitable. Do not submit.** Desk rejection likely and deserved. |

### IEEE Transactions on Education

| | |
|---|---|
| Scope fit | Strong: metric interpretation and reporting practice in DSP instruction |
| Novelty required | Moderate; pedagogical value counts |
| Likely objections | "Where is the evidence students actually make this error?"; no learner study |
| Strengths here | A documented real case; closed-form mechanism; open package a reader can run; the redundancy result is genuinely instructive |
| Weaknesses here | No educational intervention or learner evaluation; the practice claim is not evidenced |
| **Realistic suitability** | **Strong. Recommended primary target.** Expect major revision requesting either evidence of prevalence or a softened claim, both are already prepared. |

### IEEE Signal Processing Magazine (Lecture Notes / Tips & Tricks)

| | |
|---|---|
| Scope fit | Very strong for the column format |
| Novelty required | Low; clarity and utility dominate |
| Likely objections | Length; whether the point sustains a full article; house style |
| Strengths here | One-figure argument (Fig. 2); a memorable and correct message; strong visuals |
| Weaknesses here | Column formats are invited or tightly scoped; the replication component may need cutting |
| **Realistic suitability** | **Strong, with restructuring.** Highest-visibility route to the audience that commits the error. Title option 3 suits this venue better. |

### EURASIP Journal on Advances in Signal Processing

| | |
|---|---|
| Scope fit | Good; methodology and reproducibility both in scope |
| Novelty required | Moderate |
| Likely objections | Incremental contribution; single real signal |
| Strengths here | Complete open package; controlled experimental design; rigorous validation |
| Weaknesses here | Synthetic corpus; no application-domain data |
| **Realistic suitability** | **Good. Recommended alternative.** Open access suits a paper whose value depends on being read by practitioners. |

### A reproducibility or methods venue (e.g. *Scientific Data*, ReScience C)

| | |
|---|---|
| Scope fit | Strong for the recovery and replication component specifically |
| Novelty required | Low; rigor and reusability dominate |
| Likely objections | Data provenance unknown; a single small dataset |
| Strengths here | Data recovered from a lost source, fully documented; FAIR-aligned; a transferable recovery technique |
| Weaknesses here | The analytical contribution may be out of scope; dataset is small and of unknown origin |
| **Realistic suitability** | **Viable, best as a companion.** The recovery technique could stand alone as a short data/methods paper. |

### Recommendation

1. **IEEE Transactions on Education**, primary.
2. **IEEE Signal Processing Magazine** (column), highest impact if the format
   can be secured; restructure around Figure 2.
3. **EURASIP JASP**, solid alternative, open access.

Do not submit to IEEE TSP. Prestige is not a reason, and the paper's own
assessment of its novelty is the reason not to.

---

## Part 3, Publication-readiness scoring

Scored against the completed study, not the aspiration.

| Criterion | Score / 100 | Basis |
|---|---|---|
| Originality | 61 | Redundancy result and conversion law are genuine and, I believe, unstated. Mechanism is a Parseval corollary. |
| Significance | 66 | Factor-of-5.7 consequence is concrete; bounded by an unevidenced prevalence claim. |
| Mathematical rigor | 93 | Four relations derived and verified to machine precision; single stated convention; 32 gates. |
| Methodology | 86 | Controlled design with the manipulation verified as a precondition; competing explanations tested and excluded. |
| Experimental quality | 84 | Eight experiments executed; 100 realizations per noise level; corpus synthetic. |
| Literature | 74 | 10 of 14 references verified at source; decorative references removed; list is compact. |
| Reproducibility | 97 | One command, 11 seconds, 49 tests, 32 gates, checksums, executable notebooks. |
| Writing | 87 | Structured, hedged where the evidence is thin, explicit about non-claims. |
| Standards compliance | 88 | IEEE structure and citation style; verification markers must be cleared. |
| Publication readiness | 79 | Ready for the recommended venues after clearing reference markers. |

**Weighted overall: 82 / 100.**

### Verdict

> **Minor revision required**, for IEEE Transactions on Education, IEEE Signal
> Processing Magazine, or EURASIP JASP.
>
> **Reject**, for IEEE Transactions on Signal Processing, on novelty grounds.
> This assessment would be correct and should not be contested.

This is an increase from the 70/100 assessed at the forensic-review stage. The
increase is attributable to specific work, not to presentation: Experiment A
replaced a single-signal evidence base with a controlled design; three exact
relations replaced an informal observation; and one of the review's own
recommendations was found to be wrong and corrected.

### Remaining items before submission

1. Clear the four `[REFERENCE REQUIRES MANUAL VERIFICATION]` markers and confirm
   the omitted DOI for reference [7].
2. Resolve the textual-similarity matter concerning the prior work
   (`research_integrity_statement.md`, §2).
3. Insert affiliation, email, ORCID and the repository URL; deposit the package
   and mint a DOI.
4. Either evidence the prevalence claim in Section III with a structured survey,
   or soften it further. Softened wording is already in place; a survey would
   raise Significance materially.
5. Reformat to the target venue's template.

None of these is a research task except item 4.
