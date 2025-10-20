from flask import Flask, request, render_template_string
import random

app = Flask(__name__)

# ---------------- SŁOWA ----------------
WORDS = [
    "kot", "pies", "dom", "rower", "szkoła", "komputer", "telefon", "statek", "góry", "morze",
    "tęcza", "drzewo", "samolot", "krzesło", "biurko", "okno", "książka", "film", "muzyka", "zamek",
    "chleb", "ser", "pomidor", "kawa", "herbata", "czekolada", "śnieg", "słońce", "chmura", "wiatr",
    "taniec", "kosmos", "las", "ogród", "jabłko", "szpital", "traktor", "boisko", "piłka", "kino",
    "nauczyciel", "aktor", "żołnierz", "malarka", "dentysta", "programista", "muzyk", "architekt", "kucharz", "pilot",
    "samochód", "hulajnoga", "motor", "sklep", "most", "wieża", "zamek", "zamek błyskawiczny", "pociąg", "metro",
    "niedźwiedź", "lew", "tygrys", "słoń", "foka", "żaba", "panda", "pingwin", "królik", "lis",
    "zegar", "radio", "telewizor", "pióro", "plecak", "kubek", "butelka", "talerz", "nóż", "łyżka",
    "planeta", "robot", "dinozaur", "kometa", "miasto", "wieś", "państwo", "rzeka", "jezioro", "wyspa",
    "burza", "księżyc", "gwiazda", "słońce", "noc", "dzień", "poranek", "wieczór", "sen", "marzenie",
    "matematyka", "język", "historia", "geografia", "fizyka", "chemia", "muzyka", "sztuka", "sport", "gra",
    "mecz", "bramka", "trener", "piłkarz", "koszykówka", "tenis", "bieganie", "pływanie", "jazda", "skok",
    "zima", "lato", "wiosna", "jesień", "wakacje", "ferie", "święta", "urodziny", "tort", "prezent",
    "książę", "królowa", "czarodziej", "smok", "rycerz", "elf", "duch", "zombie", "robot", "kosmita",
    "prawda", "marzenie", "radość", "strach", "nadzieja", "pokój", "wojna", "cisza", "hałas", "czas",
    "przyjaciel", "rodzina", "brat", "siostra", "mama", "tata", "babcia", "dziadek", "kolega", "koleżanka",
    "plan", "projekt", "pomysł", "zadanie", "gra", "zabawa", "misja", "podróż", "przygoda", "sekret",
    "energia", "światło", "dźwięk", "cień", "ciepło", "zimno", "ogień", "woda", "powietrze", "ziemia",
    "granat", "rakieta", "mikroskop", "kompas", "zegarek", "latarka", "aparat", "kamera"
