from flask import Flask, render_template, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key = "tajny_klucz_gry_123"  # potrzebne do ciasteczek (sesji)

# --- LISTA SŁÓW ---
WORDS = [
    "pies", "kot", "samochód", "książka", "telefon", "komputer", "drzewo", "krzesło", "kwiat", "morze",
    "szkoła", "film", "pociąg", "samolot", "księżyc", "słońce", "muzyka", "las", "dom", "buty",
    "szpital", "muzeum", "ogród", "taniec", "mleko", "ryba", "rower", "talerz", "lampa",
    "kosmos", "podróż", "ciasto", "kuchnia", "miasto", "wieża", "teatr", "kościół", "rzeka", "burza",
    "minister", "nauczyciel", "architekt", "dokument", "system", "ekonomia", "konflikt", "prawo", "wolność", "kultura",
    "strategia", "dyskusja", "społeczeństwo", "nauka", "technologia", "projekt", "artysta", "poeta", "muzyk", "aktor"
]

# --- DANE O GRACH ---
games = {}  # {code: {players: [{"id": cookie_id, "name": nick}], host_id, started, word, impostor_id}}

# --- STRONA GŁÓWNA ---
@app.route("/")
def index():
    return render_template("base.html", page="index")

# --- FUNKCJA DO GENEROWANIA UNIKALNEGO ID GRACZA ---
def get_player_id():
    if "player_id" not in session:
        session["player_id"] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return session["player_id"]

# --- TWORZENIE POKOJU ---
@app.route("/create", methods=["POST"])
def create():
    name = request.form.get("name", "").strip()
    custom_code = request.form.get("code", "").strip().upper()
    code = custom_code if custom_code else ''.join(random.choices(string.ascii_uppercase, k=4))

    player_id = get_player_id()

    if code not in games:
        games[code] = {
            "players": [],
            "host_id": player_id,
            "started": False,
            "word": None,
            "impostor_id": None
        }

    game = games[code]
    if not any(p["id"] == player_id for p in game["players"]):
        game["players"].append({"id": player_id, "name": name})

    return redirect(f"/room/{code}")

# --- DOŁĄCZANIE DO POKOJU ---
@app.route("/room", methods=["POST"])
def room_redirect():
    name = request.form.get("name", "").strip()
    code = request.form.get("room", "").strip().upper()

    if not code or code not in games:
        return render_template("base.html", page="error", message="Pokój nie istnieje!")

    player_id = get_player_id()
    game = games[code]

    if len(game["players"]) >= 8:
        return render_template("base.html", page="error", message="Pokój jest pełny!")

    if not any(p["id"] == player_id for p in game["players"]):
        game["players"].append({"id": player_id, "name": name})

    return redirect(f"/room/{code}")

# --- STRONA POKOJU ---
@app.route("/room/<code>")
def room(code):
    if code not in games:
        return render_template("base.html", page="error", message="Pokój nie istnieje!")

    player_id = get_player_id()
    game = games[code]

    # Gra rozpoczęta
    if game["started"]:
        is_impostor = player_id == game["impostor_id"]
        word = "impostor" if is_impostor else game["word"]
        return render_template("base.html", page="game", code=code, impostor=is_impostor, word=word)

    # Lobby
    players = game["players"]
    is_host = player_id == game["host_id"]
    return render_template("base.html", page="lobby", code=code, players=players, is_host=is_host)

# --- START GRY ---
@app.route("/start/<code>", methods=["POST"])
def start(code):
    if code not in games:
        return render_template("base.html", page="error", message="Pokój nie istnieje!")

    game = games[code]
    if len(game["players"]) < 3:
        return render_template("base.html", page="error", message="Potrzeba co najmniej 3 graczy!")

    impostor = random.choice(game["players"])
    word = random.choice(WORDS)

    game["started"] = True
    game["word"] = word
    game["impostor_id"] = impostor["id"]

    return redirect(f"/room/{code}")

# --- ZAGRAJ PONOWNIE ---
@app.route("/playagain/<code>", methods=["POST"])
def play_again(code):
    if code not in games:
        return render_template("base.html", page="error", message="Pokój nie istnieje!")

    game = games[code]
    if len(game["players"]) < 3:
        return render_template("base.html", page="error", message="Za mało graczy!")

    impostor = random.choice(game["players"])
    word = random.choice(WORDS)

    game["started"] = True
    game["word"] = word
    game["impostor_id"] = impostor["id"]

    return redirect(f"/room/{code}")

# --- URUCHOMIENIE ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
