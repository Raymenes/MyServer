
"""
Registration of users with 0 token
Each user gets 10 tokens
Store a sentence on our database for 1 token
Retrieve stored sentence for 1 token

"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

# db is the name of the database we use
# 27017 is the default port mongodb listens to
client = MongoClient("mongodb://db:27017")

# create(if non-existing)/use the database inside mongo
db = client.SentencesDatabase
# create collection inside the database
users = db["Users"]


class Register(Resource):
    def post(self):
        postedData = request.get_json()

        # Validate request
        if (len(postedData) != 2) or ("username" not in postedData) or ("password" not in postedData):

            return jsonify({
                "Message": "Need just username and password in the request",
                "Status Code": 300
            })

        # Get the data
        username = postedData["username"]
        password = postedData["password"]

        # Validate username is not already existing

        queryExistingUser = users.find({"username": username})
        print(queryExistingUser)
        print(type(queryExistingUser))

        if len(list(queryExistingUser)) != 0:
            return jsonify({
                "Message": "username already taken",
                "Status Code": 301
            })

        # Hash sensitive data
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store username and hashed password into database
        users.insert({
            "username": username,
            "password": hashed_pw,
            "sentences": None,
            "tokens": 5
        })

        return jsonify({
            "Message": "Successfully signed up user: " + username,
            "Status Code": 200
        })


class Store(Resource):
    def post(self):

        postedData = request.get_json()

        # Validate request
        if not validatePostedData(postedData, ["username", "password", "sentence"]):
            return jsonify({
                "Message": "Error: missing parameters in request",
                "Status Code": 300
            })

        username = str(postedData["username"])
        password = str(postedData["password"])
        sentence = str(postedData["sentence"])

        # Verify username and password
        if not verifyUser(username, password):
            return jsonify({
                "Message": "Error: wrong username password",
                "Status Code": 301
            })

        # Verify user has enough tokens
        user_token_num = countTokens(username)
        if user_token_num < 1:
            return jsonify({
                "Message": "Error: user " + username + " doesn't have enough tokens",
                "Status Code": 302
            })

        users.update(
            {
                "username": username
            },
            {
                "$set": {
                    "sentences": sentence,
                    "tokens": user_token_num-1
                }
            }
        )

        return jsonify({
            "Message": {
                "sentence stored": sentence,
                "tokens left": user_token_num-1
            },
            "Status Code": 200
        })


class Retrieve(Resource):
    def post(self):
        postedData = request.get_json()

        # Validate request
        if not validatePostedData(postedData, ["username", "password"]):
            return jsonify({
                "Message": "Error: missing parameters in request",
                "Status Code": 300
            })

        username = str(postedData["username"])
        password = str(postedData["password"])

        # Verify username and password
        if not verifyUser(username, password):
            return jsonify({
                "Message": "Error: wrong username password",
                "Status Code": 301
            })

        # Verify user has enough tokens
        user_token_num = countTokens(username)
        if user_token_num < 1:
            return jsonify({
                "Message": "Error: user " + username + " doesn't have enough tokens",
                "Status Code": 302
            })

        sentence = users.find({"username": username})[0]["sentences"]
        if sentence is None:
            return jsonify({
                "Message": "Error: user doesn't have stored sentence",
                "Status Code": 303
            })

        users.update(
            {
                "username": username
            },
            {
                "$set": {
                    "tokens": user_token_num - 1
                }
            }
        )

        return jsonify({
                "Message": {
                    "sentence retrieved": sentence,
                    "tokens left": user_token_num - 1
                },
                "Status Code": 200
            })


class Experiment(Resource):
    def get(self):
        input = request.args.get("input")
        input2 = request.args.get("input2")

        if input is None:
            return jsonify({
                "Expecting Query Parameters": {
                    "Required": {
                        "input": "String"
                    },
                    "Optional": {
                        "input2": "String"
                    }
                }
            })

        return jsonify({
                "input": input,
                "input2": input2
            })


def validatePostedData(posted_data, expected_params):
    for param in expected_params:
        if param not in posted_data:
            return False

    return True


def verifyUser(username, password):
    queryExistingUser = users.find({"username": username})
    # username not existing in database
    if len(list(queryExistingUser)) == 0:
        return False

    hashed_pw = users.find({"username": username})[0]["password"]
    if bcrypt.hashpw(password.encode("utf-8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def countTokens(username):
    queryExistingUser = users.find({"username": username})
    # username not existing in database
    if len(list(queryExistingUser)) == 0:
        return 0

    return users.find({"username": username})[0]["tokens"]


api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Retrieve, "/retrieve")
api.add_resource(Experiment, "/test")

if __name__ == "__main__":
    # this is to specify the run on the local host of the machine, not the docker system
    app.run(host="0.0.0.0")
    app.run(debug=True)
    #app.run()

"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

# db is the name of the database we use
# 27017 is the default port mongodb listens to
client = MongoClient("mongodb://db:27017")

# create(if non-existing)/use the database inside mongo
db = client.aNewDB
# create collection(UserNum) inside the database(aNewDB)
UserNum = db["UserNum"]
# insert one document inside this collection
UserNum.insert({
    "num_of_users":0
})


class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]["num_of_users"]
        new_num = prev_num + 1
        UserNum.update({}, {"$set": {"num_of_users": new_num}})
        return str("Hello user " + str(new_num))

# Resource class
class Add(Resource):
    def post(self):
        # Here indicates the Resource Add was requested using POST method
        postedData = request.get_json()

        status_code = checkPostedData(postedData, "add")

        if status_code != 200:
            retMap = {
                "Message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(retMap)

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)
        result = x+y
        retMap = {
            "Message": result,
            "Status Code": 200
        }
        return jsonify(retMap)


class Subtract(Resource):
    def post(self):
        postedData = request.get_json()

        status_code = checkPostedData(postedData, "subtract")

        if status_code != 200:
            retMap = {
                "Message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(retMap)

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)
        result = x-y
        retMap = {
            "Message": result,
            "Status Code": 200
        }
        return jsonify(retMap)


class Multiply(Resource):
    def post(self):
        postedData = request.get_json()

        status_code = checkPostedData(postedData, "multiply")

        if status_code != 200:
            retMap = {
                "Message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(retMap)

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)
        result = x*y
        retMap = {
            "Message": result,
            "Status Code": 200
        }
        return jsonify(retMap)


class Divide(Resource):
    def post(self):
        postedData = request.get_json()

        status_code = checkPostedData(postedData, "divide")

        if status_code != 200:
            retMap = {
                "Message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(retMap)

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)
        result = (x*1.0)/y
        retMap = {
            "Message": result,
            "Status Code": 200
        }
        return jsonify(retMap)

# Helper method


def checkPostedData(postedData, functionName):
    if functionName in ["add", "subtract", "multiply"]:
        if ("x" not in postedData) or ("y" not in postedData):
            return 301
        else:
            return 200
    elif functionName == "divide":
        if ("x" not in postedData) or ("y" not in postedData):
            return 301
        elif int(postedData["y"]) == 0:
            return 302
        else:
            return 200


api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")
api.add_resource(Visit, "/hello")

# this '/' is basically it is listening at only '/'
# or we can do '/index', then we have to go to http://127.0.0.1:5000/index
@app.route("/")
def hello():
    return "Hello World 2!"


@app.route("/maomao")
def maomao():
    return "This is mao"


@app.route("/json")
def json_return():
    retJson = {
        'field1':'abc',
        'field2':'def'
    }
    return jsonify(retJson)


@app.route("/add_two_nums", methods=["POST", "GET"])
def add_two_nums():
    dataDict = request.get_json()

    if ("x" not in dataDict) or ("y" not in dataDict):
        return "Error: request missing required parameters", 305

    x = dataDict["x"]
    y = dataDict["y"]
    result = x+y
    return jsonify({"result": result}), 200


if __name__ == "__main__":
    # this is to specify the run on the local host of the machine, not the docker system
    app.run(host="0.0.0.0")
    app.run(debug=True)
    #app.run()

"""