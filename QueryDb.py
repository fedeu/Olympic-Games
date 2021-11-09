from matplotlib import pyplot as plt
import numpy as np
from load_db import db


def query1(city):
    # --- QUERY 1: Presa in input una città, mostrare gli eventi che ha ospitato
    queryResult = db.event.find({"City": city}, {"_id": 0, "IDEvent": 0, "City": 0})
    return queryResult, 1


def query2(sport): # -- Visualizza altezza, peso ed età degli atleti che hanno vinto una medaglia per una data disciplina;
    queryResult = db.athlete.find({"Achievements.Sport": sport, "Achievements.Medal": {"$ne": None}, "Height": {"$ne": None}, "Weight": {"$ne": None}}, {"_id": 0, "ID": 1, "Height": 1, "Weight": 1, "Age": 1, "Team": 1, "Achievements": 1})
    return queryResult, 2


def query3(team, year):  # team,year #-- Mostra le medaglie vinte da un team (nazione) in un dato anno;
    lista = []
    result = db.event.find({"Year": year}, {"_id": 0, "IDEvent": 1})
    for r in result:
        result2 = db.athlete.find({"Achievements.IDEvent": r["IDEvent"], "Achievements.Medal": {"$ne": None}, "Team": team})
        for i in result2:
            lista.append(i)
    return lista, 3


def query4(team, year):  # -- Calcola quante medaglie sono state vinte da una data nazione nelle 2 diverse stagioni per uno specifico anno
    # team = "Italy - year = 1992
    summerMedals = 0
    winterMedals = 0
    summerEvents = db.event.find({"Year": year, "Season": "Summer"}, {"_id": 0, "IDEvent": 1})
    winterEvents = db.event.find({"Year": year, "Season": "Winter"}, {"_id": 0, "IDEvent": 1})
    queries = []

    for event in summerEvents:
        result = db.athlete.find({"Team": team, "Achievements.IDEvent": event["IDEvent"], "Achievements.Medal": {"$ne": None}})
        queries.append(result)

    for queryRes in queries:
        summerMedals += queryRes.count()

    queries = []
    for event in winterEvents:
        result = db.athlete.find({"Team": team, "Achievements.IDEvent": event["IDEvent"], "Achievements.Medal": {"$ne": None}})
        queries.append(result)

    for queryRes in queries:
        winterMedals += queryRes.count()
    return [summerMedals, winterMedals], 4
    #print("Summer: " + str(summerMedals) + ", Winter: " + str(winterMedals))


def query5(nomeEvento, annoEvento, cittàEvento, season): # -- Mostra tutte le medaglie vinte in un dato evento e gli atleti che le hanno vinte;
    #nomeEvento = "Judo Men's Extra-Lightweight" annoEvento = 2012  cittàEvento = "London" season = "Summer"
    result = db.event.aggregate([
        {"$match": {
                "EventName": nomeEvento,
                "Year": annoEvento,
                "City": cittàEvento,
                "Season": season
        }},
        {"$lookup": {
            "from": "athlete",
            "localField": "IDEvent",
            "foreignField": "Achievements.IDEvent",
            "as": "lista"

        }},
        {"$limit": 5}
    ])

    lista2 = []
    for r in result:
        for item in r["lista"]:
            for medal in item["Achievements"]:
                if medal["Medal"] is not None:
                    lista2.append(item)

    return lista2, 5


def query6(nazione):  # -- Elabora un grafico a torta degli sport in cui una data nazione va meglio
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


def query7(nomeEvento, annoEvento, cittàEvento, stagioneEvento): # -- Mostra il totale delle medaglie attinenti a un dato evento per ogni nazione
    #nomeEvento = "Cross Country Skiing Men's 10 kilometres" annoEvento = 1992 cittàEvento = "Albertville" stagioneEvento = "Winter"
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
    return diz, 7


def query8(annoInf, annoSup, tipoGrafico): # -- Elabora un istogramma delle 5 nazioni che negli ultimi tot anni hanno vinto più medaglie;
    result = db.event.aggregate([
        {"$match": {
                        "Year": {"$gte": annoInf, "$lte": annoSup}
                        #"Year": {"$lte": annoSup}
        }},
        {"$lookup": {
            "from": "athlete",
            "localField": "IDEvent",
            "foreignField": "Achievements.IDEvent",
            "as": "lista"

        }}
    ])

    resultMap = {}
    for r in result:
        for item in r["lista"]:
            if item["Team"] not in resultMap.keys():
                lisMedal = [0, 0, 0, 0]
                resultMap[item["Team"]] = lisMedal

                for medal in item["Achievements"]:
                    if medal["Medal"] is not None:
                        resultMap[item["Team"]][3] += 1
                        #print("1. Anno ", item["Year"])
                        if medal["Medal"] == "Gold":
                            resultMap[item["Team"]][0] += 1
                        elif medal["Medal"] == "Silver":
                            resultMap[item["Team"]][1] += 1
                        elif medal["Medal"] == "Bronze":
                            resultMap[item["Team"]][2] += 1
            else:
                for medal in item["Achievements"]:
                    if medal["Medal"] is not None:
                        resultMap[item["Team"]][3] += 1
                        #print("Anno ", item["Year"])
                        if medal["Medal"] == "Gold":
                            resultMap[item["Team"]][0] += 1
                        elif medal["Medal"] == "Silver":
                            resultMap[item["Team"]][1] += 1
                        elif medal["Medal"] == "Bronze":
                            resultMap[item["Team"]][2] += 1

    y = 4

    if tipoGrafico == "Gold":
        y = 0
        z = "d'oro"
    elif tipoGrafico == "Silver":
        y = 1
        z = "d'argento"
    elif tipoGrafico == "Bronze":
        z = "di bronzo"
        y = 2
    elif tipoGrafico == "Total":
        z = "totali"
        y = 3
    if y == 4:
        print("il valore inserito non è corretto")
    else:
        for key, value in resultMap.items():
            if value[0] == 0:
                mapOrder = sorted(resultMap.items(), key=lambda x: x[1][y], reverse=True)
        medaglie = []
        nazioni = []
        i = 0
        for key, value in mapOrder:
            if i < 6:
                medaglie.append(value[y])
                nazioni.append(key)
                i += 1
        # GENERO L'ISTOGRAMMA
        plt.style.use('ggplot')
        plt.title("Nazioni che hanno vinto più medaglie "+z+" dal " + str(annoInf) + " al " + str(annoSup))
        plt.bar(range(len(medaglie)), medaglie, align='center', edgecolor="black")
        plt.xlabel('Nazioni')
        plt.ylabel('# Medaglie vinte')
        plt.xticks(range(len(nazioni)), nazioni)
        plt.show()


def query9(sex): # -- Riporta per ogni anno il numero di partecipazioni di atleti di uno specifico sesso
    queryResult = db.athlete.aggregate([
        {"$match": {
            "Sex": sex
        }},
        {"$lookup": {
            "from": "event",
            "localField": "Achievements.IDEvent",
            "foreignField": "IDEvent",
            "as": "participation"
        }}
    ])

    yearMap = {}
    for result in queryResult:
        for event in result["participation"]:
            if event["Year"] not in yearMap.keys():
                yearMap[event["Year"]] = 1
            else:
                yearMap[event["Year"]] += 1

    """for key in sorted(yearMap):
        print("%s: %s" % (key, yearMap[key]))"""
    return yearMap, 9


def query10():  # Riporta gli atleti che hanno vinto almeno tot medaglie
    med = 3
    queryResult = db.athlete.find({"Achievements": {"$size": med}, "Achievements.Medal": {"$ne": None}})
    return queryResult, 10


def ultimoAnno():
    result = db.event.find({}, {"Year": 1, "_id": 0}).sort("Year", -1).limit(1)
    for r in result:
        return int(r["Year"])
