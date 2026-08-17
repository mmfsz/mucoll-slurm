"""Resolve the container image and the benchmarks checkout for the submitters.

`lib/image.sh` owns the image literal — this module only reads it, so the image
is named in exactly one place for both the shell and the Python entry points.

Both values are overridable from the environment, which is how you point a run at
a locally pulled .sif or at a different benchmarks checkout without editing code:

    MUCOLL_IMAGE=/path/to/mucoll-sim.sif python submit.py ...
    MUCOLL_BENCHMARKS=/path/to/mucoll-benchmarks python submit.py ...
"""
import os
import re
from pathlib import Path

SLURM_DIR = Path(__file__).resolve().parent
IMAGE_SH = SLURM_DIR / "lib" / "image.sh"

# The v3.1 benchmarks layout (setup_config.sh + configs/ submodules) is not
# compatible with the old samf25 k4MuC checkout, so it lives alongside it rather
# than replacing it — main and this branch can both run. scripts/install_hpg.sh
# creates it.
DEFAULT_BENCHMARKS = SLURM_DIR.parent / "mucoll-benchmarks-v3.1"

_DEFAULT_RE = re.compile(r'^export\s+MUCOLL_IMAGE="\$\{MUCOLL_IMAGE:-(?P<path>[^}]*)\}"', re.M)


def image_path():
    """Return the container image path (env override wins, else lib/image.sh)."""
    env = os.environ.get("MUCOLL_IMAGE")
    if env:
        return env
    m = _DEFAULT_RE.search(IMAGE_SH.read_text())
    if not m:
        raise RuntimeError(
            f"could not parse the default MUCOLL_IMAGE out of {IMAGE_SH} — "
            "has its format changed? Set MUCOLL_IMAGE to work around this.")
    return m.group("path")


def bind_flags():
    """Extra apptainer binds needed by the image itself (see lib/image.sh)."""
    return os.environ.get("MUCOLL_BINDS", "--bind /cvmfs")


def benchmarks_path():
    """Return the mucoll-benchmarks checkout to run against."""
    return Path(os.environ.get("MUCOLL_BENCHMARKS", DEFAULT_BENCHMARKS))
