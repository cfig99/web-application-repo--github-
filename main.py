from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os


basedir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

app = Flask(__name__)

app.secret_key = 'c18984e00e031fe58f9ce8f266ac7f1e0d8aff8a45a7db6d'
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))

    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)

    favorites = db.relationship('GasStation', secondary='user_favorites', back_populates='favorited_by')

class GasStation(db.Model):
    __tablename__ = 'gas_stations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    street = db.Column(db.String(128))
    url = db.Column(db.String(256), unique=True)

    favorited_by = db.relationship('User', secondary='user_favorites', back_populates='favorites')

user_favorites = db.Table('user_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('gas_station_id', db.Integer, db.ForeignKey('gas_stations.id'), primary_key=True)
)

@app.route('/')
def index():
    db.create_all()

    log = 'index'
    return render_template('index.html', log_index=log)

@app.route('/GasCheck')
def gasCheck():
    user_logged_in = 'logged_in' in session
    return render_template('GasCheck.html', user_logged_in=user_logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch the user from the database
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['logged_in'] = True
            session['user_id'] = user.id 
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')
        
@app.route('/signup', methods =  ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return 'Username already in use'
        new_user = User(username=username, password=password, first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/about')
def about():
    log = 'about'
    return render_template('about.html', log_index=log)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_favorite', methods=['POST'])
def add_favorite():

    user_id = session['user_id']
    data = request.get_json()
    gas_station = GasStation.query.filter_by(url=data['url']).first()
    if not gas_station:
        gas_station = GasStation(name=data['name'], street=data['street'], url=data['url'])
        db.session.add(gas_station)
        db.session.flush()

    user = User.query.get(user_id)
    if gas_station not in user.favorites:
        user.favorites.append(gas_station)
        db.session.commit()

    return jsonify({'message': 'Station added to favorites'})

@app.route('/get_favorites')
def get_favorites():

    user_id = session['user_id']
    user = User.query.get(user_id)

    favorites = [{
        'name': station.name,
        'street': station.street,
        'url': station.url
    } for station in user.favorites]

    return jsonify(favorites)

if __name__ == '__main__':
    app.debug = True
    ip = '127.0.0.1'
    app.run(host=ip)
    