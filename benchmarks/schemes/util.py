import json
import zstandard as zstd
import logging
from functools import lru_cache

@lru_cache
def load_certificates():
        logging.info("Decompressing and parsing certificate chains")
        with open('data/chains.json.zst','rb') as zst_file:
            j = zstd.ZstdDecompressor().decompress(zst_file.read())
            data = json.loads(j)
            logging.info(f"Loaded {len(data)} certificate chains")
        return data