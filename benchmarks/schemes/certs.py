# Open a cert
# Build a copy
# Compare
import base64
import datetime
import json
import logging
from collections import Counter
from functools import lru_cache
import csv

import zstandard as zstd
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.x509 import oid
from cryptography.x509.extensions import ExtensionNotFound
from cryptography.hazmat.backends import default_backend

from tqdm import tqdm

MISSING_CA_CERTS = set()


def extract_chosen_name(rfc4514_string):
    parsed = [x.strip("CN=") for x in rfc4514_string.split(",") if "CN=" in x]
    if len(parsed) >= 1:
        return parsed[0]
    else:
        return rfc4514_string[0:20]


def report_missing_ca_cert(parsed_cert):
    fingerprint = parsed_cert.fingerprint(hashes.SHA256()).hex()
    if fingerprint not in MISSING_CA_CERTS:
        logging.debug(
            f"Missing CA Certificate {extract_chosen_name(parsed_cert.subject.rfc4514_string())}"
            f" issued by {extract_chosen_name(parsed_cert.issuer.rfc4514_string())}"
            f" with sha256-fingerprint={fingerprint[:6]}"
        )
        logging.debug(f"{parsed_cert.public_bytes(serialization.Encoding.PEM)}")
        MISSING_CA_CERTS.add(fingerprint)


def parse_der_to_cert(der_bytes):
    return x509.load_der_x509_certificate(der_bytes)


def is_ca_cert(parsed_cert):
    try:
        if parsed_cert.extensions.get_extension_for_oid(
            oid.ExtensionOID.BASIC_CONSTRAINTS
        ).value.ca:
            return True
    except ExtensionNotFound:
        pass
    return False


@lru_cache
def load_cert_chains():
    logging.info("Decompressing and parsing certificate chains")
    with open("data/chains.json.zst", "rb") as zst_file:
        j = zstd.ZstdDecompressor().decompress(zst_file.read())
        data = json.loads(j)
        logging.info(f"Loaded {len(data)} certificate chains")
    return data


@lru_cache
def load_ee_certs_from_chains(redact):
    #TODO: Assumes the first cert is an end-entity cert.
    end_entity_der = [base64.b64decode(x[0]) for x in load_cert_chains()]
    if redact:
        end_entity_der = [
            cert_redactor(x)
            for x in tqdm(end_entity_der, desc="Redacting end-entity certificates")
        ]
    return end_entity_der

@lru_cache
def load_ca_certs_from_chains():
    ca_certs = set()
    for chain in tqdm(load_cert_chains(),desc="Extracting CA Certificates from Chains"):
        for cert in chain:
            cert_bytes = base64.b64decode(cert)
            if is_ca_cert(parse_der_to_cert(cert_bytes)):
                ca_certs.add(cert_bytes)
    logging.info(f"Extracted {len(ca_certs)} CA Certs from certificate chains")
    return list(ca_certs)

def extract_der_column(path, column, keep=lambda x: True):
    with open(path) as output_file:
        table = csv.reader(output_file)
        _ = next(table)
        return [
            x509.load_pem_x509_certificate(
                x[column].encode(), default_backend()
            ).public_bytes(serialization.Encoding.DER)
            for x in table
            if keep(x)
        ]


# TODO: Collect more CA Certificates for use in compression
#      * Microsoft Intermediates
#      * Mozilla + Microsoft Pending
#      * Apple and Google (all
#
# TODO: Remove Microsoft Roots that are not TLS-enabled


@lru_cache
def get_all_mozilla_certs():
    roots = extract_der_column("data/AllMozillaRoots.csv", -1)
    intermediates = extract_der_column("data/AllMozillaIntermediates.csv", -1)
    return roots + intermediates


@lru_cache
def get_all_microsoft_certs():
    roots = extract_der_column("data/AllMicrosoftRoots.csv", -1)
    return roots


@lru_cache
def get_all_ccadb_certs():
    certs = get_all_microsoft_certs() + get_all_mozilla_certs()
    logging.info(f"Loaded {len(certs)} certs from the CCADB lists.")
    return certs


class CommonCertStrings:
    def __init__(self, threshold):
        self.counter = Counter()
        self.threshold = threshold

    def ingest_all(self, cert_list):
        for der_bytes in cert_list:
            self.ingest(der_bytes)

    def ingest(self, der_bytes):
        cert = parse_der_to_cert(der_bytes)
        self.counter.update([cert.issuer.public_bytes(serialization.Encoding.DER)])
        try:
            self.counter.update(
                [
                    cert.extensions.get_extension_for_oid(
                        oid.OCSPExtensionOID
                    ).public_bytes(serialization.Encoding.DER)
                ]
            )
        except ExtensionNotFound:
            pass
        extensions = [
            x509.BasicConstraints,
            x509.AuthorityKeyIdentifier,
            x509.AuthorityInformationAccess,
            x509.KeyUsage,
            x509.ExtendedKeyUsage,
            x509.NameConstraints,
            x509.FreshestCRL,
            x509.CRLDistributionPoints,
            x509.PolicyConstraints,
            x509.CertificatePolicies,
        ]
        for x in extensions:
            try:
                self.counter.update(
                    [cert.extensions.get_extension_for_class(x).value.public_bytes()]
                )
            except ExtensionNotFound:
                continue
        sct_list = cert.extensions.get_extension_for_class(
            x509.PrecertificateSignedCertificateTimestamps
        ).value
        for sct in sct_list:
            self.counter.update([sct.log_id])

    def top(self):
        out = b""
        for bits, count in self.counter.items():
            if count < self.threshold:
                continue
            out += bits
        return out


def cert_redactor(der_encoding):
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    one_day = datetime.timedelta(1, 0, 0)
    name = x509.Name(
        [
            x509.NameAttribute(oid.NameOID.COMMON_NAME, "a"),
        ]
    )

    # Setup the cert with fixed bytes for the end-entity specific fields
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.not_valid_before(datetime.datetime.today() - one_day)
    builder = builder.not_valid_after(datetime.datetime.today() + (one_day * 30))
    builder = builder.serial_number(1)
    builder = builder.public_key(public_key)

    # Copy the issuer and extensions from the passed cert
    # Skip subject specific extensions
    cert = parse_der_to_cert(der_encoding)
    builder = builder.issuer_name(cert.issuer)
    xtn_denylist = [
        oid.ExtensionOID.SUBJECT_KEY_IDENTIFIER,
        oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME,
    ]
    for xtn in cert.extensions:
        if xtn.oid in xtn_denylist:
            continue
        else:
            builder = builder.add_extension(xtn.value, critical=xtn.critical)

    new_cert = builder.sign(
        private_key=private_key,
        algorithm=None,
    )

    return new_cert.public_bytes(serialization.Encoding.DER)
