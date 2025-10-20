from flask import Flask, render_template_string, request, redirect, url_for, session
import random, string, os

app = Flask(__name__)
app.secret_key = "tajnyklucz"  # możesz wpisać cokolwiek

# --- Słowa do gry ---
WORDS = [
    "kot", "pies", "samochód", "telefon", "szkoła",
    "jabłko", "książka", "lampa", "chleb", "dom"
]

# --- Dane gry ---
games = {}

# --- Wygląd strony (HTML + CSS) ---
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
    color: #f1f1f1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    margin: 0;
}
.container {
    text-align: center;
    max-width: 400px;
    padding: 20px;
    background: #1e1e1e;
    border-radius: 20px;
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
}
button {
    background-color: #03dac6;
    border: none;
    padding: 10px 20px;
    font-size: 18px;
    border-radius: 10px;
    margin-top: 15px;
    cursor: pointer;
    color: #000;
}
button:hover {
    background-color: #00bfa5;
}
input {
    padding: 10px;
    width: 80%;
    border-radius: 8px;
    border: none;
    margin-top: 10px;
}
a {
    color: #03dac6;
    text-decoration: none;
}
</style>
</head>
<body>
<div class="container">
    {% block content %}{% endblock %}
</div>
</body>
</html>
"""

# --- Strona główna ---
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

    return render_template_string(PAGE_TEMPLATE + """
    {% block content %}
    <h1>🎮 Impostor — Gra słowna</h1>
    <form method="POST">
        <p>Podaj liczbę graczy (3–8):</p>
        <input type="number" name="players" min="3" max="8" required>
        <br>
        <button type="submit">Stwórz grę</button>
    </form>
    {% endblock %}
    """)

# --- Lobby gry (link do udostępnienia graczom) ---
@app.route("/lobby/<game_id>")
def lobby(game_id):
    link = request.url_root + "game/" + game_id + "/"
    return render_template_string(PAGE_TEMPLATE + """
    {% block content %}
    <h2>🕹 Kod gry: <span style="color:#03dac6;">{{ game_id }}</span></h2>
    <p>Udostępnij ten link graczom:</p>
    <p><a href="{{ link }}">{{ link }}</a></p>
    <p>Każdy gracz wpisuje ten link i swój numer (1–{{ players }})</p>
    {% endblock %}
    """, game_id=game_id, players=games[game_id]["players"], link=link)

# --- Strona gracza ---
@app.route("/game/<game_id>/", methods=["GET", "POST"])
def game(game_id):
    game = games.get(game_id)
    if not game:
        return "Gra nie istnieje 😢", 404

    if request.method == "POST":
        player_num = int(request.form["player"])
        if player_num == game["impostor"]:
            word = "IMPOSTOR"
        else:
            word = game["word"]

        return render_template_string(PAGE_TEMPLATE + """
        {% block content %}
        <h2>Twoje słowo:</h2>
        <h1 style="color:#03dac6;">{{ word }}</h1>
        <p>Nie pokazuj nikomu swojego słowa!</p>
        <a href="/">🔁 Nowa runda</a>
        {% endblock %}
        """, word=word)

    return render_template_string(PAGE_TEMPLATE + """
    {% block content %}
    <h2>Dołącz do gry</h2>
    <p>Kod gry: <span style="color:#03dac6;">{{ game_id }}</span></p>
    <form method="POST">
        <p>Podaj swój numer gracza (1–{{ players }}):</p>
        <input type="number" name="player" min="1" max="{{ players }}" required>
        <br>
        <button type="submit">Pokaż słowo</button>
    </form>
    {% endblock %}
    """, game_id=game_id, players=game["players"])

# --- Uruchomienie na Renderze / lokalnie ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
