from tkinter import *
from tkinter.ttk import *
import pymongo.cursor
from QueryDb import *
from load_db import checkInizializza
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


queries = ["Mostra gli eventi che ha ospitato una data città",
           "Visualizza altezza, peso ed età degli atleti che hanno vinto una medaglia per una data disciplina",
           "Mostra le medaglie vinte da un team in un dato anno",
           "Calcola quante medaglie sono state vinte da una data nazione nelle 2 diverse stagioni per uno specifico anno",
           "Mostra tutte le medaglie vinte in un dato evento e gli atleti che le hanno vinte",
           "Elabora un grafico a torta degli sport in cui una data nazione va meglio",
           "Mostra le nazioni vincitrici di una data competizione",
           "Elabora un istogramma delle 5 nazioni che hanno vinto più medaglie in un dato intervallo di anni",
           "Per ogni anno riporta il numero di partecipazioni di atleti di un dato sesso",
           "Riporta gli atleti che hanno vinto almeno una certa quantità di medaglie",
           "Inserisci un atleta", "Modifica un atleta", "Rimuovi un atleta",
           "Inserisci un evento", "Modifica un evento", "Rimuovi un evento",
           "Inserisci una medaglia", "Modifica una medaglia", "Rimuovi una medaglia"]


class Window(Tk):

    def __init__(self):
        super().__init__()
        # Import the sun-valley.tcl file to use theme
        self.tk.call("source", "./Sun-Valley-ttk-theme-master/sun-valley.tcl")
        # Then set the theme you want with the set_theme procedure
        self.tk.call("set_theme", "dark")
        self.configure(background='#4D9D8B')
        self.geometry('1250x750')
        self.title('Olympic History')
        self.iconbitmap("olympics.ico")

        # style for widgets: label error and label not found
        styleError = Style()
        styleError.configure("Error.Message.TLabel", foreground="red", background="#fff")
        correctStyle = Style()
        correctStyle.configure("BW.TLabel", foreground="green", background="#fff")

        # Menubutton
        self.menu_button = Menubutton(self, text='Seleziona una query', width=100)
        self.selected_query = IntVar()
        self.selected_query.trace("w", self.menu_item_selected)
        self.create_menu_button()

        # Frames
        self.inputFrame = Frame(self, relief=GROOVE, borderwidth=1)
        self.outputFrame = Frame(self, width=900, height=600, relief=GROOVE, borderwidth=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.outputFrame.rowconfigure(0, weight=1)
        self.outputFrame.columnconfigure(0, weight=1)

        # Create widgets and variables for input area
        self.labelsAndEntries = {}
        self.radioVar = StringVar()
        self.radioMedal = StringVar()
        self.createLabelsAndEntries()
        self.labelError = Label(self, text="", style="BW.TLabel")
        self.subtmitbtn = Button(self, text="Esegui", command=self.callQuery)

        # Create widgets and variables for output area
        self.tree = Treeview(self.outputFrame)
        self.labelNotFound = Label(self.outputFrame, text="")
        self.canvas = None


    def checkInput(self, key):
        """Checks if input is in the correct format. Returns None if not"""
        entry = self.labelsAndEntries[key][1]
        inputField = None
        # Get radiobutton value
        if key == "Sesso" or key == "Medaglia":
            if key == "Sesso":
                inputField = self.radioVar.get()
            elif key == "Medaglia":
                inputField = self.radioMedal.get()
        else:
            inputField = entry.get()
            if key == "Anno" or key == "Anno1" or key == "Anno2" or key == "Quantità" or key == "Età" or key == "ID":  # check on integers
                try:
                    inputField = int(inputField)
                except:
                    return None
                if key == "Quantità" and inputField < 1:
                    inputField = None
            elif key == "Peso" or key == "Altezza": # check on float
                try:
                    inputField = float(inputField)
                except:
                    return None
            elif key == "Stagione":
                if inputField != "Winter" and inputField != "Summer":
                    inputField = None
            elif key == "IDEvent":
                if len(inputField) > 3 and inputField[:2] != "EV":
                    inputField = None
            elif key == "Medal" and inputField != "Gold" and inputField != "Silver" and inputField != "Bronze" and inputField != "":
                inputField = "!" # error message for wrong medal
            else:  # check on strings
                if inputField is None:
                    return None
                special_characters = "\"!@#$%^&*()+?_=<>/\""
                if any(c in special_characters for c in inputField):# check on special characters
                    inputField = None
                elif all(c in " " for c in inputField): # check on string full of blank spaces
                    inputField = None
                if  inputField is not None and key != "Sport" and key != "Evento":  # check on numbers
                    numbers = "0123456789"
                    if any(c in numbers for c in inputField):
                        inputField = None
                if inputField is not None and key == "NOC" and len(inputField) != 3:
                    inputField = None
        return inputField


    def callQuery(self):
        """Get value from the input form and query the db"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.pack_forget()
        errorText = update_op = ""
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
        elif val == 4 or val == 6 or val == 13 or val == 14:
            evento = self.checkInput("Evento")
            anno = self.checkInput("Anno")
            citta = self.checkInput("Città")
            season = self.checkInput("Stagione")
            if val == 14:
                idEvento = self.checkInput("IDEvent")

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
                elif val == 13:
                    res = insertEvent(evento, anno, citta, season)
                    if res is None:
                        errorText = "Operazione fallita. Riprova."
                    else:
                        update_op = "Inserimento completato."
                else:
                    if checkEvento(idEvento) is not None:
                        res = upDateEvent(idEvento, evento, anno, citta, season)
                        if res is None:
                            errorText = "Operazione fallita. Riprova."
                        else:
                            update_op = "Modifica completata."
                    else:
                        errorText = "Evento non trovato nel database"
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
            elif int(anno1) > int(anno2):
                errorText = "Anno1 deve essere inferiore ad Anno2"
            else:
                res, numQuery = query8(anno1, anno2, medaglia)
        elif val == 8:
            sesso = self.checkInput("Sesso")
            res, numQuery = query9(sesso)
        elif val == 9:
            quant = self.checkInput("Quantità")
            if quant is None:
                errorText = "Inserisci una quantità numerica e maggiore di 0"
            else:
                res, numQuery = query10(quant)
        elif val == 10 or val == 11:
            nome = self.checkInput("Nome")
            sesso = self.checkInput("Sesso")
            eta = self.checkInput("Età")
            altezza = self.checkInput("Altezza")
            peso = self.checkInput("Peso")
            team = self.checkInput("Team")
            noc = self.checkInput("NOC")
            idAthlete = None
            if val == 11:
                idAthlete = self.checkInput("ID")
                if idAthlete is None:
                    errorText = "Inserisci un ID corretto - L'ID deve essere numerico"
                else:
                    if checkIdAthlete(idAthlete) is None:
                        errorText = "Inserisci un ID corretto - ID non trovato nel db"
            # show errors
            if nome is None:
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
            else:
                atleta = {"ID": idAthlete, "Name": nome, "Sex": sesso, "Age": eta, "Height": altezza, "Weight": peso, "NOC": noc, "Team": team}
                if val == 10:
                    medaglia = self.checkInput("Medal")
                    sport = self.checkInput("Sport")
                    idEvent = self.checkInput("IDEvent")
                    if sport is None:
                        errorText = "Inserisci uno sport corretto"
                    elif idEvent is None:
                        errorText = "Inserisci un id evento corretto - Deve iniziare per EV e contenere caratteri numerici"
                    elif medaglia == "!":
                        errorText = "Inserisci una medaglia corretta - Gold/Silver/Bronze/null"
                    else:
                        if medaglia == "":
                            medaglia = None
                        if checkEvento(idEvent) is None:
                            errorText = "Inserisci un id evento corretto - ID non trovato nel db"
                        else:
                            achievements = {"Medal": medaglia, "Sport": sport, "IDEvent": idEvent}
                            res = insertAthlete(atleta, achievements)
                            if res is None:
                                errorText = "Operazione fallita. Riprova."
                            else:
                                update_op = "Inserimento completato."
                elif val == 11:
                    if checkIdAthlete(idAthlete) is None:
                        errorText = "Inserisci un id atleta corretto - ID non presente nel db"
                    else:
                        res = upDateAthlete(idAthlete, nome, sesso, eta, altezza, peso, team, noc)
                        if res is None:
                            errorText = "Operazione fallita. Riprova."
                        else:
                            update_op = "Modifica completata."
        elif val == 12:
            idAthlete = self.checkInput("ID")
            if idAthlete is None:
                errorText = "Inserisci un ID corretto - L'ID deve essere numerico"
            elif checkIdAthlete(idAthlete) is None:
                errorText = "Inserisci un ID corretto - ID non presente nel db"
            else:
                res = deleteAthlete(idAthlete)
                if res is None:
                    errorText = "Operazione fallita. Riprova."
                else:
                    update_op = "Cancellazione completata."
        elif val == 15:
            idEvent = self.checkInput("IDEvent")
            if idEvent is None:
                errorText = "Inserisci un id evento corretto - Deve iniziare per EV e contenere caratteri numerici"
            else:
                if checkEvento(idEvent) is None:
                    errorText = "Inserisci un id evento corretto - L'evento non è presente sul db"
                else:
                    res = deleteEvent(idEvent)
                    if res is None:
                        errorText = "Operazione fallita. Riprova."
                    else:
                        update_op = "Cancellazione completata."
        elif val == 16 or val == 17:
            idAthlete = self.checkInput("ID")
            medaglia = self.checkInput("Medal")
            sport = self.checkInput("Sport")
            idEvent = self.checkInput("IDEvent")
            if idAthlete is None:
                errorText = "Inserisci un ID corretto - L'ID deve essere numerico"
            elif idEvent is None:
                errorText = "Inserisci un id evento corretto - Deve iniziare per EV e contenere caratteri numerici"
            elif sport is None:
                errorText = "Inserisci uno sport corretto"
            elif medaglia == "!":
                errorText = "Inserisci una medaglia corretta - Gold/Silver/Bronze/null"

            if checkEvento(idEvent) is not None:
                if medaglia == "":
                    medaglia = None
                achievement = {"Medal": medaglia, "Sport": sport, "IDEvent": idEvent}
                if val == 16:
                    res = insertAchievement(idAthlete, achievement)
                else:
                    res = updateAchievements(idAthlete, achievement)
                if res is None:
                    errorText = "Operazione fallita. Riprova."
                else:
                    update_op = "Aggiornamento completato."
            else:
                errorText = "Inserisci un id evento corretto - ID non trovato"
        elif val == 18:
            idAthlete = self.checkInput("ID")
            idEvent = self.checkInput("IDEvent")
            if idAthlete is None:
                errorText = "Inserisci un ID corretto - L'ID deve essere numerico"
            elif idEvent is None:
                errorText = "Inserisci un id evento corretto - Deve iniziare per EV e contenere caratteri numerici"
            elif checkEvento(idEvent) is not None:
                res = deleteAchievement(idAthlete, idEvent)
                if res is None:
                    errorText = "Operazione fallita. Riprova."
                else:
                    update_op = "Cancellazione completata."
            else:
                errorText = "Inserisci un id evento corretto - Deve iniziare per EV e contenere caratteri numerici"

        if errorText != "":
            self.labelError.config(text=errorText, style="Error.Message.TLabel")
            self.labelError.grid(row=3, column=0, padx=1, pady=4)
        elif update_op != "":
            self.labelError.config(text=update_op, style="BW.TLabel")
            self.labelError.grid(row=3, column=0, padx=1, pady=4)
        else:
            self.labelError.grid_remove()
            if res is not None and numQuery != 0:
                self.showResults(res, numQuery)


    def displayPlot(self, fig):
        """Used by query 6 and 8 to display histogram and pie chart"""
        if self.canvas is not None:
            for item in self.canvas.get_tk_widget().find_all():
                self.canvas.get_tk_widget().delete(item)
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.outputFrame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


    def createLabelsAndEntries(self):
        """Create widgets and a dictionary to group them"""
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
        self.radioVar.set("M")

        radiobtnTotal = Radiobutton(self.inputFrame, text="Total", variable=self.radioMedal,
                                    value="Total", command=self.checkInput)
        radiobtnGold = Radiobutton(self.inputFrame, text="Gold", variable=self.radioMedal,
                                   value="Gold", command=self.checkInput)
        radiobtnSilver = Radiobutton(self.inputFrame, text="Silver", variable=self.radioMedal,
                                     value="Silver", command=self.checkInput)
        radiobtnBronze = Radiobutton(self.inputFrame, text="Bronze", variable=self.radioMedal,
                                     value="Bronze", command=self.checkInput)
        self.radioMedal.set("Total")

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
        entry.focus_set() # gets the focus on the 1st entry in the form
        self.subtmitbtn.grid(row=2, column=0, pady=5)
        self.bind('<Return>', lambda event: self.callQuery()) # Press enter key to execute query

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
        self.labelError.grid_remove()
        self.labelNotFound.pack_forget()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.pack_forget()
        if self.canvas is not None:
            self.canvas.get_tk_widget().pack_forget()
            self.outputFrame.grid_remove()


    def menu_item_selected(self, *args):
        """ handle menu selected event """
        self.inputFrame.grid(row=1, column=0, padx=10, pady=10)
        val = int(self.selected_query.get())
        self.menu_button.config(text=queries[val])
        self.hideFields()
        if val == 0:
            self.showFields("Città", 0)
        elif val == 1:
            self.showFields("Sport", 0)
        elif val == 2 or val == 3:
            self.showFields("Team", 0)
            self.showFields("Anno", 1)
        elif val == 4 or val == 6 or val == 13 or val == 14:
            self.showFields("Evento", 0)
            self.showFields("Città", 1)
            self.showFields("Anno", 2)
            self.showFields("Stagione", 3)
            if val == 14:
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
            else:
                self.showFields("ID", 0)
        elif val == 12:
            self.showFields("ID", 0)
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


    def showResults(self, results, numQuery):
        """Arrange widgets in the output area"""
        self.labelNotFound.pack_forget()
        self.outputFrame.grid(row=4, columnspan=4, padx=10, pady=10, sticky=E+W+N+S)
        # Check on length of results: if 0 show label for no result
        if (type(results) is list and len(results) == 0) or (type(results) is pymongo.cursor.Cursor and results.count() == 0) or (type(results) is dict and len(results.keys())==0):
            self.labelNotFound.config(text="Nessun risultato trovato")
            self.labelNotFound.pack(fill="both", expand=True)
        else:
            if numQuery == 6 or numQuery == 8:
                self.displayPlot(results)
                return
            # Setting columns for the result table
            if numQuery == 4:
                cols = ("Summer", "Winter")
            elif numQuery == 7:
                cols = ("Team", "Position")
            elif numQuery == 9:
                cols = ("Year", "Participation")
            else:
                cols = list(results[0].keys())   # get names of the attributes

            if numQuery == 3 or numQuery == 5:
                del cols[8]
                del cols[7]
                del cols[0]
            cols = tuple(cols)
            self.tree.config(col=cols, show="headings")
            for col in cols:
                self.tree.heading(col, text=col)
                minWidth = 0
                if col == "Sex" or col == "Height" or col == "Weight" or col == "NOC" or col == "Age" or col == "Year" or col == "ID":
                    width = 50
                elif col == "IDEvent":
                    width = 100
                elif col == "Achievements":
                    minWidth = 80
                    width = 320
                elif col == "EventName":
                    width = 250
                else:
                    width = 150
                self.tree.column(col, minwidth=minWidth, width=width)

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
                    allMedals = []
                    myValues = []
                    for col in cols:
                        if col != "Achievements":
                            if col == "Age" and result[col] is not None: # convert age from float to int. some athletes have age = null
                                result[col] = int(result[col])
                            myValues.append(result[col])
                        elif col == "Achievements":
                            for medal in result["Achievements"]: # Format medals
                                allMedals.append(medal["Medal"]+", "+medal["Sport"])
                            myValues.append(allMedals)
                    self.tree.insert("", "end", values=tuple(myValues))
            self.tree.pack(fill="both", expand=True) # Show results


    def create_menu_button(self):
        """ create a menu button for query selecting"""
        menu = Menu(self.menu_button, tearoff=False)
        numbers = [x for x in range(0, 19)]  # indexes for queries
        for number in numbers:
            menu.add_radiobutton(
                label=str(number + 1) + ". " + queries[number],
                value=number,
                variable=self.selected_query)
        # associate menu with the Menubutton
        self.menu_button["menu"] = menu
        self.menu_button.grid(row=0, column=0, padx=10, pady=10)


if __name__ == "__main__":
    #checkInizializza()
    window = Window()
    window.mainloop()
