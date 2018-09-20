from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, BooleanField, DateTimeField, RadioField,
                     SelectField, TextField, TextAreaField, SubmitField)
from wtforms.validators import DataRequired, URL


app = Flask(__name__)

app.config['SECRET_KEY'] = 'MaoSecretKey'

class InfoForm(FlaskForm):
    breed = StringField('What breed are you', validators=[DataRequired()])
    neutered = BooleanField('Have you been neutered?')
    mood = RadioField("Please choose your mood:",
                      choices=[('mood_one', 'Happy'), ('mood_two', 'Nah'), ('mood_one', 'Angry')])
    food_choice = SelectField(u'Pick your favorite food:',
                              choices=[('chicken', 'Chicken'), ('beef', 'Beef'),
                                       ('fish', 'Fish'), ('cookie', 'Cookie')])
    feedback = TextAreaField('Any other feedback:')
    imgFile = FileField('Your image:', validators=[FileRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/survey", methods=['GET', 'POST'])
def survey():
    form = InfoForm()
    if form.validate_on_submit():
        session['breed'] = form.breed.data
        session['neutered'] = form.neutered.data
        session['mood'] = form.mood.data
        session['food_choice'] = form.food_choice.data
        session['feedback'] = form.feedback.data

        # filename = form.imgFile.data.filename
        # print(filename)
        # form.imgFile.data.save(filename)

        flash("Thank you for submitting the file:")

        return redirect(url_for('survey_thank_you'))
    else:
        if len(form.imgFile.errors) > 0:
            errorMsg = [0]
            flash(errorMsg)

    return render_template('survey.html', form=form)

@app.route("/survey_thank_you")
def survey_thank_you():
    return render_template('survey_thank_you.html', session=session)

@app.route("/signup_form")
def signup_form():
    return render_template('signup.html')

@app.route("/thank_you")
def thank_you():
    user_email = request.args.get('user_email')

    return render_template('thankyou.html', email=user_email)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
