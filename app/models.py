import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from flask import current_app
from time import time
import jwt

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#The strategy is to have this implemented and take out the links to add followers. So you only see your own posts in the feed. Maybe we could use in Markov app
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    businessName = db.Column(db.String(120))
    services = db.Column(db.String(120))
    email = db.Column(db.String(120), index = True, unique =True)
    password_hash = db.Column(db.String(128))
    zip_code = db.Column(db.Integer)
    coreService = db.Column(db.String(120), index = True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    followed = db.relationship('User', secondary=followers,primaryjoin=(followers.c.follower_id == id),secondaryjoin=(followers.c.followed_id == id),backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        #return followed.union(own).order_by(Post.timestamp.desc())
        return own.order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    socialnetwork = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #This is the stuff for scheduling, just date
    hour = db.Column(db.Integer)
    minute = db.Column(db.Integer)
    day = db.Column(db.Integer)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    ampm = db.Column(db.String(2))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Twittertokens(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #user_id = db.Column(db.String, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer)
    token = db.Column(db.String(640))
    token_secret = db.Column(db.String(640))
    #users = db.relationship(User)


class Facebooktokens(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer)
    access_token_fb= db.Column(db.String(640))
    #users = db.relationship(User)
    #Use this as a place holder, but will dynamically create page tokens

class Bestdicts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    hourdic = db.Column(db.String(640))
    socialnetwork = db.Column(db.String(40))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    user_username = db.Column(db.String(64), db.ForeignKey('user.username'))
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



class Feeds(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    feedlink = db.Column(db.String(140))
    industry = db.Column(db.String(140))

class FacebookAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    u_username = db.Column(db.String(64), db.ForeignKey('user.username'))
    date_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    n_followers = db.Column(db.Integer)
    n_haha = db.Column(db.Integer)
    n_sad = db.Column(db.Integer)
    n_wow = db.Column(db.Integer)
    n_love = db.Column(db.Integer)
    n_angry = db.Column(db.Integer)
    n_comments = db.Column(db.Integer)
    n_likes = db.Column(db.Integer)
    n_shares = db.Column(db.Integer)
    n_reactions = db.Column(db.Integer)
    n_engagement = db.Column(db.Integer)

class TwitterAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    u_username = db.Column(db.String(64), db.ForeignKey('user.username'))
    date_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    n_followers = db.Column(db.Integer)
    n_favorites = db.Column(db.Integer)
    n_retweets = db.Column(db.Integer)
    n_tweets = db.Column(db.Integer)
    n_engagement = db.Column(db.Integer)


class FeedItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    link = db.Column(db.String(140))
    title = db.Column(db.String(140))
    industry = db.Column(db.String(140))


    def __repr__(self):
        return '<FeedItem {}>'.format(self.title)
