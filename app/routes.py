from flask import render_template,flash, redirect, url_for
from forms import LoginForm
from app import login
from app.models import User
from flask_login import current_user, login_user, logout_user
from app import app



@app.route('/')
@app.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    user = {'username': 'Shaza'}
    return render_template('index.html', username=user['username'], title="MediConsult", posts=posts)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))



@app.route("/login", methods=['GET', 'POST'])
def login():
    """check if the user is logged in or not: is_authenticated"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form, title="Login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))



from app import routes

