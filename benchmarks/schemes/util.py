import json
import zstandard as zstd
import logging

DATA = None

def load_certificates():
    global DATA
    if not DATA:
        logging.info("Decompressing and parsing certificate chains")
        with open('data/chains.json.zst','rb') as zst_file:
            j = zstd.ZstdDecompressor().decompress(zst_file.read())
            data = json.loads(j)
            DATA = data
            logging.info(f"Loaded {len(data)} certificate chains")
    return DATA
