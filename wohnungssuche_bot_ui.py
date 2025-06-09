import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Entfernung berechnen
def entfernung_berechnen(start, ziel, api_key):
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": start,
        "destinations": ziel,
        "mode": "transit",
        "key": api_key
    }
    try:
        r = requests.get(base_url, params=params)
        data = r.json()
        return data["rows"][0]["elements"][0]["duration"]["text"]
    except:
        return "Unbekannt"

# Funktion zur Extraktion von Preis und qm
def extrahiere_preis_und_qm(text):
    preis = None
    qm = None

    # Preis finden
    preis_match = re.search(r"(\d{3,4})\s*€", text.replace(".", ""))
    if preis_match:
        preis = int(preis_match.group(1))

    # Quadratmeter finden
    qm_match = re.search(r"(\d{2,3})\s*(m²|qm)", text.lower())
    if qm_match:
        qm = int(qm_match.group(1))

    return preis, qm

# WG, Zwischenmiete etc. ausschließen
def ist_ungeeignet(titel, beschreibung):
    blacklist = ["wg", "wohngemeinschaft", "tausch", "zwischenmiete", "zwischenzeit", "mitbewohner", "untermiete"]
    text = (titel + " " + beschreibung).lower()
    return any(wort in text for wort in blacklist)

# Hauptfunktion
def suche_wohnungen(stadt, miete_max, zimmer_min, qm_min, arbeitsadresse, api_key):
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

        if ist_ungeeignet(titel, beschreibung):
            continue

        preis, qm = extrahiere_preis_und_qm(beschreibung)

        if preis is None or preis > miete_max:
            continue
        if qm is None or qm < qm_min:
            continue
        if str(zimmer_min) not in beschreibung.lower():
            continue

        entfernung = entfernung_berechnen(arbeitsadresse, stadt, api_key)
        treffer.append((titel, link, entfernung, preis, qm))

    return treffer

        for titel, link, entfernung in ergebnisse:
            st.markdown(f"**{titel}**")
            st.markdown(f"[Ansehen]({link})")
            st.markdown(f"🚌 Entfernung zum Arbeitsplatz: {entfernung}")
            st.markdown("---")
