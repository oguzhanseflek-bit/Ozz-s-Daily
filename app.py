import streamlit as st
from datetime import datetime
import os
import json

# --- AYARLAR ---
DATA_FILE = "gorevler.json"

# --- VERİ YÖNETİMİ ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}  # Boş sözlük { "2023-11-23": [...], "2023-11-24": [...] }
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- RENK SEÇİCİ ---
def get_daily_color(date_obj):
    colors = ["#FFD1DC", "#FFDAC1", "#FFF5BA", "#B5EAD7", "#C7CEEA", "#E2F0CB", "#FF9AA2"]
    return colors[date_obj.weekday()]

# --- ANA UYGULAMA ---
def main():
    st.set_page_config(page_title="Planlayıcım", page_icon="📅", layout="wide")

    # Veriyi yükle
    all_data = load_data()

    # --- YAN MENÜ (SIDEBAR) - TAKVİM ---
    with st.sidebar:
        st.header("🗓 Takvim")
        secilen_tarih = st.date_input("Günü Seç", datetime.now())
        secilen_tarih_str = str(secilen_tarih)
        
        st.info("💡 Geçmiş günlere bakabilir veya gelecek günler için plan yapabilirsin.")

    # --- GÜN KONTROLÜ ---
    # Eğer seçilen tarih veritabanında yoksa, boş bir liste oluştur
    if secilen_tarih_str not in all_data:
        all_data[secilen_tarih_str] = []

    gunluk_gorevler = all_data[secilen_tarih_str]

    # --- TASARIM VE RENKLER ---
    bg_color = get_daily_color(secilen_tarih)
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {bg_color}; }}
        .task-box {{ 
            background-color: white; 
            padding: 10px; 
            border-radius: 10px; 
            margin-bottom: 5px; 
            border-left: 5px solid #555;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title(f"📅 {secilen_tarih.strftime('%d %B %Y')} - Planı")

    # --- YENİ GÖREV EKLEME ALANI ---
    # Sadece bugüne veya geleceğe ekleme yapılsın, geçmiş değiştirilmesin (İsteğe bağlı)
    with st.expander("➕ Yeni Görev / Toplantı Ekle", expanded=True):
        with st.form("yeni_gorev", clear_on_submit=True):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                saat = st.time_input("Saat", value=datetime.now().time())
            with col2:
                gorev = st.text_input("Görev/Not", placeholder="Örn: Müşteri toplantısı...")
            with col3:
                submitted = st.form_submit_button("Kaydet")
            
            if submitted and gorev:
                yeni_kayit = {
                    "time": str(saat)[:5], # Sadece HH:MM formatında al
                    "task": gorev,
                    "completed": False
                }
                all_data[secilen_tarih_str].append(yeni_kayit)
                # Saat sırasına göre diz (09:00, 10:00...)
                all_data[secilen_tarih_str] = sorted(all_data[secilen_tarih_str], key=lambda x: x["time"])
                save_data(all_data)
                st.rerun()

    st.divider()

    # --- GÖREVLERİ LİSTELE ---
    if not gunluk_gorevler:
        st.caption("📭 Bu tarih için henüz bir plan yok.")
    else:
        # Tamamlanmayanları yarına aktar butonu (Sadece bugünse göster)
        if secilen_tarih_str == str(datetime.now().date()):
            if st.button("♻️ Yapılmayanları Yarına Aktar"):
                yarin_str = str(datetime.now().date().replace(day=datetime.now().day + 1)) # Basit tarih artırma
                if yarin_str not in all_data: all_data[yarin_str] = []
                
                # Tamamlanmayanları bul
                devredenler = [t for t in gunluk_gorevler if not t["completed"]]
                # Bugünden silme mantığı senin tercihine kalmış, şimdilik sadece kopyalıyoruz
                all_data[yarin_str].extend(devredenler)
                all_data[yarin_str] = sorted(all_data[yarin_str], key=lambda x: x["time"]) # Sırala
                save_data(all_data)
                st.success(f"{len(devredenler)} görev yarına aktarıldı!")

        for i, item in enumerate(gunluk_gorevler):
            # Görsel Düzen: [SAAT] [CHECKBOX-GÖREV] [SİL BUTONU]
            c1, c2, c3 = st.columns([1, 6, 1])
            
            with c1:
                st.markdown(f"**⏰ {item['time']}**")
            
            with c2:
                # Checkbox
                is_done = st.checkbox(item["task"], value=item["completed"], key=f"{secilen_tarih_str}_{i}")
                if is_done != item["completed"]:
                    all_data[secilen_tarih_str][i]["completed"] = is_done
                    save_data(all_data)
                    st.rerun()
            
            with c3:
                # Silme butonu (İstersen kaldırabilirsin)
                if st.button("🗑️", key=f"del_{secilen_tarih_str}_{i}"):
                    del all_data[secilen_tarih_str][i]
                    save_data(all_data)
                    st.rerun()
            
            st.markdown("---")

if __name__ == "__main__":
    main()
