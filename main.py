from flask import Flask, request, redirect, render_template_string, jsonify, make_response
import random
import string

app = Flask(__name__)

# ===============================
#  LISTA SŁÓW (50% prostych, 50% poważniejszych)
# ===============================
WORDS = [
    # proste
    "pies", "kot", "rower", "las", "telefon", "szkoła", "książka", "pociąg", "cukierek", "chmura",
    "morze", "zamek", "samolot", "kwiat", "miasto", "komputer", "pudełko", "zegarek", "słońce", "śnieg",
    "muzyka", "ulica", "auto", "długopis", "okno", "krzesło", "stół", "jabłko", "drzewo", "zupa",
    "ryba", "król", "królowa", "ogród", "pociąg", "plecak", "szalik", "czapka", "piłka", "piesek",
    "most", "dom", "góra", "kawa", "herbata", "zegar", "film", "obraz", "sklep", "buty",
    # poważniejsze
    "wolność", "technologia", "sprawiedliwość", "ambicja", "historia", "dyplomacja", "emocje", "odwaga", "strategia", "wiedza",
    "filozofia", "mechanika", "społeczeństwo", "komunikacja", "ekonomia", "fizyka", "energia", "polityka", "muzeum", "inspiracja",
    "relacja", "kultura", "sztuka", "matematyka", "psychologia", "biologia", "muzykologia", "świadomość", "analiza", "astronomia",
    "cywilizacja", "innowacja", "wartość", "honor", "dyscyplina", "motywacja", "organizacja", "równość", "empatia", "odpowiedzialność",
    "współpraca", "przyjaźń", "rozsądek", "edukacja", "wspólnota", "przyszłość", "autorytet", "badania", "technika", "etyka"
]

# ===============================
#  DANE GIER (trzymane w RAM)
# ===============================
games = {}

# ===============================
#  STRONA GŁÓWNA
# ===============================
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

            <form id="createForm" action="/create" method="post">
                <p>Wpisz kod pokoju (opcjonalnie) lub zostaw puste, aby wylosować:</p>
                <input name="room" placeholder="Kod pokoju (opcjonalnie)">
                <button type="submit">🆕 Stwórz pokój</button>
            </form>

            <hr style="margin: 20px 0; opacity: 0.3;">

            <p>Lub dołącz do istniejącego pokoju:</p>
            <form id="joinForm" onsubmit="event.preventDefault(); 
                        const code = document.querySelector('[name=join_room]').value.trim().toUpperCase();
                        if(!code) return alert('Podaj kod pokoju');
                        window.location = '/room/' + encodeURIComponent(code);">
                <input name="join_room" placeholder="Kod pokoju" required>
                <button type="submit">➡️ Dołącz</button>
            </form>
        </div>
    </body>
    </html>
    """)

# ===============================
#  TWORZENIE POKOJU
# ===============================
@app.route("/create", methods=["POST"])
def create_game():
    given = request.form.get("room", "").strip().upper()
    if given:
        room = given
    else:
        room = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))

    while room in games:
        room = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))

    games[room] = {
        "word": random.choice(WORDS),
        "players": [],
        "impostor": None,
        "started": False
    }

    link = request.host_url.rstrip("/") + f"/room/{room}"
    return render_template_string(f"""
    <html><body style="font-family:Arial;text-align:center;margin-top:40px;">
        <h2>✅ Pokój utworzony: {room}</h2>
        <p>Wyślij ten link znajomym:</p>
        <p><a href="{link}">{link}</a></p>
        <p><a href="/">⬅️ Powrót</a></p>
    </body></html>
    """)

# ===============================
#  WEJŚCIE DO POKOJU
# ===============================
@app.route("/room/<room>")
def room_page(room):
    if room not in games:
        return f"❌ Pokój {room} nie istnieje", 404

    res = make_response(render_template_string("""
    <html>
    <head>
        <title>Pokój {{ room }}</title>
        <style>
            body { background:#111; color:white; font-family:Arial; text-align:center; margin-top:5%; }
            button { background:#03a9f4; border:none; color:white; padding:10px 20px; border-radius:8px; cursor:pointer; }
            button:hover { background:#0288d1; }
            #players { margin-top:20px; }
        </style>
    </head>
    <body>
        <h1>Pokój {{ room }}</h1>
        <p id="status">Oczekiwanie na rozpoczęcie gry...</p>
        <div id="players"></div>
        <button id="startBtn" onclick="startGame()">▶️ Start</button>

        <script>
        const room = "{{ room }}";
        document.cookie = "player_id=" + Math.random().toString(36).substring(2);

        async function refresh() {
            const r = await fetch("/status/" + room);
            const data = await r.json();
            document.getElementById("players").innerHTML = "<p>Gracze: " + data.players.length + "</p>";

            if (data.started) {
                window.location = "/play/" + room;
            }

            setTimeout(refresh, 2000);
        }
        refresh();

        async function startGame() {
            await fetch("/start/" + room);
            window.location = "/play/" + room;
        }
        </script>
    </body>
    </html>
    """, room=room))
    res.set_cookie("room", room)
    return res

# ===============================
#  STATUS GRY
# ===============================
@app.route("/status/<room>")
def status(room):
    game = games.get(room)
    if not game:
        return jsonify({"error": "no_room"}), 404
    return jsonify({"players": game["players"], "started": game["started"]})

# ===============================
#  START GRY
# ===============================
@app.route("/start/<room>")
def start(room):
    game = games.get(room)
    if not game or game["started"]:
        return "❌ Gra już trwa lub pokój nie istnieje", 400

    players = game["players"]
    if len(players) < 3:
        return "❌ Potrzeba co najmniej 3 graczy", 400

    impostor = random.choice(players)
    game["impostor"] = impostor
    game["started"] = True
    return "✅ Gra rozpoczęta!"

# ===============================
#  ROZGRYWKA
# ===============================
@app.route("/play/<room>")
def play(room):
    player_id = request.cookies.get("player_id")
    game = games.get(room)
    if not game:
        return "❌ Pokój nie istnieje", 404

    # jeśli gracz jeszcze nie jest na liście — dopisz
    if player_id not in game["players"]:
        game["players"].append(player_id)

    # losowanie słowa
    word = game["word"] if player_id != game["impostor"] else "INNE SŁOWO (impostor)"

    return render_template_string("""
    <html><body style="font-family:Arial;text-align:center;margin-top:10%;">
        <h2>Twoje słowo:</h2>
        <h1 style="font-size:50px;">{{ word }}</h1>
        <p>Nie pokazuj nikomu!</p>
    </body></html>
    """, word=word)

# ===============================
#  URUCHOMIENIE
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
