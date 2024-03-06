from flask import Flask, request, jsonify
from secrets import token_hex
import json
import random

def isSet(cards):
    if (cards[0]["color"]==cards[1]["color"] and cards[1]["color"]==cards[2]["color"] or cards[0]["color"]!=cards[1]["color"] and cards[0]["color"]!=cards[2]["color"] and cards[1]["color"]!=cards[2]["color"]):
        if (cards[0]["shape"]==cards[1]["shape"] and cards[1]["shape"]==cards[2]["shape"] or cards[0]["shape"]!=cards[1]["shape"] and cards[0]["shape"]!=cards[2]["shape"] and cards[1]["shape"]!=cards[2]["shape"]):
            if (cards[0]["fill"]==cards[1]["fill"] and cards[1]["fill"]==cards[2]["fill"] or cards[0]["fill"]!=cards[1]["fill"] and cards[0]["fill"]!=cards[2]["fill"] and cards[1]["fill"]!=cards[2]["fill"]):
                if (cards[0]["count"]==cards[1]["count"] and cards[1]["count"]==cards[2]["count"] or cards[0]["count"]!=cards[1]["count"] and cards[0]["count"]!=cards[2]["count"] and cards[1]["count"]!=cards[2]["count"]):
                    return True
            else:
                return False
            
        else:
            return False
    else:
        return False

def find_a_set(field):
    cards=[] #массив со всеми картами
    for card in field["cards"]:
        cards.append(card)
    for first_card_index in range(len(cards)):
        for second_card_index in range(first_card_index+1,len(cards)):
            third_possible_card={
                "color": cards[second_card_index]["color"] if cards[first_card_index]["color"]==cards[second_card_index]["color"] else (6-cards[first_card_index]["color"]-cards[second_card_index]["color"]),
                "shape": cards[second_card_index]["shape"] if cards[first_card_index]["shape"]==cards[second_card_index]["shape"] else (6-cards[first_card_index]["shape"]-cards[second_card_index]["shape"]),
                "fill": cards[second_card_index]["fill"] if cards[first_card_index]["fill"]==cards[second_card_index]["fill"] else (6-cards[first_card_index]["fill"]-cards[second_card_index]["fill"]),
                "count": cards[second_card_index]["count"] if cards[first_card_index]["count"]==cards[second_card_index]["count"] else (6-cards[first_card_index]["count"]-cards[second_card_index]["count"])
            }
            
            for searching_third_card_index in range(len(cards)):
                if (cards[searching_third_card_index]["id"]==cards[first_card_index]["id"] or cards[searching_third_card_index]["id"]==cards[second_card_index]["id"]):
                    continue
                if (cards[searching_third_card_index]["color"]==third_possible_card["color"] and cards[searching_third_card_index]["shape"]==third_possible_card["shape"]
                    and cards[searching_third_card_index]["fill"]==third_possible_card["fill"] and cards[searching_third_card_index]["count"]==third_possible_card["count"]):
                    return [cards[first_card_index]["id"],cards[second_card_index]["id"],cards[searching_third_card_index]["id"]]
                
    return False   


app=Flask(__name__)
games={#список созданных игр
    "games": [
        #id,
        #accessToken,
        #field,
        #remained_cards
    ]
}

cards=[]
card_id=1
for color in range(1,4):
    for shape in range(1,4):
        for fill in range(1,4):
            for count in range(1,4):
                cards.append({"id":card_id,
                              "color":color,
                              "shape":shape,
                              "fill":fill,
                              "count":count})
                card_id+=1

@app.route('/user/register', methods=['POST'])
def register():
    user_registration_data=request.get_json()

    if not(user_registration_data["nickname"]) or not(user_registration_data["password"]):
        return jsonify({"succes":False,"exception":{"message":"Nickname or password are incorrect"}})
    
    users=json.load(open("jsons/users.json"))
    
    for nickname in users["users"]:
        if nickname["nickname"]==user_registration_data["nickname"]:
            return jsonify({"succes":False,"exception":{"message":"Nickname already exists"}})
    #добавляем пользователя в файл
    accessToken=token_hex(16)
    while any(accessToken==i["accessToken"] for i in users["users"]):
        accessToken=token_hex(16)
    
    users["users"].append({"nickname":user_registration_data["nickname"],"password":user_registration_data["password"],"accessToken":accessToken})
    json.dump(users,open("jsons/users.json","w"))
    return jsonify({
        "success":True,
        "exception":None,
        "nickname":user_registration_data["nickname"],
        "accessToken":accessToken
        })

@app.route('/user/login', methods=['POST'])
def login():
    user_login_data=request.get_json()
    
    users=json.load(open("jsons/users.json"))

    if not(user_login_data["nickname"]) or not(user_login_data["password"]):
        return jsonify({"succes":False,"exception":{"message":"Nickname or password are incorrect"}})
    
    if not(any(user_login_data["nickname"]==user["nickname"] for user in users["users"])):
        return jsonify({"succes":False,"exception":{"message":"Nickname does not exist"}})
    
    for user in users["users"]:
        if user["nickname"]==user_login_data["nickname"] and user["password"]==user_login_data["password"]:
            return jsonify({"succes":True,"exception":None,"nickname":user["nickname"],"accessToken":user["accessToken"]})
    return jsonify({"succes":False,"exception":{"message":"Password is incorrect"}})
    
@app.route('/set/room/create', methods=['POST'])
def create():
    create_data=request.get_json()
    ident=1

    users=json.load(open("jsons/users.json"))

    if not(create_data["accessToken"]) or not(any(create_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken is incorrect"}})

    if any(game["accessToken"]==create_data["accessToken"] for game in games["games"]):
        return jsonify({"success":False,"exception":{"message":"User is already in game"}})

    field={ "cards":[],"status":"ongoing","score":0 }
    remained_cards={ "cards":cards }

    for i in range(12):
        random_card=random.choice(remained_cards["cards"])
        field["cards"].append(random_card)
        remained_cards["cards"].remove(random_card)

    

    if not(games["games"]):
        games["games"].append({ "id":ident, "accessToken":create_data["accessToken"],"field":field, "remained_cards":remained_cards })
    else:
        max_ident=1
        for game_id in games["games"]:
            if game_id["id"]>max_ident:
                max_ident=game_id["id"]
        ident=max_ident+1
        games["games"].append({ "id":ident, "accessToken":create_data["accessToken"], "field":field, "remained_cards":remained_cards })
        
    
    return jsonify({"success":True,"exception":None,"gameId":ident})

@app.route('/set/room/list', methods=['POST'])
def list_of_games():
    list_of_games_data=request.get_json()

    users=json.load(open("jsons/users.json"))

    if not(list_of_games_data["accessToken"]) or not(any(list_of_games_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken is incorrect"}})

    return jsonify(games)

@app.route('/set/room/exitGame', methods=['POST'])
def exit_the_game():
    exit_the_game_data=request.get_json()
    
    users=json.load(open("jsons/users.json"))
    
    if not(exit_the_game_data["accessToken"]) or not(exit_the_game_data["gameId"]) or not(any(exit_the_game_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken or gameId are incorrect"}})
    if not(any(game["id"]==exit_the_game_data["gameId"] for game in games["games"])):
        return jsonify({"success":False,"exception":{"message":"game does not exist"}})

    for game in games["games"]:
        if game["id"]==exit_the_game_data["gameId"]:
            game["accessToken"]=""
            return jsonify({"success":True,"exception":None,"accessToken":exit_the_game_data["accessToken"]})
    
    

@app.route('/set/room/enter', methods=['POST'])
def enter_the_game():
    enter_the_game_data=request.get_json()

    users=json.load(open("jsons/users.json"))

    if not(enter_the_game_data["accessToken"]) or not(enter_the_game_data["gameId"]) or not(any(enter_the_game_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken or gameId are incorrect"}})

    for game in games["games"]:
        if game["accessToken"]==enter_the_game_data["accessToken"]:
            return jsonify({"success":False,"exception":{"message":"User is already in game"}})
    if not(any(game["id"]==enter_the_game_data["gameId"] for game in games["games"])):
        return jsonify({"success":False,"exception":{"message":"game does not exist"}})

    for game in games["games"]:
        if game["id"]==enter_the_game_data["gameId"]:
            if game["accessToken"]:
                return jsonify({"success":False,"exception":{"message":"Game is already being played"}})
            else:
                game["accessToken"]=enter_the_game_data["accessToken"]
    
    return jsonify({"success":True,"exception":None,"gameId":enter_the_game_data["gameId"]})

@app.route('/set/field',methods=['POST'])
def field():
    field_data=request.get_json()

    users=json.load(open("jsons/users.json"))

    if not(field_data["accessToken"]) or not(any(field_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken is incorrect"}})
    if not(any(field_data["accessToken"]==game["accessToken"] for game in games["games"])):
        return jsonify({"success":False,"exception":{"message":"User is not in game"}})
    game=0
    for i in games["games"]:
        if field_data["accessToken"] == i["accessToken"]:
            game=i

    return jsonify({"success":True,"exception":None,"field":game["field"]})

@app.route('/set/pick',methods=['POST'])
def pick():
    pick_data=request.get_json()

    if(len(pick_data["cards"])!=3):
        return jsonify({"success":False,"exception":{"message":"User chose more or less then 3 cards"}})
    
    users=json.load(open("jsons/users.json"))

    if not(pick_data["accessToken"]) or not(any(pick_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken is incorrect"}})

    if not(any(pick_data["accessToken"]==i["accessToken"] for i in games["games"])):
        return jsonify({"success":False,"exception":{"message":"There is no game for this player"}})

    game=0
    for i in games["games"]:
        if pick_data["accessToken"]==i["accessToken"]:
            game=i
    for card_id in pick_data["cards"]:
        if not(any(card_id==game["field"]["cards"][i]["id"] for i in range(len(game["field"]["cards"])))):
            return jsonify({"success":False,"exception":{"message":"Cards IDs are incorrect"}})
    if pick_data["cards"][0]==pick_data["cards"][1] or pick_data["cards"][0]==pick_data["cards"][2] or pick_data["cards"][1]==pick_data["cards"][2]:
        return jsonify({"success":False,"exception":{"message":"The are identical cards in the request"}})
    
    chosen_cards=[]
    for card in game["field"]["cards"]:
        if any(card["id"]==card_id for card_id in pick_data["cards"]):
            chosen_cards.append(card)

    if isSet(chosen_cards):
        for i in range(len(games["games"])):
            if games["games"][i]["accessToken"]==pick_data["accessToken"]:
                games["games"][i]["field"]["score"]+=3
                for card in chosen_cards:
                        games["games"][i]["field"]["cards"].remove(card)
                if len(games["games"][i]["field"]["cards"])<12:
                        for _ in range(12-len(games["games"][i]["field"]["cards"])):
                            random_card=random.choice(games["games"][i]["remained_cards"]["cards"])
                            games["games"][i]["field"]["cards"].append(random_card)
                            games["games"][i]["remained_cards"]["cards"].remove(random_card)
                return jsonify({"success":True,"exception":None,"isSet":True,"score":games["games"][i]["field"]["score"]})
    else:
        for i in range(len(games["games"])):
            if games["games"][i]["accessToken"]==pick_data["accessToken"]:
                return jsonify({"success":True,"exception":None,"isSet":False,"score":games["games"][i]["field"]["score"]})
    
@app.route('/set/add',methods=["POST"])
def add():
    add_data=request.get_json()

    users=json.load(open("jsons/users.json"))

    if not(add_data["accessToken"]) or not(any(add_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken is incorrect"}})

    if not(any(add_data["accessToken"]==i["accessToken"] for i in games["games"])):
        return jsonify({"success":False,"exception":{"message":"There is no game for this player"}})

    
    for game in range(len(games["games"])):
        if games["games"][game]["accessToken"]==add_data["accessToken"]:
            for i in range(3):
                random_card=random.choice(games["games"][game]["remained_cards"]["cards"])
                games["games"][game]["field"]["cards"].append(random_card)
                games["games"][game]["remained_cards"]["cards"].remove(random_card)
            break
    
    return jsonify({"success":True,"exception":None})

@app.route('/set/scores',methods=["POST"])
def scores():
    scores_data=request.get_json()

    users=json.load(open("jsons/users.json"))

    if not(scores_data["accessToken"]) or not(any(scores_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken is incorrect"}})

    users_scores=[]
    user={"user":"","score":""}

    for game in games["games"]:
        if game["accessToken"]:
            user["score"]=game["field"]["score"]
            for i in users["users"]:
                if i["accessToken"]==game["accessToken"]:
                    user["user"]=i["nickname"]
            users_scores.append(user)
            

    return jsonify({"success":True,"exception":None,"users":users_scores})

@app.route('/set/find_a_set',methods=["POST"])
def find_set():
    find_a_set_data=request.get_json()

    users=json.load(open("jsons/users.json"))

    if not(find_a_set_data["accessToken"]) or not(any(find_a_set_data["accessToken"]==user["accessToken"] for user in users["users"])):
        return jsonify({"success":False,"exception":{"message":"accessToken is incorrect"}})
    
    if not(any(find_a_set_data["accessToken"]==i["accessToken"] for i in games["games"])):
        return jsonify({"success":False,"exception":{"message":"There is no game for this player"}})

    field=0
    for game in games["games"]:
        if find_a_set_data["accessToken"]==game["accessToken"]:
            field=game["field"]
            break
    
    a_set=find_a_set(field)

    if a_set:
        return jsonify({"success":True,"exception":None,"set":a_set})
    else:
        return jsonify({"success":True,"exception":None,"set":None})
    

if __name__=='__main__':
    app.run(debug=True)
