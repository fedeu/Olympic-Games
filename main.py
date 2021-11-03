from tkinter import *
from tkinter.ttk import *

queries = ["Mostra gli eventi che ha ospitato una data città",
           "Visualizza altezza, peso ed età degli atleti che hanno vinto una medaglia per una data disciplina",
           "Mostra le medaglie vinte da un team in un dato anno",
           "Calcola quante medaglie sono state vinte da una data nazione nelle 2 diverse stagioni per uno specifico anno",
           "Mostra tutte le medaglie vinte in un dato evento e gli atleti che le hanno vinte",
           "Elabora un grafico a torta degli sport in cui una data nazione va meglio",
           "Mostra il totale delle medaglie attinenti a un dato evento per ogni nazione",
           "Elabora un istogramma delle 5 nazioni che hanno vinto più medaglie in un dato intervallo di anni",
           "Per ogni anno riporta il numero di partecipazioni di atleti di un dato sesso",
           "Riporta gli atleti che hanno vinto almeno una certa quantità di medaglie"]


class Window(Tk):

    def __init__(self):
        super().__init__()
        self.configure(background='#FFEFD5')
        self.geometry('750x500')
        self.title('Olympic History')

        # self.labell = Label(self.inputFrame, text="Ciaone", font=('helvetica', 15, 'bold'))

        # Menubutton variable
        self.selected_query = IntVar()
        self.selected_query.trace("w", self.menu_item_selected)

        # create the menu button
        self.create_menu_button()

        self.inputFrame = Frame(self, width=200, height=200, relief=GROOVE, borderwidth=1)
        self.inputFrame.grid(row=1, column=1, padx=10, pady=10)

        # Create labels and entries for input area - città, sport, team, evento, anno1, quantità (RIGA 1). anno, anno2 (riga2)
        self.labelsAndEntries = {}
        self.createLabelsAndEntries()
        self.subtmitbtn = Button(self, text="Esegui", command=self.callQuery)

    def checkInput(self, key):
        entry = self.labelsAndEntries[key][1]
        if key == "Anno" or key == "Anno1" or key == "Anno2" or key == "Quantità":
            try:
                input = int(entry.get())
            except:
                print("bucchì")

        elif key == "Sesso":
            input = entry.get()
            print(input)
        #else:

    def callQuery(self):
        val = int(self.selected_query.get())
        if val == 0:
            self.checkInput("Città")
        elif val == 1:
            self.checkInput("Sport")
        elif val == 2 or val == 3:
            self.checkInput("Team")
            self.checkInput("Anno")
        elif val == 4 or val == 6:
            self.checkInput("Evento")
        elif val == 5:
            self.checkInput("Team")
        elif val == 7:
            self.checkInput("Anno1")
            self.checkInput("Anno2")
        elif val == 8:
            self.checkInput("Sesso")
        elif val == 9:
            self.checkInput("Quantità")

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

        entryCity = Entry(self.inputFrame)
        entrySport = Entry(self.inputFrame)
        entryTeam = Entry(self.inputFrame)
        entryEvent = Entry(self.inputFrame)
        entryAnno1 = Entry(self.inputFrame)
        entryQuantity = Entry(self.inputFrame)

        entryAnno = Entry(self.inputFrame)
        entryAnno2 = Entry(self.inputFrame)

        radiobtnM = Radiobutton(self.inputFrame, text="M", variable=IntVar(),
                                value=0)  # Se variable = 0, il sesso scelto è M. Altrimenti F.
        radiobtnF = Radiobutton(self.inputFrame, text="F", variable=IntVar(), value=1)

        self.labelsAndEntries = {"Città": [labelCity, entryCity], "Sport": [labelSport, entrySport],
                                 "Team": [labelTeam, entryTeam], "Evento": [labelEvent, entryEvent],
                                 "Anno1": [labelAnno1, entryAnno1], "Quantità": [labelQuantity, entryQuantity],
                                 "Anno": [labelAnno, entryAnno], "Anno2": [labelAnno2, entryAnno2],
                                 "Sesso": [labelSex, radiobtnM, radiobtnF]}

    def showFields(self, key):
        label = self.labelsAndEntries[key][0]
        entry = self.labelsAndEntries[key][1]
        riga = 0
        if key == "Anno" or key == "Anno2":
            riga = 1
        label.grid(row=riga, column=0, padx=2, pady=2)
        entry.grid(row=riga, column=1, padx=2, pady=2)
        if len(self.labelsAndEntries[key]) == 3:
            entry2 = self.labelsAndEntries[key][2]
            entry2.grid(row=riga, column=2, padx=2, pady=2)
        self.subtmitbtn.grid(row=2, column=1, pady=5)

    def hideFields(self):
        for item in self.labelsAndEntries.values():
            if item == self.labelsAndEntries["Sesso"]:
                item[2].grid_remove()
            item[0].grid_remove()
            item[1].grid_remove()

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
        elif val == 5:
            self.showFields("Team")
        elif val == 7:
            self.showFields("Anno1")
            self.showFields("Anno2")
        elif val == 8:
            self.showFields("Sesso")
        elif val == 9:
            self.showFields("Quantità")

    def create_menu_button(self):
        """ create a menu button """
        # menu variable
        numbers = [x for x in range(0, 10)]

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
