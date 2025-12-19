# Gerekli Kütüphaneler: rembg ve Pillow (PIL)
# Kurulum: pip install rembg Pillow

import os
from rembg import remove
from PIL import Image

# --- HATA DÜZELTME ÇÖZÜMÜ ---
# Eğer sisteminizde NVIDIA CUDA/cuDNN sürücüleri yüklü değilse ve ONNX Runtime
# otomatik olarak GPU'yu kullanmaya çalışıp başarısız olursa bu satır CPU'ya geçmeye zorlar.
os.environ["ONNX_PROVIDERS"] = "CPUExecutionProvider"
# -----------------------------

def arka_plan_sil(giris_dosya_yolu, cikis_dosya_yolu):
    """
    Belirtilen girdi dosyasındaki görüntünün arka planını siler ve
    sonucu şeffaf arka planlı bir PNG olarak kaydeder.
    """
    try:
        # 1. Girdi dosyasının varlığını kontrol etme
        if not os.path.exists(giris_dosya_yolu):
            print(f"HATA: Girdi dosyası bulunamadı: '{giris_dosya_yolu}'")
            print("Lütfen bu betiğin yanına 'girdi.jpg' adında bir resim dosyası koyduğunuzdan emin olun.")
            return

        # 2. Görüntüyü açma (Pillow kullanarak)
        print(f"'{giris_dosya_yolu}' dosyası yükleniyor...")
        input_image = Image.open(giris_dosya_yolu)

        # 3. Arka planı silme (rembg kullanarak)
        # LOGO ve GRAFİKSEL öğelerde daha keskin sonuçlar almak için 'mask' modelini kullanıyoruz.
        # Varsayılan model: 'u2net' (Daha çok fotoğraflar için)
        print("Arka plan silme işlemi gerçekleştiriliyor (CPU ve 'mask' modeli kullanılıyor)...")
        output_image = remove(input_image, session_name='mask')

        # 4. Çıktı görüntüsünü kaydetme
        output_image.save(cikis_dosya_yolu)
        print("-" * 40)
        print(f"BAŞARILI! Arka planı silinmiş görüntü '{cikis_dosya_yolu}' olarak kaydedildi.")
        print("Çıktı dosyası şeffaf arka plana sahip bir PNG'dir.")
        print("Not: 'mask' modeli, logolar ve keskin hatlı grafikler için daha iyi sonuç vermelidir.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        print("Lütfen rembg kütüphanesinin doğru yüklendiğinden emin olun (pip install rembg).")

# --- KULLANIM ALANI ---

# Arka planı silinecek resmin dosya yolunu buraya yazın.
# Örnek olarak, betiğin çalıştığı klasöre "girdi.jpg" adında bir dosya koyabilirsiniz.
GIRDI_DOSYA = "img/porche.jpg"

# Çıktı dosyasının kaydedileceği yol. PNG şeffaflığı destekler.
# Çıktı dosyasını önceki sonuçla karışmaması için adını değiştirdim.
CIKIS_DOSYA = "cleanBg/porche_mask_modeli.png"

if __name__ == "__main__":
    print("--- Python Arka Plan Silme Uygulaması ---")
    arka_plan_sil(GIRDI_DOSYA, CIKIS_DOSYA)
