---
###
# Internet-Draft Markdown Template
#
# Rename this file from draft-todo-yourname-protocol.md to get started.
# Draft name format is "draft-<yourname>-<workgroup>-<name>.md".
#
# For initial setup, you only need to edit the first block of fields.
# Only "title" needs to be changed; delete "abbrev" if your title is short.
# Any other content can be edited, but be careful not to introduce errors.
# Some fields will be set automatically during setup if they are unchanged.
#
# Don't include "-00" or "-latest" in the filename.
# Labels in the form draft-<yourname>-<workgroup>-<name>-latest are used by
# the tools to refer to the current version; see "docname" for example.
#
# This template uses kramdown-rfc: https://github.com/cabo/kramdown-rfc
# You can replace the entire file if you prefer a different format.
# Change the file extension to match the format (.xml for XML, etc...)
#
###
title: "Abridged Certificate Compression for the WebPKI"
abbrev: "Abridged Certs"
category: info

docname: draft-jackson-tls-cert-abridge
submissiontype: IETF  # also: "independent", "IAB", or "IRTF"
number:
date:
consensus: true
v: 3
area: Security
workgroup: TLS
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
It defines a compression scheme suitable for use in [RFC 8879: TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html) which delivers a substantial improvement over the existing generic compression schemes in use today whilst ensuring equitable treatment for both CAs and website operators.

This draft may also be useful in other situations where certificate chains are stored, for example, in the operation of Certificate Transparency logs.

--- middle

# Introduction

TODO Introduction


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

# Deployment Considerations

# Security Considerations

TODO Security


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
