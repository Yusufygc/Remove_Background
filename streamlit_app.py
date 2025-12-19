# Gerekli Kütüphaneler: streamlit, rembg, Pillow
# Kurulum: pip install streamlit rembg Pillow
# streamlit run streamlit_app.py ile çalıştırabilirsiniz.
import streamlit as st
import os
from rembg import remove
from PIL import Image
from io import BytesIO

# --- HATA DÜZELTME ÇÖZÜMÜ ---
# Eğer sistemde NVIDIA CUDA/cuDNN sürücüleri yüklü değilse, CPU kullanmaya zorlar.
os.environ["ONNX_PROVIDERS"] = "CPUExecutionProvider"
# -----------------------------

def arka_plan_sil(input_bytes, model_adi: str):
    """
    Bayt verisi olarak gelen görüntünün arka planını siler.
    """
    try:
        # 1. Bayt verisini PIL Image nesnesine dönüştürme
        input_image = Image.open(BytesIO(input_bytes))
        
        # 2. Arka planı silme
        output_image = remove(input_image, session_name=model_adi)
        
        # 3. Çıktı görüntüsünü bayt verisi olarak kaydetme (Streamlit için gerekli)
        output_bytes = BytesIO()
        output_image.save(output_bytes, format="PNG")
        output_bytes.seek(0)
        
        return output_bytes
        
    except Exception as e:
        st.error(f"İşlem sırasında bir hata oluştu: {e}")
        return None

def main():
    """
    Streamlit uygulamasının ana yapısı.
    """
    
    st.set_page_config(
        page_title="Hızlı Arka Plan Silici (Streamlit)", 
        layout="centered",
        initial_sidebar_state="expanded"
    )

    st.title("🐍 Python Arka Plan Silici")
    st.markdown("`rembg` kütüphanesini kullanarak resimlerin arka planını kolayca kaldırın.")

    # --- Sol Menü (Ayarlar) ---
    st.sidebar.header("Ayarlar")
    
    # Model Seçimi
    model_secimi = st.sidebar.selectbox(
        "Kullanılacak Arka Plan Modeli:",
        options=["mask", "u2net", "u2netp"],
        index=0, # Varsayılan olarak 'mask' seçili
        format_func=lambda x: {
            "mask": "Logo/Grafik (Keskin Hatlar) - mask",
            "u2net": "Genel Fotoğraf (Yumuşak Hatlar) - u2net",
            "u2netp": "Hızlı Genel Fotoğraf (u2netp)"
        }.get(x, x),
        help="Logolar ve grafikler için 'mask', insan ve nesne fotoğrafları için 'u2net'i seçin."
    )
    
    st.sidebar.markdown(f"**Seçilen Model:** `{model_secimi}`")
    st.sidebar.markdown("---")
    
    # --- Ana İçerik (Dosya Yükleme) ---
    uploaded_file = st.file_uploader(
        "Arka planını silmek istediğiniz resmi buraya sürükleyin veya tıklayın (JPG/PNG)", 
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        # Dosya yüklendiğinde
        
        # 1. Yüklenen dosyayı okuma
        image_bytes = uploaded_file.getvalue()
        
        col1, col2 = st.columns(2)
        
        # Orijinal Görüntüyü Göster
        with col1:
            st.subheader("Orijinal Görüntü")
            st.image(image_bytes, caption=uploaded_file.name, use_column_width=True)

        # 2. Arka Plan Silme İşlemi
        st.info(f"'{model_secimi}' modeli kullanılarak arka plan silme işlemi başlatıldı...")
        
        # İşlem sırasında bir ilerleme göstergesi koymak iyi bir kullanıcı deneyimidir
        with st.spinner('İşleniyor... Lütfen bekleyin.'):
            # Arka plan silme fonksiyonunu çağır
            output_bytes = arka_plan_sil(image_bytes, model_secimi)

        # 3. Sonuç Görüntüsünü Göster ve İndirme Butonu Ekle
        if output_bytes:
            st.success("İşlem Tamamlandı!")
            
            # Sonucu PNG olarak göstermek için Image nesnesini kullanıyoruz
            result_image = Image.open(output_bytes)
            
            with col2:
                st.subheader("Arka Planı Silinmiş Sonuç")
                # Arka planın şeffaf olduğunu göstermek için siyah bir zemin kullanabiliriz
                st.image(result_image, caption="Şeffaf Arka Plan (PNG)", use_column_width=True)

            # İndirme Butonu
            new_filename = f"arka_plansiz_{uploaded_file.name.split('.')[0]}.png"
            st.download_button(
                label="Sonuç Resmini İndir (PNG)",
                data=output_bytes,
                file_name=new_filename,
                mime="image/png"
            )

    else:
        st.warning("Lütfen başlamak için bir resim dosyası yükleyin.")

if __name__ == "__main__":
    main()
