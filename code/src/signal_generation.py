"""
signal_generation.py
====================
The controlled signal corpus (S0-S6) and the offset sweep of Experiment A.

Provenance classes, kept distinct throughout the package:
  RECOVERED  S0 only - the 2013/2014 sequence recovered from published data.
  SYNTHETIC  S1-S5, and the Experiment A sweep - deterministic, no RNG except
             S4 which uses a documented fixed seed.
  STOCHASTIC S6 - repeated noise realizations under a documented seed.

No signal here is claimed to be physical data. The physical identity, units
and sampling rate of S0 are unknown and are not invented: all signals are
treated as dimensionless sequences with a normalized frequency axis.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from data_recovery import recover_sequence

__all__ = [
    "MASTER_SEED", "Signal", "make_S0", "make_S1", "make_S2", "make_S3",
    "make_S4", "make_S5", "make_S6_realizations", "offset_sweep",
    "build_corpus", "R_SWEEP_VALUES", "SNR_LEVELS_DB",
]

#: Single documented master seed. All stochastic components derive from it.
MASTER_SEED = 20260826

#: Mean-to-standard-deviation ratios for Experiment A.
R_SWEEP_VALUES: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)

#: SNR levels for the S6 noise experiment.
SNR_LEVELS_DB: tuple[float, ...] = (30.0, 20.0, 10.0, 0.0)


@dataclass(frozen=True)
class Signal:
    """A corpus member with its provenance and generating parameters."""
    ident: str
    name: str
    provenance: str            # "recovered" | "synthetic" | "stochastic"
    samples: NDArray[np.float64]
    description: str
    params: dict = field(default_factory=dict)

    @property
    def n(self) -> int:
        return int(self.samples.size)

    @property
    def mean(self) -> float:
        return float(self.samples.mean())

    @property
    def std(self) -> float:
        return float(self.samples.std())

    @property
    def r(self) -> float:
        return float("inf") if self.std == 0 else self.mean / self.std


def _set_ratio(fluctuation: NDArray, r: float) -> NDArray[np.float64]:
    """
    Add a constant offset so that mean/std equals `r`, leaving the fluctuation
    (and hence the entire AC spectrum) untouched. This is the control that
    makes Experiment A a clean test: only the DC bin changes.
    """
    f = np.asarray(fluctuation, dtype=float)
    f = f - f.mean()                     # ensure exactly zero mean
    sigma = f.std()
    if sigma == 0:
        raise ValueError("fluctuation has zero standard deviation")
    return f + r * sigma


def make_S0() -> Signal:
    """Recovered 2013/2014 baseline. RECOVERED HISTORICAL DATA."""
    return Signal(
        ident="S0", name="Recovered historical baseline", provenance="recovered",
        samples=recover_sequence(),
        description=("The 26-sample sequence of the 2013/2014 study, recovered "
                     "by Hermitian inversion of its published coefficients. "
                     "Physical identity, units and sampling rate unknown."),
        params={"N": 26, "source": "Udeh (2013/2014), recovered"})


def make_S1(n: int = 26, bin_index: int = 3, amplitude: float = 1.0) -> Signal:
    """Zero-mean sinusoid exactly on DFT bin `bin_index`. Maximal concentration."""
    t = np.arange(n)
    x = amplitude * np.cos(2 * np.pi * bin_index * t / n)
    return Signal(
        ident="S1", name="Bin-centered sinusoid", provenance="synthetic",
        samples=x - x.mean(),
        description=("Sinusoid whose frequency coincides exactly with DFT bin "
                     f"{bin_index}; energy confined to one conjugate pair."),
        params={"N": n, "bin_index": bin_index, "amplitude": amplitude})


def make_S2(n: int = 26, bin_offset: float = 3.5, amplitude: float = 1.0) -> Signal:
    """Sinusoid at a non-integer bin. Exhibits spectral leakage."""
    t = np.arange(n)
    x = amplitude * np.cos(2 * np.pi * bin_offset * t / n)
    return Signal(
        ident="S2", name="Non-bin-centered sinusoid", provenance="synthetic",
        samples=x - x.mean(),
        description=("Sinusoid at a non-integer bin position "
                     f"({bin_offset}); worst-case leakage at the half-bin offset."),
        params={"N": n, "bin_offset": bin_offset, "amplitude": amplitude})


def make_S3(n: int = 26, r: float = 4.0,
            bins: tuple[int, ...] = (2, 5, 9),
            amps: tuple[float, ...] = (1.0, 0.6, 0.3)) -> Signal:
    """
    Multi-component sinusoid with a controlled mean-to-std ratio.
    The AC content is identical for every r; only the offset changes.
    """
    t = np.arange(n)
    f = sum(a * np.cos(2 * np.pi * b * t / n + 0.3 * i)
            for i, (b, a) in enumerate(zip(bins, amps)))
    return Signal(
        ident="S3", name="Multi-component sinusoid with offset",
        provenance="synthetic", samples=_set_ratio(f, r),
        description=("Three sinusoidal components plus a constant offset "
                     f"chosen so that mean/std = {r}."),
        params={"N": n, "r": r, "bins": list(bins), "amps": list(amps)})


def make_S4(n: int = 26, seed: int = MASTER_SEED) -> Signal:
    """Zero-mean broadband (white Gaussian) sequence. Low-compaction reference."""
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    return Signal(
        ident="S4", name="Broadband zero-mean sequence", provenance="synthetic",
        samples=x - x.mean(),
        description=("White Gaussian sequence, mean removed. Spectrally flat in "
                     "expectation; a lower bound on achievable compaction."),
        params={"N": n, "seed": seed})


def make_S5(n: int = 26, decay: float = 0.25, bin_index: int = 4) -> Signal:
    """Damped-oscillation transient. Non-stationary case."""
    t = np.arange(n)
    x = np.exp(-decay * t) * np.cos(2 * np.pi * bin_index * t / n)
    return Signal(
        ident="S5", name="Damped transient", provenance="synthetic",
        samples=x - x.mean(),
        description=("Exponentially damped oscillation; energy localised in "
                     "time and therefore spread in frequency."),
        params={"N": n, "decay": decay, "bin_index": bin_index})


def make_S6_realizations(snr_db: float, n_realizations: int = 100,
                         seed: int = MASTER_SEED) -> tuple[NDArray, dict]:
    """
    S0 plus zero-mean Gaussian noise at a specified SNR.

    SNR is defined on the AC (mean-removed) power of S0, because adding noise
    scaled to the DC-inflated total power would make the nominal SNR
    meaningless for exactly the reason this study documents.

    Returns (array of shape (n_realizations, N), parameter dict). STOCHASTIC.
    """
    base = make_S0().samples
    ac_power = float(np.mean((base - base.mean()) ** 2))
    noise_sigma = float(np.sqrt(ac_power / (10.0 ** (snr_db / 10.0))))
    # Distinct, reproducible child stream per SNR level.
    rng = np.random.default_rng([seed, int(round(snr_db * 10))])
    noise = rng.standard_normal((n_realizations, base.size)) * noise_sigma
    return base[None:] + noise, {
        "snr_db": snr_db, "n_realizations": n_realizations,
        "noise_sigma": noise_sigma, "ac_power_reference": ac_power,
        "seed": seed, "seed_stream": [seed, int(round(snr_db * 10))],
    }


def offset_sweep(n: int = 26,
                 r_values: tuple[float, ...] = R_SWEEP_VALUES) -> list[Signal]:
    """Experiment A: identical AC content, offset swept over `r_values`."""
    return [make_S3(n=n, r=r) for r in r_values]


def build_corpus(n: int = 26) -> list[Signal]:
    """Deterministic corpus members S0-S5 (S6 is generated separately)."""
    return [make_S0(), make_S1(n), make_S2(n), make_S3(n), make_S4(n), make_S5(n)]
