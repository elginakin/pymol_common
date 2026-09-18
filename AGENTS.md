# Agent guide

This repository generates reproducible scientific figures. Treat biological
definitions and numbering as data that require evidence, not visual guesses.

## Sources of truth

1. Coordinate files and primary structural literature establish the biology.
2. A structure's `config/base.json` defines numbering, selections, colors,
   camera, and output behavior.
3. `config/profiles.json` defines named mutation and layer profiles.
4. `src/pymol_common/structure_workflow.py` is the shared rendering engine.
5. Files under `generated/` and `outputs/` are derived; never hand-edit them.

## Required workflow for changes

1. Read the structure README and both configuration files.
2. Preserve the declared numbering system and document any author-coordinate
   conversion explicitly.
3. Change configuration or shared source code, then regenerate.
4. Run `python structure_figures.py check <structure>`.
5. Render a preview and inspect it visually.
6. Verify the generated manifest records the expected layer and residue state.

Do not commit downloaded coordinate caches or editable PyMOL sessions. A red
mutation layer annotates residues on the reference coordinates; it does not
model a substituted side chain unless a separate modeling workflow says so.

For a new structure, follow `docs/ADDING_STRUCTURES.md`. Keep the standard
folder names so the root command can discover it automatically. Update both
human-facing documentation and tests when behavior changes.
