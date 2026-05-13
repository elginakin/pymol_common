"""Project-specific annotation helpers for influenza structures."""

from pymol_common.common.annotation import label_residue


def annotate_ha_receptor_binding_site() -> list[dict]:
    """Define labels for frequently annotated HA receptor-binding residues."""
    return [
        label_residue(chain_id="A", residue_number=190, label="HA RBS 190"),
        label_residue(chain_id="A", residue_number=225, label="HA RBS 225"),
    ]
