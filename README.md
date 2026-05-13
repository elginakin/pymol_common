# pymol_common

Shared repository for reusable protein-structure workflows (annotation, mutagenesis, and figure generation), with a scalable project layout.

## Repository layout

```text
src/pymol_common/common/
  annotation.py      # shared annotation helpers
  mutagenesis.py     # shared mutagenesis helpers
  figures.py         # shared figure-spec helpers

projects/
  influenza/
    src/             # influenza-specific Python files
    notebooks/       # influenza notebooks
    docs/            # influenza documentation
```

## How to extend for additional projects

1. Create `projects/<project_name>/`
2. Add `src/`, `notebooks/`, and `docs/`
3. Put project-specific logic in `projects/<project_name>/src/`
4. Reuse shared helpers from `src/pymol_common/common/`

This keeps common functionality centralized while allowing each project to scale independently.
