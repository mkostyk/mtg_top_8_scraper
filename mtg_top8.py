import requests
from bs4 import BeautifulSoup
import re

BASE_NAME = "https://mtgtop8.com/"
FORMATS = {"standard": "ST", "pioneer": "PI", "modern": "MO", "legacy": "LE", "historic": "HI", "explorer": "EXP",
           "vintage": "VI", "pauper": "PA", "cedh": "cEDH", "commander": "EDH"}

def fetch_top_decks_archetypes(format):
    format_code = FORMATS[format.lower()]
    URL = 'https://mtgtop8.com/format?f=' + format_code
    page = requests.get(URL)

    document = BeautifulSoup(page.content, "html.parser")
    cells = document.select_one("td")
    decks = cells.find_all("div", attrs={"style": "display:inline-block;width:48%;", "class": "hover_tr"})

    parsed_decks = []

    for deck in decks:
        name = deck.find("a").text
        link = deck.find("a")["href"]
        popularity = deck.find_all("div", class_="S14")[1].text
        parsed_decks.append({"name": name, "popularity": popularity, "link": link})

    return parsed_decks


def fetch_ids_from_archetype(archetype):
    URL = BASE_NAME + archetype["link"]
    page = requests.get(URL)

    document = BeautifulSoup(page.content, "html.parser")
    table = document.select_one("table", attrs={"width": "99%"})
    rows = table.find_all("tr", class_="hover_tr")

    decks_list = []

    for row in rows:
        link = row.select_one("a")["href"]
        splited = re.split('=|&', link)
        event_id = splited[1]
        deck_id = splited[3]
        author = row.find_all("a")[1].text
        decks_list.append({"event_id": event_id, "deck_id": deck_id, "author": author})

    archetype["decks"] = decks_list
    return archetype


def fetch_deck(deck, split=False):
    URL = BASE_NAME + "event?e=" + deck["event_id"] + "&d=" + deck["deck_id"]
    page = requests.get(URL)

    document = BeautifulSoup(page.content, "html.parser")
    elements = document.find_all("div", class_="deck_line hover_tr")
    
    cards = []

    for element in elements:
        amount = element.text.split(" ")[0]
        name = element.select_one("span").text
        if (split):
            for i in range(int(amount)):
                cards.append(name)
        else:
            cards.append({"amount": amount, "name": name})

    deck["cards"] = cards
    return deck


def get_top_decks(format, split=False):
    archetypes = fetch_top_decks_archetypes(format)
    for type in archetypes:
        decks = fetch_ids_from_archetype(type)
        for deck in decks["decks"]:
            deck = fetch_deck(deck, split)

        print(type["name"] + " decks fetched successfully")


    return archetypes