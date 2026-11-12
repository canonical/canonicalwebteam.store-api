import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tests.check_wheel_metadata import (
    check_wheel_metadata,
    requirement_distribution_name,
)

RUNTIME_REQUIREMENTS = {
    "cachetools (>=6.2.0,<7.0.0)",
    "pymacaroons (==0.13.0)",
    "redis (>=6.4.0,<7.0.0)",
    "requests (>=2.32.2,<3.0.0)",
}


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
            "MYPY>=1.14.1",
            "Coverage[extra]>=7.0",
            "mypy",
            "coverage",
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

    def test_runtime_requirement_version_changes_accepted(self):
        self.write_wheel(
            {
                "cachetools>=7.0,<8.0",
                "pymacaroons==0.14.0",
                "redis>=7.0",
                "requests>=2.32.2,<4.0.0",
            }
        )
        check_wheel_metadata(self.wheel)

    def test_runtime_requirement_format_and_case_changes_accepted(self):
        self.write_wheel(
            {
                " CacheTools >=6.2.0, <7.0.0 ",
                "PYMACAROONS(==0.13.0)",
                'Redis>=6.4.0,<7.0.0; python_version >= "3.9"',
                "Requests[security] >=2.32.2,<3.0.0",
            }
        )
        check_wheel_metadata(self.wheel)

    def test_requirement_distribution_name_normalized(self):
        for requirement in [
            " Some_Package.Name (>=1.0) ",
            "SOME--PACKAGE__NAME[extra]>=1.0; os_name == 'posix'",
            "some-package-name @ https://example.com/package.whl",
        ]:
            with self.subTest(requirement=requirement):
                self.assertEqual(
                    requirement_distribution_name(requirement),
                    "some-package-name",
                )

    def test_missing_metadata_rejected(self):
        with ZipFile(self.wheel, "w"):
            pass
        with self.assertRaisesRegex(ValueError, "METADATA"):
            check_wheel_metadata(self.wheel)
