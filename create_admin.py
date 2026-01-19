from app import create_app, db
from app.models import User
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt(app)

def create_admin(email, password, name="Admin"):
    with app.app_context():
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User {email} already exists. Updating role to 'admin'.")
            user.role = 'admin'
            user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            print("User updated successfully.")
            return

        # Create new admin
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            role='admin'
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"Admin user {email} created successfully.")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password> [name]")
    else:
        email = sys.argv[1]
        password = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else "Admin"
        create_admin(email, password, name)
