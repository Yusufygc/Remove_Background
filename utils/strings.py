"""Central UI string registry (Turkish). Single source for every user-facing
text; QML files bind to Backend properties instead of embedding literals."""

WINDOW_TITLE = "Arka Plan Kaldırıcı AI"

APP_TITLE = "Arka Plan Kaldırıcı"
APP_SUBTITLE = "Yapay Zeka Destekli Görüntü İşleme"
MODEL_LABEL = "Yapay Zeka Modeli"

BUTTON_UPLOAD = "Görsel Yükle"
BUTTON_REMOVE_BG = "Arka Planı Kaldır"
BUTTON_SAVE = "Sonucu Kaydet"

TIPS_TITLE = "İpuçları"
TIPS_TEXT = (
    "• <b>isnet-general-use</b> logolar için<br>"
    "• <b>u2net</b> karmaşık görseller için<br>"
    "• <b>silueta</b> portreler için<br>"
    "• Küçük görseller otomatik iyileştirilir"
)

HEADER_ORIGINAL = "Orijinal"
HEADER_RESULT = "Sonuç"
PLACEHOLDER_INPUT = "Yüklemek için sürükleyin veya tıklayın"
PLACEHOLDER_OUTPUT = "İşlenmiş görsel burada görünecek"

DIALOG_OPEN_TITLE = "Görsel Seç"
DIALOG_SAVE_TITLE = "Sonucu Kaydet"
DIALOG_ERROR_TITLE = "Hata"

IMAGE_FILE_FILTER = "Görsel Dosyaları (*.png *.jpg *.jpeg *.bmp *.webp)"
PNG_FILE_FILTER = "PNG Dosyaları (*.png)"

# Status bar messages (templates use str.format placeholders)
STATUS_INITIALIZING = "Yapay zeka modelleri yükleniyor..."
STATUS_READY = "Hazır! Başlamak için bir görsel yükleyin"
STATUS_PROCESSING = "{model} ile işleniyor..."
STATUS_SUCCESS = "Başarılı! Kaydetmeye hazır"
STATUS_ERROR = "İşlem başarısız"
STATUS_MODELS_FAILED = "Modeller yüklenemedi"
STATUS_MODEL_LOADED = "Yüklendi: {model}..."
STATUS_MODEL_ERROR = "Model yükleme hatası"
STATUS_SAVED = "Kaydedildi: {filename}"

# Error dialog messages
ERROR_MODELS_FAILED = "Bazı modeller yüklenemedi. Ayrıntılar için konsolu kontrol edin."
ERROR_NO_INPUT = "Önce bir görsel yükleyin."
ERROR_NO_MODEL_SESSION = "Model oturumu yüklenmedi."
ERROR_NO_OUTPUT = "Önce bir görsel işleyin."
ERROR_SAVE_FAILED = "Kaydetme başarısız:\n{error}"
ERROR_PROCESSING_FAILED = "İşlem başarısız:\n{error}"
