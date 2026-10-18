import streamlit as st
import requests
import re
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="V48 - The Perfect One", layout="wide")

st.title("🚀 V48 - The Perfect One")
st.markdown("Gelişmiş Görsel ve Veri Kazıma Aracı")

url = st.text_input("Hedef Web Sitesi URL'si:")

if url:
    if not url.startswith("http"):
        url = "https://" + url
        
    with st.spinner("Site taranıyor ve veriler çekiliyor..."):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                st.success(f"Bağlantı başarılı! Durum Kodu: {r.status_code}")
                
                # Tırnak çakışmasını önleyen üçlü tırnaklı regex satırı:
                bulunanlar = re.findall(r"""(https?://[^\s"'<>]+?\.(?:jpg|jpeg|png|webp))""", r.text)
                
                unique_images = list(set(bulunanlar))
                
                st.info(f"Toplam {len(unique_images)} adet benzersiz görsel bulundu.")
                
                if unique_images:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Bulunan Görsel Linkleri")
                        for img_url in unique_images:
                            st.code(img_url, language="text")
                            
                    with col2:
                        st.subheader("Önizleme Alanı")
                        for idx, img_url in enumerate(unique_images):
                            try:
                                st.write(f"Görsel {idx+1}")
                                st.image(img_url, use_column_width=True)
                            except Exception as img_err:
                                st.warning(f"Görsel önizlemesi yüklenemedi: {img_err}")
                else:
                    st.warning("Bu sayfada eşleşen uzantıda görsel bulunamadı.")
            else:
                st.error(f"Sunucu hata kodu döndürdü: {r.status_code}")
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
