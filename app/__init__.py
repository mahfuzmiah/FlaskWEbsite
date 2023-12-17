from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_login import LoginManager
import logging

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
from .models import User

admin = Admin(app, template_mode='bootstrap4')
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define user loader function
@login_manager.user_loader
def load_user(user_id):
    try:
        # print("user ID", User.query.get(int(user_id)))
        # print("user ID",int(user_id))
        user = User.query.get(int(user_id))
        return user    
    except:
        return None


logging.basicConfig(level=logging.DEBUG)
# Import routes
from app import views, models