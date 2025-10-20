from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import random, json, os

app = Flask(__name__)

DATA_FILE = "/tmp/games.json"

# Funkcja wczytująca i zapisująca dane z pliku
def load_games():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_games(games):
    with open(DATA_FILE, "w") as f:
        json.dump(games, f)

# Lista słów (50% prostych, 50% poważniejszych)
WORDS = [
    "pies", "kot", "rower", "góra", "las", "morze", "zamek", "tęcza", "dinozaur", "robot",
    "księżyc", "chmura", "lampa", "okno", "szkoła", "telefon", "kwiat", "piłka", "muzyka", "góra lodowa",
    "samolot", "statek", "książka", "komputer", "drzewo", "słońce", "gwiazda", "magnes", "klucz", "drzwi",
    "mikroskop", "nauczyciel", "historia", "wolność", "sztuka", "architektura", "nauka", "filozofia", "muzeum", "społeczeństwo",
    "teoria", "wynalazek", "matematyka", "astronomia", "prawo", "biologia", "psychologia", "kultura", "edukacja", "odpowiedzialność"
]

games = load_games()

@app.route("/")
def index():
    return render_template_string("""
    <html>
    <head><title>Gra - Kim jest Impostorem?</title></head>
    <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
        <h1>Kim jest Impostorem?</h1>
        <form action="/create" method="post">
            <button type="submit">Utwórz pokój</button>
        </form>
        <hr>
        <form action="/join" method="post">
            <input name="code" placeholder="Kod pokoju" required>
            <button type="submit">Dołącz</button>
        </form>
    </body></html>
    """)

@app.route("/create", methods=["POST"])
def create_room():
    games = load_games()
    code = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))
    games[code] = {
        "players": [],
        "word": random.choice(WORDS),
        "impostor": None,
        "started": False
    }
    save_games(games)
    return redirect(url_for("lobby", code=code, host=1))

@app.route("/join", methods=["POST"])
def join_room():
    code = request.form["code"].strip().upper()
    games = load_games()
    if code not in games:
        return "Nie znaleziono pokoju", 404
    return redirect(url_for("lobby", code=code))

@app.route("/lobby/<code>")
def lobby(code):
    host = request.args.get("host")
    return render_template_string("""
    <html>
    <head>
        <title>Lobby {{code}}</title>
        <script>
        function refreshLobby() {
            fetch("/lobby_data/{{code}}")
                .then(r => r.json())
                .then(data => {
                    document.getElementById("players").innerText = data.players + " graczy w lobby";
                    if (data.started) window.location = "/game/{{code}}";
                });
        }
        setInterval(refreshLobby, 2000);
        </script>
    </head>
    <body style="text-align: center; font-family: sans-serif; padding-top: 50px;">
        <h1>Pokój: {{code}}</h1>
        <p id="players">Ładowanie...</p>
        {% if host %}
        <form action="/start/{{code}}" method="post">
            <button type="submit">Rozpocznij grę</button>
        </form>
        {% endif %}
        <script>refreshLobby()</script>
    </body></html>
    """, code=code, host=host)

@app.route("/lobby_data/<code>")
def lobby_data(code):
    games = load_games()
    game = games.get(code)
    if not game:
        return jsonify({"error": "not found"}), 404
    # Dodaj gracza jeśli nie istnieje w lobby
    ip = request.remote_addr
    if ip not in game["players"] and not game["started"]:
        game["players"].append(ip)
        save_games(games)
    return jsonify({
        "players": len(game["players"]),
        "started": game["started"]
    })

@app.route("/start/<code>", methods=["POST"])
def start_game(code):
    games = load_games()
    game = games.get(code)
    if not game:
        return "Nie znaleziono pokoju", 404
    if len(game["players"]) < 3:
        return "Za mało graczy (min. 3).", 400
    game["impostor"] = random.choice(game["players"])
    game["started"] = True
    save_games(games)
    return redirect(url_for("game", code=code))

@app.route("/game/<code>")
def game(code):
    games = load_games()
    game = games.get(code)
    if not game:
        return "Pokój nie istnieje", 404
    ip = request.remote_addr
    if ip not in game["players"]:
        return "Nie jesteś w tej grze", 403
    if game["impostor"] == ip:
        word = "❓ Jesteś IMPOSTOREM! Spróbuj udawać, że znasz słowo."
    else:
        word = f"🔤 Słowo: {game['word']}"
    return render_template_string(f"""
    <html>
    <head><title>Gra - {code}</title></head>
    <body style="text-align: center; font-family: sans-serif; padding-top: 50px;">
        <h2>Pokój: {code}</h2>
        <p>{word}</p>
        <p>Ustalcie kto jest impostorem!</p>
    </body></html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
