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
            "First, we need to verify your mainframe location. Type 'pwd' to confirm your current directory.",
            "Once you know your coordinates, run 'ls -la' to scan the quarantine sandbox for security keys.",
        ],
        objectives=[
            Objective(
                id="obj_0_1",
                description="Determine your current directory coordinates inside the quarantine sandbox using 'pwd'.",
                hint="Type 'pwd' at the prompt and press Enter to verify your location.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative",
                xp_reward=50,
            ),
            Objective(
                id="obj_0_2",
                description="Scan the quarantine filesystem for hidden files and security tokens using 'ls -la'.",
                hint="Type 'ls -la' at the prompt and press Enter to inspect all files and permissions.",
                predicate_type="file_exists",
                predicate_target="/home/operative",
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
            "To record our reconnaissance telemetry, we must create a dedicated log file.",
            "Use the 'touch' command to create a new file named 'intel.txt' in this directory.",
        ],
        objectives=[
            Objective(
                id="obj_1_1",
                description="Create an operative reconnaissance telemetry file named 'intel.txt' using touch.",
                hint="Type 'touch intel.txt' at the prompt and press Enter to create the file.",
                predicate_type="file_exists",
                predicate_target="intel.txt",
                xp_reward=75,
            )
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
            "We need a dedicated repository to capture and organize incoming telemetry streams.",
            "Use the 'mkdir' command to create a new directory named 'backup'.",
        ],
        objectives=[
            Objective(
                id="obj_2_1",
                description="Establish an organized telemetry repository by creating a directory named 'backup'.",
                hint="Type 'mkdir backup' at the prompt and press Enter to construct the directory.",
                predicate_type="file_exists",
                predicate_target="backup",
                xp_reward=100,
            )
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
            "Without execution rights, our payload will be blocked by the kernel.",
            "Use 'chmod 755 run.sh' to grant read, write, and execute permissions to the script.",
        ],
        objectives=[
            Objective(
                id="obj_3_1",
                description="Grant executable permissions (755) to the automation script 'run.sh' using chmod.",
                hint="Type 'chmod 755 run.sh' at the prompt and press Enter to make the script executable.",
                predicate_type="permission_equals",
                predicate_target="run.sh",
                predicate_expected="755",
                xp_reward=150,
            )
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
            "However, recent intrusion telemetry is stored inside 'firewall.log'.",
            "Read through the security records using the 'cat' command to extract the bypass key.",
        ],
        objectives=[
            Objective(
                id="obj_4_1",
                description="Inspect the perimeter defense records by reading 'firewall.log' using the cat command.",
                hint="Type 'cat firewall.log' at the prompt and press Enter to read the file contents.",
                predicate_type="file_exists",
                predicate_target="firewall.log",
                xp_reward=200,
            )
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
            "Your simple shell commands cannot pierce my defensive subroutines.",
            "Breach my central root chamber with 'cd /root' to claim administrative victory!",
        ],
        objectives=[
            Objective(
                id="obj_5_1",
                description="Breach the central mainframe root chamber by navigating to '/root' using the cd command.",
                hint="Type 'cd /root' at the prompt and press Enter to achieve total root control.",
                predicate_type="cwd_equals",
                predicate_target="/root",
                xp_reward=500,
            )
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
