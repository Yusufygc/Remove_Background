# Mimari — Background Remover AI

PySide6 + QML masaüstü uygulaması. `rembg` (ONNX tabanlı) modelleriyle görsellerin arka planını kaldırır. Katmanlı OOP/SOLID yapısı.

**Not:** Proje 2026-09-24'te PyQt5 widget tabanlı UI'dan PySide6 + QML'e geçirildi. Eski mimari için bu sayfanın önceki hali yerine bkz [[code-review-2026-09-24]] (geçiş kararı ve gerekçesi orada log'landı).

## Katmanlar ve Modüller

| Katman | Dosya | Sorumluluk |
|---|---|---|
| Giriş noktası | `main.py` | `QGuiApplication` + `QQmlApplicationEngine` kurulumu, `Backend` oluşturma, `qml/Main.qml` yükleme, `resource_path()` ile hem kaynaktan hem PyInstaller `.exe`'den çalışacak yol çözümlemesi |
| İkon | `icons/app_icon.png`, `icons/app_icon.ico` | Uygulama/pencere ikonu (`app.setWindowIcon`) + `.exe` build ikonu |
| Backend köprüsü | `backend/app_backend.py` | `Backend(QObject)` — domain katmanını Property/Signal/Slot ile QML'e bağlar (Facade) |
| QML UI | `qml/Main.qml` | `ApplicationWindow` — pencere düzeni, dosya diyalogları, hata dialogu |
| QML UI | `qml/ControlPanel.qml` | Sol panel: model seçimi, aksiyon butonları, tips card |
| QML UI | `qml/ImageViewPanel.qml` | Sağ panel: orijinal/sonuç önizleme, `DropArea` (sürükle-bırak), status bar |
| QML UI | `qml/StyledButton.qml` | Yeniden kullanılabilir buton bileşeni |
| Domain/Servis | `models/image_processor.py` | `ImageProcessor` — işleme akışını yönetir (upscale → `rembg.remove(alpha_matting=True, post_process_mask=True)` → downscale) |
| Domain/Servis | `models/image_enhancer.py` | `ImageResizer` — küçük görselleri işlem öncesi büyütür/sonra geri küçültür |
| Model yönetimi | `models/model_manager.py` | `ModelManager` — rembg session'larını yükler/önbelleğe alır |
| Worker | `workers/background_remover_worker.py` | `BackgroundRemoverWorker` (`QThread`) — işlemi arka planda çalıştırır, `Signal` ile bildirir |
| Sabitler | `utils/constants.py` | Renk paleti (`COLORS`), model listesi, boyut/işleme sabitleri — **tek doğruluk kaynağı** |
| Sabitler | `utils/strings.py` | Tüm arayüz metinleri (Türkçe) — tek doğruluk kaynağı, QML'de literal metin yok |
| Sabitler | `utils/icons.py` | İkon adı → `qml/icons/*.svg` yolu eşlemesi — tek doğruluk kaynağı, emoji kullanılmıyor |

## Kullanılan Design Pattern'ler

- **Factory + Repository** — `ModelManager.load_model()` (factory, `rembg.new_session` üretir) + `get_session()`/`has_session()` (repository).
- **(Kaldırıldı) Strategy** — `ImageEnhancementStrategy`/`EdgeSharpeningStrategy` (elle alfa kanalı eşikleme, 0/255 binarize) kaldırıldı. `rembg`'nin dahili `alpha_matting`/`post_process_mask` özellikleri (bkz `models/image_processor.py`) aynı ihtiyacı (kenar kalitesi) çok daha doğru karşılıyor — bkz [[code-review-2026-09-24]] madde 12.
- **Observer** — Qt `Signal`/`Slot` mekanizması: `ModelManager` (`model_loaded`, `all_models_loaded`, `error_occurred`) ve `BackgroundRemoverWorker` (`finished`, `error`, `progress`) `Backend`'e olay bildirir; `Backend` de kendi Property NOTIFY sinyalleriyle QML'e bildirir.
- **Facade** — `Backend(QObject)`: `ModelManager` + `ImageProcessor` + `BackgroundRemoverWorker`'ı tek bir QML-uyumlu arayüz arkasında toplar. `main.py`'de `engine.rootContext().setContextProperty("backend", backend)` ile QML'e tek nesne olarak sunulur. Aynı `Backend`, `utils/constants.py`/`utils/icons.py`/`utils/strings.py`'yi de Property olarak QML'e sunar — **hiçbir `.qml` dosyası renk kodu, SVG yolu veya metin literal'i içermez**, hepsi `backend.colorX` / `backend.iconX` / `backend.stringX` binding'i. Yeni bir renk/ikon/metin eklemek → ilgili Python modülüne ekle + `Backend`'e Property olarak ekle; QML dosyaları değişmeden günceli görür.
- **(Kaldırıldı) Builder** — eski PyQt5 sürümündeki `ComponentBuilder` (widget'ları adım adım kuran sınıf) artık yok; QML'in kendi deklaratif komponent kompozisyonu (`qml/*.qml` dosyaları) bu ihtiyacı karşılıyor.

## Veri/İşlem Akışı (Arka Plan Kaldırma)

1. Kullanıcı `qml/ControlPanel.qml`'deki "Upload Image" butonuna basar veya `qml/ImageViewPanel.qml`'deki `DropArea`'ya dosya bırakır → `Backend.setInputImage(path)` çağrılır.
2. "Remove Background" butonu → `Backend.processImage()`: `ModelManager.get_session(model_name)` ile aktif rembg session alınır.
3. `BackgroundRemoverWorker` (ayrı `QThread`) başlatılır, `ImageProcessor.process()` çağrılır: upscale → `rembg.remove(alpha_matting=True, post_process_mask=True)` → downscale. (Eskiden burada bir `ImageEnhancer.enhance()` adımı vardı — kaldırıldı, bkz [[code-review-2026-09-24]] madde 12.)
4. `finished` sinyali `Backend._on_processing_finished`'a ulaşır: çıktı bytes'ı geçici bir PNG dosyasına yazılır (`tempfile.mkstemp`), `outputImagePath` Property'si güncellenir.
5. QML `Image { source: backend.outputImagePath }` binding'i otomatik olarak yeni görseli gösterir — PyQt5'teki manuel `QPixmap.scaled()`/resize-event yeniden yükleme mantığı artık gerekmiyor (QML `Image` + `PreserveAspectFit` bunu yerleşik olarak yapıyor).
6. Kullanıcı "Save Result" ile `Backend.saveImage(destPath)` çağırır, bellekteki orijinal bytes diske yazılır.
7. Uygulama kapanırken (`aboutToQuit`) `Backend.cleanup()` geçici PNG dosyasını siler.

## Model Yükleme Stratejisi

`Backend.loadModels()` (QML `Component.onCompleted` ile açılışta tetiklenir) → `ModelManager.load_all_models()` **4 modelin tamamını** (`isnet-general-use`, `u2net`, `u2netp`, `silueta`) eş zamanlı olarak belleğe yükler. Bilinçli bir tradeoff (model değiştirme anında olur, başlangıç süresi/bellek artar) — PyQt5 sürümünden değişmedi.

## Bilinen Sınırlamalar / İncelemeler

- Kod inceleme bulguları (PyQt5 dönemi + geçiş sonrası) için bkz [[code-review-2026-09-24]].
- Proje kuralları için bkz [[rules]].

İlgili sayfalar: [[index]], [[rules]], [[code-review-2026-09-24]]
