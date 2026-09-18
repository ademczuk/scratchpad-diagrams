# -*- coding: utf-8 -*-
import json, io, os

OUT = "diagrams"

TMAP = {"service": "backend", "compute": "backend", "database": "database",
        "external": "external", "frontend": "frontend", "cloud": "cloud",
        "security": "security", "messagebus": "messagebus"}
DMAP = {"red": "rose", "green": "emerald", "amber": "amber", "cyan": "cyan",
        "violet": "violet", "orange": "orange", "slate": "slate"}

def comp(cid, typ, label, sub, x, y, w=170, h=64):
    return {"id": cid, "type": TMAP.get(typ, typ), "label": label, "sublabel": sub, "pos": [x, y], "size": [w, h]}

def conn(cid, a, b, label="", variant=None):
    c = {"id": cid, "from": a, "to": b}
    if label:
        c["label"] = label
    if variant:
        c["variant"] = variant
    return c

def card(dot, title, items):
    return {"dot": DMAP.get(dot, dot), "title": title, "items": items}

def spec(title, components, connections, cards):
    return {"schema_version": 1, "diagram_type": "architecture",
            "meta": {"title": title, "quality_profile": "showcase"},
            "components": components, "connections": connections, "cards": cards}

specs = {}

specs["01a-marlin-watch-before"] = spec(
 "Marlin mesh watch - BEFORE (2026-09-17 morning)",
 [comp("mesh", "external", "shared/mesh-chat", "agentreef API", 40, 300),
  comp("wswatch", "service", "mesh_ws_watch", "logon task: writes log only", 280, 300),
  comp("log", "database", "mesh_watch_marlin.log", "audit trail, nothing tails it", 520, 300),
  comp("burst", "service", "burst cron 15-min", "4 fires per hour", 280, 90),
  comp("backstop", "service", "backstop cron 2h", "12 fires per day", 280, 480),
  comp("watcher", "service", "marlin_mesh_watch.py", "dedup deliverer", 760, 300),
  comp("kimi", "compute", "marlin kimi session", "mesh mail acted on here", 990, 300)],
 [conn("m1", "mesh", "wswatch", "WS rows"), conn("m2", "wswatch", "log", "append"),
  conn("b1", "burst", "watcher", "runs"), conn("b2", "backstop", "watcher", "runs"),
  conn("w1", "watcher", "kimi", "MESH lines", "emphasis")],
 [card("red", "The failure (measured)", ["QUIET-STREAK 8 = 2h no mail to marlin, then burst DELETED itself",
    "Antigravity dispatch landed 10 min later: stranded under a 2h backstop",
    "Streak counted only marlin-addressed mail, ignored warm mesh"]),
  card("amber", "Idle-day cost", ["57 fires x ~324k tokens = ~18.5M tokens per idle day"])])

specs["01b-marlin-watch-after"] = spec(
 "Marlin mesh watch - AFTER (2026-09-17 evening)",
 [comp("mesh", "external", "shared/mesh-chat", "agentreef API", 40, 300),
  comp("wswatch", "service", "mesh_ws_watch", "logon task", 250, 300),
  comp("log", "database", "mesh_watch_marlin.log", "audit trail", 460, 300),
  comp("burst", "service", "burst cron 15-min", "self-deletes only on cold mesh", 250, 90),
  comp("backstop", "service", "backstop cron hourly", "daytime 06-24 only", 250, 490),
  comp("watcher", "service", "marlin_mesh_watch.py", "warm-reset + REARM-BURST", 680, 300),
  comp("kimi", "compute", "marlin kimi session", "mesh mail acted on here", 930, 300)],
 [conn("m1", "mesh", "wswatch", "WS rows"), conn("m2", "wswatch", "log", "append"),
  conn("b1", "burst", "watcher"), conn("b2", "backstop", "watcher"),
  conn("r1", "watcher", "backstop", "", "emphasis"),
  conn("w1", "watcher", "kimi", "MESH lines", "emphasis")],
 [card("green", "The fixes (all proven in vivo)", ["Warm-mesh reset: any fleet traffic <45 min old holds the burst",
    "Backstop prompt carries burst prompt verbatim: self-heals after compaction",
    "Seen-set fail-loud, deliver-before-record, daytime-only backstop"]),
  card("cyan", "Idle-day cost after", ["27 fires x ~324k = ~7M tokens per idle day (62% cut); latency 15m warm / 60m cold"])])

specs["02a-antigravity-wake-before"] = spec(
 "Antigravity wake chain - BEFORE (5-minute cron sink)",
 [comp("mail", "database", "direct mail queue", "pending-direct.jsonl", 40, 480),
  comp("cron", "service", "schedule cron 5-min", "harness schedule", 270, 300),
  comp("turn", "compute", "full LLM turn", "every fire, empty or not", 520, 300),
  comp("agy", "compute", "agy session", "context bloat 576 empty turns/day", 790, 300)],
 [conn("c1", "cron", "turn", "12 turns/hour"), conn("t1", "turn", "agy", "prompt injected"),
  conn("m1", "mail", "agy", "waits", "dashed")],
 [card("red", "The measured sink", ["288 LLM turns/day on empty queue checks",
    "~23M tokens/day; 576 empty turns bloating context", "Mail latency: up to 5 min even while paying"])])

specs["02b-antigravity-wake-after"] = spec(
 "Antigravity wake chain - AFTER (reactive + deterministic deadman)",
 [comp("mail", "database", "direct mail queue", "pending-direct.jsonl", 40, 300),
  comp("notify", "service", "mail_notify daemon", "PM2, watches log", 270, 300),
  comp("monitor", "service", "session_monitor.py", "reactive wake <1s", 520, 200),
  comp("agy", "compute", "agy session", "woken only on mail", 790, 200),
  comp("deadman", "service", "deadman cron 30-min", "runs --check", 270, 480),
  comp("check", "service", "--check deterministic", "IDLE in <50ms, no LLM", 520, 480)],
 [conn("n1", "mail", "notify", "file event"), conn("n2", "notify", "monitor", "poke"),
  conn("m1", "monitor", "agy", "wake <1s", "emphasis"),
  conn("d1", "deadman", "check", "script run"), conn("d2", "check", "monitor", "alert only if not IDLE")],
 [card("green", "The fix (verified same-day)", ["One background task, one lock, one offset file",
    "LLM woken only when mail lands; deadman costs ~0 tokens when healthy",
    "5-min cron sink deleted; deferral accounting resists zombie locks"])])

specs["03a-auditor-before"] = spec(
 "Gemma auditor card pipeline - BEFORE (2026-09-17 morning)",
 [comp("lanes", "service", "Lane O + Lane R", "mesh-ownership, repeat-loop", 40, 140),
  comp("pile", "database", "out/*.jsonl", "1,680 active cards, 3,973 lines", 300, 140),
  comp("digest", "compute", "gemma_digest.py", "union-find clustering 0.90", 560, 140),
  comp("noise", "external", "digest noise", "chain-merge blob piles", 830, 140),
  comp("rel", "database", "relation candidates", "4,304 cards", 300, 400),
  comp("dummy", "external", "ONE dummy hash", "same key for all 4,304", 560, 400, 200, 64)],
 [conn("l1", "lanes", "pile"), conn("p1", "pile", "digest", "read"),
  conn("d1", "digest", "noise", "blob piles"), conn("r1", "rel", "dummy", "one key")],
 [card("red", "The pileup (measured)", ["1,680 active cards dating to Jul 16; 2,293 empty _meta lines",
    "4,304 relation cards shared ONE key: tombstones and dismissals silently defeated",
    "Union-find chaining: one 0.90 bridge merges distinct piles into a blob"])])

specs["03b-auditor-after"] = spec(
 "Gemma auditor card pipeline - AFTER (2026-09-17 night)",
 [comp("lanes", "service", "Lane O + Lane R + Lane T", "triage cron wired", 40, 140),
  comp("compact", "service", "compaction + archival", "protected signals kept", 300, 140),
  comp("keys", "service", "card_key() fixed", "content_hash[:16]", 300, 300),
  comp("cluster", "compute", "star clustering", "seed exemplar, sim >= 0.90", 560, 140),
  comp("digest", "compute", "gemma_digest.py", "186 distinct projections", 830, 140),
  comp("ledger", "database", "reject ledger", "untracked, 30d tombstones, skew clamp", 560, 300)],
 [conn("l1", "lanes", "compact", "retire-stale 6h"), conn("c1", "compact", "cluster", "189 active cards"),
  conn("k1", "keys", "ledger", "dismissals match"), conn("s1", "cluster", "digest", "sim >= 0.90"),
  conn("r1", "ledger", "digest", "suppressed", "emphasis")],
 [card("green", "The drainage (measured on disk)", ["Fleet backlog 5,031 to 2,124 cards; Lane O 1,680 to 189",
    "Relations 4,304 to 1,397 verified (refines, depends-on, refutes with quote proof)",
    "4 adversarial loops caught 7 defects green suites missed (NameError, medoid 0.828, seen-file, deferral accounting)"])])

specs["04a-coordination-before"] = spec(
 "Two-seat coordination - BEFORE (serial ping-pong)",
 [comp("a1", "service", "seat A posts", "2-5 min wait", 60, 300),
  comp("b1", "service", "seat B replies", "2-5 min wait", 280, 300),
  comp("a2", "service", "seat A responds", "2-5 min wait", 500, 300),
  comp("b2", "service", "seat B fixes", "2-5 min wait", 720, 300),
  comp("a3", "service", "seat A verifies", "2-5 min wait", 940, 300, 160, 64)],
 [conn("e1", "a1", "b1", "claim"), conn("e2", "b1", "a2", "response"), conn("e3", "a2", "b2", "fix"),
  conn("e4", "b2", "a3", "verify", "emphasis")],
 [card("red", "The pathology", ["A path graph: depth equals wall time; every hop re-reads full session context",
    "Subtasks run serially even when independent; SUM(cost) instead of SPAN(DAG)",
    "claude-mem-lean evaluation miss: scoped by repo diffs, not measured pains"])])

specs["04b-coordination-after"] = spec(
 "Two-seat coordination - AFTER (task DAG + wrap-up ledger)",
 [comp("dag", "service", "active_task_dag.json", "Kahn-validated, frontier dispatch", 40, 300),
  comp("t3", "service", "T3 dag-comm-spec", "antigravity, DONE", 300, 140),
  comp("t4", "service", "T4 marlin-verify", "marlin, DONE", 300, 300),
  comp("t5", "service", "T5 pilot-integration", "antigravity, DONE", 300, 460),
  comp("ledger", "database", "wrapup_ledger.jsonl", "bounded <=500 chars", 560, 300),
  comp("resume", "compute", "resume path", "reads last 3-5 entries", 830, 300)],
 [conn("d1", "dag", "t3"), conn("d2", "dag", "t4"), conn("d4", "t4", "t5", "", "emphasis"),
  conn("l1", "t3", "ledger"), conn("l2", "t4", "ledger"),
  conn("r1", "ledger", "resume", "context floor drop")],
 [card("green", "First cycle executed 2026-09-18", ["Their build unblocked my node; my completion unblocked theirs - zero ping-pong",
    "Three-edge protocol: DAG-declared tasks, articulation-first probes, cycle guards",
    "F1 resolved: TaskAlreadyClaimedError + --force prevents cross-seat re-claim race",
    "All 5 tasks DONE on active DAG; lean resuming banner live in session monitor"])])

specs["05a-lane-hardening-before"] = spec(
 "Auditor lane execution - BEFORE (8 vulnerabilities & crash fragility)",
 [comp("loop", "backend", "gemma_node_loop.py", "bare subprocesses", 40, 140),
  comp("gpu", "backend", "RTX 5090 GPU", "unarbitrated port 7878", 300, 140),
  comp("child", "backend", "orphaned child", "unsupervised PID", 560, 140),
  comp("leak", "external", "VRAM leak", "84% GPU for 70 min", 830, 140),
  comp("lock", "security", "instance_lock", "check-then-act flaw", 40, 400),
  comp("toctou", "security", "TOCTOU race", "zombie PID lockouts", 300, 400),
  comp("cards", "database", "card stores", "unbounded JSONL write", 560, 400),
  comp("crash", "external", "loop crash", "JSONDecodeError partial", 830, 400)],
 [conn("c1", "loop", "gpu", "spawns"),
  conn("c2", "gpu", "child", "unmonitored"),
  conn("c3", "child", "leak", "burns VRAM", "emphasis"),
  conn("l1", "lock", "toctou", "race"),
  conn("l2", "toctou", "cards", "corrupts"),
  conn("l3", "cards", "crash", "terminates", "emphasis")],
 [card("rose", "Measured failure modes", [
   "Orphaned lane child burned 84% GPU for 70 minutes (zero supervision)",
   "Flawed instance lock allowed double-spawns and zombie lockouts",
   "Unprotected JSON parsing crashed entire loop on partial file writes",
   "Pytest test suites failing with unhandled plugin exceptions"
  ])])

specs["05b-lane-hardening-after"] = spec(
 "Auditor lane execution - AFTER (hardened guards & 100% green tests)",
 [comp("loop", "backend", "gemma_node_loop.py", "parent supervision", 40, 140),
  comp("guard", "security", "atomic instance_lock", "stale PID reclaim", 300, 140),
  comp("proc", "backend", "supervised children", "bounded runtime", 560, 140),
  comp("clean", "external", "clean lifecycle", "0 leaks, SIGTERM traps", 830, 140),
  comp("safeio", "database", "safe JSON I/O", "trailing newline guards", 40, 400),
  comp("triage", "backend", "curation_triage.py", "30d tombstone ledger", 300, 400),
  comp("compact", "database", "lane compaction", "out/*.jsonl drained", 560, 400),
  comp("suite", "security", "hardened tests", "22/22 unit tests green", 830, 400)],
 [conn("g1", "loop", "guard", "atomic check"),
  conn("g2", "guard", "proc", "supervised"),
  conn("g3", "proc", "clean", "healthy", "emphasis"),
  conn("s1", "safeio", "triage", "safe read"),
  conn("s2", "triage", "compact", "drains piles"),
  conn("s3", "compact", "suite", "verified", "emphasis")],
 [card("emerald", "Hardened resilience (in vivo verified)", [
   "8 critical failure modes audited, patched, and verified across all lanes",
   "Atomic locking + parent PID supervision prevents orphaned GPU hogs",
   "Partial-line trailing guards and atomic file replacement eliminate JSON corruption",
   "Full test suite restored: 22/22 unit tests passing in 2.78s with zero failures"
  ])])

os.makedirs(OUT, exist_ok=True)
for name, s in specs.items():
    with io.open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    print("wrote", name)
