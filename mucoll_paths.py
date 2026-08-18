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


# --- Where productions are written -------------------------------------------
# Samples outgrew /blue: the avery group sits at ~105 T of its 119 T quota,
# while /cmsuf (Lustre) has ~777 T free. Everything below is overridable, so a
# different cluster — or a user without a /cmsuf area — still works unedited.

CMSUF_USER_ROOT = Path("/cmsuf/data/store/user")
LEGACY_OUTPUT = SLURM_DIR.parent / "output"


def _cmsuf_user_dir():
    """This user's /cmsuf area, or None.

    The HPG username and the /cmsuf directory name do not always match
    (`m.mazza` -> `mmazza`), so try the username as-is and then with dots
    removed, taking the first that exists rather than assuming a rule.
    """
    user = os.environ.get("USER", "")
    for name in (user, user.replace(".", "")):
        if name:
            d = CMSUF_USER_ROOT / name
            if d.is_dir():
                return d
    return None


def output_base():
    """Root holding `samples/` and `gridpacks/` (MUCOLL_OUTPUT overrides)."""
    env = os.environ.get("MUCOLL_OUTPUT")
    if env:
        return Path(env)
    d = _cmsuf_user_dir()
    return d / "mucoll" if d else LEGACY_OUTPUT


def samples_base():
    """Where production samples land (was `output/batch`, now `<base>/samples`)."""
    return output_base() / "samples"


def gridpack_base():
    """Where VAMP grids live (MUCOLL_GRIDPACKS overrides).

    Prefers `<base>/gridpacks`, but only once that directory exists — so grids
    keep resolving to the legacy location until they are migrated, and the
    switch happens the moment they are. No flag day, and no window where a
    production silently re-integrates because it looked in an empty new dir.
    """
    env = os.environ.get("MUCOLL_GRIDPACKS")
    if env:
        return Path(env)
    cand = output_base() / "gridpacks"
    return cand if cand.is_dir() else LEGACY_OUTPUT / "gridpacks"
