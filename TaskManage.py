from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

from tkcalendar import DateEntry
from ttkthemes import ThemedStyle
import sqlite3
import matplotlib.pyplot as plt
import pyperclip

import numpy as np

root = Tk()
root.title('System zarządzania Ludźmi')
root.geometry("1600x700")
style = ThemedStyle(root)
style.set_theme('arc')

tabControl = Notebook(root)
peopleTab = Frame(tabControl, width=1200)
taskTab = Frame(tabControl)
chartsTab = Frame(tabControl)
peopleTab.grid(column=0, row=0, sticky='ns')
root.rowconfigure(0, weight=1)
tabControl.add(peopleTab, text='Ludzie')
tabControl.add(taskTab, text='Zadania')
tabControl.pack(expand=1, fill='both')

tree = Treeview(peopleTab, selectmode='browse', column=("column3", "column4", "column5", "column6", "column7", "column8", "column9", "column10"), show='headings')

tree.heading("#3", text="IMIE")
tree.heading("#4", text="NAZWISKO")
tree.heading("#5", text="IMIE_OJCA")
tree.heading("#6", text="PESEL")
tree.heading("#7", text="KOMORKA", command=lambda: sort(tree, '#7'))
tree.heading("#8", text="STANOWISKO")
tree.heading("#9", text="TELEFON")
tree.heading("#10", text="ID_ZADANIA")
tree.column("#3", width=100)
tree.column("#4", width=125)
tree.column("#5", width=125)
tree.column("#6", width=125)
tree.column("#7", width=125)
tree.column("#8", width=200)
tree.column("#9", width=125)
tree.column("#10", width=125)


def sort(tree, col):
    itemlist = list(tree.get_children(''))
    itemlist.sort(key=lambda x: tree.set(x, col))
    for index, iid in enumerate(itemlist):
        tree.move(iid, tree.parent(iid), index)


def Query():
    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute("SELECT * from People")
    records = c.fetchall()
    if tree.get_children() is not None:
        for i in tree.get_children():
            tree.delete(i)
    for people in records:
        tree.insert("", END, values=people)
    conn.commit()
    conn.close()


def DeletePeople():
    # Utworzenie połącznia
    conn = sqlite3.connect('people.db')

    # Utworzenie kursora
    c = conn.cursor()

    select = tree.selection()
    item = tree.item(select)["values"]
    peselSelected = item[5]

    c.execute("DELETE FROM People WHERE PESEL = (:index)",
              {
                  'index': peselSelected
              }
              )
    c.execute("DELETE FROM Tasks WHERE pesel = :index", {
        'index': peselSelected
    })

    Query()

    # Zatwierdź zmiany
    conn.commit()

    # Zakończ połączenie
    conn.close()


def AddPeople():
    top = Toplevel()
    top.title("Dodaj Osobę")
    top.geometry("600x400")

    imie = Entry(top, width=60)
    nazwisko = Entry(top, width=60)
    imie_ojca = Entry(top, width=60)
    pesel = Entry(top, width=60)
    komorka = Entry(top, width=60)
    stanowisko = Entry(top, width=60)
    telefon = Entry(top, width=60)

    l3 = Label(top, text="Imię")
    l3.pack()
    imie.pack()

    l4 = Label(top, text="Nazwisko")
    l4.pack()
    nazwisko.pack()

    l5 = Label(top, text="Imię ojca")
    l5.pack()
    imie_ojca.pack()

    l6 = Label(top, text="Pesel")
    l6.pack()
    pesel.pack()

    l7 = Label(top, text="Numer Komórki")
    l7.pack()
    komorka.pack()

    l8 = Label(top, text="Stanowisko")
    l8.pack()
    stanowisko.pack()

    l9 = Label(top, text="Numer Telefonu")
    l9.pack()
    telefon.pack()

    def onClick():
        conn = sqlite3.connect('people.db')
        c = conn.cursor()
        c.execute(
            "INSERT INTO People VALUES ( :imie, :nazwisko, :imie, :pesel, :komorka, :stanowisko, :telefon, 'None')",
            {
                'imie': imie.get(),
                'nazwisko': nazwisko.get(),
                'ojciec': imie_ojca.get(),
                'komorka': komorka.get(),
                'stanowisko': stanowisko.get(),
                'telefon': telefon.get(),
                'pesel': pesel.get()

            })
        conn.commit()
        conn.close()

    submit = Button(top, text="Dodaj", command=onClick)
    submit.pack()


def LoadData():
    goal.delete(0, END)
    squad.delete(0, END)
    personId.delete(0, END)
    corona.delete(0, END)
    froms.delete(0, END)
    tos.delete(0, END)

    select = tree2.selection()

    item = tree2.item(select)["values"]
    if item[5] == "TRUE":
        corona.set("TAK")
    elif item[5] == "FALSE":
        corona.set("NIE")
    goal.insert(0, item[0])
    squad.insert(0, item[1])
    personId.insert(0, item[2])
    tos.insert(0, item[6])
    froms.insert(0, item[7])


def ChangeTask():
    niceSelection = ""

    select = tree2.selection()

    item = tree2.item(select)["values"]

    if corona.get() == "TAK":
        niceSelection = "TRUE"
    elif corona.get() == "NIE":
        niceSelection = "FALSE"

    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute(
        "UPDATE Tasks SET zadanie = :goal, komorka_organizacyjna = :squad, angazacjaWirus = :wirus, OD=:od, DO=:do WHERE ID = :id",
        {
            'goal': goal.get(),
            'squad': squad.get(),
            'id': item[4],
            'wirus': niceSelection,
            'od': froms.get_date(),
            'do': tos.get_date()
        })
    conn.commit()
    conn.close()
    QueryTasks()


def OnEClickEdit(event):
    select = tree.selection()
    item = tree.item(select)["values"]
    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute("SELECT * from People WHERE PESEL = :pesel", {
        'pesel': item[5]
    })
    records = c.fetchone()
    top = Toplevel()
    top.title("Edytuj osobę")
    top.geometry("600x400")

    imie = Entry(top, width=60)
    nazwisko = Entry(top, width=60)
    imie_ojca = Entry(top, width=60)
    komorka = Entry(top, width=60)
    stanowisko = Entry(top, width=60)
    telefon = Entry(top, width=60)

    l3 = Label(top, text="Imię")
    l3.pack()
    imie.pack()
    imie.insert(0, records[2])
    l4 = Label(top, text="Nazwisko")
    l4.pack()
    nazwisko.pack()
    nazwisko.insert(0, records[3])
    l5 = Label(top, text="Imię ojca")
    l5.pack()
    imie_ojca.pack()
    imie_ojca.insert(0, records[4])
    l7 = Label(top, text="Numer kompanii")
    l7.pack()
    komorka.pack()
    komorka.insert(0, records[6])
    l8 = Label(top, text="Stanowisko")
    l8.pack()
    stanowisko.pack()
    stanowisko.insert(0, records[7])
    l9 = Label(top, text="Numer Telefonu")
    l9.pack()
    telefon.pack()
    telefon.insert(0, records[8])

    def onClick():
        c.execute(
            "UPDATE People SET IMIĘ = :imie, NAZWISKO = :nazwisko, IMIE_OJCA= :ojciec, Komórka = :komorka, STANOWISKO = :stanowisko, TELEFON = :telefon WHERE PESEL = :pesel",
            {

                'imie': imie.get(),
                'nazwisko': nazwisko.get(),
                'ojciec': imie_ojca.get(),
                'komorka': komorka.get(),
                'stanowisko': stanowisko.get(),
                'telefon': telefon.get(),
                'pesel': item[5]

            })
        conn.commit()
        conn.close()
        messagebox.showinfo("Sukces", "Zmodyfikowano osobę poprawnie")

    submit = Button(top, text="Zmodyfikuj", command=onClick)
    submit.pack()


def OnDoubleClick(event):
    select = tree.selection()
    item = tree.item(select)["values"]
    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute("SELECT * from Tasks WHERE PESEL = :id", {
        'id': item[5]
    })
    records = c.fetchall()
    if tree2.get_children() is not None:
        for i in tree2.get_children():
            tree2.delete(i)
    for task in records:
        tree2.insert("", END, values=task)
    tabControl.select(taskTab)
    conn.commit()
    conn.close()


def OnRightClick(event):
    select = tree.selection()
    item = tree.item(select)["values"]
    pyperclip.copy(item[5])
    messagebox.showinfo('Sukces', 'Skopiowano Pesel')


def OnRightClick2(event):
    select = tree2.selection()
    item = tree2.item(select)["values"]
    pyperclip.copy(item[2])
    messagebox.showinfo('Sukces', 'Skopiowano Pesel')


tree.bind("<space>", func=OnEClickEdit)
tree.bind("<Button-3>", func=OnRightClick)
tree.bind("<Double-1>", func=OnDoubleClick)
tree.pack(expand=True, fill='y')
query_btn = Button(peopleTab, text="Pokaż Osoby", command=Query)
query_btn.pack(pady=15)
query2_btn = Button(peopleTab, text="Dodaj Osobę", command=AddPeople)
query2_btn.pack(pady=15)

query_btn4 = Button(peopleTab, text="Usuń Osobę", command=DeletePeople)
query_btn4.pack(pady=15)

tree2 = Treeview(taskTab, selectmode='browse',
                 column=(
                     "column1", "column2", "column3", "column4", "column5", "column6", "column7", "column8", "column9",
                     "column10", "column11"),
                 show='headings')
tree2.heading("#1", text="Zadanie", command=lambda: sort(tree2, '#1'))
tree2.heading("#2", text="Gdzie przydzielony", command=lambda: sort(tree2, '#2'))
tree2.heading("#3", text="Pesel")
tree2.heading("#4", text="Ilość Dni", command=lambda: sort(tree2, '#4'))
tree2.heading("#5", text="ID")
tree2.heading("#6", text="Angazacja w walkę z koronawirusem")
tree2.heading("#7", text="OD", command=lambda: sort(tree2, '#7'))
tree2.heading("#8", text="DO", command=lambda: sort(tree2, '#8'))
tree2.heading("#9", text="Imię", command=lambda: sort(tree2, '#9'))
tree2.heading("#10", text="Nazwisko", command=lambda: sort(tree2, '#10'))
tree2.heading("#11", text="Komórka w firmie", command=lambda: sort(tree2, '#11'))
tree2.column("#1", width=100)
tree2.column("#2", width=130)
tree2.column("#3", width=100)
tree2.column("#4", width=125)
tree2.column("#5", width=125)
tree2.column("#6", width=200)
tree2.column("#7", width=125)
tree2.column("#8", width=200)
tree2.column("#9", width=150)
tree2.column("#10", width=150)
tree2.column("#11", width=100)

tree2.bind("<Button-3>", func=OnRightClick2)


def QueryTasks():
    conn = sqlite3.connect('people.db')
    c = conn.cursor()
    c.execute("SELECT * from Tasks")
    records = c.fetchall()
    if tree2.get_children() is not None:
        for i in tree2.get_children():
            tree2.delete(i)
    for task in records:
        c.execute("SELECT IMIĘ, NAZWISKO, Komórka from People WHERE PESEL = :pesel", {
            'pesel': task[2]
        })
        info = c.fetchall()
        for infos in info:
            task += infos
            tree2.insert("", END, values=task)
    conn.commit()
    conn.close()


def AddTask():
    conn = sqlite3.connect('people.db')
    c = conn.cursor()

    c.execute(
        "SELECT ID from Tasks WHERE pesel = :pesel",
        {
            'pesel': personId.get()
        })
    fetchedID = c.fetchone()
    niceSelection = ""
    if corona.get() == "TAK":
        niceSelection = "TRUE"
    elif corona.get() == "NIE":
        niceSelection = "FALSE"
    if fetchedID is None:
        c.execute(
            "INSERT INTO Tasks VALUES (:zadanie, :komorka, :pesel, :iloscDni,NULL ,:angazacjaWirus, :OD, :DO)",
            {
                'zadanie': goal.get(),
                'komorka': squad.get(),
                'pesel': personId.get(),
                'iloscDni': 0,
                'angazacjaWirus': niceSelection,
                'OD': froms.get_date(),
                'DO': tos.get_date()
            })

        c.execute(
            "UPDATE Tasks SET iloscDni = (SELECT (julianday(DO)-julianday(OD)) + 1 AS iloscDni FROM Przydzialy WHERE pesel= :pesel) WHERE pesel = :pesel",
            {
                'pesel': personId.get()
            })

        c.execute(
            "UPDATE People SET ID_ZADANIA = (SELECT ID FROM Tasks WHERE pesel = :pesel) WHERE PESEL = :pesel",
            {
                'pesel': personId.get()
            })
    elif fetchedID is not None:
        checked = False
        c.execute(
            "SELECT ID from Tasks WHERE (OD >= :od AND DO <= :do) AND pesel = :pesel OR (OD <= :od AND DO >= :do) AND pesel = :pesel OR (OD = :od AND DO = :do) AND pesel = :pesel OR (OD = :do) AND pesel = :pesel OR (DO = :od) AND pesel = :pesel",
            {
                'od': froms.get_date(),
                'do': tos.get_date(),
                'pesel': personId.get()
            })
        exists = c.fetchall()

        if exists:
            checked = False
        if not exists:
            checked = True

        if checked is True:
            c.execute(
                "INSERT INTO Tasks VALUES (:zadanie, :komorka_organizacyjna, :pesel, :iloscDni,NULL ,:angazacjaWirus, :OD, :DO)",
                {
                    'zadanie': goal.get(),
                    'komorka_organizacyjna': squad.get(),
                    'pesel': personId.get(),
                    'iloscDni': 0,
                    'angazacjaWirus': niceSelection,
                    'OD': froms.get_date(),
                    'DO': tos.get_date()
                })

            c.execute(
                "UPDATE Przydzialy SET iloscDni = (SELECT julianday(DO)-julianday(OD) AS iloscDni FROM Przydzialy WHERE pesel= :pesel) WHERE pesel = :pesel",
                {
                    'pesel': personId.get()
                })

            c.execute(
                "UPDATE People SET ID_ZADANIA = (SELECT ID FROM Tasks WHERE pesel = :pesel) WHERE PESEL = :pesel",
                {
                    'pesel': personId.get()
                })
        elif checked is False:
            messagebox.showinfo('Błąd', 'Osoba ma przydzielone zadanie na ten dzień')

    # Czyszczenie
    goal.delete(0, END)
    squad.delete(0, END)
    personId.delete(0, END)
    corona.delete(0, END)
    froms.delete(0, END)
    tos.delete(0, END)

    # Zatwierdź zmiany
    conn.commit()

    # Zakończ połączenie
    conn.close()


def search():
    # Utworzenie połącznia
    conn = sqlite3.connect('people.db')

    # Utworzenie kursora
    c = conn.cursor()
    selection = spinBox.get()
    if selection == "PESEL":
        c.execute("SELECT * FROM People WHERE PESEL = (:pesel)",
                  {
                      'pesel': searchEntry.get()
                  }
                  )
        Seach = c.fetchall()
        if tree.get_children() is not None:
            for i in tree.get_children():
                tree.delete(i)
        for task in Seach:
            tree.insert("", END, values=task)


    elif selection == "NAZWISKO":
        c.execute("SELECT * FROM People WHERE NAZWISKO = (:nazwisko)",
                  {
                      'nazwisko': searchEntry.get().upper()
                  }
                  )
        Seach = c.fetchall()
        if tree.get_children() is not None:
            for i in tree.get_children():
                tree.delete(i)
        for task in Seach:
            tree.insert("", END, values=task)

    elif selection == "NUMER Komórki":
        c.execute("SELECT * FROM People WHERE Komórka = (:komórka)",
                  {
                      'komórka': searchEntry.get()
                  }
                  )
        Seach = c.fetchall()
        if tree.get_children() is not None:
            for i in tree.get_children():
                tree.delete(i)
        for task in Seach:
            tree.insert("", END, values=task)

    # Zatwierdź zmiany
    conn.commit()

    # Zakończ połączenie
    conn.close()


spin_label = Label(peopleTab, text="Wybierz opcję szukania")
spin_label.pack(side=LEFT, pady=10)
spinBox = Combobox(peopleTab, exportselection=True, values=
[
    "PESEL",
    "NAZWISKO",
    "Komórka"
])
spinBox.pack(side=LEFT, pady=10)
searchEntry = Entry(peopleTab, width=60)
searchEntry.pack(side=LEFT, padx=10, pady=10)
search_btn = Button(peopleTab, text="Wyszukaj", command=search)
search_btn.pack(side=LEFT, padx=5, pady=10)

goal_label = Label(taskTab, text="Zadania")
goal_label.pack()
goal = Entry(taskTab, width=60)
goal.pack()
squad_label = Label(taskTab, text="Jaka komórka")
squad_label.pack()
squad = Entry(taskTab, width=60)
squad.pack()
personId_label = Label(taskTab, text="Pesel")
personId_label.pack()
personId = Entry(taskTab, width=60)
personId.pack()

corona_label = Label(taskTab, text="Angażacja w sprawy wirusa")
corona_label.pack()
corona = Combobox(taskTab, exportselection=True, values=[
    "TAK",
    "NIE"
])
corona.pack()
froms_label = Label(taskTab, text="Od kiedy")
froms_label.pack()
froms = DateEntry(taskTab, width=60)
froms.pack()
tos_label = Label(taskTab, text="Do kiedy")
tos_label.pack()
tos = DateEntry(taskTab, width=60)
tos.pack()
add_btn = Button(taskTab, text="Dodaj zadanie", command=AddTask)
add_btn.pack()
load_btn = Button(taskTab, text="Wczytaj Dane", command=LoadData)
load_btn.pack()

tree2.pack(expand=True, fill='y')
query_btn2 = Button(taskTab, text="Pokaż Zadania", command=QueryTasks)
query_btn2.pack()


def DeleteTask():
    # Utworzenie połącznia
    conn = sqlite3.connect('people.db')

    # Utworzenie kursora
    c = conn.cursor()

    select = tree2.selection()
    item = tree2.item(select)["values"]
    peselSelected = item[2]
    idSelected = item[4]

    c.execute("DELETE FROM Tasks WHERE ID= (:index)",
              {
                  'index': idSelected
              }
              )
    c.execute(
        "UPDATE People SET ID_ZADANIA = (SELECT ID From Tasks where pesel = :index) WHERE PESEL = :index", {
            'index': peselSelected
        })

    # Zatwierdź zmiany
    conn.commit()

    # Zakończ połączenie
    conn.close()

    QueryTasks()


query_btn6 = Button(taskTab, text="Zmodyfikuj zadanie", command=ChangeTask)
query_btn6.pack()

query_btn3 = Button(taskTab, text="Usuń Zadanie", command=DeleteTask)
query_btn3.pack()


def DrawGraph():
    conn = sqlite3.connect('people.db')

    c = conn.cursor()


    komp1 = 0
    real1 = 0
    real2 = 0
    real3 = 0
    real4 = 0
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 1' AND angazacjaWirus='TRUE' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 1' AND angazacjaWirus='TRUE'")
    fetched = len(c.fetchall())
    if fetched != 0:
        komp1 += 1
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 1' AND angazacjaWirus='FALSE' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 1' AND angazacjaWirus='FALSE'")
    nosquad1 = len(c.fetchall())

    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 1' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 1'")
    real = c.fetchall()
    for item in real:
        c.execute("SELECT Komórka FROM People WHERE PESEL=:pesel", {
            'pesel': item[2]
        })
        fetched1 = c.fetchone()
        if fetched1[0] == "Komórka 1":
            real1 += 1
        if fetched1[0] == "Komórka 2":
            real2 += 1
        if fetched1[0] == "Komórka 3":
            real3 += 1
        if fetched1[0] == "Komórka 4":
            real4 += 1


    komp2 = 0
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 2' AND angazacjaWirus='TRUE' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 2' AND angazacjaWirus='TRUE'")
    fetched2 = len(c.fetchall())
    if fetched2 != 0:
        komp2 += 1
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 2' AND angazacjaWirus='FALSE' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 2' AND angazacjaWirus='FALSE'")
    nosquad2 = len(c.fetchall())

    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 2' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 2'")
    real = c.fetchall()
    for item in real:
        c.execute("SELECT Komórka FROM People WHERE PESEL=:pesel", {
            'pesel': item[2]
        })
        fetched2 = c.fetchone()
        if fetched2[0] == "Komórka 1":
            real1 += 1
        if fetched2[0] == "Komórka 2":
            real2 += 1
        if fetched2[0] == "Komórka 3":
            real3 += 1
        if fetched2[0] == "Komórka 4":
            real4 += 1


    komp3 = 0
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 3' AND angazacjaWirus='TRUE' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 3' AND angazacjaWirus='TRUE'")
    fetched3 = len(c.fetchall())
    if fetched3 != 0:
        komp3 += 1
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 3' AND angazacjaWirus='FALSE' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 3' AND angazacjaWirus='FALSE'")
    nosquad3 = len(c.fetchall())
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 3' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 3'")
    real = c.fetchall()
    for item in real:
        c.execute("SELECT Komórka FROM People WHERE PESEL=:pesel", {
            'pesel': item[2]
        })
        fetched3 = c.fetchone()
        if fetched3[0] == "Komórka 1":
            real1 += 1
        if fetched3[0] == "Komórka 2":
            real2 += 1
        if fetched3[0] == "Komórka 3":
            real3 += 1
        if fetched3[0] == "Komórka 4":
            real4 += 1


    komp4 = 0
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 4' AND angazacjaWirus='TRUE' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 4' AND angazacjaWirus='TRUE'")
    fetched4 = len(c.fetchall())
    if fetched4 != 0:
        komp4 += 1
    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 4' AND angazacjaWirus='FALSE' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 4' AND angazacjaWirus='FALSE'")
    nosquad4 = len(c.fetchall())

    c.execute(
        "Select * FROM Tasks WHERE (OD >= CURRENT_DATE AND DO <= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 4' OR (OD <= CURRENT_DATE AND DO >= CURRENT_DATE) AND komorka_organizacyjna = 'Komórka 4'")
    real = c.fetchall()
    for item in real:
        c.execute("SELECT Komórka FROM People WHERE PESEL=:pesel", {
            'pesel': item[2]
        })
        fetched4 = c.fetchone()
        if fetched4[0] == "Komórka 1":
            real1 += 1
        if fetched4[0] == "Komórka 2":
            real2 += 1
        if fetched4[0] == "Komórka 3":
            real3 += 1
        if fetched4[0] == "Komórka 4":
            real4 += 1


    labels = ['Komórka 1', 'Komórka 2', 'Komórka 3', 'Komórka 4']
    ang_means = [komp1, komp2, komp3, komp4]
    notang_means = [nosquad1, nosquad2, nosquad3, nosquad4]
    countreal = [real1, real2, real3, real4]

    x = np.arange(len(labels))  # the label locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, ang_means, width, label='Osoby związane ze zwalczaniem koronawirusa')
    rects2 = ax.bar(x, notang_means, width, label='Działaność bieżąca')
    rects3 = ax.bar(x + width, countreal, width, label='Łączna ilość')

    ax.set_ylabel('Ilość ludzi')
    ax.set_title('Podział zaangażowania ludzi na dzień dzisiejszy')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + 0.1, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    fig.tight_layout()

    plt.show()
    print(countreal)


query5_btn = Button(peopleTab, text="Rysuj Wykres", command=DrawGraph)
query5_btn.pack(pady=15)
copyrights = Label(peopleTab, text="Copyright:Paweł Włodarczyk")
copyrights2 = Label(peopleTab, text="www.pawelvlodarczyk.pl")
copyrights.pack()
copyrights2.pack()
copyrights3 = Label(taskTab, text="Copyright: Paweł Włodarczyk")
copyrights4 = Label(taskTab, text="www.pawelvlodarczyk.pl")
copyrights4.pack(side='right', padx=25)
copyrights3.pack(side='right')

root.mainloop()
