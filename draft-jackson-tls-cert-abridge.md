---
title: "Abridged Certificate Compression for the WebPKI"
abbrev: "Abridged Certs"
category: exp

docname: draft-jackson-tls-cert-abridge-latest
submissiontype: IETF  # also: "independent", "IAB", or "IRTF"
number:
date:
consensus: true
v: 3
area: "Security"
workgroup: "Transport Layer Security"

venue:
  group: "Transport Layer Security"
  type: "Working Group"
  mail: "tls@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/tls/"
  github: "dennisjackson/draft-jackson-tls-cert-abridge"
  latest: "https://dennisjackson.github.io/draft-jackson-tls-cert-abridge/draft-jackson-tls-cert-abridge.html"

author:
 -
    fullname: Dennis Jackson
    organization: Mozilla
    email: ietf@dennis-jackson.uk

normative:
 RFC8879:

informative:
 RFC9000:

 FastlyStudy:
   title: Does the QUIC handshake require compression to be fast?
   target: https://www.fastly.com/blog/quic-handshake-tls-compression-certificates-extension-study
   date: 2020-05-18
   author:
    -
      ins: "P. McManus"
      name: "Patrick McManus"

 QUICStudy:
   title: On the Interplay between TLS Certificates and QUIC Performance
   target: https://ilab-pub.imp.fu-berlin.de/papers/nthms-ibtcq-22.pdf
   date: 2022-12-06
   author:
    -
      ins: "TODO TODO TODO"

 PQStudy:
   title: Sizing Up Post-Quantum Signatures
   target: https://blog.cloudflare.com/sizing-up-post-quantum-signatures/
   date: 2021-11-08
   author:
    -
      ins: "Bas TODO"

 CCADB:
   title: Common CA Database
   target: https://www.ccadb.org/
   date: 2023-06-05
   author:
    -
      org: "Mozilla"
    -
      org: "Microsoft"
    -
      org: "Google"

 Intermediate:
   title: Intermediate Certs Proposal
   target: TODO
   date: 2023-06-05
   author:
    -
      org: "TODO"

--- abstract

This drafts defines a WebPKI specific scheme for use in TLS Certificate Compression {{RFC8879}}. The compression scheme relies on a static dictionary consisting of a snapshot of the root and intermediate certificates used in the WebPKI. The result is a dramatic improvement over the existing generic compression schemes used in TLS, equitable for both CAs and website operators and avoids the need for trust negotiation or additional error handling. As the scheme removes the overhead of including root and intermediate certificates in the TLS handshake, it paves the way for a transition to TLS certificates using post-quantum signatures and has an outsized impact on QUIC's handshake latency due to the magnification limits on the size of the server's response. This compression scheme may also be of interest in other situations where certificate chains are stored, for example in the operation of Certificate Transparency logs.

--- middle

# Introduction

## Motivation

When a server responds to a TLS Client Hello, its initial flight of packets is limited in size by the underlying transport protocol. If the initial flight of packets exceeds the size limit, the server must wait for the client to acknowledge receipt, incurring the latency penalty of an additional round trip before the handshake can complete. In TLS, the majority of the server’s initial flight consists of the certificate chain and consequently reducing the size of this chain to below the initial size limit can deliver substantial performance improvements.

For TLS handshakes over TCP, the maximum size of the server’s initial flight is typically around 15,000 bytes. For TLS handshakes in QUIC, the limit is much lower at a maximum of 4500 bytes ({{RFC9000}}, Section 8.1). Applying one of the generic TLS Certificate Compression schemes defined in {{RFC8879}} is already essential for QUIC deployments, as roughly 35% of uncompressed certificate chains in use on the WebPKI are larger than the QUIC size limit {{FastlyStudy}}, {{QUICStudy}}.

However, this approach is insufficient for the upcoming transition to post-quantum primitives. The current NIST PQ signatures are between 10 and 40 times the size of current elliptic curve signatures and consequently pose a substantial challenge for TLS handshakes over both TCP and QUIC {{PQStudy}}. As the increased size is due to incompressible cryptoprimitives like signatures and public keys, existing TLS Certificate Compression schemes will yield negligible improvements over the uncompressed certificates.

## Overview

This draft introduces a new TLS Certificate Compression scheme which is intended specifically for use on the WebPKI. It makes used of a shared dictionary between client and server consisting of all intermediate and root certificates contained in the root stores of major browsers sourced from the Common CA Database {{CCADB}}. As of May 2023, this dictionary would be 2.6 MB in size and consist of roughly 1500 intermediate certificates and 150 root certificates. The disk footprint can be reduced to effectively zero as many WebPKI clients (e.g. Mozilla Firefox, Google Chrome) already ship a copy of every WebPKI intermediate and root certificate as part of their application.

Using a shared dictionary allows for this compression scheme to deliver dramatically more effective compression, reducing an entire certificate chain to roughly 25% of its original size, rather than the 75% achieved by existing generic schemes. Firstly, the intermediate and root certificates are compressed to a couple of bytes each and effectively no longer contribute to the wire size of the certificate chain. Secondly, the end-entity certificate can be further reduced by reference to strings in the shared dictionary. The preliminary evaluation of this scheme suggests that 50% of certificate chains in use today fit in under 950 bytes and 95% fit in under 1613 bytes.

Perhaps surprisingly, this scheme results in a smaller wire size than the use of generic TLS certificate compression and the suppression of CA certificates as proposed in {{Intermediate}}. This is because although the proposal removes the intermediate and root certs entirely, this also removes the redundancy that generic TLS certificate compression schemes rely on.

It is also important to note that as this is only a compression scheme, it does not impact any trust decisions in the TLS handshake or perform trust negotiation. A client can offer this compression scheme whilst only trusting a subset of the certificates in the CCADB snapshot, similarly a server can offer this compression scheme whilst using a certificate chain which does not chain back to a WebPKI root. Similarly, a new root or intermediate can be included in CCADB and static dictionary at the point of application to the root stores, rather than having to wait to be approved, allowing them to benefit from this compression scheme from the very first day of trust. As a result this scheme is equitable in so far as it provides equal benefits for all CAs in the WebPKI, doesn't privilege any particular end-entity certificate or website and allows WebPKI clients to make different trust decisions without fear of breakage.

## Relationship to other drafts

This draft defines a certificate compression mechanism suitable for use with [RFC 8879: TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html).

The intent of this draft is to provide a compelling alternative to [draft-kampanakis-tls-scas](https://www.ietf.org/id/draft-kampanakis-tls-scas-latest-03.html) as it provides a better compression ratio, doesn't require any additional retries or error handling if connections fail and doesn't require clients to be frequently updated with new intermediate certificates.

[CBOR Encoded X.509 (C509)](https://www.ietf.org/archive/id/draft-ietf-cose-cbor-encoded-cert-05.html) defines a concise alternative format for X.509 certificates. If this format were to become widely used on the WebPKI, defining an alternative version of this draft specifically for C509 certificates would be sensible.

[Compact TLS, (cTLS)](https://www.ietf.org/archive/id/draft-ietf-tls-ctls-08.html) defines a version of TLS1.3 which allows a pre-configured client and server to establish a session with minimal overhead on the wire. In particular, it supports the use of a predefined list of certificates known to both parties which can be compressed. However, cTLS is still at an early stage and may be challenging to deploy in a WebPKI context due to the need for clients and servers to agree on the profile template to be used in the handshake.

[RFC 7924: TLS Cached Information Extension]( https://www.rfc-editor.org/info/rfc7924) introduced a new extension allowing clients to signal they had cached certificate information from a previous connection and for servers to signal that the clients should use that cache instead of transmitting a redundant set of certificates. However this RFC has seen little adoption in the wild as it introduces a new fingerprinting vector and arguably supplanted by session resumption.

[RFC 9191: Handling long certificate chains in TLS-Based EAP Methods](https://www.rfc-editor.org/rfc/rfc9191.txt) discusses the challenges of long certificate chains outside the WebPKI ecosystem. Although the scheme proposed in this draft is targeted at WebPKI use, it nonetheless delivers a substantial improvement over existing TLS compression schemes even when alternative roots are used. Further, defining alternative shared dictionaries for other major ecosystems may be attractive.

## Status

This draft is very much a work in progress. Open questions are marked with the tag **DISCUSS**.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Abridged Compression Scheme

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


  | Compression Method                                     | Median Size (Bytes) | Relative Size |
  |--------------------------------------------------------|---------------------|---------------|
  | Original, without any form of compression              | 4022                | 100%          |
  | Using TLS Certificate Compression with zstd            | 3335                | 83%           |
  | Transmitting only the End-Entity TLS Certificate       | 1664                | 41%           |
  | TLS Cert Compression & Only End-Entity TLS Certificate | 1469                | 37%           |
  | **This Draft, Naive Implementation**                   | 1351                | 34%           |
  | **This Draft, Optimized Implementation**               | 949                 | 24%           |

Performance is also greatly enhanced at the tails. For the optimized implementation:

  | Percentile      | Original  | This Draft    | Relative Size |
  |-----------------|-----------|---------------|---------------|
  | 5th             | 2755      | 641           | 23%           |
  | 50th            | 4022      | 949           | 24%           |
  | 95th            | 5801      | 1613          | 28%           |

# Deployment Considerations

## Management of the Shared Dictionary

### Size 

As of May 2023 this listing from the CCADB currently occupies 2.6 MB of disk space. The on-disk footprint can be further reduced as many WebPKI clients (e.g. Mozilla Firefox, Google Chrome) already ship a copy of every intermediate and root cert they trust for use in certificate validation.

### Churn 

Typically around 10 or so new root certificates are introduced to the WebPKI each year. The various root programs restrict the lifetimes of these certificates, Microsoft to between 8 and 25 years [3.A.3](https://learn.microsoft.com/en-us/security/trusted-root/program-requirements), Mozilla to between 0 and 14 years [Wiki page](https://wiki.mozilla.org/CA/Root_CA_Lifecycles). Chrome has proposed a maximum lifetime of 7 years in the future ([Update](https://www.chromium.org/Home/chromium-security/root-ca-policy/moving-forward-together/)). Some major CAs have objected to this proposed policy as the root inclusion process currently takes around 3 years from start to finish [Digicert Blog](https://www.digicert.com/blog/googles-moving-forward-together-proposals-for-root-ca-policy). Similarly, Mozilla requires CAs to apply to renew their roots with at least 2 years notice [Wiki page](https://wiki.mozilla.org/CA/Root_CA_Lifecycles).  

Typically around 100 to 200 new WebPKI intermediate certificates are issued each year. No WebPKI root program currently limits the lifetime of intermediate certificates, but they are in practice capped by the lifetime of their parent root certificate. The vast majority of these certificates are issued with 10 year lifespans. A small but notable fraction (<10%) are issued with 2 or 3 year lifetimes. Chrome's Root Program has proposed that Intermediate Certificates be limited to 3 years in the future ([Update](https://www.chromium.org/Home/chromium-security/root-ca-policy/moving-forward-together/)). 

Disclosure required as of July 2022 ([Mozilla Root Program Section 5.3.2](https://www.mozilla.org/en-US/about/governance/policies/security-group/certs/policy/#53-intermediate-certificates)) - within a week of creation and prior to usage. 
Chrome require three weeks notice before a new intermediate is issued to a new organisation. [Policy](https://www.chromium.org/Home/chromium-security/root-ca-policy/)


* [CCADB Cert Listings](https://www.ccadb.org/resources)
* [Mozilla Cert Listings](https://wiki.mozilla.org/CA/Intermediate_Certificates)
* [Firefox Distributed Intermediate Certs Listing](https://firefox.settings.services.mozilla.com/v1/buckets/security-state/collections/intermediates/records)
* [All Public Intermediate Certs](https://ccadb.my.salesforce-sites.com/mozilla/PublicAllIntermediateCerts)
* [Mozilla In Progress Root Inclusions](https://ccadb.my.salesforce-sites.com/mozilla/UpcomingRootInclusionsReport)
* [Mozilla Roots in Firefox](https://ccadb.my.salesforce-sites.com/mozilla/CACertificatesInFirefoxReport)

As root and intermediate Certificates typically have multi-year lifetime, the churn in the CCADB is relatively low and a new version of this compression scheme could be minted at yearly intervals, with the only change being the CCADB list used. Further, as this scheme separates trust negotiation from compression, its possible for proposed root and intermediate certificates to be included in the compression scheme ahead of any public trust decisions, allowing them to benefit from compression from the very first day of use.

# Security Considerations

Note that as this draft specifies a compression scheme, it does not impact the negotiation of trust between clients and servers and is robust in the face of changes to CCADB or trust in a particular WebPKI CA. The client's trusted list of CAs does not need to be a subset or superset of the CCADB list and revocation of trust in a CA does not impact the operation of this compression scheme. Similarly, servers who use roots or intermediates outside the CCADB can still offer the scheme and benefit from it


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
