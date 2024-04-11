from flask import Flask, render_template, jsonify, json

app = Flask(__name__)

@app.route('/')
def index():
    log = 'index'
    return render_template('index.html', log_index=log)

@app.route('/GasCheck')
def gasCheck():
    log = 'gasCheck'
    return render_template('GasCheck.html', log_index=log)

@app.route('/login')
def login():
    log = 'login'
    return render_template('login.html', log_index=log)

@app.route('/signup')
def signup():
    log = 'login'
    return render_template('signup.html', log_index=log)

@app.route('/about')
def about():
    log = 'about'
    return render_template('about.html', log_index=log)

if __name__ == '__main__':
    app.debug = True
    ip = '127.0.0.1'
    app.run(host=ip)
    