from flask import Flask, render_template
import random

def get_last_played_card():
    if len(played_cards) == 0:
        return "Nessuna"
    else:
        return played_cards[-1]

def create_deck():
    deck = []
    for color in ["Rosso", "Verde", "Giallo", "Blu"]:
        for value in range(10):
            card = {
                "color": color,
                "value": value
            }
            deck.append(card)
        for effect in ["Cambio giro", "Blocco", "+2"]:
            card = {
                "color": color,
                "value": effect
            }
            deck.append(card)
    for effect in ["Cambio colore", "+4"]:
        card = {
            "color": "Nessuno",
            "value": effect
        }
        deck.append(card)
    return deck

def shuffle_deck(deck: list[dict]):
    for i in range(random.randint(5,10)):
        random.shuffle(deck)
    return deck

app = Flask(__name__)

deck = shuffle_deck(create_deck())

enemy_cards = []
for i in range(7):
    enemy_cards.append(deck.pop())

player_cards = []
for i in range(7):
    player_cards.append(deck.pop())

played_cards = []

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", enemy_cards_count=len(enemy_cards), last_played_card=get_last_played_card(), player_cards=player_cards)

if __name__ == "__main__":
    app.run(debug=True, port=3000)