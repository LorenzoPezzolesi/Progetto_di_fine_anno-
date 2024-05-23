from flask import Flask, render_template, request
import random

#Crea un mazzo
def create_deck():
    deck = []
    for color in ["red", "green", "yellow", "blue"]:
        for value in range(10):
            card = {
                "color": color,
                "value": str(value)
            }
            deck.append(card)
        for effect in ["reverse", "skip", "picker"]:
            card = {
                "color": color,
                "value": effect
            }
            deck.append(card)
    for effect in ["pick_four"]:
        card = {
            "color": "wild",
            "value": effect
        }
        deck.append(card)
    return deck

#Mischia il mazzo
def shuffle_deck(deck: list[dict]):
    for i in range(random.randint(5,10)):
        random.shuffle(deck)
    return deck

#Non capito bene
def get_last_played_card():
    if len(played_cards) == 0:
        return "Nessuna"
    else:
        return played_cards[-1]

deck = shuffle_deck(create_deck()) #-->non capito bene

#Carte dell'avversario
opponent_cards = []
for i in range(7):
    opponent_cards.append(deck.pop())

#Carte del giocatore
player_cards = []
for i in range(7):
    player_cards.append(deck.pop())

played_cards = [deck.pop()]
last_player_name = "none"

turn_count = 0
last_played_card_turn = 0
turn_player_said_uno = 0

#inizio Flask
app = Flask(__name__, static_url_path='')

@app.route("/", methods=["GET", "POST"])
def index():
    # Indico che last_player_name è una variabile globale
    global last_player_name
    global turn_count
    global turn_player_said_uno
    was_valid_action = True
    winner = ""
    if len(player_cards) == 0:
        winner = "player"
    elif len(opponent_cards) == 0:
        winner = "opponent"
    # Se il giocatore può eseguire il suo turno (non è bloccato, etc.)
    if winner == "" and can_execute_turn("player"):
        # Esegui il turno del giocatore
        was_valid_action = execute_player_turn()
        # Indica che l'ultimo giocatore è il giocatore
        if was_valid_action:
            last_player_name = "player"

    if winner == "" and was_valid_action and turn_player_said_uno != turn_count and can_execute_turn("opponent"):
        execute_opponent_turn()
        last_player_name = "opponent"
    # Creo la pagina da mostrare all'utente con:
    # - Numero carte dell' avversario
    # - L'ultima carta giocata
    # - Carte della mano del giocatore
    if winner == "" and was_valid_action:
        turn_count += 1
    can_play_any_card = False
    for card in player_cards:
        if winner == "" and can_card_be_played(card):
            can_play_any_card = True
            break
    return render_template(
        "index.html", 
        enemy_cards_count=len(opponent_cards), 
        last_played_card=get_last_played_card(), 
        player_cards=player_cards,
        player_cards_count=len(player_cards),
        can_draw=True, 
        can_play=can_play_any_card and can_execute_turn("player"), 
        can_pass=True,
        winner=winner
    )
#Fine di Flask

def execute_card_effect(target_hand: list[dict[str, str]]):
    played_card = get_last_played_card()
    if played_card["value"] == "picker":
        target_hand.append(deck.pop())
        target_hand.append(deck.pop())
    elif played_card["value"] == "pick_four":
        target_hand.append(deck.pop())
        target_hand.append(deck.pop())
        target_hand.append(deck.pop())
        target_hand.append(deck.pop())

def execute_player_turn():
    global last_played_card_turn
    global turn_player_said_uno
    if request.method == "GET":
        url_parts = request.url.split("=")
        has_action = len(url_parts) > 1
        if has_action:
            action_type = url_parts[1].lower()
            if action_type == "draw":
                player_cards.append(deck.pop())
                return True
            elif action_type == "pass":
                return True
            elif action_type == "uno":
                turn_player_said_uno = turn_count
                return True
    elif request.method == "POST":
        if len(player_cards) == 1 and turn_player_said_uno == turn_count - 1:
            player_cards.append(deck.pop())
            player_cards.append(deck.pop())
            return True
        played_card_parts = request.form.get("played_card").split(" ")
        played_card = {
            "color": played_card_parts[1],
            "value": played_card_parts[0],
        }
        if played_card in player_cards and can_card_be_played(played_card):
            played_cards.append(played_card)
            player_cards.remove(played_card)
            last_played_card_turn = turn_count
            execute_card_effect(opponent_cards)
            return True
    return False

def execute_opponent_turn():
    global last_played_card_turn
    for card in opponent_cards:
        if can_card_be_played(card):
            played_cards.append(card)
            opponent_cards.remove(card)
            last_played_card_turn = turn_count
            execute_card_effect(player_cards)
            return
    opponent_cards.append(deck.pop())

def can_card_be_played(card: dict[str, str]) -> bool:
    top_played_card = get_last_played_card()
    return card["color"] == top_played_card["color"] or card["value"] == top_played_card["value"] or card["color"] == "wild" or top_played_card["color"] == "wild"

def can_execute_turn(player_name: str) -> bool:
    if player_name == last_player_name or last_player_name == "none" or last_played_card_turn < turn_count - 1:
        return True
    top_played_card = get_last_played_card()
    return top_played_card["value"] != "skip" and top_played_card["value"] != "reverse" and top_played_card["value"] != "picker" and top_played_card["value"] != "pick_four"

if __name__ == "__main__":
    app.run(debug=True, port=3000)