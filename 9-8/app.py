from flask import Flask, redirect, url_for, session, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from rauth import OAuth1Service


app = Flask(__name__)
app.secret_key = 'wj9jr2jg@249j0J4h20JaV91A03f4j2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://taeomthpaemtohaemot:hmbhopmpbmaeo553gea95hjq350hgebae09tjh09aae@ec2-23-21-238-21.compute-1.amazonaws.com:5432/daba4242232di1"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

service = OAuth1Service(
    name='twitter',
    consumer_key='3q2435h45y35thae5h5',
    consumer_secret='D5e4t635h4eh64e57yjw5rZ',
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
     return render_template('index.html')

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

@app.errorhandler(401)
def authentication_failed(error):
    return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500
