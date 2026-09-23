"""Application constants and configuration (colors, sizes, models)."""


def _with_alpha(hex_color: str, alpha: float) -> str:
    """Return an "#AARRGGBB" string: hex_color with an alpha channel applied."""
    a = format(int(round(alpha * 255)), '02x')
    return f"#{a}{hex_color.lstrip('#')}"


# Color Palette — single source of truth for every color used in the UI.
# Derived from ui/thema/*.jpg (dominant-color extraction via PIL quantize):
# deep near-black petrol/teal and navy-blue leather/fabric textures.
COLORS = {
    'primary': '#17c3d4',       # vivid petrol teal (brightened from ui/thema base hue)
    'primary_hover': '#0fa3b3',
    'success': '#22e0a0',       # vivid teal-green
    'warning': '#ffb443',       # vivid gold
    'error': '#ff5c5c',         # vivid red
    'background': '#070f14',    # near-black petrol (darkest shadow tone across all 5 images)
    'surface': '#0f232c',       # dark petrol panel
    'surface_light': '#1c3d4a', # lighter petrol-teal (hover)
    'surface_dark': '#050b0f',  # darkest, for panel gradient bottom
    'text': '#eef5f5',
    'text_secondary': '#8fa8ac',
    'border': '#28454f',
    'accent': '#2f8fe6',        # vivid blue (brightened from ui/thema navy hue)
}
COLORS['tips_background'] = _with_alpha(COLORS['primary'], 0.08)
COLORS['tips_border'] = _with_alpha(COLORS['primary'], 0.30)
COLORS['button_shadow'] = _with_alpha('#000000', 0.31)
COLORS['panel_shadow'] = _with_alpha('#000000', 0.47)

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
