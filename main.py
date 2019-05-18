from flask import Flask, jsonify, request
import pickle

app = Flask(__name__)

#
# Loading users data
#
USERS = {}
try:
    with open('USERS.pkl', 'rb') as f:
        USERS = pickle.load(f)
except:
    pass

GAMES = {}


#
# Get user token by login
#
def get_user_token(login):
    for key, item in USERS.items():
        if item[0] == login:
            return key
    return None


#
# Signing users up
#
@app.route("/sign-up", methods=["POST"])
def sign_up():
    login = request.form.get("login")
    password = request.form.get("password")
    token = str(hash((login, password,)))
    if login in [i[0] for k, i in USERS.items()]:
        return jsonify({"result": -1,
                        "error": "Such login is not available"})
    USERS[token] = [login]
    with open("USERS.pkl", 'wb') as f:
        pickle.dump(USERS, f)
    return jsonify({"result": 0,
                    "token": token})


#
# Signing users in
#
@app.route("/sign-in", methods=["POST"])
def sign_in():
    login = request.form.get("login")
    password = request.form.get("password")
    token = str(hash((login, password,)))
    print(token)
    if token not in USERS.keys():
        return jsonify({"result": -1, "error": "Authentication error"})
    return jsonify({"result": 0, "token": token})



#
# Creating a game
#
@app.route("/create-game", methods=["POST"])
def create_game():
    print(USERS, GAMES)
    host_token = request.form.get("token")
    name = request.form.get("name")
    if name in GAMES:
        return jsonify({"result": -1,
                        "error": "Choose another game name"})
    print(host_token, host_token in USERS.keys())
    if host_token not in USERS.keys():
        return jsonify({"result": -1,
                        "error": "Authentication error"})

    GAMES[name] = [USERS[host_token]]
    return jsonify({"result": 0, "connected_users": GAMES[name]})


#
# Get games list
#
@app.route("/get-games-list", methods=["POST"])
def get_games_list():
    return jsonify({"result": 0, "games": GAMES})


#
# Connect to the game
#
@app.route("/connect", methods=["POST"])
def connect():
    token = request.form.get("token")
    game_name = request.form.get("game_name")
    if game_name not in GAMES:
        return jsonify({"result": -1,
                        "error": "No such game"})
    if len(GAMES[game_name]) == 3:
        return jsonify({"result": -1,
                        "error": "Max number of users are yet connected"})
    print(USERS, token)
    if token not in USERS.keys():
        return jsonify({"result": -1,
                        "error": "Authentication failed"})
    GAMES[game_name].append(USERS[token])
    return jsonify({"result": 0,
                    "connected_users": GAMES[game_name]})


#
# Kick from the game
#
@app.route("/kick", methods=["POST"])
def kick():
    token = request.form.get("token")
    game_name = request.form.get("game_name")
    kick_token = request.form.get("kick_token")
    if token not in USERS:
        return jsonify({"result": -1,
                        "error": "Authentication failed"})
    if game_name not in GAMES:
        return jsonify({"result": -1,
                        "error": "No such game"})
    if USERS[token] != GAMES[game_name][0]:
        return jsonify({"result": -1,
                        "error": "You have no permission"})
    if kick_token not in USERS:
        return jsonify({"result": -1,
                        "error": "Such user does not exits"})
    kick_login = USERS[kick_token][0]
    print("kick login %s" % kick_login)
    print("Game %s" % GAMES[game_name])
    if kick_login not in [i[0] for i in GAMES[game_name]]:
        return jsonify({"result": -1,
                        "error": "No such user to kick"})
    GAMES[game_name].remove(USERS[kick_token])
    return jsonify({"result": 0})


#
# Check game hub status
#
@app.route("/check-hub", methods=["POST"])
def check_hub():
    token = request.form.get("token")
    game_name = request.form.get("game_name")
    if game_name not in GAMES:
        return jsonify({"result": -1,
                        "error": "Game not found"})
    if token not in USERS:
        return jsonify({"result": -1,
                        "error": "Authentication failed"})
    return jsonify({"result": 0, "connected_users": GAMES[game_name]})


if __name__ == '__main__':
    app.run(port=8080, debug=True)
