import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Funktion zur Entfernungsmessung via Google Maps Distance Matrix API
def entfernung_berechnen(start, ziel, api_key):
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": start,
        "destinations": ziel,
        "mode": "transit",
        "key": api_key
    }
    r = requests.get(base_url, params=params)
    data = r.json()
    try:
        return data["rows"][0]["elements"][0]["duration"]["text"]
    except:
        return "Unbekannt"

# Funktion zur Wohnungsanzeigensuche bei eBay Kleinanzeigen (statisch)
def suche_wohnungen(stadt, miete_max, zimmer, arbeitsadresse, api_key):
    base_url = f"https://www.kleinanzeigen.de/s-wohnung-mieten/{stadt}/k0c203"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    angebote = soup.find_all("article")
    treffer = []

    for angebot in angebote:
        link_tag = angebot.find("a", class_="ellipsis")
        if not link_tag:
            continue
        titel = link_tag.get_text(strip=True)
        link = "https://www.kleinanzeigen.de" + link_tag["href"]
        beschreibung = angebot.get_text()

        if str(miete_max) in beschreibung and str(zimmer) in beschreibung.lower():
            entfernung = entfernung_berechnen(arbeitsadresse, stadt, api_key)
            treffer.append((titel, link, entfernung))
    return treffer

# Streamlit UI
st.title("Wohnungs-Such-Bot")
st.write("Finde provisionsfreie Wohnungen aus mehreren Quellen.")

stadt = st.text_input("Stadt", value="Berlin")
miete_max = st.number_input("Max. Miete (€)", value=800)
zimmer = st.number_input("Min. Anzahl Zimmer", value=2)
arbeitsadresse = st.text_input("Arbeitsadresse", value="Potsdamer Platz, Berlin")
api_key = st.text_input("Google Maps API Key", type="password")

if st.button("Jetzt suchen"):
    st.info("Suche läuft...")
    ergebnisse = suche_wohnungen(stadt, miete_max, zimmer, arbeitsadresse, api_key)

    if not ergebnisse:
        st.warning("Keine passenden Ergebnisse gefunden.")
    else:
        for titel, link, entfernung in ergebnisse:
            st.markdown(f"**{titel}**")
            st.markdown(f"[Ansehen]({link})")
            st.markdown(f"🚌 Entfernung zum Arbeitsplatz: {entfernung}")
            st.markdown("---")
