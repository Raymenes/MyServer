# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

import subprocess
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField(u'Upload')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data, name='temp.jpg')
        file_url = photos.url(filename)

        proc = subprocess.Popen(
            "python tensor_image_classifier.py --model_dir=./tensor_model --image_file=./temp.jpg",
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        ret = proc.communicate()[0]
        proc.wait()
        with open("predictions.txt") as predict_file:
            results = str(json.load(predict_file))

    else:
        file_url = None
        results = None
    return render_template('upload.html', form=form, file_url=file_url, results=results)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)