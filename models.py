from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    """Admin user model"""
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    users = db.relationship('User', backref='created_by_admin', lazy=True, foreign_keys='User.admin_id')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        # prefix with type so login manager can distinguish
        return f'admin-{self.id}'

    def __repr__(self):
        return f'<Admin {self.username}>'


class User(UserMixin, db.Model):
    """Regular user model"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    attendance_records = db.relationship('Attendance', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        # prefix with type to avoid id collisions with Admin
        return f'user-{self.id}'

    def __repr__(self):
        return f'<User {self.username}>'


class Attendance(db.Model):
    """Attendance record model"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False)
    check_out_time = db.Column(db.DateTime, nullable=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='present', nullable=False)  # present, absent, late, leave
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attendance {self.user_id} - {self.date}>'


class AttendanceEvent(db.Model):
    """Individual check-in/check-out event"""
    __tablename__ = 'attendance_event'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_type = db.Column(db.String(10), nullable=False)  # 'in' or 'out'
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Event {self.user_id} {self.event_type} @ {self.timestamp}>'
