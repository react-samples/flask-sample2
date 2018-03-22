from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/testdb"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(120), index=True, unique=True)
    user_image_url = db.Column(db.String(120), index=True, unique=True)
    date_published = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/')
def index():

     users = User.query.all()

     return render_template('index.html', users=users)

@app.route('/form')
def form():

    return render_template('form.html')

@app.route('/register', methods=['POST'])
def register():
    if request.form['username'] and request.form['description'] and request.files['image']:

        f = request.files['image']
        filepath = 'static/' + secure_filename(f.filename)
        f.save(filepath)

        filepath = '/' + filepath

        newUser = User(username=request.form['username'],
                       description=request.form['description'],
                       user_image_url=filepath)
        db.session.add(newUser)
        db.session.commit()

        return render_template('result.html', username=request.form['username'], description=request.form['description'])
    else:
        return render_template('error.html')
