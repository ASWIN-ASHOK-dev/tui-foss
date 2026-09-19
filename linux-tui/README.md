# ⚡ CyberShell RPG v2.0

> **A Terminal-Based Linux Cyber Adventure & Shell Mastery RPG**

```text
  ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███████╗██╗  ██╗███████╗██╗     ██╗     
 ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║██╔════╝██║     ██║     
 ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████╗███████║█████╗  ██║     ██║     
 ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══██║██╔══╝  ██║     ██║     
 ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████║██║  ██║███████╗███████╗███████╗
  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
```

---

## 🌌 Overview

**CyberShell RPG v2.0** is an interactive, story-driven cyber espionage RPG played directly inside your terminal. As an elite operative code-named **Byte**, you wake up inside a compromised corporate mainframe with memory corruption. By executing real Linux commands against an in-memory Virtual Filesystem (VFS), you must bypass defensive daemons, manipulate file permissions, crack security vaults, and prevent a rogue AI overlord from triggering global lockdown.

Beware: **syntax errors cause electrical backlash damage (-15 HP)!** Think tactically before you press Enter.

---

## 🛡️ Conflict-Free 8-Person Architecture & File Ownership

CyberShell v2.0 is developed using the **Strict File Boundary Rule**: each developer has dedicated, mutually exclusive ownership over specific files. **No developer edits another person's files.**

| Developer | Core Role | Assigned Files |
| :--- | :--- | :--- |
| **Amy** 👑 | **Project Lead & Master Integrator** | `contracts.py`, `pyproject.toml`, `requirements.txt`, `run.py`, `cybershell_standalone.py`, `tests/test_integration.py`, `tests/conftest.py`, `README.md` |
| **Rudra** 💻 | **VFS Architect** | `src/cybershell/engine/node.py`, `src/cybershell/engine/vfs.py`, `tests/test_vfs.py` |
| **Aniket** ⚡ | **Shell Pipeline & Combat Engine** | `src/cybershell/engine/commands.py`, `src/cybershell/engine/interpreter.py`, `tests/test_interpreter.py` |
| **Poornendhu** 🖥️ | **Cyber-TUI Lead & Frame Renderer** | `src/cybershell/ui/renderer.py`, `src/cybershell/ui/rpg_app.py`, `tests/test_ui.py` |
| **Gautham** 🎨 | **ASCII Art, FX & Terminal Input** | `src/cybershell/ui/ascii_art.py`, `src/cybershell/ui/rpg_app.py`, `tests/test_ui.py` |
| **Neha** 📊 | **Game State & Quest Evaluator** | `src/cybershell/game/state.py`, `src/cybershell/game/evaluator.py`, `tests/test_game.py` |
| **Aswin** 📜 | **Storyline & 6 Cyber-Sectors** | `src/cybershell/game/quests.py`, `tests/test_game.py` |
| **Akash** 🔐 | **Hacker Codex & Chmod Minigame** | `src/cybershell/tools/codex.py`, `src/cybershell/tools/chmod_calc.py`, `src/cybershell/tools/chmod_minigame.py`, `src/cybershell/tools/map.py`, `tests/test_tools.py` |

---

## 🚀 Quick Start & Installation

### Requirements
- **Python 3.8+** (Linux, macOS, or Windows)
- Zero required third-party runtime dependencies! CyberShell runs completely on Python standard library.

### Option 1: Run via `uv` (Recommended)
[`uv`](https://github.com/astral-sh/uv) is an extremely fast Python package manager written in Rust. It makes running, testing, and publishing the game much easier.
```bash
# Clone the repository
git clone https://github.com/Amy-code658/tui-foss.git
cd tui-foss/linux-tui

# Run the game directly (uv will handle the virtual environment and dependencies automatically!)
uv run cybershell

# Optional launcher flags
uv run cybershell --name Cipher --sector 0
uv run cybershell --demo
uv run cybershell --smoke-test
```

### Option 2: Run via Main Launcher (Standard Python)
```bash
# Launch the game manually
python3 run.py
```

### Option 3: Run Standalone Single-File Bundle
```bash
# Zero-dependency, single-file distribution
python3 cybershell_standalone.py
```

---

## 🎮 In-Game Controls & Navigation

### Screen Navigation
From anywhere in the terminal, type a screen number or name to jump between hacker stations:
* `[0]` or `title` — CyberShell Title Screen
* `[1]` or `lab` — Mission Lab & Split Terminal Interface
* `[2]` or `codex` — Hacker Codex (Linux spellbook & combos)
* `[3]` or `inventory` — Operative inventory & loot chips
* `[4]` or `map` — Mainframe network topology map
* `[5]` or `minigame` — Chmod door lockpicking challenge

### Core Linux Shell Commands
In the Mission Lab terminal, execute authentic Linux commands against the virtual filesystem:
* `pwd` — Print working directory coordinates
* `ls`, `ls -l`, `ls -la` — List directory contents with permissions
* `cd <path>` — Navigate the directory tree (`..`, `~`, `/tmp`, etc.)
* `cat <file>` — Read file data
* `touch <file>` — Create a new file node
* `mkdir [-p] <dir>` — Create directory trees
* `chmod <mode> <file>` — Alter security permission bits (e.g. `755`, `600`)
* `echo <text>` — Print or pipe strings
* `clear` — Clear terminal buffer
* `exit` or `quit` — Disconnect from session

---

## 🧪 Testing & Verification

Run the entire automated test suite using `uv` (Recommended):
```bash
uv run pytest tests/
```

Or using standard Python:
```bash
python3 -m unittest discover -s tests
```

To run only the Master Integration Smoke Test:
```bash
uv run python3 -m unittest tests/test_integration.py
```

---

## 📦 Publishing

With `uv`, building and publishing CyberShell to PyPI is incredibly simple and fast:

```bash
# Build source distributions and wheels
uv build

# Publish to PyPI
uv publish
```

---
## 📄 License
MIT License. Created with ❤️ by Amy and the CyberShell Dev Team.
