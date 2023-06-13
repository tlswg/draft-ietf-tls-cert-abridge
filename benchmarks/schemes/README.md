# Schemes

## Howto

* Define a scheme within a python file.
* Each scheme should be a class exposing:
  * NAME: A top-level constant defining the name of the scheme.
  * Setup() -> An instance of the class.
  * Compress([certs]) -> bytes
  * Decompress([certs]) -> bytes
* For convenience, compress and decompress are given a list of DER encoded certificates.