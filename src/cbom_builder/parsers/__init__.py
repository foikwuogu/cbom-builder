"""Parsers that turn a real artifact (a certificate, a config file, ...) into an
inventory row cbom_builder.scanner can match against the crosswalk.

v0.1 ships one parser: x509_parser (PEM certificates). See docs/NEXT_STEPS.md for the
parsers planned next (TLS handshake capture, live protocol probing, OT config files).
"""

from .x509_parser import parse_certificate, parse_certificate_file

__all__ = ["parse_certificate", "parse_certificate_file"]
