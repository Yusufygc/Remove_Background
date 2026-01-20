"""UI styling and theme management."""

from utils.constants import COLORS


class StyleManager:
    """
    Manages application styles and themes.
    Implements Single Responsibility Principle - only handles styling.
    """
    
    @staticmethod
    def get_main_window_style() -> str:
        """Get main window stylesheet."""
        return f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QComboBox {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['primary']};
                background-color: {COLORS['surface_light']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['text']};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['surface_light']};
            }}
        """
    
    @staticmethod
    def get_control_panel_style() -> str:
        """Get control panel stylesheet."""
        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['surface']}, 
                    stop:1 #1a2332);
                border-radius: 20px;
            }}
        """
    
    @staticmethod
    def get_button_style(color: str, hover_color: str = None) -> str:
        """
        Get button stylesheet.
        
        Args:
            color: Primary button color
            hover_color: Hover color (auto-calculated if None)
        """
        if hover_color is None:
            hover_color = StyleManager._darken_color(color)
        
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {color};
                padding-top: 16px;
                padding-bottom: 12px;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['surface_light']};
                color: {COLORS['text_secondary']};
            }}
        """
    
    @staticmethod
    def get_image_label_style() -> str:
        """Get image label stylesheet."""
        return f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['surface']}, 
                    stop:1 {COLORS['surface_light']});
                border: 2px dashed {COLORS['border']};
                border-radius: 16px;
                padding: 20px;
                color: {COLORS['text_secondary']};
                font-size: 13px;
                font-weight: 500;
            }}
        """
    
    @staticmethod
    def get_status_label_style(status_type: str = "primary") -> str:
        """
        Get status label stylesheet.
        
        Args:
            status_type: Status type (primary, success, warning, error)
        """
        colors = {
            'primary': COLORS['primary'],
            'success': COLORS['success'],
            'warning': COLORS['warning'],
            'error': COLORS['error']
        }
        
        color = colors.get(status_type, COLORS['primary'])
        
        return f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['surface']}, 
                stop:1 {COLORS['surface_light']});
            color: {color};
            padding: 16px 20px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """
    
    @staticmethod
    def get_tips_card_style() -> str:
        """Get tips card stylesheet."""
        return f"""
            QFrame {{
                background-color: rgba(99, 102, 241, 0.08);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 12px;
                padding: 18px;
            }}
        """
    
    @staticmethod
    def _darken_color(hex_color: str) -> str:
        """Darken a hex color."""
        from PyQt5.QtGui import QColor
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        color.setHsl(h, s, max(0, l - 20), a)
        return color.name()
