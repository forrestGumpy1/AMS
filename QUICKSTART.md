# Quick Start Guide

## Getting Started with Attendance Management System

### Step 1: Install Dependencies

Open a terminal/command prompt in the `src` directory and run:

```bash
# On Windows
pip install -r requirements.txt

# On macOS/Linux
pip3 install -r requirements.txt
```

### Step 2: Initialize the Database with Sample Data

```bash
python init_db.py
```

This will create:
- 2 admin accounts
- 10 sample user accounts
- 60 days of attendance records

### Step 3: Run the Application

```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 4: Open in Browser

Navigate to: `http://127.0.0.1:5000`

---

## Test Accounts

### Admin Accounts:
| Username | Password |
|----------|----------|
| admin1 | admin123 |
| admin2 | admin123 |

### User Accounts:
| Username | Password |
|----------|----------|
| john.doe | password123 |
| jane.smith | password123 |
| bob.wilson | password123 |
| alice.johnson | password123 |
| charlie.brown | password123 |
| diana.prince | password123 |
| evan.davis | password123 |
| fiona.green | password123 |
| george.martin | password123 |
| hannah.lee | password123 |

---

## First Time Setup

1. **Login as Admin:**
   - Use admin1/admin123
   - Access the Admin Dashboard

2. **Add New Users:**
   - Click "Add New User"
   - Fill in the form with employee details
   - Users can then login with their credentials

3. **As a User:**
   - Login with your credentials
   - Click "Check In" when arriving
   - Click "Check Out" when leaving
   - View your attendance history

4. **As an Admin:**
   - Monitor attendance in real-time
   - Manage employee accounts
   - Generate attendance reports
   - View detailed attendance history for each employee

---

## Troubleshooting

### Port 5000 is already in use?
Edit `app.py` and change the port:
```python
if __name__ == '__main__':
    app.run(debug=True, port=8000)  # Change to 8000 or another free port
```

### Import errors?
Make sure virtual environment is activated and all packages installed:
```bash
pip install -r requirements.txt --force-reinstall
```

### Database corrupted?
Delete `attendance.db` and restart the application:
```bash
rm attendance.db  # On macOS/Linux
del attendance.db  # On Windows
python app.py
```

---

## File Structure

```
src/
├── app.py                 # Main application
├── config.py              # Configuration
├── models.py              # Database models
├── init_db.py             # Sample data initialization
├── requirements.txt       # Dependencies
├── README.md              # Full documentation
├── QUICKSTART.md          # This file
├── attendance.db          # Database (created on first run)
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
    └── css/
        └── style.css      # Stylesheet
```

---

## Features Overview

### User Features:
✓ Login/Logout
✓ Check-in/Check-out
✓ View personal attendance
✓ 30-day attendance history
✓ Responsive dashboard

### Admin Features:
✓ Admin login/logout
✓ Dashboard with statistics
✓ Add/delete employees
✓ View all attendance records
✓ Generate attendance reports
✓ Filter and search employees
✓ Mark attendance manually
✓ View employee attendance details

---

## Next Steps

1. Customize the styling in `static/css/style.css`
2. Add more departments
3. Implement email notifications
4. Add export to PDF/Excel
5. Deploy to a web server
6. Add biometric integration
7. Create mobile app

---

For detailed documentation, see `README.md`.
