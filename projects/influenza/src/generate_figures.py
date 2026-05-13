"""Project-specific figure presets for influenza outputs."""

from pymol_common.common.figures import figure_spec


def default_influenza_figures() -> list[dict]:
    """Return default figure presets for influenza workflows."""
    return [
        figure_spec(name="ha_overview"),
        figure_spec(name="ha_rbs_closeup", representation="sticks", color_scheme="yellow"),
    ]
