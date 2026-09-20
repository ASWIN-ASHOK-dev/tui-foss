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

Welcome to **CyberShell RPG v2.0**, an immersive, story-driven cyber espionage RPG that takes place entirely inside your terminal! 

As an elite operative code-named **Byte**, you wake up isolated inside a compromised corporate mainframe with severe memory corruption. Your goal? Bypass defensive daemons, manipulate file permissions, crack security vaults, and stop a rogue Sentinel AI Overlord from locking down the global network.

You don't play this game with WASD keys—you play it by executing **authentic Linux commands** against an in-memory Virtual Filesystem (VFS). 

> [!WARNING]
> Beware: **Syntax errors cause electrical backlash damage (-15 HP)!** Think tactically before you press Enter. If you hit 0 HP, your connection is severed and you restart.

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
cd tui-foss/linux-tui

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
MIT License. Created with ❤️ by Amy and the CyberShell Dev Team.
