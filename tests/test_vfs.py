"""Unit Test Suite for CyberShell Virtual Filesystem (VFS).

Author: Rudra (VFS Architect)
Tests all functionality across node.py and vfs.py.
Compatible with standard library unittest and pytest.
"""

import os
import sys
import time
import unittest

# Ensure 'src' is on sys.path for direct test execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cybershell.engine.node import (  # noqa: E402
    DirectoryNode,
    FileNode,
    FSNode,
    format_octal,
    format_symbolic,
    parse_permissions,
)
from cybershell.engine.vfs import VirtualFileSystem  # noqa: E402


class TestVFSNode(unittest.TestCase):
    """Test FSNode, FileNode, and DirectoryNode models and permissions."""

    def test_permission_parsing_and_formatting(self):
        # Octal int
        self.assertEqual(parse_permissions(0o755), 0o755)
        self.assertEqual(format_octal(0o755), "755")
        self.assertEqual(format_symbolic(0o755, is_dir=False), "-rwxr-xr-x")
        self.assertEqual(format_symbolic(0o755, is_dir=True), "drwxr-xr-x")

        # Octal string
        self.assertEqual(parse_permissions("644"), 0o644)
        self.assertEqual(format_octal(0o644), "644")
        self.assertEqual(format_symbolic(0o644), "-rw-r--r--")

        # Symbolic string
        self.assertEqual(parse_permissions("rwxr-xr-x"), 0o755)
        self.assertEqual(parse_permissions("-rw-------"), 0o600)
        self.assertEqual(parse_permissions("drwxr-xr-x"), 0o755)

    def test_file_node_operations(self):
        file_node = FileNode(name="payload.sh", content="echo 'Hack the Planet!'\n")
        self.assertTrue(file_node.is_file)
        self.assertFalse(file_node.is_directory)
        self.assertEqual(file_node.read(), "echo 'Hack the Planet!'\n")
        self.assertGreater(file_node.size, 0)

        # Append
        file_node.append("exit 0\n")
        self.assertIn("exit 0", file_node.read())

        # Overwrite
        file_node.write("clear\n")
        self.assertEqual(file_node.read(), "clear\n")

        # Chmod
        file_node.chmod("755")
        self.assertEqual(file_node.mode_octal, "755")
        self.assertEqual(file_node.mode_str, "-rwxr-xr-x")

    def test_directory_node_operations(self):
        parent = DirectoryNode(name="root_dir")
        sub = DirectoryNode(name="logs")
        doc = FileNode(name="agent.log", content="Sector scan initiated.")

        parent.add_child(sub)
        parent.add_child(doc)

        self.assertTrue(parent.has_child("logs"))
        self.assertTrue(parent.has_child("agent.log"))
        self.assertEqual(parent.get_child("agent.log"), doc)

        # Path computation
        self.assertEqual(doc.parent, parent)
        children = parent.list_children()
        self.assertEqual(len(children), 2)
        self.assertEqual([c.name for c in children], ["agent.log", "logs"])

        # Remove child
        removed = parent.remove_child("agent.log")
        self.assertEqual(removed.name, "agent.log")
        self.assertFalse(parent.has_child("agent.log"))


class TestVirtualFileSystem(unittest.TestCase):
    """Test VirtualFileSystem tree navigation, path resolver, and file operations."""

    def setUp(self):
        self.vfs = VirtualFileSystem(default_user="operative")

    def test_initial_state(self):
        self.assertEqual(self.vfs.pwd(), "/home/operative")
        self.assertTrue(self.vfs.exists("/bin"))
        self.assertTrue(self.vfs.exists("/etc"))
        self.assertTrue(self.vfs.exists("/home/operative"))
        self.assertTrue(self.vfs.exists("/tmp"))
        self.assertTrue(self.vfs.is_dir("/tmp"))

    def test_path_normalization(self):
        # Tilde expansion
        self.assertEqual(self.vfs.normalize_path("~"), "/home/operative")
        self.assertEqual(self.vfs.normalize_path("~/data.txt"), "/home/operative/data.txt")

        # Relative paths
        self.assertEqual(self.vfs.normalize_path("."), "/home/operative")
        self.assertEqual(self.vfs.normalize_path(".."), "/home")
        self.assertEqual(self.vfs.normalize_path("../../bin"), "/bin")

        # Redundant slashes and root jail
        self.assertEqual(self.vfs.normalize_path("///var///log///"), "/var/log")
        self.assertEqual(self.vfs.normalize_path("/../../.."), "/")

    def test_cd_navigation(self):
        self.assertEqual(self.vfs.cd("/tmp"), "/tmp")
        self.assertEqual(self.vfs.pwd(), "/tmp")

        self.assertEqual(self.vfs.cd(".."), "/")
        self.assertEqual(self.vfs.pwd(), "/")

        self.assertEqual(self.vfs.cd("~"), "/home/operative")
        self.assertEqual(self.vfs.pwd(), "/home/operative")

        # Error cases
        with self.assertRaises(FileNotFoundError):
            self.vfs.cd("/nonexistent_sector")

        self.vfs.touch("cyber.dat")
        with self.assertRaises(NotADirectoryError):
            self.vfs.cd("cyber.dat")

    def test_touch_and_file_read_write(self):
        # Touch new file
        f = self.vfs.touch("cipher.key")
        self.assertTrue(self.vfs.exists("cipher.key"))
        self.assertTrue(self.vfs.is_file("cipher.key"))
        self.assertEqual(self.vfs.read_file("cipher.key"), "")

        # Write content
        self.vfs.write_file("cipher.key", "ALPHA_OMEGA")
        self.assertEqual(self.vfs.read_file("cipher.key"), "ALPHA_OMEGA")

        # Append content
        self.vfs.write_file("cipher.key", "_CONFIDENTIAL", append=True)
        self.assertEqual(self.vfs.read_file("cipher.key"), "ALPHA_OMEGA_CONFIDENTIAL")

        # Reading directory raises error
        with self.assertRaises(IsADirectoryError):
            self.vfs.read_file("/bin")

    def test_mkdir_and_mkdir_p(self):
        # Normal mkdir
        d1 = self.vfs.mkdir("sector0")
        self.assertTrue(self.vfs.is_dir("sector0"))
        self.assertEqual(d1.path, "/home/operative/sector0")

        # Duplicate mkdir raises FileExistsError
        with self.assertRaises(FileExistsError):
            self.vfs.mkdir("sector0")

        # Nested mkdir without -p raises FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            self.vfs.mkdir("missing_parent/sub")

        # mkdir -p creates all parent directories
        d2 = self.vfs.mkdir_p("deep/nested/sub/chamber")
        self.assertTrue(self.vfs.is_dir("deep/nested/sub/chamber"))
        self.assertEqual(d2.path, "/home/operative/deep/nested/sub/chamber")

    def test_remove(self):
        self.vfs.touch("temp.txt")
        self.assertTrue(self.vfs.exists("temp.txt"))
        self.vfs.remove("temp.txt")
        self.assertFalse(self.vfs.exists("temp.txt"))

        # Removing directory without recursive raises IsADirectoryError
        self.vfs.mkdir("junk_dir")
        self.vfs.touch("junk_dir/file.txt")
        with self.assertRaises(IsADirectoryError):
            self.vfs.remove("junk_dir", recursive=False)

        # Removing recursively succeeds
        self.vfs.remove("junk_dir", recursive=True)
        self.assertFalse(self.vfs.exists("junk_dir"))

        # Safety: cannot remove root
        with self.assertRaises(PermissionError):
            self.vfs.remove("/", recursive=True)

        # Safety: cannot remove active working directory
        with self.assertRaises(PermissionError):
            self.vfs.remove("/home/operative", recursive=True)

    def test_chmod(self):
        self.vfs.touch("script.sh")
        self.assertEqual(self.vfs.resolve_path("script.sh").mode_octal, "644")

        # Chmod with octal string
        self.vfs.chmod("script.sh", "755")
        self.assertEqual(self.vfs.resolve_path("script.sh").mode_octal, "755")
        self.assertEqual(self.vfs.resolve_path("script.sh").mode_str, "-rwxr-xr-x")

        # Chmod with octal int
        self.vfs.chmod("script.sh", 0o600)
        self.assertEqual(self.vfs.resolve_path("script.sh").mode_octal, "600")
        self.assertEqual(self.vfs.resolve_path("script.sh").mode_str, "-rw-------")

    def test_copy_and_move(self):
        # File copy
        self.vfs.write_file("source.txt", "Original Data")
        self.vfs.copy("source.txt", "clone.txt")
        self.assertEqual(self.vfs.read_file("clone.txt"), "Original Data")

        # Directory copy
        self.vfs.mkdir_p("src_dir/sub")
        self.vfs.write_file("src_dir/sub/inner.txt", "Deep Data")
        self.vfs.copy("src_dir", "dst_dir", recursive=True)
        self.assertTrue(self.vfs.is_file("dst_dir/sub/inner.txt"))
        self.assertEqual(self.vfs.read_file("dst_dir/sub/inner.txt"), "Deep Data")

        # Move / Rename
        self.vfs.move("clone.txt", "renamed.txt")
        self.assertFalse(self.vfs.exists("clone.txt"))
        self.assertEqual(self.vfs.read_file("renamed.txt"), "Original Data")

    def test_reset_from_dict_and_sub_millisecond_benchmark(self):
        sector_data = {
            "home": {
                "operative": {
                    "mission_brief.txt": "Sector 0: Quarantine Zone. Decontaminate rogue daemons.",
                    "notes.txt": "Remember to chmod 755 the security scripts.",
                    ".secret_token": {
                        "content": "CYBER_TOKEN_9941",
                        "permissions": "600",
                        "owner": "operative",
                    },
                    "telemetry": {
                        "core.dump": "0xDEADBEEF 0x00000000",
                    },
                }
            },
            "var": {
                "log": {
                    "auth.log": "Failed password for daemon from 192.168.1.10",
                }
            },
        }

        # Benchmark instant sector loading
        t0 = time.perf_counter()
        self.vfs.reset_from_dict(sector_data, default_cwd="/home/operative")
        elapsed_ms = (time.perf_counter() - t0) * 1000

        # Verify load time is sub-millisecond or negligible (< 50ms)
        self.assertLess(elapsed_ms, 50.0)

        # Verify layout
        self.assertEqual(self.vfs.pwd(), "/home/operative")
        self.assertTrue(self.vfs.is_file("/home/operative/mission_brief.txt"))
        self.assertEqual(
            self.vfs.read_file("/home/operative/mission_brief.txt"),
            "Sector 0: Quarantine Zone. Decontaminate rogue daemons.",
        )
        self.assertEqual(
            self.vfs.read_file("/home/operative/.secret_token"),
            "CYBER_TOKEN_9941",
        )
        self.assertEqual(
            self.vfs.resolve_path("/home/operative/.secret_token").mode_octal,
            "600",
        )
        self.assertEqual(
            self.vfs.read_file("/var/log/auth.log"),
            "Failed password for daemon from 192.168.1.10",
        )

        # Verify hidden file listing
        regular_files = [n.name for n in self.vfs.list_dir("/home/operative", show_hidden=False)]
        all_files = [n.name for n in self.vfs.list_dir("/home/operative", show_hidden=True)]

        self.assertNotIn(".secret_token", regular_files)
        self.assertIn(".secret_token", all_files)


if __name__ == "__main__":
    unittest.main()
