"""
Enumerate the packages in this repository in order of dependency. Gaps are left
between groups of packages which are not interdependent.
"""

from pathlib import Path
import argparse
import re
import shlex
from textwrap import dedent
from subprocess import run
from toposort import toposort

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "repo_source_dir",
        nargs="?",
        type=Path,
        default=Path(),
        help="The directory containing subdirectories with packages.",
    )

    args = parser.parse_args()

    pkgname_to_dir: dict[str, Path] = {}
    pkgname_to_depends: dict[str, list[str]] = {}

    pkgbuilds = args.repo_source_dir.glob("*/PKGBUILD")
    for pkgbuild in pkgbuilds:
        result = run(
            ["bash"],
            input=dedent(
                f"""
                    {pkgbuild.read_text()}
                    echo "$pkgname"
                    for dep in "${{depends[@]}}"; do
                        echo "$dep"
                    done
                """
            ).strip(),
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.splitlines()
        pkgname = lines.pop(0)
        depends = [re.match(r"^([a-z-A-Z0-9_-]+)", line).group(0) for line in lines]

        pkgname_to_dir[pkgname] = pkgbuild.parent
        pkgname_to_depends[pkgname] = depends

    for group in toposort(pkgname_to_depends):
        print(
            "\n".join(
                str(pkgname_to_dir[pkgname])
                for pkgname in group
                if pkgname in pkgname_to_dir
            )
        )
        print()
