
from flask_mail import Message
from flask import render_template
from app import mail, app

def send_password_reset_email(user):
    """
    Sends a password reset email to the specified user.

    Parameters:
    - user: The user object for whom the password reset email is being sent.

    Returns:
    - None
    """
    token = user.generate_token()  # Assuming you have this method in your User model
    msg = Message('[MediConsult] Reset Your Password',
                  sender=app.config['ADMIN'][0],
                  recipients=[user.email])  # Assuming user.email stores the email address
    msg.body = render_template('email/reset_password.txt',
                               user=user, token=token)
    msg.html = render_template('email/reset_password.html',
                               user=user, token=token)
    mail.send(msg)
