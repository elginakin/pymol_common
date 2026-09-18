#!/usr/bin/env python3
"""Beginner-friendly entry point for every configured structure workflow."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Workflow:
    project: str
    structure_id: str
    root: Path
    base: dict
    profiles: dict

    @property
    def key(self) -> str:
        return f"{self.project}/{self.structure_id}"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def discover() -> list[Workflow]:
    workflows = []
    pattern = "projects/*/structures/*/config/base.json"
    for base_path in sorted(REPOSITORY_ROOT.glob(pattern)):
        root = base_path.parents[1]
        profiles_path = root / "config" / "profiles.json"
        generator = root / "scripts" / "generate_figures.py"
        if profiles_path.is_file() and generator.is_file():
            workflows.append(
                Workflow(
                    project=root.parents[1].name,
                    structure_id=root.name,
                    root=root,
                    base=read_json(base_path),
                    profiles=read_json(profiles_path),
                )
            )
    return workflows


def resolve(name: str, workflows: list[Workflow]) -> Workflow:
    matches = [item for item in workflows if name in {item.structure_id, item.key}]
    if not matches:
        available = ", ".join(item.key for item in workflows) or "none"
        raise SystemExit(f"Unknown structure {name!r}. Available: {available}")
    if len(matches) > 1:
        choices = ", ".join(item.key for item in matches)
        raise SystemExit(f"{name!r} is ambiguous. Use one of: {choices}")
    return matches[0]


def show_list(workflows: list[Workflow]) -> None:
    if not workflows:
        print("No structure workflows were found.")
        return
    for item in workflows:
        print(f"{item.key:24} {item.base.get('title', '')}")


def show_profiles(workflow: Workflow) -> None:
    for profile in workflow.profiles.get("profiles", []):
        positions = profile.get("mutations_sequential_ha1", [])
        mutation_text = ", ".join(map(str, positions)) if positions else "none"
        print(f"{profile['name']}: mutations {mutation_text}")
        if profile.get("description"):
            print(f"  {profile['description']}")


def show_layers(workflow: Workflow) -> None:
    print("Antigenic sites")
    for name, data in workflow.base["antigenic_sites"].items():
        state = "on" if data["enabled"] else "off"
        print(f"  {name:16} {state}")
    print("Glycans")
    for name, data in workflow.base["glycans"].items():
        state = "on" if data["enabled"] else "off"
        note = " (emphasized)" if data.get("emphasize") else ""
        print(f"  {name:16} {state}{note}")
    print("\nOne-run override example:")
    print(
        f"  python structure_figures.py render {workflow.structure_id} "
        "--glycan HA1_N197=off --antigenic 160_loop=off --preview"
    )


def generation_args(args: argparse.Namespace, render: bool) -> list[str]:
    forwarded: list[str] = []
    for profile in args.profile or []:
        forwarded.extend(["--profile", profile])
    for glycan in args.glycan or []:
        forwarded.extend(["--glycan", glycan])
    for site in args.antigenic or []:
        forwarded.extend(["--antigenic", site])
    if args.preview:
        forwarded.append("--preview")
    if render:
        forwarded.append("--render")
    if args.pymol:
        forwarded.extend(["--pymol", args.pymol])
    return forwarded


def run_workflow(workflow: Workflow, args: argparse.Namespace, render: bool) -> None:
    command = [sys.executable, str(workflow.root / "scripts" / "generate_figures.py")]
    command.extend(generation_args(args, render))
    subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)


def check_workflow(workflow: Workflow) -> None:
    subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-v",
            "-s",
            str(workflow.root / "tests"),
        ],
        cwd=REPOSITORY_ROOT,
        check=True,
    )


def doctor(workflows: list[Workflow]) -> None:
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    pymol = shutil.which("pymol")
    print(f"PyMOL: {pymol or 'not found; pass --pymol /path/to/pymol when rendering'}")
    print(f"Structure workflows: {len(workflows)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="list available structures")
    subparsers.add_parser("doctor", help="check Python, PyMOL, and discovery")

    for command, help_text in (
        ("profiles", "list mutation profiles"),
        ("layers", "list glycan and antigenic-site switches"),
        ("check", "run a structure's regression tests"),
    ):
        child = subparsers.add_parser(command, help=help_text)
        child.add_argument("structure")

    for command, help_text in (
        ("generate", "create PyMOL scripts without launching PyMOL"),
        ("render", "create scripts and render figures in PyMOL"),
    ):
        child = subparsers.add_parser(command, help=help_text)
        child.add_argument("structure")
        child.add_argument("--profile", action="append")
        child.add_argument("--glycan", action="append", metavar="NAME=on|off")
        child.add_argument("--antigenic", action="append", metavar="NAME=on|off")
        child.add_argument("--preview", action="store_true")
        child.add_argument("--pymol")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    workflows = discover()
    if args.command == "list":
        show_list(workflows)
    elif args.command == "doctor":
        doctor(workflows)
    else:
        workflow = resolve(args.structure, workflows)
        if args.command == "profiles":
            show_profiles(workflow)
        elif args.command == "layers":
            show_layers(workflow)
        elif args.command == "check":
            check_workflow(workflow)
        elif args.command == "generate":
            run_workflow(workflow, args, render=False)
        elif args.command == "render":
            run_workflow(workflow, args, render=True)


if __name__ == "__main__":
    main()
