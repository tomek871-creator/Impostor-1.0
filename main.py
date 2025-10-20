from flask import Flask, request, render_template_string
import random

app = Flask(__name__)

games = {}

WORDS = [
    "kot", "pies", "drzewo", "chleb", "telefon", "auto", "morze", "góry", "szkoła", "nauczyciel",
    "książka", "las", "słońce", "księżyc", "gwiazda", "samolot", "rower", "krzesło", "stół", "okno",
    "drzwi", "dach", "komputer", "mysz", "klawiatura", "kubek", "woda", "kawa", "herbata", "cukier",
    "dom", "pokój", "ogród", "kwiat", "trawa", "miasto", "ulica", "sklep", "kino", "teatr",
    "muzyka", "piosenka", "gitara", "fortepian", "perkusja", "sport", "piłka", "bramka", "gol", "bieganie",
    "basen", "rzeka", "jezioro", "plaża", "piasek", "deszcz", "śnieg", "wiatr", "burza", "grzmot",
    "chmura", "niebo", "lampa", "światło", "ciemność", "noc", "dzień", "poranek", "wieczór", "cień",
    "piesek", "kotka", "ptak", "ryba", "żaba", "koń", "świnia", "krowa", "owca", "zając",
    "lis", "niedźwiedź", "wilk", "tygrys", "lew", "słoń", "małpa", "żółw", "pingwin", "krokodyl",
    "motyl", "pszczoła", "osa", "komar", "mrówka", "pająk", "gąsienica", "biedronka", "delfin", "rekin",
    "rakieta", "planeta", "kosmos", "robot", "statek", "samochód", "motor", "hulajnoga", "tramwaj", "autobus",
    "ciężarówka", "metro", "pociąg", "dworzec", "bilet", "portfel", "plecak", "torebka", "klucz", "zamek",
    "obraz", "lustro", "poduszka", "kołdra", "łóżko", "kanapa", "fotel", "telewizor", "pilot", "radio",
    "gazeta", "czasopismo", "kartka", "długopis", "ołówek", "linijka", "zeszyt", "plecak", "biurko", "szafka",
    "szafa", "lód", "zupa", "kanapka", "pizza", "hamburger", "frytki", "ser", "masło", "jajko",
    "sałatka", "pomidor", "ogórek", "marchewka", "ziemniak", "cebula", "czosnek", "jabłko", "banan", "gruszka",
    "pomarańcza", "cytryna", "winogrono", "truskawka", "malina", "borówka", "wiśnia", "śliwka", "ananas", "arbuz",
    "lody", "ciasto", "tort", "cukierek", "czekolada", "baton", "ciastko", "pączek", "drożdżówka", "chlebek",
    "makaron", "ryż", "mięso", "kurczak", "ryba", "wołowina", "kiełbasa", "kotlet", "szynka", "jogurt",
    "sernik", "naleśnik", "placki", "pierogi", "zupa pomidorowa", "rosół", "barszcz", "żurek", "gulasz", "sałatka grecka",
    "biuro", "praca", "szef", "pracownik", "komputer", "drukarka", "monitor", "klawiatura", "myszka", "biurko",
    "szkoła", "uczeń", "nauczyciel", "klasa", "tablica", "kreda", "zeszyt", "lekcja", "zadanie", "ocena",
    "wakacje", "ferie", "plaża", "góry", "jezioro", "morze", "wycieczka", "podróż", "hotel", "walizka",
    "bilet", "paszport", "samolot", "lotnisko", "statek", "autobus", "tramwaj", "metro", "pociąg", "taksówka",
    "rower", "motor", "hulajnoga", "buty", "spodnie", "koszulka", "kurtka", "czapka", "szalik", "rękawiczki",
    "sukienka", "spódnica", "bluza", "sweter", "skarpetki", "buty sportowe", "klapki", "sandały", "marynarka", "garnitur",
    "ubranie", "odzież", "płaszcz", "kurtka zimowa", "torba", "plecak", "portfel", "zegarek", "bransoletka", "naszyjnik",
    "kolczyki", "pierścionek", "czapka z daszkiem", "okulary", "okulary przeciwsłoneczne", "telefon", "tablet", "laptop", "komputer", "monitor",
    "drukarka", "głośnik", "słuchawki", "mikrofon", "kamera", "mysz", "klawiatura", "pendrive", "dysk", "internet",
    "strona", "gra", "film", "muzyka", "piosenka", "artysta", "aktor", "piosenkarz", "youtuber", "bloger",
    "taniec", "śpiew", "koncert", "festiwal", "scena", "publiczność", "mikrofon", "gitara", "perkusja", "fortepian",
    "obraz", "malarz", "rzeźba", "muzeum", "galeria", "teatr", "aktor", "reżyser", "kamera", "film",
    "serial", "odcinek", "scena", "dialog", "scenariusz", "kostium", "charakteryzacja", "muzyka filmowa", "napisy", "plakat",
    "miłość", "przyjaźń", "radość", "złość", "smutek", "strach", "nadzieja", "tęsknota", "zazdrość", "śmiech",
    "łzy", "uczucia", "emocje", "marzenie", "sen", "myśl", "pomysł", "plan", "cel", "sukces",
    "porażka", "walka", "gra", "zabawa", "zwycięstwo", "nagroda", "prezent", "niespodzianka", "święta", "urodziny",
    "impreza", "taniec", "muzyka", "zabawa", "ciasto", "balony", "dekoracje", "świeczki", "życzenia", "goście",
    "rodzina", "rodzice", "dziecko", "brat", "siostra", "dziadek", "babcia", "wujek", "ciocia", "kuzyn",
    "przyjaciel", "kolega", "znajomy", "sąsiad", "dziecko", "uczeń", "student", "nauczyciel", "doktor", "pielęgniarka",
    "lekarz", "dentysta", "weterynarz", "policjant", "strażak", "żołnierz", "pilot", "kelner", "kucharz", "mechanik",
    "informatyk", "programista", "sprzedawca", "muzyk", "malarz", "aktor", "pisarz", "reżyser", "fotograf", "naukowiec"
]

# ----------------------- STRONA GŁÓWNA -----------------------
@app.route("/")
def index():
    return render_template_string("""
    <html>
    <head>
        <title>Impostor Game 🎭</title>
        <style>
            body { background-color: #121212; color: white; text-align: center; font-family: Arial; margin-top: 10%; }
            input, button { padding: 10px; border-radius: 8px; border: none; margin: 5px; }
            input { width: 200px; }
            button { background-color: #03a9f4; color: white; cursor: pointer; }
            button:hover { background-color: #0288d1; }
            .box { background-color: #1e1e1e; padding: 30px; border-radius: 12px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🎭 Impostor Game</h1>
            <form action="/create" method="post">
                <p>Podaj kod pokoju (np. TEAM5):</p>
                <input name="room" placeholder="Kod pokoju" required>
                <button type="submit">🆕 Stwórz grę</button>
            </form>
            <hr style="margin: 20px 0; opacity: 0.3;">
            <form action="/room" method="get">
                <p>Lub dołącz do istniejącego pokoju:</p>
                <input name="room" placeholder="Kod pokoju" required>
                <button type="submit">➡️ Dołącz</button>
            </form>
        </div>
    </body>
    </html>
    """)

# ----------------------- TWORZENIE GRY -----------------------
@app.route("/create", methods=["POST"])
def create_game():
    room = request.form["room"].strip().upper()
    if not room:
        return "❌ Podaj kod pokoju!"

    if room in games:
        return f"❌ Pokój {room} już istnieje."

    games[room] = {
        "word": random.choice(WORDS),
        "players": [],
        "impostor": None
    }

    return render_template_string(f"""
    <html><body style="text-align:center; font-family:Arial; margin-top:10%">
        <h2>✅ Pokój {room} utworzony!</h2>
        <p>Podziel się tym kodem ze znajomymi.</p>
        <a href="/room/{room}">➡️ Przejdź do pokoju</a>
    </body></html>
    """)

# ----------------------- WEJŚCIE DO POKOJU -----------------------
@app.route("/room/<room>")
def join_room(room):
    if room not in games:
        return "❌ Pokój nie istnieje."

    game = games[room]
    players = len(game["players"])

    if players >= 8:
        return render_template_string(f"""
        <html><body style="text-align:center; font-family:Arial; margin-top:10%">
            <h2>🛑 Pokój {room} jest pełny (8/8 graczy).</h2>
            <a href="/">⬅️ Wróć</a>
        </body></html>
        """)

    return render_template_string(f"""
    <html>
    <head>
        <title>Pokój {room}</title>
        <style>
            body {{ background-color: #121212; color: white; font-family: Arial; text-align: center; margin-top: 10%; }}
            input, button {{ padding: 10px; border-radius: 8px; border: none; margin: 5px; }}
            button {{ background-color: #03a9f4; color: white; cursor: pointer; }}
            button:hover {{ background-color: #0288d1; }}
            .box {{ background-color: #1e1e1e; padding: 20px; border-radius: 10px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Pokój: {room}</h2>
            <p>Graczy w pokoju: {players}/8</p>
            <form action="/play/{room}" method="post">
                <input name="player" placeholder="Twoje imię" required>
                <button type="submit">Dołącz i zobacz słowo</button>
            </form>
        </div>
    </body>
    </html>
    """)

# ----------------------- ROZPOCZĘCIE GRY -----------------------
@app.route("/play/<room>", methods=["POST"])
def play(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    
    player = request.form["player"].strip()
    game = games[room]

    if len(game["players"]) >= 8 and player not in game["players"]:
        return f"❌ Pokój {room} jest pełny (8/8 graczy)."

    if player not in game["players"]:
        game["players"].append(player)

    # Start gry dopiero od 3 graczy
    if len(game["players"]) >= 3 and game["impostor"] is None:
        game["impostor"] = random.choice(game["players"])

    if len(game["players"]) < 3:
        return render_template_string(f"""
        <html><body style="text-align:center; font-family:Arial; margin-top:15%">
            <h2>🕐 Czekamy na więcej graczy...</h2>
            <p>W pokoju {len(game["players"])}/3+</p>
            <a href="/room/{room}">🔁 Odśwież</a>
        </body></html>
        """)

    if player == game["impostor"]:
        word = "IMPOSTOR"
    else:
        word = game["word"]

    return render_template_string(f"""
    <html>
    <head>
        <title>Twoje słowo</title>
        <style>
            body {{ background-color: #000; color: #fff; text-align: center; font-family: Arial; margin-top: 15%; }}
            .word {{ font-size: 2em; color: #4caf50; }}
            button {{ background-color: #f44336; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; margin-top: 20px; }}
            button:hover {{ background-color: #d32f2f; }}
        </style>
    </head>
    <body>
        <h1>Gracz: {player}</h1>
        <p>Twoje słowo:</p>
        <p class="word">{word}</p>
        <form action="/new_round/{room}" method="post">
            <button type="submit">🔁 Zagraj ponownie</button>
        </form>
    </body>
    </html>
    """)

# ----------------------- NOWA RUNDA -----------------------
@app.route("/new_round/<room>", methods=["POST"])
def new_round(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    
    game = games[room]
    game["word"] = random.choice(WORDS)
    game["impostor"] = random.choice(game["players"])
    
    return render_template_string(f"""
    <html><body style="text-align:center; font-family:Arial; margin-top:10%">
        <h2>🔄 Nowa runda w pokoju {room}!</h2>
        <p>Impostor i słowo zostały zmienione.</p>
        <a href="/room/{room}">➡️ Wracaj do gry</a>
    </body></html>
    """)

# ----------------------- START APLIKACJI -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
