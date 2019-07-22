import os
from forms import InfoForm, AddTeaForm

from flask import Flask, request, render_template, flash, session, redirect, url_for, session

from wtforms.validators import DataRequired
import shutil
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from validate_email import validate_email
import csv
import re
from bs4 import BeautifulSoup


# This grabs our directory
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Key for Forms
app.config['SECRET_KEY'] = 'mysecretkey'

# Connects our Flask App to our Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create sqlite db 
db = SQLAlchemy(app)
# Add on migration capabilities in order to run terminal commands
Migrate(app,db)

###################################
# MODELS
# it inherit from db.Model class
class User(db.Model):

    # The default table name will be the class name
    __tablename__ = 'User'

    ## CREATE THE COLUMNS FOR THE TABLE 
    # Primary Key column, unique id for each user
    id = db.Column(db.Integer,primary_key=True)
    # Username
    username = db.Column(db.Text)
    # User email
    email = db.Column(db.Text)

    # This is a one-to-one relationship
    # A user can have only one fav type of tea
    tea = db.relationship('Tea',backref='user',uselist=False)

    # This sets what an instance in this table  
    def __init__(self,username,email):
        self.username = username
        self.email = email

    def __repr__(self):
        if self.tea:
            # This is the string representation of a user in the model
            return f"User {self.username}'s email' is {self.email}, user ID:{self.id}, his/her fav tea is {self.tea.tea_choice}"
        else:
            return f"User {self.username}'s email' is {self.email}, user ID:{self.id}, no tea yet."
   
    def report_tea(self):
        print("Here is my fav tea!")
        print(self.tea)        
        

class Tea(db.Model):

    # The default table name will be the class name
    __tablename__ = 'Tea'

    ## CREATE THE COLUMNS FOR THE TABLE 
    # Primary Key column, unique id for each user
    id = db.Column(db.Integer,primary_key=True)
    # Username
    temperature = db.Column(db.Text)
    # User email
    tea_choice = db.Column(db.Text)

    # Connect the tea to the user that owns it.
    user_id = db.Column(db.Integer,db.ForeignKey('User.id'))

    # This sets what an instance in this table  
    def __init__(self,temperature,tea_choice,user_id):
        self.temperature = temperature
        self.tea_choice = tea_choice
        self.user_id = user_id

    def __repr__(self):
        # This is the string representation of a tea in the model
        if self.user_id:
            return f"Tea {self.tea_choice}'s temperature is {self.temperature}, ID:{self.id}, user is {self.user_id}"
        else:
            return f"Tea {self.tea_choice}'s temperature is {self.temperature}, ID:{self.id}, no users yet"



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


@app.route('/tea_form', methods=['GET', 'POST'])
def tea():
    # Create instance of the form.
    form = InfoForm()
    
    # Grab the data from the breed on the form.
    if form.validate_on_submit():     
        session['temperature'] = form.temperature.data
        session['tea_choice'] = form.tea_choice.data

        flash(f"You just changed your tea_choice to: {session['tea_choice']}")

        return redirect(url_for("thankyou"))

    return render_template('tea.html', form=form)

@app.route('/add_tea', methods=['GET', 'POST'])
def add_tea():
    # Create instance of the form.
    form = AddTeaForm()
    
    # Grab the data from the breed on the form.
    if form.validate_on_submit():     
        temperature = form.temperature.data
        tea_choice = form.tea_choice.data
        user_id = User.query.first().id
        
        # Add new tea to DB
        new_tea = Tea(temperature,tea_choice,user_id)
        db.session.add(new_tea)
        db.session.commit()


        return redirect(url_for("list_tea"))

    return render_template('add_tea.html', form=form)

@app.route('/userslist')
def list_user():
    # Grab a list of users from database.
    users = User.query.all()
    return render_template('userslist.html', users=users)

@app.route('/tealist')
def list_tea():
    # Grab a list of tea from database.
    tea = Tea.query.all()
    return render_template('tealist.html', tea=tea)

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
    email = request.args.get('email')

    lower_letter = False
    upper_letter = False
    num_end = False
    validatedemail = False

    if (username and email):
      lower_letter = any(letter.islower() for letter in username)
      upper_letter = any(letter.isupper() for letter in username)
      num_end = username[-1].isdigit()
      validatedemail = validate_email(email)

      report = lower_letter and upper_letter and num_end and validatedemail
      
      if report:
        # if user info is validated, pass it to DB
        new_user = User(username, email)
        db.session.add(new_user)
        db.session.commit()

      return render_template('report.html',
        username=username,report=report,
        lower_letter=lower_letter,
        upper_letter=upper_letter,
        num_end=num_end,
        validatedemail = validatedemail)
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
