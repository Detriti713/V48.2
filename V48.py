import streamlit as st
import os, shutil, requests, time, hashlib, json, re, io
from PIL import Image

st.set_page_config(page_title="V48 The Perfect One", layout="wide")

st.markdown("""
<style>
.stButton > button { border-radius: 8px; width: 100%; }
.arama-etiketi { font-size: 11px; color: #00ff9d; background: rgba(0,255,157,0.1); padding: 4px 8px; border-radius: 4px; display: block; margin-bottom: 6px; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🔥 V48 "The Perfect One"")
ANA_KLASOR = "Unlu_Arsivleri"
if not os.path.exists(ANA_KLASOR): os.makedirs(ANA_KLASOR)

JUNK_KEYWORDS = ['thumbnail', 'ads', 'banner', 'logo', 'icon', 'promo', 'ad_']

def gorsel_hash_uret(veri):
try:
if isinstance(veri, bytes): img = Image.open(io.BytesIO(veri))
else: img = Image.open(veri)
try: rspl = Image.Resampling.LANCZOS
except Exception: rspl = Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else 0
img = img.convert('L').resize((9, 8), rspl)
pixels = list(img.getdata())
return "".join(["1" if pixels[i] > pixels[i+1] else "0" for i in range(64)])
except: return hashlib.md5(veri).hexdigest() if isinstance(veri, bytes) else str(time.time())

def motor_sorgula(sorgu, sayfa):
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/120.0.0.0"}
urls = [
f"https://yandex.com.tr/gorsel/search?text={sorgu}&p={sayfa}",
f"https://www.bing.com/images/search?q={sorgu}&first={sayfa*20}"
 ]
links = []
for url in urls:
try:
r = requests.get(url, headers=headers, timeout=10)
bulunanlar = re.findall(r'(https?://[^\s"'<>]+?.(?:jpg|jpeg|png|webp))', r.text)
links.extend(bulunanlar)
except Exception: continue
return list(set(links))

--- YAN MENÜ ---
st.sidebar.header("🔍 Arşiv Motoru")
kisi_adi = st.sidebar.text_input("Kişi:", placeholder="Kylie Jenner")
arama_terimi = st.sidebar.text_input("Terim:", placeholder="paparazzi, candid")
foto_limit = st.sidebar.slider("Foto Limit:", 0, 500, 40, 10)

if st.sidebar.button("🚀 İNDİRMEYİ BAŞLAT"):
if kisi_adi:
yol = os.path.join(ANA_KLASOR, kisi_adi.replace(" ", "_"))
os.makedirs(yol, exist_ok=True)
f_sayac = 0
durum = st.sidebar.empty()
p_bar = st.sidebar.progress(0)
kelimeler = [f"{kisi_adi} {arama_terimi}", f"{kisi_adi} paparazzi"]
mevcut_hashler = set()
for f in os.listdir(yol):
fp = os.path.join(yol, f)
if os.path.isfile(fp) and not f.startswith('.'):
try: mevcut_hashler.add(gorsel_hash_uret(fp))
except Exception: pass

for k in kelimeler:
if f_sayac >= foto_limit: break
for sayfa in range(1, 20):
durum.info(f"Taranıyor: {k} (Sayfa {sayfa})")
for url in motor_sorgula(k, sayfa):
if f_sayac >= foto_limit: break
if not all(part.lower() in url.lower() for part in kisi_adi.split()): continue
if any(junk in url.lower() for junk in JUNK_KEYWORDS): continue
try:
r = requests.get(url, timeout=5, stream=True)
if r.status_code == 200:
chunk_data = r.content
if len(chunk_data) > 5000:
dosya_hash = gorsel_hash_uret(chunk_data)
if dosya_hash in mevcut_hashler: continue
etiket_metni = arama_terimi if arama_terimi else "Genel"
safe_tag = "".join([c for c in etiket_metni.replace(" ", "") if c.isalnum() or c == ""])
fname = hashlib.md5(chunk_data).hexdigest() + f"_{safe_tag}" + ".jpg"
with open(os.path.join(yol, fname), 'wb') as f: f.write(chunk_data)
mevcut_hashler.add(dosya_hash)
f_sayac += 1
p_bar.progress(min(f_sayac/max(foto_limit, 1), 1.0))
except Exception: continue
durum.success("İşlem Tamamlandı!")
st.rerun()

--- GALERİ ---
if "buyuk" not in st.session_state: st.session_state["buyuk"] = None
if st.session_state["buyuk"]:
st.markdown("### 🔎 İnceleme")
st.image(st.session_state["buyuk"], use_container_width=False)
if st.button("🔽 Kapat"): st.session_state["buyuk"] = None; st.rerun()
st.markdown("---")

mevcut = [d for d in os.listdir(ANA_KLASOR) if os.path.isdir(os.path.join(ANA_KLASOR, d))]
if "aktif" not in st.session_state or st.session_state["aktif"] not in mevcut: st.session_state["aktif"] = mevcut[0] if mevcut else None

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
dosyalar = [os.path.join(yol, f) for f in os.listdir(yol) if f.lower().endswith(('.jpg','.png','.webp'))]
st.markdown(f"## {secilen} ({len(dosyalar)} Dosya)")
for chunk_idx in range(0, len(dosyalar), 4):
cols = st.columns(4)
for i, f_yol in enumerate(dosyalar[chunk_idx:chunk_idx+4]):
with cols[i]:
cols[i].image(f_yol, use_container_width=True)
if cols[i].button("🔎 Büyüt", key=f"b_{f_yol}"): st.session_state["buyuk"] = f_yol; st.rerun()
if cols[i].button("🗑️ Sil", key=f"d_{f_yol}"): os.remove(f_yol); st.rerun()