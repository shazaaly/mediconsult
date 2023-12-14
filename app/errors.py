
from flask import render_template
from app import app, db

# Define an error handler for 404 errors
@app.errorhandler(404)
def not_found_error(error):
    # Render the '404.html' template and return it with a 404 status code
    return render_template('404.html'), 404

# Define an error handler for 500 errors
@app.errorhandler(500)
def internal_server_error(error):
    # Rollback the database session
    db.session.rollback()
    # Render the '500.html' template and return it with a 500 status code
    return render_template('500.html'), 500
