# Abridged Certificate Compression for the WebPKI

This is the working area for the individual Internet-Draft, "Abridged Certificate Compression for the WebPKI".
It defines a compression scheme suitable for use in [RFC 8879: TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html) which delivers a substantial improvement over the existing generic compression schemes in use today whilst ensuring equitable treatment for both CAs and website operators.

This draft may also be useful in other situations where certificate chains are stored, for example, in the operation of Certificate Transparency logs.

## Sketch

Unlike existing TLS Certificate Compression schemes which use generic compression algorithms, this draft makes use of a WebPKI
specific compression scheme. Specifically, a listing of all intermediate and root WebPKI certificates obtained from the [Common CA Database (CCADB)](https://www.ccadb.org/) is taken a point in time and then used as a compression dictionary in conjunction with existing compression schemes like zstd.

As of May 2023 this listing from the CCADB currently occupies 2.6 MB of disk space. The on-disk footprint can be further reduced as many WebPKI clients (e.g. Mozilla Firefox, Google Chrome) already ship a copy of every intermediate and root cert as this reduces breakage with misconfigured servers and speeds up TLS Certificate Verification.

Note that as this draft specifies a compression scheme, it does not impact the negotiation of trust between clients and servers and is robust in the face of changes to CCADB or trust in a particular WebPKI CA. The client's trusted list of CAs does not need to be a subset or superset of the CCADB list and revocation of trust in a CA does not impact the operation of this compression scheme. Similarly, servers who use roots or intermediates outside the CCADB can still offer the scheme and benefit from it.

As Root and Intermediate Certificates typically have multi-year lifetime, the churn in the CCADB is relatively low and a new version of this compression scheme would not need to be minted more than yearly. Further, as this scheme separates trust negotiation from compression, its possible for proposed root and intermediate certificates to be included in the compression scheme ahead of any public trust decisions, allowing them to benefit from compression from the very first day of use.

## Status

This draft is very much a work in progress, however a preliminary evaluation based on a few thousand certificate chains is available. Each value is given in terms of the **median size in bytes** of the resulting certificate chains conveyed in a TLS handshake.

| Compression Method                                      | Size     |
|--------------------------------------------------------|----------|
| Original, without any form of compression               | 4022     |
| Using TLS Certificate Compression with zstd             | 3335     |
| Transmitting only the End-Entity TLS Certificate        | 1664     |
| TLS Cert Compression & Only End-Entity TLS Certificate  | 1469     |
| **This Draft, Naive Implementation**                    | **1351**     |
| **This Draft, Optimized Implementation**                | **949**      |

## Relationship to other drafts

This draft defines a certificate compression mechanism suitable for use with [RFC 8879: TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html).
