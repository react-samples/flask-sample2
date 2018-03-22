from flask import Flask, redirect, url_for, session, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from datetime import datetime
from rauth import OAuth1Service


app = Flask(__name__)
app.secret_key = 'wj9jr2jg@249j0J4h20JaV91A03f4j2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/hotdb"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'index'
migrate = Migrate(app, db)

service = OAuth1Service(
    name='twitter',
    consumer_key='5bd42rjh9q3j50j09j0e',
    consumer_secret='DmNMy3j5hqhq59hj90q4thtohmtobIPhbZ',
    request_token_url='https://api.twitter.com/oauth/request_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    access_token_url='https://api.twitter.com/oauth/access_token',
    base_url='https://api.twitter.com/1.1/'
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(1024), index=True, unique=True)
    user_image_url = db.Column(db.String(1024), index=True, unique=True)
    date_published = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    twitter_id = db.Column(db.String(64), nullable=False, unique=True)
    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/')
def index():
     return render_template('index.html')

@app.route('/logout')
def logout():

    logout_user()
    return redirect(url_for('index'))

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
