"""CBOM Builder -- checks OT protocol and identity components against a PQC readiness
crosswalk and produces a structured Cryptographic Bill of Materials (CBOM).
"""

__version__ = "0.1.0"

from .crosswalk import load_crosswalk
from .scanner import scan_inventory
from .report import build_report

__all__ = ["load_crosswalk", "scan_inventory", "build_report", "__version__"]
