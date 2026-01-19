from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # tasks_created relationship is removed in favor of backrefs in Task model:
    # tasks_authored and tasks_assigned

    def __repr__(self):
        return f'<User {self.email}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # We already have 'author' backref from User.tasks_created
    # Let's add explicit relationships if needed, or rely on backrefs if defined in User
    # But User definition only has tasks_created.
    # Let's add a relationship here for assignee if we want to access it easily
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='tasks_assigned', lazy=True)
    author_user = db.relationship('User', foreign_keys=[created_by], backref='tasks_authored', lazy=True)


    def __repr__(self):
        return f'<Task {self.title}>'
