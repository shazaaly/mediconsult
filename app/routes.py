from flask import render_template,flash, redirect, url_for, request
from forms import LoginForm
from forms import RegisterForm
from app import login, db
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime
from forms import EditProfileForm, EmptyForm
from app import app


@app.route('/')
@app.route('/index')
@login_required
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
    return render_template('index.html', title="MediConsult", posts=posts)



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
        if user is None or not user.password_hash or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page) != '':
            return redirect(url_for('index'))
        return redirect(url_for(next_page))
    return render_template('login.html', form=form, title="Login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    """create a new user
    """
    if current_user.is_authenticated:
        return redirect('index')
    form = RegisterForm()
    if form.validate_on_submit():
        user=User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    cases = [
        {'author':  user, 'body':'Test post 1'}
    ]
    return render_template('user.html', user=user, cases=cases)



@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.medical_degree = form.medical_degree.data
        current_user.speciality = form.speciality.data
        current_user.licenses = form.licenses.data
        db.session.commit()
        flash("Your Profile Has Been Updated Successfully")
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio
        form.medical_degree.data = current_user.medical_degree
        form.speciality.data = current_user.speciality
        form.licenses.data = current_user.licenses

    return render_template('edit_profile.html', form=form, title="Edit Profile")

@app.route("/follow/<username>", methods=['POST'])
@login_required
def follow(username):
    """follow  a user"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("User {} does not exist".format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash("You cannot follow yourself")
            return redirect(url_for('index'))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


from app import routes

