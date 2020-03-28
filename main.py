from flask import Flask, render_template, redirect,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import requests
import json
from flask_marshmallow import Marshmallow
import os,datetime
import random, string
from flask import Response
from datetime import date
app = Flask(__name__)



#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'corona_api' 
ma = Marshmallow(app)


class corona_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(50), unique=True)
    confirmed = db.Column(db.Integer)
    discharged = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    
    def __init__(self,id,state,confirmed,discharged,deaths):
        self.id = id
        self.state =state
        self.confirmed = confirmed
        self.discharged = discharged
        self.deaths = deaths

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    email = db.Column(db.String(100))
    api_key = db.Column(db.String(100))
    created_at = db.Column(db.String(50),default=datetime.datetime.utcnow) 
    def __init__(self,id,email,api_key,created):
        self.id = ma.auto_field()
        self.email = email
        self.api_key = api_key
        
        
class CoronaAPI(ma.Schema):
    class Meta:
        fields = ("id", "state", "confirmed","discharged","deaths")

class UsersAPI(ma.Schema):
    class Meta:
        fields = ("id", "email","api_key")      

corona_schema = CoronaAPI()
coronas_schema = CoronaAPI(many=True)
users_schema =  UsersAPI(many=True)
user_schema = UsersAPI()

    
       
@app.route('/hello')
def sh():
    return "hello world"
        
@app.route('/api/all/<api_key>')
def hello(api_key):
    check_api = Users.query.filter_by(api_key=api_key).first()
    if check_api:
        data = corona_data.query.all()
        response = coronas_schema.dump(data)
        return jsonify(response)
    else:
        response = {"error": "incorrect API key"}
        return response


@app.route('/api/state/<api_key>/<state>')
def show(api_key,state):
    check_api = Users.query.filter_by(api_key=api_key).first()
    if check_api:
        result = corona_data.query.filter_by(state=state.lower())
        response = coronas_schema.dump(result)
        return jsonify(response)
    else:
        response = {"error": "incorrect API key"}
        return response



@app.route('/api/users')
def all_users():
    data = Users.query.all()
    response = users_schema.dump(data)
    return jsonify(response)

@app.route('/api/users/<id>')
def user(id):
    data = Users.query.filter_by(id = id).first()
    db.session.delete(data)
    db.session.commit()
    response = {'message':'Deleted', 'status':200}
    return jsonify(response)



@app.route('/collect')
def collect():
    url = "https://www.mohfw.gov.in/"
    real = []
    data = requests.get(url)
    soup = BeautifulSoup(data.text, 'html.parser')
    real_data = ""
    for tr in soup.find_all('tbody')[7].find_all('tr'):
          real_data+=tr.get_text()

    data_real = (real_data.split('\n\n'))
    something = []
    for r in data_real:
        something.append(r.split('\n'))
    something[0].pop(0)
    # ['1', 'Andhra Pradesh', '9', '0', '0', '0']
    index = 0
    for s in something:
        id = s[0]
        state = s[1].lower()
        confirmed = s[2]
        discharged = s[4]
        deaths = s[5]        
        data= corona_data(id=id,state = state, confirmed = confirmed, discharged =discharged,deaths =deaths)
        db.session.add(data)
        db.session.commit()
        if s[0] == 25:
            break
    return "success"







@app.route('/api/delete')
def blogPage():
    data = corona_data.query.all()
    for i in data:
        db.session.delete(i)
        db.session.commit()
    return "Sucess"





@app.route('/users/<email>')
def global_api(email):
    api_key = ''.join(random.choices(string.ascii_letters + string.digits, k=25))
    user = Users(id=1,email = email, api_key = api_key,created="0")
    db.session.add(user)
    db.session.commit()  
    response = {
            'email' :email,
            'api_key' : api_key,
            'status' : 200
        }
    
    return response




    


if __name__ == '__main__':
    app.debug = True
    app.run()     