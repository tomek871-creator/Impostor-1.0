from flask import Flask, request, render_template_string, redirect, make_response
import random
import uuid

app = Flask(__name__)

games = {}

WORDS = [
    # 50% proste, 50% poważniejsze
    "pies", "kot", "telefon", "szkoła", "kwiat", "auto", "książka", "drzewo", "morze", "niebo",
    "komputer", "samolot", "rower", "kubek", "herbata", "pizza", "frytki", "ryba", "słońce", "księżyc",
    "zegar", "krzesło", "dom", "ogród", "buty", "plecak", "długopis", "zeszyt", "stół", "okno",
    "muzyka", "film", "gra", "sport", "piłka", "góry", "morze", "plaża", "śnieg", "deszcz",
    "dyrektor", "mechanizm", "nauka", "ekonomia", "społeczeństwo", "strategia", "komunikacja", "dyskusja", "organizacja", "projekt",
    "wolność", "odpowiedzialność", "moralność", "polityka", "technologia", "sztuka", "psychologia", "muzeum", "historia", "natura",
    "energia", "system", "analiza", "rozwiązanie", "edukacja", "cywilizacja", "emocje", "marzenie", "przyszłość", "zmiana"
]

# ------------------ STRONA GŁÓWNA ------------------
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
            <p>Lub dołącz do istniejącego pokoju:</p>
            <form onsubmit="event.preventDefault(); window.location='/room/' + document.querySelector('[name=room]').value.toUpperCase();">
                <input name="room" placeholder="Kod pokoju" required>
                <button type="submit">➡️ Dołącz</button>
            </form>
        </div>
    </body>
    </html>
    """)

# ------------------ TWORZENIE GRY ------------------
@app.route("/create", methods=["POST"])
def create_game():
    room = request.form["room"].strip().upper()
    if room in games:
        return f"❌ Pokój {room} już istnieje."

    games[room] = {
        "word": random.choice(WORDS),
        "players": set(),
        "impostor": None,
        "started": False
    }
    return redirect(f"/room/{room}")

# ------------------ LOBBY ------------------
@app.route("/room/<room>")
def room_lobby(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    
    game = games[room]
    player_id = request.cookies.get("player_id")
    if not player_id:
        player_id = str(uuid.uuid4())

    # Dodaj gracza (identyfikacja po ciasteczku)
    game["players"].add(player_id)

    resp = make_response(render_template_string(f"""
    <html>
    <head>
        <title>Lobby {room}</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body {{ background-color: #121212; color: white; font-family: Arial; text-align: center; margin-top: 10%; }}
            button {{ background-color: #4caf50; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; margin-top: 20px; }}
            button:hover {{ background-color: #388e3c; }}
            .box {{ background-color: #1e1e1e; padding: 30px; border-radius: 12px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Pokój: {room}</h2>
            <p>Graczy w pokoju: {len(game["players"])}</p>
            {"<form action='/start/" + room + "' method='post'><button type='submit'>🎬 Start</button></form>" if not game["started"] else "<p>Gra rozpoczęta!</p>"}
        </div>
    </body>
    </html>
    """))
    resp.set_cookie("player_id", player_id)
    return resp

# ------------------ START GRY ------------------
@app.route("/start/<room>", methods=["POST"])
def start_game(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    game = games[room]
    if len(game["players"]) < 3:
        return "❗ Potrzeba co najmniej 3 graczy."

    game["started"] = True
    game["impostor"] = random.choice(list(game["players"]))
    return redirect(f"/play/{room}")

# ------------------ EKRAN GRY ------------------
@app.route("/play/<room>")
def play(room):
    if room not in games:
        return "❌ Pokój nie istnieje."
    
    game = games[room]
    player_id = request.cookies.get("player_id")

    if not player_id or player_id not in game["players"]:
        return redirect(f"/room/{room}")

    if not game["started"]:
        return redirect(f"/room/{room}")

    if player_id == game["impostor"]:
        word = "IMPOSTOR 😈"
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
        <h1>Twoje słowo:</h1>
        <p class="word">{word}</p>
        <form action="/new_round/{room}" method="post">
            <button type="submit">🔁 Nowa runda</button>
        </form>
    </body>
    </html>
    """)

# ------------------ NOWA RUNDA ------------------
@app.route("/new_round/<room>", methods=["POST"])
def new_round(room):
    if room not in games:
        return "❌ Pokój nie istnieje."

    game = games[room]
    game["word"] = random.choice(WORDS)
    game["impostor"] = random.choice(list(game["players"]))
    game["started"] = True

    return redirect(f"/play/{room}")

# ------------------ START SERWERA ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
