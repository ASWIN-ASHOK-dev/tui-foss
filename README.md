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
| **Amy** 🔗 | **Project Lead & Master Integrator** | `contracts.py`, `pyproject.toml`, `requirements.txt`, `run.py`, `cybershell_standalone.py`, `tests/test_integration.py`, `tests/conftest.py`, `README.md` |
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
- Zero required third-party runtime dependencies! CyberShell runs completely on the Python standard library.

### Option 1: Run via `uv` (Recommended)
[`uv`](https://github.com/astral-sh/uv) is an extremely fast Python package manager. It makes running the game incredibly easy.
```bash
# Clone the repository
git clone https://github.com/Amy-code658/tui-foss.git
cd tui-foss

# Run the game directly (uv handles everything automatically!)
uv run cybershell
```

**Optional launcher flags:**
```bash
uv run cybershell --name Cipher --sector 0  # Start with a custom name
uv run cybershell --demo                    # Run a visual showcase
uv run cybershell --smoke-test              # Run diagnostics
```

### Option 2: Run via Main Launcher (Standard Python)
```bash
# Launch the game manually using Python
python3 src/cybershell/run.py
```

---

## 🎮 How to Play

### Screen Navigation
From anywhere in the Mission Lab terminal, type a screen number or name to jump between your hacker stations:
* `[0]` or `title` — CyberShell Title Screen
* `[1]` or `lab` — **Mission Lab (Main Game Screen)**
* `[2]` or `codex` — **Hacker Codex** (Linux spellbook & command references)
* `[3]` or `inventory` — **Operative Inventory** (View your collected loot chips and hardware)
* `[4]` or `map` — Mainframe network topology map
* `[5]` or `minigame` — Chmod door lockpicking challenge

### The Mission Arc
The game is split into **6 Sectors**. As you complete objectives (like creating files or navigating directories), you earn XP, level up your Hacker Rank, and gain Loot Items. Follow the on-screen dialogue from your NPC handlers to understand what commands to type next.

### Core Linux Commands
Execute these commands in the terminal just like a real Linux system:
* `pwd` — Print working directory coordinates.
* `ls`, `ls -l`, `ls -la` — List directory contents with permissions.
* `cd <path>` — Navigate the directory tree (`..`, `~`, `/tmp`, etc.).
* `cat <file>` — Read file data.
* `touch <file>` — Create a new empty file.
* `mkdir [-p] <dir>` — Create directory trees.
* `chmod <mode> <file>` — Alter security permissions (e.g., `755`, `600`).
* `echo <text>` — Print text strings.

### 🌟 Advanced Shell Features (Pipelines & Redirects)
Thanks to the custom `ShellInterpreter`, you can use advanced Linux shell operators to manipulate data and defeat bosses!
* **Pipes (`|`)**: Chain commands together (e.g., `cat firewall.log | grep ERROR`)
* **Redirects (`>`)**: Save output to a file (e.g., `echo "payload" > exploit.sh`)

---

## 🛡️ Architecture & Contributor Credits

CyberShell v2.0 was built with a **Strict File Boundary Rule**: each developer has mutually exclusive ownership over specific modules.

| Developer | Core Role |
| :--- | :--- |
| **Amy** 👑 | Project Lead, Master Integrator, Engine Bootstrapper |
| **Rudra** 💻 | Virtual Filesystem (VFS) Architect |
| **Aniket** ⚡ | Shell Pipeline (`\|`, `>`) & Combat Interpreter |
| **Poornendhu** 🖥️ | Cyber-TUI Layout & Frame Renderer |
| **Gautham** 🎨 | ASCII Art, FX & Terminal Input Loop |
| **Neha** 📊 | Game State, Storyline & 6 Cyber-Sector Quests |
| **Aswin** 📜 | Quest Evaluator, Progression Logic & Tests |
| **Akash** 🔐 | Hacker Codex & Chmod Lockpicking Minigame |

---

## 🧪 Testing

Run the entire automated test suite to ensure the integration is flawless:
```bash
python3 -m unittest discover -s tests
```

---
## 📄 License
MIT License. Created with ❤️ by The CyberShell Dev Team.
