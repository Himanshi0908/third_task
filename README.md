# Sec Task

A Flask-based REST API for secure task management with user authentication, role-based access control, and admin features.

## Features

- User registration and authentication using JWT tokens
- Role-based access control (user and admin roles)
- Task creation, assignment, updating, and deletion
- Admin panel for managing users and tasks
- Rate limiting to prevent abuse
- CORS support for cross-origin requests
- Verification scripts for automated testing of API endpoints

## Requirements

- Python 3.8 or higher
- pip for package management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Himanshi0908/third_task.git
   cd sec_task
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by creating a `.env` file in the root directory:
   ```
   SECRET_KEY=your_secret_key_here
   JWT_SECRET_KEY=your_jwt_secret_here
   SQLALCHEMY_DATABASE_URI=sqlite:///task_manager.db
   ```

## Running the Application

1. Run the application:
   ```
   python run.py
   ```

2. The API will start on `http://127.0.0.1:5000` with debug mode enabled.

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/logout` - Logout (invalidate token)

### Tasks
- `GET /api/v1/tasks` - Get user's tasks
- `POST /api/v1/tasks` - Create a new task
- `PUT /api/v1/tasks/<id>` - Update a task
- `DELETE /api/v1/tasks/<id>` - Delete a task

### Admin
- `GET /api/v1/admin/users` - Get all users (admin only)
- `DELETE /api/v1/admin/users/<id>` - Delete a user (admin only)

## Testing

The project includes verification scripts to test the API functionality:

- `verify_tasks.py` - Tests task creation, assignment, and management
- `verify_admin.py` - Tests admin user management
- `verify_api.py` - General API verification
- `verify_logout.py` - Tests logout functionality

Run a verification script with:
```
python verify_tasks.py
```

Ensure the Flask app is running before executing the scripts.

## Project Structure

```
sec_task/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   ├── middleware.py
│   └── routes/
│       ├── auth.py
│       ├── tasks.py
│       ├── admin.py
│       └── errors.py
├── instance/
├── config.py
├── run.py
├── create_admin.py
├── requirements.txt
├── verify_*.py
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run verification scripts
5. Submit a pull request

## License

This project is licensed under the MIT License.
