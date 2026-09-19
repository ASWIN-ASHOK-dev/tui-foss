"""Unit Test Suite for CyberShell UI & Visual FX.

Authors: Poornendhu & Gautham
Compatible with standard library unittest and pytest.
"""

import unittest
from tests.test_ui import (  # noqa: F401
    TestASCIIArt,
    TestCombatLogTicker,
    TestRPGAppGauthamIntegration,
    TestTerminalBufferWidget,
)

if __name__ == "__main__":
    unittest.main()
