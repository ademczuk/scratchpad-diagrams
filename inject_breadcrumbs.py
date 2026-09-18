# -*- coding: utf-8 -*-
"""
Inject interactive breadcrumb navigation into all generated archify diagram HTML pages.
Features:
- Home link back to Overview (index.html)
- Topic switcher dropdown (1 to 5)
- Segmented view switcher (Comparative | Before | After) with active highlight
- Sequential topic pager (Prev / Next)
- Keyboard shortcuts: H/Esc (Overview), C (Comparative), B (Before), A (After), [ (Prev), ] (Next)
- Responsive dark/light theme support matching Archify design
"""
import os
import re

DIAGRAMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")

TOPICS = [
    {
        "num": 1,
        "title": "1. Marlin mesh watch",
        "comparative": "01-marlin-watch-comparative.html",
        "before": "01a-marlin-watch-before.html",
        "after": "01b-marlin-watch-after.html",
    },
    {
        "num": 2,
        "title": "2. Antigravity wake chain",
        "comparative": "02-antigravity-wake-comparative.html",
        "before": "02a-antigravity-wake-before.html",
        "after": "02b-antigravity-wake-after.html",
    },
    {
        "num": 3,
        "title": "3. Gemma auditor card pipeline",
        "comparative": "03-auditor-comparative.html",
        "before": "03a-auditor-before.html",
        "after": "03b-auditor-after.html",
    },
    {
        "num": 4,
        "title": "4. Two-seat coordination",
        "comparative": "04-coordination-comparative.html",
        "before": "04a-coordination-before.html",
        "after": "04b-coordination-after.html",
    },
    {
        "num": 5,
        "title": "5. Auditor lane execution & hardening",
        "comparative": "05-lane-hardening-comparative.html",
        "before": "05a-lane-hardening-before.html",
        "after": "05b-lane-hardening-after.html",
    },
]

CSS = """
<style id="fleet-breadcrumb-style">
.fleet-breadcrumb-bar {
  position: fixed;
  top: 12px;
  left: 14px;
  z-index: 99999;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 12px;
  line-height: 1;
}
.fleet-breadcrumb-inner {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 9px;
  background: rgba(13, 17, 23, 0.92);
  border: 1px solid rgba(240, 246, 252, 0.16);
  border-radius: 8px;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #e6edf3;
}
html[data-theme="light"] .fleet-breadcrumb-inner {
  background: rgba(255, 255, 255, 0.94);
  border-color: rgba(31, 35, 40, 0.18);
  color: #1f2328;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.1);
}
.crumb-home {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #58a6ff;
  text-decoration: none;
  font-weight: 600;
  padding: 4px 6px;
  border-radius: 5px;
  transition: background 0.15s ease, color 0.15s ease;
}
.crumb-home:hover {
  background: rgba(88, 166, 255, 0.15);
  color: #79c0ff;
}
.crumb-sep {
  color: #6e7681;
  font-weight: 400;
  user-select: none;
}
.crumb-select-wrap {
  position: relative;
}
.crumb-select {
  appearance: none;
  -webkit-appearance: none;
  background: rgba(110, 118, 129, 0.12);
  color: inherit;
  border: 1px solid rgba(240, 246, 252, 0.12);
  border-radius: 6px;
  padding: 4px 22px 4px 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238b949e' stroke-width='2.5'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 6px center;
}
.crumb-select option {
  background: #161b22;
  color: #e6edf3;
}
html[data-theme="light"] .crumb-select option {
  background: #ffffff;
  color: #1f2328;
}
.crumb-views {
  display: inline-flex;
  background: rgba(110, 118, 129, 0.12);
  border-radius: 6px;
  padding: 2px;
  gap: 2px;
}
.crumb-view-tab {
  padding: 3px 8px;
  border-radius: 4px;
  text-decoration: none;
  color: #8b949e;
  font-weight: 500;
  font-size: 11px;
  transition: all 0.15s ease;
}
.crumb-view-tab:hover {
  color: #e6edf3;
  background: rgba(255, 255, 255, 0.06);
}
html[data-theme="light"] .crumb-view-tab:hover {
  color: #1f2328;
  background: rgba(0, 0, 0, 0.05);
}
.crumb-view-tab.active {
  background: #238636;
  color: #ffffff;
  font-weight: 600;
}
.crumb-view-tab.before.active {
  background: #da3633;
  color: #ffffff;
}
.crumb-view-tab.comparative.active {
  background: #1f6feb;
  color: #ffffff;
}
.crumb-pager {
  display: inline-flex;
  gap: 3px;
  margin-left: 2px;
}
.crumb-nav-btn {
  display: inline-flex;
  align-items: center;
  padding: 3px 7px;
  background: rgba(110, 118, 129, 0.12);
  border: 1px solid rgba(240, 246, 252, 0.1);
  border-radius: 5px;
  color: #8b949e;
  text-decoration: none;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.15s ease;
}
.crumb-nav-btn:hover {
  color: #e6edf3;
  border-color: rgba(240, 246, 252, 0.25);
  background: rgba(110, 118, 129, 0.22);
}
html[data-theme="light"] .crumb-nav-btn:hover {
  color: #1f2328;
  border-color: rgba(31, 35, 40, 0.3);
}
@media (max-width: 768px) {
  .crumb-home span { display: none; }
  .crumb-select { max-width: 130px; font-size: 11px; }
  .crumb-pager { display: none; }
}
</style>
"""

JS = """
<script id="fleet-breadcrumb-script">
(function() {
  window.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var key = e.key.toLowerCase();
    if (key === 'h' || (key === 'escape' && !document.querySelector('.dialog-open'))) {
      window.location.href = '../index.html';
    } else if (key === '[') {
      var prev = document.querySelector('.crumb-nav-btn.prev');
      if (prev) prev.click();
    } else if (key === ']') {
      var next = document.querySelector('.crumb-nav-btn.next');
      if (next) next.click();
    } else if (key === 'c') {
      var comp = document.querySelector('.crumb-view-tab.comparative');
      if (comp) comp.click();
    } else if (key === 'b') {
      var bef = document.querySelector('.crumb-view-tab.before');
      if (bef) bef.click();
    } else if (key === 'a') {
      var aft = document.querySelector('.crumb-view-tab.after');
      if (aft) aft.click();
    }
  });
})();
</script>
"""


def generate_breadcrumb_html(filename: str) -> str:
    # 1. Identify current topic & view
    curr_topic = None
    curr_topic_idx = 0
    curr_view = "comparative"

    for i, t in enumerate(TOPICS):
        if filename == t["comparative"]:
            curr_topic = t
            curr_topic_idx = i
            curr_view = "comparative"
            break
        elif filename == t["before"]:
            curr_topic = t
            curr_topic_idx = i
            curr_view = "before"
            break
        elif filename == t["after"]:
            curr_topic = t
            curr_topic_idx = i
            curr_view = "after"
            break

    if not curr_topic:
        return ""

    prev_topic = TOPICS[(curr_topic_idx - 1) % len(TOPICS)]
    next_topic = TOPICS[(curr_topic_idx + 1) % len(TOPICS)]

    # Link for prev/next preserves current view mode
    prev_link = prev_topic[curr_view] if curr_view in prev_topic else prev_topic["comparative"]
    next_link = next_topic[curr_view] if curr_view in next_topic else next_topic["comparative"]

    # Build options
    options_html = []
    for t in TOPICS:
        target_file = t[curr_view] if curr_view in t else t["comparative"]
        selected = ' selected="selected"' if t["num"] == curr_topic["num"] else ""
        options_html.append(f'        <option value="{target_file}"{selected}>{t["title"]}</option>')
    options_str = "\n".join(options_html)

    # Active view classes
    comp_active = " active" if curr_view == "comparative" else ""
    before_active = " active" if curr_view == "before" else ""
    after_active = " active" if curr_view == "after" else ""

    html = f"""
<!-- Fleet Breadcrumb Navigation -->
<nav class="fleet-breadcrumb-bar" id="fleet-breadcrumb" aria-label="Breadcrumb navigation">
  <div class="fleet-breadcrumb-inner">
    <a href="../index.html" class="crumb-home" title="Back to Overview (Key: H or Esc)">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      <span>Overview</span>
    </a>
    <span class="crumb-sep">/</span>
    <div class="crumb-select-wrap">
      <select id="topic-select" class="crumb-select" aria-label="Select optimization topic" onchange="location.href=this.value;">
{options_str}
      </select>
    </div>
    <span class="crumb-sep">/</span>
    <div class="crumb-views">
      <a href="{curr_topic['comparative']}" class="crumb-view-tab comparative{comp_active}" title="Comparative Unified View (Key: C)">Comparative</a>
      <a href="{curr_topic['before']}" class="crumb-view-tab before{before_active}" title="Before View (Key: B)">Before</a>
      <a href="{curr_topic['after']}" class="crumb-view-tab after{after_active}" title="After View (Key: A)">After</a>
    </div>
    <div class="crumb-pager">
      <a href="{prev_link}" class="crumb-nav-btn prev" title="Previous Topic: {prev_topic['title']} (Key: [)">‹ Prev</a>
      <a href="{next_link}" class="crumb-nav-btn next" title="Next Topic: {next_topic['title']} (Key: ])">Next ›</a>
    </div>
  </div>
</nav>
"""
    return CSS + html + JS


def inject_into_file(filepath: str) -> bool:
    filename = os.path.basename(filepath)
    breadcrumb_block = generate_breadcrumb_html(filename)
    if not breadcrumb_block:
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove existing injected breadcrumb if present
    content = re.sub(r'<style id="fleet-breadcrumb-style">.*?</script>\s*', '', content, flags=re.DOTALL)

    # Insert right after <body...>
    body_match = re.search(r'<body[^>]*>', content, flags=re.IGNORECASE)
    if not body_match:
        return False

    insert_pos = body_match.end()
    new_content = content[:insert_pos] + "\n" + breadcrumb_block + "\n" + content[insert_pos:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def main():
    count = 0
    for root, _, files in os.walk(DIAGRAMS_DIR):
        for f in files:
            if f.endswith(".html"):
                full_path = os.path.join(root, f)
                if inject_into_file(full_path):
                    print(f"Injected breadcrumbs into {f}")
                    count += 1
    print(f"Done! Successfully injected breadcrumbs into {count} diagram pages.")


if __name__ == "__main__":
    main()
