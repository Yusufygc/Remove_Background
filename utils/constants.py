"""Application constants and configuration (colors, sizes, models)."""


def _with_alpha(hex_color: str, alpha: float) -> str:
    """Return an "#AARRGGBB" string: hex_color with an alpha channel applied."""
    a = format(int(round(alpha * 255)), '02x')
    return f"#{a}{hex_color.lstrip('#')}"


# Color Palette — single source of truth for every color used in the UI.
# Light theme: white/near-white surfaces (kept the petrol-teal/navy hue
# identity from ui/thema/*.jpg, but darkened the semantic colors so they
# stay readable as TEXT on a light background, not just as button fills).
COLORS = {
    'primary': '#0e8a99',       # deep teal — readable as text/icon on white
    'primary_hover': '#0b6f7a',
    'success': '#128a5e',       # deep teal-green
    'warning': '#c07a12',       # deep amber
    'error': '#d33d3d',         # clear red
    'background': '#f3f6f7',    # soft off-white with a faint petrol-gray tint
    'surface': '#ffffff',       # cards/panels: pure white
    'surface_light': '#e7edef', # light gray-teal hover/disabled bg
    'surface_dark': '#dbe4e6',  # slightly deeper light tone (panel gradient bottom)
    'text': '#132226',          # near-black petrol-dark — high contrast on white
    'text_secondary': '#5c7075',
    'border': '#c7d3d6',
    'accent': '#1f6fc9',        # deep vivid blue — readable as text/icon on white
    'on_accent': '#ffffff',     # text/icon color for content drawn ON a colored button
}
COLORS['tips_background'] = _with_alpha(COLORS['primary'], 0.08)
COLORS['tips_border'] = _with_alpha(COLORS['primary'], 0.30)
COLORS['button_shadow'] = _with_alpha('#000000', 0.18)
COLORS['panel_shadow'] = _with_alpha('#000000', 0.12)

# Available AI Models
AVAILABLE_MODELS = ["isnet-general-use", "u2net", "u2netp", "silueta"]

# Image Processing Constants (small-image upscale before segmentation)
MIN_DIMENSION_FOR_ENHANCEMENT = 1024
IMAGE_SCALE_FACTOR = 1024

# Window / Layout Constants
WINDOW_MIN_WIDTH = 900  # Reduced for better responsiveness
WINDOW_MIN_HEIGHT = 600  # Reduced for better responsiveness
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 800
CONTROL_PANEL_MIN_WIDTH = 280  # Minimum width instead of fixed
CONTROL_PANEL_PREFERRED_WIDTH = 360  # Preferred width
CONTROL_PANEL_MAX_WIDTH = 400  # Maximum width
