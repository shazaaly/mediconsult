import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY  = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATION = False
    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'shaza.aly@gmail.com'
    MAIL_PASSWORD = 'pntp bgtk ibyq fkot'
    ADMIN='shaza.aly@gmail.com'
    # pagination
    CASES_PER_PAGE = 3

    # images and files
    IMAGE_SUPLOAD_FOLDER = os.path.join(basedir, 'app', 'static')
    LABS_UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static')

