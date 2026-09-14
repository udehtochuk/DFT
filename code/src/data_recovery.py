"""
data_recovery.py
================
Recovery of the source sequence of the 2013/2014 study from the transform
coefficients printed in that paper.

Rationale
---------
The original data file ("data.txt") is unavailable. The source paper prints
Re{.} and Im{.} of its transform coefficients for k = 0..14 of a real sequence
with N = 26. For a real sequence, bins k = 0..13 carry all 26 degrees of
freedom (bin 0 real, bins 1..12 complex, bin 13 real at Nyquist:
1 + 2*12 + 1 = 26); Hermitian symmetry supplies bins 14..25. Inverting
therefore recovers the sequence.

IMPORTANT: the paper's coefficients are in ITS convention (positive analysis
exponent). Recovery must invert that convention, not the one adopted for the
new study. See transforms.legacy_transform_1314.

Provenance: RECOVERED HISTORICAL DATA. Not synthetic. Not the original file.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from transforms import dft_matrix

__all__ = [
    "PUBLISHED_YC", "PUBLISHED_YS", "PUBLISHED_X_PARTIAL", "N_SAMPLES",
    "recover_sequence", "recovery_report",
]

N_SAMPLES = 26

#: Re{ye[k]}, k = 0..14, exactly as printed in the 2013/2014 paper.
PUBLISHED_YC: tuple[float, ...] = (
    1.256e3, -38.105, -0.581, 61.712, -49.297, 28.821, 24.561, 30.061,
    -16.164, 17.518, -15.845, -17.049, 7.905, -43.538, 7.905)

#: Im{ye[k]}, k = 0..14, exactly as printed in the 2013/2014 paper.
PUBLISHED_YS: tuple[float, ...] = (
    0.0, 42.521, -166.939, -50.205, 99.563, -10.445, -33.356, 4.529,
    -12.669, -23.870, -29.123, 8.718, -23.975, 2.154e-12, 23.975)

#: The 15 sample values (of 26) printed in the 2013/2014 paper. Validation only.
PUBLISHED_X_PARTIAL: tuple[int, ...] = (
    251, 214, 195, 175, 174, 173, 198, 295, 403, 388, 318, 288, 232, 203, 215)


def _published_spectrum_legacy() -> NDArray[np.complex128]:
    """Full length-26 spectrum in the PAPER'S convention, by Hermitian extension."""
    spec = np.zeros(N_SAMPLES, dtype=np.complex128)
    spec[:14] = [complex(a, b) for a, b in zip(PUBLISHED_YC[:14], PUBLISHED_YS[:14])]
    for k in range(14, N_SAMPLES):
        spec[k] = np.conj(spec[N_SAMPLES - k])
    return spec


def recover_sequence(round_to_integer: bool = True) -> NDArray[np.float64]:
    """
    Recover x[0..25] from the published coefficients.

    The paper's analysis kernel is exp(+j2*pi*k*n/N) with 1/sqrt(N) scaling, so
    the corresponding synthesis kernel carries exp(-j2*pi*k*n/N).

    Validation (see `recovery_report`) shows the underlying data are integers
    and that the residual against the printed samples is a uniform offset
    attributable to the DC coefficient being printed to four significant
    figures. `round_to_integer=True` therefore returns the integer sequence.
    """
    spec = _published_spectrum_legacy()
    # Inverse of the legacy (positive-exponent) transform = negative-exponent matrix.
    x = dft_matrix(N_SAMPLES, inverse=False) @ spec
    if np.max(np.abs(x.imag)) > 1e-9:
        raise AssertionError("recovered sequence is not real - recovery failed")
    x = x.real
    return np.round(x) if round_to_integer else x


def recovery_report() -> dict[str, object]:
    """Validation evidence for the recovery. Every field is computed, not asserted."""
    raw = recover_sequence(round_to_integer=False)
    rounded = recover_sequence(round_to_integer=True)
    printed = np.array(PUBLISHED_X_PARTIAL, dtype=float)
    residual = raw[:15] - printed

    spec = _published_spectrum_legacy()
    return {
        "n_samples": N_SAMPLES,
        "max_imag_part": float(np.max(np.abs(
            (dft_matrix(N_SAMPLES) @ spec).imag))),
        "residual_vs_printed_min": float(residual.min()),
        "residual_vs_printed_max": float(residual.max()),
        # The residual is dominated by DC rounding (a constant offset) but is
        # not exactly constant: the remaining spread comes from the other
        # printed coefficients being rounded to three decimals. Reported as a
        # number rather than asserted as a boolean.
        "residual_spread_ptp": float(np.ptp(residual)),
        "residual_mean_offset": float(residual.mean()),
        "dc_rounding_predicted_offset": float(
            (PUBLISHED_YC[0] - rounded.sum() / np.sqrt(N_SAMPLES)) / np.sqrt(N_SAMPLES)),
        "max_abs_residual_after_rounding": float(
            np.max(np.abs(rounded[:15] - printed))),
        "max_distance_to_integer": float(np.max(np.abs(raw - np.round(raw)))),
        # Internal-consistency checks on the PRINTED coefficients themselves.
        "printed_k14_equals_conj_k12": bool(np.isclose(
            complex(PUBLISHED_YC[14], PUBLISHED_YS[14]),
            np.conj(complex(PUBLISHED_YC[12], PUBLISHED_YS[12])))),
        "printed_nyquist_imag": float(PUBLISHED_YS[13]),
        # Implied true DC value if the integer sequence is correct.
        "dc_printed": PUBLISHED_YC[0],
        "dc_implied": float(rounded.sum() / np.sqrt(N_SAMPLES)),
        "sequence": rounded.astype(int).tolist(),
        "mean": float(rounded.mean()),
        "std_population": float(rounded.std()),
        "r_mean_over_std": float(rounded.mean() / rounded.std()),
        "minimum": float(rounded.min()),
        "maximum": float(rounded.max()),
        "sum": int(rounded.sum()),
    }
