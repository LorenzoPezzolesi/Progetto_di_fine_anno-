from flask import Flask, render_template, request
import random

def get_last_played_card():
    if len(played_cards) == 0:
        return "Nessuna"
    else:
        return played_cards[-1]

def create_deck():
    deck = []
    for color in ["red", "green", "yellow", "blue"]:
        for value in range(10):
            card = {
                "color": color,
                "value": str(value)
            }
            deck.append(card)
        for effect in ["CambioGiro", "Blocco", "+2"]:
            card = {
                "color": color,
                "value": effect
            }
            deck.append(card)
    for effect in ["CambioColore", "+4"]:
        card = {
            "color": "white",
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

opponent_cards = []
for i in range(7):
    opponent_cards.append(deck.pop())

player_cards = []
for i in range(7):
    player_cards.append(deck.pop())

played_cards = [deck.pop()]
last_player_name = "none"

@app.route("/", methods=["GET", "POST"])
def index():
    # Indico che last_player_name è una variabile globale
    global last_player_name
    # Se il giocatore può eseguire il suo turno (non è bloccato, etc.)
    if can_execute_turn("player"):
        # Esegui il turno del giocatore
        execute_player_turn()
        # Indica che l'ultimo giocatore è il giocatore
        last_player_name = "player"
    if can_execute_turn("opponent"):
        execute_opponent_turn()
        last_player_name = "opponent"
    # Creo la pagina da mostrare all'utente con:
    # - Num carte avversario
    # - Ultima carta giocata
    # - Carte della mano del giocatore
    return render_template("index.html", enemy_cards_count=len(opponent_cards), last_played_card=get_card_description(get_last_played_card()), player_cards=get_hand_descriptions(player_cards))

def get_card_description(card: dict[str, str]) -> str:
    return str(card["value"]) + " " + card["color"]

def get_hand_descriptions(hand: list[dict[str, str]]) -> list[str]:
    descriptions = []
    for card in hand:
        descriptions.append(get_card_description(card))
    return descriptions

def execute_player_turn():
    global turn
    if request.method == "GET":
        url_parts = request.url.split("=")
        has_action = len(url_parts) > 1
        if has_action:
            action_type = url_parts[1].lower()
            if action_type == "draw":
                player_cards.append(deck.pop())
    elif request.method == "POST":
        played_card_parts = request.form.get("played_card").split(" ")
        played_card = {
            "color": played_card_parts[1],
            "value": played_card_parts[0],
        }
        if can_card_be_played(played_card):
            played_cards.append(played_card)
            player_cards.remove(played_card)

def execute_opponent_turn():
    global turn
    for card in opponent_cards:
        if can_card_be_played(card):
            played_cards.append(card)
            opponent_cards.remove(card)
            return
    opponent_cards.append(deck.pop())

def can_card_be_played(card: dict[str, str]) -> bool:
    top_played_card = get_last_played_card()
    return card["color"] == top_played_card["color"] or card["value"] == top_played_card["value"] or card["color"] == "white"

def can_execute_turn(player_name: str) -> bool:
    if player_name == last_player_name or last_player_name == "none":
        return True
    top_played_card = get_last_played_card()
    return top_played_card["value"] != "Blocco" and top_played_card["value"] != "CambioGiro" and top_played_card["value"] != "+2" and top_played_card["value"] != "+4"

if __name__ == "__main__":
    app.run(debug=True, port=3000)