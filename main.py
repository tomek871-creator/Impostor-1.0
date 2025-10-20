from flask import Flask, request, redirect, url_for, render_template_string, jsonify
import random
import json
import os

app = Flask(__name__)

DATA_FILE = "/tmp/games.json"

# -----------------------------
# Pomocnicze funkcje zapisu i wczytania danych
# -----------------------------
def load_games():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_games(games):
    with open(DATA_FILE, "w") as f:
        json.dump(games, f)

# -----------------------------
# Lista słów (mix łatwe + poważniejsze)
# -----------------------------
WORDS = [
    "kot", "pies", "rower", "telefon", "lampa", "drzewo", "książka", "samolot", "okno", "zegarek",
    "pociąg", "torba", "pilot", "długopis", "szkoła", "biurko", "krzesło", "łóżko", "kubek", "plecak",
    "czekolada", "kino", "basen", "mleko", "chleb", "dom", "most", "kwiat", "wiatrak", "herbata",
    "lekarz", "muzyk", "aktor", "strażak", "policjant", "nauczyciel", "architekt", "astronauta",
    "adwokat", "malarz", "mechanik", "rolnik", "kucharz", "programista", "pilot", "żeglarz",
    "bibliotekarz", "weterynarz", "artysta", "dziennikarz", "inżynier", "sportowiec", "fotograf",
    "psycholog", "chemik", "geolog", "filozof", "naukowiec", "dyrektor", "polityk", "prezydent",
    "aktor", "projektant", "muzyk", "sędzia", "trener", "pisarz", "kompozytor", "poeta",
    "ekonomista", "dentysta", "chirurg", "fizyk", "prawnik", "historyk", "astronom",
]

# -----------------------------
# Strona główna
# -----------------------------
@app.route("/")
def index():
    return render_template_string("""
    <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
        <h2>🎭 Gra: Impostor</h2>
        <form action="/create_room" method="post">
            <button type="submit">Utwórz pokój</button>
        </form><br>
        <form action="/join_room" method="post">
            <input name="code" placeholder="Kod pokoju" required>
            <button type="submit">Dołącz</button>
        </form>
    </body></html>
    """)

# -----------------------------
# Tworzenie pokoju
# -----------------------------
@app.route("/create_room", methods=["POST"])
def create_room():
    games = load_games()
    room_code = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ123456789", k=5))
    games[room_code] = {"players": [], "word": random.choice(WORDS), "impostor": None}
    save_games(games)
    link = f"{request.host_url}room/{room_code}"
    return render_template_string(f"""
    <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
        <h2>✅ Pokój {room_code} utworzony!</h2>
        <p>Podziel się tym linkiem ze znajomymi:</p>
        <p><a href="{link}" target="_blank">{link}</a></p>
    </body></html>
    """)

# -----------------------------
# Dołączanie do pokoju
# -----------------------------
@app.route("/join_room", methods=["POST"])
def join_room():
    code = request.form["code"].strip().upper()
    return redirect(url_for("room", room=code))

# -----------------------------
# Widok pokoju (lobby + gra)
# -----------------------------
@app.route("/room/<room>")
def room(room):
    games = load_games()
    if room not in games:
        return "<h3>❌ Pokój nie istnieje</h3>", 404

    ip = request.remote_addr
    game = games[room]

    # Dodaj gracza jeśli nie ma
    if ip not in game["players"]:
        if len(game["players"]) < 10:
            game["players"].append(ip)
            save_games(games)

    # Losowanie impostora przy >= 3 graczach
    if len(game["players"]) >= 3 and game["impostor"] is None:
        game["impostor"] = random.choice(game["players"])
        save_games(games)

    # Jeśli gra się zaczęła
    if game["impostor"] is not None:
        if ip == game["impostor"]:
            word = "❓ Jesteś IMPOSTOREM! Spróbuj udawać, że znasz słowo."
        else:
            word = f"🧩 Twoje słowo: <b>{game['word']}</b>"
        return render_template_string(f"""
        <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
            <h3>Pokój {room}</h3>
            <p>{word}</p>
            <p>Liczba graczy: {len(game['players'])}</p>
            <form action="/reset/{room}" method="post">
                <button type="submit">Zagraj ponownie</button>
            </form>
        </body></html>
        """)

    # Jeśli czekamy na więcej graczy
    return render_template_string(f"""
    <html><body style='text-align:center; font-family:Arial; margin-top:10%'>
        <h3>Pokój {room}</h3>
        <p>Liczba graczy: <span id='count'>{len(game['players'])}</span></p>
        <button onclick="location.reload()">🔄 Odśwież</button>
        <p>Czekamy aż będą co najmniej 3 osoby...</p>
    </body></html>
    """)

# -----------------------------
# Reset gry (nowa runda)
# -----------------------------
@app.route("/reset/<room>", methods=["POST"])
def reset(room):
    games = load_games()
    if room in games:
        games[room]["word"] = random.choice(WORDS)
        games[room]["impostor"] = None
        save_games(games)
    return redirect(url_for("room", room=room))

# -----------------------------
# Uruchomienie
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
