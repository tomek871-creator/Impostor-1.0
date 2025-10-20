from flask import Flask, render_template_string, request, redirect, url_for, make_response
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

# --- STYL I SZABLON ---
BASE_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Impostor</title>
<style>
  html,body { height:100%; margin:0; font-family:Arial,Helvetica,sans-serif; background:#000; color:#fff; }
  .wrap{ max-width:900px; margin:24px auto; padding:20px; background: rgba(255,255,255,0.02); border-radius:12px; }
  input,button { padding:10px; border-radius:8px; border:1px solid #222; background:#111; color:#fff; }
  .muted{ color:#bbb; font-size:14px; }
  .players { margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; }
  .player { background:#111; padding:8px 12px; border-radius:8px; border:1px solid #222; }
  .host-badge { background:#00d084; color:#000; padding:2px 6px; border-radius:999px; font-size:12px; margin-left:8px; }
  .word { display:inline-block; margin-top:12px; padding:10px 12px; border-radius:10px; background:#0f0; color:#000; font-weight:bold; }
  .impostor { display:inline-block; margin-top:12px; padding:10px 12px; border-radius:10px; background:#900; color:#fff; font-weight:bold; }
  .msg { margin-top:12px; padding:8px; background: rgba(255,255,255,0.02); border-radius:8px; }
  a.btn { text-decoration:none; display:inline-block; padding:8px 12px; border-radius:8px; background:#222; color:#fff; }
</style>
</head>
<body>
<div class="wrap">
  {{ body }}
</div>
</body>
</html>
"""

# --- POMOCNICZE FUNKCJE ---
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
    body = """
    <h1>Gra: Impostor</h1>
    <p class="muted">Twórz lub dołączaj do pokoi. Gra działa dla 3–8 graczy. Impostor otrzymuje słowo <b>"impostor"</b>.</p>

    <h3>Utwórz pokój</h3>
    <form action="/create" method="post">
      <label>Twój nick: <input name="name" required></label>
      <label>Kod pokoju (opcjonalnie): <input name="code" maxlength="6"></label>
      <button type="submit">Utwórz</button>
    </form>

    <h3>Dołącz</h3>
    <form action="/room" method="post">
      <label>Twój nick: <input name="name" required></label>
      <label>Kod pokoju: <input name="room" required></label>
      <button type="submit">Dołącz</button>
    </form>
    """
    return render_template_string(BASE_HTML, body=body)

# --- TWORZENIE POKOJU ---
@app.route("/create", methods=["POST"])
def create():
    name = (request.form.get("name") or "Gracz").strip()[:20]
    req = (request.form.get("code") or "").strip().upper()
    code = req if req else generate_code()
    if code in games:
        return render_template_string(BASE_HTML, body=f"<p>Pokój {code} już istnieje.</p><a href='/' class='btn'>Powrót</a>")

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
        return render_template_string(BASE_HTML, body=f"<h2>Pokój {code} nie istnieje.</h2><a href='/' class='btn'>Powrót</a>")

    game = games[code]

    # rejestracja gracza
    if name and not find_player(game, pid):
        if len(game["players"]) >= 8:
            return render_template_string(BASE_HTML, body=f"<p>Pokój {code} jest pełny (max 8).</p><a href='/' class='btn'>Powrót</a>")
        game["players"].append({"id": pid, "name": name})

    # gra trwa
    if game["started"]:
        is_imp = (pid == game["impostor"])
        if is_imp:
            word = "<span class='impostor'>Słowo: impostor</span>"
        else:
            word = f"<span class='word'>Twoje słowo: {game['word']}</span>"
        body = f"""
            <h2>Pokój: {code}</h2>
            <div class='msg'>{word}</div>
            <p class='muted'>Host: {find_player(game, game['host'])['name']}</p>
            <a href='/' class='btn'>Wyjdź</a>
        """
        resp = make_response(render_template_string(BASE_HTML, body=body))
        resp.set_cookie("player_id", pid, httponly=True)
        return resp

    # lobby
    players_html = "".join(
        f"<div class='player'>{p['name']}{' <span class=host-badge>HOST</span>' if p['id']==game['host'] else ''}</div>"
        for p in game["players"]
    )
    start_btn = ""
    if pid == game["host"]:
        start_btn = f"""
            <form action="/start/{code}" method="post" style="display:inline-block;">
              <button type="submit">Rozpocznij grę</button>
            </form>
            <form action="/playagain/{code}" method="post" style="display:inline-block;margin-left:8px;">
              <button type="submit">Zagraj ponownie</button>
            </form>
        """
    body = f"""
        <h2>Pokój: {code}</h2>
        <p>Liczba graczy: {len(game["players"])} (min 3, max 8)</p>
        <div class="players">{players_html}</div>
        <div class="msg">{start_btn}</div>
        <a href="/" class="btn">Wyjdź</a>
    """
    resp = make_response(render_template_string(BASE_HTML, body=body))
    resp.set_cookie("player_id", pid, httponly=True)
    return resp

# --- START GRY ---
@app.route("/start/<code>", methods=["POST"])
def start(code):
    pid = get_or_set_player_id()
    if code not in games:
        return "Pokój nie istnieje", 400
    game = games[code]
    if pid != game["host"]:
        return "Tylko host może rozpocząć", 403
    n = len(game["players"])
    if n < 3:
        return "Potrzeba minimum 3 graczy", 400
    if n > 8:
        return "Maksymalnie 8 graczy", 400

    word = random.choice(WORDS)
    imp = random.choice(game["players"])["id"]
    game.update({"started": True, "word": word, "impostor": imp})
    return redirect(url_for("room", code=code))

# --- ZAGRAJ PONOWNIE ---
@app.route("/playagain/<code>", methods=["POST"])
def playagain(code):
    pid = get_or_set_player_id()
    if code not in games:
        return "Pokój nie istnieje", 400
    game = games[code]
    if pid != game["host"]:
        return "Tylko host może rozpocząć ponownie", 403
    if len(game["players"]) < 3:
        return "Za mało graczy", 400
    word = random.choice(WORDS)
    imp = random.choice(game["players"])["id"]
    game.update({"started": True, "word": word, "impostor": imp})
    return redirect(url_for("room", code=code))

# --- START SERWERA ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
