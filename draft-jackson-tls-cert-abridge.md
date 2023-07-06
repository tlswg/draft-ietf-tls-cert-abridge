---
title: "Abridged Compression for WebPKI Certificates"
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
 DATES: RFC3339

 AppleCTLogs:
   title: Certificate Transparency Logs trusted by Apple
   target: https://valid.apple.com/ct/log_list/current_log_list.json
   date: 2023-06-05
   author:
    -
      org: "Apple"

 GoogleCTLogs:
   title: Certificate Transparency Logs trusted by Google
   target: https://source.chromium.org/chromium/chromium/src/+/main:components/certificate_transparency/data/log_list.json
   date: 2023-06-05
   author:
    -
      org: "Google"

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

 ZstdImpl:
   title: ZStandard (Zstd)
   target: https://github.com/facebook/zstd
   date: 2023-06-05
   author:
    -
      org: "Facebook"

--- abstract

This drafts defines a WebPKI specific scheme for use in TLS Certificate Compression {{TLSCertCompress}}. The compression scheme relies on a predistributed static dictionary consisting of a snapshot of the root and intermediate certificates used in the WebPKI. The result is a substantial improvement over the existing generic compression schemes used in TLS, equitable for both CAs and website operators and avoids the need for trust negotiation or additional error handling. As the scheme removes the overhead of including root and intermediate certificates in the TLS handshake, it paves the way for a transition to TLS certificates using post-quantum signatures and has an outsized impact on QUIC's handshake latency due to limits on the size of the server's initial message flight. This compression scheme may also be of interest in other situations where certificate chains are stored, for example in the operation of Certificate Transparency logs.

--- middle

# Introduction

## Motivation

When a server responds to a TLS Client Hello, its initial flight of packets is limited in size by the underlying transport protocol. If the initial flight of packets exceeds the size limit, the server must wait for the client to acknowledge receipt, incurring the additional latency of a round trip before the handshake can complete. For TLS handshakes over TCP, the maximum size of the server’s initial flight is typically around 14,500 bytes. For TLS handshakes in QUIC, the limit is much lower at a maximum of 4500 bytes ({{RFC9000, Section 8.1}}).

The existing compression schemes used in {{TLSCertCompress}} have been shown to deliver a substantial improvement in QUIC handshake latency {{FastlyStudy}}, {{QUICStudy}} by reducing the size of server's certificate chain and so fitting the server's initial messages within a single flight. However, in a post-quantum setting, the signatures and public keys used in a TLS certificate chain will be typically 10 to 40 times their current size and cannot be compressed with existing TLS Certificate Compression schemes.
Consequently studies {{SCAStudy}} {{PQStudy}} have shown that post-quantum certificate transmission becomes the dominant source of latency in PQ TLS with certificate chains alone expected to exceed even the TCP initial flight limit. This motivates alternative designs for reducing the wire size of post-quantum certificate chains.

## Overview

This draft introduces a new compression scheme which is intended specifically for use in TLS Certificate Compression for WebPKI applications. It makes used of a shared dictionary between client and server consisting of all intermediate and root certificates contained in the root stores of major browsers sourced from the Common CA Database {{CCADB}}. As of May 2023, this dictionary would be 2.6 MB in size and consist of roughly 1500 intermediate certificates and 150 root certificates. The disk footprint can be reduced to near zero as many clients (such as Mozilla Firefox & Google Chrome) are already provisioned with their trusted intermediate and root certificates for compatibility and performance reasons.

Using a shared dictionary allows for this compression scheme to deliver dramatically more effective compression, reducing the size of certificate chains in use today by 75%, significantly improving on the 25% reduction achieved by existing {{TLSCertCompress}} schemes. Firstly, the intermediate and root certificates are compressed to a couple of bytes each and effectively no longer contribute to the wire size of the certificate chain. Secondly, the end-entity certificate can be further reduced by reference to strings in the shared dictionary. A preliminary evaluation of this scheme suggests that 50% of certificate chains in use today fit in under 1000 bytes and 95% fit in under 1500 bytes. This is substantially smaller than  can be achieved with the use of existing TLS certificate compression schemes and the suppression of CA certificates as proposed in {{SCA}}. This is because whilst {{SCA}} removes the intermediate and root certs from the chain entirely, this also removes the redundancy that generic TLS certificate compression schemes exploit.

It is also important to note that as this is only a compression scheme, it does not impact any trust decisions in the TLS handshake or perform trust negotiation. A client can offer this compression scheme whilst only trusting a subset of the certificates in the CCADB snapshot, similarly a server can offer this compression scheme whilst using a certificate chain which does not chain back to a WebPKI root. Further, a new root certificates are typically included in the CCADB at the start of their application to the root store, a process which typically takes more than a year and so if their application is approved will benefit from this compression scheme from the very first day of use on the web. As a result this scheme is equitable in so far as it provides equal benefits for all CAs in the WebPKI, doesn't privilege any particular end-entity certificate or website and allows WebPKI clients to make individual trust decisions without fear of breakage.

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

This draft refers to dates in Internet Date/Time Format as specified in {{Section 5.6 of DATES}} without the optional `T` separator.

# Abridged Compression Scheme {#scheme}

This section describes a compression scheme suitable for compressing certificate chains used in TLS. The scheme is defined in two parts. An initial pass compressing known intermediate and root certificates and then a subsequent pass compressing the end-entity certificate. This scheme is used by performing the compression step of Pass 1 and then the compression step of Pass 2. Decompression is performed in reverse order.

The compression scheme in this draft has two parameters listed below which influence the construction of the static dictionary. Future versions of this draft would use different parameters and so construct different dictionaries which would be registered under different TLS Certificate Compression code points. This is discussed further in {{deployment}}.

* `CCADB_SNAPSHOT_TIME` - 2023-01-01 00:00:00Z
* `CT_CERT_WINDOW` - 2022-12-01 00:00:00Z to 2023-01-01 00:00:00Z

## Pass 1: Intermediate and Root Compression

This pass relies on a shared listing of intermediate and root certificates known to both client and server. As many clients (e.g. Mozilla Firefox and Google Chrome) already ship with a list of trusted intermediate and root certificates, this pass allows for the members of the existing list to be included, rather than requiring them to have to be stored separately. This section first details how the client and server enumerate the known certificates, then describes how the listing is used to compress the certificate chain.

### Enumeration of Known Intermediate and Root Certificates {#listing}

The Common CA Database {{CCADB}} is operated by Mozilla on behalf of a number of Root Program operators including Mozilla, Microsoft, Google, Apple and Cisco. The CCADB contains a listing of all the root certificates trusted by the various root programs, as well as their associated intermediate certificates and new certificates from applicants to one or more root programs who are not yet trusted.

At the time of writing, the CCADB contains around 150 root program certificates and 1500 intermediate certificates which are trusted for TLS Server Authentication, occupying 2.6 MB of disk space. As this listing changes rarely and new inclusions typically join the CCADB listing year or more before they can be deployed on the web, the listing used in this draft will be the relevant certificates included in the CCADB at `CCADB_SNAPSHOT_TIME`.

The algorithm for enumerating the list of compressible intermediate and root certificates is given below:

1. Query the CCADB for all known root and intermediate certificates {{CCADBAllCerts}} as of `CCADB_SNAPSHOT_TIME`
2. Remove all certificates which have the extendedKeyUsage extension and do not have the TLS Server Authentication bit set or the anyExtendedKeyUsage bit set.
3. Remove all certificates whose notAfter date is on or before `CCADB_SNAPSHOT_TIME`.
4. Remove all root certificates which are not marked as trusted or in the process of applying to be trusted by at least one of the following root programs: Mozilla, Google, Microsoft, Apple.
5. Remove all intermediate certificates which are not signed by root certificates still in the listing.
6. Remove any certificates which are duplicates (have the same DER representation)
7. Order the list by the notBefore date of each certificate, breaking ties with the lexicographic ordering of the SHA256 certificate fingerprint.
8. Associate each element of the list with the concatenation of the constant `0x99` and its index in the list represented as a `uint16`.

**DISCUSS:** The four programs were selected because they represent certificate consumers in the CCADB. Are there any other root programs which ought to be included? The only drawback is a larger disk requirement, since this compression scheme does not impact trust decisions.

**TODO:** Ask CCADB to provide an authoritative copy of this listing. A subset of these lists is available in `benchmarks/data` in this draft's repository.

### Compression of CA Certificates in Certificate Chain

Compression Algorithm:

* Input: The byte representation of a `Certificate` message as defined in {{TLS13}} whose contents are `X509` certificates.
* Output: `opaque` bytes suitable for transmission in a `CompressedCertificate` message defined in {{TLSCertCompress}}.

1. Parse the message and extract a list of `CertificateEntry`s, iterate over the list.
2. Check if `cert_data` is byte-wise identical to any of the known intermediate or root certificates from the listing in the previous section.
   1. If so, replace the opaque `cert_data` member of `CertificateEntry` with its adjusted three byte identifier and copy the `CertificateEntry` structure with corrected lengths to the output.
   2. Otherwise, copy the `CertificateEntry` entry to the output.
3. Prepend the correct length information for the `Certificate` message.

The resulting output should be a well-formatted `Certificate` message payload with the known intermediate and root certificates replaced with three byte identifiers.

The decompression algorithm is simply repeating the above steps but swapping any recognized three-byte identifier in a `cert_data` field with the DER representation of the associated certificate and correcting the length field.

## Pass 2: End-Entity Compression

This section describes a pass based on Zstandard {{ZSTD}} with application-specified dictionaries. The dictionary is constructed with reference to the list of intermediate and root certificates discussed earlier in {{listing}}, as well as several external sources of information.

**DISCUSS:** This draft is largely agnostic as to which underlying compression scheme is used as long as it supports dictionaries. Is there an argument for use of an alternative scheme?

### Format of Shared Dictionary

**DISCUSS:** This section remains a work in progress. The goal is to produce a dictionary of minimal size which provides maximum compression whilst treating every CA equitably. Currently this dictionary occupies ~65KB of space, is equitable and has performance within a ~100 bytes of the best known alternative. This is discussed further in {{eval}}.

The dictionary is built by systematic combination of the common strings used in certificates by each issuer in the known list described in {{listing}}. This dictionary is constructed in three stages, with the output of each stage being concatenated with the next.

Firstly, for each intermediate certificate enumerated in the listing in {{listing}}., extract the issuer field ({{Section 4.1.2.4 of !RFC5280}}) and derive the matching authority key identifier ({{Section 4.2.1.1 of RFC5280}}) for the certificate. Order them according to the listing in {{listing}}.

Secondly, take the listing of certificate transparency logs trusted by the root programs selected in {{listing}}, which are located at{{AppleCTLogs}} {{GoogleCTLogs}} as of `CCADB_SNAPSHOT_TIME` and extract the list of log identifiers. Remove duplicates and order them lexicographically.

Finally, enumerate all certificates contained within certificate transparency logs above and issued during `CT_CERT_WINDOW`. For each issuer in the listing in {{listing}}, select the witnessed end-entity certificate with the lowest serial number. Extract the contents of the following extensions from the end-entity certificate:

* Authority Information Access ({{Section 4.2.2.1 of RFC5280}})
* Certificate Policies  ({{Section 4.2.1.4 of RFC5280}})
* CRL Distribution Points ({{Section 4.2.1.13 of RFC5280}})
* Freshest CRL ({{Section 4.2.1.15 of RFC5280}})

Concatenate the byte representation of each extension (including extension id and length) and copy it to the output. If no end-entity certificate can be found for an issuer with this process, omit the entry for that issuer.

#### Compression of End-Entity Certificates in Certificate Chain

The resulting bytes from Pass 1 are passed to ZStandard {{ZSTD}} with the dictionary specified in the previous section. It is RECOMMENDED that the compressor (i.e. the server) use the following parameters:

 * `chain_log=30`
 * `search_log=30`
 * `hash_log=30`
 * `target_length=6000`
 * `threads=1`
 * `compression_level=22`
 * `force_max_window=1`

These parameters are recommended in order to achieve the best compression ratio however implementations MAY use their preferred parameters as these parameters are not used during decompression. With TLS Certificate Compression, the server needs to only perform a single compression at startup and cache the result, so optimizing for maximal compression is recommended. The client's decompression speed is insensitive to these parameters.

# Preliminary Evaluation {#eval}

**NOTE:** This section to be removed prior to publication.

This draft is a work in progress, however a preliminary evaluation based on a few thousand certificate chains is available. The storage footprint refers to the on-disk size required for the end-entity dictionary. The other columns report the 5th, 50th and 95th percentile of the resulting certificate chains. The evaluation set was a ~75,000 certificate chains from the Tranco list.

| Scheme                                               |   Storage Footprint |   p5 |   p50 |   p95 |
|------------------------------------------------------|---------------------|------|-------|-------|
| Original                                             |                   0 | 2308 |  4032 |  5609 |
| TLS Cert Compression                                 |                   0 | 1619 |  3243 |  3821 |
| Intermediate Suppression and TLS Cert Compression    |                   0 | 1020 |  1445 |  3303 |
| **This Draft**                                       |               65336 |  661 |  1060 |  1437 |
| **This Draft with opaque trained dictionary**        |                3000 |  562 |   931 |  1454 |
| Hypothetical Optimal Compression                     |                   0 |  377 |   742 |  1075 |

 * 'Original' refers to the sampled certificate chains without any compression.
 * 'TLS Cert Compression' used ZStandard with the parameters configured for maximum compression as defined in {{TLSCertCompress}}.
 * 'Intermediate Suppression and TLS Cert Compression' was modelled as the elimination of all certificates in the intermediate and root certificates with the Basic Constraints CA value set to true. If a cert chain included an unrecognized certificate with CA status, then no CA certificates were removed from that chain. The cert chain was then passed to 'TLS Cert Compression' as a second pass.
 * 'This Draft with opaque trained dictionary' refers to pass 1 and pass 2 as defined by this draft, but instead using a 3000 byte dictionary for pass 2 which was produced by the Zstandard dictionary training algorithm. This illustrates a ceiling on what ought to be possible by improving the construction of the pass 2 dictionary in this document. However, using this trained dictionary directly will not treat all CA's equitably, as the dictionary will be biased towards compressing the most popular CAs more effectively.
 * 'Hypothetical Optimal Compression' is the resulting size of the cert chain after reducing it to only the public key in the end-entity certificate, the CA signature over the EE cert, the embedded SCT signatures and a compressed list of domains in the SAN extension. This represents the best possible compression as it entirely removes any identifiers, field tags and lengths and non-critical extensions such as OCSP, CRL and policy extensions.

# Deployment Considerations {#deployment}

## Dictionary Versioning

The scheme defined in this draft is deployed with the static dictionaries constructed from the parameters listed in {{scheme}} fixed to a particular TLS Certificate Compression code point.

As new CA certificates are added to the CCADB and deployed on the web, new versions of this draft would need to be issued with their own code point and dictionary parameters.However, the process of adding new root certificates to a root store is already a two to three year process and this scheme includes untrusted root certificates still undergoing the application process in its dictionary. As a result, it would be reasonable to expect a new version of this scheme with updated dictionaries to be issued at most once a year and more likely once every two or three years.

A more detailed analysis and discussion of CA certificate lifetimes and root store operations is included in {{churn}}, as well as an alternative design which would allow for dictionary negotiation rather than fixing one dictionary per code point.

**DISCUSS:** Are there concerns over this approach? Would using one code point per year be acceptable? Currently 3 of the 16384 'Specification Required' IANA managed code points are in use.

## Version Migration

As new versions of this scheme are specified, clients and servers would benefit from migrating to the latest version. Whilst servers using CA certificates outside the scheme's listing can still offer this compression scheme and partially benefit from it, migrating to the latest version ensures that new CAs can compete on a level playing field with existing CAs. It is possible for a client or server to offer multiple versions of this scheme without having to pay twice the storage cost, since the majority of the stored data is in the pass 1 certificate listing and the majority of certificates will be in both versions and so need only be stored once.

Clients and servers SHOULD offer the latest version of this scheme and MAY offer one or more historical versions. Although clients and servers which fall out of date will no longer benefit from the scheme, they will not suffer any other penalties or incompatibilities. Future schemes will likely establish recommended lifetimes for sunsetting a previous version and adopting a new one.

As the majority of clients deploying this scheme are likely to be web browsers which typically use monthly release cycles (even long term support versions like Firefox ESR), this is unlikely to be a restriction in practice. The picture is more complex for servers as operators are often to reluctant to update TLS libraries, but as a new version only requires changes to static data and not to code and should happen less than yearly, this is unlikely to be burdensome in practice.

## Disk Space Requirements

Clients and servers implementing this scheme need to store a listing of root and intermediate certificates for pass 1, which currently occupies around ~2.6 MB and a smaller dictionary on the order of ~100 KB for pass 2. Clients and servers offering multiple versions of this scheme do not need to duplicate the pass 1 listing, as multiple versions can refer to same string.

As popular web browsers already ship a complete list of trusted intermediate and root certificates, their additional storage requirements are minimal. Servers offering this scheme are intended to be 'full-fat' web servers and so typically have plentiful storage already. This draft is not intended for use in storage-constrained IoT devices, but alternative versions with stripped down listings may be suitable.

## Implementation Complexity

Although much of this draft is dedicated to the construction of the certificate list and dictionary used in the scheme, implementations are indifferent to these details. Pass 1 can be implemented as a simple string substitution and pass 2 with a single call to permissively licensed and widely distributed Zstandard implementations such as {{ZstdImpl}}. Future versions of this draft which vary the dictionary construction then only require changes to the static data shipped with these implementations and the use of a new code point.

There are several options for handling the distribution of the associated static data. One option is to distribute it directly with the TLS library and update it as part of that library's regular release cycles. Whilst this is easy for statically linked libraries written in languages which offer first-class package management and compile time feature selection (e.g. Go, Rust), it is trickier for dynamically linked libraries who are likely unwilling to incur the increased distribution size. In these ecosystems it may make sense to distribute the dictionaries are part of an independent package managed by the OS which can be discovered by the library at run-time. Another alternative would be to have existing automated certificate tooling provision the library with both the full certificate chain and multiple precompressed chains during the certificate issuance / renewal process.

# Security Considerations

This draft does not introduce new security considerations for TLS, except for the considerations already identified in {{TLSCertCompress}}.  In particular incorrect compression or decompression will lead to the TLS connection failing as the two parties will not agree on the transcript and the server's transcript never includes the result of the compressed certificate chain. However, implementors SHOULD use a memory-safe language to implement this compression scheme.

Note that as this draft specifies a compression scheme, it does not impact the negotiation of trust between clients and servers and is robust in the face of changes to CCADB or trust in a particular WebPKI CA. The client's trusted list of CAs does not need to be a subset or superset of the CCADB list and revocation of trust in a CA does not impact the operation of this compression scheme. Similarly, servers who use roots or intermediates outside the CCADB can still offer the scheme and benefit from it.

# IANA Considerations

**TODO:** Adopt an identifier for experimental purposes.

--- back

# Acknowledgments

The authors thank Bas Westerbaan, Martin Thomson and Kathleen Wilson for feedback on early versions of this document.

# CCADB Churn and Dictionary Negotiation {#churn}

## CCADB Churn

Typically around 10 or so new root certificates are introduced to the WebPKI each year. The various root programs restrict the lifetimes of these certificates, Microsoft to between 8 and 25 years ([3.A.3](https://learn.microsoft.com/en-us/security/trusted-root/program-requirements)), Mozilla to between 0 and 14 years ([Summary](https://wiki.mozilla.org/CA/Root_CA_Lifecycles)). Chrome has proposed a maximum lifetime of 7 years in the future ([Blog Post](https://www.chromium.org/Home/chromium-security/root-ca-policy/moving-forward-together/)). Some major CAs have objected to this proposed policy as the root inclusion process currently takes around 3 years from start to finish ([Digicert Blog](https://www.digicert.com/blog/googles-moving-forward-together-proposals-for-root-ca-policy)). Similarly, Mozilla requires CAs to apply to renew their roots with at least 2 years notice ([Summary](https://wiki.mozilla.org/CA/Root_CA_Lifecycles)).

Typically around 100 to 200 new WebPKI intermediate certificates are issued each year. No WebPKI root program currently limits the lifetime of intermediate certificates, but they are in practice capped by the lifetime of their parent root certificate. The vast majority of these certificates are issued with 10 year lifespans. A small but notable fraction (<10%) are issued with 2 or 3 year lifetimes. Chrome's Root Program has proposed that Intermediate Certificates be limited to 3 years in the future ([Update](https://www.chromium.org/Home/chromium-security/root-ca-policy/moving-forward-together/)). However, the motivation for this requirement is unclear. Unlike root certificates, intermediate certificates are only required to be disclosed with a month's notice to the CCADB ([Mozilla Root Program Section 5.3.2](https://www.mozilla.org/en-US/about/governance/policies/security-group/certs/policy/#53-intermediate-certificates), [Chrome Policy](https://www.chromium.org/Home/chromium-security/root-ca-policy/)).

## Dictionary Negotiation

This draft is currently written with a view to being adopted as a particular TLS Certificate Compression Scheme. However,
this means that each dictionary used in the wild must have an assigned code point. A new dictionary would likely need to be
issued no more than yearly. However, negotiating the dictionary used would avoid that overhead.

**DISCUSS:** A sketch for how dictionary negotiation might work is below.

This draft would instead define a new extension, which would define TLS Certificate Compression with ZStandard Dictionaries. Dictionaries would be identified by an IANA-assigned identifier of two bytes, with a further two bytes for the major version and two more for the minor version. Adding new certificates to a dictionary listing would require a minor version bump. Removing certificates or changing the pass 2 dictionary would require a major version bump.

The client lists their known dictionaries in an extension in the ClientHello. The client need only retain and advertise the highest known minor version for any major version of a dictionary they are willing to offer. The server may select any dictionary it has a copy of with matching identifier, matching major version number and a minor version number not greater than the client's minor version number.

The expectation would be that new minor versions would be issued monthly or quarterly, with new major versions only every year or multiple years. This reflects the relative rates of when certificates are added or removed to the CCADB listing. This means in practice clients would likely offer a single dictionary containing their latest known version. Servers would only need to update their dictionaries yearly when a new major version is produced.
