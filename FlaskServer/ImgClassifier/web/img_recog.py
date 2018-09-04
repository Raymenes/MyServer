from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient
import bcrypt
import requests
import subprocess
import json

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]

""" Helper functions """
def user_exist(username):
    if users.find({"username": username}).count() == 0:
        return False
    return True

# @param username - the username string
# @param password - the unencrypted password string
def user_password_correct(username, password):
    # username not existing in database
    if not user_exist(username):
        return False

    hashed_password = users.find({"username": username})[0]["password"]
    if bcrypt.hashpw(password.encode("utf-8"), hashed_password) == hashed_password:
        return True
    else:
        return False

def verify_user_credential(posted_data, username, password):
    # Validate username is not already existing
    if not user_exist(username):
        return False, jsonify({
            "Message": "username does not exist",
            "Status Code": 302
        })

    if not user_password_correct(username, password):
        return False, jsonify({
            "Message": "password incorrect",
            "Status Code": 303
        })

    return True, None


# @param posted_date - json data
# @param expected_params - list of string as expected fields in posted_date
def validate_posted_data(posted_data, expected_params):
    for param in expected_params:
        if param not in posted_data:
            return False

    return True


def subtract_user_token(username, number):
    if not user_exist(username):
        return False, jsonify({
            "Message": "username does not exist",
            "Status Code": 302
        })

    remaining = hashed_password = users.find({"username": username})[0]["tokens"]

    if remaining - number < 0:
        return False, jsonify({
            "Message": "not enough tokens for transaction",
            "Token remaining": remaining,
            "Token required": number,
            "Status Code": 302
        })
    remaining -= number
    users.update({"username": username}, {"$set": {"tokens": remaining}})

    return True, None


class Register(Resource):
    def post(self):
        posted_data = request.get_json()

        # Validate request
        if not validate_posted_data(posted_data, ["username", "password"]):
            return jsonify({
                "Message": "need username and password in the request",
                "Status Code": 301
            })

        # Get the data
        username = str(posted_data["username"])
        password = str(posted_data["password"])

        # Validate username is not already existing
        if user_exist(username):
            return jsonify({
                "Message": "username is already taken",
                "Status Code": 302
            })

        # Hash sensitive data
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store username and hashed password into database
        users.insert({
            "username": username,
            "password": hashed_password,
            "tokens": 5
        })

        return jsonify({
            "Message": "Successfully signed up user: " + username,
            "Status Code": 200
        })


class Unregister(Resource):
    def post(self):
        posted_data = request.get_json()

        # Validate request
        if not validate_posted_data(posted_data, ["username", "password"]):
            return jsonify({
                "Message": "need username and password in the request",
                "Status Code": 301
            })

        # Get the data
        username = str(posted_data["username"])
        password = str(posted_data["password"])

        verification = verify_user_credential(posted_data, username, password)
        if not verification:
            return verification

        users.delete({"username": username})

        return jsonify({
            "Message": "Successfully delete user: " + username,
            "Status Code": 200
        })


class DisplayUser(Resource):
    def get(self):
        return jsonify(
            list(
                users.find({}, {"_id": 0, "username": 1, "tokens": 1})
            )
        )

class Classify(Resource):
    def post(self):
        posted_data = request.get_json()

        # Validate request
        if not validate_posted_data(posted_data, ["username", "password", "image_url"]):
            return jsonify({
                "Message": "need username and password in the request",
                "Status Code": 301
            })

        # Get the data
        username = str(posted_data["username"])
        password = str(posted_data["password"])
        url = str(posted_data["image_url"])

        valid, message = verify_user_credential(posted_data, username, password)
        if not valid:
            return message

        success, message = subtract_user_token(username, 1)
        if not success:
            return message

        image_request = requests.get(url)
        with open("temp.jpg", "wb") as image_file:
            image_file.write(image_request.content)
            # image_file.close()
            proc = subprocess.Popen(
                "python tensor_image_classifier.py --model_dir=./tensor_model --image_file=./temp.jpg",
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            ret = proc.communicate()[0]
            proc.wait()
            with open("predictions.txt") as predict_file:
                results = json.load(predict_file)

        return results


class Refill(Resource):
    def post(self):
        posted_data = request.get_json()

        # Validate request
        if not validate_posted_data(posted_data, ["username", "password", "amount"]):
            return jsonify({
                "Message": "missing arguments in the request",
                "Status Code": 301
            })

        # Get the data
        username = str(posted_data["username"])
        password = str(posted_data["password"])
        amount = int(posted_data["amount"])

        valid, message = verify_user_credential(posted_data, username, password)
        if not valid:
            return message

        success, message = subtract_user_token(username, amount * -1)
        if not success:
            return message

        return jsonify({
                "Message": "sucessfully refilled",
                "Status Code": 301
            })


api.add_resource(Register, "/register")
api.add_resource(Unregister, "/unregister")
api.add_resource(DisplayUser, "/display")
api.add_resource(Refill, "/refill")
api.add_resource(Classify, "/classify")

if __name__ == "__main__":
    # this is to specify the run on the local host of the machine, not the docker system
    app.run(host="0.0.0.0")
    app.run(debug=True)
    # app.run()
