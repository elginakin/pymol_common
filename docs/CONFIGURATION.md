# Configuration reference

Every structure workflow has two hand-edited JSON files.

## `config/base.json`

- `title`: human-readable structure name.
- `structure`: PDB ID, object name, output prefix, and focus/context chains.
- `numbering`: conversion from the biological numbering used in profiles to
  the coordinate file's author residue IDs.
- `colors`: named hexadecimal colors used by generated PyMOL scripts.
- `display`: transparency, representation sizes, and visibility defaults.
- `antigenic_sites`: named residue selections with independent `enabled`
  switches.
- `rbs`: receptor-binding-site definition and color.
- `glycans`: independently switchable carbohydrate selections. `emphasize`
  makes one glycan visually prominent.
- `camera`: overview and close-up orientations.
- `render`: output dimensions, DPI, ray tracing, and background behavior.
- `paths`: render destinations relative to the structure folder.

## `config/profiles.json`

Each profile has this shape:

```json
{
  "name": "C.example",
  "description": "What this mutation step represents.",
  "mutations_sequential_ha1": [197, 208],
  "glycan_overrides": {"HA1_N197": false},
  "antigenic_site_overrides": {}
}
```

Profiles are figure layers on the reference structure. They do not remodel
mutated side chains.

## Precedence

The base configuration is applied first, then profile overrides, then one-run
command-line overrides. This lets one aesthetic remain consistent while each
evolutionary profile changes only the residues or glycans that differ.

## Audit trail

Generation writes a tab-separated manifest under `generated/`. It records the
input mutation positions, mapped author residue IDs, enabled antigenic sites,
and enabled glycans for every generated profile.
