"""Collect local Git changes without invoking a shell."""

from dataclasses import dataclass
from pathlib import Path
import subprocess


class GitError(Exception):
    """A Git command failed or the directory is not a repository."""


@dataclass(frozen=True)
class GitChanges:
    branch: str
    status: str
    files: tuple[str, ...]
    unstaged_diff: str
    staged_diff: str
    untracked_files: tuple[str, ...]

    @property
    def has_changes(self) -> bool:
        return bool(self.status)


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode:
        raise GitError(result.stderr.strip() or "Git 명령 실행에 실패했습니다.")
    return result.stdout


def collect_changes(cwd: Path) -> GitChanges:
    if _git(cwd, "rev-parse", "--is-inside-work-tree").strip() != "true":
        raise GitError("Git 작업 트리가 아닙니다.")
    branch = _git(cwd, "branch", "--show-current").strip() or "(detached HEAD)"
    status = _git(cwd, "status", "--short", "--untracked-files=all").rstrip()
    names = _git(cwd, "status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0")
    files: list[str] = []
    untracked: list[str] = []
    index = 0
    while index < len(names) and names[index]:
        entry = names[index]
        code, name = entry[:2], entry[3:]
        files.append(name)
        if code == "??":
            untracked.append(name)
        if "R" in code or "C" in code:
            index += 1  # porcelain -z includes the old path next
        index += 1
    # These commands also work before the first commit: unstaged and staged
    # changes are separate, and untracked content is never read implicitly.
    unstaged = _git(cwd, "diff", "--no-ext-diff", "--no-textconv", "--")
    staged = _git(cwd, "diff", "--cached", "--no-ext-diff", "--no-textconv", "--")
    return GitChanges(branch, status, tuple(files), unstaged, staged, tuple(untracked))
