"""Provenance logging shared by submit.py and make_gridpack.py.

Appends a dated entry to PRODUCTION_LOG.md recording the git commit that
generated a batch (so you can `git checkout <sha>` to recover the exact code),
the parameters, the SLURM job ids, and the output directories.
"""
import datetime
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent
LOG = REPO / "PRODUCTION_LOG.md"


def git_ref():
    """Return (sha, dirty) for the repo, or ('unknown', False) outside git."""
    try:
        sha = subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(
            ["git", "-C", str(REPO), "status", "--porcelain"], text=True).strip())
        return sha, dirty
    except Exception:
        return "unknown", False


def append(title, lines):
    """Append an entry; `lines` is a list of markdown bullet strings.

    Returns (sha, dirty) so the caller can warn the user if the tree was dirty
    (meaning the recorded SHA does not capture the exact submitted code).
    """
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sha, dirty = git_ref()
    state = "DIRTY — SHA does NOT capture the exact code" if dirty else "clean"
    body = "\n".join(lines)   # callers supply their own "- "/"  - " bullets
    entry = f"\n## {ts} — {title}\n- commit: `{sha}` ({state})\n{body}\n"
    if not LOG.exists():
        LOG.write_text("# Production log\n\n"
                       "Auto-appended by `submit.py` and `make_gridpack.py`. "
                       "Each entry pins the git commit that generated the jobs, "
                       "their SLURM ids, and their output directories.\n")
    with open(LOG, "a") as f:
        f.write(entry)
    return sha, dirty
