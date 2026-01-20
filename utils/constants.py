"""Application constants and configuration."""

# Modern Color Palette
COLORS = {
    'primary': '#6366f1',
    'primary_hover': '#4f46e5',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'background': '#0f172a',
    'surface': '#1e293b',
    'surface_light': '#334155',
    'text': '#f1f5f9',
    'text_secondary': '#94a3b8',
    'border': '#475569',
    'accent': '#8b5cf6',
}

# Available AI Models
AVAILABLE_MODELS = ["isnet-general-use", "u2net", "u2netp", "silueta"]

# Image Processing Constants
MIN_DIMENSION_FOR_ENHANCEMENT = 1024
IMAGE_SCALE_FACTOR = 1024
ALPHA_THRESHOLD_MIN = 100
ALPHA_THRESHOLD_MAX = 180
ALPHA_MULTIPLIER = 0.6
DEFAULT_ALPHA_THRESHOLD = 127

# File Dialog Filters
IMAGE_FILE_FILTER = "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
PNG_FILE_FILTER = "PNG Files (*.png)"

# UI Constants
WINDOW_TITLE = "Background Remover AI"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 700
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 800
CONTROL_PANEL_WIDTH = 360

# Status Messages
STATUS_INITIALIZING = "🚀 Initializing AI models..."
STATUS_READY = "✅ Ready! Upload an image to start"
STATUS_PROCESSING = "⚡ Processing with {model}..."
STATUS_SUCCESS = "✨ Success! Ready to save"
STATUS_ERROR = "❌ Processing failed"
