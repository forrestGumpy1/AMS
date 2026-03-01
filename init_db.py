"""
Database initialization script
Run this to create sample data for testing
"""

from app import app, db
from models import Admin, User, Attendance
from datetime import datetime, timedelta, date
import random

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create admin users
        print("Creating admin users...")
        admins = [
            {
                'username': 'admin1',
                'email': 'admin1@example.com',
                'password': 'admin123'
            },
            {
                'username': 'admin2',
                'email': 'admin2@example.com',
                'password': 'admin123'
            }
        ]
        
        admin_objects = []
        for admin_data in admins:
            admin = Admin(
                username=admin_data['username'],
                email=admin_data['email']
            )
            admin.set_password(admin_data['password'])
            db.session.add(admin)
            admin_objects.append(admin)
        
        db.session.commit()
        print(f"✓ Created {len(admins)} admin users")
        
        # Create user accounts
        print("Creating user accounts...")
        departments = ['IT', 'HR', 'Sales', 'Marketing', 'Finance', 'Operations']
        
        users_data = [
            ('john.doe', 'john@example.com', 'EMP001', 'IT'),
            ('jane.smith', 'jane@example.com', 'EMP002', 'HR'),
            ('bob.wilson', 'bob@example.com', 'EMP003', 'Sales'),
            ('alice.johnson', 'alice@example.com', 'EMP004', 'Marketing'),
            ('charlie.brown', 'charlie@example.com', 'EMP005', 'Finance'),
            ('diana.prince', 'diana@example.com', 'EMP006', 'Operations'),
            ('evan.davis', 'evan@example.com', 'EMP007', 'IT'),
            ('fiona.green', 'fiona@example.com', 'EMP008', 'Sales'),
            ('george.martin', 'george@example.com', 'EMP009', 'IT'),
            ('hannah.lee', 'hannah@example.com', 'EMP010', 'HR'),
        ]
        
        users = []
        for username, email, emp_id, dept in users_data:
            user = User(
                username=username,
                email=email,
                employee_id=emp_id,
                department=dept,
                admin_id=admin_objects[0].id
            )
            user.set_password('password123')
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print(f"✓ Created {len(users)} user accounts")
        
        # Create sample attendance records
        print("Creating attendance records...")
        attendance_count = 0
        
        today = date.today()
        for user in users:
            # Create records for last 60 days
            for days_back in range(60):
                record_date = today - timedelta(days=days_back)
                
                # Skip weekends (Saturday=5, Sunday=6)
                if record_date.weekday() >= 5:
                    continue
                
                # 80% chance of being present
                if random.random() < 0.8:
                    check_in_hour = random.randint(8, 9)
                    check_in_minute = random.randint(0, 59)
                    check_in_time = datetime.combine(
                        record_date,
                        datetime.min.time().replace(hour=check_in_hour, minute=check_in_minute)
                    )
                    
                    check_out_hour = random.randint(17, 18)
                    check_out_minute = random.randint(0, 59)
                    check_out_time = datetime.combine(
                        record_date,
                        datetime.min.time().replace(hour=check_out_hour, minute=check_out_minute)
                    )
                    
                    status = 'late' if check_in_hour > 9 else 'present'
                    
                    attendance = Attendance(
                        user_id=user.id,
                        check_in_time=check_in_time,
                        check_out_time=check_out_time,
                        date=record_date,
                        status=status,
                        notes=None
                    )
                    db.session.add(attendance)
                    attendance_count += 1
                else:
                    # Absent
                    attendance = Attendance(
                        user_id=user.id,
                        check_in_time=datetime.combine(record_date, datetime.min.time()),
                        date=record_date,
                        status='absent',
                        notes='Absent'
                    )
                    db.session.add(attendance)
                    attendance_count += 1
        
        db.session.commit()
        print(f"✓ Created {attendance_count} attendance records")
        
        print("\n" + "="*50)
        print("✓ Database initialized successfully!")
        print("="*50)
        print("\nTest Credentials:")
        print("-" * 50)
        print("ADMIN LOGIN:")
        for admin in admins:
            print(f"  Username: {admin['username']}")
            print(f"  Password: {admin['password']}")
            print()
        
        print("USER LOGIN (example):")
        print(f"  Username: john.doe")
        print(f"  Password: password123")
        print("-" * 50)

if __name__ == '__main__':
    init_database()
