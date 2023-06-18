from schemes.internal import ZstdWrapper, DictCompress, zstandard_train_dict
from schemes.certs import (
    load_ee_certs_from_chains,
    CommonCertStrings,
    get_all_ccadb_certs,
)
import zstandard

# TODO: These footprints don't reflect any additional storage caused by
#       storing CA certs from outside the client's current root store.


class Baseline:
    def __init__(self):
        ccadb_dict = b"".join(get_all_ccadb_certs())
        self.dict_size = len(ccadb_dict)
        self.inner = ZstdWrapper(zstandard.ZstdCompressionDict(ccadb_dict))

    def name(self):
        return "Method 1: Baseline"

    def footprint(self):
        return self.dict_size

    def compress(self, cert_chain):
        return self.inner.compress(cert_chain)

    def decompress(self, compressed_data):
        return self.inner.decompress(compressed_data)


class PrefixOnly:
    def __init__(self):
        self.inner1 = DictCompress(get_all_ccadb_certs())

    def footprint(self):
        return 0

    def name(self):
        return "CA Prefix Only"

    def compress(self, cert_chain):
        return self.inner1.compress(cert_chain)

    def decompress(self, compressed_data):
        return self.inner1.decompress(compressed_data)


class PrefixAndTrained:
    def __init__(self, dict_size, redact):
        self.redact = redact
        self.dict_size = dict_size
        self.inner1 = DictCompress(get_all_ccadb_certs())
        self.inner2 = ZstdWrapper(
            shared_dict=zstandard_train_dict(
                load_ee_certs_from_chains(self.redact),
                dict_size,
            )
        )

    def footprint(self):
        return self.dict_size

    def name(self):
        return f"Method 2: CA Prefix with Training redacted={self.redact}"

    def compress(self, cert_chain):
        return self.inner2.compress_bytes(self.inner1.compress(cert_chain))

    def decompress(self, compressed_data):
        return self.inner1.decompress(self.inner2.decompress(compressed_data))


class PrefixAndCommon:
    def __init__(self, threshold):
        self.inner1 = DictCompress(get_all_ccadb_certs())
        self.threshold = threshold
        common_dict = self.build_dict(threshold)
        self.dict_size = len(common_dict)
        self.inner2 = ZstdWrapper(shared_dict=common_dict)

    def name(self):
        return f"Method 2: CA Prefix and CommonStrings threshold={self.threshold}"

    def footprint(self):
        return self.dict_size

    def compress(self, cert_chain):
        return self.inner2.compress_bytes(self.inner1.compress(cert_chain))

    def decompress(self, compressed_data):
        return self.inner1.decompress(self.inner2.decompress(compressed_data))

    def build_dict(self, threshold):
        cert_strings = CommonCertStrings(threshold)
        cert_strings.ingest_all(load_ee_certs_from_chains(redact=False))
        return zstandard.ZstdCompressionDict(cert_strings.top())
