**Table 2. Independent verification of the 2013/2014 results.**

| quantity                                       |   historical |    recomputed | units   |    rel_diff | status   | note                                                    |
|:-----------------------------------------------|-------------:|--------------:|:--------|------------:|:---------|:--------------------------------------------------------|
| E (sample domain)                              |    1.694e+06 |   1.6938e+06  | -       | 0.000118064 | verified | nan                                                     |
| H (transform domain)                           |    1.694e+06 |   1.6938e+06  | -       | 0.000118064 | verified | nan                                                     |
| E1 (k=5, 11 coefficients)                      |    1.68e+06  |   1.67982e+06 | -       | 0.000106414 | verified | nan                                                     |
| 100*E1/E                                       |   99.175     |  99.1747      | %       | 2.93187e-06 | verified | nan                                                     |
| E2 (all coefficients)                          |    1.694e+06 |   1.6938e+06  | -       | 0.000118064 | verified | nan                                                     |
| 100*E2/E                                       |  100         | 100           | %       | 1.42109e-16 | verified | nan                                                     |
| 0.95E                                          |    1.609e+06 |   1.60911e+06 | -       | 6.83654e-05 | verified | nan                                                     |
| yc[k], ys[k] for k = 0..14 (max abs deviation) |    0         |   0.319962    | -       | 0.319962    | verified | yc[0] deviates by 0.320 because it is printed to 4 s.f. |
| printed samples x[0..14] (max abs deviation)   |    0         |   0           | -       | 0           | verified | nan                                                     |
