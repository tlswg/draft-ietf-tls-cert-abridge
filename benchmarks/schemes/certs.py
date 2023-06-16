# Open a cert
# Build a copy
# Compare
import json
from cryptography import x509
from cryptography.x509 import oid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.x509.extensions import ExtensionNotFound
import base64
from cryptography.hazmat.primitives import hashes
import datetime
from collections import Counter

# Cribbed from https://cryptography.io/en/latest/x509/reference/#cryptography.x509.Extensions


class CommonByte:
    def __init__(self, threshold):
        self.bytes = Counter()
        self.threshold = threshold

    def ingest(self, bytes):
        get_bytes = lambda x: x.public_bytes(serialization.Encoding.DER)
        cert = x509.load_der_x509_certificate(bytes)
        self.bytes.update([get_bytes(cert.issuer)])
        # self.bytes.update(cert.signature_algorithm_oid.dotted_string.encode()) #TODO fix
        # self.bytes.update(get_bytes(cert.signature_hash_algorithm.))
        # self.bytes.update(get_bytes(cert.version))
        try:
            self.bytes.update(
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
                self.bytes.update(
                    [cert.extensions.get_extension_for_class(x).value.public_bytes()]
                )
            except ExtensionNotFound:
                continue
        scts = cert.extensions.get_extension_for_class(
            x509.PrecertificateSignedCertificateTimestamps
        ).value
        for s in scts:
            self.bytes.update([s.log_id])

    def common(self):
        out = b""
        for bits, count in self.bytes.items():
            if count < self.threshold:
                continue
            out += bits
        return out


def cert_redactor(der_encoding):
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    builder = x509.CertificateBuilder()
    one_day = datetime.timedelta(1, 0, 0)
    cert = x509.load_der_x509_certificate(der_encoding)
    builder = builder.subject_name(
        x509.Name(
            [
                x509.NameAttribute(oid.NameOID.COMMON_NAME, "a"),
            ]
        )
    )
    builder = builder.issuer_name(cert.issuer)
    builder = builder.not_valid_before(datetime.datetime.today() - one_day)
    builder = builder.not_valid_after(datetime.datetime.today() + (one_day * 30))
    builder = builder.serial_number(1)
    builder = builder.public_key(cert.public_key())

    for xtn in cert.extensions:
        if xtn.oid in [
            oid.ExtensionOID.SUBJECT_KEY_IDENTIFIER,
            oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME,
        ]:
            continue
        builder = builder.add_extension(xtn.value, critical=xtn.critical)
    new_cert = builder.sign(
        private_key=private_key,
        algorithm=None,
    )
    return new_cert.public_bytes(serialization.Encoding.DER)


if __name__ == "__main__":
    import util

    data = util.load_certificates()
    ingester = CommonByte(len(data) / 1000)

    for chain in data:
        cert = base64.b64decode(chain[0])
        res = cert_redactor(cert)
        ingester.ingest(cert)

    print(len(ingester.common()))
