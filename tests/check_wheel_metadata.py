"""Check built wheel metadata without installing development dependencies."""

import argparse
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile

RUNTIME_REQUIREMENTS = {
    "cachetools (>=6.2.0,<7.0.0)",
    "pymacaroons (==0.13.0)",
    "redis (>=6.4.0,<7.0.0)",
    "requests (>=2.32.2,<3.0.0)",
}


def check_wheel_metadata(wheel: Path) -> None:
    with ZipFile(wheel) as archive:
        metadata_paths = [
            name
            for name in archive.namelist()
            if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_paths) != 1:
            raise ValueError("Expected exactly one wheel METADATA file")
        metadata = BytesParser().parsebytes(archive.read(metadata_paths[0]))

    requirements = set(metadata.get_all("Requires-Dist", []))
    if requirements != RUNTIME_REQUIREMENTS:
        raise ValueError(
            "Unexpected wheel dependencies: "
            f"{sorted(requirements - RUNTIME_REQUIREMENTS)}; "
            "missing runtime dependencies: "
            f"{sorted(RUNTIME_REQUIREMENTS - requirements)}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheels", type=Path, nargs="+")
    for wheel in parser.parse_args().wheels:
        check_wheel_metadata(wheel)
        print(f"{wheel}: runtime requirements match; no mypy or coverage")
