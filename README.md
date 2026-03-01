# Attendance Management System

A comprehensive Flask-based Attendance Management System with admin and user functionalities.

## Features

- **User Authentication**
  - User login and registration
  - Admin login with separate dashboard
  - Secure password hashing

- **User Features**
  - Check-in/Check-out functionality
  - View personal attendance history
  - Track attendance records for last 30 days

- **Admin Features**
  - Manage employees (add, view, delete)
  - View real-time attendance statistics
  - Track attendance for all employees
  - Generate attendance reports
  - Mark attendance for employees
  - Admin dashboard with overview

## Project Structure

```
src/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── login.html
│   ├── admin_login.html
│   ├── user_dashboard.html
│   ├── admin_dashboard.html
│   ├── admin_users.html
│   ├── admin_add_user.html
│   ├── admin_user_attendance.html
│   ├── admin_attendance_report.html
│   ├── 404.html
│   └── 500.html
└── static/
    ├── css/
    │   └── style.css      # Main stylesheet
    └── js/                # JavaScript files
```

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Steps

1. **Navigate to the project directory:**
```bash
cd c:\Users\sushant\flask\src
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
```

3. **Activate the virtual environment:**
   
   **On Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Initialize the database:**
```bash
python app.py
# The database will be created automatically on first run
```

## Running the Application

1. **Start the Flask server:**
```bash
python app.py
```

2. **Open your browser and navigate to:**
```
http://127.0.0.1:5000
```

## Default Test Credentials

### For creating an Admin account:
To create an admin account, you need to add one manually through Python:

```python
from app import app, db
from models import Admin

with app.app_context():
    # Create an admin user
    admin = Admin(
        username='admin',
        email='admin@example.com'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("Admin created successfully!")
```

### For creating a User account:
Use the admin panel to add users, or create manually through Python:

```python
from app import app, db
from models import User

with app.app_context():
    # Create a user
    user = User(
        username='john.doe',
        email='john@example.com',
        employee_id='EMP001',
        department='IT'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    print("User created successfully!")
```

## Usage Guide

### For Users:
1. Login with your credentials
2. Click "Check In" button to mark yourself present
3. Click "Check Out" button at the end of your shift
4. View your attendance history in the dashboard

### For Admins:
1. Login to the admin panel
2. View employee statistics on the dashboard
3. Navigate to "Manage Users" to add or remove employees
4. Click on employee name to view their attendance records
5. Generate detailed attendance reports from the "Attendance Report" section

## Technologies Used

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Security:** Werkzeug (password hashing)

## Key Routes

### Authentication Routes:
- `/login` - User login page
- `/admin-login` - Admin login page
- `/logout` - Logout functionality

### User Routes:
- `/user/dashboard` - User dashboard
- `/api/user/check-in` - API endpoint for check-in
- `/api/user/check-out` - API endpoint for check-out

### Admin Routes:
- `/admin/dashboard` - Admin dashboard
- `/admin/users` - Manage users
- `/admin/add-user` - Add new user
- `/admin/user/<id>/attendance` - View user attendance
- `/admin/attendance-report` - Generate attendance report
- `/admin/attendance/mark` - Mark attendance for user
- `/admin/user/<id>/delete` - Delete user

## Database Models

### Admin Model
- id (Primary Key)
- username
- email
- password_hash
- created_at

### User Model
- id (Primary Key)
- username
- email
- password_hash
- employee_id
- department
- admin_id (Foreign Key)
- created_at

### Attendance Model
- id (Primary Key)
- user_id (Foreign Key)
- check_in_time
- check_out_time
- date
- status (present, absent, late, leave)
- notes
- created_at

## Security Features

- Password hashing with Werkzeug
- Session-based authentication with Flask-Login
- CSRF protection (can be added with Flask-WTF)
- Role-based access control (User vs Admin)

## Troubleshooting

### Database Issues:
If you encounter database errors, delete `attendance.db` and restart the application to create a fresh database.

###Port Already in Use:
If port 5000 is already in use, you can change it in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=8000)  # Change port here
```

## Future Enhancements

- Email notifications for attendance
- Biometric authentication integration
- Attendance analytics and charts
- Leave management system
- Mobile application
- Export reports to PDF/Excel
- Multi-company support
- API documentation with Swagger
- Unit tests and integration tests

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please create an issue in the repository.
