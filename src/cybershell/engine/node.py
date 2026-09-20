"""Virtual Filesystem (VFS) Node Definitions.

Author: Rudra (VFS Architect)
Role: Defines the core data structures for files, directories, permissions,
      and metadata inside the in-memory Linux filesystem tree.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Union


def parse_permissions(mode: Union[int, str]) -> int:
    """Parse permissions from int (e.g. 0o755), octal string ('755'), or symbolic ('rwxr-xr-x').

    Returns a 9-bit integer (e.g. 0o755).
    """
    if isinstance(mode, int):
        return mode & 0o777

    mode_str = str(mode).strip()

    # If format is standard 3 or 4 digit octal (e.g. '755', '0755', '644')
    if mode_str.isdigit() and len(mode_str) in (3, 4):
        try:
            return int(mode_str, 8) & 0o777
        except ValueError:
            pass

    # If format is symbolic representation (e.g. 'rwxr-xr-x' or '-rwxr-xr-x' or 'drwxr-xr-x')
    if len(mode_str) in (9, 10):
        # Drop leading type indicator ('-' or 'd') if present
        sym = mode_str[-9:]
        val = 0
        mapping = [
            (0, 'r', 0o400), (1, 'w', 0o200), (2, 'x', 0o100),
            (3, 'r', 0o040), (4, 'w', 0o020), (5, 'x', 0o010),
            (6, 'r', 0o004), (7, 'w', 0o002), (8, 'x', 0o001),
        ]
        for idx, char, bit in mapping:
            if sym[idx] == char:
                val |= bit
            elif sym[idx] != '-':
                # Invalid character in symbolic mode
                raise ValueError(f"Invalid character '{sym[idx]}' in permission string: {mode}")
        return val

    raise ValueError(f"Unsupported permission format: {mode}")


def format_octal(mode: int) -> str:
    """Format an integer permission into a standard 3-digit octal string ('755')."""
    return f"{mode & 0o777:03o}"


def format_symbolic(mode: int, is_dir: bool = False) -> str:
    """Format an integer permission into a 10-char Linux ls -l string (e.g. '-rw-r--r--')."""
    chars = ['d' if is_dir else '-']
    bits = [
        (0o400, 'r'), (0o200, 'w'), (0o100, 'x'),
        (0o040, 'r'), (0o020, 'w'), (0o010, 'x'),
        (0o004, 'r'), (0o002, 'w'), (0o001, 'x'),
    ]
    for bit, char in bits:
        chars.append(char if (mode & bit) else '-')
    return "".join(chars)


class FSNode:
    """Base class for any node (file or directory) in the Virtual Filesystem."""

    def __init__(
        self,
        name: str,
        parent: Optional[DirectoryNode] = None,
        permissions: Union[int, str] = 0o755,
        owner: str = "operative",
        group: str = "operative",
    ) -> None:
        self.name: str = name
        self.parent: Optional[DirectoryNode] = parent
        self.permissions: int = parse_permissions(permissions)
        self.owner: str = owner
        self.group: str = group
        self.created_at: float = time.time()
        self.modified_at: float = self.created_at

    @property
    def path(self) -> str:
        """Compute the canonical absolute path of this node from the root."""
        if self.parent is None:
            # Root directory node
            return "/"
        parent_path = self.parent.path
        if parent_path == "/":
            return f"/{self.name}"
        return f"{parent_path}/{self.name}"

    @property
    def is_directory(self) -> bool:
        """Whether this node is a directory."""
        return False

    @property
    def is_file(self) -> bool:
        """Whether this node is a regular file."""
        return False

    @property
    def size(self) -> int:
        """Byte size of the node."""
        return 0

    @property
    def mode_octal(self) -> str:
        """3-digit octal permission string (e.g. '755', '644')."""
        return format_octal(self.permissions)

    @property
    def mode_str(self) -> str:
        """Linux-style symbolic permission string (e.g. 'drwxr-xr-x', '-rw-r--r--')."""
        return format_symbolic(self.permissions, is_dir=self.is_directory)

    def chmod(self, mode: Union[int, str]) -> None:
        """Update permissions on this node."""
        self.permissions = parse_permissions(mode)
        self.modified_at = time.time()

    def touch(self) -> None:
        """Update the modification timestamp."""
        self.modified_at = time.time()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} path={self.path!r} mode={self.mode_octal}>"


class FileNode(FSNode):
    """Represents a regular file containing text or script data."""

    def __init__(
        self,
        name: str,
        content: str = "",
        parent: Optional[DirectoryNode] = None,
        permissions: Union[int, str] = 0o644,
        owner: str = "operative",
        group: str = "operative",
    ) -> None:
        super().__init__(
            name=name,
            parent=parent,
            permissions=permissions,
            owner=owner,
            group=group,
        )
        self.content: str = content

    @property
    def is_file(self) -> bool:
        return True

    @property
    def size(self) -> int:
        """Return the size in bytes of the UTF-8 encoded text content."""
        return len(self.content.encode("utf-8"))

    def read(self) -> str:
        """Read and return the entire content of the file."""
        return self.content

    def write(self, content: str) -> None:
        """Overwrite file content and update modification time."""
        self.content = content
        self.touch()

    def append(self, content: str) -> None:
        """Append text to file content and update modification time."""
        self.content += content
        self.touch()

    def copy(self, new_name: Optional[str] = None) -> FileNode:
        """Create a detached copy of this file node."""
        target_name = new_name if new_name is not None else self.name
        new_file = FileNode(
            name=target_name,
            content=self.content,
            parent=None,
            permissions=self.permissions,
            owner=self.owner,
            group=self.group,
        )
        return new_file


class DirectoryNode(FSNode):
    """Represents a directory containing child files and subdirectories."""

    def __init__(
        self,
        name: str,
        parent: Optional[DirectoryNode] = None,
        permissions: Union[int, str] = 0o755,
        owner: str = "operative",
        group: str = "operative",
    ) -> None:
        super().__init__(
            name=name,
            parent=parent,
            permissions=permissions,
            owner=owner,
            group=group,
        )
        self.children: Dict[str, FSNode] = {}

    @property
    def is_directory(self) -> bool:
        return True

    @property
    def size(self) -> int:
        """Standard Linux directory block size (4096 bytes)."""
        return 4096

    def add_child(self, node: FSNode) -> FSNode:
        """Add or overwrite a child node in this directory."""
        node.parent = self
        self.children[node.name] = node
        self.touch()
        return node

    def remove_child(self, name: str) -> FSNode:
        """Remove a child node by name. Raises FileNotFoundError if missing."""
        if name not in self.children:
            raise FileNotFoundError(f"No such file or directory: '{name}'")
        child = self.children.pop(name)
        child.parent = None
        self.touch()
        return child

    def get_child(self, name: str) -> Optional[FSNode]:
        """Get child node by name, or return None if not present."""
        return self.children.get(name)

    def has_child(self, name: str) -> bool:
        """Return True if child with name exists."""
        return name in self.children

    def list_children(self, show_hidden: bool = False) -> List[FSNode]:
        """List all child nodes sorted alphabetically.

        Filters out hidden files (starting with '.') unless show_hidden=True.
        """
        nodes = list(self.children.values())
        if not show_hidden:
            nodes = [n for n in nodes if not n.name.startswith(".")]
        return sorted(nodes, key=lambda node: node.name)

    def copy(self, new_name: Optional[str] = None) -> DirectoryNode:
        """Recursively deep-copy this directory node and all descendants."""
        target_name = new_name if new_name is not None else self.name
        new_dir = DirectoryNode(
            name=target_name,
            parent=None,
            permissions=self.permissions,
            owner=self.owner,
            group=self.group,
        )
        for child_name, child_node in self.children.items():
            if isinstance(child_node, FileNode):
                copied_file = child_node.copy()
                new_dir.add_child(copied_file)
            elif isinstance(child_node, DirectoryNode):
                copied_subdir = child_node.copy()
                new_dir.add_child(copied_subdir)
        return new_dir
