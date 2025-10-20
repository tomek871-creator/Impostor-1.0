from flask import Flask, render_template, request, redirect, url_for, make_response
import random
import string
import uuid

app = Flask(__name__)

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
games = {}

# --- FUNKCJE POMOCNICZE ---
def generate_code(n=4):
    return ''.join(random.choices(string.ascii_uppercase, k=n))

def get_or_set_player_id():
    pid = request.cookies.get("player_id")
    if not pid:
        pid = str(uuid.uuid4())
    return pid

def find_player(game, pid):
    return next((p for p in game["players"] if p["id"] == pid), None)

# --- STRONA GŁÓWNA ---
@app.route("/", methods=["GET"])
def index():
    return render_template("base.html", page="index")

# --- TWORZENIE POKOJU ---
@app.route("/create", methods=["POST"])
def create():
    name = (request.form.get("name") or "Gracz").strip()[:20]
    req = (request.form.get("code") or "").strip().upper()
    code = req if req else generate_code()
    if code in games:
        return render_template("base.html", page="error", message=f"Pokój {code} już istnieje.")

    pid = get_or_set_player_id()
    games[code] = {
        "players": [{"id": pid, "name": name}],
        "host": pid,
        "started": False,
        "word": None,
        "impostor": None
    }
    resp = make_response(redirect(url_for("room", code=code)))
    resp.set_cookie("player_id", pid, httponly=True)
    return resp

# --- DOŁĄCZANIE DO POKOJU ---
@app.route("/room", methods=["POST"])
def join_redirect():
    room = (request.form.get("room") or "").strip().upper()
    name = (request.form.get("name") or "Gracz").strip()[:20]
    return redirect(url_for("room", code=room, name=name))

# --- STRONA POKOJU ---
@app.route("/room/<code>")
def room(code):
    name = (request.args.get("name") or "").strip()[:20]
    pid = get_or_set_player_id()

    if code not in games:
        return render_template("base.html", page="error", message=f"Pokój {code} nie istnieje.")

    game = games[code]

    # rejestracja gracza
    if name and not find_player(game, pid):
        if len(game["players"]) >= 8:
            return render_template("base.html", page="error", message=f"Pokój {code} jest pełny (max 8).")
        game["players"].append({"id": pid, "name": name})

    # gra trwa
    if game["started"]:
        is_imp = (pid == game["impostor"])
        word = "impostor" if is_imp else game["word"]
        return render_template("base.html", page="game", code=code, word=word, impostor=is_imp, host=find_player(game, game["host"])["name"])

    # lobby
    return render_template(
        "base.html",
        page="lobby",
        code=code,
        players=game["players"],
        is_host=(pid == game["host"])
    )

# --- START GRY ---
@app.route("/start/<code>", methods=["POST"])
def start(code):
    pid = get_or_set_player_id()
    if code not in games:
        return render_template("base.html", page="error", message="Pokój nie istnieje.")
    game = games[code]
    if pid != game["host"]:
        return render_template("base.html", page="error", message="Tylko host może rozpocząć grę.")
    n = len(game["players"])
    if n < 3:
        return render_template("base.html", page="error", message="Potrzeba minimum 3 graczy.")
    if n > 8:
        return render_template("base.html", page="error", message="Maksymalnie 8 graczy.")

    word = random.choice(WORDS)
    imp = random.choice(game["players"])["id"]
    game.update({"started": True, "word": word, "impostor": imp})
    return redirect(url_for("room", code=code))

# --- ZAGRAJ PONOWNIE ---
@app.route("/playagain/<code>", methods=["POST"])
def playagain(code):
    pid = get_or_set_player_id()
    if code not in games:
        return render_template("base.html", page="error", message="Pokój nie istnieje.")
    game = games[code]
    if pid != game["host"]:
        return render_template("base.html", page="error", message="Tylko host może rozpocząć ponownie.")
    if len(game["players"]) < 3:
        return render_template("base.html", page="error", message="Za mało graczy.")

    word = random.choice(WORDS)
    imp = random.choice(game["players"])["id"]
    game.update({"started": True, "word": word, "impostor": imp})
    return redirect(url_for("room", code=code))

# --- START SERWERA ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
