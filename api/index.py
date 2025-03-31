import requests
import random
from flask import Flask, jsonify, request

app = Flask(__name__)
title = "7AF94"
secretkey = "GBIPB74594RF9UDYHIAKASEJ1WG66KWWF4FAPKJK1WYZCC94S7"  
ApiKey = "OC|9837791239572874|4523778edb61de7362b2843a78428242"
coems = {}

def authjh():
    return {"content-type": "application/json", "X-SecretKey": secretkey}

@app.route("/", methods=["POST", "GET"])
def no():
    return "yesnt"

@app.route("/api/PlayFabAuthentication", methods=["GET", "POST"])
def authenticate():
    user_agent = request.headers.get('User-Agent', '')
    
    if 'UnityPlayer' not in user_agent:
        return jsonify({"BanMessage": "Your access has been revoked.", "BanExpirationTime": "Indefinite"}), 403

    data = request.get_json()
    oculus_id = data.get('OculusId')
    nonce_value = data.get("Nonce")

    validation_request = requests.post(
        "https://graph.oculus.com/user_nonce_validate",
        json={
            "access_token": "OC|9837791239572874|4523778edb61de7362b2843a78428242",
            "nonce": nonce_value,
            "user_id": oculus_id
        }
    )

    if validation_request.status_code != 200 or not validation_request.json().get("is_valid"):
        return jsonify({"BanMessage": "Your access has been revoked.", "BanExpirationTime": "Indefinite"}), 403

    auth_response = requests.post(
        url=f"https://{GameConfig.title_id}.playfabapi.com/Server/LoginWithServerCustomId",
        json={
            "ServerCustomId": "OCULUS" + oculus_id,
            "CreateAccount": True
        },
        headers=GameConfig.auth_headers()
    )

    if auth_response.status_code == 200:
        response_data = auth_response.json().get('data', {})
        return jsonify({
            "SessionTicket": response_data.get('SessionTicket'),
            "EntityToken": response_data.get('EntityToken', {}).get('EntityToken'),
            "PlayFabId": response_data.get('PlayFabId'),
            "EntityId": response_data.get('EntityToken', {}).get('Entity', {}).get('Id'),
            "EntityType": response_data.get('EntityToken', {}).get('Entity', {}).get('Type')
        }), 200
    
    ban_details = auth_response.json()
    return handle_ban_error(ban_details)

def handle_ban_error(ban_info):
    if ban_info.get("errorCode") == 1002:
        ban_description = ban_info.get("errorDetails", {})
        ban_key = next(iter(ban_description.keys()), None)
        ban_duration = ban_description.get(ban_key, [])
        expiration_time = ban_duration[0] if ban_duration else "Indefinite"
        return jsonify({"BanMessage": ban_key, "BanExpirationTime": expiration_time}), 403

@app.route("/api/titledata", methods=["POST", "GET"])
def get_title_data():
    title_data_response = requests.post(
        url=f"https://{GameConfig.title_id}.playfabapi.com/Server/GetTitleData",
        headers=GameConfig.auth_headers()
    )
    
    if title_data_response.status_code == 200:
        return jsonify(title_data_response.json().get("data", {}).get("Data", {}))
    return jsonify({}), title_data_response.status_code

@app.route("/api/CachePlayFabId", methods=["POST"])
def cpi():
    getjson = request.get_json()
    coems[getjson.get("PlayFabId")] = getjson
    return jsonify({"Message": "worked1!!"}), 200

@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consume_iap():
    request_body = request.get_json()
    user_token = request_body.get("userToken")
    user_id = request_body.get("userID")
    nonce = request_body.get("nonce")
    sku_item = request_body.get("sku")

    consumption_response = requests.post(
        url=f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku_item}&access_token={GameConfig.api_key}",
        headers={"Content-Type": "application/json"}
    )

    return jsonify({"result": consumption_response.json().get("success")}), 200 if consumption_response.json().get("success") else 400

@app.route("/cbfn", methods=["POST","GET"])
def cfbn():
    name = request.args.get('name')
    BadNames = [
        "KKK", "PENIS", "NIGG", "NEG", "NIGA", "MONKEYSLAVE", "SLAVE", "FAG", 
        "NAGGI", "TRANNY", "QUEER", "KYS", "DICK", "PUSSY", "VAGINA", "BIGBLACKCOCK", 
        "DILDO", "HITLER", "KKX", "XKK", "NIGA", "NIGE", "NIG", "NI6", "PORN", 
        "JEW", "JAXX", "TTTPIG", "SEX", "COCK", "CUM", "FUCK", "PENIS", "DICK", 
        "ELLIOT", "JMAN", "K9", "NIGGA", "TTTPIG", "NICKER", "NICKA", 
        "REEL", "NII", "@here", "!", " ", "JMAN", "PPPTIG", "CLEANINGBOT", "JANITOR", "K9", 
        "H4PKY", "MOSA", "NIGGER", "NIGGA", "IHATENIGGERS", "@everyone", "TTT"
    ]
    result = 0 if name not in BadNames else 2
    return jsonify({"Message": "the name thingy worked!", "Name": name, "Result": result})

@app.route("/gaa", methods=["POST", "GET"])
def gaa():
    getjson = request.get_json()["FunctionResult"]
    return jsonify(getjson)

@app.route("/saa", methods=["POST", "GET"])
def saa():
    getjson = request.get_json()["FunctionResult"]
    return jsonify(getjson)

@app.route("/grn", methods=["POST", "GET"])
def grn():
    return jsonify({"result": f"pluh!{random.randint(1000, 9999)}"})

@app.route("/api/photon", methods=["POST"])
def photonauth():
    getjson = request.get_json()
    Ticket = getjson.get("Ticket")
    Nonce = getjson.get("Nonce")
    TitleId = getjson.get("AppId")
    Platform = getjson.get("Platform")
    UserId = getjson.get("UserId")
    AppVersion = getjson.get("AppVersion")
    Token = getjson.get("Token")
    Username = getjson.get("username")
    if Nonce is None:
        return jsonify({'Error': 'Bad request', 'Message': 'Not Authenticated!'}), 304 
    if TitleId != '910A2':
        return jsonify({'Error': 'Bad request', 'Message': 'Invalid titleid!'}), 403
    if Platform != 'Quest':
        return jsonify({'Error': 'Bad request', 'Message': 'Invalid platform!'}), 403
    return jsonify({"ResultCode": 1, "StatusCode": 200, "Message": "authed with photon",
                    "Result": 0,
                    "UserId": UserId,
                    "AppId": TitleId,
                    "AppVersion": AppVersion,
                    "Ticket": Ticket,
                    "Token": Token,
                    "Nonce": Nonce,
                    "Platform": Platform,
                    "Username": Username}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
