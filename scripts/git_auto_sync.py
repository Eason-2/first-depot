from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _resolve_git_executable() -> str | None:
    preferred = os.getenv("GIT_EXECUTABLE", "").strip()
    if preferred:
        return preferred

    detected = shutil.which("git")
    if detected:
        return detected

    windows_candidates = [
        r"D:\Git\cmd\git.exe",
        r"D:\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
    ]
    for candidate in windows_candidates:
        if Path(candidate).exists():
            return candidate
    return None


def _run_git(git_exe: str, project_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [git_exe, *args],
        cwd=str(project_root),
        text=True,
        capture_output=True,
        check=False,
    )


def _parse_paths(raw: str) -> list[str]:
    items = [item.strip() for item in (raw or "").split(",")]
    return [item for item in items if item]


def sync_repo_changes(
    project_root: Path,
    include_paths: list[str],
    remote: str = "origin",
    branch: str = "",
    commit_prefix: str = "auto: sync local blog changes",
) -> tuple[bool, str]:
    git_exe = _resolve_git_executable()
    if not git_exe:
        return False, "git_not_found"

    inside = _run_git(git_exe, project_root, ["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0:
        return False, "not_git_repo"

    add_cmd = ["add", "--", *include_paths] if include_paths else ["add", "-A"]
    added = _run_git(git_exe, project_root, add_cmd)
    if added.returncode != 0:
        return False, f"git_add_failed: {added.stderr.strip() or added.stdout.strip()}"

    staged = _run_git(git_exe, project_root, ["diff", "--cached", "--quiet", "--exit-code"])
    if staged.returncode == 0:
        return False, "no_changes"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    message = f"{commit_prefix} ({now})"
    committed = _run_git(git_exe, project_root, ["commit", "-m", message])
    if committed.returncode != 0:
        return False, f"git_commit_failed: {committed.stderr.strip() or committed.stdout.strip()}"

    push_args = ["push", remote]
    if branch:
        push_args.append(branch)
    pushed = _run_git(git_exe, project_root, push_args)
    if pushed.returncode != 0:
        return False, f"git_push_failed: {pushed.stderr.strip() or pushed.stdout.strip()}"

    return True, "pushed"


def sync_from_env(project_root: Path) -> tuple[bool, str]:
    include_paths = _parse_paths(os.getenv("GIT_SYNC_PATHS", "deliverables/published"))
    remote = os.getenv("GIT_SYNC_REMOTE", "origin").strip() or "origin"
    branch = os.getenv("GIT_SYNC_BRANCH", "").strip()
    commit_prefix = os.getenv("GIT_SYNC_COMMIT_PREFIX", "auto: sync local blog changes").strip()
    return sync_repo_changes(
        project_root=project_root,
        include_paths=include_paths,
        remote=remote,
        branch=branch,
        commit_prefix=commit_prefix or "auto: sync local blog changes",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-commit and push local blog changes to GitHub.")
    parser.add_argument(
        "--paths",
        default=os.getenv("GIT_SYNC_PATHS", "deliverables/published"),
        help="Comma-separated paths to sync (default: deliverables/published)",
    )
    parser.add_argument("--remote", default=os.getenv("GIT_SYNC_REMOTE", "origin"), help="Git remote (default: origin)")
    parser.add_argument("--branch", default=os.getenv("GIT_SYNC_BRANCH", ""), help="Optional branch to push")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    changed, detail = sync_repo_changes(
        project_root=project_root,
        include_paths=_parse_paths(args.paths),
        remote=args.remote.strip() or "origin",
        branch=args.branch.strip(),
    )
    print(f"changed={str(changed).lower()} detail={detail}")


if __name__ == "__main__":
    main()
