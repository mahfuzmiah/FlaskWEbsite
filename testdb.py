from app import db  # Import the SQLAlchemy instance (make sure this is correctly imported from your app)
from app.models import User  # Import the User model

# Function to print usernames and password hashes
def print_user_credentials():
    users = User.query.all()  # Query all users
    for user in users:
        print(f"Username: {user.username}, Password Hash: {user.password_hash}")

if __name__ == "__main__":
    print_user_credentials()