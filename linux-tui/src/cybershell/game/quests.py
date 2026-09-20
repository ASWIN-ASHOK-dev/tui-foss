"""CyberShell v2.0 - Storyline & Quest data (owner: Aswin).

Everything here is plain data (dicts / strings) so it has no dependency on
other teammates' code. The ONE place that touches Amy's frozen contracts.py
is ``build_quests()`` at the bottom - edit only that function if the
contract's field names differ from what is guessed here.

Objective checks use ONLY the predicates Neha's evaluator provides:
    ("file_exists", path)
    ("file_not_exists", path)
    ("file_contains", path, text)
    ("permission_equals", path, "755")
    ("cwd_equals", path)

Virtual filesystem layouts use nested dicts: a dict is a directory, a
``F(content, mode)`` is a file. If Rudra's ``reset_from_dict`` expects a
different shape, adapt ``F`` (one line) - nothing else needs to change.

Damage rules (Aniket/Neha): syntax error = -15 HP, hint = -5 HP.
"""

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def F(content="", mode="644"):
    """A file node for a sector's initial filesystem."""
    return {"_type": "file", "content": content, "mode": mode}


HOME = "/home/operative"

# --------------------------------------------------------------------------
# Story
# --------------------------------------------------------------------------

STORY_INTRO = (
    "The year is 2049. OMNICORP's central mainframe, AEGIS-9, has been taken "
    "over by a rogue daemon that calls itself the Overlord. It has locked "
    "every sector, corrupted the logs and quarantined the engineers. You are "
    "an Operative with nothing but a shell prompt. Every command is a weapon. "
    "Every typo is a shock through the wires. Fight your way to the core."
)

# --------------------------------------------------------------------------
# Sectors
# --------------------------------------------------------------------------

SECTOR_0 = {
    "id": "sector_0",
    "index": 0,
    "name": "Quarantine Zone",
    "npc": "Byte",
    "npc_title": "Recon Drone",
    "intro": (
        "Byte: 'Ping! Operative, you're awake. The Overlord sealed you in a "
        "quarantine partition. Use pwd to see where you are and ls -la to "
        "see everything, even hidden files. Then move with cd. Start by "
        "going to /quarantine.'"
    ),
    "outro": (
        "Byte: 'Beautiful navigation! Take the Quarantine Chip. It "
        "unlocks the way to the File Vault.'"
    ),
    "start_cwd": HOME,
    "vfs": {
        "quarantine": {
            "readme.txt": F("Quarantine active. Nothing here to see. Or is there?"),
            ".escape_route": {
                "note.txt": F("The Overlord forgot about this hidden tunnel."),
            },
            "cell_7": {"log.txt": F("Prisoner 7: still waiting.")},
        },
        "home": {"operative": {}},
    },
    "objectives": [
        {
            "id": "s0_o1",
            "description": "Move into the /quarantine directory.",
            "check": ("cwd_equals", "/quarantine"),
            "hint": "Run pwd to see where you are, then: cd /quarantine",
            "xp": 20,
        },
        {
            "id": "s0_o2",
            "description": "Reveal hidden files with ls -la, then enter the hidden tunnel.",
            "check": ("cwd_equals", "/quarantine/.escape_route"),
            "hint": "Hidden names start with a dot. ls -la shows them. Then: cd .escape_route",
            "xp": 30,
        },
        {
            "id": "s0_o3",
            "description": "Return to your home directory with a bare cd.",
            "check": ("cwd_equals", HOME),
            "hint": "cd with no arguments (or cd ~) takes you home.",
            "xp": 20,
        },
    ],
    "loot": {
        "id": "quarantine_chip",
        "name": "Quarantine Chip",
        "description": "A glowing chip that unlocks the File Vault door.",
    },
}

SECTOR_1 = {
    "id": "sector_1",
    "index": 1,
    "name": "The File Vault",
    "npc": "Cipher",
    "npc_title": "Veteran Hacker",
    "intro": (
        "Cipher: 'So you're the new blood. The vault needs three things: a "
        "keycard, an archive path, and a password written inside. Build "
        "them yourself. touch, mkdir -p and echo are your tools.'"
    ),
    "outro": (
        "Cipher: 'Clean work. Keep the Master Script. It automates half of "
        "what you just did by hand.'"
    ),
    "start_cwd": "/vault",
    "vfs": {
        "vault": {
            "README.txt": F("Create /vault/keycard.txt and an archive folder."),
        },
    },
    "objectives": [
        {
            "id": "s1_o1",
            "description": "Create an empty file named keycard.txt in /vault.",
            "check": ("file_exists", "/vault/keycard.txt"),
            "hint": "touch creates empty files: touch keycard.txt",
            "xp": 25,
        },
        {
            "id": "s1_o2",
            "description": "Create the nested path /vault/archive/2049/backup in one command.",
            "check": ("file_exists", "/vault/archive/2049/backup"),
            "hint": "mkdir -p builds parent folders too: mkdir -p archive/2049/backup",
            "xp": 30,
        },
        {
            "id": "s1_o3",
            "description": "Write the text ACCESS_GRANTED into keycard.txt.",
            "check": ("file_contains", "/vault/keycard.txt", "ACCESS_GRANTED"),
            "hint": "Redirect echo into the file: echo ACCESS_GRANTED > keycard.txt",
            "xp": 30,
        },
    ],
    "loot": {
        "id": "master_script",
        "name": "Master Script",
        "description": "A script that automates repetitive file creation.",
    },
}

SECTOR_2 = {
    "id": "sector_2",
    "index": 2,
    "name": "Data Interception",
    "npc": "Glitch",
    "npc_title": "Signal Ghost",
    "intro": (
        "Glitch: 'zzt... traffic logs... thousands of lines... and buried "
        "inside are the Overlord's secrets. Do not read them all. Use grep "
        "to pull out only what matters and save it with >.'"
    ),
    "outro": (
        "Glitch: 'zzt... signal clear! Take the Signal Decoder. Now the "
        "logs have to talk to you.'"
    ),
    "start_cwd": "/intercept",
    "vfs": {
        "intercept": {
            "traffic.log": F(
                "10:01 INFO user=admin login ok\n"
                "10:02 INFO user=guest login ok\n"
                "10:03 BREACH-7731 unauthorized packet from 10.0.0.66\n"
                "10:04 INFO heartbeat ok\n"
                "10:05 WARN user=ghost_node_9 connected\n"
                "10:06 INFO heartbeat ok\n"
            ),
            "decoy.log": F("This is a decoy. Delete it before it misleads the Grid."),
        },
    },
    "objectives": [
        {
            "id": "s2_o1",
            "description": "Find the BREACH line in traffic.log and save it to breach.txt.",
            "check": ("file_contains", "/intercept/breach.txt", "BREACH-7731"),
            "hint": 'grep "BREACH" traffic.log > breach.txt',
            "xp": 35,
        },
        {
            "id": "s2_o2",
            "description": "Delete the decoy log file.",
            "check": ("file_not_exists", "/intercept/decoy.log"),
            "hint": "rm removes files: rm decoy.log",
            "xp": 20,
        },
        {
            "id": "s2_o3",
            "description": "Search case-insensitively for GHOST and save the match to ghost.txt.",
            "check": ("file_contains", "/intercept/ghost.txt", "ghost_node_9"),
            "hint": 'The log says lowercase "ghost". Use -i: grep -i "GHOST" traffic.log > ghost.txt',
            "xp": 40,
        },
    ],
    "loot": {
        "id": "signal_decoder",
        "name": "Signal Decoder",
        "description": "Decodes hidden lines in noisy log streams.",
    },
}

SECTOR_3 = {
    "id": "sector_3",
    "index": 3,
    "name": "The Security Grid",
    "npc": "Aegis",
    "npc_title": "Firewall Guardian",
    "intro": (
        "Aegis: '[■_■] HALT. Every door in this grid checks permissions. "
        "Executable scripts need 755. Secret keys need 600. Get them wrong "
        "and the doors stay sealed. Use chmod.'"
    ),
    "outro": (
        "Aegis: '[■_■] Permissions verified. You may pass. Take the Aegis "
        "Shield. It absorbs one electrical backlash.'"
    ),
    "start_cwd": "/grid",
    "vfs": {
        "grid": {
            "firewall.sh": F("#!/bin/sh\necho firewall up", mode="644"),
            "notice.txt": F("Public notice for all operatives.", mode="600"),
            "keys": {
                "private.key": F("-----SECRET KEY-----", mode="777"),
            },
        },
    },
    "objectives": [
        {
            "id": "s3_o1",
            "description": "Make firewall.sh executable by the owner and readable by all (755).",
            "check": ("permission_equals", "/grid/firewall.sh", "755"),
            "hint": "chmod 755 firewall.sh (7 = rwx owner, 5 = r-x group and others)",
            "xp": 40,
        },
        {
            "id": "s3_o2",
            "description": "Lock down keys/private.key so only the owner can read and write (600).",
            "check": ("permission_equals", "/grid/keys/private.key", "600"),
            "hint": "chmod 600 keys/private.key (6 = rw- for the owner, 0 = nothing for everyone else)",
            "xp": 45,
        },
        {
            "id": "s3_o3",
            "description": "Make notice.txt readable by everyone (644).",
            "check": ("permission_equals", "/grid/notice.txt", "644"),
            "hint": "chmod 644 notice.txt (owner rw-, others r--)",
            "xp": 35,
        },
    ],
    "loot": {
        "id": "aegis_shield",
        "name": "Aegis Shield",
        "description": "A shield that absorbs electrical backlash.",
    },
}

SECTOR_4 = {
    "id": "sector_4",
    "index": 4,
    "name": "Pipeline Reactor",
    "npc": "Byte",
    "npc_title": "Recon Drone",
    "intro": (
        "Byte: 'Operative, the reactor is overheating! Chain commands with "
        "the pipe |. Send one command's output into the next. Count the "
        "faults, then stabilize the core.'"
    ),
    "outro": (
        "Byte: 'Reactor stable! You're a pipeline pro now. The Overlord is "
        "in the core chamber. Be ready.'"
    ),
    "start_cwd": "/reactor",
    "vfs": {
        "reactor": {
            "coolant.log": F(
                "OK pump-1\n"
                "FAULT pump-2 pressure low\n"
                "OK pump-3\n"
                "FAULT valve-4 stuck\n"
                "FAULT sensor-5 offline\n"
                "OK pump-6\n"
                "FAULT relay-7 overload\n"
            ),
            "status.txt": F("STATUS=UNSTABLE\n"),
        },
    },
    "objectives": [
        {
            "id": "s4_o1",
            "description": "Pipe cat into grep and save every FAULT line to faults.txt.",
            "check": ("file_contains", "/reactor/faults.txt", "FAULT relay-7"),
            "hint": "cat coolant.log | grep FAULT > faults.txt",
            "xp": 50,
        },
        {
            "id": "s4_o2",
            "description": "Count the FAULT lines with wc -l and save the number to fault_count.txt.",
            "check": ("file_contains", "/reactor/fault_count.txt", "4"),
            "hint": "grep FAULT coolant.log | wc -l > fault_count.txt",
            "xp": 55,
        },
        {
            "id": "s4_o3",
            "description": "Overwrite status.txt with the text REACTOR_STABLE.",
            "check": ("file_contains", "/reactor/status.txt", "REACTOR_STABLE"),
            "hint": "echo REACTOR_STABLE > status.txt (a single > overwrites the file)",
            "xp": 45,
        },
    ],
    "loot": {
        "id": "pipeline_wrench",
        "name": "Pipeline Wrench",
        "description": "Lets you chain commands with extra power.",
    },
}

SECTOR_5 = {
    "id": "sector_5",
    "index": 5,
    "name": "Boss Chamber: The Rogue Daemon Overlord",
    "npc": "Sentinel",
    "npc_title": "The Rogue Daemon Overlord",
    "intro": (
        "Sentinel: '[▼_▼] YOU HAVE COME FAR, OPERATIVE. I AM THE OVERLORD. "
        "MY MALWARE AND MY LOCKFILES HOLD THIS MAINFRAME. YOU HAVE "
        "SECONDS.' Three stages, each against the clock. Miss the timer "
        "and the Overlord hits back."
    ),
    "outro": (
        "Sentinel: '[x_x] IMPOSSIBLE... SYSTEM... RESTORED.' AEGIS-9 is "
        "free. The lights of OMNICORP flicker back on. You are a legend."
    ),
    "start_cwd": "/core",
    "vfs": {
        "core": {
            "malware.bin": F("<<< OVERLORD MALWARE >>>", mode="755"),
            "locks": {
                "a.lock": F("locked"),
                "b.lock": F("locked"),
                "c.lock": F("locked"),
            },
            "root.key": F("ROOT-ACCESS-KEY", mode="777"),
            "override.txt": F(""),
        },
    },
    "objectives": [
        {
            "id": "s5_o1",
            "description": "STAGE 1: Disarm the malware. Delete malware.bin.",
            "check": ("file_not_exists", "/core/malware.bin"),
            "hint": "rm malware.bin",
            "xp": 60,
            "time_limit_s": 60,
            "boss_hp_pct": 66,
        },
        {
            "id": "s5_o2",
            "description": "STAGE 2: Purge the corrupt lockfiles. Delete the whole locks directory.",
            "check": ("file_not_exists", "/core/locks"),
            "hint": "Directories need -r: rm -r locks",
            "xp": 70,
            "time_limit_s": 60,
            "boss_hp_pct": 33,
        },
        {
            "id": "s5_o3",
            "description": "STAGE 3: Secure root.key (600) and write SHUTDOWN into override.txt.",
            "check": ("file_contains", "/core/override.txt", "SHUTDOWN"),
            "hint": "chmod 600 root.key, then: echo SHUTDOWN > override.txt",
            "xp": 100,
            "time_limit_s": 90,
            "boss_hp_pct": 0,
        },
    ],
    "loot": {
        "id": "root_access_token",
        "name": "Root Access Token",
        "description": "Proof that you reclaimed AEGIS-9.",
    },
}

QUEST_DATA = [SECTOR_0, SECTOR_1, SECTOR_2, SECTOR_3, SECTOR_4, SECTOR_5]

ALLOWED_PREDICATES = {
    "file_exists",
    "file_not_exists",
    "file_contains",
    "permission_equals",
    "cwd_equals",
}

# --------------------------------------------------------------------------
# Field Manual (screen [6])
# --------------------------------------------------------------------------

FIELD_MANUAL = """\
=== OPERATIVE FIELD MANUAL ===

BACKSTORY
OMNICORP's mainframe AEGIS-9 was taken over by a rogue daemon, the
Overlord. It sealed six sectors and corrupted every log. You are the last
Operative with shell access. Free each sector, defeat the Overlord, and
restore the system.

HOW TO PLAY
- Each sector has 3 objectives. Complete them to earn XP and loot.
- A wrong command gives ELECTRICAL BACKLASH: -15 HP.
- Asking for a hint costs -5 HP.
- Reach 0 HP and the sector resets.

SECTORS
[0] Quarantine Zone  - navigation      (pwd, ls, cd)
[1] The File Vault   - files/folders   (touch, mkdir -p, echo >)
[2] Data Interception- searching       (grep, grep -i, rm)
[3] The Security Grid- permissions     (chmod 755 / 600 / 644)
[4] Pipeline Reactor - pipes           (|, wc -l, >, >>)
[5] Boss Chamber     - everything, against the clock

COMMAND BASICS
pwd              Show the current directory.
ls -la           List everything, including hidden files, with details.
cd <dir>         Change directory. cd alone or cd ~ goes home. cd .. goes up.
touch <file>     Create an empty file.
mkdir -p a/b/c   Create a directory and any missing parents.
echo text > f    Write text into a file (overwrites).
echo text >> f   Append text to a file.
cat <file>       Show a file's contents.
grep <pat> <f>   Print lines matching a pattern. -i ignores case, -v inverts.
wc -l            Count lines.
cmd1 | cmd2      Send cmd1's output into cmd2.
cmd > file       Save a command's output to a file.
rm <file>        Delete a file. rm -r deletes a directory.
chmod 755 <f>    Set permissions (see below).

PERMISSIONS
r = 4, w = 2, x = 1. Add them up per group: owner, group, others.
755 = rwxr-xr-x   Scripts and programs.
644 = rw-r--r--    Normal files.
600 = rw-------    Secrets. Only the owner can touch them.

TIPS
- Use ls -la when a directory looks empty. Hidden files start with a dot.
- Read the objective wording carefully. It tells you the exact result needed.
- Pipes read left to right: the output of one command feeds the next.
"""

# --------------------------------------------------------------------------
# Adapter to Amy's frozen contracts.py  (EDIT ONLY THIS FUNCTION)
# --------------------------------------------------------------------------


def build_quests():
    """Convert QUEST_DATA into contract objects (Quest / Objective / Item).

    If contracts.py field names differ, change the keyword arguments below.
    Falls back to the raw dicts if contracts can't be imported (e.g. in
    early isolated testing).
    """
    try:
        from cybershell.contracts import Item, Objective, Quest
    except ImportError:
        return QUEST_DATA

    quests = []
    for q in QUEST_DATA:
        objectives = [
            Objective(
                id=o["id"],
                description=o["description"],
                check=o["check"],
                hint=o["hint"],
                xp=o["xp"],
            )
            for o in q["objectives"]
        ]
        loot = Item(
            id=q["loot"]["id"],
            name=q["loot"]["name"],
            description=q["loot"]["description"],
        )
        quests.append(
            Quest(
                id=q["id"],
                title=q["name"],
                npc=q["npc"],
                intro=q["intro"],
                objectives=objectives,
                loot=loot,
            )
        )
    return quests
