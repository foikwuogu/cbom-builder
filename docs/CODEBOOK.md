# Codebook — `data/processed/pqc_crosswalk.csv`

One row is one cryptographic/identity profile for a component of an OT protocol or
standard. See `data/raw/PROVENANCE.txt` for the full source list.

| Column | Definition | Source / how it was determined |
|---|---|---|
| `id` | Stable identifier (`OT-001`...`OT-016`). Referenced directly from an inventory row's `crosswalk_id` for an unambiguous match. | Assigned in build order; never reused if a row is removed. |
| `protocol` | The OT protocol or standard this row characterizes. | The standard's own name/number. |
| `component` | The specific mechanism within that protocol this row is about (a handshake, a key type, a signature). | Narrows matching when one protocol has multiple rows (e.g. OPC UA). |
| `layer` | One of `transport`, `application`, `identity`, `firmware`, `management`. | Assigned by where the cryptography operates in the stack. |
| `classical_algorithm` | The algorithm(s) currently specified/observed for this component, as documented in the source spec. | Read from the cited `source_spec`/`source_url`. |
| `algorithm_type` | `asymmetric-kex`, `asymmetric-sig`, `symmetric-*`, or `none`. | Classified from `classical_algorithm`. |
| `key_bits` | Key size(s) in bits, where meaningful. | From the source spec; `variable` where the spec allows several sizes. |
| `quantum_threat` | Controlled vocabulary: `broken-by-shor` (asymmetric algorithm a cryptographically relevant quantum computer breaks via Shor's algorithm), `weakened-by-grover` (symmetric algorithm whose effective security is halved by Grover's algorithm, not broken), `no-crypto` (no cryptography is in use to threaten), `not-vulnerable` (reserved for a future row where nothing needs to change). | Standard textbook classification of the `classical_algorithm`. |
| `pqc_replacement` | The NIST-standardized (or CNSA 2.0-recommended) algorithm to migrate to. | FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), SP 800-208 (LMS/XMSS). |
| `cnsa2_category` | Which NSA CNSA 2.0 use-case bucket this component falls under. | NSA CNSA 2.0 FAQ, Sept. 2022. |
| `cnsa2_support_by` / `cnsa2_exclusive_by` | The published "support and prefer by" / "exclusive use by" years for that bucket. | Same source. |
| `source_spec` / `source_url` | The specific public specification this row's `classical_algorithm` characterization is drawn from. | — |
| `notes` | Caveats, scope notes, or cross-references to other rows. | — |

## Inventory file format (user input to the tool)

A CSV or JSON file, one row/object per component the user has observed in their
environment:

| Field | Required | Meaning |
|---|---|---|
| `protocol` | yes | Matched against `crosswalk.protocol` (punctuation-insensitive substring match). |
| `component` | no | Narrows the match when `protocol` alone matches more than one crosswalk row. |
| `crosswalk_id` | no | If given, matches that crosswalk row directly and skips text matching entirely — the recommended field once a user knows which row applies. |
| `asset_id` | no | Any label for the asset; carried through to the report unchanged. |
| any other column | no | Passed through into the report untouched (e.g. `location`, `classical_algorithm_observed` from the certificate parser). |

## Report fields (`cbom_builder.report.build_report`)

`quantum_threat_counts`, `unmatched_components`, `ambiguous_components`, and one `items`
entry per inventory row carrying `match_status`, the matched `crosswalk_id`, and the
crosswalk's `pqc_replacement` / `cnsa2_*` fields for that row.
