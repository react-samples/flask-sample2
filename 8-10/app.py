from flask import Flask, redirect, url_for, session, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from datetime import datetime
from rauth import OAuth1Service


app = Flask(__name__)
app.secret_key = 'wj9jr2jg@249j0J4h20JaV91A03f4j2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/hostdb"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
migrate = Migrate(app, db)

service = OAuth1Service(
    name='twitter',
    consumer_key='5bdOd32t4jg09jrhq390j0',
    consumer_secret='DmNMyf42j9jh530qjhb90pmpo4jx48IbIPhbZ',
    request_token_url='https://api.twitter.com/oauth/request_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    access_token_url='https://api.twitter.com/oauth/access_token',
    base_url='https://api.twitter.com/1.1/'
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    description = db.Column(db.String(1024))
    user_image_url = db.Column(db.String(1024))
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    twitter_id = db.Column(db.String(64), nullable=False, unique=True)
    def __repr__(self):
        return '<User %r>' % self.username

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    profile_image_url = db.Column(db.String(1024))
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answerer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answerer_image_url = db.Column(db.String(1024))
    answer_body = db.Column(db.String(256))
    def __repr__(self):
        return '<User %r>' % self.body


@app.route('/')
def index():
     users = User.query.all()
     return render_template('index.html', users=users)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<id>')
def user(id):
    user = User.query.get(int(id))
    if user:
        questions = db.session.query(Question).filter(Question.answerer_id==id).all()
        print(questions)
        return render_template('user.html', user=user, questions=questions)
    else:
        return render_template('error.html')

@app.route('/question', methods=['POST'])
@login_required
def question():
    if request.form['body']:
       newQuestion = Question(
                       body=request.form['body'],
                       profile_image_url=current_user.user_image_url,
                       user_id=current_user.id,
                       answerer_image_url=request.form['answerer_image_url'],
                       answerer_id=request.form['answerer_id']
                     )
       db.session.add(newQuestion)
       db.session.commit()
       return render_template('index.html')
    else:
        return render_template('error.html')

@app.route('/answer_to/<id>', methods=['GET'])
@login_required
def answers(id):
    question = Question.query.get(int(id))
    if int(question.answerer_id) == int(current_user.id):
        return render_template('answer.html', question=question)

@app.route('/answer', methods=['POST'])
@login_required
def answer():
    question = db.session.query(Question).filter(Question.id==int(request.form['id'])).first()
    if int(question.answerer_id) == int(current_user.id) and request.form['answer_body']:
        question.answer_body = request.form['answer_body']
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('error.html')

@app.route('/oauth/twitter')
def oauth_authorize():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    else:
        request_token = service.get_request_token(
            params={'oauth_callback': url_for('oauth_callback', provider='twitter',
            _external=True)}
        )
        session['request_token'] = request_token
        return redirect(service.get_authorize_url(request_token[0]))

@app.route('/oauth/twitter/callback')
def oauth_callback():
    request_token = session.pop('request_token')
    oauth_session = service.get_auth_session(
        request_token[0],
        request_token[1],
        data={'oauth_verifier': request.args['oauth_verifier']}
    )

    profile = oauth_session.get('account/verify_credentials.json').json()

    twitter_id = str(profile.get('id'))
    username = str(profile.get('name'))
    description = str(profile.get('description'))
    profile_image_url = str(profile.get('profile_image_url'))

    user = db.session.query(User).filter(User.twitter_id==twitter_id).first()

    if user:
        user.twitter_id = twitter_id
        user.username = username
    else:
        user = User(twitter_id = twitter_id,
                   username=username,
                   description=description,
                   user_image_url=profile_image_url)
        db.session.add(user)

    db.session.commit()
    # このユーザー情報を元にセッションを生成
    login_user(user, True)
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
