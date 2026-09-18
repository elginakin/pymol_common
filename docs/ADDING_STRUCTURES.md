# Adding another structure

Create a sibling of the existing 4FQM workflow:

```text
projects/<project>/structures/<structure-id>/
  README.md
  .gitignore
  config/
    base.json
    profiles.json
  scripts/
    generate_figures.py
  tests/
    test_generate_figures.py
  generated/
  previews/
```

## Checklist

1. Verify biological assembly, chain identities, residue numbering, glycans,
   antigenic sites, and receptor-binding residues from the coordinate file and
   authoritative literature.
2. Copy the configuration schema from 4FQM and replace every structure-specific
   selection. Do not assume numbering or chain layouts transfer.
3. Use a thin `scripts/generate_figures.py` wrapper that points to the shared
   `pymol_common.structure_workflow` engine.
4. Add numbering, profile, and toggle regression tests.
5. Run `python structure_figures.py list`; automatic discovery should show the
   new `project/structure-id` key.
6. Generate, render, visually inspect, and save representative images in
   `previews/`.
7. Document scientific definitions and citations in the structure README.

Downloaded coordinates belong in `cache/`; rendered working files belong in
`outputs/`. Both are ignored. Generated PML scripts and manifests may be
tracked because they make the workflow auditable.
