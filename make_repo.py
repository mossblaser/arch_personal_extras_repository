"""
Utility which generates a package repository from the build packages in this
directory.

Usage::

    $ python make_repo.py REPO_NAME_HERE
"""

import os
import sys

from subprocess import run

from pathlib import Path
from shutil import copy

root_path = Path(__file__).parent

try:
    repo_dir = Path(sys.argv[1])
except IndexError:
    sys.stderr.write("Error: Expceted path to repo directory as first argument.\n")
    sys.exit(1)

failed = False

repo_dir.mkdir(parents=True, exist_ok=True)

all_packages = []
for pkgbuild in root_path.glob("*/PKGBUILD"):
    package = pkgbuild.parent
    
    packages = list(package.glob("*.zst"))
    if len(packages) != 1:
        sys.stderr.write(f"Error: Found {len(packages)} packages files in {package.relative_to(root_path)}\n")
        continue
    package = packages[0]
    
    target = repo_dir / package.name
    copy(package, target)
    all_packages.append(target)

result = run(["repo-add", repo_dir / f"{repo_dir.name}.db.tar.gz"] + all_packages)

if failed or result.returncode != 0:
    sys.exit(1)
