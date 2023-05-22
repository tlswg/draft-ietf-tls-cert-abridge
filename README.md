# Abridged Certificate Compression for the WebPKI

This is the working area for the individual Internet-Draft, "Abridged Certificate Compression for the WebPKI".
It defines a compression scheme suitable for use in [RFC 8879: TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html) which delivers a substantial improvement over the existing generic compression schemes in use today whilst ensuring equitable treatment for both CAs and website operators.

This draft may also be useful in other situations where certificate chains are stored, for example, in the operation of Certificate Transparency logs.

* [Editor's Copy](https://dennisjackson.github.io/draft-jackson-tls-cert-abridge/#go.draft-jackson-tls-cert-abridge.html)
* [Datatracker Page](https://datatracker.ietf.org/doc/draft-jackson-tls-cert-abridge)
* [Individual Draft](https://datatracker.ietf.org/doc/html/draft-jackson-tls-cert-abridge)
* [Compare Editor's Copy to Individual Draft](https://dennisjackson.github.io/draft-jackson-tls-cert-abridge/#go.draft-jackson-tls-cert-abridge.diff)

## Sketch

Unlike existing TLS Certificate Compression schemes which use generic compression algorithms, this draft makes use of a WebPKI
specific compression scheme. Specifically, a listing of all intermediate and root WebPKI certificates obtained from the [Common CA Database (CCADB)](https://www.ccadb.org/) is taken a point in time and then used as a compression dictionary in conjunction with existing compression schemes like zstd.

As of May 2023 this listing from the CCADB currently occupies 2.6 MB of disk space. The on-disk footprint can be further reduced as many WebPKI clients (e.g. Mozilla Firefox, Google Chrome) already ship a copy of every intermediate and root cert for use in certificate validation.

Note that as this draft specifies a compression scheme, it does not impact the negotiation of trust between clients and servers and is robust in the face of changes to CCADB or trust in a particular WebPKI CA. The client's trusted list of CAs does not need to be a subset or superset of the CCADB list and revocation of trust in a CA does not impact the operation of this compression scheme. Similarly, servers who use roots or intermediates outside the CCADB can still offer the scheme and benefit from it.

As Root and Intermediate Certificates typically have multi-year lifetime, the churn in the CCADB is relatively low and a new version of this compression scheme would not need to be minted more than yearly. Further, as this scheme separates trust negotiation from compression, its possible for proposed root and intermediate certificates to be included in the compression scheme ahead of any public trust decisions, allowing them to benefit from compression from the very first day of use.

## Status

This draft is very much a work in progress, however a preliminary evaluation based on a few thousand certificate chains is available.

| Compression Method                                      | Median Size of Certificate Chain (Bytes)     |
|--------------------------------------------------------|----------|
| Original, without any form of compression               | 4022     |
| Using TLS Certificate Compression with zstd             | 3335     |
| Transmitting only the End-Entity TLS Certificate        | 1664     |
| TLS Cert Compression & Only End-Entity TLS Certificate  | 1469     |
| **This Draft, Naive Implementation**                    | **1351**     |
| **This Draft, Optimized Implementation**                | **949**      |

## Relationship to other drafts

This draft defines a certificate compression mechanism suitable for use with [RFC 8879: TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html).
The intent of this draft is to provide a compelling alternative to (TODO), in so far as it provides for better compression and simpler deployment.

## Contributing

See the
[guidelines for contributions](https://github.com/dennisjackson/draft-jackson-tls-cert-abridge/blob/main/CONTRIBUTING.md).

Contributions can be made by creating pull requests.
The GitHub interface supports creating pull requests using the Edit (✏) button.


## Command Line Usage

Formatted text and HTML versions of the draft can be built using `make`.

```sh
$ make
```

Command line usage requires that you have the necessary software installed.  See
[the instructions](https://github.com/martinthomson/i-d-template/blob/main/doc/SETUP.md).

