from app import create_app, db
from app.models import User, Task

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Simple way to create tables for SQLite
    app.run(debug=True)
