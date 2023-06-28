---
title: "Abridged Certificate Compression for the WebPKI"
abbrev: "Abridged Certs"
category: exp

docname: draft-jackson-tls-cert-abridge-latest
submissiontype: IETF
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
 TLSCertCompress: RFC8879
 ZSTD: RFC8478
 TLS13: RFC8446


 CCADBAllCerts:
   title: CCADB Certificates Listing
   target: https://ccadb.my.salesforce-sites.com/ccadb/AllCertificateRecordsCSVFormat
   date: 2023-06-05
   author:
    -
      org: "Mozilla"
    -
      org: "Microsoft"
    -
      org: "Google"
    -
      org: "Apple"
    -
      org: "Cisco"

informative:
 RFC9000:
 SCA: I-D.kampanakis-tls-scas-latest

 FastlyStudy:
   title: Does the QUIC handshake require compression to be fast?
   target: https://www.fastly.com/blog/quic-handshake-tls-compression-certificates-extension-study
   date: 2020-05-18
   author:
    -
      ins: "P. McManus"
      name: "Patrick McManus"
      org: "Fastly"

 QUICStudy: DOI.10.1145/3555050.3569123
 SCAStudy: DOI.10.1007/978-3-031-07689-3_25

 PQStudy:
   title: Sizing Up Post-Quantum Signatures
   target: https://blog.cloudflare.com/sizing-up-post-quantum-signatures/
   date: 2021-11-08
   author:
    -
      name: Bas Westerbaan
      ins: B. Westerbaan
      org: "Cloudflare"

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
    -
      org: "Apple"
    -
      org: "Cisco"


--- abstract

This drafts defines a WebPKI specific scheme for use in TLS Certificate Compression {{TLSCertCompress}}. The compression scheme relies on a static dictionary consisting of a snapshot of the root and intermediate certificates used in the WebPKI. The result is a substantial improvement over the existing generic compression schemes used in TLS, equitable for both CAs and website operators and avoids the need for trust negotiation or additional error handling. As the scheme removes the overhead of including root and intermediate certificates in the TLS handshake, it paves the way for a transition to TLS certificates using post-quantum signatures and has an outsized impact on QUIC's handshake latency due to limits on the size of the server's initial message flight. This compression scheme may also be of interest in other situations where certificate chains are stored, for example in the operation of Certificate Transparency logs.

--- middle

# Introduction

## Motivation

When a server responds to a TLS Client Hello, its initial flight of packets is limited in size by the underlying transport protocol. If the initial flight of packets exceeds the size limit, the server must wait for the client to acknowledge receipt, incurring the latency penalty of an additional round trip before the handshake can complete. For TLS handshakes over TCP, the maximum size of the server’s initial flight is typically around 14,500 bytes. For TLS handshakes in QUIC, the limit is much lower at a maximum of 4500 bytes ({{RFC9000}}, Section 8.1).

The existing compression schemes used in {{TLSCertCompress}} have been shown to deliver a substantial improvement in QUIC handshake latency {{FastlyStudy}}, {{QUICStudy}} by reducing the size of server's certificate chain and so fitting the server's initial messages within a single flight. However, in a post-quantum setting, the signatures and public keys used in a TLS certificate chain will be typically 10 to 40 times their current size and cannot be compressed with existing TLS Certificate Compression schemes.
Consequently studies {{SCAStudy}} {{PQStudy}} have shown that post-quantum certificate transmission becomes the dominant source of latency in PQ TLS with certificate chains alone expected to exceed even the TCP initial flight limit. This motivates alternative designs for reducing the on-wire size of post-quantum certificate chains.

## Overview

This draft introduces a new TLS Certificate Compression scheme which is intended specifically for use on the WebPKI. It makes used of a shared dictionary between client and server consisting of all intermediate and root certificates contained in the root stores of major browsers sourced from the Common CA Database {{CCADB}}. As of May 2023, this dictionary would be 2.6 MB in size and consist of roughly 1500 intermediate certificates and 150 root certificates. The disk footprint can be reduced to effectively zero as many clients (such as Mozilla Firefox & Google Chrome) are already provisioned with their trusted intermediate and root certificates for compatibility and performance reasons.

Using a shared dictionary allows for this compression scheme to deliver dramatically more effective compression, reducing an entire certificate chain to roughly 25% of its original size, rather than the 75% achieved by existing generic schemes. Firstly, the intermediate and root certificates are compressed to a couple of bytes each and effectively no longer contribute to the wire size of the certificate chain. Secondly, the end-entity certificate can be further reduced by reference to strings in the shared dictionary. A preliminary evaluation of this scheme suggests that 50% of certificate chains in use today fit in under 1000 bytes and 95% fit in under 1500 bytes. This is substantially smaller than  can be achieved with the use of existing TLS certificate compression schemes and the suppression of CA certificates as proposed in {{SCA}}. This is because whilst {{SCA}} removes the intermediate and root certs from the chain entirely, this also removes the redundancy that generic TLS certificate compression schemes exploit.

It is also important to note that as this is only a compression scheme, it does not impact any trust decisions in the TLS handshake or perform trust negotiation. A client can offer this compression scheme whilst only trusting a subset of the certificates in the CCADB snapshot, similarly a server can offer this compression scheme whilst using a certificate chain which does not chain back to a WebPKI root. Similarly, a new root or intermediate can be included in CCADB and static dictionary at the start of their application to the root store and if their application is approved will benefit from this compression scheme from the very first day of trust. As a result this scheme is equitable in so far as it provides equal benefits for all CAs in the WebPKI, doesn't privilege any particular end-entity certificate or website and allows WebPKI clients to make individual trust decisions without fear of breakage.

## Relationship to other drafts

This draft defines a certificate compression mechanism suitable for use with TLS Certificate Compression {{TLSCertCompress}}.

The intent of this draft is to provide an alternative to CA Certificate Suppression {{SCA}} as it provides a better compression ratio, can operate in a wider range of scenarios (including out of sync clients or servers) and doesn't require any additional error handling or retry mechanisms.

CBOR Encoded X.509 (C509) {{?I-D.ietf-cose-cbor-encoded-cert-05}} defines a concise alternative format for X.509 certificates. If this format were to become widely used on the WebPKI, defining an alternative version of this draft specifically for C509 certificates would be beneficial.

Compact TLS, (cTLS) {{?I-D.ietf-tls-ctls-08}} defines a version of TLS1.3 which allows a pre-configured client and server to establish a session with minimal overhead on the wire. In particular, it supports the use of a predefined list of certificates known to both parties which can be compressed. However, cTLS is still at an early stage and may be challenging to deploy in a WebPKI context due to the need for clients and servers to have prior-knowledge of handshake profile in use.

TLS Cached Information Extension {{?RFC7924}} introduced a new extension allowing clients to signal they had cached certificate information from a previous connection and for servers to signal that the clients should use that cache instead of transmitting a redundant set of certificates. However this RFC has seen little adoption in the wild due to concerns over client privacy.

Handling long certificate chains in TLS-Based EAP Methods {{?RFC9191}} discusses the challenges of long certificate chains outside the WebPKI ecosystem. Although the scheme proposed in this draft is targeted at WebPKI use, defining alternative shared dictionaries for other major ecosystems may be of interest.

## Status

This draft is still at an early stage. Open questions are marked with the tag **DISCUSS**.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Abridged Compression Scheme

This section describes a compression scheme suitable for compressing certificate chains used in TLS. The scheme is defined in two parts. An initial pass compressing known intermediate and root certificates and then a subsequent pass compressing the end-entity certificates. This scheme is used by performing the compression step of Pass 1 and then the compression step of Pass 2. Decompression is performed in the reverse order.

## Pass 1: Intermediate and Root Compression

This pass relies on a shared listing of intermediate and root certificates known to both client and server. As many clients (e.g. Mozilla Firefox and Google Chrome) already ship with a list of trusted intermediate and root certificates, this pass allows for the members of the existing list to be included, rather than requiring them to have to be stored separately. This section first details how the client and server enumerate the known certificates, then describes how the listing is used to compress the certificate chain.

### Enumeration of Known Intermediate and Root Certificates

The Common CA Database {{CCADB}} is operated by Mozilla on behalf of a number of Root Program operators including Mozilla, Microsoft, Google, Apple and Cisco. The CCADB contains a listing of all the root certificates trusted by the various root programs, as well as their associated intermediate certificates and new certificates from applicants to one or more root programs who are not yet trusted.

At the time of writing, the CCADB contains around 150 root program certificates and 1500 intermediate certificates which are trusted for TLS Server Authentication, occupying 2.6 MB of disk space. As this listing changes rarely and new inclusions typically join the CCADB listing year or more before they can be deployed on the web, the listing used in this draft will be those certificates included in the CCADB on the 1st of January 2023. Further versions of this draft may provide for a listing on a new cutoff date or according to a different criteria for inclusion.

**DISCUSS:** Is minting a new draft every year or two acceptable? If not, this draft could be redesigned as its own extension and negotiate the available dictionaries which could then change dynamically. A sketch of that approach is discussed in Appendix B below.

The algorithm for enumerating the list of compressible intermediate and root certificates is given below:
1. Query the CCADB for all known root and intermediate certificates {{CCADBAllCerts}}
2. Remove all certificates which have the extendedKeyUsage extension without the TLS Server Authentication bit or anyExtendedKeyUsage bit set.
3. Remove all certificates whose notAfter date is on or before the cutoff date.
4. Remove all roots which are not marked as trusted or in the process of applying to be trusted by at least one of the following Root Programs: Mozilla, Google, Microsoft, Apple.
5. Remove all intermediate certificates whose parent root certificates are no longer in the listing.
6. Remove any certificates which are duplicates (have the same representation as as sequence of DER bytes)
7. Order the list by the notBefore date of each certificate, breaking ties with the lexicographic ordering of the SHA256 certificate fingerprint.
8. Associate each element of the list with the concatenation of the constant `0x99` and its index in the list represented as a `uint16`.

**DISCUSS**: In the future, CCADB may expose such a listing directly. The list of included root programs might also benefit from being widened. A subset of these lists is available in `benchmarks/data` in the draft Github repository.

### Compression of CA Certificates in Certificate Chain

Compression Algorithm:
* Input: The byte representation of a `Certificate` message as defined in {{TLS13}} whose contents are `X509` certificates.
* Output: `opaque` bytes suitable for transmission in a `CompressedCertificate` message defined in {{TLSCertCompress}}.

1. Parse the message and extract a list of `CertificateEntry`s, iterate over the list.
2. Check if `cert_data` is byte-wise identical to any of the known intermediate or root certificates from the listing in the previous section.
   1.  If so, replace the opaque `cert_data` member of `CertificateEntry` with its adjusted three byte identifier and copy the `CertificateEntry structure with corrected lengths to the output.
   2. Otherwise, copy the `CertificateEntry` to the output.
3. Prepend the correct length information for the `Certificate` message.

The resulting output should be a well-formatted `Certificate` message payload with the known intermediate and root certificates replaced with three byte identifiers.

The decompression algorithm is simply repeating the above steps but swapping any recognized three-byte identifier in a `cert_data` field with the DER representation of the associated certificate.

## Pass 2: End-Entity Compression

This section describes two compression schemes based on Zstandard {{ZSTTD}} with application-specified dictionaries. The first scheme offers the best compression rate and is easy to implement but relies on unstandardized dictionary training steps which are unlikely to produce an output equitable for all CAs. The second scheme is not as efficient but is both equitable and easy to standardize.

**DISCUSS** This draft is largely agnostic as to which underlying compression scheme is used as long as it supports dictionaries. Is there an argument for use of an alternative scheme? E.g. Brotli.

**DISCUSS** It is intended that the first scheme be suitable for early experimentation and implementation for empirical validation. In parallel, the second scheme can likely be improved to match the performance of the first scheme whilst retaining equity and without resort to black box techniques.

## Scheme 1: Simple Baseline

Advantages:

* The dictionary is easy to format and ship as raw bytes .
* The implementation is near identical to the existing zstd TLS Certificate Compression, with the addition of the dictionary parameter.

Drawbacks:

* WebPKI clients that already have a copy of their trusted roots and intermediates must pay the storage cost of a second copy of these certificates.

#### Format of Shared Dictionary

Take the certificate listing defined in Section XX. Convert each certificate to DER and concatenate the bytes. The result will be passed directly to zstd as a raw dictionary.

#### Server Usage

When the client and server negotiate this TLS Compression Scheme as described in TODO, identified as `0xTODO`, the server MUST compress its certificate chain with zstd as described in TODO with the raw bytes  dictionary (See Section YY of zstd) defined in Section XX.

The server SHOULD use a high compression level as this is a one-time operation that can be reused for subsequent connections and has little impact on decompression speed. The server SHOULD perform this operation at startup and cache the result for future connections for performance. The server MAY rely on an external application to perform this compression (e.g. a script which provisions a file) and simply transmit the resulting bytes.

#### Client Usage

If the client offers this TLS Compression Scheme as described in TODO, identified as `0xTODO` and the server transmits a CompressedCertificate Message with this identifier, the client MUST decompress the contents using the zstd algorithm defined in XX and with the raw bytes dictionary described in Section XX of zstd and Section XX of this draft. The client MUST follow the requirements of TLS Cert Compression with respect to size.

## Scheme 2: Footprint Optimisation

Advantages:

* Clients which already ship a subset of the certificate listing for other purposes can reuse this data rather than having to ship a duplicate.

Disadvantages:

* Greater implementation complexity.

#### Format of the Shared Dictionary

Take the certificate listing defined in Section XX. Assign a two-byte identifier according to a lexicographic ordering, starting from 0x0000 and proceeding consecutively. Let the id of a cert be written `id(cert)`.

TODO: Take 100,000 certificates sampled from certificate transparency logs and submitted between XX and YY dates according to the following algorithm. Extract the end entity certificates and redact any domain entries. Train a zstd dictionary on the result.

TODO: Define a systematic way of building a smaller zstd dictionary based on certificate profiles, subject key identifiers, etc. Alternatively could ask CAs to profile a compression profile?

#### Compression

* Do keyword substitution on certificate chain, replacing certificate chain with 3 byte identifier where possible.
* Do keyed zstd dictionary on the remaining file.

**Decompression**

* Do keyed zstd dictionary on the message.
* Do keyword substitution.

## Preliminary Evaluation

This draft is very much a work in progress, however a preliminary evaluation based on a few thousand certificate chains is available.


| Compression Method                                     | Median Size (Bytes) | Relative Size |
| ------------------------------------------------------ | ------------------- | ------------- |
| Original, without any form of compression              | 4022                | 100%          |
| Using TLS Certificate Compression with zstd            | 3335                | 83%           |
| Transmitting only the End-Entity TLS Certificate       | 1664                | 41%           |
| TLS Cert Compression & Only End-Entity TLS Certificate | 1469                | 37%           |
| **This Draft, Scheme 1 - Baseline**                    | 1351                | 34%           |
| **This Draft, Scheme 2- Footprint**                    | 949                 | 24%           |

Performance is also greatly enhanced at the tails. For the optimized implementation:

| Percentile | Original | Scheme 2, This Draft | Relative Size |
| ---------- | -------- | -------------------- | ------------- |
| 5th        | 2755     | 641                  | 23%           |
| 50th       | 4022     | 949                  | 24%           |
| 95th       | 5801     | 1613                 | 28%           |

## Security Considerations

Note that as this draft specifies a compression scheme, it does not impact the negotiation of trust between clients and servers and is robust in the face of changes to CCADB or trust in a particular WebPKI CA. The client's trusted list of CAs does not need to be a subset or superset of the CCADB list and revocation of trust in a CA does not impact the operation of this compression scheme. Similarly, servers who use roots or intermediates outside the CCADB can still offer the scheme and benefit from it

## IANA Considerations

This document has no IANA actions.


--- back

## Acknowledgments

TODO acknowledge.

## Appendix: Background on the CCADB and Churn

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

## Appendix: Independent Extension?

* A scheme is an u16 id, a u16 major version and a u16 minor version.
  * Adding to a dictionary is a minor version bump.
  * Removing from a dictionary is a major version bump.
  * Expected: minor bump every month, major bump every year.
* CH: Convey a list of schemes.
* SH:
  * Select a version from the CH list.
  * Selected version must match on scheme id and major version and be equal to or less than the minor version.
