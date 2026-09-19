"""Full End-to-End Integration and Smoke Test Suite for CyberShell RPG v2.0.

Author: Amy (Project Lead & Master Integrator)
Role: Validates contracts, engine protocols, player progression, VFS integration,
      UI lifecycle, and end-to-end quest completion simulation.
Compatible with both standard library unittest and pytest.
"""

from tests.test_integration import TestCyberShellIntegration  # noqa: F401
import unittest

if __name__ == "__main__":
    unittest.main()
