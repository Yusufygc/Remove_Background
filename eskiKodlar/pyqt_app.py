# Gerekli Kütüphaneler: PyQt5, rembg, Pillow
# Kurulum: pip install pyqt5 onnxruntime-gpu rembg Pillow

import os
import sys
from rembg import remove, new_session 
from PIL import Image
from io import BytesIO

# PyQt5 Kütüphaneleri
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal

# --- GPU İÇİN KRİTİK AYAR ---
# Conda ortamında onnxruntime-gpu kurulu olduğu varsayılır. 
# Bu satır, önceki denemelerdeki CPU zorlamasıydı ve GPU için kaldırıldı.
# os.environ["ONNX_PROVIDERS"] = "CPUExecutionProvider" 

# İşlemeyi Arka Plana Taşıyan Worker Sınıfı (Threading)
class Worker(QThread):
    finished = pyqtSignal(BytesIO)
    error = pyqtSignal(str)

    def __init__(self, input_path, model_session):
        super().__init__()
        self.input_path = input_path
        self.session = model_session

    def run(self):
        try:
            input_image = Image.open(self.input_path)
            
            # rembg.remove, session içindeki alpha_matting=False ve post_process_mask=False 
            # ayarlarına göre işlemi yapar.
            output_image = remove(input_image, session=self.session)
            
            output_bytes = BytesIO()
            output_image.save(output_bytes, format="PNG")
            output_bytes.seek(0)
            
            self.finished.emit(output_bytes)
        except Exception as e:
            self.error.emit(str(e))


class BackgroundRemoverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Arka Plan Silici")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        self.input_image_path = None
        self.output_image_bytes = None
        self.sessions = {} # Model oturumlarını tutacak sözlük
        self.worker = None 

        self.init_ui()
        self.load_models() # Uygulama başlarken modelleri yükle

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- SOL PANEL ---
        control_panel = QFrame()
        control_panel.setFixedWidth(300)
        control_panel.setStyleSheet("QFrame { background-color: #f0f0f0; border-right: 1px solid #ddd; }")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)

        control_layout.addWidget(QLabel("<h2>Arka Plan Silme Kontrolleri</h2>"))
        control_layout.addWidget(QLabel("---"))

        control_layout.addWidget(QLabel("<b>Model Seçimi:</b>"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["isnet-general-use", "mask", "u2net", "u2netp"])
        self.model_combo.setToolTip("isnet-general-use: En iyi genel keskinlik ve logo maskeleme için kullanılır.")
        control_layout.addWidget(self.model_combo)
        
        control_layout.addSpacing(20)

        self.load_button = QPushButton("1. Resim Yükle...")
        self.load_button.setIcon(QIcon.fromTheme("document-open"))
        self.load_button.clicked.connect(self.load_image)
        control_layout.addWidget(self.load_button)

        self.process_button = QPushButton("2. Arka Planı Sil")
        self.process_button.setIcon(QIcon.fromTheme("media-play"))
        self.process_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; border-radius: 5px; }")
        self.process_button.clicked.connect(self.process_image)
        self.process_button.setEnabled(False)
        control_layout.addWidget(self.process_button)

        self.save_button = QPushButton("3. Sonucu Kaydet...")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        control_layout.addWidget(self.save_button)
        
        control_layout.addStretch(1)

        main_layout.addWidget(control_panel)

        # --- SAĞ PANEL ---
        image_view_panel = QWidget()
        image_view_layout = QVBoxLayout(image_view_panel)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>ORİJİNAL GÖRÜNTÜ</b>"))
        header_layout.addWidget(QLabel("<b>ARKA PLANSIZ SONUÇ</b>"))
        image_view_layout.addLayout(header_layout)

        image_layout = QHBoxLayout()
        self.input_label = QLabel("Resim Yüklemediniz")
        self.output_label = QLabel("Sonuç Burada Görünecek")
        
        for label in [self.input_label, self.output_label]:
            label.setAlignment(Qt.AlignCenter)
            label.setFrameShape(QFrame.StyledPanel)
            label.setFrameShadow(QFrame.Sunken)
            label.setScaledContents(False)
            label.setStyleSheet("border: 1px dashed #ccc; padding: 10px;")
            image_layout.addWidget(label)
            
        image_view_layout.addLayout(image_layout)
        
        self.status_label = QLabel("Modeller Yükleniyor... Lütfen Bekleyin.")
        self.status_label.setStyleSheet("color: orange; padding: 5px; font-weight: bold;")
        image_view_layout.addWidget(self.status_label)


        main_layout.addWidget(image_view_panel)

    def load_models(self):
        """Uygulama başlatıldığında modelleri yükler ve oturumları hazırlar."""
        models = ["isnet-general-use", "mask", "u2net", "u2netp"]
        self.status_label.setText("Modeller yükleniyor... Bu ilk çalıştırmada biraz sürebilir.")
        QApplication.processEvents()
        
        try:
            for model_name in models:
                # Keskin logo maskeleri için en önemli iki ayar:
                # alpha_matting=False: Yumuşak kenar geçişlerini engeller.
                # post_process_mask=False: rembg'nin maskeyi otomatik yumuşatmasını engeller.
                self.sessions[model_name] = new_session(
                    model_name, 
                    alpha_matting=False,
                    post_process_mask=False 
                )
                self.status_label.setText(f"Model yüklendi: {model_name}")
                QApplication.processEvents()

            self.status_label.setText("Hazır. Lütfen bir resim yükleyin.")
            self.status_label.setStyleSheet("color: green; padding: 5px; font-weight: bold;")

        except Exception as e:
            self.status_label.setText("HATA: Model yüklenemedi!")
            self.status_label.setStyleSheet("color: red; padding: 5px; font-weight: bold;")
            QMessageBox.critical(self, "Model Yükleme Hatası", f"Modeller yüklenirken bir hata oluştu:\n{e}")
            self.process_button.setEnabled(False)


    def load_image(self):
        """Kullanıcının dosya seçme diyalogu ile resim yüklemesini sağlar."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Resim Yükle", 
            "", 
            "Resim Dosyaları (*.png *.jpg *.jpeg)", 
            options=options
        )
        
        if file_path:
            self.input_image_path = file_path
            self.output_image_bytes = None
            self.display_image(self.input_label, file_path)
            self.output_label.setText("Sonuç Burada Görünecek")
            self.process_button.setEnabled(True)
            self.save_button.setEnabled(False)
            self.status_label.setText(f"Resim yüklendi: {os.path.basename(file_path)}. Arka planı silmek için butona basın.")

    def display_image(self, label: QLabel, path_or_bytes):
        """Görüntüyü QLabel içinde gösterir ve boyutu ayarlar."""
        
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
        """Pencere yeniden boyutlandırıldığında resimleri yeniden çizer."""
        super().resizeEvent(event)
        if self.input_image_path:
            self.display_image(self.input_label, self.input_image_path)
        if self.output_image_bytes:
            self.display_image(self.output_label, self.output_image_bytes)

    def process_image(self):
        """Arka plan silme işlemini başlatır (Worker Thread kullanarak)."""
        if not self.input_image_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir resim yükleyin.")
            return

        model_adi = self.model_combo.currentText()
        if model_adi not in self.sessions:
             QMessageBox.critical(self, "Hata", "Model oturumu yüklenemedi. Lütfen uygulamayı yeniden başlatın.")
             return

        current_session = self.sessions[model_adi]
        self.status_label.setText(f"İşleniyor... Lütfen bekleyin. Model: '{model_adi}' (GPU/CPU İşlemi)")
        self.process_button.setEnabled(False) # İşlem bitene kadar butonu kapat
        self.save_button.setEnabled(False)
        QApplication.processEvents()

        # Worker thread'i başlatma
        self.worker = Worker(self.input_image_path, current_session)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()

    def on_processing_finished(self, output_bytes: BytesIO):
        """Worker thread başarılı olduğunda çağrılır."""
        self.output_image_bytes = output_bytes
        self.display_image(self.output_label, self.output_image_bytes)
        self.save_button.setEnabled(True)
        self.process_button.setEnabled(True)
        self.status_label.setText(f"BAŞARILI! Sonuç hazır. Kaydetmek için butona basın.")
        self.status_label.setStyleSheet("color: green; padding: 5px; font-weight: bold;")
        
    def on_processing_error(self, error_message: str):
        """Worker thread hata verdiğinde çağrılır."""
        self.output_label.setText("İşlem Başarısız Oldu.")
        self.process_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.status_label.setText("İşlem Başarısız Oldu. Hata mesajı için uyarıyı kontrol edin.")
        self.status_label.setStyleSheet("color: red; padding: 5px; font-weight: bold;")
        QMessageBox.critical(self, "Hata", f"Arka plan silme işlemi başarısız oldu:\n{error_message}")


    def save_image(self):
        """İşlenmiş resmi PNG olarak kaydeder."""
        if not self.output_image_bytes:
            QMessageBox.warning(self, "Uyarı", "Önce arka plan silme işlemini tamamlayın.")
            return
            
        base_name = os.path.basename(self.input_image_path).split('.')[0]
        model_name = self.model_combo.currentText().replace('-', '_')
        default_file_name = f"{base_name}_arka_plansiz_{model_name}_kesin_sonuc.png" 

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
                QMessageBox.information(self, "Başarılı", f"Dosya başarıyla kaydedildi:\n{save_path}")
                self.status_label.setText("Resim başarıyla kaydedildi.")
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
