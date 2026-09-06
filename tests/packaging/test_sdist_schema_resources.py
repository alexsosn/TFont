from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tfont.source_validation import SCHEMA_FILES  # noqa: E402


class SdistSchemaResourceTests(unittest.TestCase):
    def test_sdist_contains_all_canonical_structural_schemas(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dist = tmp_path / "dist"
            outside = tmp_path / "outside"
            dist.mkdir()
            outside.mkdir()

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--sdist",
                    "--outdir",
                    str(dist),
                    str(ROOT),
                ],
                check=True,
                cwd=outside,
            )
            sdists = list(dist.glob("*.tar.gz"))
            self.assertEqual(len(sdists), 1, sdists)

            with tarfile.open(sdists[0], "r:gz") as archive:
                names = set(archive.getnames())

            missing = []
            for filename in SCHEMA_FILES.values():
                suffix = f"/src/tfont/schemas/{filename}"
                if not any(name.endswith(suffix) for name in names):
                    missing.append(filename)
            self.assertFalse(missing, f"missing sdist schema resources: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
