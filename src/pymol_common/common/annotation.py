"""Reusable helpers for residue-level structure annotation."""


def residue_selection(chain_id: str, residue_number: int) -> str:
    """Build a simple PyMOL selection string for one residue."""
    if residue_number < 1:
        raise ValueError("residue_number must be >= 1")
    return f"chain {chain_id} and resi {residue_number}"


def label_residue(chain_id: str, residue_number: int, label: str) -> dict:
    """Return a small annotation specification that can be consumed downstream."""
    return {
        "selection": residue_selection(chain_id=chain_id, residue_number=residue_number),
        "label": label,
    }
