#!/usr/bin/env python3
"""Build the PQC readiness crosswalk (data/processed/pqc_crosswalk.csv + .json).

This crosswalk is compiled desk research, not a machine-fetched dataset: each row's
classical-algorithm characterization comes from the protocol/standard's own public
specification, and each PQC mapping comes from NIST FIPS 203/204/205, NIST SP 1800-38
(flagged as draft), NIST SP 800-208, and the NSA CNSA 2.0 Suite. Every row carries its
source spec, a URL, and the CNSA 2.0 use-case bucket with its published dates.

Run: python code/01_build_crosswalk.py
Writes: data/processed/pqc_crosswalk.csv, data/processed/pqc_crosswalk.json
"""

import csv
import json
import os

FIELDS = [
    "id", "protocol", "component", "layer", "classical_algorithm", "algorithm_type",
    "key_bits", "quantum_threat", "pqc_replacement", "cnsa2_category",
    "cnsa2_support_by", "cnsa2_exclusive_by", "source_spec", "source_url", "notes",
]

ROWS = [
    dict(id="OT-001", protocol="Modbus/TCP (base)", component="Application data channel",
         layer="transport", classical_algorithm="None (cleartext, unauthenticated)",
         algorithm_type="none", key_bits="", quantum_threat="no-crypto",
         pqc_replacement="N/A -- add a secure transport (see OT-002) before a PQC "
                          "algorithm choice is relevant",
         cnsa2_category="n/a", cnsa2_support_by="", cnsa2_exclusive_by="",
         source_spec="Modbus Application Protocol V1.1b3 (no native security)",
         source_url="https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf",
         notes="Baseline-hygiene finding, not a PQC-migration item: nothing to migrate "
               "until a secure transport exists."),

    dict(id="OT-002", protocol="Modbus/TCP Security (add-on) / TLS-wrapped OT protocols",
         component="TLS 1.2/1.3 handshake", layer="transport",
         classical_algorithm="ECDHE (P-256/P-384) or RSA-2048 key exchange; RSA-2048 or "
                              "ECDSA P-256 certificate signatures",
         algorithm_type="asymmetric-kex + asymmetric-sig", key_bits="2048 (RSA) / 256-384 (EC)",
         quantum_threat="broken-by-shor",
         pqc_replacement="ML-KEM-768/1024 (FIPS 203) for key exchange, hybridized with "
                          "classical ECDHE during transition; ML-DSA-65/87 (FIPS 204) for "
                          "certificate signatures",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="Modbus/TCP Security v21 (TLS-based add-on)",
         source_url="https://modbus.org/docs/MB-TCP-Security-v21_2018-07-24.pdf",
         notes="Also covers any OT protocol tunneled over TLS (MQTT-over-TLS, IEC "
               "60870-5-104 Secure, HTTPS management interfaces)."),

    dict(id="OT-003", protocol="DNP3 Secure Authentication v5 (SAv5)",
         component="Message authentication", layer="application",
         classical_algorithm="HMAC-SHA-256 (or HMAC-SHA3-256); AES-128/256 Key Wrap for "
                              "Update Key protection",
         algorithm_type="symmetric-mac + symmetric-keywrap", key_bits="128/256",
         quantum_threat="weakened-by-grover",
         pqc_replacement="No asymmetric component to replace; move to HMAC-SHA-384/512 "
                          "and AES-256 Key Wrap for full Grover margin",
         cnsa2_category="Symmetric algorithms (general use)", cnsa2_support_by="",
         cnsa2_exclusive_by="",
         source_spec="IEEE 1815-2012 (DNP3 Secure Authentication v5)",
         source_url="https://www.dnp.org",
         notes="SAv5 is symmetric-key only (pre-shared Update Keys); the practical weak "
               "point is out-of-band key distribution, not the algorithms."),

    dict(id="OT-004", protocol="DNP3 SAv6 / Asymmetric Management Protocol (AMP)",
         component="Authority Key (root key management)", layer="application",
         classical_algorithm="RSA or ECC (implementation-defined curve/size, typically "
                              "RSA-2048 or P-256)",
         algorithm_type="asymmetric-sig", key_bits="implementation-defined",
         quantum_threat="broken-by-shor",
         pqc_replacement="ML-DSA-65/87 (FIPS 204)",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="IEEE 1815-2020 (DNP3 SAv6 / AMP)", source_url="https://www.dnp.org",
         notes="Session Key and Update Key remain AES-256-GCM / AES-256 Key Wrap; see "
               "OT-005."),

    dict(id="OT-005", protocol="DNP3 SAv6 / AMP", component="Session Key encryption",
         layer="application", classical_algorithm="AES-256-GCM",
         algorithm_type="symmetric-aead", key_bits="256", quantum_threat="weakened-by-grover",
         pqc_replacement="No change needed -- AES-256 already meets NIST's post-quantum "
                          "symmetric-strength guidance",
         cnsa2_category="Symmetric algorithms (general use)", cnsa2_support_by="",
         cnsa2_exclusive_by="",
         source_spec="IEEE 1815-2020 (DNP3 SAv6 / AMP)", source_url="https://www.dnp.org",
         notes=""),

    dict(id="OT-006", protocol="OPC UA", component="SecurityPolicy Basic256Sha256 "
                                                     "(handshake + certificates)",
         layer="transport+identity",
         classical_algorithm="RSA-2048 asymmetric encryption/signature (certificates and "
                              "key exchange); AES-256-CBC symmetric; SHA-256 hash",
         algorithm_type="asymmetric-kex + asymmetric-sig", key_bits="2048",
         quantum_threat="broken-by-shor",
         pqc_replacement="ML-KEM-768/1024 for session-key establishment (likely hybrid) + "
                          "ML-DSA-65/87 for certificate signatures",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="OPC 10000-7: UA Part 7 -- Profiles, SecurityPolicy Basic256Sha256",
         source_url="https://reference.opcfoundation.org/Core/Part7/",
         notes="OPC Foundation is developing hybrid-certificate guidance; treat as "
               "transitional until finalized."),

    dict(id="OT-007", protocol="OPC UA",
         component="SecurityPolicy Aes256Sha256RsaPss", layer="transport+identity",
         classical_algorithm="RSA-PSS-2048 signatures; AES-256; SHA-256",
         algorithm_type="asymmetric-sig", key_bits="2048", quantum_threat="broken-by-shor",
         pqc_replacement="ML-DSA-65/87 (FIPS 204)",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="OPC 10000-7: UA Part 7 -- Profiles",
         source_url="https://reference.opcfoundation.org/Core/Part7/", notes=""),

    dict(id="OT-008", protocol="IEC 62351-3 (TLS profile for power-system protocols: "
                                "IEC 60870-5-104 Secure, DNP3-over-TLS)",
         component="TLS 1.2/1.3 session", layer="transport",
         classical_algorithm="ECDHE (P-256/P-384) key exchange; RSA or ECDSA certificate "
                              "signatures; AES-GCM",
         algorithm_type="asymmetric-kex + asymmetric-sig",
         key_bits="256-384 (EC) / 2048 (RSA)", quantum_threat="broken-by-shor",
         pqc_replacement="ML-KEM-768/1024 hybrid key exchange; ML-DSA certificate "
                          "signatures",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="IEC 62351-3:2023, Ed. 2",
         source_url="https://webstore.iec.ch/en/publication/68410",
         notes="Grid-facing protocols; migration here intersects directly with federal "
               "PQC mandates for energy-sector OT."),

    dict(id="OT-009", protocol="IEEE 802.1AR Secure Device Identity "
                                "(DevID / IDevID / LDevID)",
         component="Device identity certificate", layer="identity",
         classical_algorithm="RSA-2048 or ECDSA P-256 signatures",
         algorithm_type="asymmetric-sig", key_bits="2048/256",
         quantum_threat="broken-by-shor",
         pqc_replacement="ML-DSA-65/87 (FIPS 204); consider LMS/XMSS (SP 800-208) where "
                          "device-identity issuance resembles firmware-signing "
                          "infrastructure",
         cnsa2_category="Software & firmware signing", cnsa2_support_by="2025",
         cnsa2_exclusive_by="2030",
         source_spec="IEEE 802.1AR-2018",
         source_url="https://standards.ieee.org/ieee/802.1AR/6995/",
         notes="Device identity underpins zero-trust segmentation in OT; a broken IDevID "
               "key compromises every downstream trust decision."),

    dict(id="OT-010", protocol="OT firmware/software update signing "
                                "(PLC, RTU, IED firmware images)",
         component="Firmware signature", layer="firmware",
         classical_algorithm="RSA-2048 or ECDSA P-256 signatures",
         algorithm_type="asymmetric-sig", key_bits="2048/256",
         quantum_threat="broken-by-shor",
         pqc_replacement="LMS or XMSS (NIST SP 800-208, stateful hash-based) or SLH-DSA "
                          "(FIPS 205, stateless), per CNSA 2.0 signing guidance",
         cnsa2_category="Software & firmware signing", cnsa2_support_by="2025",
         cnsa2_exclusive_by="2030",
         source_spec="NIST SP 800-208; NSA CNSA 2.0 FAQ",
         source_url="https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSI_CNSA_2.0_FAQ_.PDF",
         notes="Earliest CNSA 2.0 deadline category -- prioritize firmware-signing "
               "infrastructure first."),

    dict(id="OT-011", protocol="MQTT (IIoT/OT gateway telemetry) over TLS",
         component="TLS 1.2/1.3 session", layer="transport",
         classical_algorithm="ECDHE/RSA key exchange; RSA or ECDSA certificates; AES-GCM",
         algorithm_type="asymmetric-kex + asymmetric-sig",
         key_bits="2048 / 256-384", quantum_threat="broken-by-shor",
         pqc_replacement="ML-KEM hybrid key exchange; ML-DSA certificates",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="MQTT Version 5.0 (OASIS); TLS 1.3 (RFC 8446)",
         source_url="https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html", notes=""),

    dict(id="OT-012", protocol="SNMPv3 (device/network management)",
         component="USM authPriv (auth + privacy)", layer="management",
         classical_algorithm="HMAC-SHA (auth); AES-CFB-128 (privacy)",
         algorithm_type="symmetric-mac + symmetric-cipher", key_bits="128-256",
         quantum_threat="weakened-by-grover",
         pqc_replacement="No asymmetric component; move from AES-128 to AES-256-CFB/GCM "
                          "where supported",
         cnsa2_category="Symmetric algorithms (general use)", cnsa2_support_by="",
         cnsa2_exclusive_by="",
         source_spec="RFC 3414 (USM for SNMPv3)",
         source_url="https://www.rfc-editor.org/rfc/rfc3414", notes=""),

    dict(id="OT-013", protocol="Legacy cleartext management (Telnet, unencrypted HTTP, FTP)",
         component="Management-plane transport", layer="transport",
         classical_algorithm="None", algorithm_type="none", key_bits="",
         quantum_threat="no-crypto",
         pqc_replacement="N/A -- remediate by adding TLS (see OT-002/OT-008) before this "
                          "is a PQC question",
         cnsa2_category="n/a", cnsa2_support_by="", cnsa2_exclusive_by="",
         source_spec="n/a -- protocols predate TLS adoption", source_url="",
         notes="Flagged as a baseline-hygiene finding, distinct from PQC-migration "
               "findings."),

    dict(id="OT-014", protocol="X.509 certificate (generic / protocol-agnostic)",
         component="RSA public key", layer="identity",
         classical_algorithm="RSA (variable key size)",
         algorithm_type="asymmetric-sig + asymmetric-kex", key_bits="variable "
         "(commonly 1024/2048/3072/4096)", quantum_threat="broken-by-shor",
         pqc_replacement="ML-DSA-65/87 (FIPS 204) for signatures; ML-KEM-768/1024 "
                          "(FIPS 203) where the certificate is used for key transport",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="RFC 5280 (Internet X.509 Public Key Infrastructure Certificate)",
         source_url="https://www.rfc-editor.org/rfc/rfc5280",
         notes="Fallback bucket for a parsed certificate not tied to one of the named "
               "OT protocols above (e.g. OT-006, OT-009); re-file under the specific "
               "protocol row when the certificate's actual use is known."),

    dict(id="OT-015", protocol="X.509 certificate (generic / protocol-agnostic)",
         component="EC public key (ECDSA/ECDH)", layer="identity",
         classical_algorithm="ECDSA/ECDH (variable curve: P-256/P-384/P-521)",
         algorithm_type="asymmetric-sig + asymmetric-kex",
         key_bits="variable (256/384/521)", quantum_threat="broken-by-shor",
         pqc_replacement="ML-DSA-65/87 (FIPS 204) for signatures; ML-KEM-768/1024 "
                          "(FIPS 203) where the certificate is used for key exchange",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="RFC 5280; SEC 1 (Elliptic Curve Cryptography)",
         source_url="https://www.rfc-editor.org/rfc/rfc5280",
         notes="Same fallback role as OT-014, for EC-keyed certificates."),

    dict(id="OT-016", protocol="X.509 certificate (generic / protocol-agnostic)",
         component="EdDSA public key (Ed25519/Ed448)", layer="identity",
         classical_algorithm="EdDSA (Ed25519 or Ed448)",
         algorithm_type="asymmetric-sig", key_bits="255/448",
         quantum_threat="broken-by-shor",
         pqc_replacement="ML-DSA-65/87 (FIPS 204)",
         cnsa2_category="Traditional networking equipment", cnsa2_support_by="2026",
         cnsa2_exclusive_by="2030",
         source_spec="RFC 8032 (EdDSA); RFC 5280",
         source_url="https://www.rfc-editor.org/rfc/rfc8032",
         notes="Less common in legacy OT, increasingly seen in newer IIoT gateways."),
]


def main():
    repo_root = os.path.join(os.path.dirname(__file__), "..")
    out_dir = os.path.join(repo_root, "data", "processed")
    pkg_data_dir = os.path.join(repo_root, "src", "cbom_builder", "data")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(pkg_data_dir, exist_ok=True)

    csv_path = os.path.join(out_dir, "pqc_crosswalk.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for row in ROWS:
            w.writerow(row)

    json_path = os.path.join(out_dir, "pqc_crosswalk.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ROWS, f, indent=2)

    # The package ships its own copy so it works standalone once installed (pip/PyPI);
    # this script is the single source of truth for both copies -- never hand-edit the
    # JSON in src/cbom_builder/data/ directly.
    pkg_json_path = os.path.join(pkg_data_dir, "pqc_crosswalk.json")
    with open(pkg_json_path, "w", encoding="utf-8") as f:
        json.dump(ROWS, f, indent=2)

    print(f"wrote {len(ROWS)} rows to {csv_path}, {json_path}, and {pkg_json_path}")


if __name__ == "__main__":
    main()
