"""
Update the Python dependency of the package in the provided directory and
rebuild.
"""

import sys
import argparse
from pathlib import Path
import re
import subprocess

def parse_version(version_str: str) -> tuple[int, int]:
    try:
        return tuple(map(int, version_str.split(".")))[:2]
    except:
        raise ValueError


def update_pkgbuild(pkgbuild_file: Path, target_version: tuple[int, int]) -> None:
    orig_pkgbuild = pkgbuild = pkgbuild_file.read_text()

    # Move Python version range
    assert target_version[0] == 3
    pkgbuild = re.sub(
        r"(^depends=.*)'python>=[^']+'(.*$)",
        r"\1'python>=3.X.0'\2".replace("X", str(target_version[1])),
        pkgbuild,
        flags=re.MULTILINE,
    )
    pkgbuild = re.sub(
        r"(^depends=.*)'python<[^']+'(.*$)",
        r"\1'python<3.X.0'\2".replace("X", str(target_version[1] + 1)),
        pkgbuild,
        flags=re.MULTILINE,
    )
    
    # Increment pkgrel if changed
    if pkgbuild != orig_pkgbuild:
        pkgbuild = re.sub(
            r'^pkgrel="([0-9]+)"$',
            lambda match: f'pkgrel="{int(match.group(1)) + 1}"',
            pkgbuild,
            flags=re.MULTILINE,
        )
    
    pkgbuild_file.write_text(pkgbuild)


if __name__ == "__main__":
    if sys.prefix != sys.base_prefix:
        print("Do not run inside a virtualenv!", file=sys.stderr)
        sys.exit(1)
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "package_dir",
        type=Path,
        help="The directory containing the package to update",
    )
    parser.add_argument(
        "--target-version",
        "-v",
        type=parse_version,
        default=sys.version_info[:2],
        help="The Python version to update to",
    )
    parser.add_argument(
        "--force-mkpkg",
        "-f",
        action="store_true",
        default=False,
        help="Force rebuilding of the package",
    )
    
    args = parser.parse_args()
    
    if not ((3, 1) <= args.target_version < (4, 0)):
        parser.error("--target-version must be 3.X where X.")
    
    pkgbuild_file = args.package_dir / "PKGBUILD"
    
    update_pkgbuild(pkgbuild_file, args.target_version)
    
    # Rebuild the package
    result = subprocess.run(
        ["makepkg", "-sr"] + (["-f"] if args.force_mkpkg else []),
        cwd=args.package_dir,
    )
    sys.exit(result.returncode)
