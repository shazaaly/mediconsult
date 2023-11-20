from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from libgravatar import Gravatar


from flask_login import UserMixin

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(65), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(200))
    medical_degree = db.Column(db.String(100))
    speciality = db.Column(db.String(100))
    licenses = db.Column(db.String(200))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    cases = db.relationship('Case', backref='author', lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size=120):
        gravatar = Gravatar(self.email)
        # Generate a Gravatar URL with customized settings
        gravatar_url_custom = gravatar.get_image(
            size=size,
            default='identicon',
            force_default=True,
            rating='pg',
            filetype_extension=True,
            use_ssl=True
            )
        return gravatar_url_custom



    def __repr__(self):
        return '<user {}>'.format(self.username)

class Case(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return '<Case Title {} - Body {}>'.format(self.title, self.body)
