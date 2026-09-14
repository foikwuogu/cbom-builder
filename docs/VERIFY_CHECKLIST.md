# Verification checklist (author completes before any release)

Initial and date each line in your own copy. `scripts/publish_gate.py` checks the
mechanical items (draft stamps, placeholders, secrets); these are yours.

## Reproduce
- [ ] `python code/01_build_crosswalk.py` re-run; `data/processed/pqc_crosswalk.csv`
      and `.json`, and `src/cbom_builder/data/pqc_crosswalk.json`, are identical to
      the committed versions
- [ ] `python code/02_build_web.py` re-run; `web/index.html` is identical to the
      committed version
- [ ] `python -m unittest discover -s tests -v` passes (18/18 as of this writing)
- [ ] `pip install -e .` then `cbom-builder scan tests/fixtures/sample_inventory.csv`
      reproduces the counts in `data/processed/qa_report.txt`

## Source-level checks (the sixteen crosswalk rows)
- [ ] Each row's `classical_algorithm` checked against its cited `source_spec` /
      `source_url` (data/raw/PROVENANCE.txt has the full list)
- [ ] NIST FIPS 203/204/205 confirmed still final (not superseded) at release time
- [ ] NIST SP 1800-38 checked for a newer status than "Preliminary Draft" — update
      every row and doc that flags it as draft if it has been finalized
- [ ] NSA CNSA 2.0 dates (2025/2026/2030/2033) re-checked against the current CNSA 2.0
      FAQ/press guidance for any published revision

## Row-level spot checks (minimum 15, five per bucket below)
- [ ] Five rows you can verify from memory/experience against the source spec
      (OT-001–OT-005 are a reasonable starting set)
- [ ] Five rows checked against the OT/ICS protocol specs you know best professionally
- [ ] Five rows checked cold, as if you had never seen this project (record which five)

## Judgment calls to own
- [ ] The eight protocol families chosen for v0.1 are the right starting set for this
      project's audience (energy-sector OT operators) — or note which to swap in/out
- [ ] The three generic X.509 fallback rows (OT-014/015/016) correctly represent
      "no better match" rather than replacing a more specific row that should exist
- [ ] Matching by punctuation-insensitive substring (rather than exact-string or
      fuzzy/ML matching) is the right trade-off for v0.1 — LIMITATIONS.md #3 explains
      the choice
- [ ] The web tool's "runs entirely in your browser" claim is still true (no fetch/
      network calls were added to web/index_template.html)

## Before it goes public
- [ ] README, LIMITATIONS, and this checklist read in your own voice; nothing you
      cannot defend remains
- [ ] AUTHORS.json spelling/ORCID/affiliation matches exactly what you want to appear
      in citations
- [x] `python scripts/publish_gate.py .` passes (no leftover draft-status banners, no
      VERIFY-tag or ASK-tag markers, no placeholder brackets remain — AUTHORS.json resolved;
      CITATION.cff repository-code/doi and pyproject.toml author fields resolved as
      publishing proceeds) — confirmed 2026-09-14
- [x] Author verification confirmed in conversation on 2026-09-14
- [ ] License files, name, ORCID, contact in place
- [ ] Evidence log row written the day of release (see the `niw-profile-build`
      evidence log format, if you keep one)
