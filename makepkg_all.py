"""
Utility which re-runs makepkg for all packages.
"""

import os
import sys

from pathlib import Path

from concurrent.futures import ThreadPoolExecutor
from subprocess import run, STDOUT

root_path = Path(__file__).parent

try:
    max_workers = int(sys.argv[1])
    sys.argv.pop(1)
except (IndexError, ValueError):
    max_workers = os.cpu_count()

extra_args = sys.argv[1:]

failed = False

sys.stderr.write("Building all packages...\n")

with ThreadPoolExecutor(max_workers) as executor:
    for pkgbuild, completed_process in executor.map(
        lambda pkgbuild: (
            pkgbuild,
            run(
                ["makepkg"] + extra_args,
                cwd=pkgbuild.parent,
                stderr=STDOUT,
                stdout=(pkgbuild.parent / "makepkg.log").open("wb"),
            )
        ),
        root_path.glob("*/PKGBUILD"),
    ):
        sys.stderr.write("\n")
        if completed_process.returncode != 0:
            sys.stderr.write(f"Failed to build {pkgbuild.relative_to(root_path)}:\n")
            sys.stderr.write((pkgbuild.parent / "makepkg.log").open("r").read())
            failed = True
        else:
            sys.stderr.write(f"Successfuly built {pkgbuild.relative_to(root_path)}\n")

if failed:
    sys.exit(1)
