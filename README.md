# Reproducible PyMOL structure figures

This repository turns small, readable configuration files into consistent
PyMOL figures. The first complete workflow is influenza B hemagglutinin 4FQM.

## Quick start

Requirements: Python 3.10 or newer and PyMOL 2.x.

From the repository root:

```bash
python structure_figures.py doctor
python structure_figures.py list
python structure_figures.py profiles 4fqm
python structure_figures.py render 4fqm --preview
```

Omit `--preview` for the publication-size render. If PyMOL is not on your
command path, add `--pymol /path/to/pymol`.

Common examples:

```bash
# Render one mutation profile
python structure_figures.py render 4fqm --profile C.3.1 --preview

# Hide one glycan for this run only
python structure_figures.py render 4fqm --glycan HA1_N197=off --preview

# See every available antigenic-site and glycan switch
python structure_figures.py layers 4fqm
```

## Where things live

```text
structure_figures.py                    beginner command-line entry point
src/pymol_common/structure_workflow.py  reusable generation engine
projects/influenza/structures/4fqm/     4FQM configuration, tests, and previews
docs/                                   repository-wide guides
```

Edit configuration—not generated `.pml` files—to make lasting changes. See
[the quick-start guide](docs/QUICKSTART.md),
[configuration reference](docs/CONFIGURATION.md), and
[guide to adding structures](docs/ADDING_STRUCTURES.md). The detailed 4FQM
notes are in [its structure folder](projects/influenza/structures/4fqm/README.md).

Current workflow: `influenza/4fqm` — antigenic sites in blue shades, receptor
binding site in purple, mutation layers in red, glycans in gold, a light-gray
focused protomer, and near-white transparent context protomers.
