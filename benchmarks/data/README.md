# Data for Benchmarks

* `chains.json` - Certificate Chains fetched from TLS handshakes with the Tranco Top 10k. Each record contains an array of certificates. Each certificate is encoded as base64 of the raw DER (aka lazy PEM format).
* [AllMozillaIntermediates](https://ccadb.my.salesforce-sites.com/mozilla/PublicAllIntermediateCertsWithPEMCSV) - Contains all Intermediate Certificates trusted by Mozilla. The last column contains the certificate in PEM Format. TODO: May have S/MIME Intermediates?
* [AllMozillaPendingRoots](https://ccadb.my.salesforce-sites.com/mozilla/UpcomingRootInclusionsReportCSVFormat) - Contains Roots undergoing inclusion and a download link to their PEM formats.
* [AllMozillaRoots](https://ccadb.my.salesforce-sites.com/mozilla/IncludedRootsPEMCSV?TrustBitsInclude=Websites) - All Root Certificates trusted by Mozilla for TLS.
* [AllMicrosoftRoots](https://ccadb-public.secure.force.com/microsoft/IncludedCACertificateReportForMSFTCSVPEM) - All Root Certificates trusted by Microsoft, including for non-TLS purposes.