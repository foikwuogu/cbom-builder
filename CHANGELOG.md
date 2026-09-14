# Changelog

## v0.1.0 — 2026-09-13 (unreleased draft)

- Initial crosswalk: 16 rows covering Modbus, DNP3 SAv5/SAv6, OPC UA, IEC 62351-3,
  IEEE 802.1AR, OT firmware signing, MQTT, SNMPv3, and generic X.509 certificates,
  against NIST FIPS 203/204/205, NIST SP 1800-38 (draft), NIST SP 800-208, and NSA
  CNSA 2.0.
- `cbom_builder` Python package: crosswalk loader, inventory scanner, CBOM report
  builder (JSON/CSV/text), and a CLI (`cbom-builder scan|parse-cert|list-crosswalk`).
- First real parser: X.509 (PEM) certificate parser.
- Static, client-side web tool (`web/index.html`) mirroring the same matching logic.
- Test suite (18 tests, `python -m unittest discover -s tests`).
