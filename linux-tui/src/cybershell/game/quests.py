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
            "First, verify your mainframe location using 'pwd'.",
            "Next, inspect the sandbox contents using 'ls -la'.",
            "Finally, establish our communications beacon using 'touch beacon.log'.",
        ],
        objectives=[
            Objective(
                id="obj_0_1",
                description="Determine your current directory coordinates inside the quarantine sandbox using 'pwd'.",
                hint="Type 'pwd' at the prompt and press Enter to verify your location.",
                command="pwd",
                syntax="pwd",
                explanation="Prints the absolute pathname of your current working directory.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative",
                xp_reward=50,
            ),
            Objective(
                id="obj_0_2",
                description="Scan the quarantine filesystem for hidden files and security tokens using 'ls -la'.",
                hint="Type 'ls -la' at the prompt and press Enter to inspect all files and permissions.",
                command="ls",
                syntax="ls -la",
                explanation="Lists directory contents with detailed file permissions (-l) and hidden dotfiles (-a).",
                predicate_type="file_exists",
                predicate_target="/home/operative",
                xp_reward=50,
            ),
            Objective(
                id="obj_0_3",
                description="Deploy an operative status beacon file named 'beacon.log' using touch.",
                hint="Type 'touch beacon.log' at the prompt and press Enter to deploy the beacon.",
                command="touch",
                syntax="touch <filename>",
                explanation="Creates a new empty file or updates the timestamp of an existing file.",
                predicate_type="file_exists",
                predicate_target="beacon.log",
                xp_reward=50,
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
            "Record our reconnaissance telemetry by creating 'intel.txt' with touch.",
            "Make a backup copy named 'intel.bak' with cp before modifying data.",
            "Write the decryption key 'OMNICORP' into 'intel.txt' using echo and redirect (>).",
        ],
        objectives=[
            Objective(
                id="obj_1_1",
                description="Create an operative reconnaissance telemetry file named 'intel.txt' using touch.",
                hint="Type 'touch intel.txt' at the prompt and press Enter to create the file.",
                command="touch",
                syntax="touch <filename>",
                explanation="Creates a new, empty file in the current working directory.",
                predicate_type="file_exists",
                predicate_target="intel.txt",
                xp_reward=75,
            ),
            Objective(
                id="obj_1_2",
                description="Duplicate your telemetry file to create a backup copy named 'intel.bak' using cp.",
                hint="Type 'cp intel.txt intel.bak' at the prompt and press Enter to copy the file.",
                command="cp",
                syntax="cp <source_file> <dest_file>",
                explanation="Copies files or directories from a source location to a destination path.",
                predicate_type="file_exists",
                predicate_target="intel.bak",
                xp_reward=75,
            ),
            Objective(
                id="obj_1_3",
                description="Write the decrypted vault code 'OMNICORP' into 'intel.txt' using echo and redirect (>).",
                hint="Type 'echo \"OMNICORP\" > intel.txt' at the prompt and press Enter to store the key.",
                command="echo",
                syntax="echo <text> > <filename>",
                explanation="Outputs text; the redirect operator (>) writes the output into the target file.",
                predicate_type="file_contains",
                predicate_target="intel.txt",
                predicate_expected="OMNICORP",
                xp_reward=100,
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
            "Construct a new directory folder named 'backup' using mkdir.",
            "Navigate into your new directory using 'cd backup'.",
            "Capture telemetry packets into 'packet.dump' using touch.",
        ],
        objectives=[
            Objective(
                id="obj_2_1",
                description="Establish an organized telemetry repository by creating a directory named 'backup'.",
                hint="Type 'mkdir backup' at the prompt and press Enter to construct the directory.",
                command="mkdir",
                syntax="mkdir <directory_name>",
                explanation="Creates one or more new directories in the filesystem.",
                predicate_type="file_exists",
                predicate_target="backup",
                xp_reward=100,
            ),
            Objective(
                id="obj_2_2",
                description="Navigate inside the newly created 'backup' directory using the cd command.",
                hint="Type 'cd backup' at the prompt and press Enter to enter the directory.",
                command="cd",
                syntax="cd <directory_path>",
                explanation="Changes your current working directory to the target directory path.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative/backup",
                xp_reward=100,
            ),
            Objective(
                id="obj_2_3",
                description="Capture incoming packet streams by creating a file named 'packet.dump' in backup.",
                hint="Type 'touch packet.dump' at the prompt and press Enter to create the capture file.",
                command="touch",
                syntax="touch <filename>",
                explanation="Creates a new file in your current active directory.",
                predicate_type="file_exists",
                predicate_target="/home/operative/backup/packet.dump",
                xp_reward=100,
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
            "Use 'chmod 755 /home/operative/run.sh' to grant read, write, and execute permissions.",
            "Secure 'firewall.log' by setting permissions to owner-only read/write (chmod 600).",
            "Generate an operative countermeasure script named 'exploit.sh' using touch.",
        ],
        objectives=[
            Objective(
                id="obj_3_1",
                description="Grant executable permissions (755) to the automation script 'run.sh' using chmod.",
                hint="Type 'chmod 755 /home/operative/run.sh' or navigate back home and run 'chmod 755 run.sh'.",
                command="chmod",
                syntax="chmod 755 <filename>",
                explanation="Changes file permissions: 7 (rwx owner), 5 (r-x group), 5 (r-x others).",
                predicate_type="permission_equals",
                predicate_target="/home/operative/run.sh",
                predicate_expected="755",
                xp_reward=150,
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
                description="Inspect the perimeter defense records by reading 'firewall.log' using the cat command.",
                hint="Type 'cat /home/operative/firewall.log' at the prompt and press Enter.",
                command="cat",
                syntax="cat <filename>",
                explanation="Concatenates and displays the entire contents of a file to your terminal.",
                predicate_type="file_exists",
                predicate_target="/home/operative/firewall.log",
                xp_reward=200,
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
                description="Breach the central mainframe root chamber by navigating to '/root' using the cd command.",
                hint="Type 'cd /root' at the prompt and press Enter to access the system root chamber.",
                command="cd",
                syntax="cd /root",
                explanation="Navigates directly to the system root administrative directory.",
                predicate_type="cwd_equals",
                predicate_target="/root",
                xp_reward=400,
            ),
            Objective(
                id="obj_5_2",
                description="Establish an administrative security lockfile named '/root/override.lock' using touch.",
                hint="Type 'touch /root/override.lock' at the prompt and press Enter to lock the core.",
                command="touch",
                syntax="touch /root/override.lock",
                explanation="Creates an administrative override lockfile in the system root chamber.",
                predicate_type="file_exists",
                predicate_target="/root/override.lock",
                xp_reward=400,
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
    )

    return quests
