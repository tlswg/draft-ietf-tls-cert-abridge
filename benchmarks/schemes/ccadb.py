import csv
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def extract_der_column(path, column):
        with open(path) as input:
            table = csv.reader(input)
            next(table)
            extract = lambda x : x509.load_pem_x509_certificate(x[column].encode(), default_backend()).public_bytes(serialization.Encoding.DER)
            return [extract(x) for x in table]

def ccadb_certs():
        roots = extract_der_column('data/AllMozillaRoots.csv',-1)
        intermediates = extract_der_column('data/AllMozillaIntermediates.csv',-1)
        pending = [] # TODO Pending
        return iter(roots + intermediates + pending)