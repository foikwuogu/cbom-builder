import unittest

from cbom_builder.crosswalk import find_by_id, load_crosswalk


class TestCrosswalk(unittest.TestCase):
    def test_load_crosswalk_bundled(self):
        rows = load_crosswalk()
        self.assertEqual(len(rows), 16)
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)), "crosswalk ids must be unique")

    def test_every_row_has_required_fields(self):
        required = {"id", "protocol", "component", "quantum_threat", "pqc_replacement"}
        for row in load_crosswalk():
            missing = required - row.keys()
            self.assertFalse(missing, f"{row['id']} missing fields: {missing}")

    def test_quantum_threat_values_are_from_the_controlled_vocabulary(self):
        allowed = {"broken-by-shor", "weakened-by-grover", "no-crypto", "not-vulnerable"}
        for row in load_crosswalk():
            self.assertIn(row["quantum_threat"], allowed, row["id"])

    def test_find_by_id(self):
        row = find_by_id(load_crosswalk(), "OT-006")
        self.assertIsNotNone(row)
        self.assertEqual(row["protocol"], "OPC UA")
        self.assertIsNone(find_by_id(load_crosswalk(), "OT-999"))

    def test_shor_broken_rows_have_a_named_pqc_replacement(self):
        for row in load_crosswalk():
            if row["quantum_threat"] == "broken-by-shor":
                self.assertTrue(row["pqc_replacement"], row["id"])
                self.assertTrue(
                    any(tag in row["pqc_replacement"]
                        for tag in ("ML-", "LMS", "XMSS", "SLH-DSA")),
                    row["id"],
                )


if __name__ == "__main__":
    unittest.main()
