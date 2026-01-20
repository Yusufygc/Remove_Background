"""UI component builders using Builder pattern."""

from PyQt5.QtWidgets import (
    QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

from ui.styles import StyleManager
from utils.constants import COLORS


class DragDropLabel(QLabel):
    """
    Custom QLabel with drag and drop support for image files.
    Implements Single Responsibility Principle - only handles drag & drop.
    """
    
    file_dropped = pyqtSignal(str)  # Signal emitted when file is dropped
    
    def __init__(self, placeholder_text: str, parent=None):
        super().__init__(placeholder_text, parent)
        self.setAcceptDrops(True)
        self._default_style = None
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any URL is an image file
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if self._is_image_file(file_path):
                    event.acceptProposedAction()
                    # Visual feedback - highlight border
                    self._apply_drag_style()
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event - restore default style."""
        self._restore_default_style()
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event):
        """Handle drop event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if self._is_image_file(file_path):
                    self.file_dropped.emit(file_path)
                    event.acceptProposedAction()
                    self._restore_default_style()
                    return
        event.ignore()
        self._restore_default_style()
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is a valid image file."""
        import os
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
        ext = os.path.splitext(file_path)[1].lower()
        return ext in valid_extensions and os.path.isfile(file_path)
    
    def _apply_drag_style(self):
        """Apply visual feedback style when dragging over."""
        if self._default_style is None:
            self._default_style = self.styleSheet()
        
        drag_style = self._default_style.replace(
            f"border: 2px dashed {COLORS['border']};",
            f"border: 3px solid {COLORS['primary']};"
        )
        self.setStyleSheet(drag_style)
    
    def _restore_default_style(self):
        """Restore default style."""
        if self._default_style is not None:
            self.setStyleSheet(self._default_style)


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
    def create_image_label(placeholder_text: str, enable_drag_drop: bool = False) -> QLabel:
        """
        Create an image preview label with optional drag & drop support.
        
        Args:
            placeholder_text: Placeholder text to display
            enable_drag_drop: Enable drag and drop functionality
            
        Returns:
            Styled QLabel (or DragDropLabel) for image display
        """
        if enable_drag_drop:
            label = DragDropLabel(placeholder_text)
        else:
            label = QLabel(placeholder_text)
        
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumSize(250, 200)  # Reduced minimum size for responsiveness
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setScaledContents(False)
        label.setStyleSheet(StyleManager.get_image_label_style())
        
        # Store default style for drag & drop label
        if enable_drag_drop:
            label._default_style = StyleManager.get_image_label_style()
        
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
        Create styled control panel frame with responsive width.
        
        Returns:
            Styled QFrame for control panel
        """
        from utils.constants import (
            CONTROL_PANEL_MIN_WIDTH,
            CONTROL_PANEL_PREFERRED_WIDTH,
            CONTROL_PANEL_MAX_WIDTH
        )
        
        panel = QFrame()
        # Use minimum and maximum width instead of fixed width for responsiveness
        panel.setMinimumWidth(CONTROL_PANEL_MIN_WIDTH)
        panel.setMaximumWidth(CONTROL_PANEL_MAX_WIDTH)
        # Set preferred size hint
        panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
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
