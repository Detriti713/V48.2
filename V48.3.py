import streamlit as st
import requests
import re
from PIL import Image
from io import BytesIO
import base64

st.set_page_config(
    page_title="V48 - The Perfect One",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel Stil Tanımlamaları
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 V48 - The Perfect One")
st.markdown("### Gelişmiş Web Görsel ve Medya Kazıma ve Analiz Aracı")
st.markdown("---")

# Yan Menü Ayarları ve Filtreler
st.sidebar.header("⚙️ Ayarlar & Filtreler")
user_agent = st.sidebar.selectbox(
    "User-Agent Seçin",
    [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
    ]
)

timeout_val = st.sidebar.slider("İstek Zaman Aşımı (Saniye)", 5, 30, 10)

st.sidebar.subheader("Uzantı Filtreleri")
check_jpg = st.sidebar.checkbox("JPG / JPEG", value=True)
check_png = st.sidebar.checkbox("PNG", value=True)
check_webp = st.sidebar.checkbox("WEBP", value=True)
check_svg = st.sidebar.checkbox("SVG", value=False)
check_gif = st.sidebar.checkbox("GIF", value=False)

extensions = []
if check_jpg: extensions.extend(["jpg", "jpeg"])
if check_png: extensions.append("png")
if check_webp: extensions.append("webp")
if check_svg: extensions.append("svg")
if check_gif: extensions.append("gif")

# Ana Giriş Alanı
col_input1, col_input2 = st.columns([4, 1])
with col_input1:
    url = st.text_input("Hedef Web Sitesi URL'si:", placeholder="https://ornek.com")
with col_input2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("Taramayı Başlat", type="primary", use_container_width=True)

if url or search_button:
    if not url:
        st.warning("Lütfen geçerli bir URL girin.")
    else:
        if not url.startswith("http"):
            url = "https://" + url

        with st.spinner("Hedef site taranıyor, veriler analiz ediliyor..."):
            try:
                headers = {"User-Agent": user_agent}
                response = requests.get(url, headers=headers, timeout=timeout_val)
                
                if response.status_code == 200:
                    st.success(f"Bağlantı başarılı! (HTTP Status: {response.status_code})")
                    
                    # Üçlü tırnak ile SyntaxError hatasından arındırılmış tam regex satırları:
                    ext_str = "|".join(extensions) if extensions else "jpg|jpeg|png|webp"
                    regex_pattern = r"""(https?://[^\s"'<>]+?\.(?:""" + ext_str + r"""\b))"""
                    
                    bulunanlar = re.findall(regex_pattern, response.text, re.IGNORECASE)
                    img_tags = re.findall(r"""<img[^>]+src=["']([^"']+)["']""", response.text, re.IGNORECASE)
                    
                    all_links = list(set(bulunanlar + img_tags))
                    
                    # Göreceli (relative) linkleri tam URL formatına dönüştürme
                    processed_links = []
                    for link in all_links:
                        if link.startswith("//"):
                            processed_links.append("https:" + link)
                        elif link.startswith("/"):
                            base_domain = "/".join(url.split("/")[:3])
                            processed_links.append(base_domain + link)
                        elif not link.startswith("http"):
                            continue
                        else:
                            processed_links.append(link)
                            
                    unique_images = list(set(processed_links))
                    
                    # İstatistik Göstergeleri
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Toplam Bulunan Medya", len(all_links))
                    m2.metric("Benzersiz Görsel", len(unique_images))
                    m3.metric("HTTP Durumu", response.status_code)
                    
                    st.markdown("---")
                    
                    if unique_images:
                        tab1, tab2 = st.tabs(["🖼️ Görsel Önizleme ve Kartlar", "📋 Ham Link Listesi"])
                        
                        with tab1:
                            cols = st.columns(3)
                            for idx, img_url in enumerate(unique_images):
                                with cols[idx % 3]:
                                    st.markdown(f"**Görsel #{idx+1}**")
                                    st.code(img_url, language="text")
                                    try:
                                        st.image(img_url, use_column_width=True)
                                    except Exception as e:
                                        st.info("Önizleme yüklenemedi (CORS / Erişim engeli)")
                                    st.markdown("---")
                                    
                        with tab2:
                            st.subheader("Tüm Linkler (Toplu Kopyalama)")
                            text_data = "\n".join(unique_images)
                            st.text_area("Linkler:", value=text_data, height=300)
                            st.download_button(
                                label="📥 Linkleri TXT Olarak İndir",
                                data=text_data,
                                file_name="v48_gorseller.txt",
                                mime="text/plain"
                            )
                    else:
                        st.warning("Belirtilen kriterlere uygun görsel bulunamadı.")
                else:
                    st.error(f"Sunucu hata kodu döndürdü: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("Bağlantı zaman aşımına uğradı. Lütfen tekrar deneyin.")
            except requests.exceptions.RequestException as e:
                st.error(f"Bir ağ hatası oluştu: {e}")
            except Exception as e:
                st.error(f"Beklenmeyen bir hata oluştu: {e}")
