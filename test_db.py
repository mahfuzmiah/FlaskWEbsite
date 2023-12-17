

from app import db
from app.models import User

def test_db():
    try:
        # Attempt to query the User table
        users = User.query.all()
        print("Database connection successful.")
        print("Users in database:")
        for user in users:
            print(user.username)
    except Exception as e:
        print("Error accessing database:", e)

if __name__ == "__main__":
    test_db()
