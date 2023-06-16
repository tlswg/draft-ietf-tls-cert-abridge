import schemes.zstd_base
import schemes.ccadb
import base64
from tqdm import tqdm
from schemes.util import load_certificates, load_ee_certs
from schemes.certs import cert_redactor, CommonByte
import logging
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import oid
from cryptography.x509.extensions import ExtensionNotFound
import zstandard


class DictCompress:
    def __init__(self, entries):
        self.cmap = dict()
        self.dmap = dict()
        prefix = b"\x12\x34"
        identifier = 0
        for e in entries:
            eid = prefix + identifier.to_bytes(2, "big")
            self.cmap[e] = eid
            self.dmap[eid] = e
            identifier += 1

    def name(self):
        return "Base: Dictionary Compressor"

    def compress(self, certList):
        compressed = b""
        for c in certList:
            if c in self.cmap.keys():
                compressed += self.cmap[c]
            else:
                cert = x509.load_der_x509_certificate(c)
                try:
                    if cert.extensions.get_extension_for_oid(
                        oid.ExtensionOID.BASIC_CONSTRAINTS
                    ).value.ca:
                        logging.warning(
                            f"CA Certificate {cert.subject.rfc4514_string()} issued by {cert.issuer.rfc4514_string()} not found in prefix dictionary. sha256-fingerprint={cert.fingerprint(hashes.SHA256()).hex()[:6]}"
                        )
                        # logging.info(f"{cert.public_bytes(serialization.Encoding.PEM)}")
                        compressed += b"\x12\x34\00\00"
                except ExtensionNotFound:
                    pass
                compressed += c
            first = False
        return compressed

    def decompress(self, compressed_data):
        # TODO - Needs to know to skip the first cert
        pass


class PrefixOnly:
    def __init__(self):
        self.inner1 = DictCompress(schemes.ccadb.ccadb_certs())

    def footprint(self):
        return 0  # TODO + Overhead of microsoft certs

    def name(self):
        return f"Method 2: CA Prefix Only"

    def compress(self, certList):
        return self.inner1.compress(certList)

    def decompress(self, compressed_data):
        return self.inner1.decompress(compressed_data)


class PrefixAndTrained:
    def __init__(self, dictSize, redact):
        self.redact = redact
        self.dictSize = dictSize
        self.inner1 = DictCompress(schemes.ccadb.ccadb_certs())
        self.inner2 = schemes.zstd_base.zstdPython(
            shared_dict=self.buildEEDict(dictSize)
        )

    def footprint(self):
        return self.dictSize  # TODO + Overhead of non Mozilla Certs

    def name(self):
        return f"Method 2: CA Prefix and Trained Zstd {self.dictSize}, redacted={self.redact}"

    def compress(self, certList):
        return self.inner2.compressBytes(self.inner1.compress(certList))

    def decompress(self, compressed_data):
        return self.inner1.decompress(self.inner2.decompress(compressed_data))

    def buildEEDict(self, dictSize):
        return schemes.zstd_base.zstdTrainPython(dictSize, load_ee_certs(self.redact))


class PrefixAndSystematic:
    def __init__(self, threshold):
        self.inner1 = DictCompress(schemes.ccadb.ccadb_certs())
        self.threshold = threshold
        d = self.buildEEDict(threshold)
        self.dictSize = len(d)
        self.inner2 = schemes.zstd_base.zstdPython(shared_dict=d)

    def name(self):
        return f"Method 2: CA Prefix and Systematic Zstd threshold={self.threshold}"

    def footprint(self):
        return self.dictSize  # TODO + Overhead from non-Mozilla Root Stores

    def compress(self, certList):
        return self.inner2.compressBytes(self.inner1.compress(certList))

    def decompress(self, compressed_data):
        return self.inner1.decompress(self.inner2.decompress(compressed_data))

    def buildEEDict(self, threshold):
        data = load_certificates()
        ee = [
            base64.b64decode(x[0])
            for x in tqdm(data, desc="Decoding end entity certificates")
        ]
        ingester = CommonByte(threshold)
        for c in ee:
            ingester.ingest(c)
        return zstandard.ZstdCompressionDict(ingester.common())
