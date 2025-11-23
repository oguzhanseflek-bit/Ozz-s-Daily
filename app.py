import streamlit as st
from datetime import datetime
import os
import json

DATA_FILE = "gorevler.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"date": str(datetime.now().date()), "tasks": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def check_new_day(data):
    bugun = str(datetime.now().date())
    if data.get("date") != bugun:
        yeni_gorevler = [t for t in data["tasks"] if not t["completed"]]
        data["date"] = bugun
        data["tasks"] = yeni_gorevler
        save_data(data)
        st.toast("Yeni gün! Yapılanlar temizlendi.")
    return data

def get_daily_color():
    colors = ["#FFD1DC", "#FFDAC1", "#FFF5BA", "#B5EAD7", "#C7CEEA", "#E2F0CB", "#FF9AA2"]
    return colors[datetime.now().weekday()]

st.set_page_config(page_title="Günlük Notum", page_icon="📝")
data = check_new_day(load_data())

st.markdown(f"""<style>.stApp {{background-color: {get_daily_color()};}} 
.stTextInput>div>div {{background-color: white; border-radius: 10px;}}</style>""", unsafe_allow_html=True)

st.title(f"📅 {datetime.now().strftime('%d.%m.%Y')}")

with st.form("ekle", clear_on_submit=True):
    c1, c2 = st.columns([4,1])
    yeni = c1.text_input("Not ekle:", placeholder="Görev yaz...")
    if c2.form_submit_button("Ekle") and yeni:
        data["tasks"].append({"text": yeni, "completed": False})
        save_data(data)
        st.rerun()

for i, task in enumerate(data["tasks"]):
    durum = st.checkbox(task["text"], value=task["completed"], key=f"t_{i}")
    if durum != task["completed"]:
        data["tasks"][i]["completed"] = durum
        save_data(data)
        st.rerun()