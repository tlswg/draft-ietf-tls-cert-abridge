# Schemes

## Adding a Scheme

Define a class with this format:

```
class NullCompressor:
    def __init__(self):
        pass

    def name(self):
        return "Original"

    def footprint(self):
        return 0 # Storage Footprint on disk

    def compress(self, cert_chain):
        return b"".join(cert_chain)

    def decompress(self, compressed_data):
        return compressed_data
```

Add an instantiation of the class to `load_schemes` in `benchmark.py`.

## Structure

* `abridged.py` - Compression Schemes introduced in this draft
* `existing.py` - Existing Options
* `internal.py` - Internal compression schemes wrapped by others
* `certs.py` - Utility functions for working with CA certificates and certificate chains