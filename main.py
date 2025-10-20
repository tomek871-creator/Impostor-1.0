from flask import Flask, request, render_template_string, redirect, make_response
import random, json, os, uuid

app = Flask(__name__)
DATA_FILE = "games.json"


# ----------------- Pomocnicze funkcje -----------------
def load_games():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_games(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


# ----------------- Lista słów -----------------
WORDS = [
    "pies","kot","rower","zamek","tęcza","robot","księżyc","szkoła","telefon","piłka",
    "muzyka","drzewo","słońce","gwiazda","klucz","okno","samolot","książka","komputer","morze",
    "mikroskop","nauczyciel","historia","wolność","sztuka","architektura","nauka","filozofia","muzeum","społeczeństwo",
    "teoria","wynalazek","matematyka","astronomia","prawo","biologia","psychologia","kultura","edukacja","odpowiedzialność"
]


# ----------------- Strona główna -----------------
@app.route("/")
def index():
    return render_template_string("""
    <html><body style="text-align:center;font-family:sans-serif;margin-top:10%;">
        <h1>🎭 Kim jest Impostorem?</h1>
        <form action="/create" method="post">
            <button type="submit">🆕 Stwórz pokój</button>
        </form>
        <hr>
        <form action="/room" method="get">
            <input name="room" placeholder="Kod pokoju" required>
            <button type="submit">➡️ Dołącz</button>
        </form>
    </body></html>
    """)


# ----------------- Tworzenie pokoju -----------------
@app.route("/create", methods=["POST"])
def create_game():
    games = load_games()
    code = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))
    games[code] = {
        "word": random.choice(WORDS),
        "players": [],
        "impostor": None,
        "started": False,
        "host": None
    }
    save_games(games)
    return redirect(f"/room/{code}")


# ----------------- Dołączanie do pokoju -----------------
@app.route("/room/<room>")
def join_room(room):
    games = load_games()
    if room not in games:
        return "❌ Pokój nie istnieje."

    game = games[room]

    # pobierz lub utwórz unikalny identyfikator gracza
    player_id = request.cookies.get("player_id")
    if not player_id:
        player_id = str(uuid.uuid4())

    # przypisz hosta, jeśli to pierwszy gracz
    if game["host"] is None:
        game["host"] = player_id

    # dodaj gracza, jeśli go nie ma
    if player_id not in game["players"]:
        game["players"].append(player_id)
        save_games(games)

    players = len(game["players"])
    is_host = (player_id == game["host"])

    # jeśli gra już wystartowała, przekieruj do słowa
    if game["started"]:
        resp = make_response(redirect(f"/play/{room}"))
        resp.set_cookie("player_id", player_id)
        return resp

    start_button = ""
    if is_host:
        start_button = f"""
        <form action="/start/{room}" method="post">
            <button type="submit" style="padding:10px 20px;font-size:18px;">🚀 Start gry</button>
        </form>
        """

    html = f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="3">
    </head>
    <body style="text-align:center;font-family:sans-serif;margin-top:10%;">
        <h2>Pokój: {room}</h2>
        <p>Graczy w pokoju: {players}</p>
        {"<p>Jesteś hostem 👑</p>" if is_host else ""}
        {start_button}
        <p>Oczekiwanie na rozpoczęcie gry...</p>
    </body></html>
    """

    resp = make_response(html)
    resp.set_cookie("player_id", player_id)
    return resp


# ----------------- Host startuje grę -----------------
@app.route("/start/<room>", methods=["POST"])
def start_game(room):
    games = load_games()
    if room not in games:
        return "❌ Pokój nie istnieje."

    game = games[room]
    player_id = request.cookies.get("player_id")

    if player_id != game["host"]:
        return redirect(f"/room/{room}")

    if len(game["players"]) < 3:
        return f"<h3>❌ Potrzeba co najmniej 3 graczy, aby rozpocząć grę.</h3><a href='/room/{room}'>⬅️ Powrót</a>"

    game["impostor"] = random.choice(game["players"])
    game["started"] = True
    save_games(games)

    return redirect(f"/play/{room}")


# ----------------- Ekran ze słowem -----------------
@app.route("/play/<room>")
def play(room):
    games = load_games()
    if room not in games:
        return "❌ Pokój nie istnieje."

    game = games[room]
    player_id = request.cookies.get("player_id")

    if player_id not in game["players"]:
        return redirect(f"/room/{room}")

    if not game["started"]:
        return redirect(f"/room/{room}")

    word = "IMPOSTOR" if player_id == game["impostor"] else game["word"]

    return render_template_string(f"""
    <html><body style="text-align:center;font-family:sans-serif;margin-top:10%;">
        <h2>Twoje słowo:</h2>
        <h1 style="color:#4caf50;">{word}</h1>
        <p>Nie pokazuj innym! 😎</p>
        <a href="/room/{room}">⬅️ Powrót do lobby</a>
    </body></html>
    """)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
