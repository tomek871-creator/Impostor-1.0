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
    "granat", "rakieta", "mikroskop", "kompas", "zegarek", "latarka", "aparat", "kamera", "lornetka", "telefon",
    "internet", "robotyka", "sztuka", "technologia", "planeta", "program", "dane", "system", "gra", "muzyka",
    "teatr", "film", "aktor", "kamera", "scena", "widownia", "mikrofon", "piosenka", "melodia", "taniec",
    "serce", "rozum", "emocja", "szczęście", "radość", "złość", "miłość", "strach", "sen", "spokój"
]

# ---------------- GRA ----------------
games = {}

@app.route("/")
def index():
    return render_template_string("""
    <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
        <h1>🎭 Impostor Game</h1>
        <form action="/create" method="post">
            <input name="room" placeholder="Kod pokoju" required>
            <button type="submit">Stwórz pokój</button>
        </form>
        <hr>
        <form action="/room" method="get">
            <input name="room" placeholder="Kod pokoju" required>
            <button type="submit">Dołącz</button>
        </form>
    </body></html>
    """)

@app.route("/create", methods=["POST"])
def create_game():
    room = request.form["room"].strip().upper()
    if room in games:
        return f"❌ Pokój {room} już istnieje."
    games[room] = {"word": random.choice(WORDS), "players": 0, "impostor": None, "started": False}
    return render_template_string(f"""
    <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
        <h2>✅ Pokój {room} utworzony!</h2>
        <p>Podziel się tym kodem ze znajomymi.</p>
        <a href="/room/{room}">➡️ Przejdź do lobby</a>
    </body></html>
    """)

@app.route("/room/<room>")
def join_room(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    game = games[room]
    return render_template_string(f"""
    <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
        <h2>Pokój: {room}</h2>
        <p>Gracze w pokoju: {game["players"]}/8</p>
        <form action="/play/{room}" method="post">
            <button type="submit">Dołącz do gry</button>
        </form>
        <br>
        <a href="/room/{room}">🔁 Odśwież</a>
    </body></html>
    """)

@app.route("/play/<room>", methods=["POST"])
def play(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    game = games[room]
    game["players"] += 1
    player_id = game["players"]

    # GRA STARTUJE gdy 3+ graczy
    if game["players"] >= 3 and not game["started"]:
        game["started"] = True
        game["impostor"] = random.randint(1, game["players"])

    if not game["started"]:
        return render_template_string(f"""
        <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
            <h2>🕐 Czekamy na więcej graczy...</h2>
            <p>W pokoju {game["players"]}/3+</p>
            <a href="/room/{room}">🔁 Odśwież</a>
        </body></html>
        """)

    # przypisanie słowa
    word = "IMPOSTOR" if player_id == game["impostor"] else game["word"]

    return render_template_string(f"""
    <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
        <h1>Gracz {player_id}</h1>
        <p>Twoje słowo:</p>
        <h2 style="color:lightgreen;">{word}</h2>
        <form action="/new_round/{room}" method="post">
            <button type="submit">🔁 Nowa runda</button>
        </form>
    </body></html>
    """)

@app.route("/new_round/<room>", methods=["POST"])
def new_round(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    game = games[room]
    game["word"] = random.choice(WORDS)
    game["impostor"] = random.randint(1, game["players"])
    game["started"] = True
    return render_template_string(f"""
    <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
        <h2>🔄 Nowa runda w pokoju {room}!</h2>
        <p>Nowe słowo i impostor zostały wylosowane.</p>
        <a href="/room/{room}">➡️ Wracaj do lobby</a>
    </body></html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
