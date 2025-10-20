from flask import Flask, request, render_template_string, redirect
import random

app = Flask(__name__)

games = {}

WORDS = [
    # 🟢 CODZIENNE, ŁATWIEJSZE (175)
    "kot", "pies", "królik", "koń", "ryba", "żaba", "ptak", "mysz", "owca", "koza",
    "świnia", "krowa", "kurczak", "gęś", "kaczka", "lis", "jeleń", "słoń", "tygrys", "lew",
    "panda", "pingwin", "delfin", "rekin", "żółw", "małpa", "miś", "zając", "motyl", "biedronka",
    "dom", "pokój", "okno", "drzwi", "lampa", "łóżko", "kanapa", "krzesło", "stół", "dywan",
    "szafa", "telewizor", "pilot", "komputer", "telefon", "laptop", "mysz", "klawiatura", "kubek", "talerz",
    "widelec", "łyżka", "nóż", "patelnia", "czajnik", "zlew", "garnek", "pralka", "lustro", "zegar",
    "szkoła", "klasa", "uczeń", "nauczyciel", "zeszyt", "piórnik", "ołówek", "długopis", "linijka", "plecak",
    "książka", "biblioteka", "tablica", "lekcja", "zadanie", "boisko", "piłka", "bramka", "trener", "mecz",
    "sport", "bieganie", "pływanie", "taniec", "muzyka", "piosenka", "gitara", "bęben", "fortepian", "flet",
    "film", "aktor", "reżyser", "mikrofon", "kamera", "scena", "światło", "teatr", "kino", "widownia",
    "las", "drzewo", "kwiat", "trawa", "rzeka", "jezioro", "morze", "plaża", "piasek", "kamień",
    "góra", "chmura", "słońce", "księżyc", "gwiazda", "deszcz", "śnieg", "burza", "tęcza", "wiatr",
    "miasto", "wieś", "sklep", "restauracja", "hotel", "kościół", "poczta", "zoo", "muzeum", "rynek",
    "samochód", "rower", "autobus", "pociąg", "tramwaj", "samolot", "statek", "hulajnoga", "bilet", "walizka",
    "dzień", "noc", "poranek", "wieczór", "wakacje", "urodziny", "prezent", "tort", "balon", "świeczka",
    "cukierek", "ciasto", "lody", "czekolada", "kanapka", "zupa", "pizza", "makaron", "jajko", "chleb",
    "ser", "jabłko", "banan", "truskawka", "malina", "gruszka", "pomidor", "ogórek", "ziemniak", "marchewka",
    "mama", "tata", "brat", "siostra", "babcia", "dziadek", "ciocia", "wujek", "kuzyn", "kuzynka",
    "przyjaciel", "kolega", "koleżanka", "rodzina", "dziecko", "sąsiad", "zwierzak", "piesek", "kotek", "domownik",

    # 🔵 POWAŻNIEJSZE / CIEKAWSZE (175)
    "astronauta", "kosmos", "planeta", "galaktyka", "gwiazdozbiór", "czarna dziura", "kometa", "rakieta", "satelita", "teleskop",
    "naukowiec", "fizyka", "chemia", "biologia", "mikroskop", "eksperyment", "atom", "energia", "elektryczność", "magnes",
    "robot", "sztuczna inteligencja", "programista", "inżynier", "architekt", "projekt", "mechanizm", "silnik", "technologia", "komunikacja",
    "system", "internet", "hasło", "dane", "plik", "sieć", "kod", "baza danych", "algorytm", "oprogramowanie",
    "muzeum nauki", "obserwatorium", "laboratorium", "badanie", "eksperyment", "odkrycie", "wynalazek", "historia", "prehistoria", "cywilizacja",
    "państwo", "rząd", "prezydent", "konstytucja", "prawo", "wolność", "obywatel", "społeczeństwo", "gospodarka", "ekonomia",
    "bank", "pieniądz", "handel", "transakcja", "biznes", "firma", "produkt", "reklama", "technologia", "wynalazca",
    "architektura", "budowla", "most", "wieżowiec", "zamek", "katedra", "pomnik", "rzeźba", "malarstwo", "galeria",
    "malarz", "rzeźbiarz", "muzyk", "dyrygent", "piosenkarz", "poeta", "pisarz", "aktor teatralny", "reżyser filmowy", "producent",
    "wojna", "pokój", "bitwa", "żołnierz", "strategia", "sojusz", "armia", "dowódca", "obrona", "atak",
    "planeta", "ekosystem", "klimat", "pogoda", "globalne ocieplenie", "energia słoneczna", "wiatrak", "elektrownia", "paliwo", "elektryk",
    "mechanik", "lekarz", "chirurg", "dentysta", "farmaceuta", "weterynarz", "psycholog", "ratownik", "nauczyciel akademicki", "profesor",
    "bibliotekarz", "historyk", "geograf", "astronom", "biotechnolog", "chemik", "fizyk", "matematyk", "filozof", "językoznawca",
    "kamera", "mikrofon", "nagranie", "produkcja", "studio", "radio", "telewizja", "gazeta", "redaktor", "dziennikarz",
    "reportaż", "informacja", "komentarz", "recenzja", "dyskusja", "debat", "argument", "opinia", "krytyk", "narrator",
    "polityka", "partia", "wybory", "kampania", "prezentacja", "spotkanie", "konferencja", "plan", "projekt", "cel",
    "marzenie", "inspiracja", "motywacja", "odwaga", "cierpliwość", "zaufanie", "nadzieja", "przyszłość", "kariera", "sukces",
    "porażka", "nauka", "próba", "postęp", "zmiana", "rozwiązanie", "technika", "innowacja", "wizja", "strategia",
    "światło", "energia", "fala", "dźwięk", "laser", "obraz", "piksel", "kamera termowizyjna", "drukarka 3D", "czujnik",
    "system bezpieczeństwa", "kod QR", "hasło dostępu", "konto użytkownika", "serwer", "aplikacja", "program", "symulator", "grafika", "model 3D",
    "robotyka", "cyberbezpieczeństwo", "sztuka nowoczesna", "ekologia", "recykling", "zrównoważony rozwój", "elektromobilność", "satelita", "mikrochip", "biometria"
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
            <form action="/join" method="get">
                <p>Lub dołącz do istniejącego pokoju:</p>
                <input name="room" placeholder="Kod pokoju" required>
                <button type="submit">➡️ Dołącz</button>
            </form>
        </div>
    </body>
    </html>
    """)

# ----------------------- DOŁĄCZANIE DO POKOJU -----------------------
@app.route("/join")
def join():
    room = request.args.get("room", "").strip().upper()
    if not room:
        return "❌ Podaj kod pokoju!"
    return redirect(f"/room/{room}")

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
        return f"🛑 Pokój {room} jest pełny (8/8 graczy)."

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

    # Reset impostora, wylosuj nowe słowo, ale zachowaj graczy
    game["word"] = random.choice(WORDS)
    if game["players"]:
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
