"""Reusable figure specification helpers."""


def figure_spec(
    name: str,
    representation: str = "cartoon",
    color_scheme: str = "chainbow",
    ray_trace: bool = True,
) -> dict:
    """Create a lightweight figure-generation specification."""
    return {
        "name": name,
        "representation": representation,
        "color_scheme": color_scheme,
        "ray_trace": ray_trace,
    }
