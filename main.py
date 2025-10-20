from flask import Flask, render_template_string, request, redirect, url_for, session
import random, string

app = Flask(__name__)
app.secret_key = "tajnehaslo"  # wymagane, by działała sesja

# === Lista słów do gry ===
words = [
    "kot", "pies", "dom", "rower", "telefon", "szkoła", "pizza", "lody",
    "film", "las", "morze", "góry", "książka", "samochód", "kawa", "herbata",
    "gitara", "komputer", "kwiat", "okno", "drzewo", "muzyka", "park", "śnieg",
    "słońce", "miasto", "autobus", "kino", "taniec", "sala", "biurko", "nauka"
]

# === Dane o grach ===
games = {}

# === Szablon HTML (ciemny motyw, mobile style) ===
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Impostor Game</title>
<style>
body { background:#121212; color:white; font-family:sans-serif; text-align:center; margin:0; padding:0; }
.container { max-width:400px; margin:auto; padding:20px; }
button { background:#1e88e5; color:white; border:none; padding:12px 20px;
  border-radius:10px; margin:10px; cursor:pointer; font-size:18px; width:80%; }
input { padding:10px; border-radius:8px; border:none; text-align:center; width:80%; margin:5px; font-size:16px; }
.card { background:#1e1e1e; padding:20px; border-radius:15px; margin-top:20px; }
</style>
</head>
<body>
<div class="container">
{% block content %}{% endblock %}
</div>
</body>
</html>
"""

# === Strona główna ===
@app.route("/")
def index():
    return render_template_string(PAGE_TEMPLATE + """
    {% block content %}
    <h2>🎮 Impostor Game</h2>
    <form action="/create" method="post">
      <input name="room_code" placeholder="Wpisz kod pokoju (np. TEAM5)" maxlength="5">
      <button type="submit">🆕 Stwórz pokój</button>
    </form>
    <form action="/join" method="post">
      <input name="room_code" placeholder="Dołącz do pokoju (np. TEAM5)" maxlength="5">
      <input name="player_name" placeholder="Twoje imię">
      <button type="submit">🔗 Dołącz</button>
    </form>
    {% endblock %}
    """)

# === Tworzenie nowego pokoju ===
@app.route("/create", methods=["POST"])
def create_game():
    custom_code = request.form.get("room_code", "").strip().upper()
    code = custom_code if custom_code else ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    if code in games:
        return render_template_string(PAGE_TEMPLATE + """
        {% block content %}
        <p>⚠️ Pokój {{code}} już istnieje. Spróbuj inny kod.</p>
        <a href="/">⬅️ Wróć</a>
        {% endblock %}
        """, code=code)

    games[code] = {"players": [], "word": random.choice(words), "impostor": None}
    session["player_name"] = "HOST"
    session["room_code"] = code
    return redirect(url_for("play", code=code))

# === Dołączanie do pokoju ===
@app.route("/join", methods=["POST"])
def join_game():
    code = request.form.get("room_code", "").strip().upper()
    name = request.form.get("player_name", "").strip()
    if not code or not name:
        return redirect(url_for("index"))

    if code not in games:
        return render_template_string(PAGE_TEMPLATE + """
        {% block content %}
        <p>❌ Pokój {{code}} nie istnieje.</p>
        <a href="/">⬅️ Wróć</a>
        {% endblock %}
        """, code=code)

    games[code]["players"].append({"name": name, "word": None})
    session["player_name"] = name
    session["room_code"] = code
    return redirect(url_for("play", code=code))

# === Strona pokoju ===
@app.route("/play/<code>")
def play(code):
    if code not in games:
        return redirect(url_for("index"))
    game = games[code]

    # Gdy gra gotowa (min. 3 graczy) i jeszcze nie wylosowano impostora
    if len(game["players"]) >= 3 and game["impostor"] is None:
        game["word"] = random.choice(words)
        impostor_index = random.randint(0, len(game["players"]) - 1)
        game["impostor"] = impostor_index
        for i, player in enumerate(game["players"]):
            player["word"] = "IMPOSTOR" if i == impostor_index else game["word"]

    player_list = "".join([f"<li>{p['name']}</li>" for p in game["players"]])
    return render_template_string(PAGE_TEMPLATE + f"""
    {% block content %}
    <h3>Pokój: {code}</h3>
    <div class="card">
        <p>Gracze:</p>
        <ul style="list-style:none; padding:0;">{player_list}</ul>
        <a href="/word/{code}"><button>🔍 Zobacz swoje słowo</button></a>
        <a href="/restart/{code}"><button>🔁 Zagraj ponownie</button></a>
    </div>
    {% endblock %}
    """)

# === Wyświetlanie słowa danego gracza ===
@app.route("/word/<code>")
def word(code):
    if code not in games:
        return redirect(url_for("index"))

    game = games[code]
    name = session.get("player_name")
    if not name:
        return redirect(url_for("index"))

    # znajdź gracza
    player = next((p for p in game["players"] if p["name"] == name), None)
    if not player:
        return redirect(url_for("index"))

    word_text = player["word"] or "Czekaj na start..."
    return render_template_string(PAGE_TEMPLATE + f"""
    {% block content %}
    <div class="card">
        <h3>Twoje słowo:</h3>
        <h1 style="color:#ffcc00;">{word_text}</h1>
        <a href="/play/{code}"><button>⬅️ Wróć</button></a>
    </div>
    {% endblock %}
    """)

# === Nowa runda ===
@app.route("/restart/<code>")
def restart(code):
    if code in games:
        game = games[code]
        game["word"] = random.choice(words)
        game["impostor"] = None
        for player in game["players"]:
            player["word"] = None
    return redirect(url_for("play", code=code))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
