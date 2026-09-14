# Limitations

1. **The crosswalk is representative, not exhaustive.** v0.1 ships 16 rows covering
   eight protocol families (Modbus, DNP3 SAv5/SAv6, OPC UA, IEC 62351-3, IEEE 802.1AR,
   OT firmware signing, MQTT, SNMPv3) plus three generic X.509 fallback rows. Real OT
   environments run many other protocols (BACnet, PROFINET, EtherNet/IP/CIP, IEC 61850
   GOOSE/MMS, proprietary vendor protocols) that are not yet represented. Adding a row
   is a data change (`code/01_build_crosswalk.py`), not a code change.

2. **NIST SP 1800-38 is still a Preliminary Draft** (published 2023-04-24, not
   finalized as of this writing). Guidance drawn from it may change before NIST
   finalizes the publication. Every reference to it in this project is flagged as
   draft; check for a newer revision before treating the crosswalk as settled guidance.

3. **Matching is text-based, not semantic.** The scanner/web tool match an inventory
   row's `protocol`/`component` text against the crosswalk by normalized substring
   containment. Two different phrasings of the same protocol that don't share enough
   text may not match, and will show as `unmatched` rather than silently guessed at.
   Use the `crosswalk_id` field for a guaranteed-correct match once you know which row
   applies (see CODEBOOK.md).

4. **The certificate parser reads only the public key algorithm/size**, not whether
   the certificate is actually in active use, how it's deployed, or whether a
   compensating control (e.g. a hardware security module, short-lived cert rotation)
   changes its real-world risk. A `broken-by-shor` finding is a "migrate this
   algorithm" flag, not a live-exploitation warning.

5. **CNSA 2.0 dates are use-case buckets, not per-product certifications.** The
   `cnsa2_support_by` / `cnsa2_exclusive_by` columns reflect the NSA's published
   timeline for the *category* a component falls into (e.g. "traditional networking
   equipment"), not a vendor-specific compliance date for any particular OT product.

6. **No live network scanning, TLS handshake capture, or OT config-file parsing yet**
   (see NEXT_STEPS.md). v0.1 requires a user-supplied inventory (CSV/JSON) or a
   certificate file; it does not reach into a running OT network.

7. **This tool identifies quantum-vulnerable cryptography; it does not by itself
   demonstrate regulatory compliance.** Mapping to "emerging federal PQC mandates"
   (per the project's stated goal) requires the operator to match these findings
   against whichever specific mandate applies to their sector and jurisdiction — that
   mapping is not automated here.

8. **The `not-vulnerable` quantum-threat category is currently unused** (no crosswalk
   row is classified that way in v0.1); it exists in the schema for future entries
   (e.g. a component already migrated to a PQC algorithm).
