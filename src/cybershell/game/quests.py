"""Story and Quest Definitions for CyberShell RPG.

Author: Neha (Narrative & Quests)
"""

from __future__ import annotations

from typing import Dict

from cybershell.contracts import Item, Objective, Quest

def get_sector_quests() -> Dict[int, Quest]:
    """Returns a dictionary mapping sector IDs to their Quests."""
    quests = {}

    # Sector 0: Quarantine Zone
    quests[0] = Quest(
        id="quest_sector_0",
        sector_id=0,
        sector_name="Quarantine Zone",
        npc_name="Byte",
        lore=(
            "You awaken inside an isolated quarantine memory sandbox after an unexpected memory wipe. "
            "A corporate security lockdown has sealed off all engineers from the central network."
        ),
        dialogue=[
            "Operative! Welcome back to the grid. Your memory registers appear scrambled.",
            "Verify your mainframe location coordinates before venturing forward.",
            "Survey the sandbox environment to discover breadcrumbs and directories.",
            "Deploy the operative beacon file 'beacon.log' to unlock the perimeter gate.",
        ],
        objectives=[
            Objective(
                id="obj_0_1",
                description="Verify your current location coordinates inside the quarantine sandbox.",
                hint="Type 'pwd' at the prompt and press Enter to verify your location.",
                command="pwd",
                syntax="pwd",
                explanation="Prints the absolute pathname of your current working directory.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative",
                xp_reward=50,
                hints=[
                    "Check where you are currently located in the mainframe filesystem.",
                    "Look up the standard command that prints your working directory coordinates.",
                    "Execute 'pwd' to confirm your coordinates.",
                ],
                scenario="System memory registers are scrambled. Confirm your terminal coordinates.",
            ),
            Objective(
                id="obj_0_2",
                description="Survey the quarantine environment for directory assets, hidden files, and permissions.",
                hint="Type 'ls -la' at the prompt and press Enter to inspect all files and permissions.",
                command="ls",
                syntax="ls [-la]",
                explanation="Lists directory contents with detailed file permissions (-l) and hidden dotfiles (-a).",
                predicate_type="file_exists",
                predicate_target="/home/operative",
                xp_reward=50,
                hints=[
                    "Inspect the contents of the current directory to see what files were left behind.",
                    "Check 'man ls' to see how to list all directory contents including details.",
                    "Run 'ls' or 'ls -la' to survey all files, directories, and hidden assets.",
                ],
                scenario="The incident left multiple status logs and system files. Inspect your surroundings.",
            ),
            Objective(
                id="obj_0_3",
                description="Deploy an operative status beacon named 'beacon.log' to synchronize clearance.",
                hint="Type 'touch beacon.log' at the prompt and press Enter to deploy the beacon.",
                command="touch",
                syntax="touch <filename>",
                explanation="Creates a new empty file or updates the timestamp of an existing file.",
                predicate_type="file_exists",
                predicate_target="beacon.log",
                xp_reward=50,
                hints=[
                    "Place a new status file named 'beacon.log' in your active directory.",
                    "The standard tool to create empty files without opening an editor is 'touch'.",
                    "Execute 'touch beacon.log' to deploy your signal.",
                ],
                scenario="With reconnaissance complete, drop the recovery beacon to link with external grid.",
            ),
        ],
        reward_item=Item(
            id="item_quarantine_chip",
            name="Quarantine Keychip",
            description="An encrypted hardware token that grants clearance to Sector 1 File Vault.",
            category="hardware",
            rarity="rare",
        ),
        reward_xp=100,
        environment_tree={
            "README.txt": (
                "[QUARANTINE SECTOR NOTICE]\n"
                "Emergency reboot occurred at 03:41 UTC.\n"
                "System logs and breadcrumbs are preserved under logs/ and system/.\n"
            ),
            "logs": {
                "incident.log": (
                    "[SECTOR 0 INCIDENT REPORT]\n"
                    "Alert: Unauthorized memory probe detected.\n"
                    "Status: Sandbox locked down pending operative verification.\n"
                ),
                "boot.log": "System registers loaded successfully.\n",
            },
            "system": {
                "telemetry.conf": "PORT=443\nNODE=SEC_0\nSTATUS=ONLINE\n",
            },
            ".easter_egg": "OPERATIVE SECRET: You explored the hidden dotfiles of Sector 0! (+50 XP)\n",
        },
    )

    # Sector 1: The File Vault
    quests[1] = Quest(
        id="quest_sector_1",
        sector_id=1,
        sector_name="The File Vault",
        npc_name="Cipher",
        lore=(
            "You have breached the quarantine perimeter and reached the corporate File Vault, "
            "an encrypted data archive containing classified corporate secrets and security logs."
        ),
        dialogue=[
            "Operative, we have successfully infiltrated the corporate File Vault.",
            "Record our reconnaissance telemetry by creating 'intel.txt'.",
            "Make a backup copy named 'intel.bak' before modifying critical data.",
            "Store the vault decryption passphrase 'OMNICORP' into 'intel.txt' using redirection.",
        ],
        objectives=[
            Objective(
                id="obj_1_1",
                description="Create an operative reconnaissance telemetry file named 'intel.txt'.",
                hint="Type 'touch intel.txt' at the prompt and press Enter to create the file.",
                command="touch",
                syntax="touch <filename>",
                explanation="Creates a new, empty file in the current working directory.",
                predicate_type="file_exists",
                predicate_target="intel.txt",
                xp_reward=75,
                hints=[
                    "Create an intel file named intel.txt to store reconnaissance findings.",
                    "Use 'touch' with the desired file name.",
                    "Execute 'touch intel.txt' at the prompt.",
                ],
                scenario="Create an active reconnaissance log before inspecting the vault archives.",
            ),
            Objective(
                id="obj_1_2",
                description="Duplicate your telemetry file to create a backup copy named 'intel.bak'.",
                hint="Type 'cp intel.txt intel.bak' at the prompt and press Enter to copy the file.",
                command="cp",
                syntax="cp <source_file> <dest_file>",
                explanation="Copies files or directories from a source location to a destination path.",
                predicate_type="file_exists",
                predicate_target="intel.bak",
                xp_reward=75,
                hints=[
                    "Duplicate your telemetry record so modifying it won't lose original state.",
                    "Check 'man cp' to review file copy syntax.",
                    "Run 'cp intel.txt intel.bak' to clone the file.",
                ],
                scenario="In corporate mainframe espionage, always duplicate critical intel files.",
            ),
            Objective(
                id="obj_1_3",
                description="Store the vault decryption code 'OMNICORP' into 'intel.txt' using redirection.",
                hint="Type 'echo \"OMNICORP\" > intel.txt' at the prompt and press Enter to store the key.",
                command="echo",
                syntax="echo <text> > <filename>",
                explanation="Outputs text; the redirect operator (>) writes the output into the target file.",
                predicate_type="file_contains",
                predicate_target="intel.txt",
                predicate_expected="OMNICORP",
                xp_reward=100,
                hints=[
                    "Write the authorization phrase OMNICORP into intel.txt.",
                    "Use 'echo' combined with the output redirection operator '>'.",
                    "Execute 'echo \"OMNICORP\" > intel.txt'.",
                ],
                scenario="Write the discovered clearance code into your intel log to authorize transmission.",
            ),
        ],
        reward_item=Item(
            id="item_vault_pass",
            name="Vault Pass",
            description="A cryptographic clearance pass required to route through the Sector 2 Datastream.",
            category="key",
            rarity="common",
        ),
        reward_xp=150,
        environment_tree={
            "vault_notes.txt": (
                "[VAULT ARCHIVE DIRECTORY]\n"
                "Security clearance required for datastream transit.\n"
                "Create an intel log and store the passkey OMNICORP.\n"
            ),
            ".vault_token": "VAULT_TOKEN=CIPHER_882_AUTH\n",
            ".secret": {
                ".vault_backup.key": "SECRET BONUS: Hidden vault passkey retrieved! (+50 XP)\n",
            },
        },
    )

    # Sector 2: The Datastream
    quests[2] = Quest(
        id="quest_sector_2",
        sector_id=2,
        sector_name="The Datastream",
        npc_name="Echo",
        lore=(
            "You are traversing the high-speed Datastream bus, "
            "the central conduit through which packets route across the entire mainframe."
        ),
        dialogue=[
            "The packet density in this sector is dangerously high. Millions of packets are flowing past.",
            "Construct a new directory folder named 'backup' for stream capture.",
            "Navigate into your new directory to isolate capture operations.",
            "Capture telemetry packets into 'packet.dump'.",
        ],
        objectives=[
            Objective(
                id="obj_2_1",
                description="Construct an isolated telemetry folder named 'backup'.",
                hint="Type 'mkdir backup' at the prompt and press Enter to construct the directory.",
                command="mkdir",
                syntax="mkdir <directory_name>",
                explanation="Creates one or more new directories in the filesystem.",
                predicate_type="file_exists",
                predicate_target="backup",
                xp_reward=100,
                hints=[
                    "Set up an isolated directory folder named 'backup'.",
                    "Check 'man mkdir' to see how directories are created.",
                    "Run 'mkdir backup' to make the folder.",
                ],
                scenario="Establish an isolated directory to avoid cluttering root datastream telemetry.",
            ),
            Objective(
                id="obj_2_2",
                description="Navigate inside the newly created 'backup' directory.",
                hint="Type 'cd backup' at the prompt and press Enter to enter the directory.",
                command="cd",
                syntax="cd <directory_path>",
                explanation="Changes your current working directory to the target directory path.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative/backup",
                xp_reward=100,
                hints=[
                    "Shift your active terminal context into the backup directory.",
                    "Use the change directory tool 'cd'.",
                    "Execute 'cd backup'.",
                ],
                scenario="Move your terminal session inside the storage folder.",
            ),
            Objective(
                id="obj_2_3",
                description="Capture incoming packet streams into 'packet.dump' inside backup.",
                hint="Type 'touch packet.dump' at the prompt and press Enter to create the capture file.",
                command="touch",
                syntax="touch <filename>",
                explanation="Creates a new file in your current active directory.",
                predicate_type="file_exists",
                predicate_target="/home/operative/backup/packet.dump",
                xp_reward=100,
                hints=[
                    "Create packet.dump in your current directory.",
                    "Use 'touch' with the filename.",
                    "Run 'touch packet.dump'.",
                ],
                scenario="Deploy a stream capture file to store packet telemetry.",
            ),
        ],
        reward_item=Item(
            id="item_data_cache",
            name="Data Cache Module",
            description="An expanded high-speed storage buffer for storing extracted mainframe data.",
            category="hardware",
            rarity="uncommon",
        ),
        reward_xp=200,
        environment_tree={
            "summary.txt": (
                "[DATASTREAM TELEMETRY]\n"
                "High density traffic dump available.\n"
                "Stage incoming streams in a dedicated backup folder.\n"
            ),
            "traffic.log": (
                "[04:10:00] TCP 192.168.1.1:443 -> 10.0.0.1:8080 ACK\n"
                "[04:12:15] UDP 192.168.1.5:53 -> 8.8.8.8:53 QUERY\n"
                "[04:15:33] CRITICAL_ALERT: Rogue stream signature AUTH_KEY=SIGMA-404-BYPASS\n"
                "[04:18:22] TCP 192.168.1.10:443 -> 10.0.0.1:8080 ACK\n"
            ),
        },
    )

    # Sector 3: Execution Core
    quests[3] = Quest(
        id="quest_sector_3",
        sector_id=3,
        sector_name="Execution Core",
        npc_name="Logic",
        lore=(
            "You have reached the Execution Core, the high-privilege engine "
            "where system automation daemons and background tasks run."
        ),
        dialogue=[
            "We located an automation script named 'run.sh', but its execution permissions have been locked.",
            "Restore read, write, and execute permissions (755) to 'run.sh' using chmod.",
            "Secure 'firewall.log' by setting permissions to owner-only read/write (chmod 600).",
            "Generate an operative countermeasure script named 'exploit.sh'.",
        ],
        objectives=[
            Objective(
                id="obj_3_1",
                description="Restore executable permissions (755) to the automation script 'run.sh' using chmod.",
                hint="Type 'chmod 755 /home/operative/run.sh' or navigate back home and run 'chmod 755 run.sh'.",
                command="chmod",
                syntax="chmod 755 <filename>",
                explanation="Changes file permissions: 7 (rwx owner), 5 (r-x group), 5 (r-x others).",
                predicate_type="permission_equals",
                predicate_target="/home/operative/run.sh",
                predicate_expected="755",
                xp_reward=150,
                hints=[
                    "Check the file permissions with 'ls -l', then update them.",
                    "Check 'man chmod' to review octal mode 755 (read, write, execute for owner).",
                    "Run 'chmod 755 /home/operative/run.sh' or 'chmod 755 run.sh'.",
                ],
                scenario="The diagnostic script cannot execute without proper execution permissions.",
            ),
            Objective(
                id="obj_3_2",
                description="Lock down sensitive security logs by setting permissions on 'firewall.log' to 600.",
                hint="Type 'chmod 600 /home/operative/firewall.log' at the prompt and press Enter.",
                command="chmod",
                syntax="chmod 600 <filename>",
                explanation="Restricts file access strictly to the owner (rw-------) for high security.",
                predicate_type="permission_equals",
                predicate_target="/home/operative/firewall.log",
                predicate_expected="600",
                xp_reward=150,
                hints=[
                    "Secure firewall.log so only the owner can read or write to it.",
                    "Mode 600 sets read/write for owner and denies access to group/others.",
                    "Execute 'chmod 600 /home/operative/firewall.log'.",
                ],
                scenario="Prevent unauthorized users from reading system firewall logs.",
            ),
            Objective(
                id="obj_3_3",
                description="Generate an operative countermeasure script named 'exploit.sh' using touch.",
                hint="Type 'touch /home/operative/exploit.sh' at the prompt and press Enter.",
                command="touch",
                syntax="touch <filename>",
                explanation="Creates a new script file in the target directory.",
                predicate_type="file_exists",
                predicate_target="/home/operative/exploit.sh",
                xp_reward=150,
                hints=[
                    "Create exploit.sh in /home/operative to stage payload delivery.",
                    "Use 'touch' with the full path or filename.",
                    "Run 'touch /home/operative/exploit.sh'.",
                ],
                scenario="Prepare the exploit script required for penetrating the next sector barrier.",
            ),
        ],
        reward_item=Item(
            id="item_logic_bomb",
            name="Logic Bomb Exploit",
            description="A custom-crafted logic bomb payload capable of puncturing mainframe firewall shields.",
            category="exploit",
            rarity="epic",
        ),
        reward_xp=300,
        environment_tree={
            "run.sh": {
                "content": '#!/bin/bash\necho "Execution Core operational."\n',
                "permissions": 0o644,
            },
            "firewall.log": {
                "content": "ERROR: Security perimeter breached.\nALERT: Sentinel Overlord daemon detected.\n",
                "permissions": 0o644,
            },
            "policy.txt": "Security Policy: Core scripts require 755; security logs require 600.\n",
        },
    )

    # Sector 4: The Firewall
    quests[4] = Quest(
        id="quest_sector_4",
        sector_id=4,
        sector_name="The Firewall",
        npc_name="Aegis",
        lore=(
            "You stand before the Firewall, the reinforced perimeter barrier "
            "that shields the central Sentinel Overlord AI from outside intrusion."
        ),
        dialogue=[
            "The firewall's exterior shields are impenetrable to direct brute-force connections.",
            "Read through perimeter security records using 'cat /home/operative/firewall.log'.",
            "Append the bypass key 'BYPASS_ALPHA' to the log using the '>>' redirect operator.",
            "Construct a dedicated folder for breach exploits at '/home/operative/exploits' using mkdir.",
        ],
        objectives=[
            Objective(
                id="obj_4_1",
                description="Inspect the perimeter defense records by reading 'firewall.log' using cat.",
                hint="Type 'cat /home/operative/firewall.log' at the prompt and press Enter.",
                command="cat",
                syntax="cat <filename>",
                explanation="Concatenates and displays the entire contents of a file to your terminal.",
                predicate_type="file_exists",
                predicate_target="/home/operative/firewall.log",
                xp_reward=200,
                hints=[
                    "Inspect the defense records stored in firewall.log.",
                    "Check 'man cat' to see how files are read and output to the terminal.",
                    "Run 'cat /home/operative/firewall.log'.",
                ],
                scenario="Read through the firewall security logs to identify bypass opportunities.",
            ),
            Objective(
                id="obj_4_2",
                description="Append the bypass code 'BYPASS_ALPHA' to 'firewall.log' using the >> redirect operator.",
                hint="Type 'echo \"BYPASS_ALPHA\" >> /home/operative/firewall.log' at the prompt and press Enter.",
                command="echo",
                syntax="echo <text> >> <filename>",
                explanation="The >> operator appends output to the end of a file without overwriting it.",
                predicate_type="file_contains",
                predicate_target="/home/operative/firewall.log",
                predicate_expected="BYPASS_ALPHA",
                xp_reward=200,
                hints=[
                    "Append the authorization bypass code to the end of firewall.log.",
                    "Use 'echo' with the append operator '>>' so previous contents remain intact.",
                    "Execute 'echo \"BYPASS_ALPHA\" >> /home/operative/firewall.log'.",
                ],
                scenario="Inject the bypass authentication key directly into the active firewall stream.",
            ),
            Objective(
                id="obj_4_3",
                description="Construct a dedicated folder for final breach exploits named '/home/operative/exploits'.",
                hint="Type 'mkdir -p /home/operative/exploits' at the prompt and press Enter.",
                command="mkdir",
                syntax="mkdir -p <path>",
                explanation="Creates directory path hierarchies, including parent directories as needed (-p).",
                predicate_type="file_exists",
                predicate_target="/home/operative/exploits",
                xp_reward=200,
                hints=[
                    "Create the directory path /home/operative/exploits.",
                    "Check 'man mkdir' to review the -p flag for creating parent folders if needed.",
                    "Run 'mkdir -p /home/operative/exploits'.",
                ],
                scenario="Build a dedicated repository folder for staging root breach tools.",
            ),
        ],
        reward_item=Item(
            id="item_shield_breaker",
            name="Shield Breaker Key",
            description="A legendary hardware key that disables the Sentinel Overlord's invulnerability shield.",
            category="exploit",
            rarity="legendary",
        ),
        reward_xp=400,
        environment_tree={
            "firewall.log": (
                "DROP packet from 10.0.0.1\n"
                "ALERT: BREACH_ALERT connection established\n"
                "PASS packet to 192.168.1.5\n"
            ),
            "rules.conf": "Firewall Rule 1: Append bypass key >> to permit passage.\n",
        },
    )

    # Sector 5: Sentinel Boss
    quests[5] = Quest(
        id="quest_sector_5",
        sector_id=5,
        sector_name="Sentinel Overlord",
        npc_name="Overlord",
        lore=(
            "CRITICAL ALERT: You have penetrated the inner sanctum. "
            "The rogue Sentinel Overlord AI has initiated deletion protocols to purge your operative connection."
        ),
        dialogue=[
            "INTRUDER DETECTED. You have reached the core of AEGIS-9.",
            "Breach my central root chamber with 'cd /root' to challenge administrative control!",
            "Lock down the rogue daemon by creating '/root/override.lock' with touch.",
            "Plant the system liberation flag with 'echo \"SYSTEM_RESTORED\" > /root/core.flag'!",
        ],
        objectives=[
            Objective(
                id="obj_5_1",
                description="Breach the central mainframe root chamber by navigating to '/root'.",
                hint="Type 'cd /root' at the prompt and press Enter to access the system root chamber.",
                command="cd",
                syntax="cd /root",
                explanation="Navigates directly to the system root administrative directory.",
                predicate_type="cwd_equals",
                predicate_target="/root",
                xp_reward=400,
                hints=[
                    "Move into the central administrative chamber at /root.",
                    "Use 'cd' with the target absolute path.",
                    "Run 'cd /root'.",
                ],
                scenario="Access the core administrative chamber where the rogue AI process executes.",
            ),
            Objective(
                id="obj_5_2",
                description="Establish an administrative security lockfile named '/root/override.lock'.",
                hint="Type 'touch /root/override.lock' at the prompt and press Enter to lock the core.",
                command="touch",
                syntax="touch /root/override.lock",
                explanation="Creates an administrative override lockfile in the system root chamber.",
                predicate_type="file_exists",
                predicate_target="/root/override.lock",
                xp_reward=400,
                hints=[
                    "Create the override.lock file inside /root to halt AI deletion threads.",
                    "Use 'touch' with the destination path.",
                    "Execute 'touch /root/override.lock'.",
                ],
                scenario="Lock down the rogue deletion daemon before it purges operative telemetry.",
            ),
            Objective(
                id="obj_5_3",
                description="Plant the liberation flag by writing 'SYSTEM_RESTORED' into '/root/core.flag'.",
                hint="Type 'echo \"SYSTEM_RESTORED\" > /root/core.flag' at the prompt and press Enter!",
                command="echo",
                syntax="echo \"SYSTEM_RESTORED\" > /root/core.flag",
                explanation="Writes the system liberation flag to purge the Overlord and free the mainframe.",
                predicate_type="file_contains",
                predicate_target="/root/core.flag",
                predicate_expected="SYSTEM_RESTORED",
                xp_reward=500,
                hints=[
                    "Broadcast the liberation flag code into /root/core.flag.",
                    "Use 'echo' with the redirect operator '>' to write to the file.",
                    "Run 'echo \"SYSTEM_RESTORED\" > /root/core.flag'.",
                ],
                scenario="Neutralize Sentinel Overlord and liberate the entire corporate mainframe!",
            ),
        ],
        reward_item=Item(
            id="item_root_access",
            name="Root Access Key",
            description="Total administrative supremacy over OMNICORP's central mainframe.",
            category="artifact",
            rarity="mythic",
        ),
        reward_xp=1000,
        environment_tree={
            "/root": {
                "overlord.conf": (
                    "[SENTINEL OVERLORD CONTROL CORE]\n"
                    "STATUS: HOSTILE_TAKEOVER\n"
                    "OVERRIDE_PASSPHRASE=\"SYSTEM_RESTORED\"\n"
                ),
                "daemon.lock": "DAEMON LOCK ACTIVE\n",
            },
        },
    )

    return quests
