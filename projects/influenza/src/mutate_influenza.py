"""Project-specific mutation presets for influenza."""

from pymol_common.common.mutagenesis import build_mutagenesis_plan


def common_ha_mutations() -> list[str]:
    """Return a starter set of influenza HA mutations."""
    return build_mutagenesis_plan(
        [
            {"wild_type": "Q", "residue_number": 226, "mutant": "L"},
            {"wild_type": "G", "residue_number": 228, "mutant": "S"},
        ]
    )
