from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/testdb"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(120), index=True, unique=True)
    user_image_url = db.Column(db.String(120), index=True, unique=True)
    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.cli.command('initdb')
def initdb_command():
    db.create_all()
