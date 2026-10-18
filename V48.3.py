import streamlit as st
import requests
import re
from PIL import Image

st.set_page_config(page_title="V48 - The Perfect One", layout="centered")

st.title("V48 - The Perfect One")

url = st.text_input("Web Sitesi URL'si Girin:")

if url:
try:
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers)

# Syntax hatası düzeltilmiş regex satırı:
bulunanlar = re.findall(r'(https?://[^\s"'<>]+?.(?:jpg|jpeg|png|webp))', r.text)

if bulunanlar:
st.success(f"{len(bulunanlar)} adet görsel bulundu!")
for img_url in set(bulunanlar):
st.write(img_url)
try:
st.image(img_url)
except:
pass
else:
st.warning("Görsel bulunamadı.")
except Exception as e:
st.error(f"Bir hata oluştu: {e}")