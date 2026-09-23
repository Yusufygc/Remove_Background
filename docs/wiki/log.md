# Kayıt Defteri

## [2026-09-24] [INGEST] | .exe paketleme hazırlığı: path düzeltmesi + uygulama ikonu
Kullanıcı isteği: uygulamayı PyInstaller ile `.exe`'ye çevirmeye hazırla, projeye uygun bir ikon bul.

- `main.py`'ye `resource_path(*parts)` yardımcı fonksiyonu eklendi: `sys.frozen`/`sys._MEIPASS` kontrolü ile hem `python main.py` hem donmuş `.exe` içinde doğru taban dizini bulur. `qml_path` bunu kullanacak şekilde güncellendi.
- İkon: proje bağlamına (AI destekli fotoğraf arka planı kaldırma) uygun bir "fotoğraf çerçevesi + dağ silüeti + AI sparkle" ikonu, mevcut tema rengiyle (`#0e8a99` petrol teal + beyaz) PIL ile çizildi (harici asset/kütüphane yok, tamamen kod ile üretildi). Önce taslak PNG üretilip Read tool ile görsel olarak kontrol edildi, sonra onaylanan tasarım `icons/app_icon.png` (512×512 kaynak) ve `icons/app_icon.ico` (16-256px çok boyutlu, Windows exe ikonu) olarak kaydedildi.
- `main.py`'de `app.setWindowIcon(QIcon(resource_path("icons", "app_icon.ico")))` eklendi — pencere/taskbar ikonu artık ayarlanıyor (önceki QML `ApplicationWindow.icon` denemesi bu Qt sürümünde başarısız olmuştu, bkz [[code-review-2026-09-24]]; bu sefer Python tarafında `QGuiApplication.setWindowIcon` ile yapıldı, çalıştı).
- `.gitignore`'a `build/`, `dist/`, `*.spec` eklendi (gelecekteki PyInstaller çıktıları için).
- `README.md`'ye PyInstaller build komutu örneği eklendi (`--add-data`, `--icon`). **`pyinstaller` henüz kurulmadı, build alınmadı** — sadece hazırlık yapıldı, kullanıcı istemedikçe kurulum/build çalıştırılmadı.

**Önemli:** Kullanıcı ikonu kendisi inceleyecek ("ben kontrol ederim sonra iconu") — henüz onaylanmadı, değiştirilebilir.

Doğrulama: `QIcon(...).isNull()` → `False`, `availableSizes()` 7 boyut listeledi. Uygulama hem açılışta hem doğal kapanışta hatasız (stderr boş).

## [2026-09-24] [REVIEW] | Devre dışı buton kontrastı düzeltildi
Kullanıcı bildirdi: boşta beklerken (görsel yüklenmeden) "Arka Planı Kaldır" ve "Sonucu Kaydet" butonları arka planla neredeyse aynı renkte, okunmuyordu. Kök neden: `qml/StyledButton.qml` devre dışı durumda `backend.colorSurfaceLight` (`#e7edef`) dolgu + `opacity: 0.6` kullanıyordu — açık temada bu, panel/sayfa arka planına (`#ffffff`/`#f3f6f7`/`#dbe4e6`) neredeyse eşit bir tona düşüyordu; üstüne beyaz ikon da soluk zeminde kayboluyordu.

**Düzeltme:** Devre dışı dolgu `backend.colorBorder` (`#c7d3d6`, belirgin şekilde daha gri) yapıldı, global `opacity` dimming kaldırıldı, `border.width: 1 / border.color: colorTextSecondary` eklendi (şekil her zaman belirgin). İkon artık `ColorOverlay` ile etkin durumda beyaz (`colorOnAccent`), devre dışı durumda `colorTextSecondary` (koyu gri) olarak boyanıyor — önceden sabit beyazdı, açık gri zeminde görünmüyordu.

Doğrulama: uygulama hatasız açıldı (stderr temiz, `engine.warnings` ile de doğrulandı). **Görsel kontrast doğrulaması yapılamadı** (ekran görüntüsü alınamıyor bu ortamda).

## [2026-09-24] [LINT] | Commit kuralı kesinleştirildi: Co-Authored-By asla eklenmez
Kullanıcı, `8382ab1` commit'inde `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` satırının eklenmiş olmasına itiraz etti ve bunun **hiçbir istisna olmadan** eklenmemesini istedi. `docs/wiki/rules.md` Bölüm 6 güncellendi: önceki "aktif oturum talimatı üstün sayılır" istisnası kaldırıldı, kural mutlak hale getirildi. Zaten push edilmiş `8382ab1` commit'inin düzeltilmesi (`amend` + `push --force`) ayrıca ele alınıyor — bkz kullanıcı onayı.

## [2026-09-24] [INGEST] | Koyu temadan açık/beyaz temaya geçildi
Kullanıcı isteği: arka plan beyaz tonlarından olsun. Düz bir "background beyaz olsun" değişikliği yetmezdi — koyu temadaki `primary`/`success`/`warning`/`error`/`accent` renkleri, koyu zemin üstünde okunacak şekilde tasarlanmıştı; aynı değerler beyaz zemine taşınsa metin/ikon rengi olarak kullanıldıkları yerlerde (durum metni, ipuçları başlığı/ikonu) kontrast neredeyse kaybolurdu. Bu yüzden `utils/constants.py::COLORS` tam bir açık tema seti olarak yeniden tanımlandı: `background` `#f3f6f7` (hafif petrol-gri beyaz), `surface` `#ffffff`, `text` `#132226` (koyu petrol-siyah), `border`/`text_secondary` açık-orta gri; `primary`/`success`/`warning`/`error`/`accent` aynı ton ailesinde ama **koyulaştırılmış** hallerine çekildi (`#17c3d4`→`#0e8a99` vb.) — böylece hem buton zemini hem de düz metin/ikon rengi olarak beyazda okunaklı kalıyorlar. Gölge alfa değerleri de (`button_shadow`/`panel_shadow`) koyu temadaki sert siyah gölgeden (0.31/0.47) açık temaya uygun yumuşak gölgeye (0.18/0.12) çekildi.

Yeni bir tasarım sorunu ortaya çıktı: butonların (`StyledButton.qml`) etiket rengi `backend.colorText` kullanıyordu — bu artık koyu (gövde metni için doğru) ama renkli buton zeminlerinin üstünde beyaz yazı gerekiyor. Çözüm: `COLORS['on_accent'] = '#ffffff'` eklendi, `Backend.colorOnAccent` Property'si oluşturuldu, `StyledButton.qml`'de etkin buton etiketi `colorText` yerine `colorOnAccent`'a bağlandı — gövde metni (tema moduna göre otomatik uyarlanan `colorText`) ile buton-üstü metin (her zaman beyaz kalan `colorOnAccent`) ayrıştırıldı.

Doğrulama: `python -m py_compile`; hem açılış (force-kill ile) hem **doğal kapanış** (geçici `QTimer` ile, madde 14'teki ders uygulanarak) test edildi — ikisi de temiz (`HasExited: False` / `ExitCode: 0`, stderr boş). **Görsel doğrulama yapılamadı** (bu ortamda ekran görüntüsü alınamıyor).

## [2026-09-24] [REVIEW] | Kapanışta konsola düşen "Cannot read property of null" hataları düzeltildi
Kullanıcı bildirdi: uygulama çalışırken sorun yok ama **pencere kapatıldıktan sonra** konsola onlarca `TypeError: Cannot read property 'X' of null` düşüyordu (tüm `backend.*` erişimleri). Kök neden: `main.py::main()`'da `app.exec()` dönünce fonksiyon `sys.exit()` ile çıkarken Python yerel değişkenleri (`app`, `backend`, `engine`) garbage-collect ediyordu — sıra garanti değildi. `backend` (QML'e context property olarak verilen QObject), QML motoru (`engine`, dolayısıyla pencere/component ağacı) hâlâ ayaktayken önce silinirse, kapanış sırasında QML'in kendi son binding yeniden-değerlendirmeleri artık ölü olan C++ nesnesine erişip her property için ayrı bir hata basıyordu.

**Düzeltme:** `app.exec()` sonrası, `sys.exit()`'ten önce açıkça `del engine` sonra `del backend` eklendi — QML motoru backend'den önce yok ediliyor, garanti sıra.

**Doğrulama:** Force-kill ile test bu hatayı hiç tetiklemiyordu (süreç anında öldürülüyor, `app.exec()` hiç dönmüyor) — bu yüzden önceki testlerde fark edilmemişti. Geçici bir `QTimer.singleShot(3000, app.quit)` ile **doğal** kapanış tetiklendi: düzeltme öncesi konsola hata basıyordu, düzeltme sonrası `ExitCode: 0`, stdout/stderr tamamen boş. Debug timer kaldırıldı.

## [2026-09-24] [LINT] | İpuçları fontu büyütüldü/beyazlatıldı, tema renkleri canlılaştırıldı
Kullanıcı isteği: `qml/ControlPanel.qml` ipuçları başlığı 12→14px, metni 10→13px büyütüldü; metin rengi `colorTextSecondary` (soluk gri-mavi) yerine `colorText` (parlak beyaz) yapıldı. `utils/constants.py::COLORS` — `primary`/`success`/`warning`/`error`/`accent` daha canlı/parlak tonlara çekildi (`#1596a9`→`#17c3d4`, `#22b378`→`#22e0a0`, `#d99a44`→`#ffb443`, `#d9534f`→`#ff5c5c`, `#3a6ea5`→`#2f8fe6`); `background`/`surface`/`text` aynı kaldı (koyu tema kimliği korunuyor). Tek dosya değişti, `backend`/`qml` otomatik yansıdı. Doğrulama: derleme + hatasız açılış; görsel doğrulama yine yapılamadı (ekran görüntüsü alınamıyor bu ortamda).

## [2026-09-24] [INGEST] | Tema renk paleti değiştirildi (kaynak: ui/thema/*.jpg)
Kullanıcı `ui/thema/` klasörüne 5 referans görsel ekledi (koyu petrol-teal ve lacivert dokulu duvar kağıtları/deri/kumaş dokuları). PIL `quantize` ile her görselden baskın renkler örneklendi (bkz commit/log detayı: `#033644-#094352` petrol teal, `#071819-#1f4842` koyu teal-yeşil, `#113058-#184b80` lacivert, `#3f6585-#5f8cae` çelik mavi). Ortak tema: neredeyse siyah zeminler + petrol/teal/lacivert orta tonlar — eski mor/indigo (`#6366f1`/`#8b5cf6`) paletiyle uyuşmuyordu.

`utils/constants.py::COLORS` **tek dosyada** güncellendi (merkezi tema mekanizması sayesinde — bkz [[architecture]] madde "Facade"): `primary` petrol teal `#1596a9`, `accent` lacivert `#3a6ea5`, `background`/`surface`/`surface_light`/`surface_dark` görsellerden örneklenen koyu petrol tonları, `success`/`warning`/`error` yeni palete göre hafifçe ayarlandı (kontrast/anlam için). Başka hiçbir dosyaya dokunulmadı — `backend/app_backend.py` Property'leri ve `qml/*.qml` binding'leri otomatik yeni renkleri kullanıyor.

Doğrulama: `python -m py_compile`, uygulama hatasız açıldı (`HasExited: False`, stderr temiz). **Görsel/piksel doğrulama yapılamadı** — bu ortamda pencere ekran görüntüsü alınamıyor (window station izolasyonu, `EnumWindows`/ekran yakalama pencereyi bulamıyor, önceki oturumlarda da aynı kısıt görüldü). Renklerin gerçekte nasıl göründüğü kullanıcı tarafından elle kontrol edilmeli.

## [2026-09-24] [REVIEW] | Alpha matting açıldı, kaba eşikleme kaldırıldı
Kullanıcıyla "asıl mekanizma" (arka plan silme kalitesi) üzerine yapılan tartışma sonucu gerçek bir bug bulundu: `models/model_manager.py`'de `new_session(model_name, alpha_matting=False, post_process_mask=False)` çağrılıyordu ama bu parametreler `rembg` API'sinde `new_session()`'a değil `remove()`'a ait — `new_session`'ın `**kwargs`'ı sessizce yutuyordu, hiçbir etkisi yoktu (`inspect.signature` ile doğrulandı). Düzeltme: parametreler `models/image_processor.py`'deki gerçek `remove()` çağrısına taşındı ve `True` yapıldı.

Bunun doğal sonucu olarak `models/image_enhancer.py`'deki `EdgeSharpeningStrategy` (alfa kanalını 0/255'e sert eşikleyen elle yazılmış Strategy) **kaldırıldı** — artık gerçek matting'in ürettiği yumuşak gradyan kenarları geri bozacaktı. Kullanıcı talimatı: "kullanıcıya seçim yaptırma, en basit haline indir" — yani strateji seçimi UI'a taşınmadı, tek otomatik doğru davranış uygulandı. `ImageResizer` (upscale/downscale) korundu, `utils/constants.py`'deki artık kullanılmayan eşik sabitleri temizlendi.

Doğrulama: gerçek görsel (`img/porche.jpg`, model `u2netp`) uçtan uca işlendi — çıktı alfa kanalında 256 farklı değer (tam gradyan), 8090 yumuşak-kenar pikseli ölçüldü (öncesinde sadece 0/255, 2 değer). Ayrıntı: [[code-review-2026-09-24]] madde 12-13, [[architecture]] güncellendi.

## [2026-09-24] [INGEST] | Arayüz Türkçeleştirildi, merkezi tema/ikon/string mekanizması kuruldu
Kullanıcı talebiyle: (1) tüm arayüz metinleri Türkçe'ye çevrildi (Türkçe karakterlere dikkat edilerek — ı, ğ, ü, ş, ö, ç, İ), (2) `statusType`→renk eşlemesi `Backend.statusColor`'a taşındı (bkz [[code-review-2026-09-24]] madde 11 — uygulandı), (3) merkezi tema/ikon/string mekanizması kuruldu ve emoji tamamen kaldırıldı:
- `utils/strings.py` (yeni) — tüm arayüz metinleri tek dosyada.
- `utils/icons.py` (yeni) — ikon adı → `qml/icons/*.svg` yolu eşlemesi.
- `qml/icons/*.svg` (yeni, 7 dosya) — emoji yerine geçen basit çizgi ikonlar (palette, upload, wand, save, tip, image, sparkle).
- `utils/constants.py` — `surface_dark`, `tips_background`, `tips_border`, `button_shadow`, `panel_shadow` renkleri eklendi (önceden QML'de hardcode edilen hex/rgba değerleri buraya taşındı); `WINDOW_TITLE`/dosya filtreleri `utils/strings.py`'ye taşındı.
- `backend/app_backend.py` — `utils/strings.py` ve `utils/icons.py`'den okuyup `iconUpload`, `stringButtonUpload` gibi yeni Property'ler olarak QML'e sunuyor; tüm emoji'li f-string'ler kaldırıldı.
- `qml/*.qml` — tüm literal renk/emoji/metin kaldırıldı, `backend.colorX`/`iconX`/`stringX` binding'lerine geçirildi. Butonlara `Image` ikon eklendi (`StyledButton.icon`), panel/tips başlıklarına `ColorOverlay` ile temaya göre renklenen ikon eklendi.

Geliştirme sırasında bulunup düzeltilen hata: `ApplicationWindow.icon` QML'de grouped property değil (`icon.source: ...` değil, düz `icon: ...` bekliyor) — `Cannot assign to non-existent property "icon"` uyarısı verdi; pencere/taskbar ikonu ayarı bu Qt sürümünde güvenilir çalışmadığı için kapsam dışı bırakıldı (sadece uygulama içi ikonlar hedeflendi), satır kaldırıldı. Runtime doğrulaması: `engine.rootObjects()[0].isVisible()` → `True`, geometry 1400x800, stderr/QML warning temiz (`engine.warnings` sinyaliyle ayrıca doğrulandı).

**Doğrulanamayan:** ikonların ve Türkçe metinlerin gerçek görsel çıktısı (pikselde nasıl göründüğü, ColorOverlay tint doğruluğu) elle/görsel olarak kontrol edilmedi — sadece yapısal yükleme (QML hata/uyarı yokluğu) doğrulandı.

## [2026-09-24] [INGEST] | Wiki kuruldu, mimari dokümante edildi
`AI-Gelistirme-Metodolojisi.md` ve `LLM-wiki.md` ham kaynaklarına göre `docs/wiki/` yapısı ([[rules]], [[index]], [[architecture]]) kuruldu. Kod tabanı ([[architecture]]) analiz edilip design pattern'ler ve işlem akışı belgelendi.

## [2026-09-24] [INGEST] | PySide6 + QML geçişi tamamlandı
Sistem PyQt5 widget tabanlı UI'dan **PySide6 + QML**'e geçirildi (kullanıcı talebi, mimari karar — bkz [[architecture]]). Kapsam: mevcut özel karanlık tema QML'de birebir korundu (renk/boyut sabitleri `utils/constants.py`'de tek doğruluk kaynağı olarak kaldı); Python↔QML köprüsü tek bir `Backend(QObject)` (Facade) ile kuruldu (`backend/app_backend.py`); `ModelManager`, `ImageProcessor`, `ImageEnhancer`, `BackgroundRemoverWorker` mantığı değişmeden korundu, sadece `pyqtSignal` → `Signal` (PySide6 API) çevrildi; eski `ui/` klasörü (PyQt5 widget kodu) tamamen silindi. Yeni dosyalar: `backend/app_backend.py`, `qml/Main.qml`, `qml/ControlPanel.qml`, `qml/ImageViewPanel.qml`, `qml/StyledButton.qml`. `requirements.txt`, `README.md` güncellendi. `.venv` içinde `PyQt5` kaldırılıp `PySide6` kuruldu (base Python'a dokunulmadı).

Geliştirme sırasında bulunup düzeltilen QML hataları: `ImageViewPanel.qml`'de eksik `import QtQuick.Controls` (Label kullanılamıyordu), `ComboBox` özelleştirmesi için varsayılan native stilin `background`/`contentItem` override'a izin vermemesi (`QQuickStyle.setStyle("Basic")` ile çözüldü). Runtime doğrulaması: `engine.rootObjects()[0].isVisible()` → `True`, pencere başlığı "Background Remover AI", geometry 1400x800, stderr temiz.

**Doğrulanamayan:** gerçek sürükle-bırak hissi, buton tıklama akışı, gerçek görsel işleme çıktısı uçtan uca elle test edilmedi — sadece pencerenin hatasız açıldığı doğrulandı.

## [2026-09-24] [REVIEW] | 7 bulgu uygulandı + runtime doğrulamasında 8. kritik bulgu bulundu ve düzeltildi
[[code-review-2026-09-24]] içindeki 7 bulgu sırayla uygulandı: `.gitignore` + `.pyc` takipten çıkarma, `README.md` kırık referans temizliği, `typing.Any` düzeltmesi (3 dosya), ölü import/sabit temizliği, ölü `_update_responsive_fonts` kaldırma, `resizeEvent`'te disk yerine önbellekli `QPixmap` kullanımı, `requirements.txt` eklendi. `python -m py_compile` ile sözdizimi doğrulandı. Ardından proje kökünde `.venv` kurulup (`python -m venv .venv`, bağımlılıklar sadece venv içine kuruldu, base Python'a dokunulmadı) uygulama gerçekten çalıştırıldı. Bu sırada **8. bulgu** ortaya çıktı: `main.py`'de PyQt5'in onnxruntime'dan önce importlanması Windows'ta DLL çakışmasına yol açıp uygulamanın açılmasını tamamen engelliyordu. Import sırası düzeltildi, uygulama pencere başlığıyla ("Background Remover AI", `Responding: True`) doğrulandı ve test süreci temiz kapatıldı.

## [2026-09-24] [REVIEW] | İlk kod inceleme raporu oluşturuldu
Tüm kod tabanı taranarak god object/SOLID/DRY/KISS/optimizasyon + mantık hatası açısından incelendi. 7 bulgu tespit edildi, bkz [[code-review-2026-09-24]]. Henüz onay alınmadı, hiçbir düzeltme uygulanmadı.
