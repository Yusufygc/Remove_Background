# Background Remover AI (PyQt5 + rembg)

Modern bir **PyQt5** arayüzü ile, `rembg` modellerini kullanarak görsellerin arka planını kaldıran masaüstü uygulaması.

## Özellikler

- **AI model seçimi**: `isnet-general-use`, `u2net`, `u2netp`, `silueta`
- **Arka planda işleme**: UI donmadan iş parçacığında (QThread) çalışır
- **PNG çıktı**: Şeffaf arka planlı sonuç kaydı
- **Küçük görseller için otomatik iyileştirme**: İşlem kalitesini artırmak için ölçekleme + kenar iyileştirme

## Kurulum

### Gereksinimler

- Python 3.9+ (öneri)
- PyQt5
- rembg
- Pillow
- numpy
- (Opsiyonel) onnxruntime / onnxruntime-gpu

### Kurulum (pip)

```bash
pip install pyqt5 rembg pillow numpy
```

> Not: `rembg` arka planda ONNX kullanır. Bazı ortamlarda `onnxruntime` ayrıca gerekebilir.

## Çalıştırma

`RemoveBG` klasöründe:

```bash
python main.py
```

## Proje Mimarisi (OOP + SOLID)

Kod tabanı, sorumlulukları ayıracak şekilde katmanlara bölündü ve genişletilebilir hale getirildi.

- **UI katmanı**: sadece arayüz ve kullanıcı etkileşimi
- **Domain/Service katmanı**: görsel işleme ve iyileştirme
- **Model yönetimi**: model session’larını yönetir
- **Worker (thread)**: uzun süren işleri arka planda çalıştırır

### Kullanılan Design Pattern’ler

- **Factory + Repository**: `models/model_manager.py` (`ModelManager`)
- **Strategy**: `models/image_enhancer.py` (`ImageEnhancer` + stratejiler)
- **Builder**: `ui/components.py` (`ComponentBuilder`)
- **Observer**: `workers/background_remover_worker.py` (Qt `pyqtSignal`)

## Klasör Yapısı

```
RemoveBG/
├── main.py
├── models/
│   ├── model_manager.py
│   ├── image_processor.py
│   └── image_enhancer.py
├── ui/
│   ├── main_window.py
│   ├── styles.py
│   └── components.py
├── workers/
│   └── background_remover_worker.py
└── utils/
    └── constants.py
```

## Geliştirme Notları

- **Yeni model ekleme**: `utils/constants.py` içindeki `AVAILABLE_MODELS` listesine ekleyin.
- **Yeni iyileştirme algoritması**: `ImageEnhancementStrategy` implement edip `ImageEnhancer` içine strategy olarak verin.
- **UI tema/stil**: `ui/styles.py` üzerinden yönetilir.

## Eski Kod

Eski tek dosyalı sürüm (referans amaçlı) korunmuştur:

- `modern_pyqt_claudeApp.py`

