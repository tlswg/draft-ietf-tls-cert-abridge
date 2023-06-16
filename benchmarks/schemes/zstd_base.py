import zstandard

ZSTD_LEVEL = 22


class zstdPython:
    def __init__(self, shared_dict=None):
        # self.dictBytes = zstandard.ZstdCompressionDict(shared_dict)
        params = zstandard.ZstdCompressionParameters(
            chain_log=30,
            search_log=30,
            hash_log=30,
            target_length=6000,
            threads=1,
            compression_level=ZSTD_LEVEL,
            force_max_window=1,
        )
        self.comp = zstandard.ZstdCompressor(
            compression_params=params, dict_data=shared_dict
        )

    def name(self):
        return "Zstd Python"

    def compress(self, certList):
        return self.compressBytes(b"".join(certList))

    def compressBytes(self, data):
        return self.comp.compress(data)

    def decompress(self, compressed_data):
        # TODO Not Implemented
        pass


def zstdTrainPython(targetSize, samples):
    return zstandard.train_dictionary(
        targetSize, samples, level=ZSTD_LEVEL, notifications=2, threads=-1, accel=5
    )  # TODO accel=1 is much slower but more accurate
