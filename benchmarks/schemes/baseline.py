
import zlib
import csv
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import tempfile
import subprocess

class BaselinePurePython:
    def __init__(self):
        self.dict = self.build_dict()
        self.comp = zlib.compressobj(zlib.Z_BEST_COMPRESSION, zlib.DEFLATED, 15, 9, zlib.Z_DEFAULT_STRATEGY,zdict=self.dict)
        self.decomp = zlib.decompressobj(zlib.MAX_WBITS,self.dict)

    def name(self):
        return "Method 1: Baseline in Pure Python"

    def compress(self, certList):
        c = self.comp.copy()
        return c.compress(b"".join(certList)) + c.flush()

    def decompress(self, compressed_data):
        d = self.decomp.copy()
        return d.decompress(compressed_data) + d.flush()

    def build_dict(self):
        d = b""
        with open('data/AllMozillaRoots.csv') as roots:
            table = csv.reader(roots)
            first = True
            for r in table:
                if first:
                    first = False
                    continue
                cert = x509.load_pem_x509_certificate(r[-1].encode(), default_backend())
                cert_val = cert.public_bytes(serialization.Encoding.DER)
                d += cert_val
        with open('data/AllMozillaIntermediates.csv') as intermediates:
            #TODO Fix Lazy Copy Paste
            table = csv.reader(intermediates)
            first = True
            for r in table:
                if first:
                    first = False
                    continue
                cert = x509.load_pem_x509_certificate(r[-1].encode(), default_backend())
                cert_val = cert.public_bytes(serialization.Encoding.DER)
                d += cert_val
        # TODO: Pending Roots
        return d


class BaselineShell:
    def __init__(self):
        self.dictBytes = self.build_dict()
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            temp_file.write(self.dictBytes)
        self.dictFile = temp_file.name

    def name(self):
        return "Method 1: Baseline via Shell"

    def compress(self, certList):
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            temp_file.write(b"".join(certList))
            name = temp_file.name
        command =  [
            "zstd",
            "-f",
            "-9",
            "-q",
            "--single-thread",
            "--zstd=searchLog=30",
            "--zstd=hashLog=30",
            "--zstd=chainLog=30",
            "--zstd=targetLength=6000",
            "--patch-from",
            self.dictFile,
            "-c",
            name
        ]
        completed_process = subprocess.run(command, capture_output=True,shell=False)
        return completed_process.stdout

    def decompress(self, compressed_data):
        # TODO Not Implemented
        pass

    def build_dict(self):
        d = b""
        with open('data/AllMozillaRoots.csv') as roots:
            table = csv.reader(roots)
            first = True
            for r in table:
                if first:
                    first = False
                    continue
                cert = x509.load_pem_x509_certificate(r[-1].encode(), default_backend())
                cert_val = cert.public_bytes(serialization.Encoding.DER)
                d += cert_val
        with open('data/AllMozillaIntermediates.csv') as intermediates:
            #TODO Fix Lazy Copy Paste
            table = csv.reader(intermediates)
            first = True
            for r in table:
                if first:
                    first = False
                    continue
                cert = x509.load_pem_x509_certificate(r[-1].encode(), default_backend())
                cert_val = cert.public_bytes(serialization.Encoding.DER)
                d += cert_val
        # TODO: Pending Roots
        return d