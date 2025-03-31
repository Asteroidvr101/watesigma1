from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

class GameConfig:
    title_id = "7AF94"
    secret_key = "GBIPB74594RF9UDYHIAKASEJ1WG66KWWF4FAPKJK1WYZCC94S7"
    api_key = "OC|9807548162641339|f4cedc6635c40602c7fd43608a7c92cc"
    coems = {}

    @staticmethod
    def auth_headers():
        return {
            "Content-Type": "application/json",
            "X-SecretKey": GameConfig.secret_key
        }

polling_data = [
    {
        "id": 1,
        "query": "IS THIS REAL?",
        "options": ["YES", "NO"],
        "votes": [],
        "predictions": [],
        "start": "2025-03-27T18:00:00",
        "end": "2025-03-30T18:00:00",
        "active": True
    }
]

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
            "access_token": "OC|9807548162641339|f4cedc6635c40602c7fd43608a7c92cc",
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

@app.route("/api/FetchPoll", methods=["GET", "POST"])
def fetch_polls():
    return jsonify(polling_data), 200

@app.route("/api/Vote", methods=["POST"])
def register_vote():
    vote_information = request.json
    poll_id = int(vote_information.get("PollId", -1))
    playfab_identifier = vote_information.get("PlayFabId")
    option_index = vote_information.get("OptionIndex")
    is_prediction = vote_information.get("IsPrediction")
    
    poll_instance = next((poll for poll in polling_data if poll["id"] == poll_id), None)

    if not poll_instance or not poll_instance["active"] or option_index < 0 or option_index >= len(poll_instance["options"]):
        return "", 404

    embed_content = {
        "embeds": [{
            "title": "Vote Received ✔️",
            "description": f"**PlayFab ID**: {playfab_identifier}\n**Prediction**: {is_prediction}\n**Question**: {poll_instance['query']}\n**Voted For**: {poll_instance['options'][option_index]}",
            "color": 3447003
        }]
    }
    
    requests.post(
        "https://discord.com/api/webhooks/1353133682382213273/XS7JQstllHIZuKuOKhc3oBom2QAdQJN7ad0S9MZYlfttvVnShClTlofpz2vugsJzDPkh",
        json=embed_content
    )
    
    return jsonify({"success": True}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8098)
