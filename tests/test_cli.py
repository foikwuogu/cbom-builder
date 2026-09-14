import json
import os
import subprocess
import sys
import tempfile
import unittest

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample_inventory.csv")


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "cbom_builder.cli", *args],
        capture_output=True, text=True,
    )


class TestCli(unittest.TestCase):
    def test_cli_version(self):
        result = run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("cbom-builder", result.stdout)

    def test_cli_scan_text(self):
        result = run_cli("scan", FIXTURE, "--format", "text")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Quantum-threat breakdown", result.stdout)

    def test_cli_scan_json_output(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "report.json")
            result = run_cli("scan", FIXTURE, "--format", "json", "--output", out)
            self.assertEqual(result.returncode, 0)
            with open(out) as f:
                report = json.load(f)
            self.assertEqual(report["total_components"], 8)

    def test_cli_list_crosswalk(self):
        result = run_cli("list-crosswalk")
        self.assertEqual(result.returncode, 0)
        self.assertIn("OT-001", result.stdout)
        self.assertIn("16 entries.", result.stdout)


if __name__ == "__main__":
    unittest.main()
