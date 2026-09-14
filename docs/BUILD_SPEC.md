# Build spec — CBOM Builder

```
PROJECT:        CBOM Builder (Pipeline/Tool, stacked with a small reference dataset)
QUESTION:       Given an OT system's protocol and identity/cryptographic components, which
                are quantum-vulnerable, and what does NIST/CNSA 2.0 guidance say to migrate
                them to?
SOURCES:
  - NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA) — final, issued 2024-08-13
    https://www.federalregister.gov/documents/2024/08/14/2024-17956/
  - NIST SP 1800-38A/B/C, Migration to Post-Quantum Cryptography (NCCoE) — Preliminary Draft,
    2023-04-24 (not yet finalized; flagged as draft guidance throughout)
    https://www.nccoe.nist.gov/publications/practice-guide/migration-post-quantum-cryptography-nist-sp-1800-38-practice-guide
  - NSA CNSA 2.0 Suite and transition timeline — CSI, 2022-09 (algorithm/use-case table,
    2025/2030/2033 deadlines) https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSI_CNSA_2.0_FAQ_.PDF
  - NIST SP 800-208 (LMS/XMSS stateful hash-based signatures for firmware signing)
  - Public protocol/security specifications used to characterize each OT component's current
    cryptography: OPC Foundation Part 7 (SecurityPolicies), DNP3/IEEE 1815 Secure
    Authentication v5 and v6, IEC 62351-3 (TLS profile for power-system protocols),
    IEEE 802.1AR (Secure Device Identity)
UNIT:           one protocol/component cryptographic profile (e.g., "OPC UA —
                Basic256Sha256", "DNP3 SAv6 — Authority Key")
MEASURES:
  - classical_algorithm      the algorithm(s) currently in use, as documented in the spec
  - quantum_threat           broken-by-shor | weakened-by-grover | not-vulnerable | no-crypto
  - pqc_replacement          the NIST-standardized or CNSA 2.0 algorithm to migrate to
  - cnsa2_category / dates   which CNSA 2.0 use-case bucket it falls in, and that bucket's
                             support-by / exclusive-by dates
OUTPUTS:
  - data/processed/pqc_crosswalk.csv (+ .json)     the reference crosswalk
  - src/cbom_builder/ (installable package + CLI)  scans a user's component inventory
    against the crosswalk and emits a CBOM report (JSON + CSV + text summary)
  - src/cbom_builder/parsers/x509_parser.py        first real parser: reads a PEM
    certificate and extracts its public-key algorithm/size for lookup
  - web/index.html                                  static, client-side CBOM report builder
    (upload/paste inventory, get the same report + a vulnerability breakdown chart), hostable
    on GitHub Pages
  - docs/ (README, CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST, NEXT_STEPS)
VENUES:         GitHub (public repo, tagged release) + Zenodo (DOI on first release)
VERIFY POINTS:
  - the crosswalk's protocol → algorithm characterizations, and the NIST/CNSA 2.0
    mappings and dates, against the primary sources
  - that SP 1800-38 is correctly flagged as draft (not final) guidance everywhere it's cited
  - the CBOM report's output on the worked examples in tests/fixtures/
LICENSE:        code MIT; crosswalk dataset and docs CC BY 4.0
ASSUMPTIONS:
  - Protocol coverage is representative, not exhaustive (Modbus/TCP+Security, DNP3 SAv5/SAv6,
    OPC UA, IEC 62351-3, MQTT-over-TLS, IEEE 802.1AR device identity, OT firmware signing,
    SNMPv3) — the crosswalk is a structured, extensible table, not a closed list; adding a
    row does not require touching the code
  - v0.1 input is a structured inventory file (CSV/JSON) the user fills in by hand or exports
    from asset-management tooling; a certificate-file parser ships now, other parsers
    (TLS handshake capture, live protocol probing) are documented as NEXT_STEPS, not built
    this round
  - the web front-end is a static, client-side page (no server, no data leaves the browser),
    reusing the same crosswalk JSON as the Python package
```
