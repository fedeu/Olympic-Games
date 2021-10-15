import pandas as pd
from pymongo import MongoClient
import json
import csv

dbName = "ProvaDB"
clientUrl = "mongodb+srv://"
client = MongoClient(clientUrl)
db = client[dbName]

def popolaDB(csvPath, collectionName):
    coll = db[collectionName]
    data = pd.read_csv(csvPath)
    payload = json.loads(data.to_json(orient='records'))
    coll.remove()
    coll.insert(payload)
    print(coll.count())


if __name__ == "__main__":

    # GESTIONE CSV per le collection ATLETA, EVENTO, MEDAGLIA
    rootPath = "C:/Users/feder/Documents/Università/Magistrale/Basi di dati 2/progetto/dataset/"
    dataAE = pd.read_csv(rootPath + "athlete_events.csv")

    # da saltare quando hai già tolto Games
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
                if ',' in eventX: # Alcune specialità trascrivono i numeri in 1,000 anziché 1000: ciò crea problemi per pandas col csv, perciò rimuove le virgole
                    eventX = eventX.replace(',', '')
                diz[eventX + "," + row[1] + "," + row[2] + "," + row[3]] = "EV" + str(
                    index)  # il dizionario assicura l'unicità di ciascun evento
                index += 1

    eventLines = [["EventName", "Year", "City", "Season", "IDEvent"]]  # Label delle colonne
    for eventinfo, idevent in diz.items():
        itemOfLines = eventinfo.split(',')
        itemOfLines.append(idevent)
        eventLines.append(itemOfLines)

    # da saltare quando hai già ricavato il file event
    with open(rootPath + "event_info.csv", 'w', newline="") as writefile:  # Trascrive nel csv i dati ottenuti da Evento
        writer = csv.writer(writefile)
        writer.writerows(eventLines)

    # INSERIMENTO ID-EVENTO IN ATHLETE.CSV
    medalLines = [['Medal', 'Sport', 'IDEvent', 'IDAthlete']]  # Label delle colonne
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
            medalLines.append([row[13], row[11], diz[keyForDictEvent], row[0]])

    # CREAZIONE CSV MEDAGLIA
    with open(rootPath + "medal_info1.csv", "w", newline="") as writefile:
        writer = csv.writer(writefile)
        writer.writerows(medalLines)

    dfAthlete = pd.read_csv(rootPath + "athlete_events1.csv")
    attributesToDrop = ["Year", "Season", "City", "Sport", "Event", "Medal"]
    for attribute in attributesToDrop:
        dfAthlete.drop(attribute, inplace=True, axis=1)

    dfAthlete = dfAthlete.drop_duplicates() # elimina le occorrenze ripetute di atleta, dovute inizialmente alla competizione per più medaglie
    dfAthlete.to_csv(rootPath + "athlete_info.csv", index=False)

    # CARICAMENTO SU MONGODB - da saltare quando hai già caricato tutto
    popolaDB(rootPath + "athlete_info.csv", "athlete")
    popolaDB(rootPath + "event_info.csv", "event")
    popolaDB(rootPath + "medal_info1.csv", "achievement")
    
    #AGGIUNTA INDICE ID AD ATLETA
    resp = db.athlete.create_index([("ID", 1)])
    print("index response:", resp)

    # EMBED MEDAL in EVENT sotto forma di array - PRIMA DI FARE QUESTA COSA CONVIENE AGGIUNGERE GLI INDICI!!!
    allMedals = db.medal.find({}, {"_id": 0})
    db.athlete.update_many({}, {"$set": {"Medals": []}}) #da saltare se già fatto
    for medal in allMedals:
        db.athlete.update_one({"ID": medal["IDAthlete"]}, {"$push": {"Medals": {i: medal[i] for i in medal if i != "IDAthlete"}}})

    print(db.athlete.find_one({'ID': 5}))

    # DROP MEDAL COLLECTION
    db.medal.drop()
