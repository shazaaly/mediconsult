
from flask import current_app
from app import db
from datetime import datetime
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from libgravatar import Gravatar
from flask_login import UserMixin
import jwt

from sqlalchemy_searchable import make_searchable


"""ِAssosiation Table for secondary"""
followers= db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class Comment(db.Model):
    """
    Represents a comment made on a case.

    Attributes:
        id (int): The unique identifier of the comment.
        text (str): The text content of the comment.
        timestamp (datetime): The timestamp of when the comment was made.
        user_id (int): The ID of the user who made the comment.
        case_id (int): The ID of the case the comment belongs to.
    """

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))

    def __repr__(self) -> str:
        return '<comment  {} >'.format(self.text)

class User(UserMixin,db.Model):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password_hash (str): The hashed password of the user.
        bio (str): The bio of the user.
        medical_degree (str): The medical degree of the user.
        speciality (str): The speciality of the user.
        licenses (str): The licenses of the user.
        last_seen (datetime): The last time the user was seen.
        cases (relationship): The cases associated with the user.
        followed (relationship): The users followed by the user.
        comments (relationship): The comments made by the user.
    """

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
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers',lazy='dynamic'),
        lazy='dynamic'
    )
    comments= db.relationship('Comment', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_following(self, user):
        """Check if the user is already following another user.

        Args:
            user (User): The user to check if it is being followed.

        Returns:
            bool: True if the user is following the other user, False otherwise.
        """
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        """Follow another user.

        Args:
            user (User): The user to follow.
        """
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """Unfollow another user.

        Args:
            user (User): The user to unfollow.
        """
        if self.is_following(user):
            self.followed.remove(user)

    def followed_cases(self):
        """Return cases of followed users.

        Returns:
            Query: The query object containing the cases of followed users.
        """
        followed = Case.query.join(
            followers, (followers.c.followed_id == Case.user_id)
        ).join(
            User, (User.id == followers.c.follower_id)
        ).filter(User.id == self.id)

        own = Case.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Case.timestamp.desc())

    def avatar(self, size=120):
        gravatar = Gravatar(self.email)
        gravatar_url_custom = gravatar.get_image(
            size=size,
            default='identicon',
            force_default=True,
            rating='pg',
            filetype_extension=True,
            use_ssl=True
        )
        return gravatar_url_custom

    def generate_token(self, expires_in=600):
        """Generate a JWT token.

        Args:
            expires_in (int): The expiration time of the token in seconds. Default is 600 seconds.

        Returns:
            str: The generated JWT token.
        """
        return jwt.encode(
            {
                'reset_password': self.id,
                'exp': time() + expires_in
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_user_token(token):
        """Verify a user token and return the corresponding user.

        Args:
            token (str): The token to verify.

        Returns:
            User: The user corresponding to the token, or None if the token is invalid.
        """
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithm='HS256')['reset_password']
        except:
            return
        user = User.query.get(id)
        return user

    def __repr__(self):
        return '<user {}>'.format(self.username)



class Case(db.Model):
    #__tablename__ = 'case'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    question = db.Column(db.String(140))
    patient_age = db.Column(db.String(20))
    patient_sex = db.Column(db.String(10))
    chief_complaint = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    # Add columns for image and lab files
    image_files = db.Column(db.String(255))  # Store file paths for images
    lab_files = db.Column(db.String(255))  # Store file paths for lab files
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='case', lazy='dynamic')

    def get_images(self):
        """Get the images associated with the case.

        Returns:
            list: A list of image file paths.
        """
        return self.image_files.split(',') if self.image_files else []

    def get_lab_files(self):
        """Get the lab files associated with the case.

        Returns:
            list: A list of lab file paths.
        """
        return self.lab_files.split(",") if self.lab_files else []

    def __repr__(self) -> str:
        return '<Case Title {} - chief_complaint {}>'.format(self.title, self.chief_complaint)
