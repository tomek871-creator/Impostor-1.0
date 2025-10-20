from flask import Flask, render_template_string, request, redirect, url_for
import random
import string

app = Flask(__name__)

# --- LISTA SŁÓW ---
WORDS = [
    "pies", "kot", "samochód", "książka", "telefon", "komputer", "drzewo", "krzesło", "kwiat", "morze",
    "szkoła", "film", "pociąg", "samolot", "księżyc", "słońce", "muzyka", "las", "dom", "buty",
    "pociąg", "szpital", "muzeum", "ogród", "taniec", "mleko", "ryba", "rower", "talerz", "lampa",
    "kosmos", "podróż", "ciasto", "kuchnia", "miasto", "wieża", "teatr", "kościół", "rzeka", "burza",
    "minister", "nauczyciel", "architekt", "dokument", "system", "ekonomia", "konflikt", "prawo", "wolność", "kultura",
    "strategia", "dyskusja", "społeczeństwo", "nauka", "technologia", "projekt", "artysta", "poeta", "muzyk", "aktor"
]

# --- DANE O GRACH ---
games = {}

# --- STRONA GŁÓWNA ---
@app.route("/")
def index():
    return render_template_string("""
    <h1>Gra: Impostor</h1>
    <form action="/create" method="post">
        <button type="submit">Utwórz pokój</button>
    </form>
    <br>
    <form action="/room" method="post">
        <input type="text" name="room" placeholder="Kod pokoju" required>
        <button type="submit">Dołącz</button>
    </form>
    """)

# --- UTWORZENIE POKOJU ---
@app.route("/create", methods=["POST"])
def create():
    code = ''.join(random.choices(string.ascii_uppercase, k=4))
    games[code] = {"players": [], "started": False, "word": None, "impostor": None}
    return redirect(f"/room/{code}?host=1")

# --- BEZPIECZNE DOŁĄCZENIE (naprawia 'Not Found') ---
@app.route("/room", methods=["GET", "POST"])
@app.route("/room/", methods=["GET", "POST"])
def room_redirect():
    code = ""
    if request.method == "POST":
        code = (request.form.get("room") or "").strip().upper()
    if not code:
        code = (request.args.get("room") or "").strip().upper()
    if not code:
        return redirect("/")
    return redirect(f"/room/{code}")

# --- STRONA POKOJU ---
@app.route("/room/<code>")
def room(code):
    host = request.args.get("host") == "1"

    if code not in games:
        return "Pokój nie istnieje."

    game = games[code]

    # Rejestracja gracza
    player_id = request.remote_addr  # unikalne ID = adres IP
    if player_id not in game["players"]:
        game["players"].append(player_id)

    # Jeśli gra już się zaczęła
    if game["started"]:
        impostor = game["impostor"]
        if player_id == impostor:
            word = game["word_impostor"]
        else:
            word = game["word"]
        return render_template_string(f"""
            <h2>Gra rozpoczęta!</h2>
            <p>Twoje słowo: <b>{word}</b></p>
        """)

    # Jeśli jeszcze nie zaczęła
    player_count = len(game["players"])
    players_text = "<br>".join([f"Gracz {i+1}" for i in range(player_count)])
    start_button = ""
    if host:
        start_button = f"""
            <form action="/start/{code}" method="post">
                <button type="submit">Rozpocznij grę</button>
            </form>
        """

    return render_template_string(f"""
        <h2>Pokój: {code}</h2>
        <p>Liczba graczy: {player_count}</p>
        {players_text}
        <br>
        {start_button}
        <br>
        <form method="get" action="/room/{code}">
            <button type="submit">Odśwież</button>
        </form>
    """)

# --- ROZPOCZĘCIE GRY ---
@app.route("/start/<code>", methods=["POST"])
def start(code):
    if code not in games:
        return "Błąd: pokój nie istnieje."

    game = games[code]
    if len(game["players"]) < 3:
        return "Potrzeba co najmniej 3 graczy!"

    # Losowanie słów i impostora
    impostor = random.choice(game["players"])
    normal_word = random.choice(WORDS)
    impostor_word = random.choice([w for w in WORDS if w != normal_word])

    game["started"] = True
    game["word"] = normal_word
    game["word_impostor"] = impostor_word
    game["impostor"] = impostor

    return redirect(f"/room/{code}")

# --- URUCHOMIENIE ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
