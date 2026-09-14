**Table 12. Numerical validation gates.**

| check                                                      |    measured |   tolerance | passed   | note                                                    |
|:-----------------------------------------------------------|------------:|------------:|:---------|:--------------------------------------------------------|
| direct DFT vs FFT (max abs diff)                           | 1.91181e-12 |       1e-09 | True     |                                                         |
| direct DFT vs FFT (max rel diff)                           | 1.52175e-15 |       1e-12 | True     |                                                         |
| IDFT(DFT(x)) round-trip                                    | 1.69905e-12 |       1e-09 | True     |                                                         |
| Hermitian symmetry violation                               | 1.813e-12   |       1e-09 | True     |                                                         |
| Nyquist bin imaginary part                                 | 6.54789e-13 |       1e-09 | True     | N even => X[N/2] real                                   |
| DC bin imaginary part                                      | 0           |       1e-09 | True     |                                                         |
| legacy transform == mirrored unitary DFT                   | 1.813e-12   |       1e-09 | True     | confirms the 2013/14 spectrum is frequency-reversed     |
| |legacy| == |unitary| (magnitudes unaffected)              | 0           |       1e-09 | True     |                                                         |
| Parseval discrepancy, float64                              | 2.74921e-16 |       1e-12 | True     |                                                         |
| eta_DC measured vs r^2/(1+r^2)                             | 3.33067e-16 |       1e-12 | True     |                                                         |
| DCT-II Parseval                                            | 1.37461e-16 |       1e-12 | True     |                                                         |
| DCT-II round-trip                                          | 9.09495e-13 |       1e-09 | True     |                                                         |
| 11-coefficient reconstruction is real                      | 7.01661e-13 |       1e-09 | True     |                                                         |
| full-mask reconstruction == x                              | 1.67688e-12 |       1e-09 | True     |                                                         |
| historical: E (sample domain)                              | 0.000118064 |       0.001 | True     |                                                         |
| historical: H (transform domain)                           | 0.000118064 |       0.001 | True     |                                                         |
| historical: E1 (k=5, 11 coefficients)                      | 0.000106414 |       0.001 | True     |                                                         |
| historical: 100*E1/E                                       | 2.93187e-06 |       0.001 | True     |                                                         |
| historical: E2 (all coefficients)                          | 0.000118064 |       0.001 | True     |                                                         |
| historical: 100*E2/E                                       | 1.42109e-16 |       0.001 | True     |                                                         |
| historical: 0.95E                                          | 6.83654e-05 |       0.001 | True     |                                                         |
| historical: yc[k], ys[k] for k = 0..14 (max abs deviation) | 0.319962    |       0.5   | True     | yc[0] deviates by 0.320 because it is printed to 4 s.f. |
| historical: printed samples x[0..14] (max abs deviation)   | 0           |       0.5   | True     |                                                         |
| identity: eps_L2 == sqrt(1 - eta)                          | 2.50703e-15 |       1e-12 | True     |                                                         |
| identity: 1-eta_total == (1-eta_AC)(1-eta_DC)              | 3.33067e-16 |       1e-12 | True     |                                                         |
| identity: eps_full == eps_AC / sqrt(1+r^2)                 | 8.32667e-17 |       1e-12 | True     |                                                         |
| magnitude ranking attains the true optimum at every budget | 2.22045e-16 |       1e-12 | True     | exhaustive over 16384 conjugate-symmetric sets          |
| window sidelobe vs literature: rectangular                 | 0.0456563   |       1.5   | True     | measured -13.3 dB, literature -13.3 dB                  |
| window sidelobe vs literature: hann                        | 0.0325882   |       1.5   | True     | measured -31.5 dB, literature -31.5 dB                  |
| window sidelobe vs literature: hamming                     | 0.749281    |       1.5   | True     | measured -42.4 dB, literature -41.7 dB                  |
| window sidelobe vs literature: blackman                    | 0.0101484   |       1.5   | True     | measured -58.1 dB, literature -58.1 dB                  |
| cumulative-energy mask reaches its threshold               | 0           |       1e-12 | True     |                                                         |
| cumulative mask is conjugate-symmetric                     | 4.73399e-13 |       1e-09 | True     |                                                         |
