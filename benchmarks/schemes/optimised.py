import schemes.zstd_base
import schemes.ccadb
import base64
import tempfile
from tqdm import tqdm
from schemes.util import load_certificates
from schemes.certs import cert_redactor, CommonByte
import logging
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from  cryptography.x509 import oid

class DictCompress:
    def __init__(self, entries):
        self.cmap = dict()
        self.dmap = dict()
        prefix = b'\x12\x34'
        identifier = 0
        for e in entries:
            eid = prefix + identifier.to_bytes(2,'big')
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
                if cert.extensions.get_extension_for_oid(oid.ExtensionOID.BASIC_CONSTRAINTS).value.ca:
                    logging.warning(f"CA Certificate {cert.subject.rfc4514_string()} issued by {cert.issuer.rfc4514_string()} not found in prefix dictionary. sha256-fingerprint={cert.fingerprint(hashes.SHA256()).hex()[:6]}")
                    # logging.info(f"{cert.public_bytes(serialization.Encoding.PEM)}")
                    compressed += b"\x12\x34\00\00"
                compressed += c
            first = False
        return compressed

    def decompress(self, compressed_data):
        #TODO - Needs to know to skip the first cert
        pass

class PrefixAndTrained:
    def __init__(self,dictSize,redact):
        self.redact = redact
        self.dictSize = dictSize
        self.inner1 = DictCompress(schemes.ccadb.ccadb_certs())
        self.inner2 = schemes.zstd_base.ZstdBase(shared_dict=self.buildEEDict(dictSize))

    def name(self):
        return f"Method 2: CA Prefix and Trained Zstd {self.dictSize}, redacted={self.redact}"

    def compress(self, certList):
        return self.inner2.compressBytes(self.inner1.compress(certList))

    def decompress(self, compressed_data):
        return self.inner1.decompress(self.inner2.decompress(compressed_data))


    def buildEEDict(self,dictSize):
        data = load_certificates()
        ee = [base64.b64decode(x[0]) for x in tqdm(data,desc="b64 decoding certs")]
        if self.redact:
            ee = [cert_redactor(x) for x in tqdm(ee,desc='Redacting end-entity certificates')]
        with tempfile.TemporaryDirectory() as temp_dir:
            for index, cert in tqdm(enumerate(ee),desc='Writing files for zstd dict training'):
                file_path = f"{temp_dir}/{index}.bin"
                with open(file_path, 'wb') as file:
                    file.write(cert)
            schemes.zstd_base.zstdTrain(dictSize,temp_dir)
            with open(f"{temp_dir}/dictionary.bin",'rb') as dFile:
                dBytes = dFile.read()
                return dBytes


class PrefixAndSystematic:
    def __init__(self,threshold):
        self.inner1 = DictCompress(schemes.ccadb.ccadb_certs())
        self.inner2 = schemes.zstd_base.ZstdBase(shared_dict=self.buildEEDict(threshold))

    def name(self):
        return "Method 2: CA Prefix and Systematic Zstd"

    def compress(self, certList):
        return self.inner2.compressBytes(self.inner1.compress(certList))

    def decompress(self, compressed_data):
        return self.inner1.decompress(self.inner2.decompress(compressed_data))


    def buildEEDict(self,threshold):
        data = load_certificates()
        ee = [base64.b64decode(x[0]) for x in tqdm(data,desc="Decoding end entity certificates")]
        ingester = CommonByte(threshold)
        for c in ee:
            ingester.ingest(c)
        return ingester.common()