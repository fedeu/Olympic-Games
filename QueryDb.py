from matplotlib import pyplot as plt
import numpy as np
from load_db import db


def query2(sport): # -- Visualizza altezza, peso ed età degli atleti che hanno vinto una medaglia per una data disciplina;
    queryResult = db.athlete.find({"Achievements.Sport": sport, "Achievements.Medal": {"$ne": None}, "Height": {"$ne": None}, "Weight": {"$ne": None}}, {"_id": 0})
    if queryResult is not None:
        print("---Name---Age---Height---Weight---")
        for r in queryResult:
            if not list(r['Achievements']):  # se la lista delle medaglie è vuota, salta l'atleta dal conteggio
                continue
            else:
                print(r["Name"] + " " + str(int(r["Age"])) + " " + str(r["Height"]) + " " + str(r["Weight"]))


def query4():  # -- Calcola quante medaglie sono state vinte da una data nazione nelle 2 diverse stagioni per uno specifico anno
    team = "Italy"
    year = 1936
    summerMedals = 0
    winterMedals = 0
    summerEvents = db.event.find({"Year": year, "Season": "Summer"}, {"_id": 0, "IDEvent": 1})
    winterEvents = db.event.find({"Year": year, "Season": "Winter"}, {"_id": 0, "IDEvent": 1})
    queries = []

    for event in summerEvents:
        result = db.athlete.find({"Team": team, "Achievements.IDEvent": event["IDEvent"], "Achievements.Medal": {"$ne": None}})
        queries.append(result)

    for queryRes in queries:
        summerMedals += queryRes.countDocuments()

    queries = []
    for event in winterEvents:
        result = db.athlete.find({"Team": team, "Achievements.IDEvent": event["IDEvent"], "Achievements.Medal": {"$ne": None}})
        queries.append(result)

    for queryRes in queries:
        winterMedals += queryRes.countDocuments()
    print("Summer: " + str(summerMedals) + ", Winter: " + str(winterMedals))


def query6():  # -- Elabora un grafico a torta degli sport in cui una data nazione va meglio
    nazione = "Italy"
    resultMap = {}
    queryResult = db.athlete.find({'Team': nazione, 'Achievements.Medal': {
        '$ne': None}})  # Trova tutti gli atleti di una specifica nazione e che hanno vinto una medaglia
    for athlete in queryResult:
        for achievement in athlete["Achievements"]:
            if achievement['Sport'] not in resultMap.keys():  # Aggiunge un nuovo sport
                resultMap[achievement['Sport']] = 1
            else:
                resultMap[achievement['Sport']] += 1  # Incrementa il conteggio delle medaglie per un dato sport

    for key, value in resultMap.items():
        print("Sport: " + key + ", Count of medals: " + str(value))

    # GRAFICO A TORTA
    sports = list(resultMap.keys())[:10]
    medals = list(resultMap.values())[:10]

    colors = ("orange", "cyan", "yellow", "brown", "indigo", "beige", "green") # Color parameters
    explode = (0.1, 0.1, 0.2, 0.3, 0.2, 0.2, 0.1, 0.1, 0.1, 0.0)
    wp = {'linewidth': 1, 'edgecolor': "black"} # Wedge properties

    # Creating autocpt arguments
    def func(pct, allvalues):
        absolute = int(pct / 100. * np.sum(allvalues))
        return "{:.1f}%\n({:d})".format(pct, absolute)

    # Creating plot
    fig, ax = plt.subplots(figsize=(10, 7))
    wedges, texts, autotexts = ax.pie(medals,
                                      autopct=lambda pct: func(pct, medals),
                                      explode=explode,
                                      labels=sports,
                                      shadow=True,
                                      colors=colors,
                                      wedgeprops=wp,
                                      textprops=dict(color="black"))

    # Adding legend
    ax.legend(wedges, sports,
              title="Sport",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=6)
    ax.set_title(nazione)

    plt.show()


def query7(): # -- Mostra il totale delle medaglie attinenti a un dato evento per ogni nazione
    nomeEvento = "Cross Country Skiing Men's 10 kilometres"
    annoEvento = 1992
    cittàEvento = "Albertville"
    stagioneEvento = "Winter"

    result = db.event.aggregate([
        {"$match": {
            "EventName": nomeEvento,
            "Year": annoEvento,
            "City": cittàEvento,
            "Season": stagioneEvento
        }},
        {"$lookup": {
            "from": "athlete",
            "localField": "IDEvent",
            "foreignField": "Achievements.IDEvent",
            "as": "participation"
        }}
    ])

    diz = {}  # per contenere Nazione - NumMedaglie
    for r in result:
        for item in r["participation"]:
            if item["Achievements"][0]["Medal"] is not None:
                team = item["Team"]
                if team not in diz.keys():
                    diz[team] = 1
                else:
                    diz[team] += 1

    for key, val in diz.items():
        print("Team: " + key + " ," + "Count: " + str(val))


def query9(): # -- Riporta per ogni anno il numero di partecipazioni di atleti di uno specifico sesso
    sex = "M"
    queryResult = db.athlete.aggregate([
        {"$match": {
            "Sex": sex
        }},
        {"$lookup": {
            "from": "event",
            "localField": "Achievements.IDEvent",
            "foreignField": "IDEvent",
            "as": "participation"
        }},
        {"$limit": 50}
    ])

    yearMap = {}
    for result in queryResult:
        for event in result["participation"]:
            if event["Year"] not in yearMap.keys():
                yearMap[event["Year"]] = 1
            else:
                yearMap[event["Year"]] += 1

    for key in sorted(yearMap):
        print("%s: %s" % (key, yearMap[key]))


def query10():  # Riporta gli atleti che hanno vinto almeno tot medaglie
    med = 3
    queryResult = db.athlete.find({"Achievements": {"$size": med}, "Achievements.Medal": {"$ne": None}})
    for r in queryResult:
        print(r)
