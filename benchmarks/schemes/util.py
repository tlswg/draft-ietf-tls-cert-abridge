import json
import zstandard as zstd
import logging
from functools import lru_cache
import schemes.certs
import base64
from tqdm import tqdm

@lru_cache
def load_certificates():
        logging.info("Decompressing and parsing certificate chains")
        with open('data/chains.json.zst','rb') as zst_file:
            j = zstd.ZstdDecompressor().decompress(zst_file.read())
            data = json.loads(j)
            logging.info(f"Loaded {len(data)} certificate chains")
        return data

@lru_cache
def load_ee_certs(redact):
    data = load_certificates()
    ee = [base64.b64decode(x[0]) for x in tqdm(data,desc="b64 decoding certs")]
    if redact:
        ee = [schemes.certs.cert_redactor(x) for x in tqdm(ee,desc='Redacting end-entity certificates')]
    return ee