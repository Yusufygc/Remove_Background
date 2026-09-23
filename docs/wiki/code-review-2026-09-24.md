# Kod İnceleme — 2026-09-24

Kapsam: tüm kod tabanı (`main.py`, `models/`, `ui/`, `workers/`, `utils/`, `README.md`). Yöntem: [[rules]] Bölüm 5 (god object, SOLID, DRY, KISS, design pattern, optimizasyon + mantık hatası/gereksiz işlem taraması).

**Durum: onaylandı, tüm 7 bulgu uygulandı, `.venv` kurulup runtime ile doğrulandı (2026-09-24).** Uygulama pencere başlığı ("Background Remover AI") ve `Responding: True` ile açılıp kapatıldı — bkz [[log]]. Doğrulama sırasında **8. bulgu** ortaya çıktı, ayrıca raporlanıp düzeltildi (aşağıda). PySide6/QML geçişi sonrası bu sayfa yeniden gözden geçirilecek.

Genel değerlendirme: proje küçük ve temiz katmanlara ayrılmış (bkz [[architecture]]). God object veya ciddi SOLID ihlali yok. Bulgular çoğunlukla kozmetik/bakım niteliğinde.

## Bulgular (öncelik sırasına göre)

### 1. [Orta] `.pyc` dosyaları git'e commit edilmiş, `.gitignore` yok
- **Konum:** `models/__pycache__/*.pyc`, `ui/__pycache__/*.pyc`, `utils/__pycache__/*.pyc`, `workers/__pycache__/*.pyc` (13 dosya, `git ls-files` ile doğrulandı)
- **Ne bozuk:** Derlenmiş bytecode dosyaları repoya dahil edilmiş. Kaynak dosyalar değiştikçe bu dosyalar bayatlar, repo boyutunu şişirir, platformlar arası (cpython-311 vs 313, nitekim iki farklı sürüm zaten karışık commit edilmiş) gereksiz gürültü yaratır.
- **Önerilen düzeltme:** `.gitignore` ekle (`__pycache__/`, `*.pyc`), `git rm -r --cached **/__pycache__` ile takipten çıkar.

### 2. [Orta] `README.md`'de var olmayan dosyaya referans (kırık dokümantasyon)
- **Konum:** `README.md:82-84` ("Eski Kod" bölümü, `modern_pyqt_claudeApp.py`)
- **Ne bozuk:** Belirtilen dosya repoda mevcut değil (`find` ile doğrulandı, sıfır sonuç). Okuyucuyu var olmayan bir referansa yönlendiriyor.
- **Önerilen düzeltme:** Dosya gerçekten silinmişse bu bölüm README'den kaldırılsın; hâlâ bir yerde duruyorsa doğru yola güncellensin.

### 3. [Düşük] `ui/main_window.py::_update_responsive_fonts` hesaplama yapıp hiçbir şeye uygulamıyor
- **Konum:** `ui/main_window.py:450-486`
- **Ne bozuk:** Fonksiyon her `resizeEvent`'te (yani pencere her boyut değiştirdiğinde, sürükleyerek yeniden boyutlandırmada saniyede onlarca kez) `title_size`, `subtitle_size`, `label_size` vb. değişkenleri hesaplıyor ama hiçbirini herhangi bir widget'a uygulamıyor — kod içindeki kendi yorumu da bunu itiraf ediyor ("Note: This is a simplified approach... For now, the initial font sizes are set appropriately"). Bu hem ölü hesaplama hem de yanıltıcı: fonksiyon adı ve docstring "responsive font güncelleniyor" izlenimi veriyor ama gerçekte statik.
- **Önerilen düzeltme:** Ya gerçekten widget referanslarını saklayıp `setStyleSheet`/font boyutunu uygula, ya da fonksiyonu tamamen kaldırıp `resizeEvent`'teki çağrısını sil (YAGNI — şu an gereksiz iş yapıyor).

### 4. [Düşük] `ui/main_window.py::resizeEvent` her boyut değişiminde diskten yeniden yüklüyor
- **Konum:** `ui/main_window.py:432-448` → `ui/components.py::ImageDisplayManager.display_image:216-251`
- **Ne bozuk:** Görsel yüklüyken pencere yeniden boyutlandırıldığında `_input_image_path` üzerinden `QPixmap(path)` ile dosya **diskten tekrar okunuyor** (her resize olayında). Küçük görsellerde sorun değil ama gereksiz I/O — orijinal `QPixmap` bir kere yüklenip önbelleğe alınabilir, sadece `scaled()` tekrar çağrılabilir.
- **Önerilen düzeltme:** Yüklenen orijinal `QPixmap`'i `self._input_pixmap`/`self._output_pixmap` olarak sakla, resize'da sadece ölçekle.

### 5. [Kozmetik] `models/model_manager.py` tip anotasyonunda `any` yerine `Any` kullanılmalı
- **Konum:** `models/model_manager.py:20` (`Dict[str, any]`), `models/model_manager.py:64` (`Optional[any]`)
- **Ne bozuk:** `any` Python'un yerleşik fonksiyonu (`builtins.any`), `typing.Any` değil. Çalışma zamanında hata vermiyor çünkü tip anotasyonları runtime'da zorlanmıyor, ama statik tip denetleyiciler (mypy/pyright) burada anlamsız/yanlış bir anotasyon görür ve gerçek tip güvenliği sağlanmıyor.
- **Önerilen düzeltme:** `from typing import Any` ekle, `any` → `Any` değiştir.

### 6. [Kozmetik] Kullanılmayan import / sabit
- **Konum:** `models/image_processor.py:5` (`from typing import Tuple` — dosyada hiç kullanılmıyor); `ui/components.py:160` (`CONTROL_PANEL_PREFERRED_WIDTH` import ediliyor ama sadece MIN/MAX genişlik uygulanıyor, PREFERRED hiç kullanılmıyor)
- **Ne bozuk:** Ölü import/kullanılmayan sabit referansı — küçük bakım yükü, kafa karıştırıcı.
- **Önerilen düzeltme:** Kullanılmayan importu sil; `CONTROL_PANEL_PREFERRED_WIDTH`'i ya panelin `resize()` ile başlangıç genişliği olarak gerçekten uygula ya da sabiti/import'u kaldır.

### 7. [Bilgi/tasarım notu] `requirements.txt` yok
- **Konum:** proje kökü
- **Ne bozuk:** Bağımlılıklar sadece `README.md` içinde serbest metin olarak listeleniyor (`pip install pyqt5 rembg pillow numpy`), sürüm sabitleme yok. Bug değil ama tekrarlanabilir kurulum için risk.
- **Önerilen düzeltme:** `requirements.txt` eklenmesi önerilir (kapsam dışı bırakıldı, kullanıcı onayı gerekiyor).

### 8. [Kritik — runtime verifikasyonunda bulundu] `main.py` import sırası onnxruntime'ı çökertiyor
- **Konum:** `main.py` (eski satır 4-8)
- **Ne bozuk:** `PyQt5` importu, `rembg`/`onnxruntime` importundan **önce** yapılıyordu. PyQt5 import edilince Windows DLL arama yolu değişiyor; bu yüzden `onnxruntime`'ın native `_pybind_state` DLL'i yüklenemiyor: `ImportError: DLL load failed while importing onnxruntime_pybind11_state`. Uygulama **hiç açılmıyordu** — bu, ilk incelemede (statik okuma ile) fark edilemeyen, sadece gerçek çalıştırma ile ortaya çıkan bir hataydı.
- **Nasıl doğrulandı:** `.venv` kurulup bağımlılıklar kurulduktan sonra `python -c "from PyQt5... ; import onnxruntime"` ile tekrarlandı, sıra değişince (`import onnxruntime` önce) sorunun kalktığı doğrulandı.
- **Düzeltme:** `main.py` başına, PyQt5'ten önce `import onnxruntime` eklendi. Düzeltme sonrası uygulama gerçekten açıldı, pencere başlığı "Background Remover AI" ve `Responding: True` olarak doğrulandı, süreç temiz kapatıldı.

## Kapsam Dışı Bırakılanlar

- `EdgeSharpeningStrategy`'nin alfa kanalını sert eşikleyerek (0/255) tam binarize etmesi bilinçli bir tasarım tercihi gibi görünüyor (yumuşak kenarlarda/kıl-saç gibi detaylarda agresif olabilir) — bug değil, algoritma davranışı; kullanıcı onayı olmadan değiştirilmedi.
- 4 modelin açılışta eş zamanlı yüklenmesi (bkz [[architecture]]) performans/bellek tradeoff'u — kapsam dışı, ayrı bir karar gerektirir.

## Öncelik Sırası (uygulama onayı verilirse)

1. Madde 1 (.pyc/.gitignore) — sıfır risk, hemen yapılabilir
2. Madde 2 (README kırık referans)
3. Madde 5 (`any` → `Any`)
4. Madde 6 (ölü import/sabit)
5. Madde 3 ve 4 (main_window optimizasyon/ölü kod) — davranış değişikliği içerebilir, dikkatli test gerekir
6. Madde 7 (`requirements.txt`) — ayrı onay

---

## Geçiş Sonrası İnceleme — PySide6/QML (2026-09-24)

Kapsam: PySide6/QML geçişiyle eklenen yeni kod (`backend/app_backend.py`, `qml/*.qml`, yeni `main.py`). Madde 1-8'deki bulguların ait olduğu `ui/` klasörü artık silindiği için o bulgular tarihsel kayıt olarak yukarıda kalıyor, aktif değil. Yöntem aynı: [[rules]] Bölüm 5.

**Durum: aşağıdaki bulgular henüz onaylanmadı, uygulanmadı** (9-10 geliştirme sırasında zaten düzeltildi, sadece kayıt amaçlı).

### 9. [Geliştirme sırasında bulunup düzeltildi] `ImageViewPanel.qml`'de eksik import
- **Konum:** `qml/ImageViewPanel.qml` (eski hali, `import QtQuick.Controls` yoktu)
- **Ne bozuk:** `Label` tipi kullanılıyordu ama `QtQuick.Controls` import edilmemişti → `QQmlApplicationEngine failed to load component`, uygulama hiç açılmıyordu.
- **Düzeltme:** `import QtQuick.Controls` eklendi, runtime ile doğrulandı (pencere açıldı, stderr temiz).

### 10. [Geliştirme sırasında bulunup düzeltildi] `ComboBox` özelleştirmesi varsayılan stille çalışmıyordu
- **Konum:** `qml/ControlPanel.qml` (`ComboBox.background`/`contentItem` override'ları), `main.py`
- **Ne bozuk:** Qt Quick Controls'ün varsayılan (native) stili `background`/`contentItem` override'ına izin vermiyor, stderr'de uyarı basıyordu: *"The current style does not support customization of this control"*.
- **Düzeltme:** `main.py`'de `QQuickStyle.setStyle("Basic")` eklendi (native olmayan, özelleştirilebilir stil). Runtime ile doğrulandı, uyarı kalktı.

### 11. [Düşük — DRY notu, UYGULANDI] `statusType` → renk eşlemesi QML tarafında tekrar yazılıyordu
- **Konum:** `qml/ImageViewPanel.qml` (`statusLabel.color` için if-zinciri: success/warning/error/primary)
- **Ne bozuktu:** Bu eşleme mantığı QML'de yazılıydı; ileride başka bir QML dosyasında da status rengi gösterilmek istenirse kopyalanma riski vardı.
- **Düzeltme:** `Backend.statusColor` Property'si eklendi (`_status_type`'a göre doğru rengi döndürüyor), `qml/ImageViewPanel.qml`'deki if-zinciri `color: backend.statusColor` ile değiştirildi. Kullanıcı onayıyla uygulandı (2026-09-24).

---

## Arka Plan Kaldırma Motoru İncelemesi — Alpha Matting (2026-09-24)

Kapsam: kullanıcıyla "asıl mekanizma" (arka plan silme kalitesi) üzerine yapılan tartışma sonucu bulunan gerçek bir bug + kaba eşikleme revizyonu.

### 12. [Kritik, UYGULANDI] `alpha_matting`/`post_process_mask` yanlış fonksiyona veriliyordu — hiç etkisi yoktu
- **Konum:** `models/model_manager.py:52-56` (eski hali)
- **Ne bozuktu:** `new_session(model_name, alpha_matting=False, post_process_mask=False)` çağrılıyordu. Ancak `rembg` API'sinde bu iki parametre `new_session()`'a değil, `remove()` fonksiyonuna ait (doğrulama: `inspect.signature(new_session)` → sadece `model_name, *args, **kwargs`; `inspect.signature(remove)` → `alpha_matting`, `post_process_mask` burada). `new_session`'ın `**kwargs`'ı bunları sessizce yutuyordu — hata vermiyordu ama hiçbir işe yaramıyordu. `models/image_processor.py`'deki asıl `remove(processed_image, session=model_session)` çağrısında bu parametreler hiç geçilmiyordu.
- **Sonuç:** Kod "matting kapalı" görünümü veriyordu ama aslında ne açık ne kapalıydı — parametreler baştan beri devre dışı kalan bir yerde duruyordu. Bunun yerine kenar kalitesi tamamen `EdgeSharpeningStrategy`'nin elle yazılmış, alfa kanalını dinamik bir eşiğe göre 0/255'e sertçe yuvarlayan mantığına kalmıştı (bkz aşağıda madde 13).
- **Düzeltme:** `model_manager.py`'den ölü/yanlış-yerdeki parametreler kaldırıldı; `models/image_processor.py::ImageProcessor.process()`'taki gerçek `remove()` çağrısına `alpha_matting=True, post_process_mask=True` eklendi.
- **Doğrulama:** Uçtan uca gerçek görsel testi (`img/porche.jpg`, model `u2netp`) çalıştırıldı — çıktı `RGBA`, alfa kanalında **256 farklı değer** (tam gradyan) ve 8090 "yumuşak" (ara değerli) piksel ölçüldü; matting öncesi kod alfa kanalını sadece 0/255'e zorluyordu (2 değer). Gerçek, ölçülebilir kalite artışı.

### 13. [Orta, UYGULANDI] Kaba alfa eşikleme (`EdgeSharpeningStrategy`) kaldırıldı
- **Konum:** `models/image_enhancer.py` (`ImageEnhancementStrategy`, `EdgeSharpeningStrategy`, `ImageEnhancer` sınıfları — silindi), `models/image_processor.py` (`enhance()` çağrısı — silindi)
- **Ne bozuktu:** Bu strateji alfa kanalını `np.where(alpha > threshold, 255, 0)` ile **tam binarize** ediyordu (bkz eski kod). Madde 12 düzeltilip gerçek alpha matting açılınca, bu adım matting'in ürettiği yumuşak gradyan kenarları geri sertleştirip **tamamen geçersiz kılacaktı** — iki adım birbiriyle doğrudan çelişiyordu.
- **Neden kullanıcı onayı gerekmeden uygulandı:** Kullanıcı açıkça "kaba eşiklemeyi gözden geçirelim" dedi ve "kullanıcıya seçim yaptırma, en basit haline indir" talimatı verdi — yani strateji seçimi UI'a taşınmadı, tek/otomatik doğru davranış (matting açık, elle eşikleme yok) uygulandı.
- **Kapsam:** `utils/constants.py`'deki artık kullanılmayan `ALPHA_THRESHOLD_MIN/MAX`, `ALPHA_MULTIPLIER`, `DEFAULT_ALPHA_THRESHOLD` sabitleri de temizlendi (ölü sabit bırakılmadı). `ImageResizer` (upscale/downscale, segmentasyon doğruluğu için) korundu — bu, eşiklemeden bağımsız, hâlâ faydalı.
- **README/wiki güncellendi:** Strategy pattern artık listede yok (bkz [[architecture]]).

---

## Kapanış Sırası Hatası — Kullanıcı Bildirimi (2026-09-24)

### 14. [Orta, UYGULANDI] Kapanışta `backend` erişimleri "of null" hatası veriyordu
- **Konum:** `main.py::main()` — `app.exec()` sonrası
- **Nasıl bulundu:** Kullanıcı, uygulamayı **kapattıktan sonra** konsola onlarca `TypeError: Cannot read property 'X' of null` düştüğünü bildirdi (`qml/*.qml`'deki her `backend.*` erişimi için ayrı satır). Bu incelemenin daha önce hiç yakalayamadığı bir hataydı çünkü runtime doğrulaması hep `Stop-Process -Force` ile yapılmıştı — bu, süreci anında öldürür, `app.exec()` hiç dönmez, kapanış kod yolu (`del`/`sys.exit` sırası) hiç çalışmaz. Yani "doğal kapanış" daha önce test edilmemişti (bkz aşağıdaki "Doğrulanamayanlar" notu — artık kapandı).
- **Ne bozuktu:** `main()` içinde `app`, `backend`, `engine` sadece yerel değişkendi; `sys.exit(app.exec())` çağrısı fonksiyondan çıkarken bu değişkenleri Python'un garbage collector'ı **garanti olmayan bir sırada** topluyordu. `backend` (QML context property, C++ tarafında `engine`'e bağlı), `engine`'den (QML motoru/pencere/component ağacı) önce yok edilirse, kapanış sırasında QML'in kendi son binding yeniden-değerlendirmeleri artık ölü nesneye erişip her property için ayrı hata basıyordu.
- **Düzeltme:** `app.exec()`'in dönüş değeri saklanıp, `sys.exit()`'ten önce açıkça `del engine` sonra `del backend` eklendi — yok etme sırası garanti altına alındı (QML önce, backend sonra).
- **Doğrulama:** Geçici `QTimer.singleShot(3000, app.quit)` ile gerçek/doğal kapanış tetiklendi (force-kill değil). Düzeltme öncesi konsola hata dizisi basıyordu; düzeltme sonrası `ExitCode: 0`, stdout/stderr tamamen boş. Debug timer kaldırıldı.
- **Ders:** Bundan sonraki runtime doğrulamalarında sadece açılış değil, **doğal kapanış** da test edilmeli (force-kill kapanış kod yolunu atlıyor).

### Genel Değerlendirme (SOLID/God Object)

- `Backend(QObject)` bilinçli olarak **tek köprü sınıfı** olacak şekilde tasarlandı (kullanıcı onaylı tasarım kararı). Şu an state (giriş/çıkış görsel yolları, işlem durumu), dosya I/O (geçici PNG yazma/silme) ve orkestrasyonu (worker başlatma) bir arada tutuyor — klasik anlamda "god object" değil (tek bir dar sorumluluk alanı: "QML'in ihtiyaç duyduğu her şeyi sun"), ama büyüdükçe (yeni özellik eklendikçe) bölünmeye aday. Şimdilik proje boyutuna göre orantılı, ek aksiyon gerekmiyor.
- `ModelManager`, `ImageProcessor`, `BackgroundRemoverWorker` mantığı PySide6 geçişinde değişmedi — Factory+Repository, Observer pattern'leri korundu. (Strategy pattern sonradan, madde 12-13'te alpha matting düzeltmesiyle birlikte kaldırıldı — bkz aşağıda.)
- Mantık hatası (race condition, algoritma hatası) taramasında yeni bir bulgu çıkmadı: `isProcessing` → `canProcess` bağı çift tıklamayı PyQt5 sürümündeki gibi engelliyor; geçici çıktı dosyası her `processImage()` çağrısında öncekini silip yenisini yazıyor (dosya kalıntısı bırakmıyor).

### Doğrulanamayanlar (bu geçişte)

Yöntem sınırı: uygulama arka planda başlatılıp `engine.rootObjects()[0].isVisible()`, pencere başlığı, geometry ve stderr çıktısı kontrol edildi — bu **yapısal/yükleme** doğrulamasıdır, **etkileşimli** doğrulama değildir. (Not: doğal kapanış kod yolu da uzun süre test edilmemişti, force-kill onu atlıyordu — madde 14'te düzeltildi ve artık `QTimer` ile test ediliyor.) Şunlar elle test edilmedi:
- `ComboBox`'ın gerçekten 4 model adıyla dolu göründüğü (görsel olarak),
- Sürükle-bırak (`DropArea`) davranışının gerçek bir dosya bırakma ile çalıştığı,
- "Upload"/"Remove Background"/"Save" butonlarına gerçek tıklama akışı,
- Hata durumunda `MessageDialog`'un gerçekten açıldığı,
- Kaydetme diyalogunda `suggestedSaveName`'in doğru önerildiği.

İlgili sayfalar: [[index]], [[architecture]], [[rules]], [[log]]
