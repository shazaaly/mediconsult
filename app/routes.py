from flask import render_template, flash, redirect, url_for, request, g
from forms import SearchForm
from flask import g
import os
from forms import LoginForm, RegisterForm, CaseForm, EditProfileForm, EmptyForm, ResetPasswordRequestForm, ResetPasswordForm, CommentForm, SearchForm
from app import login, db
from app.models import User, Case
from app.models import Comment
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_mail import Message
from app.email import send_password_reset_email



from app import app


@app.route('/')
@app.route('/index')
def index():
    # cases = Case.query.all()
    # page = request.args.get('page', 1, type=int)
    #cases = current_user.followed_cases().paginate(
        #page=page, per_page=app.config['CASES_PER_PAGE'], error_out=False)
    #return render_template('index.html', title="MediConsult", cases=cases.items)
    return render_template('index.html', title="MediConsult")

@app.route('/')
@app.route('/about')
def about():

    return render_template('about.html', title="MediConsult")

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)

    cases = Case.query.order_by(Case.timestamp.desc()).paginate(page=page, per_page=app.config['CASES_PER_PAGE'], error_out=False)
    return render_template('explore.html', title='Explore', cases=cases.items)


@app.route("/show_case/<case_id>", methods=['GET', 'POST'])
def show_case(case_id):
    case = Case.query.get_or_404(case_id)
    comments = case.comments.order_by(Comment.timestamp.desc())
    form = CommentForm()
    if case:
        if form.validate_on_submit():
            comment = Comment(
                text=form.text.data,
                user_id=current_user.id,
                case_id=case.id
            )
            db.session.add(comment)
            db.session.commit()
            flash('Your Comment has been Added')
            return redirect(url_for('show_case', case_id=case.id))
        comments = case.comments.order_by(Comment.timestamp.desc())
        return render_template('show_case.html', title=case.title, case=case, form=form, comments=comments)

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

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password_form():
    """send password reset email(user)
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user) # send_password_reset_email helper fx
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_user_token(token)
    #print(user)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    cases = Case.query.filter_by(user_id = current_user.id)
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
             user_id=current_user.id
            # Add other fields as needed
        )
        # Save uploaded files to the file system
        try:
            image_files = form.image_files.data
            image_files_paths = []

            for image_file in image_files:
                if image_file:
                    filename = secure_filename(image_file.filename)
                    filepath = os.path.join(app.config['IMAGE_SUPLOAD_FOLDER'], filename)
                    relative_path = filename

                    image_file.save(filepath)
                    image_files_paths.append(relative_path)
            case.image_files =",".join(image_files_paths)

            lab_files = form.lab_files.data
            labe_files_path = []
            for lab_file in lab_files:
                if lab_file:
                    filename = secure_filename(lab_file.filename)
                    filepath = os.path.join(app.config['LABS_UPLOAD_FOLDER'], filename)
                    relative_path = filename
                    lab_file.save(filepath)
                    labe_files_path.append(relative_path)
            case.lab_files =",".join(labe_files_path)
            db.session.add(case)
            db.session.commit()
            print("case id is" , case.id)
            flash('Case submitted successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
    return render_template('submit_case.html', form=form, title="submit medical case")

@app.route('/send_email')
def send_email():
    msg = Message('Hello', recipients=['recipient@example.com'])
    msg.body = 'This is a test email from Flask-Mail'
    mail.send(msg)
    return 'Email sent!'


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


from app import routes

