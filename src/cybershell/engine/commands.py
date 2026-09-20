"""Shell command implementations for the CyberShell virtual filesystem.

This module deliberately contains no command-line parsing.  ``ShellInterpreter``
turns a user command into an argument vector and passes it here, which makes the
individual commands straightforward to test and reusable by the game UI.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

from cybershell.contracts import CommandResult
from cybershell.engine.node import DirectoryNode, FSNode
from cybershell.engine.vfs import VirtualFileSystem


class ShellCommands:
    """Execute supported Linux-like commands against a :class:`VirtualFileSystem`."""

    def __init__(self, vfs: VirtualFileSystem) -> None:
        self.vfs = vfs
        self._commands: Dict[str, Callable[[Sequence[str], str], CommandResult]] = {
            "pwd": self.pwd,
            "cd": self.cd,
            "ls": self.ls,
            "echo": self.echo,
            "touch": self.touch,
            "mkdir": self.mkdir,
            "cat": self.cat,
            "head": self.head,
            "tail": self.tail,
            "cp": self.cp,
            "mv": self.mv,
            "rm": self.rm,
            "chmod": self.chmod,
            "grep": self.grep,
            "wc": self.wc,
        }

    @property
    def command_names(self) -> Tuple[str, ...]:
        """Return the commands provided by this shell implementation."""
        return tuple(self._commands)

    def execute(self, argv: Sequence[str], stdin: str = "") -> CommandResult:
        """Run one already-tokenized command, optionally consuming piped input."""
        if not argv:
            return CommandResult(stderr="cybershell: syntax error near unexpected token `|`\n", exit_code=2)
        command = argv[0]
        handler = self._commands.get(command)
        if handler is None:
            return CommandResult(stderr=f"cybershell: command not found: {command}\n", exit_code=127)
        try:
            return handler(argv[1:], stdin)
        except (FileNotFoundError, NotADirectoryError, IsADirectoryError, FileExistsError, PermissionError) as error:
            return self._filesystem_error(command, error)
        except ValueError as error:
            return CommandResult(stderr=f"{command}: {error}\n", exit_code=1)

    @staticmethod
    def _filesystem_error(command: str, error: Exception) -> CommandResult:
        """Translate VFS exceptions into concise, familiar shell diagnostics."""
        message = str(error)
        target = ""
        if "'" in message:
            pieces = message.split("'")
            if len(pieces) >= 2:
                target = pieces[-2]
        if isinstance(error, FileNotFoundError):
            detail = "No such file or directory"
        elif isinstance(error, NotADirectoryError):
            detail = "Not a directory"
        elif isinstance(error, IsADirectoryError):
            detail = "Is a directory"
        elif isinstance(error, FileExistsError):
            detail = "File exists"
        else:
            detail = "Permission denied"
        prefix = f"{command}: {target}: " if target else f"{command}: "
        return CommandResult(stderr=f"{prefix}{detail}\n", exit_code=1)

    def pwd(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        if args:
            return CommandResult(stderr="pwd: too many arguments\n", exit_code=1)
        return CommandResult(stdout=f"{self.vfs.get_cwd_path()}\n")

    def cd(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        if len(args) > 1:
            return CommandResult(stderr="cd: too many arguments\n", exit_code=1)
        destination = args[0] if args else "~"
        new_path = self.vfs.cd(destination)
        return CommandResult(metadata={"cwd": new_path})

    def ls(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        show_hidden = False
        long_format = False
        paths: List[str] = []
        for arg in args:
            if arg == "--":
                paths.extend(args[args.index(arg) + 1 :])
                break
            if arg.startswith("-") and arg != "-":
                flags = arg[1:]
                if not flags or any(flag not in "al" for flag in flags):
                    return CommandResult(stderr=f"ls: invalid option -- '{flags[:1]}'\n", exit_code=2)
                show_hidden = show_hidden or "a" in flags
                long_format = long_format or "l" in flags
            else:
                paths.append(arg)
        paths = paths or ["."]

        output: List[str] = []
        for index, path in enumerate(paths):
            node = self.vfs.resolve_path(path)
            if len(paths) > 1:
                if index:
                    output.append("")
                output.append(f"{path}:")
            if show_hidden and isinstance(node, DirectoryNode):
                output.append(self._format_ls_node(node, long_format, "."))
                output.append(self._format_ls_node(node.parent or node, long_format, ".."))
            nodes = self._ls_nodes(node, show_hidden)
            output.extend(self._format_ls_node(item, long_format) for item in nodes)
        return CommandResult(stdout="\n".join(output) + ("\n" if output else ""))

    def _ls_nodes(self, node: FSNode, show_hidden: bool) -> List[FSNode]:
        if not isinstance(node, DirectoryNode):
            return [node]
        nodes = node.list_children(show_hidden=show_hidden)
        return nodes

    @staticmethod
    def _format_ls_node(node: FSNode, long_format: bool, display_name: Optional[str] = None) -> str:
        name = node.name if display_name is None else display_name
        if not long_format:
            return name or "."
        return f"{node.mode_str}  1 {node.owner:<10} {node.group:<10} {node.size:>6} {name or '.'}"

    @staticmethod
    def echo(args: Sequence[str], stdin: str = "") -> CommandResult:
        newline = True
        words = list(args)
        if words and words[0] == "-n":
            newline = False
            words = words[1:]
        return CommandResult(stdout=" ".join(words) + ("\n" if newline else ""))

    def touch(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(stderr="touch: missing file operand\n", exit_code=1)
        for path in args:
            self.vfs.touch(path)
        return CommandResult()

    def mkdir(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        parents = False
        paths: List[str] = []
        for arg in args:
            if arg == "-p":
                parents = True
            elif arg.startswith("-"):
                return CommandResult(stderr=f"mkdir: invalid option -- '{arg[1:2]}'\n", exit_code=2)
            else:
                paths.append(arg)
        if not paths:
            return CommandResult(stderr="mkdir: missing operand\n", exit_code=1)
        for path in paths:
            if parents:
                self.vfs.mkdir_p(path)
            else:
                self.vfs.mkdir(path)
        return CommandResult()

    def cat(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        if not args:
            return CommandResult(stdout=stdin)
        return CommandResult(stdout="".join(self.vfs.read_file(path) for path in args))

    def head(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        count, paths, error = self._line_options("head", args)
        if error:
            return error
        content = self._read_inputs(paths, stdin, "head")
        if isinstance(content, CommandResult):
            return content
        return CommandResult(stdout="".join(content.splitlines(keepends=True)[:count]))

    def tail(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        count, paths, error = self._line_options("tail", args)
        if error:
            return error
        content = self._read_inputs(paths, stdin, "tail")
        if isinstance(content, CommandResult):
            return content
        return CommandResult(stdout="".join(content.splitlines(keepends=True)[-count:]))

    @staticmethod
    def _line_options(command: str, args: Sequence[str]) -> Tuple[int, List[str], Optional[CommandResult]]:
        words = list(args)
        count = 10
        if words[:1] == ["-n"]:
            if len(words) < 2 or not words[1].isdigit():
                return count, [], CommandResult(stderr=f"{command}: invalid number of lines\n", exit_code=1)
            count = int(words[1])
            words = words[2:]
        return count, words, None

    def _read_inputs(self, paths: Sequence[str], stdin: str, command: str):
        if not paths:
            return stdin
        try:
            return "".join(self.vfs.read_file(path) for path in paths)
        except (FileNotFoundError, NotADirectoryError, IsADirectoryError, FileExistsError, PermissionError) as error:
            return self._filesystem_error(command, error)

    def cp(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        recursive = False
        words = [arg for arg in args if arg not in ("-r", "-R")]
        recursive = len(words) != len(args)
        if len(words) != 2:
            return CommandResult(stderr="cp: missing destination file operand\n", exit_code=1)
        self.vfs.copy(words[0], words[1], recursive=recursive)
        return CommandResult()

    def mv(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        if len(args) != 2:
            return CommandResult(stderr="mv: missing destination file operand\n", exit_code=1)
        self.vfs.move(args[0], args[1])
        return CommandResult()

    def rm(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        recursive = any(arg in ("-r", "-R", "-rf", "-fr") for arg in args)
        force = any(arg in ("-f", "-rf", "-fr") for arg in args)
        paths = [arg for arg in args if not arg.startswith("-")]
        if not paths:
            return CommandResult(stderr="rm: missing operand\n", exit_code=1)
        for path in paths:
            try:
                self.vfs.remove(path, recursive=recursive)
            except FileNotFoundError:
                if not force:
                    raise
        return CommandResult()

    def chmod(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        if len(args) < 2:
            return CommandResult(stderr="chmod: missing operand\n", exit_code=1)
        mode, paths = args[0], args[1:]
        for path in paths:
            self.vfs.chmod(path, mode)
        return CommandResult()

    def grep(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        ignore_case = False
        invert = False
        words: List[str] = []
        for arg in args:
            if arg.startswith("-") and arg != "-" and not words:
                flags = arg[1:]
                if any(flag not in "iv" for flag in flags):
                    return CommandResult(stderr=f"grep: invalid option -- '{flags[:1]}'\n", exit_code=2)
                ignore_case = ignore_case or "i" in flags
                invert = invert or "v" in flags
            else:
                words.append(arg)
        if not words:
            return CommandResult(stderr="grep: missing search pattern\n", exit_code=2)
        pattern, paths = words[0], words[1:]
        content = self._read_inputs(paths, stdin, "grep")
        if isinstance(content, CommandResult):
            return content
        comparable_pattern = pattern.lower() if ignore_case else pattern
        selected = []
        for line in content.splitlines(keepends=True):
            comparable_line = line.lower() if ignore_case else line
            matches = comparable_pattern in comparable_line
            if matches != invert:
                selected.append(line)
        return CommandResult(stdout="".join(selected), exit_code=0 if selected else 1)

    def wc(self, args: Sequence[str], stdin: str = "") -> CommandResult:
        if args and args[0] != "-l":
            return CommandResult(stderr="wc: only -l is supported\n", exit_code=2)
        paths = args[1:] if args else []
        content = self._read_inputs(paths, stdin, "wc")
        if isinstance(content, CommandResult):
            return content
        return CommandResult(stdout=f"{content.count(chr(10))}\n")
