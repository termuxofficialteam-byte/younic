#!/usr/bin/env python3
# YOUNIC v3.0 - AI Developer Studio, powered by Qoder
# Copyright (c) 2026 Termux Developer. All rights reserved.
# See LICENSE for terms. Contact: termuxofficialteam@gmail.com
import os, sys, json, re, time, subprocess, difflib, shutil, random, threading, ast, urllib.request, urllib.error

BASE  = os.path.expanduser("~/codex")
PROJ  = os.path.join(BASE, "projects")
BAK   = os.path.join(BASE, "backups")
KEYF  = os.path.join(BASE, ".apikey")
CONFIGF = os.path.join(BASE, "config.json")
APP_DIR = os.path.dirname(os.path.abspath(__file__))   # folder where codex.py runs
TOOLS_DIR = os.path.join(APP_DIR, "tools")
REGISTRY = os.path.join(TOOLS_DIR, "registry.json")    # tool memory
OUT   = os.path.join(os.path.expanduser("~"), "Documents", "Codex") if os.name == "nt" else "/sdcard/Codex"
MODEL = "gemini-3.5-flash-lite"
APP_NAME = "YOUNIC"
APP_VERSION = "3.0.0"
# EDUCATIONAL USE ONLY: generated code is not sandboxed or security-reviewed.
# Tool creation may install dependencies and execute generated programs locally.
AI_TOOL_NAME = "Qoder"
DEV_NAME = "Termux Developer"
DEV_EMAIL = "termuxofficialteam@gmail.com"
# NOTE: data folders (~/codex, /sdcard/Codex) are kept as-is so existing projects, keys and backups still work.
STREAM_URL = "https://generativelanguage.googleapis.com/v1beta/models/%s:streamGenerateContent?alt=sse"

# Palette: ACC/DACC = green accent (UI), ERR = red (errors only)
R="\033[0m"; B="\033[1m"; DIM="\033[2m"; STRIKE="\033[9m"
ERR="\033[91m"; ACC="\033[92m"; DACC="\033[32m"; GRN="\033[92m"; YEL="\033[93m"
CYN="\033[96m"; GRY="\033[90m"; WHT="\033[97m"; MAG="\033[95m"
DBG_RED="\033[48;5;52m"
DBG_GRN="\033[48;5;22m"
DBG_YEL="\033[48;5;58m"
DBG_CYN="\033[48;5;23m"

if os.name == "nt": os.system("")  # turns on ANSI colour codes in the Windows console
def w(s): sys.stdout.write(s); sys.stdout.flush()
def cls(): os.system("cls" if os.name == "nt" else "clear")
def cols():
    try: return max(40, shutil.get_terminal_size().columns)
    except Exception: return 60

SYSTEM = (
 "You are Qoder, the built-in AI coding assistant of YOUNIC (AI Developer Studio by Termux Developer), "
 "an elite software engineer inside Termux on Android. "
 "Output ONE complete working program. Format EXACTLY: first line 'FILENAME: name.ext', "
 "then ONE fenced code block with the full code, nothing else after it. "
 "Pick the extension matching the language the user asked for (or infer a sensible one). "
 "HTML: single file, inline CSS/JS, clean modern mobile UI. Python: stdlib only, works with python3. "
 "C/C++: C11/C++17, must compile with clang/clang++ in Termux, no external libs. "
 "JavaScript/TypeScript: Node.js compatible, no external npm packages. "
 "Go: single file, 'package main', stdlib only, no go.mod needed. "
 "Rust: single file with fn main(), std only, no external crates. "
 "Java: public class name MUST exactly match the filename (without .java). "
 "PHP/Ruby/Perl/Lua: standard interpreter syntax, no external gems/modules/luarocks. "
 "No placeholders, no explanations, always return the COMPLETE file."
)

BANNER = r"""
██╗   ██╗ ██████╗ ██╗   ██╗███╗   ██╗██╗ ██████╗
╚██╗ ██╔╝██╔═══██╗██║   ██║████╗  ██║██║██╔════╝
 ╚████╔╝ ██║   ██║██║   ██║██╔██╗ ██║██║██║
  ╚██╔╝  ██║   ██║██║   ██║██║╚██╗██║██║██║
   ██║   ╚██████╔╝╚██████╔╝██║ ╚████║██║╚██████╗
   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝"""

STATS = {"runs": 0, "lines": 0, "fixes": 0, "start": time.time()}
TYPE_CPS = 260   # characters/sec typewriter speed for the live-write display
CURSOR = "▍"
ANIM = True      # animations on/off (toggle with /anim on|off)


# ---------- green shading loop effects ----------
SHADES = [22, 28, 34, 40, 46, 82, 118, 82, 46, 40, 34, 28]
MATRIX_CHARS = "01<>{}[]#$%&*+=/|"          # ASCII only, so columns stay aligned
MATRIX_SHADES = [22, 28, 34, 40, 46]
def sh(n): return "\033[38;5;%dm" % n

def shaded_banner_frame(lines, phase):
    out = []
    for ln in lines:
        row = ""
        for x, ch in enumerate(ln):
            if ch == " ":
                row += ch
            else:
                row += sh(SHADES[(x // 2 + phase) % len(SHADES)]) + B + ch
        out.append(row + R)
    return out

def green_wave(seconds=3.0, fps=14):
    lines = BANNER.strip("\n").split("\n")
    h = len(lines)
    frames = int(seconds * fps)
    w("\033[?25l")
    try:
        for f in range(frames):
            if f > 0: w("\033[%dA" % h)
            for row in shaded_banner_frame(lines, f):
                w(row + "\033[K\n")
            time.sleep(1.0 / fps)
    finally:
        w("\033[?25h")

def matrix_rain(seconds=1.2, fps=16, height=7):
    """Green falling-code intro shown before the banner (NEW)."""
    width = min(cols() - 1, 80)
    drops = [random.randint(-height, 0) for _ in range(width)]
    w("\033[?25l")
    try:
        for f in range(int(seconds * fps)):
            if f > 0: w("\033[%dA" % height)
            for y in range(height):
                row = ""
                for x in range(width):
                    dist = drops[x] - y
                    if dist == 0:
                        row += WHT + random.choice(MATRIX_CHARS) + R
                    elif 0 < dist <= 5:
                        row += sh(MATRIX_SHADES[5 - dist]) + random.choice(MATRIX_CHARS) + R
                    else:
                        row += " "
                w(row + "\033[K\n")
            for x in range(width):
                drops[x] += 1
                if drops[x] - height > 5:
                    drops[x] = random.randint(-height, 0)
            time.sleep(1.0 / fps)
        # erase the rain area so the banner starts on a clean screen
        w("\033[%dA" % height + ("\033[K\n" * height) + "\033[%dA" % height)
    finally:
        w("\033[?25h")

def pulse_line(seconds=1.5, fps=16):
    width = min(cols() - 2, 44)
    w("\033[?25l")
    try:
        for f in range(int(seconds * fps)):
            row = ""
            for x in range(width):
                row += sh(SHADES[(x + f) % len(SHADES)]) + "\u2501"
            w("\r" + row + R)
            time.sleep(1.0 / fps)
        w("\n")
    finally:
        w("\033[?25h")

def shade_bar(pct, width=20):
    fill = int(width * pct / 100)
    row = ""
    for i in range(width):
        row += (sh(SHADES[(i * 2) % len(SHADES)]) + "\u2588") if i < fill else (GRY + "\u2591")
    return row + R + " %3d%%" % pct

def _glitch(text, amt=0.25):
    glyphs = "▓▒░█▄▀■□#$%&"
    return "".join(random.choice(glyphs) if (c != " " and random.random() < amt) else c for c in text)

def typewriter(text, color=GRY, delay=0.012):
    """Print plain text one character at a time (NEW). Skips delay when animations are off."""
    for c in text:
        w(color + c + R)
        if ANIM and delay: time.sleep(delay)

def boot_sequence():
    """Hacker-movie style startup diagnostics — shown once before the banner."""
    cls(); w("\033[?25l")
    lines = [
        ("KERNEL", "termux-app :: android sandbox", True),
        ("SHELL",  os.environ.get("SHELL", "/bin/bash"), True),
        ("HOME",   BASE, True),
        ("PROJ",   PROJ, True),
        ("BACKUP", BAK, True),
        ("MODEL",  MODEL, True),
        ("OUTPUT", OUT, True),
        ("AUTH",   "%s [key vault]" % (KEYF if os.path.exists(KEYF) else "no key found"), os.path.exists(KEYF)),
        ("LINK",   "generativelanguage.googleapis.com :: 443", True),
    ]
    try:
        for label, val, ok in lines:
            frames = 3 if ANIM else 1
            for f in range(frames):
                amt = (0.5 - f * 0.18) if ANIM else 0
                w("\r" + ACC + "[" + random.choice(SPIN) + "] " + GRY + label.ljust(7) + R + " " + _glitch(val, amt))
                if ANIM: time.sleep(0.02)
            mark = GRN + "✔" if ok else YEL + "⚠"
            w("\r" + mark + R + " " + WHT + label.ljust(7) + R + " " + sh(40) + val + R + "   \n")
            if ANIM: time.sleep(0.05)
        w(DACC + " " + "─" * 42 + "\n" + R)
        w(GRN + B + " SYSTEM READY" + R + GRY + "  — initializing YOUNIC...\n" + R)
        w(YEL + B + "  EDUCATIONAL USE ONLY — generated code is untrusted and is not sandboxed.\n" + R)
        w(YEL + "  /tool may install dependencies and run generated programs on this device.\n" + R)
        w(YEL + "  Review code first; use a disposable, unprivileged environment.\n" + R)
        if ANIM: time.sleep(0.35)
    finally:
        w("\033[?25h")

def net_trace(host="generativelanguage.googleapis.com", seconds=0.55):
    """Fake network-hop animation shown right before hitting the real API."""
    w("\033[?25l")
    hops = ["resolving dns", "tls handshake", host, "stream open"]
    try:
        for i, hop in enumerate(hops):
            pct = int(100 * (i + 1) / len(hops))
            w("\r" + ACC + "◈" + R + " " + GRY + "connect  " + R + shade_bar(pct, 16) + "  " + sh(82) + hop + R + "   ")
            if ANIM: time.sleep(seconds / len(hops))
        w("\r" + GRN + "✔" + R + " " + WHT + "connect  " + R + shade_bar(100, 16) + "  " + GRY + host + R + "   \n")
    finally:
        w("\033[?25h")

def scan_path(path, label="PATH"):
    """Show the real file path being touched, with a quick green scan-bar (recording flourish)."""
    w("\033[?25l")
    try:
        steps = range(0, 101, 20) if ANIM else []
        for i in steps:
            w("\r" + sh(46) + "▶ " + R + GRY + label.ljust(6) + R + " " + shade_bar(i, 14) + "  " + DIM + path + R)
            time.sleep(0.012)
        w("\r" + GRN + "▶ " + R + WHT + label.ljust(6) + R + " " + shade_bar(100, 14) + "  " + ACC + path + R + "\n")
    finally:
        w("\033[?25h")

FUNCTION_GROUPS = [
    ("PROJECT", ["/new", "/paste", "/open", "/show", "/list", "/save", "/undo"]),
    ("AI CODE", ["/edit", "/fix", "/advise", "/loop", "/run"]),
    ("TOOLS",   ["/tool", "/tools", "/launch", "/runmode"]),
    ("SETTINGS", ["/key", "/model", "/outdir", "/speed", "/anim", "/stats", "/clear"]),
    ("HELP",    ["/menu", "/guide", "/about", "/help", "/quit"]),
]

def banner(anim=True):
    cls()
    lines = BANNER.split("\n")
    if anim and ANIM:
        matrix_rain()
        cls()
        glitch = "▓▒░█▄▀■□"
        for f in range(5):
            cls()
            for ln in lines:
                g = "".join(random.choice(glitch) if (c != " " and random.random() < 0.3 * (4 - f) / 4) else c for c in ln)
                w(ACC + B + g + R + "\n")
            time.sleep(0.08)
        cls()
        w("\n")
        green_wave(2.6)
    else:
        for ln in lines:
            w(ACC + B + ln + R + "\n")
    w(DACC + " " + "═" * 42 + "\n" + R)
    w(ACC + B + "  " + APP_NAME + " v" + APP_VERSION + R + GRY + "  AI DEVELOPER STUDIO\n" + R)
    w(GRY + "  Developer: " + WHT + DEV_NAME + R + "\n")
    w(GRY + "  Email:     " + ACC + _mail_link(DEV_EMAIL) + R + "\n")
    w(GRY + "  Powered by " + AI_TOOL_NAME + "  |  model: " + ACC + MODEL + R + "\n")
    w(DACC + " " + "═" * 42 + "\n" + R)
    for head, cmds in FUNCTION_GROUPS:
        w(ACC + B + " " + head.ljust(9) + R + GRY + " ".join(cmds) + R + "\n")
    w("\n")

def goodbye_screen():
    """Clean exit screen with session summary (NEW)."""
    cls()
    lines = BANNER.strip("\n").split("\n")
    for i, ln in enumerate(lines):
        w(sh(SHADES[i % len(SHADES)]) + B + ln + R + "\n")
        if ANIM: time.sleep(0.05)
    w(DACC + " " + "═" * 42 + "\n" + R)
    typewriter("  YOUNIC closed. see you soon.\n", GRY, 0.012)
    up = int(time.time() - STATS["start"])
    w(GRY + "  runs: " + WHT + str(STATS["runs"]) + GRY + "  lines: " + WHT + str(STATS["lines"]) +
      GRY + "  uptime: " + WHT + "%ds\n" % up + R)
    w(DACC + " " + "═" * 42 + "\n" + R)

SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
def bar(pct, width=24, color=ACC):
    pct = max(0, min(100, pct))
    fill = int(width * pct / 100)
    return color + "█" * fill + GRY + "░" * (width - fill) + R + " %3d%%" % pct

def box(title, rows, width=None):
    """Draw a bordered panel with label/text rows (NEW)."""
    width = width or min(cols() - 2, 60)
    label_w = max([len(l) for l, _ in rows] + [0]) + 2
    inner = width - 4
    text_w = max(1, inner - label_w)
    k = max(1, width - len(title) - 5)
    w(DACC + "╭─ " + ACC + B + title + R + DACC + " " + "─" * k + "╮" + R + "\n")
    for label, text in rows:
        body = text[:text_w]
        pad = " " * max(0, text_w - len(body))
        w(DACC + "│ " + R + GRY + label.ljust(label_w) + R + WHT + body + R + pad + DACC + " │" + R + "\n")
    w(DACC + "╰" + "─" * (width - 2) + "╯" + R + "\n")

def notify(kind, msg):
    """One-line status message: ok / warn / err / info (NEW)."""
    icon, col = {"ok": ("✔", GRN), "warn": ("⚠", YEL), "err": ("✖", ERR), "info": ("ℹ", ACC)}.get(kind, ("•", GRY))
    w(col + icon + R + " " + msg + "\n")

def show_help():
    """Full command reference screen (NEW)."""
    box("COMMANDS", [
        ("/new", "naya project, history reset"),
        ("/paste", "code paste karke file banayein"),
        ("/open <file>", "projects se file load"),
        ("/show [file]", "file ka code dikhayein"),
        ("/edit [req]", "AI se file edit karayein"),
        ("/fix", "error check + AI fix"),
        ("/run", "file chalayein"),
        ("/loop", "edit loop mode"),
        ("/save", "sdcard mein export"),
        ("/undo", "last backup restore"),
        ("/list", "projects ki list"),
        ("/stats", "session stats"),
        ("/model [name]", "model dekhein / badlein"),
        ("/outdir [path]", "save location"),
        ("/speed [preset]", "typing speed"),
        ("/anim on|off", "animations on / off"),
        ("/key", "API key reset"),
        ("/advise", "code ki advice + selector"),
        ("/menu", "command selector menu"),
        ("/guide", "help & guidance center"),
        ("/about", "app + developer info"),
        ("/clear", "screen saaf + intro animation"),
        ("/tool <naam> <req>", "tool upgrade ya naya banayein"),
        ("/tools", "saare tools ki list"),
        ("/launch <naam>", "tool ko naye terminal mein chalayein"),
        ("/runmode <mode>", "auto|newterm|same|vscode"),
        ("/help", "ye screen"),
        ("/quit", "bahar nikalna"),
    ])

class Loader:
    def __init__(self, label, color=ACC):
        self.label, self.color, self.pct = label, color, 0
        self.run = False; self.t = None
    def _loop(self):
        i = 0
        while self.run:
            w("\r" + self.color + SPIN[i % len(SPIN)] + R + " " + WHT + self.label.ljust(9) + R + " " + bar(self.pct, 20, self.color) + "  ")
            i += 1; time.sleep(0.08)
    def start(self):
        self.run = True
        self.t = threading.Thread(target=self._loop, daemon=True); self.t.start()
    def set(self, p): self.pct = p
    def stop(self, ok=True, note=""):
        self.run = False
        if self.t: self.t.join()
        mark = GRN + "✔" + R if ok else ERR + "✖" + R
        w("\r" + mark + " " + WHT + self.label.ljust(9) + R + " " + bar(100 if ok else self.pct, 20, GRN if ok else ERR) + " " + GRY + note + R + "   \n")

def timed_stage(label, seconds=0.6, color=CYN, ok=True, note=""):
    L = Loader(label, color); L.start()
    for i in range(21):
        L.set(int(100 * i / 20))
        if ANIM: time.sleep(seconds / 20)
    L.stop(ok, note)

def pipeline_panel(state):
    order = ["WRITE", "SAVE", "CHECK", "BUILD", "FIX", "EXPORT"]
    parts = []
    for s in order:
        st = state.get(s, "wait")
        if st == "ok":    parts.append(GRN + "✔ " + s + R)
        elif st == "run": parts.append(YEL + "⠿ " + s + R)
        elif st == "err": parts.append(ERR + "✖ " + s + R)
        elif st == "skip":parts.append(GRY + "– " + s + R)
        else:             parts.append(GRY + "○ " + s + R)
    w("\n" + DACC + "┌" + "─" * 40 + "┐\n" + R)
    w(DACC + "│ " + R + "  ".join(parts[:3]) + "\n")
    w(DACC + "│ " + R + "  ".join(parts[3:]) + "\n")
    w(DACC + "└" + "─" * 40 + "┘\n" + R)

STRIP = {
    "new":  (GRN, DBG_GRN, "▌"),
    "mod":  (YEL, DBG_YEL, "▌"),
    "err":  (ERR, DBG_RED, "▌"),
    "chk":  (CYN, DBG_CYN, "▌"),
    "same": (GRY, "",      "│"),
}
def render_line(n, text, kind="same", width=None):
    fg, bg, ch = STRIP[kind]
    width = width or cols()
    body = text.replace("\t", "  ")[:max(10, width - 9)]
    pad = " " * max(0, width - 8 - len(body))
    if kind == "same":
        return fg + ch + R + GRY + "%4d " % n + R + WHT + body + R
    return fg + B + ch + R + GRY + "%4d " % n + R + bg + WHT + body + pad + R

def type_line(n, text, kind="new"):
    """Reveal a line char-by-char for a live 'typing' effect (record-friendly)."""
    fg, bg, ch = STRIP[kind]
    width = cols()
    body = text.replace("\t", "  ")[:max(10, width - 9)]
    prefix = fg + B + ch + R + GRY + "%4d " % n + R
    delay = 1.0 / TYPE_CPS if (TYPE_CPS > 0 and ANIM) else 0
    if not body:
        w(render_line(n, text, kind) + "\n"); return
    shown = ""
    for c in body:
        shown += c
        w("\r" + prefix + WHT + shown + R + ACC + B + CURSOR + R + "  ")
        if delay: time.sleep(delay)
    w("\r" + render_line(n, text, kind) + "   \n")

def show_file(path, marks=None, start=1, end=None):
    marks = marks or {}
    lines = open(path, errors="ignore").read().split("\n")
    end = end or len(lines)
    w(DACC + "╭─ " + WHT + os.path.basename(path) + GRY + "  (%d lines)\n" % len(lines) + R)
    for i in range(start, min(end, len(lines)) + 1):
        w(render_line(i, lines[i-1], marks.get(i, "same")) + "\n")
    w(DACC + "╰" + "─" * 30 + "\n" + R)

def get_key():
    if os.path.exists(KEYF): return open(KEYF).read().strip()
    k = input(ACC + "[?] API key paste karein: " + R).strip()
    open(KEYF, "w").write(k); os.chmod(KEYF, 0o600)
    return k

def load_model():
    global MODEL
    if os.path.exists(CONFIGF):
        try: MODEL = json.load(open(CONFIGF)).get("model", MODEL)
        except Exception: pass

def save_model(name):
    global MODEL
    MODEL = name
    _save_config({"model": name})

def load_outdir():
    global OUT
    if os.path.exists(CONFIGF):
        try: OUT = json.load(open(CONFIGF)).get("outdir", OUT)
        except Exception: pass

def save_outdir(path):
    global OUT
    OUT = path
    _save_config({"outdir": path})

def load_speed():
    global TYPE_CPS
    if os.path.exists(CONFIGF):
        try: TYPE_CPS = json.load(open(CONFIGF)).get("speed", TYPE_CPS)
        except Exception: pass

def save_speed(cps):
    global TYPE_CPS
    TYPE_CPS = cps
    _save_config({"speed": cps})

def load_anim():
    global ANIM
    if os.path.exists(CONFIGF):
        try: ANIM = bool(json.load(open(CONFIGF)).get("anim", ANIM))
        except Exception: pass

def save_anim(on):
    global ANIM
    ANIM = on
    _save_config({"anim": on})

def _save_config(patch):
    os.makedirs(BASE, exist_ok=True)
    cfg = {}
    if os.path.exists(CONFIGF):
        try: cfg = json.load(open(CONFIGF))
        except Exception: pass
    cfg.update(patch)
    json.dump(cfg, open(CONFIGF, "w"))

def stream_ai(history, key, max_retries=3):
    body = {"systemInstruction": {"parts": [{"text": SYSTEM}]},
            "contents": history,
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8192}}
    data = json.dumps(body).encode()
    for attempt in range(1, max_retries + 1):
        req = urllib.request.Request(STREAM_URL % MODEL, data=data,
              headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                for raw in r:
                    line = raw.decode("utf-8", "ignore").strip()
                    if not line.startswith("data:"): continue
                    try:
                        d = json.loads(line[5:].strip())
                        t = d["candidates"][0]["content"]["parts"][0].get("text", "")
                        if t: yield t
                    except Exception: continue
            return
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                wait = 2 ** attempt
                yield "\n@@RETRY@@ HTTP %s, %ss baad retry (%d/%d)\n" % (e.code, wait, attempt, max_retries)
                time.sleep(wait); continue
            yield "\n@@ERROR@@ %s %s" % (e.code, e.read().decode()[:300]); return
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                yield "\n@@RETRY@@ Network error, %ss baad retry (%d/%d)\n" % (wait, attempt, max_retries)
                time.sleep(wait); continue
            yield "\n@@ERROR@@ %s" % e; return
        except Exception as e:
            yield "\n@@ERROR@@ %s" % e; return

def extract(text):
    name = "output.txt"
    m = re.search(r"FILENAME:\s*([\w.\-]+)", text)
    if m: name = m.group(1)
    c = re.search(r"```[a-zA-Z+]*\n(.*?)(```|$)", text, re.S)
    code = c.group(1) if c else text
    return name, code.rstrip("\n") + "\n"

def live_write(history, key, old_code=None):
    full = ""; buf = ""; ln = 0; in_code = False
    old_lines = old_code.split("\n") if old_code else []
    w("\n")
    net_trace()
    L = Loader("WRITE", ACC); L.start()
    if ANIM: time.sleep(0.25)
    L.stop(True, "stream shuru")
    w(DACC + "╭─ " + WHT + "LIVE CODE" + GRY + "  strip: " + GRN + "▌new " + YEL + "▌changed " + GRY + "│same\n" + R)
    for chunk in stream_ai(history, key):
        if "@@ERROR@@" in chunk: return None, chunk
        if "@@RETRY@@" in chunk:
            w(YEL + chunk.replace("@@RETRY@@", "").strip() + R + "\n")
            continue
        full += chunk; buf += chunk
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            if line.strip().startswith("```"):
                in_code = not in_code; continue
            if not in_code or line.startswith("FILENAME:"): continue
            ln += 1
            if old_code is None: kind = "new"
            elif ln <= len(old_lines) and old_lines[ln-1] == line: kind = "same"
            elif line in old_lines: kind = "mod"
            else: kind = "new"
            if kind == "same":
                w(render_line(ln, line, kind) + "\n")
            else:
                type_line(ln, line, kind)
            STATS["lines"] += 1
    w(DACC + "╰" + "─" * 30 + "\n" + R)
    return full, None

def show_diff(old, new):
    o, n = old.split("\n"), new.split("\n")
    sm = difflib.SequenceMatcher(None, o, n)
    added = removed = 0
    w("\n" + DACC + "╭─ " + WHT + "DIFF" + GRY + "  (old vs new)\n" + R)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        for k, x in enumerate(o[i1:i2]):
            w(ERR + B + "▌" + R + GRY + "%4d " % (i1 + k + 1) + R + DBG_RED + ERR + STRIKE + x[:cols()-9] + R + "\n"); removed += 1
        for k, x in enumerate(n[j1:j2]):
            w(GRN + B + "▌" + R + GRY + "%4d " % (j1 + k + 1) + R + DBG_GRN + WHT + x[:cols()-9] + R + "\n"); added += 1
        if ANIM: time.sleep(0.02)
    w(DACC + "╰" + R + GRY + " +%d / -%d lines\n" % (added, removed) + R)

def parse_error_lines(log, path):
    base = os.path.basename(path)
    nums = set()
    for m in re.finditer(r'File "[^"]*%s", line (\d+)' % re.escape(base), log):
        nums.add(int(m.group(1)))
    for m in re.finditer(r"%s:(\d+):(\d+)?" % re.escape(base), log):
        nums.add(int(m.group(1)))
    return sorted(nums)

def debug_view(path, log):
    nums = parse_error_lines(log, path)
    lines = open(path, errors="ignore").read().split("\n")
    w("\n" + ACC + B + "╭─ DEBUGGER " + R + GRY + "error lines: " + (", ".join(map(str, nums)) or "n/a") + "\n" + R)
    if nums:
        shown = set()
        for e in nums[:4]:
            for i in range(max(1, e - 2), min(len(lines), e + 2) + 1):
                if i in shown: continue
                shown.add(i)
                w(render_line(i, lines[i-1], "err" if i == e else "same") + "\n")
                if i == e:
                    msg = ""
                    for ln in log.split("\n"):
                        if "error" in ln.lower():
                            msg = ln.strip(); break
                    w(ERR + " " * 6 + "└─► " + msg[:cols()-12] + R + "\n")
            w(GRY + "  ···\n" + R)
    else:
        for ln in log.strip().split("\n")[:12]:
            c = ERR if ("error" in ln.lower() or "Traceback" in ln) else YEL if "warning" in ln.lower() else GRY
            w(ERR + "▌" + R + " " + c + ln[:cols()-4] + R + "\n")
    w(DACC + "╰" + "─" * 30 + "\n" + R)

SIMPLE_CHECK = {
    ".py":  (["python", "-m", "py_compile", "{f}"], "python"),
    ".c":   (["clang", "-fsyntax-only", "-Wall", "{f}"], "clang"),
    ".cpp": (["clang++", "-std=c++17", "-fsyntax-only", "-Wall", "{f}"], "clang"),
    ".js":  (["node", "--check", "{f}"], "nodejs"),
    ".mjs": (["node", "--check", "{f}"], "nodejs"),
    ".ts":  (["tsc", "--noEmit", "{f}"], "typescript (npm i -g typescript)"),
    ".sh":  (["bash", "-n", "{f}"], None),
    ".php": (["php", "-l", "{f}"], "php"),
    ".rb":  (["ruby", "-c", "{f}"], "ruby"),
    ".pl":  (["perl", "-c", "{f}"], "perl"),
    ".lua": (["luac", "-p", "{f}"], "lua"),
    ".go":  (["gofmt", "-e", "{f}"], "golang"),
}

def _run_cmd(cmd_template, path, pkg_hint, timeout=25):
    cmd = [c.replace("{f}", path) for c in cmd_template]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (p.returncode == 0), (p.stderr or p.stdout)
    except FileNotFoundError:
        hint = (" (pkg install %s)" % pkg_hint) if pkg_hint else ""
        return False, "%s installed nahi hai%s" % (cmd[0], hint)
    except subprocess.TimeoutExpired:
        return True, ""

def _test_run(cmd, timeout=5):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, input="")
        if p.returncode != 0 and p.stderr.strip():
            return False, p.stderr
    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError as e:
        return False, "%s installed nahi hai" % cmd[0]
    return True, ""

def check_only(path):
    ext = os.path.splitext(path)[1]
    if ext in (".html", ".htm"):
        src = open(path, errors="ignore").read(); low = src.lower(); probs = []
        if "<html" not in low: probs.append("%s:1: error: <html> tag missing" % os.path.basename(path))
        for t in ("script", "style", "body", "div"):
            a, b = low.count("<" + t), low.count("</" + t + ">")
            if a != b: probs.append("%s:1: error: <%s> tags unbalanced (%d open, %d close)" % (os.path.basename(path), t, a, b))
        return (not probs), "\n".join(probs)
    if ext == ".java":
        d = os.path.dirname(path) or "."
        return _run_cmd(["javac", "-d", d, "{f}"], path, "openjdk-17", timeout=30)
    if ext == ".rs":
        return _run_cmd(["rustc", "--edition", "2021", "--emit=metadata", "-o", "/tmp/_younic_rustcheck.rmeta", "{f}"],
                         path, "rust", timeout=30)
    if ext in SIMPLE_CHECK:
        cmd, pkg = SIMPLE_CHECK[ext]
        return _run_cmd(cmd, path, pkg, timeout=30)
    return True, ""

def build(path):
    ext = os.path.splitext(path)[1]
    if ext == ".py":
        return _test_run(["python", path])
    if ext == ".c":
        p = subprocess.run(["clang", "-Wall", path, "-o", path[:-2]], capture_output=True, text=True)
        return (p.returncode == 0), p.stderr
    if ext == ".cpp":
        p = subprocess.run(["clang++", "-std=c++17", "-Wall", path, "-o", path[:-4]], capture_output=True, text=True)
        return (p.returncode == 0), p.stderr
    if ext in (".js", ".mjs"):
        return _test_run(["node", path])
    if ext == ".sh":
        p = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
        return (p.returncode == 0), p.stderr
    if ext == ".php":
        return _test_run(["php", path])
    if ext == ".rb":
        return _test_run(["ruby", path])
    if ext == ".pl":
        return _test_run(["perl", path])
    if ext == ".lua":
        return _test_run(["lua", path])
    if ext == ".go":
        try:
            env = dict(os.environ, GO111MODULE="off")
            p = subprocess.run(["go", "run", path], capture_output=True, text=True, timeout=15, env=env)
            if p.returncode != 0: return False, p.stderr
        except subprocess.TimeoutExpired: pass
        except FileNotFoundError: return False, "golang installed nahi hai (pkg install golang)"
        return True, ""
    if ext == ".rs":
        out = path[:-3]
        p = subprocess.run(["rustc", "--edition", "2021", "-O", path, "-o", out], capture_output=True, text=True)
        if p.returncode != 0: return False, p.stderr
        try:
            p2 = subprocess.run([out], capture_output=True, text=True, timeout=5)
            if p2.returncode != 0 and p2.stderr.strip(): return False, p2.stderr
        except subprocess.TimeoutExpired: pass
        except FileNotFoundError: pass
        return True, ""
    if ext == ".java":
        d = os.path.dirname(path) or "."
        cls = os.path.splitext(os.path.basename(path))[0]
        p = subprocess.run(["javac", "-d", d, path], capture_output=True, text=True)
        if p.returncode != 0: return False, p.stderr
        try:
            p2 = subprocess.run(["java", "-cp", d, cls], capture_output=True, text=True, timeout=5)
            if p2.returncode != 0 and p2.stderr.strip(): return False, p2.stderr
        except subprocess.TimeoutExpired: pass
        except FileNotFoundError: return False, "openjdk installed nahi hai (pkg install openjdk-17)"
        return True, ""
    if ext == ".ts":
        tmp = path + ".out.js"
        try:
            p = subprocess.run(["tsc", "--target", "es2020", "--outFile", tmp, path], capture_output=True, text=True)
            if p.returncode != 0: return False, p.stderr
            p2 = subprocess.run(["node", tmp], capture_output=True, text=True, timeout=5)
            if p2.returncode != 0 and p2.stderr.strip(): return False, p2.stderr
        except subprocess.TimeoutExpired: pass
        except FileNotFoundError: return False, "typescript installed nahi hai (npm i -g typescript)"
        return True, ""
    return True, ""

def backup(path):
    if os.path.exists(path):
        os.makedirs(BAK, exist_ok=True)
        dst = os.path.join(BAK, "%s.%d.bak" % (os.path.basename(path), int(time.time())))
        shutil.copy(path, dst); return dst

def export(path):
    dst = os.path.join(OUT, os.path.basename(path))
    scan_path(dst, "SYNC")
    L = Loader("EXPORT", GRN); L.start()
    try:
        os.makedirs(OUT, exist_ok=True)
        for i in range(0, 101, 10):
            L.set(i)
            if ANIM: time.sleep(0.03)
        shutil.copy(path, dst)
        L.stop(True, dst)
        return True
    except Exception as e:
        L.stop(False, "termux-setup-storage chalayein")
        return False

def pipeline(history, key, old_code=None):
    state = {}
    state["WRITE"] = "run"; pipeline_panel(state)
    full, err = live_write(history, key, old_code)
    if err:
        state["WRITE"] = "err"; pipeline_panel(state)
        w(ERR + err + R + "\n"); return None
    name, code = extract(full)
    history.append({"role": "model", "parts": [{"text": full}]})
    state["WRITE"] = "ok"
    if old_code is not None: show_diff(old_code, code)

    os.makedirs(PROJ, exist_ok=True)
    path = os.path.join(PROJ, name)
    backup(path)
    scan_path(path, "SAVE")
    timed_stage("SAVE", 0.3, GRN, True, "%d bytes" % len(code))
    open(path, "w").write(code); state["SAVE"] = "ok"

    ok = False
    for attempt in range(1, 4):
        timed_stage("CHECK", 0.6, CYN, True, "syntax scan")
        ok, log = check_only(path)
        if ok:
            state["CHECK"] = "ok"
            L = Loader("BUILD", CYN); L.start()
            for i in range(0, 101, 5):
                L.set(i)
                if ANIM: time.sleep(0.03)
            ok, log = build(path)
            L.stop(ok, "compile/interpret")
            if ok: state["BUILD"] = "ok"; break
            state["BUILD"] = "err"
        else:
            state["CHECK"] = "err"
        debug_view(path, log)
        state["FIX"] = "run"; STATS["fixes"] += 1
        w(YEL + "[FIX] AI se fix ho raha hai (attempt %d/3)\n" % attempt + R)
        history.append({"role": "user", "parts": [{"text":
            "Yeh error aaya. Poori fixed file do (same format):\n" + log[:1800]}]})
        old = code
        full, err = live_write(history, key, old)
        if err: state["FIX"] = "err"; w(ERR + err + R + "\n"); break
        history.append({"role": "model", "parts": [{"text": full}]})
        _, code = extract(full)
        show_diff(old, code)
        open(path, "w").write(code)
        state["FIX"] = "ok"
    if ok:
        notify("ok", GRN + B + "PASS: sab checks clear" + R)
    else:
        notify("warn", YEL + "3 attempts ke baad bhi error. /fix ya /edit se dobara try karein" + R)
    if not state.get("BUILD"): state["BUILD"] = "skip" if ok else "err"
    state["EXPORT"] = "ok" if export(path) else "err"
    pipeline_panel(state)
    STATS["runs"] += 1
    return path

def run_file(path):
    ext = os.path.splitext(path)[1]
    w(CYN + B + "\n[EXEC] " + R + os.path.basename(path) + "\n" + DACC + "─" * 30 + R + "\n")
    try:
        if ext == ".py":
            env = dict(os.environ, PYTHONPATH=os.path.join(os.path.dirname(path), "lib") + os.pathsep + os.environ.get("PYTHONPATH", ""))
            subprocess.call([sys.executable, path], cwd=os.path.dirname(path), env=env)
        elif ext == ".c":
            exe = path[:-2]
            if not os.path.exists(exe): build(path)
            subprocess.call([exe])
        elif ext == ".cpp":
            exe = path[:-4]
            if not os.path.exists(exe): build(path)
            subprocess.call([exe])
        elif ext in (".html", ".htm"):
            subprocess.call(["termux-open", path])
        elif ext in (".js", ".mjs"):
            subprocess.call(["node", path])
        elif ext == ".sh":
            subprocess.call(["bash", path])
        elif ext == ".php": subprocess.call(["php", path])
        elif ext == ".rb": subprocess.call(["ruby", path])
        elif ext == ".pl": subprocess.call(["perl", path])
        elif ext == ".lua": subprocess.call(["lua", path])
        elif ext == ".go":
            env = dict(os.environ, GO111MODULE="off")
            subprocess.call(["go", "run", path], env=env)
        elif ext == ".rs":
            out = path[:-3]
            if not os.path.exists(out):
                subprocess.run(["rustc", "--edition", "2021", "-O", path, "-o", out])
            subprocess.call([out])
        elif ext == ".java":
            d = os.path.dirname(path) or "."
            cls = os.path.splitext(os.path.basename(path))[0]
            subprocess.run(["javac", "-d", d, path])
            subprocess.call(["java", "-cp", d, cls])
        elif ext == ".ts":
            tmp = path + ".out.js"
            subprocess.run(["tsc", "--target", "es2020", "--outFile", tmp, path])
            subprocess.call(["node", tmp])
    except Exception as e:
        w(ERR + str(e) + R + "\n")

def multiline(prompt):
    w(YEL + prompt + "\n(khatam karne ke liye nayi line par END)\n" + R)
    out = []
    while True:
        try: l = input()
        except EOFError: break
        if l.strip() == "END": break
        out.append(l)
    return "\n".join(out) + "\n"

def edit_loop(history, key, current):
    if not current or not os.path.exists(current):
        notify("warn", "Pehle /open ya /paste se file load karein")
        return current
    w(DACC + " " + "═" * 42 + "\n" + R)
    w(GRY + "  [ LOOP MODE ] " + WHT + os.path.basename(current) + R + "\n" + R)
    w(GRY + "  Change likhein, ya: preview | save | quit\n" + R)
    w(DACC + " " + "═" * 42 + "\n" + R)
    while True:
        try:
            req = input(ACC + B + "edit" + R + GRY + "@loop" + R + ACC + " ❯ " + R).strip()
        except (EOFError, KeyboardInterrupt):
            w("\n"); break
        if not req: continue
        if req in ("quit", "/quit", "exit"):
            notify("info", "Loop band. (Save nahi hua ho to /loop se dobara aa sakte hain)")
            break
        if req in ("preview", "/preview", "show"):
            show_file(current); continue
        if req in ("save", "/save"):
            if export(current):
                notify("ok", GRN + B + "Saved to local storage: " + R + os.path.join(OUT, os.path.basename(current)))
            break
        old = open(current).read()
        edit_history = [{"role": "user", "parts": [{"text":
            "FILENAME: %s\nExisting code:\n```\n%s```\nIsme yeh change karo aur poori updated file do (same format):\n%s" %
            (os.path.basename(current), old, req)}]}]
        r = pipeline(edit_history, key, old)
        if r:
            current = r
            show_file(current)
            w(GRY + "Aur change likhein, ya 'preview' / 'save' / 'quit'\n" + R)
    return current

def pulse_title(text, seconds=1.0, fps=12):
    """Green pulsing title line (NEW animation)."""
    if not ANIM:
        w(ACC + B + text + R + "\n"); return
    w("\033[?25l")
    try:
        for f in range(int(seconds * fps)):
            row = "".join(sh(SHADES[(x + f) % len(SHADES)]) + B + c for x, c in enumerate(text))
            w("\r" + row + R)
            time.sleep(1.0 / fps)
        w("\n")
    finally:
        w("\033[?25h")

def radar_sweep(label="SCAN", seconds=0.8, fps=12):
    """Rotating radar glyph with a growing green bar (NEW animation)."""
    glyphs = "◐◓◑◒"
    w("\033[?25l")
    try:
        frames = int(seconds * fps) if ANIM else 0
        for f in range(frames):
            pct = int(100 * (f + 1) / frames)
            w("\r" + ACC + glyphs[f % 4] + R + " " + WHT + label.ljust(8) + R + " " + shade_bar(pct, 18))
            time.sleep(1.0 / fps)
        w("\r" + GRN + "✔" + R + " " + WHT + label.ljust(8) + R + " " + shade_bar(100, 18) + "\n")
    finally:
        w("\033[?25h")

def run_with_spinner(label, fn, color=CYN):
    """Run real work in a thread while a spinner shows. Returns fn()'s result (NEW)."""
    result = {}
    def worker():
        try: result["v"] = fn()
        except Exception as e: result["e"] = e
    t = threading.Thread(target=worker, daemon=True); t.start()
    i = 0
    while t.is_alive():
        if ANIM:
            w("\r" + color + SPIN[i % len(SPIN)] + R + " " + WHT + label.ljust(9) + R + GRY + " working..." + R)
        i += 1
        time.sleep(0.08 if ANIM else 0.1)
    t.join()
    if "e" in result:
        w("\r" + ERR + "✖" + R + " " + WHT + label.ljust(9) + R + " " + ERR + str(result["e"]) + R + "\n")
        return None
    w("\r" + GRN + "✔" + R + " " + WHT + label.ljust(9) + R + GRN + " done" + R + "            \n")
    return result.get("v")

def select_menu(title, options):
    """Numbered selector panel. Returns chosen index or None on Enter/cancel (NEW)."""
    box(title, [(str(i + 1), opt) for i, opt in enumerate(options)])
    while True:
        try:
            pick = input(ACC + B + "select" + R + GRY + " (number, Enter = cancel) ❯ " + R).strip()
        except (EOFError, KeyboardInterrupt):
            w("\n"); return None
        if not pick: return None
        if pick.isdigit() and 1 <= int(pick) <= len(options):
            return int(pick) - 1
        notify("warn", "1 se %d ke beech number likhein" % len(options))

def analyze_code(path):
    """Local static analysis, no API call. Returns list of (severity, line, message) (NEW)."""
    src = open(path, errors="ignore").read()
    findings = []
    for i, ln in enumerate(src.split("\n"), 1):
        if len(ln) > 100:
            findings.append(("info", i, "line 100 characters se lambi hai"))
        if re.search(r"\b(TODO|FIXME)\b", ln):
            findings.append(("info", i, "TODO/FIXME mila"))
    if not path.endswith(".py"):
        return findings
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [("err", e.lineno or 0, "syntax error: %s" % e.msg)]
    if "__name__" not in src or "__main__" not in src:
        findings.append(("warn", 0, "if __name__ == '__main__' guard nahi hai"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(("warn", node.lineno, "bare except: specific exception likhein"))
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) in ("eval", "exec"):
            findings.append(("warn", node.lineno, "eval/exec security risk hai"))
        if isinstance(node, ast.FunctionDef):
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            if length > 60:
                findings.append(("info", node.lineno, "%s() %d lines ka hai, chhote functions behtar" % (node.name, length)))
            if length > 15 and not ast.get_docstring(node):
                findings.append(("info", node.lineno, "%s() ka docstring nahi" % node.name))
    return sorted(findings, key=lambda f: ({"err": 0, "warn": 1, "info": 2}[f[0]], f[1]))

def show_advice(findings):
    if not findings:
        notify("ok", "Qoder: koi masla nahi mila, code saaf lag raha hai")
        return
    icons = {"err": "✖", "warn": "⚠", "info": "ℹ"}
    rows = [("%s L%d" % (icons[s], ln), msg) for s, ln, msg in findings[:12]]
    box("ADVICE", rows)
    if len(findings) > 12:
        w(GRY + "  ...aur %d points\n" % (len(findings) - 12) + R)

def ai_review(path, key):
    """Ask the AI for a short Roman Urdu review. Uses the API (NEW)."""
    src = open(path, errors="ignore").read()
    hist = [{"role": "user", "parts": [{"text":
        "FILENAME: %s\nCode:\n```\n%s```\nIs code ka review karo. Roman Urdu mein 5 short points do: "
        "bugs, security, performance, aur behtar tareeqa. Code mat likho." % (os.path.basename(path), src)}]}]
    w("\n" + ACC + B + "╭─ QODER ADVICE" + R + "\n")
    delay = 1.0 / TYPE_CPS if (TYPE_CPS > 0 and ANIM) else 0
    for chunk in stream_ai(hist, key):
        if "@@ERROR@@" in chunk:
            notify("err", chunk.replace("@@ERROR@@", "").strip()); return
        if "@@RETRY@@" in chunk:
            w(YEL + chunk.replace("@@RETRY@@", "").strip() + R + "\n"); continue
        for c in chunk:
            w(WHT + c + R)
            if delay: time.sleep(delay)
    w("\n" + DACC + "╰" + "─" * 30 + "\n" + R)

def qoder_advise(path, key):
    """/advise: local analysis, advice panel, then a selector for the next step (NEW).
    Returns the new file path if the AI changed the file, else None."""
    if not path or not os.path.exists(path):
        notify("warn", "Pehle /open ya /paste se file load karein")
        return None
    findings = run_with_spinner("ANALYZE", lambda: analyze_code(path))
    if findings is None:
        return None
    show_advice(findings)
    choice = select_menu("NEXT STEP", [
        "AI se fix karwao (file change hogi, backup banega)",
        "AI se detailed review (sirf dekhne ke liye)",
        "Sirf report rakho, koi change nahi",
    ])
    if choice == 0:
        req = "Ye advice follow karo aur code sudhar do (poori file, same format):\n" + "\n".join(
            "L%d: %s" % (ln, msg) for _, ln, msg in findings)
        old = open(path).read()
        history = [{"role": "user", "parts": [{"text":
            "FILENAME: %s\nExisting code:\n```\n%s```\n%s" % (os.path.basename(path), old, req)}]}]
        return pipeline(history, key, old)
    if choice == 1:
        ai_review(path, key)
    return None

MENU_ITEMS = [
    ("/new", "naya project"),
    ("/paste", "code paste karein"),
    ("/open", "projects se file kholen"),
    ("/edit", "AI se file edit karein"),
    ("/advise", "Qoder advice + selector"),
    ("/guide", "help & guidance center"),
    ("/about", "app + developer info"),
    ("/fix", "error check + fix"),
    ("/run", "file chalayein"),
    ("/help", "saari commands"),
    ("/quit", "bahar nikalein"),
]

def pick_menu():
    """/menu: selector of common actions. Returns the command string or None (NEW)."""
    pulse_title("▸ YOUNIC MENU", 0.8)
    idx = select_menu("YOUNIC MENU", ["%s  %s" % (c.ljust(8), d) for c, d in MENU_ITEMS])
    if idx is None:
        return None
    cmd = MENU_ITEMS[idx][0]
    if cmd == "/open":
        name = input(ACC + "[?] file ka naam: " + R).strip()
        return "/open " + name if name else None
    return cmd

# ================= TOOL SYSTEM (NEW) =================
UPGRADE_WORDS = ("upgrade", "update", "improve", "badlo", "behtar", "sudhar")
FILE_RE = re.compile(r"FILENAME:\s*([^\s`]+)\s*```[^\n]*\n(.*?)```", re.S)

def read_text(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()

def write_text(p, code):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(code)

def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:40] or "tool"

def tool_dir(name):
    return os.path.join(TOOLS_DIR, name)

def load_registry():
    """Tool memory: returns {name: info}. Keeps a copy if the file is damaged (NEW)."""
    if os.path.exists(REGISTRY):
        try:
            with open(REGISTRY, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            notify("warn", "registry.json padh nahi paya, broken copy save ki hai")
            try: shutil.copy(REGISTRY, REGISTRY + ".broken")
            except Exception: pass
    return {}

def save_registry(reg):
    os.makedirs(TOOLS_DIR, exist_ok=True)
    tmp = REGISTRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, REGISTRY)

def unique_name(base, reg):
    name, n = base, 2
    while name in reg or os.path.exists(tool_dir(name)):
        name = "%s_%d" % (base, n); n += 1
    return name

def safe_rel(name):
    """Blocks absolute paths and '..' so files stay inside the tool folder."""
    parts = [p for p in name.replace("\\", "/").split("/") if p not in ("", ".")]
    if not parts or ".." in parts or name.startswith("/"):
        return None
    return "/".join(parts)

def extract_files(text):
    """Parse one or many 'FILENAME: path' + code block pairs (NEW)."""
    out = []
    for m in FILE_RE.finditer(text):
        rel = safe_rel(m.group(1))
        if rel:
            out.append((rel, m.group(2).rstrip("\n") + "\n"))
    if not out:
        name, code = extract(text)
        out = [(safe_rel(name) or "main.py", code)]
    return out

def ask_ai(history, key):
    """Collect the full AI answer, raise on API error (NEW)."""
    parts = []
    for chunk in stream_ai(history, key):
        if "@@ERROR@@" in chunk:
            raise RuntimeError(chunk.replace("@@ERROR@@", "").strip())
        if "@@RETRY@@" in chunk:
            continue
        parts.append(chunk)
    return "".join(parts)

def plan_tool(request, key, existing=None):
    """Step 1 of a long project: ask for a file list only (NEW)."""
    prompt = ("Is request ke liye project ka file plan banao. Sirf plan do, code nahi. "
              "Har line exactly is format mein: FILE: relative/path | ek line purpose. "
              "Pehli file entry point honi chahiye. Max 12 files. Dependencies ho to requirements.txt bhi list karo. "
              "Program non-interactive ho, input() na ho.\n")
    if existing:
        prompt += "Existing files (ye upgrade hai): " + ", ".join(existing) + "\n"
    prompt += "REQUEST: " + request
    text = ask_ai([{"role": "user", "parts": [{"text": prompt}]}], key)
    plan, seen = [], set()
    for m in re.finditer(r"FILE:\s*([^\s|]+)\s*\|\s*(.+)", text):
        rel = safe_rel(m.group(1).strip("`"))
        if rel and rel not in seen:
            seen.add(rel)
            plan.append((rel, m.group(2).strip()))
    return plan[:12]

def gen_file(rel, purpose, plan, done, request, key, old=None):
    """Step 2: write ONE file of the plan, with earlier files as context (NEW)."""
    prompt = "PROJECT REQUEST: %s\n\nFILE PLAN:\n%s\n\n" % (request, "\n".join("%s | %s" % p for p in plan))
    if done:
        ctx = "\n\n".join("FILENAME: %s\n```\n%s```" % (n, c) for n, c in done.items())
        prompt += "ALREADY WRITTEN FILES (inke saath consistent raho):\n%s\n\n" % ctx[-12000:]
    if old is not None:
        prompt += "EXISTING VERSION of %s (upgrade karna hai, behtar karo):\n```\n%s```\n\n" % (rel, old[:12000])
    prompt += ("Ab sirf file '%s' likho (%s). Format: FILENAME: %s aur phir ek fenced code block. "
               "Poori file likho, koi placeholder nahi. Program non-interactive ho." % (rel, purpose, rel))
    files = extract_files(ask_ai([{"role": "user", "parts": [{"text": prompt}]}], key))
    for n, c in files:
        if n == rel:
            return c
    return files[0][1]

def write_tool_file(tdir, rel, code, backup_root=None):
    full = os.path.join(tdir, rel)
    if backup_root and os.path.exists(full):
        dst = os.path.join(backup_root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(full, dst)
    write_text(full, code)

def install_requirements(tdir):
    """Installs requirements.txt into tools/<name>/lib, not the global Python (NEW)."""
    req = os.path.join(tdir, "requirements.txt")
    if not os.path.exists(req):
        return True, ""
    try:
        p = subprocess.run([sys.executable, "-m", "pip", "install", "-r", req,
                            "--target", os.path.join(tdir, "lib"), "--quiet"],
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False, "pip install timeout"
    return p.returncode == 0, (p.stderr or "")[-800:]

def test_tool(tdir, rel, files):
    """Syntax-check every Python file, then run the entry file (NEW).
    A Python tool that is still running after 8s counts as OK (GUI/server tools)."""
    for f in files:
        if f.endswith(".py"):
            ok, log = check_only(os.path.join(tdir, f))
            if not ok:
                return False, log
    path = os.path.join(tdir, rel)
    if rel.endswith(".py"):
        env = dict(os.environ)
        env["PYTHONPATH"] = os.path.join(tdir, "lib") + os.pathsep + env.get("PYTHONPATH", "")
        try:
            p = subprocess.run([sys.executable, path], cwd=tdir, env=env, capture_output=True,
                               text=True, timeout=8, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return True, ""
        if p.returncode != 0:
            return False, ((p.stderr or p.stdout) or "exit code %d" % p.returncode)[-2000:]
        return True, ""
    if rel.endswith((".html", ".htm")):
        return check_only(path)
    return build(path)

def fix_tool(request, key, tdir, files, log):
    """Auto-fix: AI gets all tool files and the error, returns only changed files (NEW)."""
    snap = "\n\n".join("FILENAME: %s\n```\n%s```" % (f, read_text(os.path.join(tdir, f))[:8000])
                       for f in files if os.path.exists(os.path.join(tdir, f)))
    prompt = ("PROJECT REQUEST: %s\n\nPROJECT FILES:\n%s\n\nERROR:\n%s\n\n"
              "Error fix karo. Sirf jo files badalni hain unhe likho: FILENAME: path aur poori file ka code block. "
              "Program non-interactive ho." % (request, snap[:30000], log[:1800]))
    return extract_files(ask_ai([{"role": "user", "parts": [{"text": prompt}]}], key))

def route_request(text, reg):
    """Upgrade only when an existing tool name AND an upgrade word are both in the message (NEW)."""
    low = text.lower()
    if any(k in low for k in UPGRADE_WORDS):
        for name in reg:
            if name in low or name.replace("_", " ") in low:
                return name, True
    return None, False

def preview_code(rel, code, limit=20):
    """Shows the first `limit` lines of a file so you can follow along; the full file is saved (NEW)."""
    lines = code.rstrip("\n").split("\n")
    total = len(lines)
    w(DACC + "╭─ " + WHT + rel + GRY + "  (%d lines, preview %d)\n" % (total, min(limit, total)) + R)
    for i, ln in enumerate(lines[:limit], 1):
        w(render_line(i, ln, "new") + "\n")
    if total > limit:
        w(GRY + "  ··· +%d lines file mein save ho gayi hain\n" % (total - limit) + R)
    w(DACC + "╰" + "─" * 30 + "\n" + R)

def build_tool(request, key, name=None, upgrade=False):
    """Create a new tool from zero, or upgrade an existing one (NEW)."""
    reg = load_registry()
    if upgrade:
        if name not in reg:
            notify("err", "Tool nahi mila: %s" % name); return None
        tdir = tool_dir(name)
        version = reg[name].get("version", 1)
        old_files = [f for f in reg[name].get("files", []) if os.path.exists(os.path.join(tdir, f))]
        old_texts = {f: read_text(os.path.join(tdir, f)) for f in old_files}
        notify("info", "Upgrade mode: %s (v%d)" % (name, version))
    else:
        name = unique_name(name or slugify(" ".join(request.split()[:4])), reg)
        tdir, version, old_files, old_texts = tool_dir(name), 0, [], {}
        notify("info", "Naya tool bana raha hoon: %s" % name)

    plan = run_with_spinner("PLAN", lambda: plan_tool(request, key, old_files))
    if not plan:
        notify("err", "AI ne file plan nahi di, dobara try karein"); return None
    box("TOOL PLAN: " + name, plan)

    os.makedirs(tdir, exist_ok=True)
    backup_root = os.path.join(tdir, ".backup_" + (("v%d" % version) if upgrade else "initial"))
    done = {}
    for rel, purpose in plan:
        notify("info", "Writing " + rel)
        code = run_with_spinner("WRITE", lambda r=rel, p=purpose, o=old_texts.get(rel):
                                gen_file(r, p, plan, done, request, key, o))
        if code is None:
            return None
        done[rel] = code
        preview_code(rel, code)
    written = []
    for rel, code in done.items():
        write_tool_file(tdir, rel, code, backup_root)
        written.append(rel)

    ok, log = run_with_spinner("INSTALL", lambda: install_requirements(tdir)) or (False, "install crash")
    if not ok:
        notify("warn", "Install problem: " + log[-200:])

    entry = plan[0][0]
    ok = False
    for attempt in range(1, 4):
        ok, log = run_with_spinner("TEST", lambda: test_tool(tdir, entry, written)) or (False, "test crash")
        if ok:
            break
        debug_view(os.path.join(tdir, entry), log) if os.path.exists(os.path.join(tdir, entry)) else None
        if attempt == 3:
            break
        notify("warn", "Auto-fix attempt %d/2" % attempt)
        STATS["fixes"] += 1
        fixed = run_with_spinner("FIX", lambda: fix_tool(request, key, tdir, written, log))
        if not fixed:
            break
        fix_root = os.path.join(tdir, ".backup_fix")
        for rel, code in fixed:
            write_tool_file(tdir, rel, code, fix_root)
            preview_code(rel, code)
            if rel not in written:
                written.append(rel)

    files = sorted(set(old_files) | set(written))
    reg[name] = {
        "path": tdir, "entry": entry, "files": files,
        "version": version + 1 if upgrade else 1,
        "description": request[:160],
        "updated": time.strftime("%Y-%m-%d %H:%M"),
        "status": "ok" if ok else "needs-fix",
    }
    save_registry(reg)
    try:
        if "README.md" not in files:
            files = sorted(set(files) | {write_tool_readme(tdir, name, request, reg[name]["version"], entry, files, ok)})
            reg[name]["files"] = files; save_registry(reg)
        else:
            write_tool_readme(tdir, name, request, reg[name]["version"], entry, files, ok)
    except OSError as e:
        notify("warn", "README likh nahi paya: %s" % e)
    box("TOOL DONE: " + name, [
        ("status", "ok" if ok else "needs-fix (manually check karein)"),
        ("version", str(reg[name]["version"])),
        ("entry", os.path.join(tdir, entry)),
        ("files", str(len(files))),
    ])
    if ok:
        notify("ok", "Tool test pass ho gaya, ab naye terminal mein chala kar dekhte hain")
        launch_tool(tdir, entry)
    else:
        notify("warn", "Test pass nahi hua, isliye naye terminal mein nahi chalaya. Theek hone ke baad /launch %s se chalayein" % name)
    STATS["runs"] += 1
    return os.path.join(tdir, entry)

def is_termux():
    return "com.termux" in os.environ.get("PREFIX", "")

def run_mode():
    """auto | newterm | same | vscode  (set with /runmode)."""
    try:
        with open(CONFIGF, encoding="utf-8") as f:
            return json.load(f).get("runmode", "auto")
    except Exception:
        return "auto"

def make_run_script(tdir, entry):
    """Writes run_tool.bat (Windows) or run_tool.sh (Linux/Termux) inside the tool folder (NEW)."""
    path = os.path.join(tdir, entry)
    ext = os.path.splitext(entry)[1].lower()
    lib = os.path.join(tdir, "lib")
    if os.name == "nt":
        if ext == ".py": cmd = '"%s" "%s"' % (sys.executable, path)
        elif ext in (".js", ".mjs"): cmd = 'node "%s"' % path
        elif ext in (".html", ".htm"): cmd = 'start "" "%s"' % path
        else: return None
        body = ("@echo off\r\ncd /d \"%s\"\r\nset \"PYTHONPATH=%s;%%PYTHONPATH%%\"\r\n%s\r\n"
                "echo.\r\necho ==== tool finished ====\r\npause\r\n") % (tdir, lib, cmd)
        script = os.path.join(tdir, "run_tool.bat")
    else:
        if ext == ".py": cmd = '"%s" "%s"' % (sys.executable, path)
        elif ext in (".js", ".mjs"): cmd = 'node "%s"' % path
        elif ext in (".html", ".htm"): cmd = 'termux-open "%s" 2>/dev/null || xdg-open "%s"' % (path, path)
        elif ext == ".sh": cmd = 'sh "%s"' % path
        else: return None
        body = ("#!/bin/sh\ncd \"%s\" || exit 1\nPYTHONPATH=\"%s:$PYTHONPATH\" %s\n"
                "echo\necho \"==== tool finished ====\"\nread -r _\n") % (tdir, lib, cmd)
        script = os.path.join(tdir, "run_tool.sh")
    with open(script, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    return script

def launch_tool(tdir, entry):
    """Runs the tool in a NEW terminal where possible, otherwise in the current one (NEW)."""
    script = make_run_script(tdir, entry)
    if not script:
        notify("info", "Ye file type direct run nahi hoti: " + entry); return
    mode = run_mode()
    if mode == "vscode" and shutil.which("code"):
        subprocess.Popen(["code", "-r", tdir])
        notify("ok", "VS Code mein folder khula. Terminal mein chalayein: " + entry); return
    if os.name == "nt" and mode in ("auto", "newterm"):
        w(CYN + B + "[LAUNCH] " + R + GRY + script + R + "\n")
        try:
            os.startfile(script)   # opens the .bat in a new CMD console window
        except Exception:
            try:
                subprocess.Popen('start "YOUNIC Tool" cmd /k "%s"' % script, shell=True)
            except Exception as e:
                notify("err", "Naya window nahi khula: %s" % e)
                notify("info", "Manually chalayein: " + script)
                return
        notify("ok", "Naye CMD window mein tool chal raha hai")
        return
    if os.name != "nt" and mode in ("auto", "newterm") and not is_termux():
        for term in (["x-terminal-emulator", "-e"], ["gnome-terminal", "--"], ["konsole", "-e"], ["xterm", "-e"]):
            if shutil.which(term[0]):
                subprocess.Popen(term + ["sh", script])
                notify("ok", "Naye %s terminal mein tool chal raha hai" % term[0]); return
    notify("info", "Same terminal mein test ho raha hai")
    if os.name == "nt":
        subprocess.call(["cmd", "/c", script])
    else:
        subprocess.call(["sh", script])

def show_tools():
    reg = load_registry()
    if not reg:
        notify("info", "Abhi koi tool nahi bana. Free text mein request likhein."); return
    box("TOOLS (%d)" % len(reg), [
        (n, "v%d %s | %s" % (v.get("version", 1), v.get("status", ""), v.get("description", "")[:50]))
        for n, v in reg.items()])

def stats():
    up = int(time.time() - STATS["start"])
    w(DACC + "╭─ " + WHT + "STATS\n" + R)
    w(GRY + "│ runs: " + WHT + str(STATS["runs"]) + GRY + "  lines: " + WHT + str(STATS["lines"]) +
      GRY + "  auto-fixes: " + WHT + str(STATS["fixes"]) + GRY + "  uptime: " + WHT + "%ds\n" % up + R)
    w(DACC + "╰" + "─" * 30 + "\n" + R)

def _mail_link(addr):
    """Clickable mailto link (OSC 8). Terminals without support still show the plain address."""
    return "\033]8;;mailto:%s\033\\%s\033]8;;\033\\" % (addr, addr)

def show_about():
    """/about: application, developer, version, credits and support info."""
    box("ABOUT " + APP_NAME, [
        ("app", APP_NAME + " - AI Developer Studio"),
        ("version", APP_VERSION),
        ("ai tool", AI_TOOL_NAME + " (built-in AI coding assistant)"),
        ("developer", DEV_NAME),
        ("contact", DEV_EMAIL),
        ("model", MODEL),
        ("platform", "Termux / Linux / Windows (terminal)"),
        ("warning", "Education only; generated code is untrusted and unsandboxed"),
    ])
    w(GRY + "  email: " + ACC + _mail_link(DEV_EMAIL) + R + "\n")
    w(GRY + "  credits: " + DEV_NAME + " - built on Python standard library.\n")
    w(GRY + "  support: send your problem with the command you ran and the error text.\n")
    w(GRY + "  AI tools created inside " + APP_NAME + " are not officially verified or\n"
      "  published by " + DEV_NAME + ". Review them before use.\n" + R)

GUIDE_TOPICS = [
    ("Getting started", [
        "Termux setup — run these commands in Termux, one at a time:",
        "pkg update -y && pkg upgrade -y",
        "pkg install -y python git",
        "cd ~",
        "git clone https://github.com/termuxofficialteam-byte/younic.git",
        "cd ~/younic",
        "python younic2.py",
        "First run: paste your Gemini API key at the prompt (keep it private).",
        "Key is saved in ~/codex/.apikey; no pip install is needed for YOUNIC.",
        "Update later: cd ~/younic && git pull",
        "Shared storage for /save: termux-setup-storage (approve Android prompt).",
        "Windows: python younic2.py (after downloading/cloning the repository).",
        "Type /help to see every command, or /menu to pick one.",
    ]),
    ("Project guide", [
        "/new            start a fresh session (history reset)",
        "/paste          paste your own code and save it as a file",
        "/list           show files in your projects folder",
        "/open <file>    load a file to work on",
        "Plain text (e.g. 'make a calculator in python') creates a new tool/project.",
    ]),
    ("File explorer", [
        "YOUNIC is a terminal app, so there is no graphical file tree.",
        "/list shows files, /show [file] prints a file with its code.",
        "Rename or delete files with normal Termux commands (mv, rm).",
        "Search files with the terminal: grep -r \"text\" ~/codex/projects",
    ]),
    ("Code editor", [
        "There is no multi-tab editor in this version. One current file is active.",
        "/open or /paste sets the current file; /show displays it.",
        "/edit <change>  AI edits the current file (backup is made first).",
        "/loop           repeated edit mode for several changes.",
    ]),
    ("Terminal guide", [
        "/run            run the current file",
        "/launch <tool>  open a tool in a new terminal window",
        "/runmode auto|newterm|same|vscode   choose how tools start",
        "Commands are typed at the YOUNIC prompt; /quit exits.",
    ]),
    ("Qoder AI guide", [
        "Qoder is the built-in AI coding assistant.",
        "Ask in plain text to generate a new file or tool.",
        "/advise         analyse the current file and choose an AI fix or review",
        "/fix            compile/check the file and ask Qoder to fix the error",
        "/edit <change>  ask Qoder to change the current file",
        "/tool <name> <request>  upgrade an existing tool (version goes up)",
    ]),
    ("Tool guide", [
        "/tool <request>        create a new tool (plan, write, install, test)",
        "/tools                 list all tools with version and status",
        "/launch <name>         run a tool",
        "Every generated tool folder has a README.md with install and usage notes.",
        "To remove a tool, delete its folder inside the tools directory yourself.",
    ]),
    ("Debugging guide", [
        "/fix            check and let Qoder repair errors in the current file",
        "/advise         get a list of findings before changing anything",
        "New tools are tested automatically, with up to 2 AI auto-fix attempts.",
        "If a test still fails, the tool is marked needs-fix; read the log and retry.",
    ]),
    ("Backup guide", [
        "Before every AI change, the old file is saved in ~/codex/backups.",
        "/undo           restore the last backup of the current file",
        "Tool upgrades keep older versions in a .backup_vN folder inside the tool.",
        "Nothing is deleted automatically by YOUNIC.",
    ]),
    ("Settings guide", [
        "/key            reset the stored API key (you are asked again)",
        "/model <name>   show or change the AI model",
        "/outdir <path>  set the save location used by /save",
        "/speed <preset> typing speed: slow, normal, fast, turbo, instant",
        "/anim on|off    turn animations on or off (off is faster)",
    ]),
]

def show_guide():
    """/guide: built-in help center. Pick a topic by number; Enter goes back."""
    titles = [t for t, _ in GUIDE_TOPICS]
    while True:
        idx = select_menu(APP_NAME + " HELP CENTER", titles)
        if idx is None or not (0 <= idx < len(GUIDE_TOPICS)):
            return
        title, lines = GUIDE_TOPICS[idx]
        w(DACC + "╭─ " + ACC + B + title.upper() + R + "\n")
        for ln in lines: w(GRY + "│ " + WHT + ln + R + "\n")
        w(DACC + "╰" + "─" * 30 + "\n" + R)

def write_tool_readme(tdir, name, request, version, entry, files, ok):
    """README.md for every generated tool (install, usage, dependencies, contact)."""
    ext = os.path.splitext(entry)[1].lower()
    has_req = "requirements.txt" in files
    if ext == ".py":
        run = "python3 %s   (Windows: python %s)" % (entry, entry)
    elif ext in (".js", ".mjs"):
        run = "node %s" % entry
    elif ext in (".html", ".htm"):
        run = "Open %s in a browser." % entry
    elif ext == ".sh":
        run = "sh %s" % entry
    else:
        run = "See the entry file: %s" % entry
    install = ("pip install -r requirements.txt" if has_req else
               "No external packages needed." if ext != ".js" else "No npm packages needed.")
    text = "\n".join([
        "# %s" % name,
        "",
        request.strip(),
        "",
        "## Information",
        "- Tool: %s" % name,
        "- Version: %s" % version,
        "- Status: %s" % ("tested OK" if ok else "needs manual check"),
        "- Created with: %s inside %s %s" % (AI_TOOL_NAME, APP_NAME, APP_VERSION),
        "- Developer of YOUNIC: %s (%s)" % (DEV_NAME, DEV_EMAIL),
        "- Note: this tool was generated by AI and is not officially verified or",
        "  published by %s. Review the code before using it." % DEV_NAME,
        "",
        "## Supported platform",
        "Termux (Android), Linux, Windows (where the runtime is installed).",
        "",
        "## Dependencies",
        "- Runtime: %s" % ("Python 3" if ext == ".py" else "Node.js" if ext in (".js", ".mjs") else "see entry file"),
        "- Install: %s" % install,
        "",
        "## Installation",
        "1. Keep all files in this folder together.",
        "2. Run the install command above if needed.",
        "",
        "## Usage",
        "Run:  %s" % run,
        "Or from YOUNIC:  /launch %s" % name,
        "",
        "## Support",
        "Contact: %s" % DEV_EMAIL,
        "",
    ])
    with open(os.path.join(tdir, "README.md"), "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return "README.md"


def main():
    os.makedirs(PROJ, exist_ok=True); os.makedirs(BAK, exist_ok=True)
    load_model()
    load_outdir()
    load_speed()
    load_anim()
    boot_sequence()
    key = get_key(); banner()
    history, current = [], None
    while True:
        try: u = input(ACC + B + "younic" + R + GRY + "@termux" + R + ACC + " ❯ " + R).strip()
        except (EOFError, KeyboardInterrupt): print(); break
        if not u: continue
        cmd = u.split()[0]
        arg = u[len(cmd):].strip()

        if cmd == "/menu":
            pick = pick_menu()
            if not pick: continue
            u = pick; cmd = u.split()[0]; arg = u[len(cmd):].strip()
        if cmd == "/advise":
            r = qoder_advise(current, key)
            if r: current = r
            continue
        if cmd == "/clear":
            banner(True); continue
        if cmd == "/tools":
            show_tools(); continue
        if cmd == "/launch":
            reg = load_registry(); n = slugify(arg)
            if n not in reg:
                notify("warn", "Tool nahi mila: %s" % arg); continue
            launch_tool(reg[n]["path"], reg[n]["entry"]); continue
        if cmd == "/runmode":
            m = arg.strip().lower()
            if m in ("auto", "newterm", "same", "vscode"):
                _save_config({"runmode": m}); notify("ok", "Run mode: " + m)
            else:
                notify("info", "Run mode: " + run_mode())
                w(GRY + "Usage: /runmode auto|newterm|same|vscode\n" + R)
            continue
        if cmd == "/tool":
            parts = arg.split(maxsplit=1)
            if not parts:
                notify("warn", "Usage: /tool <naam> <request>  ya  /tool <nayi request>"); continue
            first = slugify(parts[0])
            if len(parts) == 2 and first in load_registry():
                r = build_tool(parts[1], key, first, upgrade=True)
            elif len(parts) == 2:
                r = build_tool(parts[1], key, first, upgrade=False)
            else:
                r = build_tool(arg, key, None, upgrade=False)
            if r: current = r
            continue

        if cmd == "/quit": break
        if cmd == "/about": show_about(); continue
        if cmd == "/guide": show_guide(); continue
        if cmd == "/help": show_help(); continue
        if cmd == "/anim":
            a = arg.strip().lower()
            if a in ("on", "off"):
                save_anim(a == "on")
                notify("ok", "Animation: %s" % a)
            else:
                notify("info", "Animation: %s" % ("on" if ANIM else "off"))
                w(GRY + "Usage: /anim on|off\n" + R)
            continue
        if cmd == "/new": history, current = [], None; banner(False); continue
        if cmd == "/stats": stats(); continue
        if cmd == "/key":
            if os.path.exists(KEYF): os.remove(KEYF)
            key = get_key(); continue
        if cmd == "/model":
            if arg:
                save_model(arg); w(GRN + "Model set: " + MODEL + "\n" + R)
            else:
                w(CYN + "Current: " + MODEL + "\n" + R)
                w(GRY + "Usage: /model gemini-3.5-flash\n" + R)
            continue
        if cmd == "/outdir":
            if arg:
                save_outdir(os.path.expanduser(arg)); w(GRN + "Save location set: " + OUT + "\n" + R)
            else:
                w(CYN + "Current save location: " + OUT + "\n" + R)
                w(GRY + "Usage: /outdir /sdcard/Download\n" + R)
            continue
        if cmd == "/speed":
            presets = {"slow": 60, "normal": 150, "fast": 260, "turbo": 500, "instant": 0}
            if arg.strip() in presets:
                save_speed(presets[arg.strip()])
                w(GRN + "Typing speed: %s (%d chars/sec)\n" % (arg.strip(), TYPE_CPS) + R)
            elif arg.strip().isdigit():
                save_speed(int(arg.strip()))
                w(GRN + "Typing speed set: %d chars/sec\n" % TYPE_CPS + R)
            else:
                w(CYN + "Current: %d chars/sec\n" % TYPE_CPS + R)
                w(GRY + "Usage: /speed slow|normal|fast|turbo|instant  ya  /speed 300\n" + R)
            continue
        if cmd == "/list":
            for f in sorted(os.listdir(PROJ)):
                w("  " + CYN + f + GRY + "  %d B\n" % os.path.getsize(os.path.join(PROJ, f)) + R)
            continue
        if cmd == "/show":
            p = current if not arg else (arg if os.path.isabs(arg) else os.path.join(PROJ, arg))
            if p and os.path.exists(p): show_file(p)
            else: notify("warn", "File nahi mili")
            continue
        if cmd == "/run":
            run_file(current) if current else notify("warn", "Pehle project banayein"); continue
        if cmd == "/save":
            export(current) if current else notify("warn", "Koi file nahi"); continue
        if cmd == "/open":
            p = arg if os.path.isabs(arg) else os.path.join(PROJ, arg)
            if os.path.exists(p):
                current = p; history = []
                notify("ok", "Loaded: " + p); show_file(p)
            else: notify("err", "File nahi mili")
            continue
        if cmd == "/paste":
            code = multiline("[PASTE] apna code paste karein")
            name = input(ACC + "[?] filename (jaise app.py): " + R).strip() or "pasted.py"
            current = os.path.join(PROJ, name)
            open(current, "w").write(code)
            notify("ok", "Saved: %s (%d lines)" % (current, code.count("\n")))
            history = []; show_file(current)
            current = edit_loop(history, key, current)
            continue
        if cmd == "/loop":
            current = edit_loop(history, key, current)
            continue
        if cmd == "/undo":
            if not current: notify("warn", "Koi file nahi"); continue
            baks = sorted([f for f in os.listdir(BAK) if f.startswith(os.path.basename(current) + ".")])
            if not baks: notify("warn", "Koi backup nahi"); continue
            shutil.copy(os.path.join(BAK, baks[-1]), current)
            os.remove(os.path.join(BAK, baks[-1]))
            notify("ok", "Wapas restore: " + baks[-1]); continue
        if cmd == "/fix":
            if not current: notify("warn", "Pehle /open ya /paste"); continue
            ok, log = check_only(current)
            if ok: ok, log = build(current)
            if ok: notify("ok", "koi error nahi mila"); continue
            debug_view(current, log)
            old = open(current).read()
            history = [{"role": "user", "parts": [{"text":
                "FILENAME: %s\nCode:\n```\n%s```\nError:\n%s\nPoori fixed file do (same format)." %
                (os.path.basename(current), old, log[:1800])}]}]
            r = pipeline(history, key, old)
            if r: current = r
            continue
        if cmd == "/edit":
            if not current: notify("warn", "Pehle /open ya /paste"); continue
            req = arg or input(ACC + "[?] kya change karna hai: " + R)
            old = open(current).read()
            history = [{"role": "user", "parts": [{"text":
                "FILENAME: %s\nExisting code:\n```\n%s```\nIsme yeh change karo aur poori updated file do (same format):\n%s" %
                (os.path.basename(current), old, req)}]}]
            r = pipeline(history, key, old)
            if r: current = r
            continue

        name, upgrade = route_request(u, load_registry())
        r = build_tool(u, key, name, upgrade)
        if r: current = r

    goodbye_screen()

if __name__ == "__main__":
    main()
