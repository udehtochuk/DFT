"""
transforms.py
=============
Unitary DFT / inverse DFT, an independent FFT-based path, DCT-II, and the
Hermitian-symmetry utilities used throughout the study.

CONVENTION (used everywhere in this package, without exception)
---------------------------------------------------------------
    X[k] = (1/sqrt(N)) * sum_{n=0}^{N-1} x[n] * exp(-j*2*pi*k*n/N)
    x[n] = (1/sqrt(N)) * sum_{k=0}^{N-1} X[k] * exp(+j*2*pi*k*n/N)

This pair is unitary, hence Parseval/Plancherel holds analytically:

    sum_n |x[n]|^2 == sum_k |X[k]|^2

Note the NEGATIVE exponent in analysis. The 2013/2014 source study stated this
convention but computed the conjugate one (positive exponent), which yields a
frequency-reversed spectrum. See `legacy_transform_1314` and validation.py.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = [
    "dft_matrix", "dft_direct", "idft_direct", "dft_fft", "idft_fft",
    "legacy_transform_1314", "hermitian_partner", "conjugate_pairs",
    "is_hermitian", "dct2_ortho", "idct2_ortho",
]


def _check_1d_real(x: NDArray) -> NDArray[np.float64]:
    x = np.asarray(x)
    if x.ndim != 1:
        raise ValueError(f"expected a 1-D sequence, got shape {x.shape}")
    if x.size == 0:
        raise ValueError("empty sequence")
    if np.iscomplexobj(x):
        raise ValueError("expected a real-valued sequence")
    return x.astype(np.float64)


def dft_matrix(n_samples: int, inverse: bool = False) -> NDArray[np.complex128]:
    """Unitary DFT matrix. `inverse=True` returns the synthesis matrix."""
    if n_samples < 1:
        raise ValueError("n_samples must be >= 1")
    k = np.arange(n_samples)
    sign = +1.0 if inverse else -1.0
    return np.exp(sign * 2j * np.pi * np.outer(k, k) / n_samples) / np.sqrt(n_samples)


def dft_direct(x: NDArray) -> NDArray[np.complex128]:
    """Direct O(N^2) unitary DFT. Independent of numpy.fft by construction."""
    x = _check_1d_real(x)
    return dft_matrix(x.size) @ x.astype(np.complex128)


def idft_direct(spectrum: NDArray) -> NDArray[np.complex128]:
    """Direct O(N^2) unitary inverse DFT."""
    spectrum = np.asarray(spectrum, dtype=np.complex128)
    if spectrum.ndim != 1:
        raise ValueError("expected a 1-D spectrum")
    return dft_matrix(spectrum.size, inverse=True) @ spectrum


def dft_fft(x: NDArray) -> NDArray[np.complex128]:
    """FFT-based unitary DFT (numpy.fft, with the same normalization)."""
    x = _check_1d_real(x)
    return np.fft.fft(x) / np.sqrt(x.size)


def idft_fft(spectrum: NDArray) -> NDArray[np.complex128]:
    """FFT-based unitary inverse DFT."""
    spectrum = np.asarray(spectrum, dtype=np.complex128)
    return np.fft.ifft(spectrum) * np.sqrt(spectrum.size)


def legacy_transform_1314(x: NDArray) -> NDArray[np.complex128]:
    """
    The transform as ACTUALLY COMPUTED in the 2013/2014 source study:

        ye[k] = (1/sqrt(N)) * sum_n x[n] * exp(+j*2*pi*k*n/N)

    Provided solely so that the historical coefficient tables can be
    reproduced exactly and the convention discrepancy demonstrated.
    It satisfies  ye[k] == X[(N-k) % N]  for real x.
    """
    x = _check_1d_real(x)
    return dft_matrix(x.size, inverse=True) @ x.astype(np.complex128)


def hermitian_partner(k: int, n_samples: int) -> int:
    """Index of the conjugate partner of bin k."""
    return int((n_samples - k) % n_samples)


def conjugate_pairs(n_samples: int) -> list[tuple[int, ...]]:
    """
    Partition bin indices into conjugate groups. Self-conjugate bins (DC, and
    Nyquist when N is even) come back as 1-tuples; all others as 2-tuples.
    Retaining whole groups guarantees a real-valued reconstruction.
    """
    groups, seen = [], set()
    for k in range(n_samples):
        if k in seen:
            continue
        partner = hermitian_partner(k, n_samples)
        if partner == k:
            groups.append((k,))
            seen.add(k)
        else:
            groups.append((k, partner))
            seen.update((k, partner))
    return groups


def is_hermitian(spectrum: NDArray, tol: float = 1e-9) -> bool:
    """True if X[N-k] == conj(X[k]) for all k, within `tol`."""
    spectrum = np.asarray(spectrum, dtype=np.complex128)
    n = spectrum.size
    mirrored = np.array([spectrum[(n - k) % n] for k in range(n)])
    return bool(np.max(np.abs(mirrored - np.conj(spectrum))) < tol)


def dct2_ortho(x: NDArray) -> NDArray[np.float64]:
    """
    Orthonormal DCT-II:
        C[k] = a(k) * sum_n x[n] * cos(pi*(2n+1)*k/(2N)),
        a(0) = sqrt(1/N),  a(k>0) = sqrt(2/N)
    Orthonormal, so Parseval holds: sum x^2 == sum C^2.
    Implemented directly (no scipy dependency) so the convention is explicit.
    """
    x = _check_1d_real(x)
    n = x.size
    idx = np.arange(n)
    basis = np.cos(np.pi * np.outer(np.arange(n), 2 * idx + 1) / (2 * n))
    scale = np.full(n, np.sqrt(2.0 / n))
    scale[0] = np.sqrt(1.0 / n)
    return (basis @ x) * scale


def idct2_ortho(coeffs: NDArray) -> NDArray[np.float64]:
    """Inverse of `dct2_ortho`."""
    coeffs = np.asarray(coeffs, dtype=np.float64)
    n = coeffs.size
    idx = np.arange(n)
    basis = np.cos(np.pi * np.outer(np.arange(n), 2 * idx + 1) / (2 * n))
    scale = np.full(n, np.sqrt(2.0 / n))
    scale[0] = np.sqrt(1.0 / n)
    return basis.T @ (coeffs * scale)
