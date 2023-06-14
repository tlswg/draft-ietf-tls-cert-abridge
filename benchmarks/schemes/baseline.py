import schemes.zstd_base
import schemes.ccadb
class Baseline:
    def __init__(self):
        d = b"".join(schemes.ccadb.ccadb_certs())
        self.dictSize = len(d)
        self.inner = schemes.zstd_base.ZstdBase(d)

    def name(self):
        return "Method 1: Baseline"

    def footprint(self):
        return self.dictSize

    def compress(self, certList):
        return self.inner.compress(certList)

    def decompress(self, compressed_data):
        return self.inner.decompress(compressed_data)
