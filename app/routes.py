from flask import render_template,flash, redirect, url_for, request
from forms import LoginForm, RegisterForm, CaseForm, EditProfileForm, EmptyForm
from app import login, db
from app.models import User, Case
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime
from werkzeug.utils import secure_filename
from app import app


@app.route('/')
@app.route('/index')
@login_required
def index():
    cases = Case.query.all()
    return render_template('index.html', title="MediConsult", cases=cases)



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
    form=EmptyForm()
    return render_template('user.html', user=user, cases=cases, form=form)



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

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
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

@app.route('/submit_case', methods=['GET', 'POST'])
def submit_case():
    """handle form submission of a new case"""
    form = CaseForm()
    if form.validate_on_submit():
        case = Case(
            title=form.title.data,
            patient_age=form.patient_age.data,
            patient_sex=form.patient_sex.data,
            chief_complaint=form.chief_complaint.data,
            medical_history=form.medical_history.data,
            current_medications=form.current_medications.data,
            # Add other fields as needed
        )
        db.session.add(case)
        db.session.commit()
        # Save uploaded files to the file system
        try:


            image_files = form.image_files.data
            image_files_paths = []

            for image_file in image_files:
                if image_file:
                    filename = secure_filename(image_file.filename)
                    filepath = os.path.join(app.config['IMAGE_SUPLOAD_FOLDER'], filename)
                    image_file.save(filepath)
                    image_files_paths.append(filepath)
                    case.image_files =",".join(image_files_paths)

            lab_files = form.lab_files.data
            labe_files_path = []
            for lab_file in lab_files:
                if lab_file:
                    filename = secure_filename(lab_file.filename)
                    filepath = os.path.join(app.config['LABS_UPLOAD_FOLDER'], filename)
                    lab_file.save(filepath)
                    labe_files_path.append(filepath)
                    case.lab_files =",".join(labe_files_path)

            db.session.commit()
            flash('Case submitted successfully!', 'success')

        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
    return render_template('submit_case.html', form=form, title="submit medical case")



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


from app import routes

