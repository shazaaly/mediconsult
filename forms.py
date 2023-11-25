from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me  = BooleanField('Remember Me')
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user=User.query.filter_by(username=username.data).first()
        if user is not None:
             raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')



class EditProfileForm(FlaskForm):
    """
    A form for editing user profile information.

    Attributes:
        username (StringField): The username field.
        bio (TextAreaField): The bio field.
        medical_degree (StringField): The medical degree field.
        speciality (StringField): The speciality field.
        licenses (StringField): The licenses field.
        submit (SubmitField): The submit button.

    Methods:
        __init__(self, original_username): Initializes the EditProfileForm object.
        validate_username(self, username): Validates the username field.

    """

    username = StringField('Username', validators=[DataRequired()])
    bio = TextAreaField('bio')
    medical_degree = StringField('medical_degree')
    speciality = StringField('speciality')
    licenses = StringField('licenses')
    submit = SubmitField('Submit')

    def __init__(self, original_username,*args, **kwargs):
        """
        Initialize the EditProfileForm object.

        Args:
            original_username (str): The original username.

        Returns:
            None
        """
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """
        Validate the username field.

        Args:
            username (str): The username to be validated.

        Raises:
            ValidationError: If the username is already taken.

        Returns:
            None
        """
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class CaseForm(FlaskForm):
    """ form to add and submit a new case"""
    title = StringField('Title', validators=[DataRequired()])
    patient_age = StringField('Patient Age', validators=[DataRequired()])
    patient_sex = StringField('Patient Sex', validators=[DataRequired()])
    chief_complaint = TextAreaField('Chief Complaint', validators=[DataRequired()])
    medical_history = StringField('Medical History', validators=[DataRequired()])
    current_medications = StringField('Current Medications', validators=[DataRequired()])
    # Use MultipleFileField for multiple image files
    image_files = MultipleFileField('Upload Image Files')
    lab_files = MultipleFileField('Upload Lab Files')
    submit = SubmitField('Submit')



