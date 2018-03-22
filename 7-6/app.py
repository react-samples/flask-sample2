from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

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



@app.cli.command('initdb')
def initdb_command():
    db.create_all()
