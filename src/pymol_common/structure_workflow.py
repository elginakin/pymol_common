#!/usr/bin/env python3
"""Generate reproducible PyMOL scripts from shared visual/profile configs.

The generator does not model amino-acid substitutions.  It maps sequential
HA1 positions onto the 4FQM coordinate numbering and displays those residues
as red mutation layers on the experimentally determined structure.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return data


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    if not slug:
        raise ValueError(f"Profile name cannot be converted to a filename: {value!r}")
    return slug


def parse_toggle(value: str) -> tuple[str, bool]:
    try:
        name, state = value.rsplit("=", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use NAME=on or NAME=off") from exc
    normalized = state.lower()
    if normalized not in {"on", "off", "true", "false", "1", "0"}:
        raise argparse.ArgumentTypeError("Toggle state must be on or off")
    return name, normalized in {"on", "true", "1"}


def hex_to_rgb(color: str) -> tuple[float, float, float]:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
        raise ValueError(f"Invalid RGB hex color: {color!r}")
    return tuple(int(color[index : index + 2], 16) / 255 for index in (1, 3, 5))


def sequential_to_author(position: int, numbering: dict[str, Any]) -> str:
    """Convert sequential Brisbane HA1 numbering to the author IDs in 4FQM."""
    if not isinstance(position, int) or position < 1:
        raise ValueError(f"Mutation positions must be positive integers: {position!r}")

    explicit = numbering.get("explicit_author_ids", {})
    if str(position) in explicit:
        return str(explicit[str(position)])

    author_position = position
    for rule in sorted(
        numbering.get("offset_rules", []),
        key=lambda item: int(item["sequential_minimum"]),
    ):
        if position >= int(rule["sequential_minimum"]):
            author_position = position + int(rule["author_offset"])
    return str(author_position)


def apply_overrides(
    base: dict[str, Any],
    profile: dict[str, Any],
    glycan_cli: list[tuple[str, bool]],
    antigenic_cli: list[tuple[str, bool]],
) -> dict[str, Any]:
    config = deepcopy(base)

    for name, enabled in profile.get("glycan_overrides", {}).items():
        if name not in config["glycans"]:
            raise ValueError(f"Unknown glycan override {name!r} in profile {profile['name']!r}")
        config["glycans"][name]["enabled"] = bool(enabled)

    for name, enabled in profile.get("antigenic_site_overrides", {}).items():
        if name not in config["antigenic_sites"]:
            raise ValueError(
                f"Unknown antigenic-site override {name!r} in profile {profile['name']!r}"
            )
        config["antigenic_sites"][name]["enabled"] = bool(enabled)

    for name, enabled in glycan_cli:
        if name not in config["glycans"]:
            raise ValueError(f"Unknown glycan toggle {name!r}")
        config["glycans"][name]["enabled"] = enabled

    for name, enabled in antigenic_cli:
        if name not in config["antigenic_sites"]:
            raise ValueError(f"Unknown antigenic-site toggle {name!r}")
        config["antigenic_sites"][name]["enabled"] = enabled

    return config


def validate_base(config: dict[str, Any]) -> None:
    required = {
        "structure",
        "numbering",
        "colors",
        "display",
        "antigenic_sites",
        "rbs",
        "glycans",
        "camera",
        "render",
        "paths",
    }
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"Base config is missing keys: {', '.join(missing)}")

    for color in config["colors"].values():
        hex_to_rgb(color)

    transparency = float(config["display"]["context_transparency"])
    if not 0 <= transparency <= 1:
        raise ValueError("context_transparency must be between 0 and 1")

    if not config["glycans"]:
        raise ValueError("At least one glycan definition is required")


def validate_profiles(profiles: list[dict[str, Any]]) -> None:
    names: set[str] = set()
    slugs: set[str] = set()
    for profile in profiles:
        name = profile.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("Every profile requires a non-empty name")
        slug = slugify(name)
        if name in names or slug in slugs:
            raise ValueError(f"Duplicate profile name or filename slug: {name!r}")
        names.add(name)
        slugs.add(slug)
        mutations = profile.get("mutations_sequential_ha1", [])
        if len(mutations) != len(set(mutations)):
            raise ValueError(f"Duplicate mutation position in profile {name!r}")
        for position in mutations:
            if not isinstance(position, int) or position < 1:
                raise ValueError(f"Invalid mutation position {position!r} in {name!r}")


def pml_color(name: str, color: str) -> str:
    red, green, blue = hex_to_rgb(color)
    return f"set_color {name}, [{red:.4f}, {green:.4f}, {blue:.4f}]"


def pml_union(names: list[str]) -> str:
    return " or ".join(names) if names else "none"


def build_pml(
    config: dict[str, Any],
    profile: dict[str, Any],
    figure_dir_name: str,
    session_dir_name: str,
    preview: bool,
) -> tuple[str, list[str]]:
    structure = config["structure"]
    display = config["display"]
    render = deepcopy(config["render"])
    camera = config["camera"]
    object_name = structure["object_name"]
    profile_slug = slugify(profile["name"])
    output_prefix = structure.get("output_prefix", structure["pdb_id"].lower())
    prefix = f"{output_prefix}_{profile_slug}"

    if preview:
        render["width"] = 675
        render["height"] = 900

    mutations = profile.get("mutations_sequential_ha1", [])
    author_mutations = [
        sequential_to_author(position, config["numbering"]) for position in mutations
    ]

    lines = [
        f"# Generated profile: {profile['name']}",
        f"# {profile.get('description', '')}",
        f"# Mutation input uses {config['numbering']['name']}.",
        "# This file is generated.  Edit the JSON configs and regenerate it.",
        "",
        "reinitialize",
        "set fetch_path, cache",
        (
            f"fetch {structure['pdb_id']}, {object_name}, "
            f"type={structure['fetch_type']}, async=0"
        ),
        "remove solvent",
        "",
    ]

    lines.extend(pml_color(name, value) for name, value in config["colors"].items())
    lines.extend(
        [
            "",
            (
                f"select focus_ha1, {object_name} and polymer.protein and "
                f"chain {structure['focus_ha1_chain']}"
            ),
            (
                f"select focus_ha2, {object_name} and polymer.protein and "
                f"chain {structure['focus_ha2_chain']}"
            ),
            "select focus_protomer, focus_ha1 or focus_ha2",
            (
                f"select context_ha1, {object_name} and polymer.protein and chain "
                + "+".join(structure["context_ha1_chains"])
            ),
            (
                f"select context_ha2, {object_name} and polymer.protein and chain "
                + "+".join(structure["context_ha2_chains"])
            ),
            "select context_protomers, context_ha1 or context_ha2",
            "select trimer_protein, focus_protomer or context_protomers",
            "",
        ]
    )

    enabled_sites: list[str] = []
    for name, site in config["antigenic_sites"].items():
        selection_name = f"antigenic_{name}"
        lines.append(
            f"select {selection_name}, focus_ha1 and resi {site['author_resi']}"
        )
        if site["enabled"]:
            enabled_sites.append(selection_name)
    lines.append(f"select antigenic_sites, {pml_union(enabled_sites)}")

    rbs_resi = "+".join(str(position) for position in config["rbs"]["author_resi"])
    lines.append(f"select rbs_focus, focus_ha1 and resi {rbs_resi}")

    mutation_selection_names: list[str] = []
    for sequential, author in zip(mutations, author_mutations):
        name = f"mutation_{sequential}"
        mutation_selection_names.append(name)
        lines.append(f"select {name}, focus_ha1 and resi {author}")
    lines.append(f"select mutations_focus, {pml_union(mutation_selection_names)}")
    lines.append("")

    enabled_glycans: list[str] = []
    emphasized_glycans: list[str] = []
    for name, glycan in config["glycans"].items():
        selection_name = f"glycan_{name}"
        lines.append(
            f"select {selection_name}, {object_name} and resn NAG+BMA and "
            f"({glycan['selection']})"
        )
        if glycan["enabled"]:
            enabled_glycans.append(selection_name)
            if glycan.get("emphasize", False):
                emphasized_glycans.append(selection_name)
    lines.append(f"select focus_glycans, {pml_union(enabled_glycans)}")
    lines.append(f"select emphasized_glycans, {pml_union(emphasized_glycans)}")

    lines.extend(
        [
            "",
            f"hide everything, {object_name}",
            "show cartoon, focus_protomer",
            "color ha_body, focus_protomer",
        ]
    )
    if display["show_context_protomers"]:
        lines.extend(
            [
                "show surface, context_protomers",
                "color ha_context, context_protomers",
                f"set transparency, {display['context_transparency']}, context_protomers",
            ]
        )

    lines.extend(["show spheres, antigenic_sites"])
    for name, site in config["antigenic_sites"].items():
        if site["enabled"]:
            lines.append(f"color {site['color']}, antigenic_{name}")
    lines.append(
        f"set sphere_scale, {display['antigenic_sphere_scale']}, antigenic_sites"
    )

    if display["show_rbs"]:
        lines.extend(
            [
                "show sticks, rbs_focus",
                "show spheres, rbs_focus",
                f"color {config['rbs']['color']}, rbs_focus",
                "set stick_radius, 0.19, rbs_focus",
                f"set sphere_scale, {display['rbs_sphere_scale']}, rbs_focus",
            ]
        )

    lines.extend(
        [
            "show sticks, mutations_focus",
            "show spheres, mutations_focus",
            "color mutation_red, mutations_focus",
            f"set sphere_scale, {display['mutation_sphere_scale']}, mutations_focus",
        ]
    )
    if display["mutation_labels"]:
        for sequential in mutations:
            lines.append(f'label mutation_{sequential} and name CA, "{sequential}"')

    lines.extend(
        [
            "show sticks, focus_glycans",
            "color glycan_gold, focus_glycans",
            f"set stick_radius, {display['glycan_stick_radius']}, focus_glycans",
            "show spheres, emphasized_glycans",
            "color glycan_gold, emphasized_glycans",
            (
                "set sphere_scale, "
                f"{display['emphasized_glycan_sphere_scale']}, emphasized_glycans"
            ),
            "",
            "bg_color white",
            "set orthoscopic, on",
            "set depth_cue, off",
            "set fog, 0",
            "set antialias, 2",
            (
                "set ray_opaque_background, off"
                if render["transparent_background"]
                else "set ray_opaque_background, on"
            ),
            "set ray_trace_mode, 1",
            "set ray_trace_gain, 0.08",
            "set ray_shadows, on",
            "set ambient, 0.48",
            "set direct, 0.42",
            "set specular, 0.18",
            "set shininess, 25",
            "set cartoon_fancy_helices, on",
            "set cartoon_smooth_loops, on",
            f"set surface_quality, {display['surface_quality']}",
            "set stick_quality, 18",
            "set sphere_quality, 2",
            "",
            "disable all",
            f"enable {object_name}",
            "orient trimer_protein",
            f"turn z, {camera['turn_z']}",
            f"turn y, {camera['turn_y']}",
            f"zoom trimer_protein, {camera['zoom_buffer']}",
            "scene overview, store",
            (
                f"zoom (focus_ha1 and resi {camera['closeup_author_resi']}) "
                f"or emphasized_glycans, {camera['closeup_buffer']}"
            ),
            "scene glycan_closeup, store",
            "scene overview, recall",
            "",
            f"viewport {render['width']}, {render['height']}",
        ]
    )
    if render["ray_trace"]:
        lines.append(f"ray {render['width']}, {render['height']}")
    lines.extend(
        [
            f"png {figure_dir_name}/{prefix}.png, dpi={render['dpi']}",
            f"save {session_dir_name}/{prefix}.pse",
            "scene glycan_closeup, recall",
            "deselect",
            "",
        ]
    )
    return "\n".join(lines), author_mutations


def write_manifest(
    rows: list[dict[str, str]], output_dir: Path, output_prefix: str
) -> Path:
    path = output_dir / f"{output_prefix}_profile_manifest.tsv"
    fields = [
        "profile",
        "description",
        "mutations_sequential_ha1",
        "mutations_4fqm_author",
        "enabled_antigenic_sites",
        "enabled_glycans",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def select_profiles(
    profiles: list[dict[str, Any]], requested: list[str] | None
) -> list[dict[str, Any]]:
    if not requested:
        return profiles
    by_name = {profile["name"]: profile for profile in profiles}
    missing = [name for name in requested if name not in by_name]
    if missing:
        raise ValueError(f"Unknown profiles: {', '.join(missing)}")
    return [by_name[name] for name in requested]


def parse_args(structure_root: Path, argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-config", type=Path, default=structure_root / "config" / "base.json")
    parser.add_argument(
        "--profiles-config", type=Path, default=structure_root / "config" / "profiles.json"
    )
    parser.add_argument("--output-dir", type=Path, default=structure_root / "generated")
    parser.add_argument("--profile", action="append", dest="profiles")
    parser.add_argument("--glycan", action="append", type=parse_toggle, default=[])
    parser.add_argument("--antigenic", action="append", type=parse_toggle, default=[])
    parser.add_argument("--preview", action="store_true", help="Render at 675 by 900 pixels")
    parser.add_argument("--render", action="store_true", help="Run each generated PML in PyMOL")
    parser.add_argument("--pymol", help="PyMOL executable path; otherwise search PATH")
    return parser.parse_args(argv)


def main(structure_root: Path, argv: list[str] | None = None) -> None:
    """Run one structure workflow rooted at ``structure_root``."""
    structure_root = structure_root.resolve()
    args = parse_args(structure_root, argv)
    base = load_json(args.base_config)
    profile_data = load_json(args.profiles_config)
    profiles = profile_data.get("profiles", [])
    if not isinstance(profiles, list):
        raise ValueError("profiles must be a JSON list")

    validate_base(base)
    validate_profiles(profiles)
    selected = select_profiles(profiles, args.profiles)
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = structure_root / output_dir
    output_dir = output_dir.resolve()
    try:
        output_dir_relative = output_dir.relative_to(structure_root)
    except ValueError as exc:
        raise ValueError("--output-dir must be inside the PyMOL workflow directory") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = structure_root / base["paths"]["figures"]
    session_dir = structure_root / base["paths"]["sessions"]
    figure_dir.mkdir(parents=True, exist_ok=True)
    session_dir.mkdir(parents=True, exist_ok=True)
    (structure_root / "cache").mkdir(exist_ok=True)

    manifest_rows: list[dict[str, str]] = []
    generated_paths: list[Path] = []
    for profile in selected:
        config = apply_overrides(base, profile, args.glycan, args.antigenic)
        pml, author_mutations = build_pml(
            config=config,
            profile=profile,
            figure_dir_name=figure_dir.relative_to(structure_root).as_posix(),
            session_dir_name=session_dir.relative_to(structure_root).as_posix(),
            preview=args.preview,
        )
        output_prefix = config["structure"].get(
            "output_prefix", config["structure"]["pdb_id"].lower()
        )
        output_path = output_dir / f"{output_prefix}_{slugify(profile['name'])}.pml"
        output_path.write_text(pml, encoding="utf-8")
        generated_paths.append(output_path)

        enabled_sites = [
            name for name, value in config["antigenic_sites"].items() if value["enabled"]
        ]
        enabled_glycans = [
            name for name, value in config["glycans"].items() if value["enabled"]
        ]
        manifest_rows.append(
            {
                "profile": profile["name"],
                "description": profile.get("description", ""),
                "mutations_sequential_ha1": ",".join(
                    str(value) for value in profile.get("mutations_sequential_ha1", [])
                ),
                "mutations_4fqm_author": ",".join(author_mutations),
                "enabled_antigenic_sites": ",".join(enabled_sites),
                "enabled_glycans": ",".join(enabled_glycans),
            }
        )

    output_prefix = base["structure"].get(
        "output_prefix", base["structure"]["pdb_id"].lower()
    )
    manifest = write_manifest(manifest_rows, output_dir, output_prefix)
    for path in generated_paths:
        print(f"generated {path}")
    print(f"generated {manifest}")

    if args.render:
        executable = args.pymol or shutil.which("pymol")
        if not executable:
            raise RuntimeError("PyMOL was not found. Pass --pymol /path/to/pymol")
        for path in generated_paths:
            subprocess.run(
                [executable, "-cq", str(path.relative_to(structure_root))],
                cwd=structure_root,
                check=True,
            )
