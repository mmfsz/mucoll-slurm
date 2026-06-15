#!/usr/bin/env python3
"""
Watchdog for VBF inclusive production jobs (vbfZ/H/W_inclusive, 500 each = 1500 total).

Polls every 10 minutes. Resubmits jobs that fail due to transient causes:
  - NODE_FAIL / PREEMPTED
  - FAILED with signal-based exit code (0:N, N>0) — e.g. the 0:53 node kills we saw
  - TIMEOUT (treated as IO stall; 20 events should finish well within 10 h)

Does NOT resubmit:
  - FAILED with non-zero script exit (N:0, N>0) — execution/code error

Safety brakes:
  - Per-job resubmit cap (default 3): jobs at cap left as FAILED permanently.
  - Structural failure check: if no job has ever COMPLETED after
    --require-completion-after resubmit cycles and sampled stderrs share the
    same error fingerprint, abort and print diagnostics.
  - Node blacklisting: nodes causing repeated NODE_FAIL/PREEMPTED/signal-kills
    are excluded from future submissions via #SBATCH --exclude=.

State is persisted to OUTPUT_DIR/watchdog_state.json so the watchdog can be
restarted without losing resubmit counts.

Usage (from mucoll-slurm/):
    nohup python3 watchdog_vbf_inclusive.py > watchdog_vbf.log 2>&1 &
    echo $! > watchdog_vbf.pid
Stop:
    kill $(cat watchdog_vbf.pid)
"""

import argparse
import json
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Production configuration — mirrors submit_vbf_inclusive_10k.py
# ---------------------------------------------------------------------------
SLURM_DIR        = Path(__file__).parent.resolve()
MUONCOLLIDER_DIR = SLURM_DIR.parent
OUTPUT_BASE_DIR  = MUONCOLLIDER_DIR / "output/vbf_inclusive_production_10k"
BENCHMARKS_PATH  = MUONCOLLIDER_DIR / "mucoll-benchmarks"
APPTAINER_IMAGE  = SLURM_DIR / "mucoll-sim.sif"
_GP              = MUONCOLLIDER_DIR / "output/gridpacks"

PROCESSES = [
    ("vbfZ_inclusive", SLURM_DIR / "chains/run_chain_vbfZ.sh",
     ["4"], _GP / "grid_mumu_vbfZqq_inclusive"),
    ("vbfH_inclusive", SLURM_DIR / "chains/run_chain_vbfH.sh",
     ["4"], _GP / "grid_mumu_vbfHbb_inclusive"),
    ("vbfW_inclusive", SLURM_DIR / "chains/run_chain_vbfW.sh",
     ["4"], _GP / "grid_mumu_vbfWqq_inclusive"),
]
NUM_JOBS        = 500
NEVENTS_PER_JOB = 20

# ---------------------------------------------------------------------------
# Watchdog tunables
# ---------------------------------------------------------------------------
POLL_INTERVAL                  = 600   # seconds between scans
MAX_RESUBMIT_PER_JOB           = 3
REQUIRE_COMPLETION_AFTER_CYCLES = 2    # structural-failure check after this many cycles

# Exit-code interpretation:
#   "0:N" with N>0  → killed by signal N  → transient / node error
#   "N:0" with N>0  → script exited N     → execution error, do not resubmit
SIGNAL_EXIT_RE   = re.compile(r"^0:([1-9]\d*)$")   # 0:N, N>0
TERMINAL_STATES  = {"FAILED", "TIMEOUT", "NODE_FAIL", "PREEMPTED",
                    "CANCELLED", "OUT_OF_MEMORY"}

STATE_FILE     = OUTPUT_BASE_DIR / "watchdog_state.json"
BLACKLIST_FILE = OUTPUT_BASE_DIR / "watchdog_blacklist.txt"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Blacklist helpers
# ---------------------------------------------------------------------------
def load_blacklist():
    if BLACKLIST_FILE.exists():
        return sorted({n.strip() for n in BLACKLIST_FILE.read_text().split() if n.strip()})
    return []


def save_blacklist(nodes):
    BLACKLIST_FILE.write_text("\n".join(sorted(set(nodes))) + "\n")


# ---------------------------------------------------------------------------
# SLURM queries
# ---------------------------------------------------------------------------
def sacct_by_ids(slurm_ids):
    """Return {slurm_id: (state, exit_code, node)} for a list of IDs."""
    if not slurm_ids:
        return {}
    out = subprocess.run(
        ["sacct", "-j", ",".join(slurm_ids), "-X", "-n",
         "--format=JobID,State,ExitCode,NodeList"],
        capture_output=True, text=True,
    ).stdout
    result = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            jid   = parts[0].split(".")[0]
            state = parts[1]
            code  = parts[2] if len(parts) > 2 else "0:0"
            node  = parts[3] if len(parts) > 3 else ""
            result[jid] = (state, code, node)
    return result


def squeue_active():
    """Return {slurm_id: (job_name, state)} for all active jobs of this user."""
    out = subprocess.run(
        ["squeue", "-u", subprocess.check_output(["whoami"], text=True).strip(),
         "--format=%i %j %T", "-h"],
        capture_output=True, text=True,
    ).stdout
    result = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3:
            result[parts[0]] = (parts[1], parts[2])
    return result


def sacct_discover(lookback_days=7):
    """Find all mucoll_vbf*_inclusive_* jobs submitted in the last lookback_days days.
    Returns {job_name: [(submit_time, slurm_id), ...]} sorted newest-first."""
    import datetime
    since = (datetime.datetime.now() -
             datetime.timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M")
    out = subprocess.run(
        ["sacct", "--starttime", since, "-X", "-n",
         "--format=JobID,JobName%50,Submit,State,ExitCode,NodeList",
         "--user", subprocess.check_output(["whoami"], text=True).strip()],
        capture_output=True, text=True,
    ).stdout
    by_name = defaultdict(list)
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            jid    = parts[0].split(".")[0]
            name   = parts[1]
            submit = parts[2]
            if re.match(r"^mucoll_vbf[ZHW]_inclusive_\d+$", name):
                by_name[name].append((submit, jid))
    # sort newest-first within each name
    for name in by_name:
        by_name[name].sort(reverse=True)
    return by_name


# ---------------------------------------------------------------------------
# State file helpers
# ---------------------------------------------------------------------------
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def build_initial_state():
    """Build state from currently active + recently completed SLURM jobs."""
    log("Building initial state from SLURM (this may take a moment)...")
    state = {}
    active = squeue_active()
    discovered = sacct_discover()

    # For each expected job, pick the most recent SLURM ID
    for label, script, extras, gridpack in PROCESSES:
        for job_id in range(NUM_JOBS):
            key   = f"{label}_{job_id}"
            name  = f"mucoll_{key}"

            # First check squeue (most reliable for in-flight jobs)
            slurm_id = next((sid for sid, (n, _) in active.items() if n == name), None)

            # Fall back to sacct history
            if slurm_id is None and name in discovered:
                _, slurm_id = discovered[name][0]   # newest submission

            state[key] = {
                "label":          label,
                "job_id":         job_id,
                "slurm_id":       slurm_id,
                "resubmit_count": 0,
                "status":         "UNKNOWN",
            }

    log(f"  found SLURM IDs for "
        f"{sum(1 for e in state.values() if e['slurm_id'])} / {len(state)} jobs")
    return state


# ---------------------------------------------------------------------------
# Job resubmission
# ---------------------------------------------------------------------------
def make_sbatch(label, job_id, script_path, extras, gridpack, blacklist):
    """Generate and sbatch a single job; return new SLURM ID or None."""
    log_dir   = OUTPUT_BASE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    job_name  = f"mucoll_{label}_{job_id}"

    exclude_line = ""
    if blacklist:
        exclude_line = f"#SBATCH --exclude={','.join(sorted(set(blacklist)))}\n"

    script = (
        f"#!/bin/bash\n"
        f"#SBATCH --job-name={job_name}\n"
        f"#SBATCH --output={log_dir}/{label}_job_{job_id}.out\n"
        f"#SBATCH --error={log_dir}/{label}_job_{job_id}.err\n"
        f"#SBATCH --time=10:00:00\n"
        f"#SBATCH --mem=16G\n"
        f"#SBATCH --nodes=1\n"
        f"#SBATCH --ntasks=1\n"
        f"#SBATCH --cpus-per-task=4\n"
        f"#SBATCH --qos=avery-b\n"
        f"{exclude_line}"
        f"\n"
        f"echo \"Running on host: $(hostname)\"\n"
        f"echo \"Process: {label}  Job ID: {job_id}\"\n"
        f"apptainer exec --cleanenv --bind {MUONCOLLIDER_DIR} {APPTAINER_IMAGE} "
        f"bash {script_path} {job_id} {NEVENTS_PER_JOB} {OUTPUT_BASE_DIR} "
        f"{BENCHMARKS_PATH} {' '.join(extras)} {gridpack}\n"
    )

    tmp = SLURM_DIR / f"_watchdog_resub_{label}_{job_id}.sh"
    try:
        tmp.write_text(script)
        r = subprocess.run(["sbatch", str(tmp)], capture_output=True, text=True, check=True)
        m = re.search(r"Submitted batch job (\d+)", r.stdout)
        return m.group(1) if m else None
    except subprocess.CalledProcessError as e:
        log(f"    sbatch error for {job_name}: {e.stderr.strip()}")
        return None
    finally:
        if tmp.exists():
            tmp.unlink()


# ---------------------------------------------------------------------------
# Stderr sampling for structural-failure check
# ---------------------------------------------------------------------------
def sample_stderr_tails(failed_entries, state, n_samples=3, n_lines=8):
    """Read last n_lines of stderr for up to n_samples failed jobs.
    Returns (tails_list, fingerprints_list)."""
    tails, fps = [], []
    log_dir = OUTPUT_BASE_DIR / "logs"
    for key, entry, sacct_state, code, node in failed_entries[:n_samples]:
        label  = entry["label"]
        job_id = entry["job_id"]
        err_file = log_dir / f"{label}_job_{job_id}.err"
        if not err_file.exists():
            continue
        try:
            lines = err_file.read_text(errors="replace").splitlines()
        except Exception:
            continue
        tail     = lines[-n_lines:] if lines else []
        nonempty = [l for l in tail if l.strip()]
        fp       = nonempty[-1].strip() if nonempty else ""
        tails.append((key, sacct_state, node, tail))
        fps.append(fp)
    return tails, fps


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------
def scan(state, blacklist, total_resubmit_cycles, any_completed_ever,
         process_map, max_resubmit, require_completion_after):
    """One scan cycle. Returns (n_resubmitted, blacklist, counts_dict, any_completed_ever)."""

    # Build a map from SLURM id → state key for efficient lookup
    id_to_key = {e["slurm_id"]: k for k, e in state.items() if e["slurm_id"]}
    live_ids  = list(id_to_key.keys())

    sacct_data = sacct_by_ids(live_ids)

    counts = defaultdict(int)
    transient_failed = []   # (key, entry, sacct_state, exit_code, node)
    exec_errors      = []   # same, but execution errors

    for key, entry in state.items():
        sid = entry.get("slurm_id")
        if not sid:
            counts["no_id"] += 1
            continue

        sacct_state, code, node = sacct_data.get(sid, ("UNKNOWN", "0:0", ""))
        entry["status"] = sacct_state

        if sacct_state == "COMPLETED":
            counts["completed"] += 1

        elif sacct_state in ("RUNNING", "PENDING"):
            counts["active"] += 1

        elif sacct_state in TERMINAL_STATES:
            # Determine if this is a transient (node) failure or execution error
            is_transient = False

            if sacct_state in ("NODE_FAIL", "PREEMPTED"):
                is_transient = True
            elif sacct_state == "TIMEOUT":
                is_transient = True   # treat all timeouts as IO stalls
            elif sacct_state == "OUT_OF_MEMORY":
                is_transient = True   # hardware limit, retry on different node
            elif sacct_state == "FAILED":
                if SIGNAL_EXIT_RE.match(code):
                    is_transient = True   # killed by signal (e.g. 0:53)
                # else: script returned non-zero → execution error
            elif sacct_state.startswith("CANCELLED"):
                is_transient = False  # user-cancelled, don't resubmit

            if is_transient:
                transient_failed.append((key, entry, sacct_state, code, node))
            else:
                exec_errors.append((key, entry, sacct_state, code, node))
                counts["exec_error"] += 1

        else:
            counts["unknown"] += 1

    completed = counts["completed"]
    if completed > 0:
        any_completed_ever = True

    # ---- Safety brake: structural failure check ----
    if (transient_failed
            and total_resubmit_cycles >= require_completion_after
            and not any_completed_ever):
        tails, fps = sample_stderr_tails(transient_failed, state)
        unique_fps = {f for f in fps if f}
        if tails and len(unique_fps) <= 1:
            log("=" * 70)
            log("ABORT: structural failure detected — no job has COMPLETED after "
                f"{total_resubmit_cycles} resubmit cycle(s) and all sampled "
                "stderrs share the same fingerprint. Likely a code/config bug.")
            log(f"  Common fingerprint: {next(iter(unique_fps), '<empty>')}")
            for k, st, nd, tail in tails:
                log(f"  --- {k} (state={st}, node={nd or 'n/a'}) ---")
                for line in tail:
                    log(f"    {line}")
            log("Fix the underlying issue and restart the watchdog.")
            log("=" * 70)
            raise SystemExit(2)

    if exec_errors:
        log(f"  {len(exec_errors)} execution error(s) — NOT resubmitting:")
        for key, entry, st, code, node in exec_errors[:5]:
            log(f"    {key}: state={st} exit={code} node={node}")
        if len(exec_errors) > 5:
            log(f"    ... and {len(exec_errors) - 5} more")

    # ---- Per-job resubmit cap ----
    over_cap  = [e for e in transient_failed if e[1]["resubmit_count"] >= max_resubmit]
    eligible  = [e for e in transient_failed if e[1]["resubmit_count"] <  max_resubmit]
    if over_cap:
        log(f"  {len(over_cap)} job(s) at resubmit cap ({max_resubmit}) — leaving as FAILED:")
        for key, _, st, code, _ in over_cap[:5]:
            log(f"    {key}: state={st} exit={code}")
        counts["over_cap"] += len(over_cap)

    # ---- Blacklist bad nodes ----
    new_bad = set()
    for key, entry, st, code, node in eligible:
        if st in ("NODE_FAIL", "PREEMPTED") and node:
            new_bad.add(node)
        elif st == "FAILED" and SIGNAL_EXIT_RE.match(code) and node:
            new_bad.add(node)

    if new_bad:
        blacklist = sorted(set(blacklist) | new_bad)
        log(f"  blacklisting node(s): {sorted(new_bad)}")

    # ---- Resubmit eligible transient failures ----
    n_resubmitted = 0
    for key, entry, st, code, node in eligible:
        label  = entry["label"]
        job_id = entry["job_id"]
        script_path, extras, gridpack = process_map[label]
        new_sid = make_sbatch(label, job_id, script_path, extras, gridpack, blacklist)
        if new_sid:
            entry["slurm_id"]       = new_sid
            entry["resubmit_count"] = entry.get("resubmit_count", 0) + 1
            entry["status"]         = "PENDING"
            n_resubmitted += 1
            log(f"  resubmitted {key} (attempt {entry['resubmit_count']}, "
                f"prev state={st} exit={code}) → job {new_sid}")
        else:
            log(f"  failed to resubmit {key}")

    counts["resubmitted"] = n_resubmitted
    return n_resubmitted, blacklist, counts, any_completed_ever


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Watchdog for VBF inclusive production")
    ap.add_argument("--poll", type=int, default=POLL_INTERVAL,
                    help=f"Poll interval in seconds (default {POLL_INTERVAL})")
    ap.add_argument("--max-resubmit", type=int, default=MAX_RESUBMIT_PER_JOB,
                    help=f"Per-job resubmit cap (default {MAX_RESUBMIT_PER_JOB})")
    ap.add_argument("--require-completion-after", type=int,
                    default=REQUIRE_COMPLETION_AFTER_CYCLES,
                    help="Abort if no job completed after this many resubmit cycles "
                         f"(default {REQUIRE_COMPLETION_AFTER_CYCLES})")
    ap.add_argument("--rebuild-state", action="store_true",
                    help="Ignore existing state file and rediscover jobs from SLURM")
    args = ap.parse_args()

    OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

    # Build process lookup: label → (script_path, extras, gridpack)
    process_map = {
        label: (script, extras, gridpack)
        for label, script, extras, gridpack in PROCESSES
    }

    # Load or build state
    if STATE_FILE.exists() and not args.rebuild_state:
        state = load_state()
        log(f"Loaded state: {len(state)} job entries from {STATE_FILE}")
    else:
        state = build_initial_state()
        save_state(state)
        log(f"State saved to {STATE_FILE}")

    blacklist                = load_blacklist()
    total_resubmit_cycles    = 0
    any_completed_ever       = any(e.get("status") == "COMPLETED" for e in state.values())

    log(f"Watchdog started | jobs={len(state)} | poll={args.poll}s | "
        f"max_resubmit={args.max_resubmit} | blacklist={blacklist or 'empty'}")

    while True:
        try:
            n_resub, blacklist, counts, any_completed_ever = scan(
                state, blacklist, total_resubmit_cycles, any_completed_ever,
                process_map, args.max_resubmit, args.require_completion_after,
            )
            save_state(state)
            save_blacklist(blacklist)

            if n_resub > 0:
                total_resubmit_cycles += 1

            log(
                f"scan | completed={counts['completed']} "
                f"active={counts['active']} "
                f"resubmitted={counts['resubmitted']} "
                f"exec_errors={counts['exec_error']} "
                f"over_cap={counts['over_cap']} "
                f"unknown={counts['unknown']} "
                f"| cycles={total_resubmit_cycles} "
                f"blacklist={blacklist or 'empty'}"
            )

            # Exit when all jobs are in terminal state and nothing was resubmitted
            n_active    = counts["active"]
            n_completed = counts["completed"]
            if n_active == 0 and n_resub == 0:
                log(f"All jobs settled. completed={n_completed} "
                    f"exec_errors={counts['exec_error']} "
                    f"over_cap={counts['over_cap']}. Watchdog exiting.")
                return

        except SystemExit:
            raise
        except Exception as exc:
            log(f"ERROR in scan: {exc!r} (continuing)")

        time.sleep(args.poll)


if __name__ == "__main__":
    main()
