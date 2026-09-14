# CBOM Builder

**Status:** v0.1.0, author-verified, pending first release | **Maintainer:** Friday Ogochukwu Ikwuogu,
[ORCID 0009-0009-2222-1318](https://orcid.org/0009-0009-2222-1318) | **License:** code
[MIT](LICENSE), crosswalk/docs [CC BY 4.0](LICENSE)

CBOM Builder checks OT (operational technology) protocol and identity components
against a Post-Quantum Cryptography (PQC) readiness crosswalk and produces a structured
Cryptographic Bill of Materials (CBOM), so an operator can see which of their
components use quantum-vulnerable cryptography and what NIST/CNSA 2.0 guidance says to
migrate them to.

Three ways to use it:

- **Web tool** (`web/index.html`) — paste or upload a CSV inventory, get a report in
  your browser. Nothing leaves the browser; matching runs against the bundled
  crosswalk in JavaScript.
- **CLI / Python package** (`cbom-builder`) — for scripting, CI, or scanning many
  assets at once.
- **Certificate parser** — point it at a PEM certificate and it extracts the public-key
  algorithm/size for you, instead of typing it in by hand.

## What is here

```
code/                 numbered build scripts (run in order to regenerate everything)
  01_build_crosswalk.py    builds data/processed/pqc_crosswalk.{csv,json} and the
                            package's bundled copy, from cited public specifications
  02_build_web.py           injects the crosswalk + example inventory into web/index.html
src/cbom_builder/     the installable Python package (see below)
data/raw/             PROVENANCE.txt — every source consulted, with URLs and dates
data/processed/       pqc_crosswalk.csv / .json, qa_report.txt
docs/                 BUILD_SPEC, CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST, NEXT_STEPS
tests/                18 tests covering the crosswalk, scanner, parser, report, and CLI
web/                  index_template.html (source) -> index.html (built, self-contained)
```

## Run it

**Web tool** — open `web/index.html` in any browser (or serve `web/` via GitHub
Pages). Click "Load example inventory" to see it work, or paste your own CSV.

**CLI**:

```
pip install -e .
cbom-builder list-crosswalk
cbom-builder scan tests/fixtures/sample_inventory.csv --format text
cbom-builder scan my_inventory.csv --format json --output cbom_report.json
cbom-builder parse-cert device.pem
```

**Python**:

```python
from cbom_builder import load_crosswalk, scan_inventory, build_report

crosswalk = load_crosswalk()
inventory = [{"asset_id": "PLC-101", "protocol": "Modbus/TCP (base)"}]
report = build_report(scan_inventory(inventory, crosswalk))
```

**Regenerate the data/web files after editing the crosswalk**:

```
python code/01_build_crosswalk.py
python code/02_build_web.py
python -m unittest discover -s tests -v
```

A stranger should be able to run these from this README alone and reproduce
`data/processed/` and `web/index.html` exactly.

## Sources

| Source | Vintage | License | Status |
|---|---|---|---|
| [NIST FIPS 203/204/205](https://www.federalregister.gov/documents/2024/08/14/2024-17956/) (ML-KEM, ML-DSA, SLH-DSA) | 2024-08-13 | Public domain (US gov't) | Final |
| [NIST SP 1800-38](https://www.nccoe.nist.gov/publications/practice-guide/migration-post-quantum-cryptography-nist-sp-1800-38-practice-guide) (Migration to PQC) | 2023-04-24 | Public domain (US gov't) | **Preliminary Draft — not final** |
| [NSA CNSA 2.0 FAQ](https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSI_CNSA_2.0_FAQ_.PDF) | 2022-09-07 | Public domain (US gov't) | Current guidance |
| NIST SP 800-208 (LMS/XMSS) | — | Public domain (US gov't) | Final |
| Protocol specs (Modbus, DNP3/IEEE 1815, OPC UA Part 7, IEC 62351-3, IEEE 802.1AR, MQTT, RFC 5280/3414/8032) | various | Each standard's own terms | See `data/raw/PROVENANCE.txt` |

Full citations, access dates, and a known-gap note: `data/raw/PROVENANCE.txt`.

## Headline numbers (from `data/processed/qa_report.txt`, author-verified 2026-09-14)

The crosswalk has 16 entries across 8 protocol families plus 3 generic X.509 fallback
rows. Scanning the bundled example inventory (8 components) finds 4 components using
cryptography broken by Shor's algorithm, 1 weakened by Grover's algorithm, 2 with no
cryptography in use at all, and 1 unmatched (a made-up protocol name, included in the
example on purpose to show how unmatched components are reported rather than guessed
at).

## Limitations

See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) before using or citing anything here
— in particular, the crosswalk is a representative starting set (not exhaustive) and
NIST SP 1800-38 is still in draft.

## Citation

See [`CITATION.cff`](CITATION.cff). DOI: pending first release.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).
