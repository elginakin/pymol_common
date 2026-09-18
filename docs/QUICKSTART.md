# Quick start

All commands below run from the repository root.

## 1. Check your setup

```bash
python structure_figures.py doctor
```

Python can generate scripts without PyMOL. Rendering PNG figures and editable
sessions requires PyMOL 2.x. If it is installed somewhere unusual, use
`--pymol /full/path/to/pymol` on a render command.

## 2. Explore what is available

```bash
python structure_figures.py list
python structure_figures.py profiles 4fqm
python structure_figures.py layers 4fqm
```

## 3. Make a quick preview

```bash
python structure_figures.py render 4fqm --profile C.3.1 --preview
```

The PNG appears in
`projects/influenza/structures/4fqm/outputs/figures/`; the editable PyMOL
session appears in `outputs/sessions/`.

## 4. Make a publication-size figure

```bash
python structure_figures.py render 4fqm --profile C.3.1
```

## Change layers without editing files

Hide a glycan or antigenic site for one run:

```bash
python structure_figures.py render 4fqm \
  --profile C.3.1 \
  --glycan HA1_N197=off \
  --antigenic 160_loop=off \
  --preview
```

Repeat either option to switch multiple layers. Use `layers 4fqm` to see valid
names. These command-line changes are temporary; edit the JSON configuration
for a lasting default or profile-specific change.

## Generate scripts on a computer without PyMOL

```bash
python structure_figures.py generate 4fqm
```

This creates auditable `.pml` scripts and a profile manifest under
`generated/`, but does not render them.

## Verify after an edit

```bash
python structure_figures.py check 4fqm
```
