from tkinter import *
from tkinter.ttk import *
from QueryDb import *

#RISOLVI QUERY 4
#AGGIUNGI QUERY DI INSERIMENTO/CANC/MOD

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
        self.geometry('750x500')
        self.title('Olympic History')

        # Menubutton variable
        self.selected_query = IntVar()
        self.selected_query.trace("w", self.menu_item_selected)

        # create the menu button
        self.create_menu_button()

        self.inputFrame = Frame(self, width=200, height=200, relief=GROOVE, borderwidth=1)
        self.inputFrame.grid(row=1, column=1, padx=10, pady=10)

        # Create labels and entries for input area - città, sport, team, evento, anno1, quantità (RIGA 1). anno, anno2 (riga2)
        self.labelsAndEntries = {}
        self.radioVar = IntVar()
        self.createLabelsAndEntries()
        self.labelError = Label(self, text="")
        self.labelError.grid(row=3, column=1, padx=1, pady=4)
        self.subtmitbtn = Button(self, text="Esegui", command=self.callQuery)




    def checkInput(self, key):
        """Checks if input is in the correct format"""
        if key is None:
            key = "Sesso"
        entry = self.labelsAndEntries[key][1]
        if key == "Anno" or key == "Anno1" or key == "Anno2" or key == "Quantità":  #check on integers
            try:
                inputField = int(entry.get())
            except:
                inputField = None
        elif key == "Sesso":
            inputField = self.radioVar.get()
        else:   # check on strings: special characters
            inputField = entry.get()
            special_characters = "\"!@#$%^&*()-+?_=,<>/\""

            if any(c in special_characters for c in inputField) or len(inputField) == 0:
                inputField = None
            if key == "Città" or key == "Team" or key == "Evento": # check on strings: numbers
                numbers = "0123456789"
                if any(c in numbers for c in inputField):
                    inputField = None
        return inputField

    def callQuery(self):
        self.labelError.config(text="")
        val = int(self.selected_query.get())
        if val == 0:
            città = self.checkInput("Città")
            if città is not None:
                #query1(città)
                pass
            else:
                self.labelError.config(text="Inserisci una città valida")
        elif val == 1:
            sport = self.checkInput("Sport")
            if sport is not None:
                query2(sport)
            else:
                self.labelError.config(text="Inserisci uno sport valido")
        elif val == 2 or val == 3:
            team = self.checkInput("Team")
            anno = self.checkInput("Anno")
            if anno is None and team is None:
                self.labelError.config(text="Inserisci dei parametri validi")
            elif team is None:
                self.labelError.config(text="Inserisci un team valido")
            elif anno is None:
                self.labelError.config(text="Inserisci un anno valido")

            if val == 2:
                pass
                #query3(team, anno)
            else:
                query4(team, anno)
        elif val == 4 or val == 6:
            evento = self.checkInput("Evento")
            anno = self.checkInput("Anno")
            città = self.checkInput("Città")
            season = self.checkInput("Stagione")
            if evento is None:
                self.labelError.config(text="Inserisci un evento valido")
            elif anno is None:
                self.labelError.config(text="Inserisci un anno valido")
            elif città is None:
                self.labelError.config(text="Inserisci una città valida")
            elif season is None:
                self.labelError.config(text="Inserisci una stagione valida")
            elif evento is not None and anno is not None and città is not None and season is not None:
                if val == 4:
                    pass
                    #query5(evento, anno, città, season)
                else:
                    query6(evento, anno, città, season)
        elif val == 5:
            team = self.checkInput("Team")
            if team is None:
                self.labelError.config(text="Inserisci un team valido")
            else:
                query6(team)
        elif val == 7:
            anno1 = self.checkInput("Anno1")
            anno2 = self.checkInput("Anno2")
            if anno1 is None:
                self.labelError.config(text="Inserisci un anno valido come primo parametro")
            elif anno2 is None:
                self.labelError.config(text="Inserisci un anno valido come secondo parametro")
            else:
                pass
                #query8(anno1, anno2)
        elif val == 8:
            sesso = self.checkInput("Sesso")
            query9(sesso)
        elif val == 9:
            quant = self.checkInput("Quantità")
            if quant is None:
                self.labelError.config(text="Inserisci una quantità valida")
            else:
                query10()

    def createLabelsAndEntries(self):
        labelCity = Label(self.inputFrame, text="Città")
        labelSport = Label(self.inputFrame, text="Sport")
        labelTeam = Label(self.inputFrame, text="Team")
        labelEvent = Label(self.inputFrame, text="Evento")
        labelAnno1 = Label(self.inputFrame, text="Anno1")
        labelQuantity = Label(self.inputFrame, text="Quantità")

        labelAnno = Label(self.inputFrame, text="Anno")
        labelAnno2 = Label(self.inputFrame, text="Anno2")
        labelSex = Label(self.inputFrame, text="Sesso")

        labelSeason = Label(self.inputFrame, text="Stagione")

        entryCity = Entry(self.inputFrame)
        entrySport = Entry(self.inputFrame)
        entryTeam = Entry(self.inputFrame)
        entryEvent = Entry(self.inputFrame)
        entryAnno1 = Entry(self.inputFrame)
        entryQuantity = Entry(self.inputFrame)

        entryAnno = Entry(self.inputFrame)
        entryAnno2 = Entry(self.inputFrame)

        entrySeason = Entry(self.inputFrame)


        radiobtnM = Radiobutton(self.inputFrame, text="M", variable=self.radioVar,
                                value=0, command=self.checkInput)  # Se variable = 0, il sesso scelto è M. Altrimenti F.
        radiobtnF = Radiobutton(self.inputFrame, text="F", variable=self.radioVar, value=1, command=self.checkInput)

        self.labelsAndEntries = {"Città": [labelCity, entryCity], "Sport": [labelSport, entrySport],
                                 "Team": [labelTeam, entryTeam], "Evento": [labelEvent, entryEvent],
                                 "Anno1": [labelAnno1, entryAnno1], "Quantità": [labelQuantity, entryQuantity],
                                 "Anno": [labelAnno, entryAnno], "Anno2": [labelAnno2, entryAnno2],
                                 "Sesso": [labelSex, radiobtnM, radiobtnF], "Stagione": [labelSeason, entrySeason]}

    def showFields(self, key):
        """Arrange labels and entries into the input frame"""
        label = self.labelsAndEntries[key][0]
        entry = self.labelsAndEntries[key][1]
        riga = 0
        if self.labelsAndEntries["Evento"][0].grid_info() is not None:
            if key == "Città":
                riga = 1
            elif key == "Anno":
                riga = 2
            elif key == "Stagione":
                riga = 3
        elif (self.labelsAndEntries["Team"][0].grid_info() is not None and key == "Anno") or self.labelsAndEntries["Anno1"][0].grid_info() is not None:
            riga = 1
        label.grid(row=riga, column=0, padx=2, pady=2)
        entry.grid(row=riga, column=1, padx=2, pady=2)
        if len(self.labelsAndEntries[key]) == 3:    # to show the 2nd radio button
            entry2 = self.labelsAndEntries[key][2]
            entry2.grid(row=riga, column=2, padx=2, pady=2)

        self.subtmitbtn.grid(row=2, column=1, pady=5)

    def hideFields(self):
        """hide already created fields to place the new"""
        for item in self.labelsAndEntries.values():
            if item == self.labelsAndEntries["Sesso"]:
                item[2].grid_remove()
            item[0].grid_remove()
            item[1].grid_remove()
        self.labelError.config(text="")

    def menu_item_selected(self, *args):
        """ handle menu selected event """
        val = int(self.selected_query.get())
        self.hideFields()
        if val == 0:
            self.showFields("Città")
        elif val == 1:
            self.showFields("Sport")
        elif val == 2 or val == 3:
            self.showFields("Team")
            self.showFields("Anno")
        elif val == 4 or val == 6:
            self.showFields("Evento")
            self.showFields("Città")
            self.showFields("Anno")
            self.showFields("Stagione")
        elif val == 5:
            self.showFields("Team")
        elif val == 7:
            self.showFields("Anno1")
            self.showFields("Anno2")
        elif val == 8:
            self.showFields("Sesso")
        elif val == 9:
            self.showFields("Quantità")
        elif val == 10:
            self.showFields("")
        elif val == 11:
            self.showFields("")
        elif val == 12:
            self.showFields("")
        elif val == 13:
            self.showFields("")
        elif val == 14:
            self.showFields("")
        elif val == 15:
            self.showFields("")
        elif val == 16:
            self.showFields("")
        elif val == 17:
            self.showFields("")
        elif val == 18:
            self.showFields("")


    def create_menu_button(self):
        """ create a menu button for query selecting"""
        numbers = [x for x in range(0, 19)]

        # create the Menubutton
        menu_button = Menubutton(
            self,
            text='Seleziona una query', width=100)

        # create a new menu instance
        menu = Menu(menu_button, tearoff=False)

        for number in numbers:
            menu.add_radiobutton(
                label=str(number + 1) + ". " + queries[number],
                value=number,
                variable=self.selected_query)

        # associate menu with the Menubutton
        menu_button["menu"] = menu
        menu_button.grid(row=0, column=1, padx=10, pady=10)


if __name__ == "__main__":
    window = Window()
    window.mainloop()
