"""
test_study.py
=============
Automated tests. Run with:  pytest -q   (from the `code/` directory)

Tolerances are deliberate. If a test fails, investigate the cause; do not
loosen the tolerance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import coefficient_selection as cs        # noqa: E402
import dct_comparison as DCT              # noqa: E402
import dft_analysis as ANA                # noqa: E402
import leakage_analysis as LEAK           # noqa: E402
import metrics as M                       # noqa: E402
import signal_generation as SG            # noqa: E402
import transforms as T                    # noqa: E402
import validation as VAL                  # noqa: E402
from data_recovery import (PUBLISHED_X_PARTIAL, recover_sequence,
                           recovery_report)

TOL = 1e-9
RNG = np.random.default_rng(12345)


# --------------------------------------------------------------- transforms
def test_dft_of_known_analytical_signal():
    """A unit-amplitude bin-centered cosine puts A*sqrt(N)/2 in bins k0 and N-k0."""
    n, k0 = 32, 5
    x = np.cos(2 * np.pi * k0 * np.arange(n) / n)
    X = T.dft_direct(x)
    expected = np.sqrt(n) / 2
    assert abs(abs(X[k0]) - expected) < TOL
    assert abs(abs(X[n - k0]) - expected) < TOL
    others = [abs(X[k]) for k in range(n) if k not in (k0, n - k0)]
    assert max(others) < TOL


def test_dft_of_constant_signal():
    """A constant c puts all energy in bin 0, with X[0] = c*sqrt(N)."""
    n, c = 16, 3.5
    X = T.dft_direct(np.full(n, c))
    assert abs(X[0].real - c * np.sqrt(n)) < TOL
    assert max(abs(X[k]) for k in range(1, n)) < TOL


def test_dft_of_unit_impulse_is_flat():
    n = 24
    x = np.zeros(n); x[0] = 1.0
    mag = np.abs(T.dft_direct(x))
    assert np.allclose(mag, 1 / np.sqrt(n), atol=TOL)


@pytest.mark.parametrize("n", [8, 16, 26, 33, 64])
def test_dft_matches_numpy_fft(n):
    x = RNG.standard_normal(n) * 40 + 150
    assert np.max(np.abs(T.dft_direct(x) - T.dft_fft(x))) < 1e-9


@pytest.mark.parametrize("n", [8, 26, 33])
def test_idft_inverts_dft(n):
    x = RNG.standard_normal(n) * 10
    assert np.max(np.abs(T.idft_direct(T.dft_direct(x)) - x)) < TOL
    assert np.max(np.abs(T.idft_fft(T.dft_fft(x)) - x)) < TOL


@pytest.mark.parametrize("n", [8, 26, 33])
def test_hermitian_symmetry_of_real_signals(n):
    assert T.is_hermitian(T.dft_direct(RNG.standard_normal(n)))


def test_nyquist_bin_is_real_for_even_n():
    for n in (8, 16, 26):
        assert abs(T.dft_direct(RNG.standard_normal(n))[n // 2].imag) < TOL


def test_conjugate_pairs_partition_all_bins():
    for n in (7, 8, 26):
        groups = T.conjugate_pairs(n)
        flat = [k for g in groups for k in g]
        assert sorted(flat) == list(range(n))
        assert len(flat) == len(set(flat))


def test_parseval_holds_for_unitary_dft():
    for n in (8, 26, 64):
        x = RNG.standard_normal(n) * 30 + 200
        assert M.parseval_discrepancy(x, T.dft_direct(x)) < 1e-12


def test_legacy_convention_is_frequency_reversed():
    """The 2013/2014 transform equals the mirrored standard DFT."""
    x = recover_sequence()
    n = x.size
    unitary, legacy = T.dft_direct(x), T.legacy_transform_1314(x)
    mirrored = np.array([unitary[(n - k) % n] for k in range(n)])
    assert np.max(np.abs(legacy - mirrored)) < TOL
    assert np.max(np.abs(np.abs(legacy) - np.abs(unitary))) < TOL   # magnitudes equal
    assert np.max(np.abs(legacy - unitary)) > 1.0                    # but not identical


def test_dct_is_orthonormal_and_invertible():
    for n in (8, 26, 40):
        x = RNG.standard_normal(n) * 15 + 60
        c = T.dct2_ortho(x)
        assert abs(np.sum(c ** 2) - np.sum(x ** 2)) / np.sum(x ** 2) < 1e-12
        assert np.max(np.abs(T.idct2_ortho(c) - x)) < TOL


# ------------------------------------------------------------- data recovery
def test_recovery_reproduces_printed_samples_exactly():
    x = recover_sequence()
    assert x.size == 26
    assert np.array_equal(x[:15].astype(int), np.array(PUBLISHED_X_PARTIAL))


def test_recovery_is_integer_valued_and_explained_by_dc_rounding():
    rep = recovery_report()
    assert rep["max_distance_to_integer"] < 0.1
    # The mean residual must be explained by DC rounding to better than 1e-4.
    assert abs(rep["residual_mean_offset"]
               - rep["dc_rounding_predicted_offset"]) < 1e-4
    assert rep["printed_k14_equals_conj_k12"] is True
    assert abs(rep["printed_nyquist_imag"]) < 1e-9


def test_recovery_is_deterministic():
    assert np.array_equal(recover_sequence(), recover_sequence())


# ------------------------------------------------------------------- metrics
def test_dc_share_formula_matches_measurement():
    for sig in SG.build_corpus():
        x = sig.samples
        if x.std() == 0:
            continue
        measured = M.dc_energy_share(T.dft_direct(x))
        predicted = M.dc_share_theoretical(x.mean() / x.std())
        assert abs(measured - predicted) < 1e-12


@pytest.mark.parametrize("r,expected", [(0.0, 0.0), (1.0, 0.5), (2.0, 0.8),
                                        (3.0, 0.9)])
def test_dc_share_known_values(r, expected):
    assert abs(M.dc_share_theoretical(r) - expected) < 1e-12


def test_l2_error_equals_sqrt_one_minus_eta():
    """The exact identity underpinning the paper's redundancy result."""
    x = recover_sequence()
    spec = T.dft_direct(x)
    for k in range(0, x.size // 2 + 1):
        mask = cs.lowpass_mask(x.size, k)
        eta = M.energy_retention_total(spec, mask)
        eps = M.relative_l2_error(x, cs.reconstruct_from_mask(spec, mask))
        assert abs(eps - M.l2_error_from_retention(eta)) < 1e-12


def test_basis_conversion_law():
    x = recover_sequence()
    spec = T.dft_direct(x)
    r = x.mean() / x.std()
    for k in range(0, x.size // 2 + 1):
        mask = cs.lowpass_mask(x.size, k)
        eta_t = M.energy_retention_total(spec, mask)
        eta_a = M.energy_retention_ac(spec, mask)
        assert abs(eta_t - M.total_from_ac_retention(eta_a, r)) < 1e-12


def test_error_scaling_law():
    x = recover_sequence()
    spec = T.dft_direct(x)
    r = x.mean() / x.std()
    ac = x - x.mean()
    for k in range(1, x.size // 2 + 1):
        mask = cs.lowpass_mask(x.size, k)
        mask_ac = mask.copy(); mask_ac[0] = False
        e_full = M.relative_l2_error(x, cs.reconstruct_from_mask(spec, mask))
        e_ac = M.relative_l2_error(ac, cs.reconstruct_from_mask(spec, mask_ac))
        assert abs(e_full - e_ac / M.l2_scaling_factor(r)) < 1e-12


def test_metrics_reject_degenerate_input():
    with pytest.raises(ZeroDivisionError):
        M.relative_l2_error(np.zeros(4), np.zeros(4))
    with pytest.raises(ZeroDivisionError):
        M.energy_retention_ac(T.dft_direct(np.full(8, 2.0)),
                              np.ones(8, dtype=bool))


# -------------------------------------------------------- coefficient choice
def test_all_selection_masks_give_real_reconstructions():
    x = recover_sequence()
    spec = T.dft_direct(x)
    for masks in (cs.lowpass_masks(spec), cs.magnitude_ranked_masks(spec),
                  cs.magnitude_ranked_masks(spec, basis="ac")):
        for mask in masks:
            out = T.idft_direct(spec * mask)
            assert np.max(np.abs(out.imag)) < 1e-8


def test_full_mask_reconstructs_exactly():
    x = recover_sequence()
    spec = T.dft_direct(x)
    rec = cs.reconstruct_from_mask(spec, np.ones(x.size, dtype=bool))
    assert np.max(np.abs(rec - x)) < TOL


def test_cumulative_energy_reaches_threshold():
    x = recover_sequence()
    spec = T.dft_direct(x)
    for thr in (0.5, 0.8, 0.95, 0.99):
        for basis in ("total", "ac"):
            _, achieved = cs.cumulative_energy_mask(spec, thr, basis=basis)
            assert achieved >= thr - 1e-12


def test_magnitude_selection_is_at_least_as_efficient_as_lowpass():
    """At equal retained-coefficient count, magnitude ranking cannot retain
    less energy than low-pass ranking (it maximizes retained energy by
    construction)."""
    x = recover_sequence()
    spec = T.dft_direct(x)
    lp = {int(m.sum()): M.energy_retention_total(spec, m)
          for m in cs.lowpass_masks(spec)}
    mg = {int(m.sum()): M.energy_retention_total(spec, m)
          for m in cs.magnitude_ranked_masks(spec)}
    for n_coeff in set(lp) & set(mg):
        assert mg[n_coeff] >= lp[n_coeff] - 1e-12


def test_reconstruct_rejects_non_conjugate_mask():
    x = recover_sequence()
    spec = T.dft_direct(x)
    bad = np.zeros(x.size, dtype=bool); bad[3] = True     # bin 3 without bin 23
    with pytest.raises(AssertionError):
        cs.reconstruct_from_mask(spec, bad)


def test_lowpass_mask_rejects_out_of_range_k():
    with pytest.raises(ValueError):
        cs.lowpass_mask(26, 26)


# ---------------------------------------------------- deterministic sig. gen.
def test_signal_generation_is_deterministic():
    for maker in (SG.make_S0, SG.make_S1, SG.make_S2, SG.make_S3,
                  SG.make_S4, SG.make_S5):
        assert np.array_equal(maker().samples, maker().samples)


def test_offset_sweep_holds_ac_content_constant():
    """Only the DC bin may change across the sweep - that is the control."""
    sigs = SG.offset_sweep()
    ref = T.dft_direct(sigs[0].samples)
    for sig in sigs[1:]:
        spec = T.dft_direct(sig.samples)
        assert np.max(np.abs(spec[1:] - ref[1:])) < 1e-9


def test_offset_sweep_achieves_requested_ratios():
    for sig in SG.offset_sweep():
        r = sig.params["r"]
        assert abs(sig.mean / sig.std - r) < 1e-9 if sig.std else True


def test_noise_realizations_are_reproducible_and_correctly_scaled():
    a, pa = SG.make_S6_realizations(20.0, 20)
    b, pb = SG.make_S6_realizations(20.0, 20)
    assert np.array_equal(a, b)
    assert a.shape == (20, 26)
    base = SG.make_S0().samples
    expected = np.sqrt(np.mean((base - base.mean()) ** 2) / 10 ** 2.0)
    assert abs(pa["noise_sigma"] - expected) < 1e-12
    assert pa["seed_stream"] == pb["seed_stream"]


def test_different_snr_gives_different_noise():
    a, _ = SG.make_S6_realizations(30.0, 5)
    b, _ = SG.make_S6_realizations(10.0, 5)
    assert not np.allclose(a, b)


# --------------------------------------------------------------- experiments
def test_experiment_a_matches_theory():
    df = ANA.experiment_a_dc_sweep()
    assert df["abs_error"].max() < 1e-12
    assert df["eta_total_7coef"].is_monotonic_increasing
    # AC-basis quantities must be invariant: only the offset changed.
    assert df["eta_ac_7coef"].std() < 1e-12
    assert df["eps_l2_ac_7coef"].std() < 1e-12


def test_window_sidelobes_match_published_values():
    reference = {"rectangular": -13.3, "hann": -31.5,
                 "hamming": -41.7, "blackman": -58.1}
    for name, ref_db in reference.items():
        _, measured = LEAK.window_response(name, 64)
        assert abs(measured - ref_db) < 1.5, f"{name}: {measured:.1f} dB"


def test_bin_centered_sinusoid_has_no_leakage():
    df = LEAK.leakage_experiment()
    centered = df[df["bin_centered"]]
    assert centered["leakage_energy_fraction"].max() < 1e-12
    assert df[~df["bin_centered"]]["leakage_energy_fraction"].min() > 1e-3


def test_dct_beats_dft_on_transient_but_not_on_pure_tone():
    """Direction, not magnitude: a known result used as a sanity check."""
    tc = DCT.threshold_comparison(thresholds=(0.99,))
    def n_at(sig, tf):
        row = tc[(tc["id"] == sig) & (tc["transform"] == tf)]
        return int(row["n_coeff"].iloc[0])
    assert n_at("S5", "DCT-II") < n_at("S5", "DFT")      # transient: DCT wins
    assert n_at("S1", "DFT") <= n_at("S1", "DCT-II")     # pure tone: DFT wins


def test_precision_sweep_float64_beats_float32():
    rows = VAL.precision_sweep(recover_sequence())
    for n in {r["N"] for r in rows}:
        f32 = [r["eps_parseval"] for r in rows if r["N"] == n and r["precision"] == "float32"][0]
        f64 = [r["eps_parseval"] for r in rows if r["N"] == n and r["precision"] == "float64"][0]
        assert f64 < f32
        assert f64 < 1e-13


# ------------------------------------------------------------------ the gate
def test_all_validation_checks_pass():
    checks = VAL.run_all_checks(verbose=False)
    assert len(checks) >= 25
    assert all(c.passed for c in checks)


def test_historical_results_all_verified():
    rows = VAL.historical_verification_table()
    assert len(rows) == 9
    assert all(r["status"] == "verified" for r in rows)
