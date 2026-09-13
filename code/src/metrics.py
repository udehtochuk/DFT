"""
metrics.py
==========
Performance metrics. All energies assume the unitary convention of
`transforms` (Parseval: sum |x[n]|^2 == sum |X[k]|^2).

Metric roles, stated explicitly because the distinction is the subject of this
study:

  * eta_total, eta_ac  -- energy-ACCOUNTING quantities. They say how much
    squared magnitude a coefficient subset carries. They are NOT fidelity
    measures.
  * eps_l2, rmse, snr  -- reconstruction FIDELITY measures.
  * eps_parseval       -- a NUMERICAL-ACCURACY diagnostic only. It is never
    evidence that Parseval's theorem "holds": that is analytic.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = [
    "total_energy", "dc_energy_share", "dc_share_theoretical",
    "l2_error_from_retention", "total_from_ac_retention",
    "l2_scaling_factor",
    "energy_retention_total", "energy_retention_ac",
    "relative_l2_error", "rmse", "reconstruction_snr_db",
    "parseval_discrepancy", "compression_ratio", "summarize_reconstruction",
]


def total_energy(x: NDArray) -> float:
    """E = sum |x[n]|^2."""
    return float(np.sum(np.abs(np.asarray(x)) ** 2))


def dc_energy_share(spectrum: NDArray) -> float:
    """eta_DC = |X[0]|^2 / E, measured from the spectrum."""
    spectrum = np.asarray(spectrum)
    denom = np.sum(np.abs(spectrum) ** 2)
    if denom == 0:
        raise ZeroDivisionError("zero-energy signal")
    return float(np.abs(spectrum[0]) ** 2 / denom)


def dc_share_theoretical(r: float) -> float:
    """
    Analytical DC energy share for a real sequence:

        eta_DC = mu^2 / (mu^2 + sigma^2) = r^2 / (1 + r^2),   r = mu / sigma

    Derivation: |X[0]|^2 = N*mu^2 and E = N*(mu^2 + sigma^2) with sigma the
    population standard deviation. This is a corollary of Parseval, not a new
    result. For sigma = 0 the ratio is defined as 1 by continuity.
    """
    r = float(r)
    if not np.isfinite(r):
        return 1.0
    return r ** 2 / (1.0 + r ** 2)


def l2_error_from_retention(eta: float) -> float:
    """
    Exact relation for ANY orthonormal transform:

        eps_L2 = sqrt(1 - eta)

    Proof: the retained and discarded subspaces are orthogonal, so
    ||x - x_hat||^2 = sum_{discarded} |X[k]|^2 = (1 - eta) * E, and dividing by
    ||x||^2 = E gives the result.

    CONSEQUENCE, and the reason this function exists: retained energy and
    relative L2 error computed on the SAME basis are the same information in
    two forms. Reporting both adds nothing. What distinguishes an informative
    report from an uninformative one is the BASIS, not the choice of metric.
    """
    return float(np.sqrt(max(0.0, 1.0 - float(eta))))


def total_from_ac_retention(eta_ac: float, r: float) -> float:
    """
    Exact conversion between reporting bases when the DC bin is retained:

        1 - eta_total = (1 - eta_AC) * (1 - eta_DC) = (1 - eta_AC) / (1 + r^2)

    so eta_total = 1 - (1 - eta_AC) / (1 + r^2). The mean-to-standard-deviation
    ratio r is therefore a sufficient statistic for translating between the two
    bases, which is why the reporting protocol requires r to be stated.
    """
    return float(1.0 - (1.0 - float(eta_ac)) / (1.0 + float(r) ** 2))


def l2_scaling_factor(r: float) -> float:
    """
    Exact ratio between the two error measures when DC is retained:

        eps_L2(full signal) = eps_L2(fluctuation) / sqrt(1 + r^2)

    At r = 3.697 (the recovered baseline) the factor is 3.83: an error of 35%
    on the fluctuation is reported as 9% on the full signal.
    """
    return float(np.sqrt(1.0 + float(r) ** 2))


def energy_retention_total(spectrum: NDArray, mask: NDArray) -> float:
    """eta_total = retained spectral energy / total spectral energy."""
    spectrum, mask = np.asarray(spectrum), np.asarray(mask, dtype=bool)
    denom = np.sum(np.abs(spectrum) ** 2)
    if denom == 0:
        raise ZeroDivisionError("zero-energy signal")
    return float(np.sum(np.abs(spectrum[mask]) ** 2) / denom)


def energy_retention_ac(spectrum: NDArray, mask: NDArray) -> float:
    """
    eta_AC = retained non-DC spectral energy / total non-DC spectral energy.
    The DC bin is excluded from BOTH numerator and denominator.
    """
    spectrum, mask = np.asarray(spectrum), np.asarray(mask, dtype=bool).copy()
    ac = np.abs(spectrum) ** 2
    ac[0] = 0.0
    denom = float(np.sum(ac))
    total = float(np.sum(np.abs(spectrum) ** 2))
    # A constant signal has AC energy of order 1e-32 rather than exactly zero,
    # so the guard must be relative: below this level the "AC basis" is
    # rounding noise and any ratio formed from it is meaningless.
    if total <= 0 or denom <= 1e-20 * total:
        raise ZeroDivisionError(
            "signal has no alternating component: the AC basis is undefined")
    mask[0] = False
    return float(np.sum(ac[mask]) / denom)


def relative_l2_error(x: NDArray, x_hat: NDArray) -> float:
    """eps_L2 = ||x - x_hat||_2 / ||x||_2. Dimensionless and scale-invariant."""
    x, x_hat = np.asarray(x, dtype=float), np.asarray(np.real(x_hat), dtype=float)
    nrm = np.linalg.norm(x)
    if nrm == 0:
        raise ZeroDivisionError("zero-norm reference signal")
    return float(np.linalg.norm(x_hat - x) / nrm)


def rmse(x: NDArray, x_hat: NDArray) -> float:
    """Root-mean-square error, in the units of the signal."""
    x, x_hat = np.asarray(x, dtype=float), np.asarray(np.real(x_hat), dtype=float)
    return float(np.sqrt(np.mean((x_hat - x) ** 2)))


def reconstruction_snr_db(x: NDArray, x_hat: NDArray) -> float:
    """10*log10( sum x^2 / sum (x - x_hat)^2 ). Infinite for exact recovery."""
    x, x_hat = np.asarray(x, dtype=float), np.asarray(np.real(x_hat), dtype=float)
    err = float(np.sum((x_hat - x) ** 2))
    if err == 0:
        return float("inf")
    return float(10.0 * np.log10(np.sum(x ** 2) / err))


def parseval_discrepancy(x: NDArray, spectrum: NDArray) -> float:
    """
    eps_P = |E_time - E_freq| / E_time.

    NUMERICAL diagnostic only. Under a unitary transform the identity is
    analytic; any non-zero value here measures finite-precision arithmetic,
    not the validity of the theorem.
    """
    e_time = float(np.sum(np.asarray(x, dtype=np.float64) ** 2))
    e_freq = float(np.sum(np.abs(np.asarray(spectrum, dtype=np.complex128)) ** 2))
    if e_time == 0:
        raise ZeroDivisionError("zero-energy signal")
    return abs(e_time - e_freq) / e_time


def compression_ratio(mask: NDArray) -> float:
    """Retained coefficients / total coefficients."""
    mask = np.asarray(mask, dtype=bool)
    return float(mask.sum() / mask.size)


def summarize_reconstruction(x: NDArray, x_hat: NDArray, spectrum: NDArray,
                             mask: NDArray) -> dict[str, float]:
    """All primary metrics for one retention set. Energy is never reported alone."""
    return {
        "n_coeff": int(np.asarray(mask, dtype=bool).sum()),
        "coeff_ratio": compression_ratio(mask),
        "eta_total": energy_retention_total(spectrum, mask),
        "eta_ac": energy_retention_ac(spectrum, mask),
        "eps_l2": relative_l2_error(x, x_hat),
        "rmse": rmse(x, x_hat),
        "snr_db": reconstruction_snr_db(x, x_hat),
        "max_imag": float(np.max(np.abs(np.imag(np.asarray(x_hat, dtype=complex))))),
    }
