# -*- coding: utf-8 -*-
import os
from flask import Flask, request, render_template, make_response, send_from_directory, jsonify, session
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from pymongo import MongoClient

import subprocess
import json

import ip_lookup


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Maomao have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()

client = MongoClient("mongodb://db:27017")
db = client.VisitorRecord
visitors = db["Visitors"]

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

headers = {'Content-Type': 'text/html'}


class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'Please Upload Image only'), FileRequired(u'The file was empty!')])
    submit = SubmitField(u'Upload')


def visitor_exist(visitor_ip):
    if visitors.find({"visitor_ip": visitor_ip}).count() == 0:
        return False
    return True

def create_visitor_record(visitor_ip):
    visitor_info = ip_lookup.get_info(visitor_ip)
    visitors.insert({
            "visitor_ip": visitor_ip,
            "visit_num": 1,
            "visitor_info": visitor_info
        })
def update_visitor_record(visitor_ip):
    if visitor_exist(visitor_ip):
        previous_visit_num = visitors.find({"visitor_ip": visitor_ip})[0]["visit_num"]
        visitors.update({"visitor_ip": visitor_ip}, {"$set": {"visit_num": previous_visit_num+1}})
    else:
        create_visitor_record(visitor_ip)

def track_visitor():
    visitor_ip = request.environ['REMOTE_ADDR']
    if 'visitor_ip' not in session:
        session['visitor_ip'] = visitor_ip
        update_visitor_record(visitor_ip)

def get_all_visits():
    return jsonify(
        list(
            visitors.find({}, {"_id": 0, "visitor_ip": 1, "visit_num": 1})
        )
    )

@app.route('/')
def hello_world():
    track_visitor()
    return make_response(render_template('index.html'), 200, headers)
    # return 'You can find: \n Project [Exploration on Death and Time] at /Lifetime \n ' \
    #        'Project [Mental Health] at /MentalHealth'


@app.route('/Time')
def death_and_time():
    return make_response(render_template('death_and_time.html'), 200, headers)


@app.route('/MentalHealth')
def mental_health():
    return make_response(render_template('mental_health.html'), 200, headers)


@app.route('/HarryPotter')
def harry_potter():
    return make_response(render_template('harry_potter.html'), 200, headers)


@app.route('/ImgClass', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data, name='temp.jpg')
        file_url = photos.url(filename)

        proc = subprocess.Popen(
            "python tensor_image_classifier.py --model_dir=./tensor_model --image_file=./"+filename,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        ret = proc.communicate()[0]
        proc.wait()
        with open("predictions.txt") as predict_file:
            predictions = json.load(predict_file)
            predict_item = predictions["0"]["item"]
            predict_score = int(float(predictions["0"]["score"]) * 100)
            results = "Min thinks this is [" + predict_item + "] with about " + str(predict_score) + "% confidence. "

        # if os.path.exists("./temp.jpg"):
        #     os.remove("./temp.jpg")
    else:
        file_url = None
        results = None
    return render_template('upload.html', form=form, file_url=file_url, results=results)


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    visitor_ip = request.environ['REMOTE_ADDR']
    visitor_info = ip_lookup.get_info(visitor_ip)
    return jsonify({
            "visitor_ip": visitor_ip,
            "visit_num": 1,
            "visitor_info": visitor_info
        })

@app.route("/get_visits")
def get_visits():
    secret_code = request.args.get("secret_code")
    if secret_code == 'catdog':
        return get_all_visits()
    return 404

@app.route('/img/<path:filepath>')
def img_data(filepath):
    return send_from_directory('static/img', filepath)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4999, debug=False)
