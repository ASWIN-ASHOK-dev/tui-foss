"""Story and Quest Definitions for CyberShell RPG.

Author: Neha (Narrative & Quests)
"""

from cybershell.contracts import Objective, Quest, Item

def get_sector_quests() -> dict[int, Quest]:
    """Returns a dictionary mapping sector IDs to their Quests."""
    quests = {}

    # Sector 0: Quarantine Zone
    quests[0] = Quest(
        id="quest_sector_0",
        sector_id=0,
        sector_name="Quarantine Zone",
        npc_name="Byte",
        lore="You wake up in an isolated sandbox with memory corruption.",
        dialogue=[
            "Operative! Welcome back to the grid.",
            "Type 'pwd' to check sector coordinates, or 'ls -la' to scan for security keys.",
        ],
        objectives=[
            Objective(
                id="obj_0_1",
                description="Determine mainframe position with 'pwd'",
                hint="Type 'pwd'",
                predicate_type="cwd_equals",
                predicate_target="/home/operative",
                xp_reward=50,
            ),
            Objective(
                id="obj_0_2",
                description="List quarantine contents with 'ls -la'",
                hint="Type 'ls -la'",
                predicate_type="file_exists",
                predicate_target="/home/operative",
                xp_reward=50,
            ),
        ],
        reward_item=Item(
            id="item_quarantine_chip",
            name="Quarantine Keychip",
            description="Grants clearance to Sector 1 File Vault.",
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
        lore="A massive repository of corporate secrets.",
        dialogue=[
            "We need to create a log file to track our movements.",
            "Use 'touch' to create an empty file named 'intel.txt'.",
        ],
        objectives=[
            Objective(
                id="obj_1_1",
                description="Create intel.txt",
                hint="Type 'touch intel.txt'",
                predicate_type="file_exists",
                predicate_target="intel.txt",
                xp_reward=75,
            )
        ],
        reward_item=Item(
            id="item_vault_pass",
            name="Vault Pass",
            description="Access pass for Sector 2.",
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
        lore="The primary data bus connecting the mainframe.",
        dialogue=[
            "We need to organize the data.",
            "Use 'mkdir' to create a directory called 'backup'.",
        ],
        objectives=[
            Objective(
                id="obj_2_1",
                description="Create backup directory",
                hint="Type 'mkdir backup'",
                predicate_type="file_exists",
                predicate_target="backup",
                xp_reward=100,
            )
        ],
        reward_item=Item(
            id="item_data_cache",
            name="Data Cache",
            description="Extra storage for logs.",
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
        lore="Where the heavy processing happens.",
        dialogue=[
            "There's an executable file 'run.sh' that needs the right permissions.",
            "Use 'chmod 755 run.sh' to make it executable.",
        ],
        objectives=[
            Objective(
                id="obj_3_1",
                description="Change permissions of run.sh to 755",
                hint="Type 'chmod 755 run.sh'",
                predicate_type="permission_equals",
                predicate_target="run.sh",
                predicate_expected="755",
                xp_reward=150,
            )
        ],
        reward_item=Item(
            id="item_logic_bomb",
            name="Logic Bomb",
            description="Explosive code payload.",
            category="weapon",
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
        lore="The last line of defense before the Sentinel Boss.",
        dialogue=[
            "The firewall logs contain the key to bypass the outer shield.",
            "Read 'firewall.log' using 'cat'.",
        ],
        objectives=[
            Objective(
                id="obj_4_1",
                description="Read firewall.log",
                hint="Type 'cat firewall.log'",
                predicate_type="file_exists",
                predicate_target="firewall.log",
                xp_reward=200,
            )
        ],
        reward_item=Item(
            id="item_shield_breaker",
            name="Shield Breaker",
            description="Bypasses firewall protocols.",
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
        lore="The core security AI protecting the system.",
        dialogue=[
            "INTRUDER DETECTED. PREPARE FOR DELETION.",
            "You cannot defeat me with simple shell commands.",
        ],
        objectives=[
            Objective(
                id="obj_5_1",
                description="Defeat the Sentinel Boss (Simulated via command)",
                hint="Use advanced pipelines and exploits.",
                predicate_type="cwd_equals",
                predicate_target="/root",
                xp_reward=500,
            )
        ],
        reward_item=Item(
            id="item_root_access",
            name="Root Access Key",
            description="Total control over the system.",
            category="artifact",
            rarity="mythic",
        ),
        reward_xp=1000,
    )

    return quests
