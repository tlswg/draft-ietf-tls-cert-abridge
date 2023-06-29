# Benchmarks

This folder contains scripts for benchmarking the various compression schemes.

| Scheme                                               |   Storage Footprint |   p5 |   p50 |   p95 |
|------------------------------------------------------|---------------------|------|-------|-------|
| Original                                             |                   0 | 2308 |  4032 |  5609 |
| TLS Cert Compression                                 |                   0 | 1619 |  3243 |  3821 |
| Intermediate Suppression                             |                   0 | 1315 |  1688 |  4227 |
| Intermediate Suppression and TLS Cert Compression    |                   0 | 1020 |  1445 |  3303 |
| Pass 1 only (intermediate and root compression)      |                   0 | 1001 |  1429 |  2456 |
| Dictionary composed all intermediate and root certs  |             3455467 |  721 |  1094 |  1631 |
| Pass 1 plus popular strings                          |                1848 |  718 |  1128 |  1627 |
| This Draft                                           |               65336 |  661 |  1060 |  1437 |
| Pass 1 plus trained end-entity zstd dict             |                3000 |  562 |   931 |  1454 |
| Pass 1 plus trained end-entity zstd dict             |              100000 |  520 |   894 |  1291 |
| Hypothetical Optimal Compression                     |                   0 |  377 |   742 |  1075 |


## Evaluated Schemes

* **TLS Certificate Compression** - Using zstandard tuned for maximum compression
* **Intermediate Suppression** - Removes the intermediate and root certificates from the chain. Has no effect if the chain contains a certificate not in Mozilla's list of intermediates and roots.
* **Pass 1** - Just the compression scheme defined in the draft for intermediate and root certificates.
* **Dictionary of all intermediate and root certs** - Pure Zstandard with a very large dictionary composed of the concatination of all intermediate and root certificates in the CCADB.
* **Pass 1 plus popular strings** - Pass 1 followed by compression of the end-entity certificate using a dictionary of common strings extracted from witnessed certificate chains.
* **This Draft** - As described in this document.
* **Pass 1 plus trained zstd dict** - The end entity certiifcates from a number of certificate chains have their subject-specific (name, domains) removed and then are passed to the Zstandard dictionary training function with a size of 3 KB or 100 KB.
* **Hypothetical Optimal Compression** - This assumes an end-entity certificate can be reduced to purely the compressed domain names and public key, CA signature and SCTs.
## Methodology

These compression schemes are defined in the associated scripts in the schemes folder. Each scheme is evaluated over a sample of certificate chains fetched from the Tranco top 100k. The confidence interval for each percentile is calculated and the upper bound is taken.