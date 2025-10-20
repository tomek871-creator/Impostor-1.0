from flask import Flask, request, redirect, url_for, render_template_string
import random
import string

app = Flask(__name__)

# ===============================
# USTAWIENIA GRY
# ===============================

# Lista słów (możesz rozbudować)
WORDS = [
    "kot", "pies", "rower", "samolot", "słońce", "księżyc", "telefon", "komputer", "las", "morze",
    "góry", "miasto", "dom", "krzesło", "kawa", "herbata", "jabłko", "banan", "samochód", "muzyka",
    "kino", "szkoła", "ogród", "śnieg", "deszcz", "chleb", "ryba", "zegarek", "długopis", "pociąg"
]

# Pokoje gier
games = {}

# ===============================
# STRONA GŁÓWNA
# ===============================
@app.route("/")
def index():
    return render_template_string("""
    <html>
    <head>
        <title>Impostor Game</title>
        <style>
            body { background-color: #121212; color: #f0f0f0; font-family: Arial; text-align: center; margin-top: 10%; }
            input, button { padding: 10px; border-radius: 8px; border: none; margin: 5px; }
            button { background-color: #3f51b5; color: white; cursor: pointer; }
            button:hover { background-color: #5c6bc0; }
            .box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🎭 Impostor Game</h1>
            <form action="/create" method="post">
                <input name="room" placeholder="Podaj kod pokoju (np. TEAM5)" required>
                <button type="submit">Stwórz pokój</button>
            </form>
            <form action="/join" method="post">
                <input name="room" placeholder="Dołącz do pokoju" required>
                <button type="submit">Dołącz</button>
            </form>
        </div>
    </body>
    </html>
    """)

# ===============================
# TWORZENIE POKOJU
# ===============================
@app.route("/create", methods=["POST"])
def create_game():
    room = request.form["room"].upper().strip()
    if not room:
        return redirect(url_for("index"))
    word = random.choice(WORDS)
    games[room] = {
        "players": [],
        "word": word,
        "impostor": None
    }
    return redirect(url_for("join_room", room=room))

# ===============================
# DOŁĄCZANIE DO POKOJU
# ===============================
@app.route("/join", methods=["POST"])
def join():
    room = request.form["room"].upper().strip()
    if room not in games:
        return "❌ Pokój nie istnieje. Wróć i utwórz nowy."
    return redirect(url_for("join_room", room=room))

@app.route("/room/<room>")
def join_room(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
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
            <form action="/play/{room}" method="post">
                <input name="player" placeholder="Twoje imię" required>
                <button type="submit">Dołącz i zobacz słowo</button>
            </form>
        </div>
    </body>
    </html>
    """)

# ===============================
# START GRY – WYŚWIETLENIE SŁOWA
# ===============================
@app.route("/play/<room>", methods=["POST"])
def play(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    
    player = request.form["player"]
    game = games[room]

    if player not in game["players"]:
        game["players"].append(player)

    if len(game["players"]) >= 3 and game["impostor"] is None:
        game["impostor"] = random.choice(game["players"])

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

# ===============================
# NOWA RUNDA
# ===============================
@app.route("/new_round/<room>", methods=["POST"])
def new_round(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    
    game = games[room]
    game["word"] = random.choice(WORDS)
    if len(game["players"]) >= 3:
        game["impostor"] = random.choice(game["players"])
    return redirect(url_for("join_room", room=room))

# ===============================
# START SERWERA
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
