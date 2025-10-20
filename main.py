from flask import Flask, render_template_string, request, redirect, url_for
import random
import string

app = Flask(__name__)

# ------------------- DANE -------------------
WORDS = [
    "pies", "kot", "samochód", "rower", "dom", "telefon", "książka", "chleb",
    "szkoła", "kino", "komputer", "okno", "las", "morze", "zegar", "jabłko",
    "herbata", "kawa", "gitara", "muzyka", "taniec", "sport", "piłka", "krzesło"
]

games = {}

# ------------------- WYGLĄD STRONY -------------------
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Impostor — Gra słowna</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #121212;
            color: #f5f5f5;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        h1 { color: #00C896; }
        button {
            background-color: #00C896;
            border: none;
            color: white;
            padding: 10px 20px;
            font-size: 18px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover { background-color: #00A97F; }
        input {
            padding: 8px;
            font-size: 16px;
            border-radius: 6px;
            border: 1px solid #555;
            margin: 10px;
            text-align: center;
            background-color: #1f1f1f;
            color: #fff;
        }
        .card {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            display: inline-block;
            margin-top: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.4);
        }
        a {
            color: #00C896;
            text-decoration: none;
        }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
"""

# ------------------- STRONY -------------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        num_players = int(request.form["players"])
        game_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        word = random.choice(WORDS)
        impostor = random.randint(1, num_players)

        games[game_id] = {
            "word": word,
            "players": num_players,
            "impostor": impostor
        }

        return redirect(url_for("lobby", game_id=game_id))

    return render_template_string(PAGE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <h1>🎮 Impostor — Gra słowna</h1>
    <form method="POST">
        <p>Podaj liczbę graczy (3–8):</p>
        <input type="number" name="players" min="3" max="8" required>
        <br>
        <button type="submit">Stwórz grę</button>
    </form>
    """))

@app.route("/lobby/<game_id>")
def lobby(game_id):
    if game_id not in games:
        return "Nie znaleziono gry 😢", 404
    game = games[game_id]
    return render_template_string(PAGE_TEMPLATE.replace("{% block content %}{% endblock %}", f"""
    <h1>🔢 Kod gry: {game_id}</h1>
    <p>Liczba graczy: {game['players']}</p>
    <p><b>Każdy gracz niech wejdzie na ten sam link:</b></p>
    <div class="card">
        <p>👉 <a href='{url_for("play", game_id=game_id, _external=True)}'>{url_for("play", game_id=game_id, _external=True)}</a></p>
    </div>
    """))

@app.route("/play/<game_id>")
def play(game_id):
    if game_id not in games:
        return "Nie znaleziono gry 😢", 404
    game = games[game_id]
    player_id = random.randint(1, game["players"])
    if player_id == game["impostor"]:
        word = "IMPOSTOR"
    else:
        word = game["word"]
    return render_template_string(PAGE_TEMPLATE.replace("{% block content %}{% endblock %}", f"""
    <div class="card">
        <h2>Twój numer gracza: {player_id}</h2>
        <h3>Twoje słowo:</h3>
        <h1>{word}</h1>
    </div>
    <br>
    <a href='{url_for("lobby", game_id=game_id)}'>
        <button>🔁 Zagraj ponownie</button>
    </a>
    """))

# ------------------- URUCHOMIENIE -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
