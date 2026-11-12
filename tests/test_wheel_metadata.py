import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tests.check_wheel_metadata import (
    RUNTIME_REQUIREMENTS,
    check_wheel_metadata,
)


class TestWheelMetadata(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.wheel = Path(directory.name) / "store_api.whl"

    def write_wheel(self, requirements):
        metadata = "Metadata-Version: 2.1\nName: canonicalwebteam.store-api\n"
        for requirement in sorted(requirements):
            metadata += f"Requires-Dist: {requirement}\n"
        with ZipFile(self.wheel, "w") as archive:
            archive.writestr("store_api.dist-info/METADATA", metadata)

    def test_runtime_requirements_match(self):
        self.write_wheel(RUNTIME_REQUIREMENTS)
        check_wheel_metadata(self.wheel)

    def test_development_tools_rejected(self):
        for requirement in [
            "mypy (>=1.14.1,<2.0.0)",
            "coverage (>=7.0,<8.0)",
        ]:
            with self.subTest(requirement=requirement):
                self.write_wheel(RUNTIME_REQUIREMENTS | {requirement})
                with self.assertRaisesRegex(
                    ValueError, "Unexpected wheel dependencies"
                ):
                    check_wheel_metadata(self.wheel)

    def test_runtime_requirement_removal_rejected(self):
        for requirement in RUNTIME_REQUIREMENTS:
            with self.subTest(requirement=requirement):
                self.write_wheel(RUNTIME_REQUIREMENTS - {requirement})
                with self.assertRaisesRegex(
                    ValueError, "missing runtime dependencies"
                ):
                    check_wheel_metadata(self.wheel)

    def test_runtime_requirement_version_change_rejected(self):
        requirements = RUNTIME_REQUIREMENTS - {"requests (>=2.32.2,<3.0.0)"}
        self.write_wheel(requirements | {"requests (>=2.32.2,<4.0.0)"})
        with self.assertRaisesRegex(ValueError, "requests"):
            check_wheel_metadata(self.wheel)

    def test_missing_metadata_rejected(self):
        with ZipFile(self.wheel, "w"):
            pass
        with self.assertRaisesRegex(ValueError, "METADATA"):
            check_wheel_metadata(self.wheel)
