"""Reusable helpers for recording mutagenesis plans."""


def mutation_code(wild_type: str, residue_number: int, mutant: str) -> str:
    """Format mutation code in common WT<resi>MUT style (for example: K417N)."""
    if residue_number < 1:
        raise ValueError("residue_number must be >= 1")
    return f"{wild_type.upper()}{residue_number}{mutant.upper()}"


def build_mutagenesis_plan(mutations: list[dict]) -> list[str]:
    """Create mutation codes from a list of mutation dicts."""
    return [
        mutation_code(
            wild_type=item["wild_type"],
            residue_number=item["residue_number"],
            mutant=item["mutant"],
        )
        for item in mutations
    ]
