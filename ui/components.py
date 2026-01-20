"""UI component builders using Builder pattern."""

from PyQt5.QtWidgets import (
    QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt, QSize

from ui.styles import StyleManager
from utils.constants import COLORS


class ComponentBuilder:
    """
    Builder class for creating UI components.
    Uses Builder pattern to construct complex UI elements.
    """
    
    @staticmethod
    def create_button(text: str, color: str) -> QPushButton:
        """
        Create a styled button.
        
        Args:
            text: Button text
            color: Button color
            
        Returns:
            Styled QPushButton
        """
        button = QPushButton(text)
        hover_color = StyleManager._darken_color(color)
        button.setStyleSheet(StyleManager.get_button_style(color, hover_color))
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        button.setGraphicsEffect(shadow)
        
        return button
    
    @staticmethod
    def create_image_label(placeholder_text: str) -> QLabel:
        """
        Create an image preview label.
        
        Args:
            placeholder_text: Placeholder text to display
            
        Returns:
            Styled QLabel for image display
        """
        label = QLabel(placeholder_text)
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumSize(400, 350)
        label.setScaledContents(False)
        label.setStyleSheet(StyleManager.get_image_label_style())
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 8)
        label.setGraphicsEffect(shadow)
        
        return label
    
    @staticmethod
    def create_control_panel() -> QFrame:
        """
        Create styled control panel frame.
        
        Returns:
            Styled QFrame for control panel
        """
        panel = QFrame()
        panel.setFixedWidth(360)
        panel.setStyleSheet(StyleManager.get_control_panel_style())
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 10)
        panel.setGraphicsEffect(shadow)
        
        return panel
    
    @staticmethod
    def create_tips_card() -> QFrame:
        """
        Create styled tips card frame.
        
        Returns:
            Styled QFrame for tips card
        """
        card = QFrame()
        card.setStyleSheet(StyleManager.get_tips_card_style())
        return card
    
    @staticmethod
    def create_separator() -> QFrame:
        """
        Create a horizontal separator line.
        
        Returns:
            Styled QFrame separator
        """
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(
            f"background-color: {COLORS['border']}; max-height: 1px; margin: 10px 0px;"
        )
        return line


class ImageDisplayManager:
    """
    Manages image display operations.
    Implements Single Responsibility Principle - only handles image display.
    """
    
    @staticmethod
    def display_image(label: QLabel, path_or_bytes, available_size=None):
        """
        Display image in a label.
        
        Args:
            label: QLabel to display image in
            path_or_bytes: Image path (str) or BytesIO object
            available_size: Optional size tuple for scaling
        """
        from io import BytesIO
        
        # Load pixmap
        pixmap = QPixmap()
        if isinstance(path_or_bytes, str):
            pixmap = QPixmap(path_or_bytes)
        elif isinstance(path_or_bytes, BytesIO):
            pixmap.loadFromData(path_or_bytes.getvalue())
        else:
            return
        
        if pixmap.isNull():
            return
        
        # Scale pixmap
        if available_size is None:
            available_size = label.size()
        
        scaled_pixmap = pixmap.scaled(
            available_size.width() - 40,
            available_size.height() - 40,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        label.setPixmap(scaled_pixmap)
        label.setText("")
