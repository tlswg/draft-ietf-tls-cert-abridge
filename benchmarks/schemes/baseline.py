import schemes.zstd_base
import schemes.ccadb
class Baseline:
    def __init__(self):
        self.inner = schemes.zstd_base.ZstdBase(b"".join(schemes.ccadb.ccadb_certs()))

    def name(self):
        return "Method 1: Baseline"

    def compress(self, certList):
        return self.inner.compress(certList)

    def decompress(self, compressed_data):
        return self.inner.decompress(compressed_data)
