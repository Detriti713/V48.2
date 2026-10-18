import streamlit as st
import os, shutil, requests, time, hashlib, json, re, io
from PIL import Image

st.set_page_config(page_title="Pro Mega Arşivleyici V48", layout="wide")

# V48 Orijinal UI Stilleri
st.markdown("""
    <style>
    .stButton > button { border-radius: 8px; width: 100%; }
    .arama-etiketi { font-size: 11px; color: #00ff9d; background: rgba(0,255,157,0.1); padding: 4px 8px; border-radius: 4px; display: block; margin-bottom: 6px; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🔥 Mega Arşivleyici V48 (Orijinal Kararlı Sürüm)")
ANA_KLASOR = "Unlu_Arsivleri"
if not os.path.exists(ANA_KLASOR): os.makedirs(ANA_KLASOR)

JUNK_KEYWORDS = ['thumbnail', 'ads', 'banner', 'logo', 'icon', 'promo', 'ad_']

# V48 dHash Algoritması
def gorsel_hash_uret(veri, is_video=False):
    try:
        if is_video:
            if isinstance(veri, bytes): return hashlib.md5(veri).hexdigest()
            with open(veri, "rb") as f: return hashlib.md5(f.read()).hexdigest()
        
        if isinstance(veri, bytes): img = Image.open(io.BytesIO(veri))
        else: img = Image.open(veri)
        
        try: rspl = Image.Resampling.LANCZOS
        except Exception: rspl = Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else 0
        
        img = img.convert('L').resize((9, 8), rspl)
        pixels = list(img.getdata())
        
        hash_bits = []
        for row in range(8):
            for col in range(8):
                idx = row * 9 + col
                hash_bits.append("1" if pixels[idx] > pixels[idx+1] else "0")
        return "".join(hash_bits)
    except Exception:
        if isinstance(veri, bytes): return hashlib.md5(veri).hexdigest()
        try:
            with open(veri, "rb") as f: return hashlib.md5(f.read()).hexdigest()
        except Exception: return str(veri)

def motor_sorgula(sorgu, sayfa):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    urls = [
        f"https://yandex.com.tr/gorsel/search?text={sorgu}&p={sayfa}",
        f"https://www.bing.com/images/search?q={sorgu}&first={sayfa*20}",
        f"https://yandex.com.tr/video/search?text={sorgu}&p={sayfa}",
        f"https://www.bing.com/videos/search?q={sorgu}"
    ]
    links = []
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            bulunanlar = re.findall(r'(https?://[^\s"\'<>]+?\.(?:jpg|jpeg|png|webp|mp4|gif))', r.text)
            links.extend(bulunanlar)
            ham_videolar = re.findall(r'"(https?://[^"\s<>]+?\.mp4[^"\s<>]*)"', r.text)
            links.extend([v.split('?')[0] for v in ham_videolar])
        except Exception: continue
    return list(set(links))

# --- YAN MENÜ ---
st.sidebar.header("🔍 Arşiv Motoru")
kisi_adi = st.sidebar.text_input("Kişi:", placeholder="Kylie Jenner")
arama_terimi = st.sidebar.text_input("Terim:", placeholder="paparazzi, candid, video")
foto_limit = st.sidebar.slider("Foto Limit:", 0, 500, 40, 10)
video_limit = st.sidebar.slider("Video Limit:", 0, 50, 10, 1)

if st.sidebar.button("🚀 İNDİRMEYİ BAŞLAT"):
    if kisi_adi:
        yol = os.path.join(ANA_KLASOR, kisi_adi.replace(" ", "_"))
        os.makedirs(yol, exist_ok=True)
        f_sayac = 0
        v_sayac = 0
        durum = st.sidebar.empty()
        p_bar = st.sidebar.progress(0)
        kelimeler = [f"{kisi_adi} {arama_terimi}", f"{kisi_adi} video", f"{kisi_adi} paparazzi"]
        mevcut_hashler = set()
        for f in os.listdir(yol):
            fp = os.path.join(yol, f)
            if os.path.isfile(fp) and not f.startswith('.'):
                try:
                    if os.path.getsize(fp) > 1024:
                        is_vid = f.lower().endswith('.mp4')
                        mevcut_hashler.add(gorsel_hash_uret(fp, is_video=is_vid))
                except Exception: pass
        
        try:
            del_file = os.path.join(yol, ".silinen_hashler.json")
            if os.path.exists(del_file):
                with open(del_file, "r") as f_json:
                    for dh in json.load(f_json):
                        mevcut_hashler.add(dh)
        except Exception: pass
        
        for idx, k in enumerate(kelimeler):
            if f_sayac >= foto_limit and v_sayac >= video_limit: break
            for sayfa in range(1, 20):
                durum.info(f"Taranıyor: {k} (Sayfa {sayfa})")
                linkler = motor_sorgula(k, sayfa)
                for url in linkler:
                    if f_sayac >= foto_limit and v_sayac >= video_limit: break
                    if not all(part.lower() in url.lower() for part in kisi_adi.split()): continue
                    if any(junk in url.lower() for junk in JUNK_KEYWORDS): continue
                    is_video = url.lower().endswith('.mp4') or '.mp4' in url.lower()
                    if (is_video and v_sayac >= video_limit) or (not is_video and f_sayac >= foto_limit): continue
                    try:
                        r = requests.get(url, timeout=5, stream=True)
                        if r.status_code == 200:
                            content_type = r.headers.get('Content-Type', '')
                            if 'image' in content_type or 'video' in content_type:
                                chunk_data = r.content
                                if len(chunk_data) > 5000:
                                    dosya_hash = gorsel_hash_uret(chunk_data, is_video=is_video)
                                    is_mukerrer = False
                                    if len(dosya_hash) == 64: 
                                        for m_hash in mevcut_hashler:
                                            if len(m_hash) == 64:
                                                fark = sum(c1 != c2 for c1, c2 in zip(dosya_hash, m_hash))
                                                if fark <= 16:
                                                    is_mukerrer = True
                                                    break
                                    else: 
                                        if dosya_hash in mevcut_hashler:
                                            is_mukerrer = True
                                    if is_mukerrer: continue 
                                    etiket_metni = arama_terimi if arama_terimi else "Genel"
                                    safe_tag = "".join([c for c in etiket_metni.replace(" ", "_") if c.isalnum() or c == "_"])
                                    fname = hashlib.md5(chunk_data).hexdigest() + f"___{safe_tag}__" + (".mp4" if is_video else ".jpg")
                                    path = os.path.join(yol, fname)
                                    with open(path, 'wb') as f:
                                        f.write(chunk_data)
                                    mevcut_hashler.add(dosya_hash)
                                    if is_video: v_sayac += 1
                                    else: f_sayac += 1
                                    p_bar.progress(min((f_sayac+v_sayac)/(max(foto_limit+video_limit, 1)), 1.0))
                    except Exception: continue
        durum.success("İşlem Tamamlandı!")
        st.rerun()

# --- GALERİ ---
if "buyuk" not in st.session_state: st.session_state["buyuk"] = None

if st.session_state["buyuk"]:
    st.markdown("### 🔎 İnceleme")
    if st.session_state["buyuk"].lower().endswith('.mp4'):
        st.video(st.session_state["buyuk"])
    else:
        st.image(st.session_state["buyuk"], use_container_width=False)
    if st.button("🔽 Kapat"):
        st.session_state["buyuk"] = None
        st.rerun()
    st.markdown("---")

mevcut = [d for d in os.listdir(ANA_KLASOR) if os.path.isdir(os.path.join(ANA_KLASOR, d))]
if "aktif" not in st.session_state or st.session_state["aktif"] not in mevcut: 
    st.session_state["aktif"] = mevcut[0] if mevcut else None

if mevcut:
    st.subheader("👤 Mevcut Arşivler")
    cols = st.columns(min(len(mevcut), 6))
    for i, kls in enumerate(mevcut):
        if cols[i % 6].button(kls, type="primary" if st.session_state["aktif"] == kls else "secondary"):
            st.session_state["aktif"] = kls
            st.rerun()

    if st.session_state["aktif"]:
        secilen = st.session_state["aktif"]
        yol = os.path.join(ANA_KLASOR, secilen)
        dosyalar = [os.path.join(yol, f) for f in os.listdir(yol) if f.lower().endswith(('.jpg','.png','.mp4','.webp'))]
        st.markdown(f"## {secilen} ({len(dosyalar)} Dosya)")
        
        for chunk_idx in range(0, len(dosyalar), 4):
            cols = st.columns(4)
            for i, f_yol in enumerate(dosyalar[chunk_idx:chunk_idx+4]):
                with cols[i]:
                    if f_yol.lower().endswith('.mp4'): cols[i].video(f_yol)
                    else: cols[i].image(f_yol, use_container_width=True)
                    if cols[i].button("🔎 Büyüt", key=f"b_{f_yol}"):
                        st.session_state["buyuk"] = f_yol
                        st.rerun()
                    if cols[i].button("🗑️ Sil", key=f"d_{f_yol}"):
                        os.remove(f_yol)
                        st.rerun()
