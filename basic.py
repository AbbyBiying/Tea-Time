import os
from flask import Flask, request, render_template, flash, session, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, DateTimeField,
                     RadioField,SelectField,TextField,
                     TextAreaField,SubmitField)
from wtforms.validators import DataRequired
from bs4 import BeautifulSoup
import shutil
import requests
import csv
from datetime import datetime
import re
from flask_sqlalchemy import SQLAlchemy
from validate_email import validate_email

# This grabs our directory
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Connects our Flask App to our Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create sqlite db 
db = SQLAlchemy(app)

# it inherit from db.Model class
class User(db.Model):

    # The default table name will be the class name
    __tablename__ = 'User'

    ## CREATE THE COLUMNS FOR THE TABLE 
    # Primary Key column, unique id for each puppy
    id = db.Column(db.Integer,primary_key=True)
    # Username
    username = db.Column(db.Text)
    # User email
    email = db.Column(db.Text)

    # This sets what an instance in this table  
    def __init__(self,username,email):
        self.username = username
        self.email = email

    def __repr__(self):
        # This is the string representation of a puppy in the model
        return f"User {self.username}'s email' is {self.email}."

proxies = {'http' : 'http://10.10.0.0:0000',  
          'https': 'http://120.10.0.0:0000'}

# library to generate user agent
from user_agent import generate_user_agent

url='https://www.nytimes.com/'

# generate a user agent
headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
#headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.63 Safari/537.36'}
page_response = requests.get(url, timeout=5, headers=headers)


# website scraping
titles_list = []

def scraper():
    try:
        data = requests.get(url, timeout=5)
        if page_response.status_code == 200:

            html = BeautifulSoup(data.text, 'html.parser')

            titles = html.select('h2 span')

            try:
                for title in titles:
                  titles_list.append(title.string)

            except IndexError:
                return 'No matching element found.'  


            # write titles_list into csv file
            with open('index.csv', 'a') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([titles_list, datetime.now()])
        else:
            print(page_response.status_code)
            # notify, try again
    except requests.Timeout as e:
        print("It is time to timeout")
        print(str(e))
    return titles_list       

scraper()

# create a WTForm Class 
class InfoForm(FlaskForm):    
    drink_tea  = BooleanField("Do you drink tea?")
    temperature = RadioField('Hot tea/iced tea:', choices=[('hot','Hot Tea'),('iced','Iced Tea')])
    tea_choice = SelectField(u'Pick Your Favorite Tea:',
                          choices=[('Black', 'Black tea'), ('Green', 'Green tea'),
                                   ('Oolong', 'Oolong tea'),('Pu-erh','Pu-erh tea'),
                                   ('Masala_chai', 'Masala chai'),('Cold', 'Cold brew tea')])
    feedback = TextAreaField()
    submit = SubmitField('Submit')


@app.route('/tea_form', methods=['GET', 'POST'])
def home():
    # Create instance of the form.
    form = InfoForm()
    
    # Grab the data from the breed on the form.
    if form.validate_on_submit():     
        session['drink_tea'] = form.drink_tea.data
        session['temperature'] = form.temperature.data
        session['tea_choice'] = form.tea_choice.data
        session['feedback'] = form.feedback.data

        flash(f"You just changed your tea_choice to: {session['tea_choice']}")

        return redirect(url_for("thankyou"))

    return render_template('home.html', form=form)


@app.route('/')
def index():
    return render_template('index.html',titles_list=titles_list)

@app.route('/signup_form')
def signup_form():
    return render_template('signup_form.html')

@app.route('/thankyou')
def thankyou():
    username = request.args.get('username')
     
    return render_template('thankyou.html',username=username)

@app.route('/cn/<name>')
def cn(name):
    return render_template('chinese.html',name=name)

@app.route('/users')
def users():
    userslist = ['ABBY','JOHN','BIYING','SU']
    return render_template('users.html',userslist=userslist)

@app.route('/report')
def report():    
    username = request.args.get('username')

    lower_letter = False
    upper_letter = False
    num_end = False

    if username and email:
      lower_letter = any(letter.islower() for letter in username)
      upper_letter = any(letter.isupper() for letter in username)
      num_end = username[-1].isdigit()

      report = lower_letter and upper_letter and num_end
      return render_template('report.html',
        username=username,report=report,
        lower_letter=lower_letter,
        upper_letter=upper_letter,
        num_end=num_end)
    else:
      return redirect(url_for('index'))

@app.route('/user/<name>')
def user(name):
    return '<h1>This is a page for {}<h1>'.format(name.upper())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


if __name__ == '__main__':
    app.run(debug=True)
