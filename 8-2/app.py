from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)
app.secret_key = 'A0Z3324t5hw4hwthth'

@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in'] == True:
        return 'You are logged in'
    else:
        session['logged_in'] = True
        return 'You are not logged in'
