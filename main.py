
import json, os, random
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import OneLineListItem

CUSTOM_WORDS_FILE = "custom_words.json"
MAX_ADD = 50

with open("words.json", encoding="utf-8") as f:
    DEFAULT_WORDS = json.load(f)

if os.path.exists(CUSTOM_WORDS_FILE):
    with open(CUSTOM_WORDS_FILE, encoding="utf-8") as f:
        CUSTOM_WORDS = json.load(f)
else:
    CUSTOM_WORDS = []

def get_all_words():
    return DEFAULT_WORDS + CUSTOM_WORDS

KV = """
MDScreen:
    ScreenManager:
        id: sm
        MDScreen:
            name: "lobby"
            MDBoxLayout:
                orientation: "vertical"
                padding: dp(12)
                spacing: dp(10)
                MDLabel:
                    id: lobby_title
                    text: "Pokój: ---"
                    halign: "center"
                MDBoxLayout:
                    id: players_box
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(200)
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(12)
                    MDRectangleFlatButton:
                        text: "Start gry"
                        on_release: app.start_game()
                    MDRectangleFlatButton:
                        text: "Dodaj słowa"
                        on_release: app.add_words()
                    MDRectangleFlatButton:
                        text: "Opuść pokój"
                        on_release: app.leave_room()
"""

class ImpostorApp(MDApp):
    def build(self):
        self.root = Builder.load_string(KV)
        Clock.schedule_once(lambda dt: self.refresh_lobby(), 0)
        Clock.schedule_interval(lambda dt: self.refresh_lobby(), 1.5)
        return self.root

    def refresh_lobby(self):
        players_box = self.root.ids.players_box
        players_box.clear_widgets()
        for name in ["Host", "Gracz1", "Gracz2"]:
            item = OneLineListItem(text=name)
            players_box.add_widget(item)

    def start_game(self):
        word = random.choice(get_all_words())
        self.show_snackbar(f"Gra wystartowała! Słowo: {word}")

    def add_words(self):
        new_words = ["jabłko", "gruszka", "herbata"]  # Tu możesz dodać interfejs później
        if len(new_words) > MAX_ADD:
            self.show_snackbar(f"Maksymalnie {MAX_ADD} słów naraz.")
        else:
            CUSTOM_WORDS.extend(new_words)
            with open(CUSTOM_WORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(CUSTOM_WORDS, f, ensure_ascii=False, indent=2)
            self.show_snackbar(f"Dodano {len(new_words)} słów!")

    def leave_room(self):
        self.show_snackbar("Opuściłeś pokój.")

    from kivymd.toast import toast

def show_snackbar(self, text):
    toast(text)


if __name__ == "__main__":
    ImpostorApp().run()
