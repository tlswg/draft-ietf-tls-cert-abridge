---
title: "Abridged Certificate Compression for the WebPKI"
abbrev: "Abridged Certs"
category: info

docname: draft-jackson-tls-cert-abridge-latest
submissiontype: IETF  # also: "independent", "IAB", or "IRTF"
number:
date:
consensus: true
v: 3
area: "Security"
workgroup: "Transport Layer Security"
# keyword:
#  - next generation
#  - unicorn
#  - sparkling distributed ledger
# venue:
#   group: WG
#   type: Working Group
#   mail: WG@example.com
#   arch: https://example.com/WG
#   github: USER/REPO
#   latest: https://example.com/LATEST

author:
 -
    fullname: Dennis Jackson
    organization: Mozilla
    email: ietf@dennis-jackson.uk

normative:

informative:


--- abstract

This is the working area for the individual Internet-Draft, "Abridged Certificate Compression for the WebPKI".
It defines a compression scheme suitable for use in [RFC 8879: TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html) which uses WebPKI specific information to deliver a substantial improvement over the existing generic compression schemes in use today whilst being careful to ensure CAs and website operators are treated equitably.

As well as substantially decreasing the size of the end-entity TLS certificate, this draft also compresses any intermediate or root Certificate used in the Web PKI to a couple of bytes. This not only reduces the latency of TLS session establishment in general, but has an outsized impact on QUIC handshakes due to the magnification limits on the server's response. It also allows for an easy transition to Post-Quantum TLS Certificates since intermediate and root certificates no longer contribute to packet size on the wire. This draft may also be useful in other situations where certificate chains are stored, for example, in the operation of Certificate Transparency logs.

--- middle

# Introduction

TODO Introduction

## Related Work

This draft defines a certificate compression mechanism suitable for use with [RFC 8879: TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html).

The intent of this draft is to provide a compelling alternative to [draft-kampanakis-tls-scas](https://www.ietf.org/id/draft-kampanakis-tls-scas-latest-03.html) as it provides better compression, doesn't require any additional retries or error handling if connections fail and doesn't require clients to be frequently updated.

[CBOR Encoded X.509 (C509)](https://www.ietf.org/archive/id/draft-ietf-cose-cbor-encoded-cert-05.html) defines a concise alternative format for X.509 certificates. If this format were to become widely used on the WebPKI, defining an alternative version of this draft specifically for C509 certificates would be sensible.

[Compact TLS, (cTLS)](https://www.ietf.org/archive/id/draft-ietf-tls-ctls-08.html) defines a version of TLS1.3 which allows a pre-configured client and server to establish a session with minimal overhead on the wire. In particular, it supports the use of a predefined list of certificates known to both parties which can be compressed. However, cTLS is still at an early stage and may be challenging to deploy in a WebPKI context due to the need for clients and servers to agree on the profile template to be used in the handshake.


# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Description

This section is a work in progress. It currently defines two distinct approaches with differing tradeoffs but prior to progression this will need to be winnowed down to a single method.

## Versioning

* Take the listing available here. (TODO)

## Method 1: Naive

#### Setup

* Convert to DER and concatenate.
* Pass the resulting blob to Zstd

#### Operation

* Recommend use of max compression level since it is a start-up operation on the TLS Server and doesn't impact decompression speed.
* Use zstd with dict.

## Method 2: Optimized

#### Setup

* Do the lexicographic ordering and assign a two-byte identifier in sequence.
* Do CT-fetch and train keyed zstd dictionary

#### Operation

* Do keyword substitution on certificate chain, replacing certificate chain with 3 byte identifier where possible.
* Do keyed zstd dictionary on the remaining file.

## Tradeoffs and Open Questions

Method 1 is very simple to implement, but isn't quite as efficient and imposes an additional storage requirement on clients.
It can likely be deployed as-is with minimal changes to all existing implementations.

Method 2 requires more custom code, but reduces the storage footprint and delivers a better compression ratio.

#### Bikeshedding Opportunities

* zstd vs brotli
*

# Expected Benefits

This draft is very much a work in progress, however a preliminary evaluation based on a few thousand certificate chains is available.

```
| Compression Method                                     | Median Size (Bytes) | Relative Size |
|--------------------------------------------------------|---------------------|---------------|
| Original, without any form of compression              | 4022                | 100%          |
| Using TLS Certificate Compression with zstd            | 3335                | 83%           |
| Transmitting only the End-Entity TLS Certificate       | 1664                | 41%           |
| TLS Cert Compression & Only End-Entity TLS Certificate | 1469                | 37%           |
| **This Draft, Naive Implementation**                   | 1351                | 34%           |
| **This Draft, Optimized Implementation**               | 949                 | 24%           |
```

# Deployment Considerations

As of May 2023 this listing from the CCADB currently occupies 2.6 MB of disk space. The on-disk footprint can be further reduced as many WebPKI clients (e.g. Mozilla Firefox, Google Chrome) already ship a copy of every intermediate and root cert they trust for use in certificate validation.

As root and intermediate Certificates typically have multi-year lifetime, the churn in the CCADB is relatively low and a new version of this compression scheme could be minted at yearly intervals, with the only change being the CCADB list used. Further, as this scheme separates trust negotiation from compression, its possible for proposed root and intermediate certificates to be included in the compression scheme ahead of any public trust decisions, allowing them to benefit from compression from the very first day of use.

# Security Considerations

Note that as this draft specifies a compression scheme, it does not impact the negotiation of trust between clients and servers and is robust in the face of changes to CCADB or trust in a particular WebPKI CA. The client's trusted list of CAs does not need to be a subset or superset of the CCADB list and revocation of trust in a CA does not impact the operation of this compression scheme. Similarly, servers who use roots or intermediates outside the CCADB can still offer the scheme and benefit from it


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
