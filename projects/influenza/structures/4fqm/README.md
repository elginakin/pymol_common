# Influenza B HA 4FQM

This workflow produces consistent views of the B/Brisbane/60/2008 influenza B
HA trimer in RCSB PDB entry 4FQM.

## Visual design

- HA1/HA2 chains A/B: light-gray opaque cartoon carrying the annotations.
- Other protomers C/D and E/F: near-white translucent surfaces, visible as
  structural context but not annotated.
- Antigenic regions: four coordinated shades of blue.
- Receptor-binding site: purple spheres and sticks.
- Mutation profile: red spheres and sticks.
- Crystallographically resolved N-linked glycans: gold, with HA1 N197
  emphasized.

## Easiest way to use it

Run these commands from the repository root:

```bash
python structure_figures.py profiles 4fqm
python structure_figures.py layers 4fqm
python structure_figures.py render 4fqm --profile C.3.1 --preview
```

Remove `--preview` for an 1800 × 2400 px, 300 dpi image. The PNG is written to
`outputs/figures/` and its editable PyMOL session to `outputs/sessions/`.

## Mutation profiles

The included profiles are:

- `base`: no mutation overlay.
- `C.3.1`: sequential HA1 positions 197 and 208.
- `C.5.6.1`: sequential HA1 position 199.

Add profiles to `config/profiles.json`. These red layers identify positions on
the 4FQM reference; they do not remodel a substituted amino-acid side chain.

## Toggle glycans and antigenic sites

List every valid switch:

```bash
python structure_figures.py layers 4fqm
```

For a one-time render:

```bash
python structure_figures.py render 4fqm \
  --profile C.3.1 \
  --glycan HA1_N197=off \
  --antigenic 160_loop=off \
  --preview
```

Repeat `--glycan` or `--antigenic` to change multiple layers. For a permanent
default, change the relevant `enabled` value in `config/base.json`. For one
named evolutionary profile, place the changes in that profile's
`glycan_overrides` or `antigenic_site_overrides` object.

Available glycan names are `HA1_N25`, `HA1_N59`, `HA1_N145`, `HA1_N197`,
`HA1_N233`, `HA1_N304`, `HA1_N333`, and `HA2_N145`.

## Numbering note: N197 versus 4FQM residue 194

Figure labels and profile inputs use sequential B/Brisbane/60/2008 HA1
numbering, so the emphasized attachment residue is Asn197. The 4FQM coordinate
file stores that same residue as author residue Asn194 because three residues
in the 160 loop are represented with insertion codes 163A, 163B, and 163C.
The configured numbering map handles this conversion automatically.

Examples: sequential 197 → author 194, sequential 199 → author 196, and
sequential 208 → author 205. Regression tests protect these mappings.

## Folder contents

- `config/base.json`: biology, visual style, layer defaults, camera, and render.
- `config/profiles.json`: named mutation and layer profiles.
- `scripts/generate_figures.py`: thin adapter to the shared generator.
- `tests/`: numbering and layer regression tests.
- `generated/`: reproducible PML scripts and audit manifest.
- `previews/`: curated example images.
- `cache/` and `outputs/`: local working files, ignored by Git.

Run `python structure_figures.py check 4fqm` after edits.

## Structural references

- Wang et al. (2008), *Crystal Structure of Unliganded Influenza B Virus
  Hemagglutinin*: https://doi.org/10.1128/JVI.02477-07
- Wang et al. (2007), *Structural basis for receptor specificity of influenza
  B virus hemagglutinin*: https://doi.org/10.1073/pnas.0708363104
- RCSB PDB 4FQM: https://www.rcsb.org/structure/4FQM
