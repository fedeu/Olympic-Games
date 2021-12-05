import pandas as pd
import json
import csv
from pymongo import MongoClient

dbName = "OlympicGames"
clientUrl = "*"
client = MongoClient(clientUrl)
db = client[dbName]


def popolaDB(csvPath, collectionName):
    print("Popopolando " + collectionName)
    coll = db[collectionName]
    data = pd.read_csv(csvPath)
    payload = json.loads(data.to_json(orient='records'))
    coll.remove()
    coll.insert(payload)
    print(coll.count())


def inizializzaDB():
    # GESTIONE CSV per le collection ATHLETE, EVENT, ACHIEVEMENT
    rootPath = "./dataset/"
    dataAE = pd.read_csv(rootPath + "athlete_events.csv")

    dataAE.drop("Games", inplace=True, axis=1)  # Cancella la colonna 'Games'
    dataAE.to_csv(rootPath + "athlete_events1.csv", index=False)

    # CREAZIONE CSV EVENTO
    dfEvent = dataAE[['Event', 'Year', 'City', 'Season']].copy()  # Crea dataframe contenente solo le info sull'evento
    dfEvent['IDEvent'] = None  # Aggiunge colonna per l'id dell'evento
    dfEvent.to_csv(rootPath + "event_info.csv", index=False)  # Converti dataframe in csv
    index = 0
    diz = {}
    with open(rootPath + "event_info.csv",
              'r') as readfile:  # Scorre il file e crea un id per l'evento, inserendolo in un dizionario
        reader = csv.reader(readfile)
        for row in reader:
            if row[0] == 'Event':  # Salta la prima riga che contiene i nomi degli attributi
                continue
            else:
                eventX = row[0]
                if ',' in eventX:  # Alcune specialità trascrivono i numeri in 1,000 anziché 1000: ciò crea problemi per pandas col csv, perciò rimuove le virgole
                    eventX = eventX.replace(',', '')
                diz[eventX + "," + row[1] + "," + row[2] + "," + row[3]] = "EV" + str(
                    index)  # il dizionario assicura l'unicità di ciascun evento
                index += 1

    eventLines = [["EventName", "Year", "City", "Season", "IDEvent"]]  # Label delle colonne
    for eventinfo, idevent in diz.items():
        itemOfLines = eventinfo.split(',')
        itemOfLines.append(idevent)
        eventLines.append(itemOfLines)

    with open(rootPath + "event_info.csv", 'w', newline="") as writefile:  # Trascrive nel csv i dati ottenuti da Evento
        writer = csv.writer(writefile)
        writer.writerows(eventLines)

    # INSERIMENTO ID-EVENTO IN ATHLETE.CSV
    medalLines = [['Medal', 'Sport', 'IDEvent', 'IDAthlete',
                   'AthleteAge']]  # Label delle colonne -- DEVO SALVARE ANCHE L'ETà DELL'ATLETA
    with open(rootPath + "athlete_events1.csv", "r") as readfile:
        reader = csv.reader(readfile)
        for row in reader:
            if row[0] == "ID":  # Salta la prima riga che contiene i nomi degli attributi
                continue
            # Ricostruisce la chiave per il dizionario, così da ricavarsi l'id creato in precedenza e inserirlo nel csv di Medal
            eventX = row[12]
            if ',' in eventX:
                eventX = eventX.replace(',', '')
            keyForDictEvent = "" + eventX + "," + (row[8]) + "," + (row[10]) + "," + row[9]
            medalLines.append([row[13], row[11], diz[keyForDictEvent], row[0], row[3]])

    # CREAZIONE CSV MEDAGLIA
    with open(rootPath + "medal_info1.csv", "w", newline="") as writefile:
        writer = csv.writer(writefile)
        writer.writerows(medalLines)

    dfAthlete = pd.read_csv(rootPath + "athlete_events1.csv")
    attributesToDrop = ["Year", "Season", "City", "Sport", "Event", "Medal"]
    for attribute in attributesToDrop:
        dfAthlete.drop(attribute, inplace=True, axis=1)

    dfAthlete = dfAthlete.drop_duplicates()  # elimina le occorrenze ripetute di atleta, dovute alla competizione per più medaglie
    dfAthlete.to_csv(rootPath + "athlete_info.csv", index=False)


    # CARICAMENTO SU MONGODB
    popolaDB(rootPath + "athlete_info.csv", "athlete")
    popolaDB(rootPath + "event_info.csv", "event")
    popolaDB(rootPath + "medal_info1.csv", "achievement")

    creaIndici()

    # Incorpora ACHIEVEMENT in EVENT sotto forma di array
    db.athlete.update_many({}, {"$set": {"Achievements": []}})  # Aggiungi l'attributo Achievements ad Athletes
    firstHalfOfAchievements = db.achievement.find({"IDAthlete": {"$lte": 60000}}, {"_id": 0}).sort("IDAthlete", 1)
    secondHalfOfAchievements = db.achievement.find({"IDAthlete": {"$gt": 60000, "$lte": 120000}}, {"_id": 0}).sort(
        "IDAthlete", 1)
    thirdHalfOfAchievements = db.achievement.find({"IDAthlete": {"$gt": 120000}}, {"_id": 0}).sort("IDAthlete", 1)
    insertAchievement(firstHalfOfAchievements)
    print("inserito first")
    insertAchievement(secondHalfOfAchievements)
    print("inserito second")
    insertAchievement(thirdHalfOfAchievements)
    print("inserito third")

    db.achievement.drop()
    creaIndiciAchievements()


def insertAchievement(achievements):
    for a in achievements:
        db.athlete.update_one({"ID": a["IDAthlete"], "Age": a["AthleteAge"]},
                              {"$push": {
                                  "Achievements": {i: a[i] for i in a if
                                                   i != "IDAthlete" and i != "AthleteAge"}}})


def creaIndici():
    # Indici per Athlete
    db.athlete.create_index([("ID", 1)])
    db.athlete.create_index([("Team", 1)])
    db.athlete.create_index([("Age", 1)])
    db.athlete.create_index([("Sex", 1)])
    db.athlete.create_index([("Name", 1)])
    db.athlete.create_index([("Height", 1)])
    db.athlete.create_index([("Weight", 1)])
    db.athlete.create_index([("NOC", 1)])

    # Indici per Achievement
    db.achievement.create_index([("IDAthlete", 1)])
    db.achievement.create_index([("IDEvent", 1)])
    db.achievement.create_index([("Sport", 1)])
    db.achievement.create_index([("Medal", 1)])
    db.achievement.create_index([("AthleteAge", 1)])

    # Indici per Event
    db.event.create_index([("EventName", 1)])
    db.event.create_index([("Year", 1)])
    db.event.create_index([("City", 1)])
    db.event.create_index([("Season", 1)])
    db.event.create_index([("IDEvent", 1)])


def creaIndiciAchievements():
    # Indici per Achievement embedded in Athlete
    db.athlete.create_index([("Achievements.Medal", 1)])
    db.athlete.create_index([("Achievements.Sport", 1)])
    db.athlete.create_index([("Achievements.IDEvent", 1)])

def checkInizializza():
    if dbName not in client.list_database_names():  # Se non trova il db, lo crea e carica il dataset
        inizializzaDB()
