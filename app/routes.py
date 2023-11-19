from flask import render_template,flash, redirect
from forms import LoginForm
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




@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(" Logged in successfully user {}, remeber me : {}".format(form.username.data, form.remember_me.data))
        return redirect("/index")
    return render_template('login.html', form=form, title="Login")

from app import routes

