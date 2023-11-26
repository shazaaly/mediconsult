from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from libgravatar import Gravatar


from flask_login import UserMixin


"""ِAssosiation Table for secondary"""
followers= db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

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
    #a query returns the list of followed users, which as you already know, it would be user.followed.all()
    #get followed users:
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers',lazy='dynamic'),
        lazy='dynamic'
        )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_following(self, user):
        """check if user is already following another user """
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """unfollow user"""
        if self.is_following(user):
            self.followed.remove(user)

    def followed_cases(self):
        """return cases of followed users"""
        followed = Case.query.join(
            followers, (followers.c.followed_id == Case.user_id)
        ).filter(
            followers.c.follower_id == self.id
        ).order_by(
            Case.timestamp.desc()
        )

        own = Case.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Case.timestamp.desc())

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

    def get_images(self):
        """get images of case """
        return self.image_files.split(',') if self.image_files else []

    def get_lab_files(self):
        return self.lab_files.split(",") if self.lab_files else []

    def __repr__(self) -> str:
        return '<Case Title {} - chief_complaint {}>'.format(self.title, self.chief_complaint)