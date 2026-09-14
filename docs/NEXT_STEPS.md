# Next steps (what v0.2+ adds)

This is a first release. What it deliberately does not do yet:

1. **More parsers**, so users type less by hand:
   - TLS handshake capture (pcap) → extract negotiated cipher suite and certificate
     chain automatically.
   - OT config-file parsers for specific platforms (e.g. an OPC UA server's
     `SecurityPolicy` config, a DNP3 master's Update Key configuration file).
   - Live, read-only protocol probing (connect and read the security handshake without
     touching process control) — needs careful safety review before it touches a real
     OT network.

2. **Broaden the crosswalk**: BACnet/SC, PROFINET Security, EtherNet/IP CIP Security,
   IEC 61850 (GOOSE/MMS via IEC 62351-6), proprietary vendor protocols on request.

3. **Track SP 1800-38 to final.** Re-check its migration guidance once NIST finalizes
   the publication, and update every crosswalk row and doc reference that currently
   says "draft."

4. **A hosted (not just static-client) web version** that can accept larger uploads,
   persist a user's inventory across sessions, and export a signed PDF/CSV report —
   if there's demand once the static tool is in use.

5. **A "mandate mapping" layer**: a second crosswalk from CNSA 2.0/NIST categories to
   specific named federal PQC mandates and their compliance deadlines, so a finding
   points at the actual regulatory citation, not just the NIST timeline.

6. **CI**: a GitHub Actions workflow running the test suite and `publish_gate.py` on
   every push (not yet added in v0.1 — add `.github/workflows/tests.yml` running
   `python -m unittest discover -s tests`).
