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
    QCheckBox, QSpinBox, QGroupBox
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal

# İşlemeyi Arka Plana Taşıyan Worker Sınıfı (Threading)
class Worker(QThread):
    finished = pyqtSignal(BytesIO)
    error = pyqtSignal(str)

    def __init__(self, input_path, model_session, apply_sharpening=False, threshold=127):
        super().__init__()
        self.input_path = input_path
        self.session = model_session
        self.apply_sharpening = apply_sharpening
        self.threshold = threshold

    def run(self):
        try:
            # Resmi yüksek kalitede aç
            input_image = Image.open(self.input_path)
            
            # Eğer resim çok küçükse, kaliteyi korumak için büyült
            original_size = input_image.size
            max_dimension = max(original_size)
            
            if max_dimension < 1024:
                scale_factor = 1024 / max_dimension
                new_size = (int(original_size[0] * scale_factor), 
                           int(original_size[1] * scale_factor))
                input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Arka planı sil
            output_image = remove(input_image, session=self.session)
            
            # Orijinal boyuta geri getir (eğer büyütüldüyse)
            if max_dimension < 1024:
                output_image = output_image.resize(original_size, Image.Resampling.LANCZOS)
            
            # Keskinleştirme işlemi (opsiyonel)
            if self.apply_sharpening:
                output_image = self.sharpen_edges(output_image, self.threshold)
            
            output_bytes = BytesIO()
            output_image.save(output_bytes, format="PNG", optimize=False, compress_level=1)
            output_bytes.seek(0)
            
            self.finished.emit(output_bytes)
        except Exception as e:
            self.error.emit(str(e))
    
    def sharpen_edges(self, image, threshold):
        """Alpha kanalını keskinleştirerek bulanıklığı azaltır"""
        if image.mode != 'RGBA':
            return image
        
        # Numpy array'e çevir
        img_array = np.array(image)
        
        # Alpha kanalını al
        alpha = img_array[:, :, 3]
        
        # Eşik değeri uygula (keskin kenarlar için)
        alpha = np.where(alpha > threshold, 255, 0).astype(np.uint8)
        
        # Alpha kanalını geri yerleştir
        img_array[:, :, 3] = alpha
        
        return Image.fromarray(img_array)


class BackgroundRemoverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Arka Plan Silici - Keskin Logo Sonuçları")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(900, 600)
        
        self.input_image_path = None
        self.output_image_bytes = None
        self.sessions = {}
        self.worker = None 

        self.init_ui()
        self.load_models()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- SOL PANEL ---
        control_panel = QFrame()
        control_panel.setFixedWidth(340)
        control_panel.setStyleSheet("QFrame { background-color: #f0f0f0; border-right: 1px solid #ddd; }")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)

        control_layout.addWidget(QLabel("<h2>Arka Plan Silme Kontrolleri</h2>"))
        control_layout.addWidget(QLabel("---"))

        # Model Seçimi
        control_layout.addWidget(QLabel("<b>Model Seçimi:</b>"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["isnet-general-use", "u2net", "u2netp", "silueta"])
        self.model_combo.setToolTip("isnet-general-use: En iyi genel sonuçlar için önerilir")
        control_layout.addWidget(self.model_combo)
        
        control_layout.addSpacing(10)

        # Keskinleştirme Ayarları
        sharp_group = QGroupBox("Keskinlik Ayarları")
        sharp_layout = QVBoxLayout()
        
        self.sharpen_checkbox = QCheckBox("Kenar Keskinleştirme Uygula")
        self.sharpen_checkbox.setChecked(True)
        self.sharpen_checkbox.setToolTip("Logo kenarlarını daha keskin yapar")
        sharp_layout.addWidget(self.sharpen_checkbox)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Eşik Değeri:"))
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(50, 250)
        self.threshold_spinbox.setValue(127)
        self.threshold_spinbox.setToolTip("Düşük: Yumuşak kenarlar (50-100)\nOrta: Dengeli (100-150)\nYüksek: Çok keskin (150-250)")
        threshold_layout.addWidget(self.threshold_spinbox)
        sharp_layout.addLayout(threshold_layout)
        
        sharp_group.setLayout(sharp_layout)
        control_layout.addWidget(sharp_group)
        
        control_layout.addSpacing(20)

        # Butonlar
        self.load_button = QPushButton("1. Resim Yükle...")
        self.load_button.setIcon(QIcon.fromTheme("document-open"))
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setMinimumHeight(40)
        control_layout.addWidget(self.load_button)

        self.process_button = QPushButton("2. Arka Planı Sil")
        self.process_button.setIcon(QIcon.fromTheme("media-play"))
        self.process_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; border-radius: 5px; font-size: 14px; } QPushButton:hover { background-color: #45a049; }")
        self.process_button.setMinimumHeight(50)
        self.process_button.clicked.connect(self.process_image)
        self.process_button.setEnabled(False)
        control_layout.addWidget(self.process_button)

        self.save_button = QPushButton("3. Sonucu Kaydet...")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        control_layout.addWidget(self.save_button)
        
        control_layout.addSpacing(20)
        
        # İpuçları
        tips_label = QLabel(
            "<b>💡 İpuçları:</b><br>"
            "• Logolar için <b>isnet-general-use</b> kullanın<br>"
            "• Keskin kenarlar için eşik değerini 150-200 yapın<br>"
            "• Yumuşak geçişler için 80-120 kullanın<br>"
            "• Küçük resimler otomatik büyütülür"
        )
        tips_label.setWordWrap(True)
        tips_label.setStyleSheet("background-color: #e3f2fd; padding: 10px; border-radius: 5px; font-size: 11px;")
        control_layout.addWidget(tips_label)
        
        control_layout.addStretch(1)

        main_layout.addWidget(control_panel)

        # --- SAĞ PANEL ---
        image_view_panel = QWidget()
        image_view_layout = QVBoxLayout(image_view_panel)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b style='font-size: 14px;'>ORİJİNAL GÖRÜNTÜ</b>"))
        header_layout.addWidget(QLabel("<b style='font-size: 14px;'>ARKA PLANSIZ SONUÇ</b>"))
        image_view_layout.addLayout(header_layout)

        image_layout = QHBoxLayout()
        self.input_label = QLabel("Resim Yüklemediniz")
        self.output_label = QLabel("Sonuç Burada Görünecek")
        
        for label in [self.input_label, self.output_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setFrameShape(QFrame.StyledPanel)
            label.setFrameShadow(QFrame.Sunken)
            label.setScaledContents(False)
            label.setStyleSheet("border: 2px dashed #999; padding: 10px; background-color: white;")
            image_layout.addWidget(label)
            
        image_view_layout.addLayout(image_layout)
        
        self.status_label = QLabel("Modeller Yükleniyor... Lütfen Bekleyin.")
        self.status_label.setStyleSheet("color: orange; padding: 8px; font-weight: bold; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        image_view_layout.addWidget(self.status_label)

        main_layout.addWidget(image_view_panel)

    def load_models(self):
        """Uygulama başlatıldığında modelleri yükler"""
        models = ["isnet-general-use", "u2net", "u2netp", "silueta"]
        self.status_label.setText("Modeller yükleniyor... İlk çalıştırmada biraz sürebilir.")
        QApplication.processEvents()
        
        try:
            for model_name in models:
                self.sessions[model_name] = new_session(
                    model_name, 
                    alpha_matting=False,
                    post_process_mask=False
                )
                self.status_label.setText(f"Model yüklendi: {model_name}")
                QApplication.processEvents()

            self.status_label.setText("✓ Hazır! Lütfen bir resim yükleyin.")
            self.status_label.setStyleSheet("color: green; padding: 8px; font-weight: bold; font-size: 13px;")

        except Exception as e:
            self.status_label.setText("❌ HATA: Model yüklenemedi!")
            self.status_label.setStyleSheet("color: red; padding: 8px; font-weight: bold; font-size: 13px;")
            QMessageBox.critical(self, "Model Yükleme Hatası", f"Modeller yüklenirken bir hata oluştu:\n{e}")
            self.process_button.setEnabled(False)

    def load_image(self):
        """Kullanıcının resim yüklemesini sağlar"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Resim Yükle", 
            "", 
            "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.webp)", 
            options=options
        )
        
        if file_path:
            self.input_image_path = file_path
            self.output_image_bytes = None
            self.display_image(self.input_label, file_path)
            self.output_label.setText("Sonuç Burada Görünecek")
            self.output_label.setPixmap(QPixmap())
            self.process_button.setEnabled(True)
            self.save_button.setEnabled(False)
            
            # Görüntü boyutu bilgisi
            img = Image.open(file_path)
            size_info = f"{img.size[0]}x{img.size[1]} px"
            self.status_label.setText(f"✓ Resim yüklendi: {os.path.basename(file_path)} ({size_info})")
            self.status_label.setStyleSheet("color: blue; padding: 8px; font-weight: bold; font-size: 13px;")

    def display_image(self, label: QLabel, path_or_bytes):
        """Görüntüyü QLabel içinde gösterir"""
        if isinstance(path_or_bytes, str):
            pixmap = QPixmap(path_or_bytes)
        elif isinstance(path_or_bytes, BytesIO):
            pixmap = QPixmap()
            pixmap.loadFromData(path_or_bytes.getvalue())
        else:
            label.setText("Görüntü Yüklenemedi")
            return
            
        if pixmap.isNull():
            label.setText("Görüntü Geçersiz")
            return
            
        scaled_pixmap = pixmap.scaled(
            label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        label.setText("")

    def resizeEvent(self, event):
        """Pencere yeniden boyutlandırıldığında resimleri yeniden çizer"""
        super().resizeEvent(event)
        if self.input_image_path:
            self.display_image(self.input_label, self.input_image_path)
        if self.output_image_bytes:
            self.display_image(self.output_label, self.output_image_bytes)

    def process_image(self):
        """Arka plan silme işlemini başlatır"""
        if not self.input_image_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir resim yükleyin.")
            return

        model_adi = self.model_combo.currentText()
        if model_adi not in self.sessions:
             QMessageBox.critical(self, "Hata", "Model oturumu yüklenemedi. Lütfen uygulamayı yeniden başlatın.")
             return

        current_session = self.sessions[model_adi]
        apply_sharp = self.sharpen_checkbox.isChecked()
        threshold = self.threshold_spinbox.value()
        
        sharp_info = f" (Keskinleştirme: {'Açık' if apply_sharp else 'Kapalı'})" if apply_sharp else ""
        self.status_label.setText(f"⏳ İşleniyor... Model: '{model_adi}'{sharp_info}")
        self.status_label.setStyleSheet("color: orange; padding: 8px; font-weight: bold; font-size: 13px;")
        self.process_button.setEnabled(False)
        self.save_button.setEnabled(False)
        QApplication.processEvents()

        # Worker thread'i başlat
        self.worker = Worker(self.input_image_path, current_session, apply_sharp, threshold)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()

    def on_processing_finished(self, output_bytes: BytesIO):
        """Worker thread başarılı olduğunda çağrılır"""
        self.output_image_bytes = output_bytes
        self.display_image(self.output_label, self.output_image_bytes)
        self.save_button.setEnabled(True)
        self.process_button.setEnabled(True)
        self.status_label.setText(f"✓ BAŞARILI! Sonuç hazır. Kaydetmek için butona basın.")
        self.status_label.setStyleSheet("color: green; padding: 8px; font-weight: bold; font-size: 13px;")
        
    def on_processing_error(self, error_message: str):
        """Worker thread hata verdiğinde çağrılır"""
        self.output_label.setText("❌ İşlem Başarısız Oldu.")
        self.process_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.status_label.setText("❌ İşlem Başarısız!")
        self.status_label.setStyleSheet("color: red; padding: 8px; font-weight: bold; font-size: 13px;")
        QMessageBox.critical(self, "Hata", f"Arka plan silme işlemi başarısız oldu:\n{error_message}")

    def save_image(self):
        """İşlenmiş resmi PNG olarak kaydeder"""
        if not self.output_image_bytes:
            QMessageBox.warning(self, "Uyarı", "Önce arka plan silme işlemini tamamlayın.")
            return
            
        base_name = os.path.basename(self.input_image_path).split('.')[0]
        model_name = self.model_combo.currentText().replace('-', '_')
        sharp_suffix = "_sharp" if self.sharpen_checkbox.isChecked() else ""
        default_file_name = f"{base_name}_no_bg_{model_name}{sharp_suffix}.png" 

        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Sonucu Kaydet", 
            default_file_name,
            "PNG Dosyaları (*.png)", 
            options=options
        )
        
        if save_path:
            try:
                with open(save_path, 'wb') as f:
                    f.write(self.output_image_bytes.getvalue())
                QMessageBox.information(self, "Başarılı", f"✓ Dosya başarıyla kaydedildi:\n{save_path}")
                self.status_label.setText(f"✓ Resim kaydedildi: {os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken bir hata oluştu:\n{e}")

# Uygulamayı Başlatma
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling) 
        
        window = BackgroundRemoverApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Uygulama başlatılırken bir hata oluştu: {e}")
        import traceback
        traceback.print_exc()