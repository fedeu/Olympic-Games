from matplotlib import pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from load_db import db


def query1(city): # --- QUERY 1: Presa in input una città, mostrare gli eventi che ha ospitato
    queryResult = db.event.find({"City": city}, {"_id": 0, "IDEvent": 0, "City": 0})
    return queryResult, 1


def query2(sport):  # -- Visualizza altezza, peso ed età degli atleti che hanno vinto una medaglia per una data disciplina;
    queryResult = db.athlete.find(
        {"Achievements.Sport": sport, "Achievements.Medal": {"$ne": None}, "Height": {"$ne": None},
         "Weight": {"$ne": None}}, {"_id": 0, "NOC": 0})
    return queryResult, 2


def query3(team, year):  # -- Mostra le medaglie vinte da un team (nazione) in un dato anno
    result = db.event.aggregate([
        {"$match": {"Year": year}},
        {"$lookup": {
            "from": "athlete",
            "localField": "IDEvent",
            "foreignField": "Achievements.IDEvent",
            "as": "lista"
        }}
    ])

    # Elimino le medaglie nulle
    finalResult = {}
    for r in result:
        for item in r["lista"]:
            newMedaglia = []
            if item["Team"] == team:
                medaglia = item["Achievements"]
                for med in medaglia:
                    if med["Medal"] != None:
                        newMedaglia.append(med)
                temp = item
                temp["Achievements"] = newMedaglia
                if temp["Achievements"]:  # verifico se la lista Achievements è vuota
                    finalResult[temp["_id"]] = temp

    result = {}
    final = []
    for key, val in finalResult.items():
        if key not in result.keys():
            result[key] = val
            final.append(val)
    return final, 3


def query4(team, year):  # -- Calcola quante medaglie sono state vinte da una data nazione nelle 2 diverse stagioni per uno specifico anno
    seasons = ["Summer", "Winter"]
    medals = []
    for season in seasons:
        queries = []
        counter = 0
        events = db.event.find({"Year": year, "Season": season}, {"_id": 0, "IDEvent": 1})
        for event in events:
            result = db.athlete.find(
                {"Team": team, "Achievements.IDEvent": event["IDEvent"], "Achievements.Medal": {"$ne": None}})
            queries.append(result)
        for queryRes in queries:
            counter += queryRes.count()
        medals.append(counter)
    return [medals[0], medals[1]], 4


def query5(nomeEvento, annoEvento, cittàEvento, season): # -- Mostra tutte le medaglie vinte in un dato evento e gli atleti che le hanno vinte;
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
        }}
    ])

    #Elimino le medaglie nulle
    finalResult = {}
    for r in result:
        for item in r["lista"]:
            newMedaglia = []
            medaglia = item["Achievements"]
            for med in medaglia:
                if med["Medal"] is not None:
                    newMedaglia.append(med)
            temp = item
            temp["Achievements"] = newMedaglia
            if temp["Achievements"]:  # verifico se la lista Achievements è vuota
                finalResult[temp["_id"]] = temp
    result = {}
    final = []
    for key, val in finalResult.items():
        if key not in result.keys():
            result[key] = val
            final.append(val)
    return final, 5


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

    # GRAFICO A TORTA
    sports = list(resultMap.keys())[:10]
    medals = list(resultMap.values())[:10]

    colors = ("orange", "cyan", "yellow", "brown", "indigo", "beige", "green")  # Color parameters
    explode = (0.1, 0.1, 0.2, 0.3, 0.2, 0.2, 0.1, 0.1, 0.1, 0.0)
    wp = {'linewidth': 1, 'edgecolor': "black"}  # Wedge properties

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
    """# Adding legend
    ax.legend(wedges, sports,
              title="Sport",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))"""
    plt.setp(autotexts, size=6)
    ax.set_title(nazione)
    return fig, 6


def query7(nomeEvento, annoEvento, cittàEvento, stagioneEvento):  # -- Mostra le nazioni vincitrici di una data competizione
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
    idEvent = db.event.find_one({"EventName":nomeEvento, "Year":annoEvento, "City":cittàEvento, "Season":stagioneEvento}, {"_id":0, "IDEvent":1})
    diz = {}  # per contenere Nazione - TipoMedaglia
    for r in result:
        for item in r["participation"]:
            for achievement in item["Achievements"]:
                if achievement["Medal"] is not None and achievement["IDEvent"] == idEvent["IDEvent"]:
                    diz[item["Team"]] = achievement["Medal"]
    return diz, 7


def query8(annoInf, annoSup, tipoGrafico):  # -- Elabora un istogramma delle 5 nazioni che negli ultimi tot anni hanno vinto più medaglie;
    result = db.event.aggregate([
        {"$match": {
            "Year": {"$gte": annoInf, "$lte": annoSup}
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
        app = {}
        for key, value in mapOrder:
            if i < 6:
                medaglie.append(value[y])
                nazioni.append(key)
                app[key] = value
                i += 1
        # GENERO L'ISTOGRAMMA
        fig, ax = plt.subplots()
        ax.bar(range(len(medaglie)), medaglie)
        ax.set(title="Nazioni che hanno vinto più medaglie " + z + " dal " + str(annoInf) + " al " + str(annoSup),
               ylabel='# Medaglie vinte', xlabel='Nazioni')
        plt.xticks(range(len(nazioni)), nazioni)
        return fig, 8


def query9(sex):  # -- Riporta per ogni anno il numero di partecipazioni di atleti di uno specifico sesso
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
        for part in result["participation"]:
            if part["Year"] not in yearMap.keys():
                yearMap[part["Year"]] = 1
            else:
                yearMap[part["Year"]] += 1
    for key in sorted(yearMap):
        print("%s: %s" % (key, yearMap[key]))
    return yearMap, 9


def query10(numMed):  # Riporta gli atleti che hanno vinto almeno tot medaglie
    queryResult = db.athlete.find()
    finalResult = {}
    for item in queryResult:
        newMedaglia = []
        temp = item
        for med in item["Achievements"]:
            if med["Medal"] is not None:
                newMedaglia.append(med)
            temp["Achievements"] = newMedaglia
        if temp["Achievements"]:  # verifico se la lista Achievements non è vuota
            if temp["ID"] in finalResult:
                elemInDict = finalResult.get(temp["ID"])
                newMedaglia2 = elemInDict["Achievements"] + newMedaglia
                temp["Achievements"] = newMedaglia2
                finalResult[temp["ID"]] = temp
            else:
                finalResult[temp["ID"]] = temp
    final = []
    for kay, val in finalResult.items():
        count = 0
        for med in val["Achievements"]:
            count += 1
        app = val
        if count >= numMed:
            del app["_id"]
            del app["Age"]
            del app["Weight"]
            del app["Height"]
            medal = app["Achievements"]
            del app["Achievements"]
            app["NumMedWin"] = count
            app["Achievements"] = medal
            final.append(app)
    return final, 10


def ultimoAnno():
    result = db.event.find({}, {"Year": 1, "_id": 0}).sort("Year", -1).limit(1)
    for r in result:
        return int(r["Year"])


def insertEvent(eventName, year, city, season):
    idEvent = findMaxIDEvent() + 1
    db.event.insert_one({"EventName": eventName, "Year": year, "City": city, "Season": season, "IDEvent": "EV" + str(idEvent)})


def findMaxIDEvent():
    idEvent = db.event.find({}, {"IDEvent": 1, "_id": 0}).sort("IDEvent", -1).limit(1)
    for doc in idEvent:
        return int(((doc["IDEvent"])[2:])) + 1


def upDateEvent(idEvent, eventName, year, city, season):
    db.event.update_one({"IDEvent": idEvent},
                        {"$set": {"EventName": eventName, "Year": year, "City": city, "Season": season}})


def deleteEvent(idEvento):
    listaMedaglie = []
    listaAtleti = []

    resultQuery = db.athlete.find({"Achievements.IDEvent": idEvento}, {"_id": 0})
    for res in resultQuery:
        for medal in res["Achievements"]:
            if len(res["Achievements"]) == 1:
                listaAtleti.append(res["ID"])
            else:
                if medal["IDEvent"] == idEvento:
                    diz = {"ID": res["ID"], "IDEvent": medal["IDEvent"]}
                    listaMedaglie.append(diz)

        for atleti in listaAtleti:
            deleteAthlete(atleti)

        for medaglie in listaMedaglie:
            deleteAchievement(medaglie["ID"], medaglie["IDEvent"])

    db.event.delete_one({"IDEvent": idEvento})


def findMaxIDAthlete():
    idAthlete = db.athlete.find({}, {"ID": 1, "_id": 0}).sort("ID", -1).limit(1)
    for doc in idAthlete:
        return int(doc["ID"])


def checkEvento(idEvento):
    return db.event.find_one({"IDEvent": idEvento}, {"IDEvent": 1, "_id": 0})


def upDateAthlete(idAthlete, name, sex, age, height, weight, team, noc):
    db.athlete.update_one({"ID": id}, {
        "$set": {"ID": idAthlete, "Name": name, "Sex": sex, "Age": age, "Height": height, "Weight": weight,
                 "Team": team, "NOC": noc}})


def insertAthlete(athlete, achievements):
    idAthlete = findMaxIDAthlete() + 1
    db.athlete.insert_one({"ID": idAthlete, "Name": athlete["Name"], "Sex": athlete["Sex"], "Age": athlete["Age"],
                           "Height": athlete["Height"], "Weight": athlete["Weight"], "Team": athlete["Team"],
                           "NOC": athlete["NOC"]})
    if achievements is not None:
        db.athlete.update_many({"ID": idAthlete}, {"$push": {"Achievements": achievements}})


def checkIdAthlete(idAthlete):
    found = db.athlete.find_one({"ID": idAthlete}, {"IDEvent": 1, "_id": 0})
    return found


def deleteAthlete(idAthlete):
    db.athlete.delete_one({"ID": idAthlete})


def insertAchievement(idAthlete, achievements):
    db.athlete.update_many({"ID": idAthlete}, {"$push": {"Achievements": achievements}})


def deleteAchievement(idAthlete, idEvent):
    db.athlete.update({"ID": idAthlete, "Achievements.IDEvent": idEvent},
                      {"$pull": {"Achievements": {"IDEvent": idEvent}}})
    # check se achievements dell'atleta è vuoto: in tal caso, cancellare a cascata l'atleta


def updateAchievements(idAthlete, achievement):
    db.athlete.update_one(
        {"ID": idAthlete, "Achievements.IDEvent": achievement["IDEvent"]},
        {"$set": {
                "Achievements.$.Sport": achievement["Sport"],
                "Achievements.$.Medal": achievement["Medal"],
                "Achievements.$.IDEvent": achievement["IDEvent"]
            }
        })
