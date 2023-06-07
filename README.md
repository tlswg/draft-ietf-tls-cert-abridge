# Abridged Certificate Compression for the WebPKI

This is the working area for the individual Internet-Draft, "Abridged Certificate Compression for the WebPKI".

This drafts defines WebPKI specific compression scheme for use in [TLS Certificate Compression](https://www.rfc-editor.org/rfc/rfc8879.html). The compression scheme relies on a static dictionary consisting of a snapshot of the root and intermediate certificates used in the WebPKI. The result is a dramatic improvement over the existing generic compression schemes used in TLS, equitable for both CAs and website operators and avoids the need for trust negotiation or additional error handling. 

As the scheme removes the overhead of including root and intermediate certificates in the TLS handshake, it paves the way for a transition to PQ TLS certificates and has an outsized impact on QUIC's performance due to magnification limits on the server's response. This compression scheme may also be of interest in other situations where certificate chains are stored, for example in the operation of Certificate Transparency logs.

* [Editor's Copy](https://dennisjackson.github.io/draft-jackson-tls-cert-abridge/#go.draft-jackson-tls-cert-abridge.html)

## Preliminary Evaluation

This draft is very much a work in progress, however a preliminary evaluation based on a few thousand certificate chains is available.

| Compression Method                                     | Median Size (Bytes) | Relative Size |
|--------------------------------------------------------|---------------------|---------------|
| Original, without any form of compression              | 4022                | 100%          |
| Using TLS Certificate Compression with zstd            | 3335                | 83%           |
| Transmitting only the End-Entity TLS Certificate       | 1664                | 41%           |
| TLS Cert Compression & Only End-Entity TLS Certificate | 1469                | 37%           |
| **This Draft, Naive Implementation**                   | **1351**            | **34%**       |
| **This Draft, Optimized Implementation**               | **949**             | **24%**       |

Performance is also greatly enhanced at the tails. For the optimized implementation:

| Percentile      | Original  | This Draft    | Relative Size |
|-----------------|-----------|---------------|---------------|
| 5th             | 2755      | 641           | 23%           |
| 50th            | 4022      | 949           | 24%           |
| 95th            | 5801      | 1613          | 28%           |

## Contributing

See the [guidelines for contributions](https://github.com/dennisjackson/draft-jackson-tls-cert-abridge/blob/main/CONTRIBUTING.md).

Contributions can be made by creating pull requests. The GitHub interface supports creating pull requests using the Edit (✏) button. 

Formatted text and HTML versions of the draft can be built using `make`. Command line usage requires that you have the necessary software installed.  See [the instructions](https://github.com/martinthomson/i-d-template/blob/main/doc/SETUP.md).

