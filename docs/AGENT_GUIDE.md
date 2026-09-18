# Guidance for coding agents

Start with the root `AGENTS.md`, then read the target structure's README,
`config/base.json`, and `config/profiles.json`.

Important boundaries:

- Configuration and Python source are authoritative; generated files are not.
- Preserve the declared biological numbering system. PyMOL selections may use
  different author residue IDs, so keep mapping tests and explanations current.
- Identify glycans from coordinate connectivity and structure records, not
  merely nearby carbohydrate atoms.
- Glycan presence, absence, and emphasis must be explicit configuration state.
- Mutation layers annotate reference coordinates unless modeling is explicitly
  requested and implemented.
- Do not edit exploratory notebooks or unrelated project code while changing a
  production structure workflow.

Minimum verification is a clean structure-specific test run, regeneration of
all requested profiles, inspection of the manifest, and visual review of a
fresh preview render.
