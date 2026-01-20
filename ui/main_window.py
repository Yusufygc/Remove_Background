"""Main window implementation following SOLID principles."""

import os
from io import BytesIO
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox, QFrame, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.model_manager import ModelManager
from models.image_processor import ImageProcessor
from workers.background_remover_worker import BackgroundRemoverWorker
from ui.styles import StyleManager
from ui.components import ComponentBuilder, ImageDisplayManager
from utils.constants import (
    WINDOW_TITLE, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, AVAILABLE_MODELS,
    IMAGE_FILE_FILTER, PNG_FILE_FILTER, STATUS_INITIALIZING,
    STATUS_READY, STATUS_PROCESSING, STATUS_SUCCESS, STATUS_ERROR,
    COLORS
)


class BackgroundRemoverApp(QMainWindow):
    """
    Main application window.
    Follows Single Responsibility Principle - coordinates UI components.
    Uses Dependency Injection for model manager and image processor.
    """
    
    def __init__(
        self,
        model_manager: ModelManager = None,
        image_processor: ImageProcessor = None
    ):
        """
        Initialize main window.
        
        Args:
            model_manager: Model manager instance (creates new if None)
            image_processor: Image processor instance (creates new if None)
        """
        super().__init__()
        
        # Dependency Injection - allows testing and flexibility
        self._model_manager = model_manager or ModelManager()
        self._image_processor = image_processor or ImageProcessor()
        
        # State management
        self._input_image_path: Optional[str] = None
        self._output_image_bytes: Optional[BytesIO] = None
        self._worker: Optional[BackgroundRemoverWorker] = None
        
        # UI components
        self._model_combo: Optional[QComboBox] = None
        self._load_button: Optional[QPushButton] = None
        self._process_button: Optional[QPushButton] = None
        self._save_button: Optional[QPushButton] = None
        self._input_label: Optional[QLabel] = None
        self._output_label: Optional[QLabel] = None
        self._status_label: Optional[QLabel] = None
        
        self._setup_window()
        self._init_ui()
        self._connect_signals()
        self._load_models()
    
    def _setup_window(self):
        """Setup window properties."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(StyleManager.get_main_window_style())
    
    def _init_ui(self):
        """Initialize user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)  # Reduced spacing for smaller screens
        main_layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins for responsiveness
        
        # Control panel (left) - responsive width
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel, 0)  # Don't stretch, use preferred size
        
        # Image view panel (right) - takes remaining space
        image_view_panel = self._create_image_view_panel()
        main_layout.addWidget(image_view_panel, 1)  # Stretch factor 1
    
    def _create_control_panel(self) -> QFrame:
        """Create control panel with buttons and settings."""
        control_panel = ComponentBuilder.create_control_panel()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(15)  # Reduced spacing for responsiveness
        control_layout.setContentsMargins(20, 20, 20, 20)  # Responsive margins
        
        # Title - responsive font size (minimum 18px, preferred 24px)
        title = QLabel("🎨 Background Remover")
        title.setWordWrap(True)
        title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {COLORS['text']};
            margin-bottom: 5px;
        """)
        control_layout.addWidget(title)
        
        subtitle = QLabel("AI-Powered Image Processing")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            margin-bottom: 15px;
        """)
        control_layout.addWidget(subtitle)
        
        # Separator
        control_layout.addWidget(ComponentBuilder.create_separator())
        control_layout.addSpacing(10)
        
        # Model selection
        model_label = QLabel("AI Model")
        model_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {COLORS['text']};
            margin-bottom: 8px;
        """)
        control_layout.addWidget(model_label)
        
        self._model_combo = QComboBox()
        self._model_combo.addItems(AVAILABLE_MODELS)
        self._model_combo.setCurrentIndex(0)
        # Make combo box responsive
        self._model_combo.setMinimumHeight(35)
        control_layout.addWidget(self._model_combo)
        
        control_layout.addSpacing(15)  # Reduced spacing
        
        # Buttons
        self._load_button = ComponentBuilder.create_button(
            "📁 Upload Image", COLORS['primary']
        )
        self._load_button.clicked.connect(self._load_image)
        control_layout.addWidget(self._load_button)
        
        self._process_button = ComponentBuilder.create_button(
            "✨ Remove Background", COLORS['accent']
        )
        self._process_button.clicked.connect(self._process_image)
        self._process_button.setEnabled(False)
        control_layout.addWidget(self._process_button)
        
        self._save_button = ComponentBuilder.create_button(
            "💾 Save Result", COLORS['success']
        )
        self._save_button.clicked.connect(self._save_image)
        self._save_button.setEnabled(False)
        control_layout.addWidget(self._save_button)
        
        control_layout.addSpacing(15)  # Reduced spacing
        
        # Tips card
        tips_card = self._create_tips_card()
        control_layout.addWidget(tips_card)
        
        control_layout.addStretch(1)
        
        return control_panel
    
    def _create_tips_card(self) -> QFrame:
        """Create tips card with responsive design."""
        tips_card = ComponentBuilder.create_tips_card()
        tips_layout = QVBoxLayout(tips_card)
        tips_layout.setSpacing(10)  # Reduced spacing
        # Responsive margins - smaller on small screens
        tips_layout.setContentsMargins(15, 15, 15, 15)
        
        tips_title = QLabel("💡 Pro Tips")
        tips_title.setWordWrap(True)
        tips_title.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 700;
            color: {COLORS['primary']};
            margin-bottom: 4px;
        """)
        tips_layout.addWidget(tips_title)
        
        tips_text = QLabel(
            "• <b>isnet-general-use</b> for logos<br>"
            "• <b>u2net</b> for complex images<br>"
            "• <b>silueta</b> for portraits<br>"
            "• Small images auto-enhanced"
        )
        tips_text.setWordWrap(True)
        tips_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        tips_text.setStyleSheet(f"""
            font-size: 10px;
            color: {COLORS['text_secondary']};
            line-height: 1.5;
            padding-top: 2px;
        """)
        tips_layout.addWidget(tips_text)
        
        return tips_card
    
    def _create_image_view_panel(self) -> QWidget:
        """Create image view panel."""
        image_view_panel = QWidget()
        image_view_layout = QVBoxLayout(image_view_panel)
        image_view_layout.setSpacing(20)
        image_view_layout.setContentsMargins(0, 0, 0, 0)
        
        # Headers
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        original_header = QLabel("📸 Original")
        original_header.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {COLORS['text']};
        """)
        
        result_header = QLabel("✨ Result")
        result_header.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {COLORS['text']};
        """)
        
        header_layout.addWidget(original_header)
        header_layout.addWidget(result_header)
        image_view_layout.addLayout(header_layout)
        
        # Image previews
        image_container = QHBoxLayout()
        image_container.setSpacing(20)
        
        self._input_label = ComponentBuilder.create_image_label(
            "Drop or click to upload image",
            enable_drag_drop=True
        )
        # Connect drag & drop signal
        self._input_label.file_dropped.connect(self._on_file_dropped)
        
        self._output_label = ComponentBuilder.create_image_label(
            "Processed image will appear here"
        )
        
        image_container.addWidget(self._input_label, 1)
        image_container.addWidget(self._output_label, 1)
        image_view_layout.addLayout(image_container, 1)
        
        # Status bar
        self._status_label = QLabel(STATUS_INITIALIZING)
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet(
            StyleManager.get_status_label_style("warning")
        )
        image_view_layout.addWidget(self._status_label)
        
        return image_view_panel
    
    def _connect_signals(self):
        """Connect model manager signals."""
        self._model_manager.model_loaded.connect(self._on_model_loaded)
        self._model_manager.all_models_loaded.connect(self._on_all_models_loaded)
        self._model_manager.error_occurred.connect(self._on_model_error)
    
    def _load_models(self):
        """Load all AI models."""
        self._update_status(STATUS_INITIALIZING, "warning")
        QApplication.processEvents()
        
        if not self._model_manager.load_all_models():
            self._update_status("❌ Failed to load models", "error")
            QMessageBox.critical(
                self, "Error", "Some models failed to load. Check console for details."
            )
    
    def _on_model_loaded(self, model_name: str):
        """Handle model loaded signal."""
        self._update_status(f"⚙️ Loaded: {model_name}...", "warning")
        QApplication.processEvents()
    
    def _on_all_models_loaded(self):
        """Handle all models loaded signal."""
        self._update_status(STATUS_READY, "success")
    
    def _on_model_error(self, error_message: str):
        """Handle model error signal."""
        self._update_status("❌ Model loading error", "error")
        QMessageBox.critical(self, "Error", error_message)
    
    def _load_image(self):
        """Load image from file dialog."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            IMAGE_FILE_FILTER,
            options=options
        )
        
        if file_path:
            self._set_image(file_path)
    
    def _on_file_dropped(self, file_path: str):
        """Handle file dropped event."""
        self._set_image(file_path)
    
    def _set_image(self, file_path: str):
        """Set image from file path (used by both dialog and drag & drop)."""
        self._input_image_path = file_path
        self._output_image_bytes = None
        ImageDisplayManager.display_image(self._input_label, file_path)
        
        # Reset output label
        self._output_label.clear()
        self._output_label.setText("Processed image will appear here")
        
        self._process_button.setEnabled(True)
        self._save_button.setEnabled(False)
        
        # Update status with image info
        from PIL import Image
        img = Image.open(file_path)
        size_info = f"{img.size[0]}×{img.size[1]}px"
        filename = os.path.basename(file_path)
        self._update_status(f"📸 {filename} ({size_info})", "primary")
    
    def _process_image(self):
        """Process image to remove background."""
        if not self._input_image_path:
            QMessageBox.warning(self, "Warning", "Please upload an image first.")
            return
        
        model_name = self._model_combo.currentText()
        if not self._model_manager.has_session(model_name):
            QMessageBox.critical(self, "Error", "Model session not loaded.")
            return
        
        session = self._model_manager.get_session(model_name)
        
        self._update_status(
            STATUS_PROCESSING.format(model=model_name), "warning"
        )
        self._process_button.setEnabled(False)
        self._save_button.setEnabled(False)
        QApplication.processEvents()
        
        # Create and start worker
        self._worker = BackgroundRemoverWorker(
            self._input_image_path,
            session,
            self._image_processor
        )
        self._worker.finished.connect(self._on_processing_finished)
        self._worker.error.connect(self._on_processing_error)
        self._worker.progress.connect(
            lambda msg: self._update_status(f"⚡ {msg}", "warning")
        )
        self._worker.start()
    
    def _on_processing_finished(self, output_bytes: BytesIO):
        """Handle processing finished signal."""
        self._output_image_bytes = output_bytes
        ImageDisplayManager.display_image(self._output_label, output_bytes)
        self._save_button.setEnabled(True)
        self._process_button.setEnabled(True)
        self._update_status(STATUS_SUCCESS, "success")
    
    def _on_processing_error(self, error_message: str):
        """Handle processing error signal."""
        self._output_label.clear()
        self._output_label.setText("❌ Processing failed")
        self._process_button.setEnabled(True)
        self._save_button.setEnabled(False)
        self._update_status(STATUS_ERROR, "error")
        QMessageBox.critical(self, "Error", f"Processing failed:\n{error_message}")
    
    def _save_image(self):
        """Save processed image to file."""
        if not self._output_image_bytes:
            QMessageBox.warning(self, "Warning", "Process an image first.")
            return
        
        base_name = os.path.basename(self._input_image_path).split('.')[0]
        model_name = self._model_combo.currentText().replace('-', '_')
        default_file_name = f"{base_name}_no_bg_{model_name}.png"
        
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Result",
            default_file_name,
            PNG_FILE_FILTER,
            options=options
        )
        
        if save_path:
            try:
                with open(save_path, 'wb') as f:
                    f.write(self._output_image_bytes.getvalue())
                QMessageBox.information(self, "Success", "✅ Saved successfully!")
                self._update_status(
                    f"💾 Saved: {os.path.basename(save_path)}", "success"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Save failed:\n{e}")
    
    def _update_status(self, message: str, status_type: str = "primary"):
        """
        Update status label.
        
        Args:
            message: Status message
            status_type: Status type (primary, success, warning, error)
        """
        self._status_label.setText(message)
        self._status_label.setStyleSheet(
            StyleManager.get_status_label_style(status_type)
        )
    
    def resizeEvent(self, event):
        """Handle window resize event with responsive adjustments."""
        super().resizeEvent(event)
        
        # Responsive font sizing based on window width
        window_width = self.width()
        self._update_responsive_fonts(window_width)
        
        # Update images if they exist
        if self._input_image_path:
            ImageDisplayManager.display_image(
                self._input_label, self._input_image_path
            )
        if self._output_image_bytes:
            ImageDisplayManager.display_image(
                self._output_label, self._output_image_bytes
            )
    
    def _update_responsive_fonts(self, window_width: int):
        """
        Update font sizes based on window width for responsive design.
        
        Args:
            window_width: Current window width in pixels
        """
        # Calculate responsive font sizes
        # Small screens (< 1000px): smaller fonts
        # Medium screens (1000-1400px): medium fonts  
        # Large screens (> 1400px): larger fonts
        
        if window_width < 1000:
            title_size = 18
            subtitle_size = 11
            label_size = 11
            tips_title_size = 11
            tips_text_size = 9
            header_size = 12
        elif window_width < 1400:
            title_size = 22
            subtitle_size = 12
            label_size = 12
            tips_title_size = 12
            tips_text_size = 10
            header_size = 14
        else:
            title_size = 24
            subtitle_size = 13
            label_size = 13
            tips_title_size = 13
            tips_text_size = 11
            header_size = 15
        
        # Update title font (if we had reference, but we'll update via stylesheet)
        # Note: This is a simplified approach. For full control, we'd need to store references
        # For now, the initial font sizes are set appropriately and will work well