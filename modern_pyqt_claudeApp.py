# Gerekli Kütüphaneler: PyQt5, rembg, Pillow
# Kurulum: pip install pyqt5 onnxruntime-gpu rembg Pillow

import os
import sys
from rembg import remove, new_session 
from PIL import Image
from io import BytesIO
import numpy as np

# PyQt5 Kütüphaneleri
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve

# Modern Renk Paleti
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

# İşlemeyi Arka Plana Taşıyan Worker Sınıfı
class Worker(QThread):
    finished = pyqtSignal(BytesIO)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, input_path, model_session):
        super().__init__()
        self.input_path = input_path
        self.session = model_session

    def run(self):
        try:
            self.progress.emit("Görüntü yükleniyor...")
            input_image = Image.open(self.input_path)
            
            original_size = input_image.size
            max_dimension = max(original_size)
            
            if max_dimension < 1024:
                self.progress.emit("Görüntü optimize ediliyor...")
                scale_factor = 1024 / max_dimension
                new_size = (int(original_size[0] * scale_factor), 
                           int(original_size[1] * scale_factor))
                input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
            
            self.progress.emit("Arka plan siliniyor...")
            output_image = remove(input_image, session=self.session)
            
            if max_dimension < 1024:
                self.progress.emit("Son işlemler...")
                output_image = output_image.resize(original_size, Image.Resampling.LANCZOS)
            
            self.progress.emit("Keskinleştiriliyor...")
            output_image = self.sharpen_edges(output_image)
            
            output_bytes = BytesIO()
            output_image.save(output_bytes, format="PNG", optimize=False, compress_level=1)
            output_bytes.seek(0)
            
            self.finished.emit(output_bytes)
        except Exception as e:
            self.error.emit(str(e))
    
    def sharpen_edges(self, image):
        if image.mode != 'RGBA':
            return image
        
        img_array = np.array(image)
        alpha = img_array[:, :, 3]
        
        non_zero_alpha = alpha[alpha > 0]
        if len(non_zero_alpha) > 0:
            avg_alpha = np.mean(non_zero_alpha)
            threshold = int(max(100, min(180, avg_alpha * 0.6)))
        else:
            threshold = 127
        
        alpha = np.where(alpha > threshold, 255, 0).astype(np.uint8)
        img_array[:, :, 3] = alpha
        
        return Image.fromarray(img_array)


class BackgroundRemoverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Background Remover AI")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)
        
        self.input_image_path = None
        self.output_image_bytes = None
        self.sessions = {}
        self.worker = None 

        self.setup_window_style()
        self.init_ui()
        self.load_models()

    def setup_window_style(self):
        self.setStyleSheet(f"""
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
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- SOL PANEL ---
        control_panel = QFrame()
        control_panel.setFixedWidth(360)
        control_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['surface']}, 
                    stop:1 #1a2332);
                border-radius: 20px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 10)
        control_panel.setGraphicsEffect(shadow)
        
        control_layout = QVBoxLayout(control_panel)
        control_layout.setSpacing(20)
        control_layout.setContentsMargins(25, 30, 25, 30)

        # Başlık
        title = QLabel("🎨 Background Remover")
        title.setStyleSheet(f"""
            font-size: 26px;
            font-weight: 700;
            color: {COLORS['text']};
            margin-bottom: 5px;
        """)
        control_layout.addWidget(title)

        subtitle = QLabel("AI-Powered Image Processing")
        subtitle.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
            margin-bottom: 15px;
        """)
        control_layout.addWidget(subtitle)

        # Ayırıcı
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px; margin: 10px 0px;")
        control_layout.addWidget(line)

        control_layout.addSpacing(10)

        # Model Seçimi
        model_label = QLabel("AI Model")
        model_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {COLORS['text']};
            margin-bottom: 8px;
        """)
        control_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["isnet-general-use", "u2net", "u2netp", "silueta"])
        self.model_combo.setCurrentIndex(0)
        control_layout.addWidget(self.model_combo)

        control_layout.addSpacing(20)

        # Butonlar
        self.load_button = self.create_button("📁 Upload Image", COLORS['primary'])
        self.load_button.clicked.connect(self.load_image)
        control_layout.addWidget(self.load_button)

        self.process_button = self.create_button("✨ Remove Background", COLORS['accent'])
        self.process_button.clicked.connect(self.process_image)
        self.process_button.setEnabled(False)
        control_layout.addWidget(self.process_button)

        self.save_button = self.create_button("💾 Save Result", COLORS['success'])
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        control_layout.addWidget(self.save_button)

        control_layout.addSpacing(20)

        # İpuçları Card
        tips_card = QFrame()
        tips_card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(99, 102, 241, 0.08);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 12px;
                padding: 18px;
            }}
        """)
        tips_layout = QVBoxLayout(tips_card)
        tips_layout.setSpacing(10)
        
        tips_title = QLabel("💡 Pro Tips")
        tips_title.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {COLORS['primary']};
        """)
        tips_layout.addWidget(tips_title)

        tips_text = QLabel(
            "• <b>isnet-general-use</b> for logos<br>"
            "• <b>u2net</b> for complex images<br>"
            "• <b>silueta</b> for portraits<br>"
            "• Small images auto-enhanced"
        )
        tips_text.setWordWrap(True)
        tips_text.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_secondary']};
            line-height: 20px;
        """)
        tips_layout.addWidget(tips_text)
        control_layout.addWidget(tips_card)

        control_layout.addStretch(1)

        main_layout.addWidget(control_panel)

        # --- SAĞ PANEL ---
        image_view_panel = QWidget()
        image_view_layout = QVBoxLayout(image_view_panel)
        image_view_layout.setSpacing(20)
        image_view_layout.setContentsMargins(0, 0, 0, 0)

        # Başlıklar
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        original_header = QLabel("📸 Original")
        original_header.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 600;
            color: {COLORS['text']};
        """)
        
        result_header = QLabel("✨ Result")
        result_header.setStyleSheet(f"""
            font-size: 15px;
            font-weight: 600;
            color: {COLORS['text']};
        """)
        
        header_layout.addWidget(original_header)
        header_layout.addWidget(result_header)
        image_view_layout.addLayout(header_layout)

        # Görüntü önizlemeleri
        image_container = QHBoxLayout()
        image_container.setSpacing(20)
        
        self.input_label = self.create_image_label("Drop or click to upload image")
        self.output_label = self.create_image_label("Processed image will appear here")
        
        image_container.addWidget(self.input_label, 1)
        image_container.addWidget(self.output_label, 1)
        image_view_layout.addLayout(image_container, 1)

        # Durum çubuğu
        self.status_label = QLabel("🚀 Initializing AI models...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['surface']}, 
                stop:1 {COLORS['surface_light']});
            color: {COLORS['warning']};
            padding: 16px 20px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)
        image_view_layout.addWidget(self.status_label)

        main_layout.addWidget(image_view_panel, 1)

    def create_button(self, text, color):
        """Modern buton oluştur"""
        button = QPushButton(text)
        hover_color = self.darken_color(color)
        
        button.setStyleSheet(f"""
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
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        button.setGraphicsEffect(shadow)
        
        return button

    def create_image_label(self, text):
        """Görüntü önizleme etiketi oluştur"""
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumSize(400, 350)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setScaledContents(False)
        label.setStyleSheet(f"""
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
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 8)
        label.setGraphicsEffect(shadow)
        
        return label

    def darken_color(self, hex_color):
        """Rengi koyulaştır"""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        color.setHsl(h, s, max(0, l - 20), a)
        return color.name()

    def load_models(self):
        models = ["isnet-general-use", "u2net", "u2netp", "silueta"]
        
        try:
            for model_name in models:
                self.update_status(f"⚙️ Loading: {model_name}...", "warning")
                QApplication.processEvents()
                
                self.sessions[model_name] = new_session(
                    model_name, 
                    alpha_matting=False,
                    post_process_mask=False
                )

            self.update_status("✅ Ready! Upload an image to start", "success")

        except Exception as e:
            self.update_status("❌ Failed to load models", "error")
            QMessageBox.critical(self, "Error", f"Model loading failed:\n{e}")
            self.process_button.setEnabled(False)

    def load_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)", 
            options=options
        )
        
        if file_path:
            self.input_image_path = file_path
            self.output_image_bytes = None
            self.display_image(self.input_label, file_path)
            
            # Output label'ı sıfırla
            self.output_label.clear()
            self.output_label.setText("Processed image will appear here")
            
            self.process_button.setEnabled(True)
            self.save_button.setEnabled(False)
            
            img = Image.open(file_path)
            size_info = f"{img.size[0]}×{img.size[1]}px"
            filename = os.path.basename(file_path)
            self.update_status(f"📸 {filename} ({size_info})", "primary")

    def display_image(self, label: QLabel, path_or_bytes):
        if isinstance(path_or_bytes, str):
            pixmap = QPixmap(path_or_bytes)
        elif isinstance(path_or_bytes, BytesIO):
            pixmap = QPixmap()
            pixmap.loadFromData(path_or_bytes.getvalue())
        else:
            return
            
        if pixmap.isNull():
            return
        
        # Label boyutuna göre ölçeklendir
        available_size = label.size()
        scaled_pixmap = pixmap.scaled(
            available_size.width() - 40,
            available_size.height() - 40,
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        label.setText("")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.input_image_path:
            self.display_image(self.input_label, self.input_image_path)
        if self.output_image_bytes:
            self.display_image(self.output_label, self.output_image_bytes)

    def process_image(self):
        if not self.input_image_path:
            QMessageBox.warning(self, "Warning", "Please upload an image first.")
            return

        model_adi = self.model_combo.currentText()
        if model_adi not in self.sessions:
            QMessageBox.critical(self, "Error", "Model session not loaded.")
            return

        current_session = self.sessions[model_adi]
        
        self.update_status(f"⚡ Processing with {model_adi}...", "warning")
        self.process_button.setEnabled(False)
        self.save_button.setEnabled(False)
        QApplication.processEvents()

        self.worker = Worker(self.input_image_path, current_session)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.progress.connect(lambda msg: self.update_status(f"⚡ {msg}", "warning"))
        self.worker.start()

    def on_processing_finished(self, output_bytes: BytesIO):
        self.output_image_bytes = output_bytes
        self.display_image(self.output_label, self.output_image_bytes)
        self.save_button.setEnabled(True)
        self.process_button.setEnabled(True)
        self.update_status("✨ Success! Ready to save", "success")
        
    def on_processing_error(self, error_message: str):
        self.output_label.clear()
        self.output_label.setText("❌ Processing failed")
        self.process_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.update_status("❌ Processing failed", "error")
        QMessageBox.critical(self, "Error", f"Processing failed:\n{error_message}")

    def save_image(self):
        if not self.output_image_bytes:
            QMessageBox.warning(self, "Warning", "Process an image first.")
            return
            
        base_name = os.path.basename(self.input_image_path).split('.')[0]
        model_name = self.model_combo.currentText().replace('-', '_')
        default_file_name = f"{base_name}_no_bg_{model_name}.png"

        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Result", 
            default_file_name,
            "PNG Files (*.png)", 
            options=options
        )
        
        if save_path:
            try:
                with open(save_path, 'wb') as f:
                    f.write(self.output_image_bytes.getvalue())
                QMessageBox.information(self, "Success", f"✅ Saved successfully!")
                self.update_status(f"💾 Saved: {os.path.basename(save_path)}", "success")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Save failed:\n{e}")

    def update_status(self, message, status_type="primary"):
        colors = {
            'primary': COLORS['primary'],
            'success': COLORS['success'],
            'warning': COLORS['warning'],
            'error': COLORS['error']
        }
        
        self.status_label.setText(message)
        color = colors.get(status_type, COLORS['primary'])
        self.status_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['surface']}, 
                stop:1 {COLORS['surface_light']});
            color: {color};
            padding: 16px 20px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid {COLORS['border']};
        """)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        window = BackgroundRemoverApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application startup error: {e}")
        import traceback
        traceback.print_exc()