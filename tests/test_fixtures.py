import json
import os
import unittest
from pathlib import Path

from ee2pw.core import builder

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PRESETS_DIR = FIXTURES_DIR / "presets"
EXPECTED_DIR = FIXTURES_DIR / "expected"

# Regenerate expected outputs with: UPDATE_FIXTURES=1 python -m unittest tests.test_fixtures
UPDATE = os.environ.get("UPDATE_FIXTURES") == "1"


class TestFixtures(unittest.TestCase):
    def test_presets_match_expected(self) -> None:
        presets = sorted(PRESETS_DIR.glob("*.json"))
        self.assertTrue(presets, f"no presets in {PRESETS_DIR}")

        for preset in presets:
            with self.subTest(preset=preset.name):
                result = builder(str(preset), "Test Chain", "/irs", "test_sink")
                expected_path = EXPECTED_DIR / preset.name

                if UPDATE:
                    expected_path.write_text(json.dumps(result, indent=2) + "\n")

                self.assertTrue(
                    expected_path.exists(),
                    f"missing {expected_path}, run with UPDATE_FIXTURES=1",
                )
                self.assertEqual(result, json.loads(expected_path.read_text()))


if __name__ == "__main__":
    unittest.main()
