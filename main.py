from tkinter import *
from tkinter.ttk import *

import pymongo.cursor

from QueryDb import *

queries = ["Mostra gli eventi che ha ospitato una data città",
           "Visualizza altezza, peso ed età degli atleti che hanno vinto una medaglia per una data disciplina",
           "Mostra le medaglie vinte da un team in un dato anno",
           "Calcola quante medaglie sono state vinte da una data nazione nelle 2 diverse stagioni per uno specifico anno",
           "Mostra tutte le medaglie vinte in un dato evento e gli atleti che le hanno vinte",
           "Elabora un grafico a torta degli sport in cui una data nazione va meglio",
           "Mostra il totale delle medaglie attinenti a un dato evento per ogni nazione",
           "Elabora un istogramma delle 5 nazioni che hanno vinto più medaglie in un dato intervallo di anni",
           "Per ogni anno riporta il numero di partecipazioni di atleti di un dato sesso",
           "Riporta gli atleti che hanno vinto almeno una certa quantità di medaglie",
           "Inserisci un atleta", "Modifica un atleta", "Rimuovi un atleta",
           "Inserisci un evento", "Modifica un evento", "Rimuovi un evento",
           "Inserisci una medaglia", "Modifica una medaglia", "Rimuovi una medaglia"]


class Window(Tk):

    def __init__(self):
        super().__init__()
        self.configure(background='#FFEFD5')
        self.geometry('1250x750')
        self.title('Olympic History')

        # style for widgets
        styleError = Style()
        styleError.configure("BW.TLabel", foreground="red")

        # Menubutton
        self.selected_query = IntVar()
        self.selected_query.trace("w", self.menu_item_selected)
        self.create_menu_button()

        self.inputFrame = Frame(self, width=200, height=200, relief=GROOVE, borderwidth=1)
        self.outputFrame = Frame(self, width=400, height=500, relief=GROOVE, borderwidth=1)

        # Create widgets and variables for input area
        self.labelsAndEntries = {}
        self.radioVar = StringVar()
        self.radioMedal = StringVar()
        self.createLabelsAndEntries()
        self.labelError = Label(self, text="", style="BW.TLabel")
        self.subtmitbtn = Button(self, text="Esegui", command=self.callQuery)

        # Create widgets and variables for output area
        self.tree = Treeview(self.outputFrame)
        self.treeMedal = Treeview(self.outputFrame)
        self.labelNotFound = Label(self.outputFrame, text="")

    def checkInput(self, key):
        """Checks if input is in the correct format. Returns None if not"""
        entry = self.labelsAndEntries[key][1]

        # Get radiobutton value
        if key == "Sesso" or key == "Medaglia":
            if key == "Sesso":
                inputField = self.radioVar.get()
            elif key == "Medaglia":
                inputField = self.radioMedal.get()
        else:
            inputField = entry.get()
            if key == "Anno" or key == "Anno1" or key == "Anno2" or key == "Quantità" or key == "Età":  # check on integers
                try:
                    inputField = int(inputField)
                except:
                    inputField = None
            elif key == "Weight" or key == "Height": # check on float
                try:
                    inputField = float(inputField)
                except:
                    inputField = None
            elif key == "Stagione":
                if inputField != "Winter" or inputField != "Summer":
                    inputField = None
            elif key == "IDEvent":
                if len(entry) > 3:
                    if entry[:2] != "EV":
                        inputField = None
                else:
                    inputField = None
            elif key == "Medal":
                if inputField != "Gold" or inputField != "Silver" or inputField != "Bronze" or inputField != "":
                    inputField = None
            else:  # check on strings
                special_characters = "\"!@#$%^&*()+?_=<>/\""
                if any(c in special_characters for c in inputField):# check on special characters
                    inputField = None
                elif all(c in " " for c in inputField): # check on string full of blank spaces
                    inputField = None
                if inputField is not None and (key != "Sport" or key != "Evento"):  # check on numbers
                    numbers = "0123456789"
                    if any(c in numbers for c in inputField):
                        inputField = None
                if inputField is not None and key == "NOC" and len(inputField) != 3:
                    inputField = None
        return inputField


    def callQuery(self):
        if self.tree.grid_info() is not None:
            self.tree.grid_remove()
        if self.treeMedal.grid_info() is not None:
            self.treeMedal.grid_remove()
        errorText = ""
        val = int(self.selected_query.get())
        res = None
        numQuery = 0
        if val == 0:
            citta = self.checkInput("Città")
            if citta is not None:
                res, numQuery = query1(citta)
            else:
                errorText = "Inserisci una città valida"
        elif val == 1:
            sport = self.checkInput("Sport")
            if sport is not None:
                res, numQuery = query2(sport)
            else:
                errorText = "Inserisci uno sport valido"
        elif val == 2 or val == 3:
            team = self.checkInput("Team")
            anno = self.checkInput("Anno")
            if anno is None and team is None:
                errorText = "Inserisci dei parametri validi"
            elif team is None:
                errorText = "Inserisci un team valido"
            elif anno is None:
                errorText = "Inserisci un anno valido"

            if val == 2:
                res, numQuery = query3(team, anno)
            else:
                res, numQuery = query4(team, anno)
        elif val == 4 or val == 6 or val == 13:
            evento = self.checkInput("Evento")
            anno = self.checkInput("Anno")
            citta = self.checkInput("Città")
            season = self.checkInput("Stagione")
            if evento is None:
                errorText = "Inserisci un evento valido"
            elif anno is None:
                errorText = "Inserisci un anno valido"
            elif citta is None:
                errorText = "Inserisci una città valida"
            elif season is None:
                errorText = "Inserisci una stagione valida: Winter o Summer"
            else:
                if val == 4:
                    res, numQuery = query5(evento, anno, citta, season)
                elif val == 6:
                    res, numQuery = query7(evento, anno, citta, season)
                else:
                    # query 14
                    pass
        elif val == 5:
            team = self.checkInput("Team")
            if team is None:
                errorText = "Inserisci un team valido"
            else:
                res, numQuery = query6(team)
        elif val == 7:
            anno1 = self.checkInput("Anno1")
            anno2 = self.checkInput("Anno2")
            medaglia = self.checkInput("Medaglia")

            if anno1 is None:
                errorText = "Inserisci un anno valido come primo parametro"
            elif anno2 is None:
                errorText = "Inserisci un anno valido come secondo parametro"
            else:
                res = query8(anno1, anno2, medaglia)
        elif val == 8:
            sesso = self.checkInput("Sesso")
            res = query9(sesso)
        elif val == 9:
            quant = self.checkInput("Quantità")
            if quant is None:
                errorText = "Inserisci una quantità valida"
            else:
                res, numQuery = query10()
        elif val == 10 or val == 11:
            idAthlete = self.checkInput("ID")
            nome = self.checkInput("Nome")
            sesso = self.checkInput("Sesso")
            eta = self.checkInput("Età")
            altezza = self.checkInput("Altezza")
            peso = self.checkInput("Peso")
            team = self.checkInput("Team")
            noc = self.checkInput("NOC")
            # show errors
            if idAthlete is None:
                errorText = "Inserisci un ID corretto - L'ID deve essere numerico"
            elif nome is None:
                errorText = "Inserisci un nome corretto"
            elif eta is None:
                errorText = "Inserisci un'età corretta"
            elif altezza is None:
                errorText = "Inserisci un'altezza corretta - L'altezza deve essere in cm"
            elif peso is None:
                errorText = "Inserisci un peso corretto - Il peso deve essere in kg"
            elif team is None:
                errorText = "Inserisci un team corretto"
            elif noc is None:
                errorText = "Inserisci un NOC corretto - Il NOC deve essere di 3 caratteri"

            if val == 10:
                #medaglia = self.checkInput("Medal")
                sport = self.checkInput("Sport")
                idEvent = self.checkInput("IDEvent")
                if sport is None:
                    errorText = "Inserisci uno sport corretto"
                elif idEvent is None:
                    errorText = "Inserisci un id evento corretto - Deve iniziare per EV e contenere caratteri numerici"
                else:
                    # check su id evento + esegui query
                    pass
            elif val == 11:
                # esegui query
                pass
        elif val == 12:
            id = self.checkInput("ID")
            if id is None:
                errorText = "Inserisci un ID corretto - L'ID deve essere numerico"
            # query
        elif val == 14:
            pass
        elif val == 15:
            idEvent = self.checkInput("IDEvent")
            if idEvent is None:
                errorText = "Inserisci un id evento corretto - Deve iniziare per EV e contenere caratteri numerici"
            else:
                # query
                pass
        elif val == 16 or val == 17:
            idAthlete = self.checkInput("ID")
            medaglia = self.checkInput("Medal")
            sport = self.checkInput("Sport")
            idEvent = self.checkInput("IDEvent")
            if idAthlete is None:
                errorText = "Inserisci un ID corretto - L'ID deve essere numerico"
            elif idEvent is None:
                errorText = "Inserisci un id evento corretto - Deve iniziare per EV e contenere caratteri numerici"
                """elif medaglia is None:
                errorText = "Inserisci una medaglia corretta - Deve essere nulla o Gold/Silver/Bronze"""
            elif sport is None:
                errorText = "Inserisci uno sport corretto"

            if val == 16:
                # query
                pass
            else:
                #altra query
                pass

        if errorText != "":
            self.labelError.config(text=errorText)
            self.labelError.grid(row=3, column=1, padx=1, pady=4)
        else:
            self.showResults(res, numQuery)


    def createLabelsAndEntries(self):
        # ATHLETE
        labelID = Label(self.inputFrame, text="ID")
        labelAthleteName = Label(self.inputFrame, text="Nome")
        labelAge = Label(self.inputFrame, text="Età")
        labelHeight = Label(self.inputFrame, text="Altezza")
        labelWeight = Label(self.inputFrame, text="Peso")
        labelNoc = Label(self.inputFrame, text="NOC")
        labelTeam = Label(self.inputFrame, text="Team")
        labelSex = Label(self.inputFrame, text="Sesso")

        entryID = Entry(self.inputFrame)
        entryAthleteName = Entry(self.inputFrame)
        entryAge = Entry(self.inputFrame)
        entryHeight = Entry(self.inputFrame)
        entryWeight = Entry(self.inputFrame)
        entryNoc = Entry(self.inputFrame)
        entryTeam = Entry(self.inputFrame)

        # EVENT
        labelCity = Label(self.inputFrame, text="Città")
        labelEvent = Label(self.inputFrame, text="Evento")
        labelAnno = Label(self.inputFrame, text="Anno")
        labelSeason = Label(self.inputFrame, text="Stagione")
        labelIDEvent = Label(self.inputFrame, text="IDEvent")

        entryCity = Entry(self.inputFrame)
        entryEvent = Entry(self.inputFrame)
        entryAnno = Entry(self.inputFrame)
        entryIDEvent = Entry(self.inputFrame)
        entrySeason = Entry(self.inputFrame)

        # MEDAL
        labelMedal = Label(self.inputFrame, text="Medaglia")
        labelSport = Label(self.inputFrame, text="Sport")
        labelAnno1 = Label(self.inputFrame, text="Anno1")
        labelAnno2 = Label(self.inputFrame, text="Anno2")
        labelQuantity = Label(self.inputFrame, text="Quantità")
        labelTypeMedal = Label(self.inputFrame, text="Tipo medaglia")

        entryMedal = Entry(self.inputFrame)
        entrySport = Entry(self.inputFrame)
        entryAnno1 = Entry(self.inputFrame)
        entryAnno2 = Entry(self.inputFrame)
        entryQuantity = Entry(self.inputFrame)

        radiobtnM = Radiobutton(self.inputFrame, text="M", variable=self.radioVar,
                                value="M", command=self.checkInput)
        radiobtnF = Radiobutton(self.inputFrame, text="F", variable=self.radioVar, value="F", command=self.checkInput)

        radiobtnTotal = Radiobutton(self.inputFrame, text="Total", variable=self.radioMedal,
                                    value="Total", command=self.checkInput)
        radiobtnGold = Radiobutton(self.inputFrame, text="Gold", variable=self.radioMedal,
                                   value="Gold", command=self.checkInput)
        radiobtnSilver = Radiobutton(self.inputFrame, text="Silver", variable=self.radioMedal,
                                     value="Silver", command=self.checkInput)
        radiobtnBronze = Radiobutton(self.inputFrame, text="Bronze", variable=self.radioMedal,
                                     value="Bronze", command=self.checkInput)

        self.labelsAndEntries = {"Città": [labelCity, entryCity], "Sport": [labelSport, entrySport],
                                 "Team": [labelTeam, entryTeam], "Evento": [labelEvent, entryEvent],
                                 "Anno1": [labelAnno1, entryAnno1], "Quantità": [labelQuantity, entryQuantity],
                                 "Anno": [labelAnno, entryAnno], "Anno2": [labelAnno2, entryAnno2],
                                 "Sesso": [labelSex, radiobtnM, radiobtnF], "Stagione": [labelSeason, entrySeason],
                                 "Medaglia": [labelTypeMedal, radiobtnTotal, radiobtnGold, radiobtnSilver,
                                              radiobtnBronze], "Nome": [labelAthleteName, entryAthleteName],
                                 "Età": [labelAge, entryAge], "Altezza": [labelHeight, entryHeight],
                                 "Peso": [labelWeight, entryWeight], "NOC": [labelNoc, entryNoc],
                                 "ID": [labelID, entryID], "IDEvent": [labelIDEvent, entryIDEvent],
                                 "Medal": [labelMedal, entryMedal]}

    def showFields(self, key, riga):
        """Arrange labels and entries into the input frame"""
        label = self.labelsAndEntries[key][0]
        entry = self.labelsAndEntries[key][1]

        if len(self.labelsAndEntries[key]) == 3:  # to show the 2nd radio button of "Sesso"
            entry2 = self.labelsAndEntries[key][2]
            entry2.grid(row=riga, column=2, padx=2, pady=2)
        elif len(self.labelsAndEntries[key]) == 5: # to show the other radio button of "Medaglia"
            entry2 = self.labelsAndEntries[key][2]
            entry3 = self.labelsAndEntries[key][3]
            entry4 = self.labelsAndEntries[key][4]
            entry2.grid(row=riga, column=2, padx=2, pady=2)
            entry3.grid(row=riga, column=3, padx=2, pady=2)
            entry4.grid(row=riga, column=4, padx=2, pady=2)

        label.grid(row=riga, column=0, padx=2, pady=2)
        entry.grid(row=riga, column=1, padx=2, pady=2)
        entry.focus_set()
        self.subtmitbtn.grid(row=2, column=1, pady=5)

    def hideFields(self):
        """Hide already created fields to place the new ones"""
        for item in self.labelsAndEntries.values():
            if item == self.labelsAndEntries["Medaglia"]:
                item[3].grid_remove()
                item[4].grid_remove()
                item[2].grid_remove()
            elif item == self.labelsAndEntries["Sesso"]:
                item[2].grid_remove()
            item[0].grid_remove()
            item[1].grid_remove()
        #self.labelError.config(text="")
        self.labelError.grid_remove()
        #self.labelNotFound.config(text="")
        self.labelNotFound.grid_remove()
        self.tree.grid_remove()
        self.treeMedal.grid_remove()

    def menu_item_selected(self, *args):
        """ handle menu selected event """
        self.inputFrame.grid(row=1, column=1, padx=10, pady=10)
        val = int(self.selected_query.get())
        self.hideFields()
        if val == 0:
            self.showFields("Città", 0)
        elif val == 1:
            self.showFields("Sport", 0)
        elif val == 2 or val == 3:
            self.showFields("Team", 0)
            self.showFields("Anno", 1)
        elif val == 4 or val == 6 or val == 13:
            self.showFields("Evento", 0)
            self.showFields("Città", 1)
            self.showFields("Anno", 2)
            self.showFields("Stagione", 3)
            if val == 13:
                self.showFields("IDEvent", 4)
        elif val == 5:
            self.showFields("Team", 0)
        elif val == 7:
            self.showFields("Anno1", 0)
            self.showFields("Anno2", 1)
            self.showFields("Medaglia", 2)
        elif val == 8:
            self.showFields("Sesso", 0)
        elif val == 9:
            self.showFields("Quantità", 0)
        elif val == 10 or val == 11:
            self.showFields("ID", 0)
            self.showFields("Nome", 1)
            self.showFields("Sesso", 2)
            self.showFields("Età", 3)
            self.showFields("Altezza", 4)
            self.showFields("Peso", 5)
            self.showFields("Team", 6)
            self.showFields("NOC", 7)
            if val == 10:
                self.showFields("Medal", 8)
                self.showFields("Sport", 9)
                self.showFields("IDEvent", 10)
        elif val == 12:
            self.showFields("ID", 0)
        elif val == 14: # tutta la roba dell'evento ... forse?
            self.showFields("")
        elif val == 15:
            self.showFields("IDEvent", 0)
        elif val == 16 or val == 17:
            self.showFields("ID", 0)
            self.showFields("Medal", 1)
            self.showFields("Sport", 2)
            self.showFields("IDEvent", 3)
        elif val == 18:
            self.showFields("ID", 0)
            self.showFields("IDEvent", 1)


    def showNoResultLabel(self):
        self.labelNotFound.config(text="Nessun risultato trovato")
        self.labelNotFound.grid(row=0, column=0)


    def showResults(self, results, numQuery): # MANCANO LA QUERY 9 E QUELLE COI GRAFICI
        """Arrange widgets in the output area"""
        if self.labelNotFound.grid_info() is not None:
            self.labelNotFound.grid_remove()
        self.outputFrame.grid(row=4, columnspan=2, padx=10, pady=10)
        # Check on length of results: if not 0 display table
        if (type(results) is list and len(results) == 0) or (type(results) is pymongo.cursor.Cursor and results.count() == 0):
            self.showNoResultLabel()
        else:
            # Setting columns for the result table
            if numQuery == 4:
                cols = ("Summer", "Winter")
            elif numQuery == 7:
                cols = ("Team", "Medal counter")
            elif numQuery == 9:
                cols = ("Year", "Participation")
            else:
                cols = list(results[0].keys())   # get names of the attributes

            if numQuery == 3 or numQuery == 5:
                del cols[8]
                del cols[7]
                del cols[0]
                medals = []
            cols = tuple(cols)

            self.tree.config(col=cols, show="headings")
            for col in cols:
                if col != "Achievements" or (col == "Achievements" and numQuery == 2):
                    self.tree.heading(col, text=col)
                    if col == "Sex" or col == "Height" or col == "Weight" or col == "NOC" or col == "Age" or col == "Year":
                        self.tree.column(col, minwidth=0, width=50)
                    elif col == "Achievements":
                        self.tree.column(col, minwidth=50, width=300)
                    elif col == "EventName":
                        self.tree.column(col, minwidth=0, width=250)
                    else:
                        self.tree.column(col, minwidth=0, width=150)

            # Setting the treeview to display results
            if numQuery == 4:
                self.tree.insert("", "end", values=(results[0], results[1]))
            elif numQuery == 7:
                for key, value in results.items():
                    self.tree.insert("", "end", values=(key, value))
            elif numQuery == 9:
                for key in sorted(results):
                    self.tree.insert("", "end", values=(key, results[key]))
            else:
                for result in results:
                    if numQuery == 3 or numQuery == 5: # Getting medal data to create second table of results
                        for medal in result["Achievements"]:
                            medal["IDAthlete"] = result["ID"]
                            medals.append(medal)
                    myValues = []
                    for col in cols:
                        if col != "Achievements":
                            myValues.append(result[col])
                        elif col == "Achievements" and numQuery == 2:
                            for medal in result["Achievements"]: # Format medals
                                myValues.append("<"+medal["Medal"]+", "+medal["Sport"]+">")
                    self.tree.insert("", "end", values=tuple(myValues))

            # Show results
            self.tree.grid(row=1, columnspan=3, pady=2)

            if numQuery == 3 or numQuery == 5: # Create second table to display medals in detail
                cols = tuple(list(medals[0].keys()))
                self.treeMedal.config(col=cols, show="headings")
                for col in cols:
                    self.treeMedal.heading(col, text=col)

                for medal in medals:
                    myValues = []
                    for col in cols:
                        myValues.append(medal[col])
                    self.treeMedal.insert("", "end", values=tuple(myValues))
                self.treeMedal.grid(row=2, column=0, pady=2)


    def create_menu_button(self):
        """ create a menu button for query selecting"""
        menu_button = Menubutton(
            self,
            text='Seleziona una query', width=100)
        menu = Menu(menu_button, tearoff=False)

        numbers = [x for x in range(0, 19)]  # indexes for queries
        for number in numbers:
            menu.add_radiobutton(
                label=str(number + 1) + ". " + queries[number],
                value=number,
                variable=self.selected_query)

        # associate menu with the Menubutton
        menu_button["menu"] = menu
        menu_button.grid(row=0, column=0, padx=10, pady=10)


if __name__ == "__main__":
    window = Window()
    window.mainloop()
