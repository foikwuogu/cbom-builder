"""Parse an X.509 (PEM) certificate into a crosswalk-matchable inventory row.

This is CBOM Builder's first real component parser (see docs/BUILD_SPEC.md): instead of
a user hand-typing a certificate's algorithm into an inventory file, they can point the
tool at the certificate itself. The output is the same shape as a hand-written inventory
row, so it flows straight into cbom_builder.scanner.scan_inventory.
"""

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, ed448, ed25519, rsa


def _describe_public_key(public_key):
    """Return (component, classical_algorithm, key_bits) for a cryptography public key."""
    if isinstance(public_key, rsa.RSAPublicKey):
        bits = public_key.key_size
        return "RSA public key", f"RSA-{bits}", str(bits)
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        curve = public_key.curve.name
        bits = public_key.curve.key_size
        return "EC public key (ECDSA/ECDH)", f"ECDSA/ECDH ({curve})", str(bits)
    if isinstance(public_key, (ed25519.Ed25519PublicKey, ed448.Ed448PublicKey)):
        name = "Ed25519" if isinstance(public_key, ed25519.Ed25519PublicKey) else "Ed448"
        bits = "255" if name == "Ed25519" else "448"
        return "EdDSA public key (Ed25519/Ed448)", name, bits
    return "Unrecognized public key type", type(public_key).__name__, ""


def parse_certificate(pem_data, asset_id=None):
    """Parse PEM certificate bytes/str into an inventory row dict.

    Args:
        pem_data: the certificate in PEM format, as bytes or str.
        asset_id: optional label to carry through the report (e.g. a hostname or asset
            tag); defaults to the certificate's subject common name if present.
    """
    if isinstance(pem_data, str):
        pem_data = pem_data.encode("utf-8")

    cert = x509.load_pem_x509_certificate(pem_data)
    public_key = cert.public_key()
    component, classical_algorithm, key_bits = _describe_public_key(public_key)

    try:
        cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        subject_cn = cn[0].value if cn else None
    except Exception:
        subject_cn = None

    return {
        "asset_id": asset_id or subject_cn or "unlabeled-certificate",
        "protocol": "X.509 certificate (generic / protocol-agnostic)",
        "component": component,
        "classical_algorithm_observed": classical_algorithm,
        "key_bits_observed": key_bits,
        "signature_algorithm_observed": cert.signature_algorithm_oid._name,
        "issuer": cert.issuer.rfc4514_string(),
        "not_valid_after": cert.not_valid_after_utc.date().isoformat(),
    }


def parse_certificate_file(path, asset_id=None):
    """Read a PEM certificate file and parse it. See parse_certificate()."""
    with open(path, "rb") as f:
        return parse_certificate(f.read(), asset_id=asset_id)
