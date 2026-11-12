"""Check built wheel metadata without installing development dependencies."""

import argparse
import re
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile

RUNTIME_DEPENDENCY_NAMES = {"cachetools", "pymacaroons", "redis", "requests"}


def requirement_distribution_name(requirement: str) -> str:
    name = re.split(r"[\s\[<>=!~(;@]", requirement.strip(), maxsplit=1)[0]
    return re.sub(r"[-_.]+", "-", name).lower()


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

    dependency_names = {
        requirement_distribution_name(requirement)
        for requirement in metadata.get_all("Requires-Dist", [])
    }
    if dependency_names != RUNTIME_DEPENDENCY_NAMES:
        raise ValueError(
            "Unexpected wheel dependencies: "
            f"{sorted(dependency_names - RUNTIME_DEPENDENCY_NAMES)}; "
            "missing runtime dependencies: "
            f"{sorted(RUNTIME_DEPENDENCY_NAMES - dependency_names)}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheels", type=Path, nargs="+")
    for wheel in parser.parse_args().wheels:
        check_wheel_metadata(wheel)
        print(f"{wheel}: runtime dependency names match; no mypy or coverage")
