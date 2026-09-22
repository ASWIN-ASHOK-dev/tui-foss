"""Byte's Linux Adventure - 15 Adventure Levels & Quests.

Friendly, playful exploration scenarios teaching Linux fundamentals step by step.
"""

from __future__ import annotations

from typing import Dict

from cybershell.contracts import Item, Objective, Quest


def get_sector_quests() -> Dict[int, Quest]:
    """Returns a dictionary mapping level IDs (0-14 for Levels 1-15) to their Quests."""
    quests: Dict[int, Quest] = {}

    # -------------------------------------------------------------------------
    # LEVEL 1: LOOK AROUND (pwd, ls)
    # -------------------------------------------------------------------------
    quests[0] = Quest(
        id="level_01",
        sector_id=0,
        sector_name="Look Around",
        npc_name="Byte",
        lore="You just arrived in your new Linux world! Let's get our bearings and see what is nearby.",
        dialogue=[
            "Hello! I'm Byte, your friendly guide.",
            "Whenever you arrive in a new folder, two commands are super handy: 'pwd' and 'ls'.",
            "Let's find where you are first!",
        ],
        objectives=[
            Objective(
                id="obj_1_1",
                description="Find where you are in the computer using pwd.",
                hint="Type 'pwd' and press Enter to see your current directory path.",
                command="pwd",
                syntax="pwd",
                explanation="Prints your current working directory path.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative",
                xp_reward=50,
                hints=[
                    "Which command prints your current folder location?",
                    "It stands for 'Print Working Directory'.",
                    "Type: pwd",
                ],
                scenario="You just arrived. Where are you in the filesystem?",
            ),
            Objective(
                id="obj_1_2",
                description="Look around to see what files are nearby using ls.",
                hint="Type 'ls' and press Enter to list the files in this folder.",
                command="ls",
                syntax="ls",
                explanation="Lists the files and folders in your current location.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative",
                xp_reward=50,
                hints=[
                    "Use the list command to see nearby files and folders.",
                    "The command is just two letters: l and s.",
                    "Type: ls",
                ],
                scenario="Now look around. Something useful is nearby.",
            ),
        ],
        reward_item=Item(
            id="item_compass",
            name="Wooden Compass 🧭",
            description="Helps you always find your bearings in any folder.",
            category="tool",
            rarity="common",
        ),
        reward_xp=100,
        environment_tree={
            "welcome.txt": "Welcome to your Linux Adventure! There is so much to explore.\n",
            "notes.txt": "Tip: 'pwd' tells you where you are, and 'ls' shows you what's around!\n",
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 2: FOLLOW THE PATH (cd, ..)
    # -------------------------------------------------------------------------
    quests[1] = Quest(
        id="level_02",
        sector_id=1,
        sector_name="Follow the Path",
        npc_name="Byte",
        lore="Look! There is a cozy garden folder right here. Let's step inside and explore it.",
        dialogue=[
            "Moving between folders is just like walking through rooms in a house.",
            "Use 'cd' followed by the folder name to step inside!",
        ],
        objectives=[
            Objective(
                id="obj_2_1",
                description="Step inside the 'garden' folder using cd garden.",
                hint="Type 'cd garden' and press Enter to walk into the garden.",
                command="cd",
                syntax="cd garden",
                explanation="Changes your current directory to the garden folder.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative/garden",
                xp_reward=50,
                hints=[
                    "Use the change directory command 'cd' with 'garden'.",
                    "Remember to put a space after 'cd'.",
                    "Type: cd garden",
                ],
                scenario="There's a folder here. What's inside?",
            ),
            Objective(
                id="obj_2_2",
                description="Step back out to your home folder using cd ..",
                hint="Type 'cd ..' and press Enter to move up one folder level.",
                command="cd",
                syntax="cd ..",
                explanation="'..' refers to the parent folder one level up.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative",
                xp_reward=50,
                hints=[
                    "Two dots (..) represent the folder above you.",
                    "Type 'cd ..' with a space between cd and ..",
                    "Type: cd ..",
                ],
                scenario="Nice! Now step back out to return to your home base.",
            ),
        ],
        reward_item=Item(
            id="item_shoes",
            name="Walking Shoes 👟",
            description="Comfy shoes for walking through directories.",
            category="clothing",
            rarity="common",
        ),
        reward_xp=100,
        environment_tree={
            "garden": {
                "flowers.txt": "Sunflowers, daisies, and lavender grow here peacefully. 🌸\n",
                "bench.txt": "A warm wooden bench where you can sit and code.\n",
            },
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 3: READ THE NOTE (cat, less)
    # -------------------------------------------------------------------------
    quests[2] = Quest(
        id="level_03",
        sector_id=2,
        sector_name="Read the Note",
        npc_name="Penny",
        lore="Someone left a friendly letter named 'welcome.txt' on the desk. Let's read what it says!",
        dialogue=[
            "Hi there! I'm Penny the archivist.",
            "You can read text files directly on your screen using 'cat' or 'less'.",
        ],
        objectives=[
            Objective(
                id="obj_3_1",
                description="Read the contents of 'welcome.txt' using cat welcome.txt.",
                hint="Type 'cat welcome.txt' and press Enter to read the note.",
                command="cat,less",
                syntax="cat <filename>",
                explanation="Outputs the text inside a file right onto your terminal.",
                predicate_type="file_read",
                predicate_target="welcome.txt",
                xp_reward=100,
                hints=[
                    "The 'cat' command prints file contents to your terminal.",
                    "Specify the file name after the command.",
                    "Type: cat welcome.txt",
                ],
                scenario="You found a note! Read it.",
            ),
        ],
        reward_item=Item(
            id="item_magnifier",
            name="Magnifying Glass 🔍",
            description="Helps you inspect file contents with ease.",
            category="tool",
            rarity="uncommon",
        ),
        reward_xp=100,
        environment_tree={
            "welcome.txt": "Great job! Reading files is one of the most essential Linux skills.\nKeep exploring! 🌱\n",
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 4: HIDDEN STUFF (ls -a)
    # -------------------------------------------------------------------------
    quests[3] = Quest(
        id="level_04",
        sector_id=3,
        sector_name="Hidden Stuff",
        npc_name="Byte",
        lore="In Linux, any file that starts with a dot '.' is hidden from regular view. Let's find what's hiding!",
        dialogue=[
            "Normal 'ls' keeps hidden dotfiles out of your way.",
            "Passing the '-a' flag (all) will reveal everything in the room!",
        ],
        objectives=[
            Objective(
                id="obj_4_1",
                description="Reveal hidden files using ls -a.",
                hint="Type 'ls -a' and press Enter to see all files, including dotfiles.",
                command="ls",
                syntax="ls -a",
                explanation="Lists all directory contents, including hidden files beginning with a dot.",
                predicate_type="pattern_matched",
                predicate_target="ls",
                predicate_expected="-a",
                xp_reward=50,
                hints=[
                    "Use the '-a' flag with 'ls' to show all files.",
                    "Make sure there is a space between ls and -a.",
                    "Type: ls -a",
                ],
                scenario="Someone hid a secret file here. Standard ls won't show it!",
            ),
            Objective(
                id="obj_4_2",
                description="Read the hidden secret recipe using cat .secret_recipe.",
                hint="Type 'cat .secret_recipe' and press Enter to read the secret.",
                command="cat,less",
                syntax="cat .secret_recipe",
                explanation="Reads the hidden file contents.",
                predicate_type="file_read",
                predicate_target=".secret_recipe",
                xp_reward=50,
                hints=[
                    "Don't forget the leading dot in the filename!",
                    "Type: cat .secret_recipe",
                    "Type: cat .secret_recipe",
                ],
                scenario="You spotted the hidden file! Read what is inside.",
            ),
        ],
        reward_item=Item(
            id="item_flashlight",
            name="Pocket Flashlight 🔦",
            description="Shines bright light onto hidden dotfiles.",
            category="tool",
            rarity="uncommon",
        ),
        reward_xp=100,
        environment_tree={
            ".secret_recipe": "Secret Cookie Recipe: 2 cups flour, 1 cup chocolate chips, lots of love! 🍪\n",
            "ordinary_list.txt": "Milk, eggs, flour.\n",
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 5: FIND IT (find)
    # -------------------------------------------------------------------------
    quests[4] = Quest(
        id="level_05",
        sector_id=4,
        sector_name="Find It",
        npc_name="Fern",
        lore="A lost key file named 'treasure.txt' is buried deep inside a maze of folders. Let's track it down!",
        dialogue=[
            "Hello! I'm Fern.",
            "Instead of clicking through every folder, Linux has a magic wand: the 'find' command!",
        ],
        objectives=[
            Objective(
                id="obj_5_1",
                description="Locate 'treasure.txt' anywhere in the current folder using find.",
                hint="Type 'find . -name \"treasure.txt\"' and press Enter.",
                command="find",
                syntax="find . -name \"treasure.txt\"",
                explanation="Searches the current directory '.' recursively for files matching the pattern.",
                predicate_type="pattern_matched",
                predicate_target="find",
                predicate_expected="treasure.txt",
                xp_reward=100,
                hints=[
                    "Use 'find .' with the '-name' option.",
                    "Look for 'treasure.txt'.",
                    "Type: find . -name \"treasure.txt\"",
                ],
                scenario="A lost file is buried deep in subfolders. Find where it is!",
            ),
        ],
        reward_item=Item(
            id="item_detector",
            name="Metal Detector 🧭",
            description="Locates lost files buried across deep subdirectories.",
            category="tool",
            rarity="rare",
        ),
        reward_xp=100,
        environment_tree={
            "chest": {
                "compartment": {
                    "deep_pocket": {
                        "treasure.txt": "You found the hidden treasure! 💎\n",
                    },
                },
            },
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 6: SEARCH INSIDE (grep)
    # -------------------------------------------------------------------------
    quests[5] = Quest(
        id="level_06",
        sector_id=5,
        sector_name="Search Inside",
        npc_name="Byte",
        lore="There is a long list of items in 'items.txt'. We need to find the line with the word 'banana'!",
        dialogue=[
            "Reading line-by-line is slow.",
            "The 'grep' command filters through text instantly and prints only matching lines!",
        ],
        objectives=[
            Objective(
                id="obj_6_1",
                description="Search for 'banana' in 'items.txt' using grep.",
                hint="Type 'grep \"banana\" items.txt' and press Enter.",
                command="grep",
                syntax="grep \"banana\" items.txt",
                explanation="Searches for matching text pattern inside a file.",
                predicate_type="pattern_matched",
                predicate_target="items.txt",
                predicate_expected="banana",
                xp_reward=100,
                hints=[
                    "Use 'grep <word> <filename>'.",
                    "Look for the word 'banana' inside 'items.txt'.",
                    "Type: grep \"banana\" items.txt",
                ],
                scenario="Find the file line containing the word 'banana'.",
            ),
        ],
        reward_item=Item(
            id="item_catcher",
            name="Word Catcher 🪤",
            description="Filters and catches any word across long files.",
            category="tool",
            rarity="rare",
        ),
        reward_xp=100,
        environment_tree={
            "items.txt": "apple\ncherry\nsweet yellow banana\ngrape\nwatermelon\n",
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 7: COPY & MOVE (cp, mv)
    # -------------------------------------------------------------------------
    quests[6] = Quest(
        id="level_07",
        sector_id=6,
        sector_name="Copy & Move",
        npc_name="Oliver",
        lore="Let's organize our desk! Make a backup copy of 'drawing.txt' and move 'photo.png' into 'gallery/'.",
        dialogue=[
            "Hi! I'm Oliver the organizer.",
            "'cp' makes a duplicate copy, while 'mv' moves or renames a file.",
        ],
        objectives=[
            Objective(
                id="obj_7_1",
                description="Make a copy of 'drawing.txt' named 'drawing_backup.txt' using cp.",
                hint="Type 'cp drawing.txt drawing_backup.txt' and press Enter.",
                command="cp",
                syntax="cp drawing.txt drawing_backup.txt",
                explanation="Copies source file to destination filename.",
                predicate_type="file_exists",
                predicate_target="drawing_backup.txt",
                xp_reward=50,
                hints=[
                    "Use 'cp source destination'.",
                    "Source is 'drawing.txt', destination is 'drawing_backup.txt'.",
                    "Type: cp drawing.txt drawing_backup.txt",
                ],
                scenario="Duplicate your drawing so you never lose the original.",
            ),
            Objective(
                id="obj_7_2",
                description="Move 'photo.png' into the 'gallery/' folder using mv.",
                hint="Type 'mv photo.png gallery/' and press Enter.",
                command="mv",
                syntax="mv photo.png gallery/",
                explanation="Moves a file into a target directory.",
                predicate_type="file_exists",
                predicate_target="gallery/photo.png",
                xp_reward=50,
                hints=[
                    "Use 'mv <file> <folder>/'.",
                    "Move 'photo.png' into 'gallery/'.",
                    "Type: mv photo.png gallery/",
                ],
                scenario="Put the photo away into the gallery folder.",
            ),
        ],
        reward_item=Item(
            id="item_toolbox",
            name="Handy Toolbox 🧰",
            description="Handy tools for moving and copying files effortlessly.",
            category="tool",
            rarity="rare",
        ),
        reward_xp=100,
        environment_tree={
            "drawing.txt": "A cheerful sketch of a green seedling. 🌱\n",
            "photo.png": "Picture of a peaceful morning sunrise. 🌅\n",
            "gallery": {},
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 8: CLEAN UP (rm, mkdir, touch)
    # -------------------------------------------------------------------------
    quests[7] = Quest(
        id="level_08",
        sector_id=7,
        sector_name="Clean Up",
        npc_name="Byte",
        lore="Let's tidy up! Delete the junk file, make a new 'workspace' folder, and create a 'workspace/todo.txt'.",
        dialogue=[
            "A clean workspace is a happy workspace.",
            "'rm' deletes unwanted files, 'mkdir' creates folders, and 'touch' creates empty files.",
        ],
        objectives=[
            Objective(
                id="obj_8_1",
                description="Delete the temporary junk file 'junk.tmp' using rm.",
                hint="Type 'rm junk.tmp' and press Enter.",
                command="rm",
                syntax="rm junk.tmp",
                explanation="Removes a file from the filesystem.",
                predicate_type="file_not_exists",
                predicate_target="junk.tmp",
                xp_reward=40,
                hints=[
                    "Use 'rm' with the filename to delete it.",
                    "Type: rm junk.tmp",
                    "Type: rm junk.tmp",
                ],
                scenario="Clear away the leftover junk file.",
            ),
            Objective(
                id="obj_8_2",
                description="Create a new folder named 'workspace' using mkdir.",
                hint="Type 'mkdir workspace' and press Enter.",
                command="mkdir",
                syntax="mkdir workspace",
                explanation="Creates a new directory folder.",
                predicate_type="file_exists",
                predicate_target="workspace",
                xp_reward=40,
                hints=[
                    "Use 'mkdir' to make a new directory.",
                    "Type: mkdir workspace",
                    "Type: mkdir workspace",
                ],
                scenario="Create a fresh new folder for your projects.",
            ),
            Objective(
                id="obj_8_3",
                description="Create an empty file 'workspace/todo.txt' using touch.",
                hint="Type 'touch workspace/todo.txt' and press Enter.",
                command="touch",
                syntax="touch workspace/todo.txt",
                explanation="Creates a new empty file in the workspace directory.",
                predicate_type="file_exists",
                predicate_target="workspace/todo.txt",
                xp_reward=40,
                hints=[
                    "Use 'touch' with the destination path.",
                    "Type: touch workspace/todo.txt",
                    "Type: touch workspace/todo.txt",
                ],
                scenario="Start a new todo list inside your workspace.",
            ),
        ],
        reward_item=Item(
            id="item_broom",
            name="Little Broom 🧹",
            description="Keeps your filesystem spick and span.",
            category="tool",
            rarity="rare",
        ),
        reward_xp=120,
        environment_tree={
            "junk.tmp": "Old temporary scratch notes that are no longer needed.\n",
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 9: WHO CAN OPEN THIS? (chmod)
    # -------------------------------------------------------------------------
    quests[8] = Quest(
        id="level_09",
        sector_id=8,
        sector_name="Who Can Open This?",
        npc_name="Penny",
        lore="We have a fun mini-game script 'play.sh', but it doesn't have execute permission yet!",
        dialogue=[
            "Every file in Linux has permissions controlling who can Read (r), Write (w), and Execute (x).",
            "Use 'chmod 755 play.sh' (or 'chmod +x play.sh') to make it executable!",
        ],
        objectives=[
            Objective(
                id="obj_9_1",
                description="Make 'play.sh' executable using chmod (755 or +x).",
                hint="Type 'chmod 755 play.sh' or 'chmod +x play.sh' and press Enter.",
                command="chmod",
                syntax="chmod 755 play.sh",
                explanation="Grants read and execute permissions to a script file.",
                predicate_type="permission_equals",
                predicate_target="play.sh",
                predicate_expected="755",
                xp_reward=100,
                hints=[
                    "Use 'chmod' to change permissions.",
                    "Mode 755 makes a script readable and executable.",
                    "Type: chmod 755 play.sh",
                ],
                scenario="Fix the permissions so everyone can run the play script.",
            ),
        ],
        reward_item=Item(
            id="item_brass_key",
            name="Brass Permission Key 🗝️",
            description="Unlocks the right permissions on any script.",
            category="tool",
            rarity="epic",
        ),
        reward_xp=100,
        environment_tree={
            "play.sh": {
                "content": "#!/bin/bash\necho '🎉 Let the games begin!'\n",
                "permissions": 0o644,
            },
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 10: COUNT & SORT (wc, sort)
    # -------------------------------------------------------------------------
    quests[9] = Quest(
        id="level_10",
        sector_id=9,
        sector_name="Count & Sort",
        npc_name="Oliver",
        lore="Let's process some data! Count the lines in 'guestbook.txt' and sort 'names.txt' alphabetically.",
        dialogue=[
            "'wc -l' counts the number of lines in a file.",
            "'sort' puts lines in clean alphabetical order!",
        ],
        objectives=[
            Objective(
                id="obj_10_1",
                description="Count how many lines are in 'guestbook.txt' using wc -l.",
                hint="Type 'wc -l guestbook.txt' and press Enter.",
                command="wc",
                syntax="wc -l guestbook.txt",
                explanation="Counts total newline lines in a text file.",
                predicate_type="pattern_matched",
                predicate_target="guestbook.txt",
                predicate_expected="guestbook.txt",
                xp_reward=50,
                hints=[
                    "Use 'wc -l <filename>'.",
                    "Type: wc -l guestbook.txt",
                    "Type: wc -l guestbook.txt",
                ],
                scenario="Find out how many guests signed the book.",
            ),
            Objective(
                id="obj_10_2",
                description="Sort 'names.txt' in alphabetical order using sort.",
                hint="Type 'sort names.txt' and press Enter.",
                command="sort",
                syntax="sort names.txt",
                explanation="Sorts lines in text file alphabetically.",
                predicate_type="pattern_matched",
                predicate_target="names.txt",
                predicate_expected="names.txt",
                xp_reward=50,
                hints=[
                    "Use 'sort <filename>'.",
                    "Type: sort names.txt",
                    "Type: sort names.txt",
                ],
                scenario="Order the names alphabetically from A to Z.",
            ),
        ],
        reward_item=Item(
            id="item_abacus",
            name="Polished Abacus 🧮",
            description="Counts lines and organizes numbers with ease.",
            category="tool",
            rarity="epic",
        ),
        reward_xp=100,
        environment_tree={
            "guestbook.txt": "Alice\nBob\nCharlie\nDiana\nEvan\n",
            "names.txt": "Zoe\nCharlie\nAlice\nBob\n",
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 11: CONNECT THE COMMANDS (pipes |)
    # -------------------------------------------------------------------------
    quests[10] = Quest(
        id="level_11",
        sector_id=10,
        sector_name="Connect the Commands",
        npc_name="Byte",
        lore="The pipe operator '|' is one of Linux's greatest superpowers! It connects command output directly into the next command.",
        dialogue=[
            "Imagine a physical pipe carrying water from one tool straight into another.",
            "Try: cat animals.txt | grep \"cat\" to filter animals!",
        ],
        objectives=[
            Objective(
                id="obj_11_1",
                description="Connect commands with a pipe: search for 'cat' in 'animals.txt'.",
                hint="Type 'cat animals.txt | grep \"cat\"' and press Enter.",
                command="cat,grep",
                syntax="cat animals.txt | grep \"cat\"",
                explanation="Pipes standard output of cat into standard input of grep.",
                predicate_type="pipeline_used",
                predicate_target="cat",
                predicate_expected="cat",
                xp_reward=100,
                hints=[
                    "Use the pipe symbol '|' between the two commands.",
                    "Try: cat animals.txt | grep \"cat\"",
                    "Type: cat animals.txt | grep \"cat\"",
                ],
                scenario="Chain two commands together with a pipe.",
            ),
        ],
        reward_item=Item(
            id="item_funnel",
            name="Magic Pipe Funnel 🌪️",
            description="Channels output from one tool straight into another.",
            category="tool",
            rarity="epic",
        ),
        reward_xp=100,
        environment_tree={
            "animals.txt": "dog\ncat\nbird\nwild cat\nfish\nblack cat\n",
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 12: REDIRECT IT (>, >>, <)
    # -------------------------------------------------------------------------
    quests[11] = Quest(
        id="level_12",
        sector_id=11,
        sector_name="Redirect It",
        npc_name="Penny",
        lore="Instead of printing text on screen, '>' saves it into a file, and '>>' appends more to it!",
        dialogue=[
            "'>' sends text into a file (creating or replacing it).",
            "'>>' appends text to the end without erasing what was already there.",
        ],
        objectives=[
            Objective(
                id="obj_12_1",
                description="Save 'Hello Linux' into 'greeting.txt' using echo \"Hello Linux\" > greeting.txt.",
                hint="Type 'echo \"Hello Linux\" > greeting.txt' and press Enter.",
                command="echo",
                syntax="echo \"Hello Linux\" > greeting.txt",
                explanation="Redirects output into greeting.txt.",
                predicate_type="file_contains",
                predicate_target="greeting.txt",
                predicate_expected="Hello Linux",
                xp_reward=50,
                hints=[
                    "Use '>' to write into greeting.txt.",
                    "Type: echo \"Hello Linux\" > greeting.txt",
                    "Type: echo \"Hello Linux\" > greeting.txt",
                ],
                scenario="Create a greeting file with the > redirect operator.",
            ),
            Objective(
                id="obj_12_2",
                description="Append 'Have fun!' to 'greeting.txt' using echo \"Have fun!\" >> greeting.txt.",
                hint="Type 'echo \"Have fun!\" >> greeting.txt' and press Enter.",
                command="echo",
                syntax="echo \"Have fun!\" >> greeting.txt",
                explanation="Appends text to the end of greeting.txt without overwriting.",
                predicate_type="file_contains",
                predicate_target="greeting.txt",
                predicate_expected="Have fun!",
                xp_reward=50,
                hints=[
                    "Use '>>' to append to greeting.txt.",
                    "Type: echo \"Have fun!\" >> greeting.txt",
                    "Type: echo \"Have fun!\" >> greeting.txt",
                ],
                scenario="Add a friendly second line to your greeting file.",
            ),
        ],
        reward_item=Item(
            id="item_quill",
            name="Quill & Ink 🖋️",
            description="Writes and redirects your thoughts into files.",
            category="tool",
            rarity="epic",
        ),
        reward_xp=100,
        environment_tree={
            "notes.txt": "Tip: '>' creates or overwrites, '>>' adds to the end.\n",
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 13: SEARCH + PIPE (find, grep, |)
    # -------------------------------------------------------------------------
    quests[12] = Quest(
        id="level_13",
        sector_id=12,
        sector_name="Search + Pipe",
        npc_name="Nova",
        lore="Let's combine what we've learned: use 'find' to locate all '.txt' files and pipe them to 'grep' for 'clue'!",
        dialogue=[
            "Hello! I'm Nova.",
            "When you combine search tools with pipes, you can inspect hundreds of files in seconds!",
        ],
        objectives=[
            Objective(
                id="obj_13_1",
                description="Find text files and filter for 'clue' using find . -name \"*.txt\" | grep \"clue\".",
                hint="Type 'find . -name \"*.txt\" | grep \"clue\"' and press Enter.",
                command="find,grep",
                syntax="find . -name \"*.txt\" | grep \"clue\"",
                explanation="Finds text files recursively and pipes results into grep filter.",
                predicate_type="pipeline_used",
                predicate_target="find",
                predicate_expected="clue",
                xp_reward=100,
                hints=[
                    "Start with 'find . -name \"*.txt\"'.",
                    "Pipe into 'grep \"clue\"'.",
                    "Type: find . -name \"*.txt\" | grep \"clue\"",
                ],
                scenario="Combine find and grep to spot clue files across directories.",
            ),
        ],
        reward_item=Item(
            id="item_spyglass",
            name="Super Spyglass 🔭",
            description="Finds and filters simultaneously across all folders.",
            category="tool",
            rarity="legendary",
        ),
        reward_xp=100,
        environment_tree={
            "docs": {
                "clue1.txt": "First piece of the puzzle: follow the sunshine.\n",
                "story.txt": "A relaxing bedtime story about a little robot.\n",
                "clue2.txt": "Second piece of the puzzle: look in the attic.\n",
            },
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 14: THE BIG MESS (Multi-step exploration)
    # -------------------------------------------------------------------------
    quests[13] = Quest(
        id="level_14",
        sector_id=13,
        sector_name="The Big Mess",
        npc_name="Fern",
        lore="We have arrived in the dusty attic! It's a real mess with folders, hidden notes, and locked scripts.",
        dialogue=[
            "This room brings together navigation, hidden files, and permissions.",
            "Explore step-by-step and uncover the secret!",
        ],
        objectives=[
            Objective(
                id="obj_14_1",
                description="Step inside the 'attic' folder using cd attic.",
                hint="Type 'cd attic' and press Enter.",
                command="cd",
                syntax="cd attic",
                explanation="Enters the attic directory.",
                predicate_type="cwd_equals",
                predicate_target="/home/operative/attic",
                xp_reward=50,
                hints=[
                    "Navigate into the attic.",
                    "Type: cd attic",
                    "Type: cd attic",
                ],
                scenario="Walk inside the attic room.",
            ),
            Objective(
                id="obj_14_2",
                description="Read the hidden note '.secret_note' using cat .secret_note.",
                hint="Type 'cat .secret_note' and press Enter.",
                command="cat,less",
                syntax="cat .secret_note",
                explanation="Reads the hidden clue note.",
                predicate_type="file_read",
                predicate_target=".secret_note",
                xp_reward=50,
                hints=[
                    "Remember to include the leading dot for hidden files!",
                    "Type: cat .secret_note",
                    "Type: cat .secret_note",
                ],
                scenario="Read the hidden note tucked away in the corner.",
            ),
            Objective(
                id="obj_14_3",
                description="Make 'solve.sh' executable using chmod (755 or +x).",
                hint="Type 'chmod 755 solve.sh' or 'chmod +x solve.sh' and press Enter.",
                command="chmod",
                syntax="chmod 755 solve.sh",
                explanation="Grants execute permission to solve.sh.",
                predicate_type="permission_equals",
                predicate_target="solve.sh",
                predicate_expected="755",
                xp_reward=50,
                hints=[
                    "Use 'chmod 755 solve.sh' or 'chmod +x solve.sh'.",
                    "Type: chmod 755 solve.sh",
                    "Type: chmod 755 solve.sh",
                ],
                scenario="Fix permissions on the attic puzzle solver.",
            ),
        ],
        reward_item=Item(
            id="item_trophy_box",
            name="Organizer Medal 🎖️",
            description="Proof that you conquered the big messy room!",
            category="badge",
            rarity="legendary",
        ),
        reward_xp=150,
        environment_tree={
            "attic": {
                ".secret_note": "The magic word is SUNSHINE! Keep it in mind for the final challenge.\n",
                "solve.sh": {
                    "content": "#!/bin/bash\necho 'Attic mystery cleared!'\n",
                    "permissions": 0o644,
                },
                "boxes": {
                    "album.txt": "Old photos and warm memories.\n",
                },
            },
        },
    )

    # -------------------------------------------------------------------------
    # LEVEL 15: FINAL CHALLENGE (The Ultimate Exploration Puzzle)
    # -------------------------------------------------------------------------
    quests[14] = Quest(
        id="level_15",
        sector_id=14,
        sector_name="The Final Challenge",
        npc_name="Byte",
        lore="The final adventure puzzle! Combine your skills: read the briefing, find the hidden star in the maze, and record your victory!",
        dialogue=[
            "You have learned so much on this journey.",
            "Now it's time for the final challenge: follow the clues, track down the golden star, and claim your victory!",
        ],
        objectives=[
            Objective(
                id="obj_15_1",
                description="Read 'start_here.txt' to get your final mission briefing.",
                hint="Type 'cat start_here.txt' and press Enter.",
                command="cat,less",
                syntax="cat start_here.txt",
                explanation="Reads the final puzzle instructions.",
                predicate_type="file_read",
                predicate_target="start_here.txt",
                xp_reward=50,
                hints=[
                    "Read the starting instructions file.",
                    "Type: cat start_here.txt",
                    "Type: cat start_here.txt",
                ],
                scenario="Inspect the clue instructions on your desk.",
            ),
            Objective(
                id="obj_15_2",
                description="Locate 'star.txt' hidden in the maze using find . -name \"star.txt\".",
                hint="Type 'find . -name \"star.txt\"' and press Enter.",
                command="find",
                syntax="find . -name \"star.txt\"",
                explanation="Locates the star file inside the maze directory.",
                predicate_type="pattern_matched",
                predicate_target="find",
                predicate_expected="star.txt",
                xp_reward=75,
                hints=[
                    "Use find to search all subfolders for 'star.txt'.",
                    "Type: find . -name \"star.txt\"",
                    "Type: find . -name \"star.txt\"",
                ],
                scenario="Find where the Golden Star is resting in the maze.",
            ),
            Objective(
                id="obj_15_3",
                description="Write 'I_LOVE_LINUX' into 'trophy.txt' to complete your adventure!",
                hint="Type 'echo \"I_LOVE_LINUX\" > trophy.txt' and press Enter!",
                command="echo",
                syntax="echo \"I_LOVE_LINUX\" > trophy.txt",
                explanation="Writes the victory passphrase to complete the game.",
                predicate_type="file_contains",
                predicate_target="trophy.txt",
                predicate_expected="I_LOVE_LINUX",
                xp_reward=100,
                hints=[
                    "Use 'echo \"I_LOVE_LINUX\" > trophy.txt'.",
                    "Make sure the text matches exactly: I_LOVE_LINUX",
                    "Type: echo \"I_LOVE_LINUX\" > trophy.txt",
                ],
                scenario="Claim your victory and complete the final challenge!",
            ),
        ],
        reward_item=Item(
            id="item_golden_star",
            name="Golden Linux Star ⭐",
            description="Awarded to true terminal adventurers who mastered all 15 levels!",
            category="artifact",
            rarity="mythic",
        ),
        reward_xp=250,
        environment_tree={
            "start_here.txt": (
                "Welcome to the Final Challenge! 🌟\n"
                "Step 1: Use 'find . -name \"star.txt\"' to locate where the Golden Star is.\n"
                "Step 2: Read what the star says!\n"
                "Step 3: Write 'I_LOVE_LINUX' into 'trophy.txt' using '>' to claim your trophy!\n"
            ),
            "maze": {
                "hallway": {
                    "room_a": {
                        "star.txt": "⭐ You found the Golden Star! Write 'I_LOVE_LINUX' into 'trophy.txt' to win!\n",
                    },
                },
            },
        },
    )

    return quests
