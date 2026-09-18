# -*- coding: utf-8 -*-
import json, io, os

OUT = "diagrams-v2"
TYPES = {"service": "backend", "compute": "backend", "database": "database",
         "external": "external", "cloud": "cloud", "messagebus": "messagebus",
         "security": "security"}

def new(cid, label, sub, x, y, w=180, h=66, tag=None, typ="service"):
    c = {"id": cid, "type": TYPES.get(typ, typ), "label": label, "sublabel": sub,
         "pos": [x, y], "size": [w, h]}
    if tag:
        c["tag"] = tag
    return c

def old(cid, label, sub, x, y, w=180, h=66, tag="removed"):
    # OLD components render grey via external type, with a badge.
    c = {"id": cid, "type": "external", "label": label, "sublabel": sub,
         "pos": [x, y], "size": [w, h]}
    if tag:
        c["tag"] = tag
    return c

def conn(cid, a, b, label="", variant=None):
    c = {"id": cid, "from": a, "to": b}
    if label:
        c["label"] = label
    if variant:
        c["variant"] = variant
    return c

def card(dot, title, items):
    return {"dot": dot, "title": title, "items": items}

def spec(title, components, connections, cards):
    # Tight viewBox: cards render outside the canvas, so size it to the
    # component bounding box plus margin. A wide canvas scales down at the
    # 1440px desktop viewport and fails the 6px minimum font check.
    import math
    max_x = max(c["pos"][0] + c["size"][0] for c in components) + 50
    max_y = max(c["pos"][1] + c["size"][1] for c in components) + 40
    vb = [int(math.ceil(max_x / 10.0) * 10), int(math.ceil(max_y / 10.0) * 10)]
    return {"schema_version": 1, "diagram_type": "architecture",
            "meta": {"title": title, "quality_profile": "showcase",
                     "viewBox": vb},
            "components": components, "connections": connections, "cards": cards}

specs = {}

# ---------------- 1. marlin watch: comparative ----------------
specs["01-marlin-watch-comparative"] = spec(
 "Marlin mesh watch: BEFORE to AFTER (2026-09-17)",
 # OLD cluster (left, grey)
 [old("oburst", "burst cron 15-min", "self-deleted on 8 quiet", 60, 80),
  old("oback", "backstop cron 2h", "12 fires/day, stranded mail", 60, 500),
  # NEW cluster (right, solid)
  new("nburst", "burst cron 15-min", "warm-reset keeps it alive", 700, 80),
  new("nback", "backstop cron hourly", "daytime 06-24", 700, 500),
  new("rearm", "REARM-BURST", "re-creates the burst", 470, 480, 170, 60, "self-heal"),
  # shared spine (solid)
  new("mesh", "shared/mesh-chat", "agentreef API", 60, 290, 160, 60),
  new("wswatch", "mesh_ws_watch", "logon task", 290, 290, 160, 60),
  new("log", "mesh_watch_marlin.log", "audit trail", 520, 290, 170, 60),
  new("watcher", "marlin_mesh_watch.py", "fail-loud deliverer", 940, 430, 190, 66),
  new("kimi", "marlin kimi session", "acts on mail", 1150, 290, 150, 60)],
 [conn("s1", "mesh", "wswatch", "WS rows"), conn("s2", "wswatch", "log"),
  conn("s3", "log", "watcher"), conn("s4", "watcher", "kimi", "MESH lines", "emphasis"),
  conn("n1", "nburst", "watcher"), conn("n2", "nback", "watcher"),
  conn("n4", "rearm", "nback", "", "emphasis"),
  conn("x1", "oburst", "nburst", "", "dashed")],
 [card("slate", "How to read this", ["Grey boxes with dashed edges: the old shape, removed or replaced",
    "Solid boxes and solid edges: what runs now", "Dashed cross edges: old part replaced by new part"]),
  card("rose", "The failure that drove it", ["QUIET-STREAK 8 = 2h no marlin mail, burst self-deleted; Antigravity dispatch landed 10 min later, stranded under a 2h backstop"]),
  card("emerald", "Measured result", ["57 to 27 fires per idle day; ~18.5M to ~7M tokens (62% cut); latency 15m warm, 60m cold"])])

# ---------------- 2. antigravity wake: comparative ----------------
specs["02-antigravity-wake-comparative"] = spec(
 "Antigravity wake chain: BEFORE to AFTER (2026-09-17)",
 [old("ocron", "schedule cron 5-min", "288 LLM turns/day on empty checks", 60, 100),
  old("oturn", "full LLM turn per fire", "~23M tokens/day, 576 empty turns", 60, 260),
  new("mail", "direct mail queue", "pending-direct.jsonl", 60, 470, 180, 60),
  new("notify", "mail_notify daemon", "PM2, watches the log", 330, 470, 180, 60),
  new("monitor", "session_monitor.py", "reactive wake <1s", 610, 380, 180, 60, "unified"),
  new("agy", "agy session", "woken only on mail", 900, 380, 170, 60),
  new("deadman", "deadman cron 30-min", "runs a script, not the model", 330, 90, 200, 60),
  new("check", "--check deterministic", "IDLE in <50ms, near-zero tokens", 610, 90, 200, 60),
  new("alert", "alert on not-IDLE", "surfaces to operator", 900, 90, 180, 60)],
 [conn("n1", "mail", "notify", "file event"), conn("n2", "notify", "monitor", "poke"),
  conn("n3", "monitor", "agy", "wake <1s", "emphasis"),
  conn("d1", "deadman", "check", "script run"), conn("d2", "check", "alert", "only if unhealthy"),
  conn("o1", "ocron", "oturn", "", "dashed"),
  conn("o2", "oturn", "agy", "forced prompt each fire", "dashed"),
  conn("x1", "oturn", "monitor", "", "dashed")],
 [card("slate", "How to read this", ["Grey boxes with dashed edges: the old shape, removed or replaced",
    "Solid: what runs now; emphasis: the load-bearing edge"]),
  card("rose", "The sink that drove it", ["A 5-minute schedule cron forced a full LLM turn every fire, empty queue or not"]),
  card("emerald", "Measured result", ["~23M tokens/day to near-zero when idle; mail wake under 1 second; one background task instead of two"])])

# ---------------- 3. auditor pipeline: comparative ----------------
specs["03-auditor-comparative"] = spec(
 "Gemma auditor card pipeline: BEFORE to AFTER (2026-09-17)",
 [old("opile", "out/*.jsonl unbounded", "1,680 active cards to Jul 16", 60, 90),
  old("oappend", "open(a) append", "2,293 empty _meta lines", 60, 240),
  old("ounion", "union-find clustering", "0.90 bridge chains blobs", 60, 390),
  old("odummy", "card_key() collapsed", "4,304 cards, ONE dummy hash", 60, 540),
  new("lanes", "Lane O + R + T", "triage cron every 6h", 330, 90, 180, 60),
  new("compact", "compaction + archival", "protected signals kept", 590, 90, 180, 60),
  new("keys", "card_key() fixed", "content_hash[:16] per card", 330, 470, 180, 60),
  new("cluster", "star clustering", "seed, sim >= 0.90", 590, 300, 170, 60),
  new("ledger", "reject ledger hardened", "30d tombstones, skew clamp", 850, 470, 190, 60),
  new("digest", "gemma_digest.py", "186 projections", 1060, 200, 160, 60),
  new("drain", "drain sweep", "quote-failed archived", 850, 90, 170, 60)],
 [conn("n0", "lanes", "compact", "retire-stale"), conn("n1", "compact", "drain"),
  conn("n3", "keys", "ledger", "dismissals match now"),
  conn("n4", "cluster", "digest", "0.910 worst sim proven", "emphasis"),
  conn("n5", "ledger", "digest", "suppressed", "emphasis"), conn("n6", "drain", "digest", "1,397 verified"),
  conn("o1", "opile", "oappend", "", "dashed"), conn("o2", "oappend", "ounion", "", "dashed"),
  conn("o3", "ounion", "odummy", "", "dashed"),
  conn("x2", "ounion", "cluster", "", "dashed"),
  conn("x3", "odummy", "keys", "", "dashed")],
 [card("slate", "How to read this", ["Grey boxes with dashed edges: the old shape, removed or replaced",
    "Dashed cross edges: old part replaced by new part; solid: current"]),
  card("rose", "The defect that hid under everything", ["Every relation candidate hashed to one dummy key: tombstones, dismissals, dedup all silently defeated (4,304 cards, one identity)"]),
  card("emerald", "Measured result", ["Fleet backlog 5,031 to 2,124; Lane O 1,680 to 189; relations 4,304 to 1,397 verified; 7 defects caught by adversarial loops that green suites missed"])])

# ---------------- 4. coordination: comparative ----------------
specs["04-coordination-comparative"] = spec(
 "Two-seat coordination: BEFORE to AFTER (2026-09-18)",
 [old("oa1", "seat A posts", "wait 2-5 min", 60, 150),
  old("ob1", "seat B replies", "wait 2-5 min", 60, 290),
  old("oa2", "seat A responds", "wait 2-5 min", 60, 430),
  old("ob2", "seat B fixes", "wait 2-5 min", 60, 570, 180, 60, "removed"),
  new("dag", "active_task_dag.json", "Kahn-validated, frontier dispatch", 420, 90, 220, 60, "built T1"),
  new("t4", "T4 marlin-verify", "claimed by marlin, DONE", 420, 260, 190, 60),
  new("t5", "T5 pilot-integration", "claimed & completed, DONE", 640, 430, 200, 60),
  new("ledger", "wrapup_ledger.jsonl", "bounded <=500 chars", 700, 260, 190, 60),
  new("thread", "fan-in mesh thread", "parallel nodes, one merge", 700, 90, 190, 60),
  new("resume", "resume path", "reads last 3-5 entries", 980, 260, 180, 60)],
 [conn("o1", "oa1", "ob1", "", "dashed"), conn("o2", "ob1", "oa2", "", "dashed"),
  conn("o3", "oa2", "ob2", "", "dashed"),
  conn("n2", "t4", "t5", "unblocks", "emphasis"),
  conn("n3", "t4", "ledger"), conn("n4", "ledger", "resume", "floor drop"),
  conn("n5", "thread", "t4", "numbered fan-in"),
  conn("x1", "ob2", "dag", "", "dashed")],
 [card("slate", "How to read this", ["Grey boxes with dashed edges: the old serial ping-pong chain",
    "Solid: the task DAG plus wrap-up ledger that replaced it"]),
  card("rose", "The pathology", ["A path graph: wall time equalled chain depth; every hop re-read full session context; subtasks ran serially even when independent"]),
  card("emerald", "First cycle executed 2026-09-18", ["Antigravity built T1-T3, marlin verified T4, T4 unblocked T5, Antigravity completed T5: zero ping-pong; F1 resolved with TaskAlreadyClaimedError + --force"])])

# ---------------- 5. lane hardening: comparative ----------------
specs["05-lane-hardening-comparative"] = spec(
 "Auditor lane execution: BEFORE to AFTER (2026-09-18)",
 [old("obare", "bare subprocesses", "no watchdog, 84% GPU 70m", 60, 120),
  old("olock", "flawed instance_lock", "check-then-act TOCTOU", 60, 270),
  old("oio", "raw JSONL write", "JSONDecodeError partial", 60, 420),
  old("otests", "failing test suites", "pytest plugin crashes", 60, 570),
  new("loop", "gemma_node_loop.py", "parent supervision + traps", 400, 120, 210, 60),
  new("lock", "atomic instance_lock", "stale PID reclaim, verify", 400, 270, 210, 60),
  new("safeio", "safe JSON I/O", "trailing newline guards", 400, 420, 210, 60),
  new("proc", "supervised children", "leak-resilient, 0 VRAM waste", 700, 120, 210, 60),
  new("triage", "curation_triage.py", "active compaction & drain", 700, 270, 210, 60),
  new("suite", "hardened test suite", "22/22 unit tests green", 700, 420, 210, 60)],
 [conn("o1", "obare", "olock", "", "dashed"),
  conn("o2", "olock", "oio", "", "dashed"),
  conn("o3", "oio", "otests", "", "dashed"),
  conn("x1", "obare", "loop", "", "dashed"),
  conn("n1", "loop", "proc", "supervises"),
  conn("n2", "loop", "lock"),
  conn("n3", "lock", "triage", "syncs"),
  conn("n4", "lock", "safeio"),
  conn("n5", "safeio", "suite", "tests safe I/O"),
  conn("n6", "proc", "triage"),
  conn("n7", "triage", "suite", "", "emphasis")],
 [card("slate", "How to read this", ["Grey boxes: bare subprocesses, TOCTOU lock races, and crashing test runner", "Solid: supervised subprocesses, atomic locks, safe file I/O, and 22/22 green tests"]),
  card("rose", "The failure modes", ["Orphaned child burned 84% GPU for 70 min; partial JSON writes crashed loop; test suites failed with unhandled exceptions"]),
  card("emerald", "Hardened resilience", ["8 vulnerabilities audited & resolved; atomic locks + parent PID supervision; 22/22 unit tests green in 2.78s"])])

os.makedirs(OUT, exist_ok=True)
for name, s in specs.items():
    with io.open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    print("wrote", name)
