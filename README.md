# Background Remover AI (PySide6 + QML + rembg)

Modern bir **PySide6 + QML** arayüzü ile, `rembg` modellerini kullanarak görsellerin arka planını kaldıran masaüstü uygulaması.

## Özellikler

- **AI model seçimi**: `isnet-general-use`, `u2net`, `u2netp`, `silueta`
- **Arka planda işleme**: UI donmadan iş parçacığında (QThread) çalışır
- **Alpha matting + mask temizliği**: `rembg`'nin dahili `alpha_matting`/`post_process_mask` özellikleri açık — saç/kürk gibi yumuşak kenarlar sert bir eşiklemeyle değil, gerçek gradyan alfa ile korunur
- **PNG çıktı**: Şeffaf arka planlı sonuç kaydı
- **Küçük görseller için otomatik ölçekleme**: Segmentasyon doğruluğunu artırmak için küçük görseller işlemeden önce büyütülür, sonra orijinal boyuta döndürülür
- **Sürükle-bırak**: Görsel önizleme alanına dosya bırakılarak da yüklenebilir

## Kurulum

### Gereksinimler

- Python 3.9+ (öneri)
- PySide6
- rembg
- Pillow
- numpy
- onnxruntime / onnxruntime-gpu

### Kurulum (pip)

```bash
pip install -r requirements.txt
```

> Not: `rembg` arka planda ONNX kullanır. `onnxruntime` bu yüzden gereklidir.

## Çalıştırma

```bash
python main.py
```

## .exe Paketleme (PyInstaller)

`main.py::resource_path()`, kaynak dosyaları (`qml/`, `icons/`) hem `python main.py` ile hem de dondurulmuş (frozen) bir `.exe` içinden doğru şekilde bulacak şekilde yazıldı (PyInstaller çalışırken `sys._MEIPASS` kullanılır). Build komutu (PySide6'nın QML plugin'lerini de eklemek gerekiyor, yoksa `.exe` QML modüllerini bulamaz):

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "ArkaPlanKaldiriciAI" ^
  --icon icons\app_icon.ico ^
  --add-data "qml;qml" ^
  --add-data "icons;icons" ^
  --add-data ".venv\Lib\site-packages\PySide6\qml;PySide6\qml" ^
  main.py
```

> `--add-data` Windows'ta `KAYNAK;HEDEF` biçiminde (`;`), Linux/macOS'ta `KAYNAK:HEDEF` (`:`) kullanır. `--collect-all PySide6` **kullanmayın** — tüm Qt modüllerini (Qt3D, QtCharts, QtDBus, ...) gereksiz yere paketleyip build'i çok büyütür/yavaşlatır; yukarıdaki hedefli `--add-data` yeterli.

Çıktı `dist/ArkaPlanKaldiriciAI/` klasöründe oluşur (~790 MB, çoğu `onnxruntime`/`scipy`/`numpy` DLL'leri).

## Kurulum Sihirbazı (Inno Setup)

`installer/setup.iss`, PyInstaller çıktısını (`dist/ArkaPlanKaldiriciAI/`) tek bir `.exe` kurulum dosyasına paketler (Türkçe arayüzlü, masaüstü kısayolu opsiyonel, admin gerektirmez). Önce yukarıdaki PyInstaller build'i alınmış olmalı, sonra:

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

Çıktı: `installer/output/ArkaPlanKaldiriciAI_Kurulum.exe`. (Bu klasör `.gitignore`'da — repo'ya commit edilmez, her seferinde yerel olarak üretilir.)

## Proje Mimarisi (OOP + SOLID)

Kod tabanı, sorumlulukları ayıracak şekilde katmanlara bölündü ve genişletilebilir hale getirildi.

- **QML katmanı** (`qml/`): sadece arayüz ve kullanıcı etkileşimi (deklaratif)
- **Backend köprüsü** (`backend/app_backend.py`): Python domain katmanını Qt Property/Signal/Slot ile QML'e bağlar
- **Domain/Service katmanı** (`models/`): görsel işleme ve iyileştirme
- **Model yönetimi** (`models/model_manager.py`): model session'larını yönetir
- **Worker (thread)** (`workers/`): uzun süren işleri arka planda çalıştırır

### Kullanılan Design Pattern'ler

- **Factory + Repository**: `models/model_manager.py` (`ModelManager`)
- **Observer**: `workers/background_remover_worker.py` + `models/model_manager.py` (Qt `Signal`)
- **Facade**: `backend/app_backend.py` (`Backend`) — domain katmanını tek bir QML-uyumlu arayüz arkasında toplar

> Not: Önceki PyQt5 sürümündeki **Builder** pattern (`ComponentBuilder`, widget'ları adım adım kuran sınıf) QML'e geçişle birlikte kaldırıldı; QML'in kendi deklaratif komponent kompozisyonu bu ihtiyacı doğrudan karşılıyor. **Strategy** pattern de (`ImageEnhancer`/`EdgeSharpeningStrategy`, manuel alfa eşikleme) kaldırıldı — `rembg`'nin dahili `alpha_matting` özelliği aynı işi (kenar kalitesini iyileştirme) çok daha doğru yapıyor, elle yazılmış kaba eşikleme koda gerek kalmadı.

## Klasör Yapısı

```
RemoveBG/
├── main.py
├── icons/
│   ├── app_icon.png      # uygulama/pencere ikonu (kaynak)
│   └── app_icon.ico      # Windows .exe ikonu (çok boyutlu)
├── installer/
│   └── setup.iss         # Inno Setup kurulum sihirbazı betiği
├── backend/
│   └── app_backend.py
├── qml/
│   ├── Main.qml
│   ├── ControlPanel.qml
│   ├── ImageViewPanel.qml
│   ├── StyledButton.qml
│   └── icons/            # SVG ikonlar (upload, wand, save, tip, ...)
├── models/
│   ├── model_manager.py
│   ├── image_processor.py
│   └── image_enhancer.py    # ImageResizer (upscale/downscale) — sadece yardımcı, artık strateji içermiyor
├── workers/
│   └── background_remover_worker.py
└── utils/
    ├── constants.py       # renkler, boyutlar, model listesi
    ├── strings.py         # tüm arayüz metinleri (Türkçe)
    └── icons.py           # ikon adı -> SVG yolu eşlemesi
```

## Geliştirme Notları

- **Yeni model ekleme**: `utils/constants.py` içindeki `AVAILABLE_MODELS` listesine ekleyin.
- **Kenar/matting davranışı**: `models/image_processor.py::ImageProcessor.process()` içindeki `remove(...)` çağrısına verilen `alpha_matting`/`post_process_mask`/`alpha_matting_*` parametreleriyle ayarlanır (bkz [rembg dokümantasyonu](https://github.com/danielgatis/rembg)).
- **Merkezi tema/ikon/metin mekanizması**: QML dosyalarında hiçbir renk kodu, SVG yolu veya metin **doğrudan yazılmaz**. Üç modül tek doğruluk kaynağıdır:
  - `utils/constants.py` → `COLORS` (renk paleti) + boyut sabitleri
  - `utils/icons.py` → ikon adı → `qml/icons/*.svg` yolu eşlemesi
  - `utils/strings.py` → tüm arayüz metinleri (Türkçe)

  `backend/app_backend.py` bu üçünü `colorPrimary`, `iconUpload`, `stringButtonUpload` gibi Qt Property'ler olarak QML'e sunar; `qml/*.qml` dosyaları yalnızca bu property'lere bağlanır. Yeni bir renk/ikon/metin eklemek istediğinizde ilgili Python modülüne ekleyip `Backend`'e bir Property olarak eklemeniz yeterli — QML dosyalarına dokunmadan tüm arayüzde tutarlı kalır.
- **Emoji kullanılmaz**: Arayüzdeki tüm ikonlar `qml/icons/` altındaki SVG dosyalarıdır (gerektiğinde `Qt5Compat.GraphicalEffects.ColorOverlay` ile temaya göre renklendirilir), durum mesajları ve buton etiketleri düz metindir.
