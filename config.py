import os
basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = 'd4f8d98d27a34c018b0e7e3629fefe60'

SQLALCHEMY_TRACK_MODIFICATIONS = True  

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
# Set to False to disable modification tracking and save resources

# CSRF protection for Flask-WTF forms
WTF_CSRF_ENABLED = True