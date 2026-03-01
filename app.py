from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
from config import Config
from models import db, Admin, User, Attendance, AttendanceEvent
import json
import io
import csv
from flask import Response

app = Flask(__name__)
app.config.from_object(Config)

# Ensure uploads directory exists on startup
upload_dir = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(upload_dir, exist_ok=True)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    """Retrieve user or admin based on prefixed ID (user-<id> or admin-<id>)"""
    if not user_id:
        return None
    if isinstance(user_id, bytes):
        user_id = user_id.decode('utf-8')
    if user_id.startswith('admin-'):
        try:
            uid = int(user_id.split('-', 1)[1])
        except ValueError:
            return None
        return Admin.query.get(uid)
    elif user_id.startswith('user-'):
        try:
            uid = int(user_id.split('-', 1)[1])
        except ValueError:
            return None
        return User.query.get(uid)
    return None

@login_manager.unauthorized_handler
def unauthorized_callback():
    """Return JSON for API requests, otherwise redirect to login."""
    if request.path.startswith('/api/') or request.path.startswith('/admin/'):
        return jsonify({'error': 'Unauthorized'}), 401
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

# ===================== AUTHENTICATION ROUTES =====================

@app.route('/')
def index():
    """Home page - redirect based on login status"""
    if current_user.is_authenticated:
        # admin users have attribute 'email' and are instance of Admin after loader fix
        if hasattr(current_user, 'email') and isinstance(current_user, Admin):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('user_dashboard'))
        
        return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('admin_login.html', error='Username and password are required')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin, remember=True)
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_login.html', error='Invalid username or password')
    
    return render_template('admin_login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('login'))

# ===================== USER ROUTES =====================

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """User dashboard"""
    if not isinstance(current_user, User):
        return redirect(url_for('index'))
    
    today = date.today()
    attendance_today = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    # Get attendance history (last 30 days) and events
    thirty_days_ago = today - timedelta(days=30)
    attendance_records = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= thirty_days_ago
    ).order_by(Attendance.date.desc()).all()
    events = AttendanceEvent.query.filter(
        AttendanceEvent.user_id == current_user.id,
        AttendanceEvent.timestamp >= datetime.combine(thirty_days_ago, datetime.min.time())
    ).order_by(AttendanceEvent.timestamp.desc()).all()
    
    return render_template('user_dashboard.html', 
                         attendance_today=attendance_today,
                         attendance_records=attendance_records,
                         events=events)

@app.route('/api/user/check-in', methods=['POST'])
@login_required
def check_in():
    """User check-in event"""
    if not isinstance(current_user, User):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # always create an event regardless of previous
    event = AttendanceEvent(
        user_id=current_user.id,
        timestamp=datetime.now(),
        event_type='in'
    )
    db.session.add(event)
    db.session.commit()
    
    # optionally update today's summary record
    today = date.today()
    attendance = Attendance.query.filter_by(user_id=current_user.id, date=today).first()
    if not attendance:
        attendance = Attendance(
            user_id=current_user.id,
            check_in_time=event.timestamp,
            date=today,
            status='present'
        )
        db.session.add(attendance)
    else:
        # update check_in_time to earliest
        if not attendance.check_in_time or event.timestamp < attendance.check_in_time:
            attendance.check_in_time = event.timestamp
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Check-in recorded',
        'time': event.timestamp.strftime('%H:%M:%S')
    })

@app.route('/api/user/check-out', methods=['POST'])
@login_required
def check_out():
    """User check-out event"""
    if not isinstance(current_user, User):
        return jsonify({'error': 'Unauthorized'}), 401
    
    event = AttendanceEvent(
        user_id=current_user.id,
        timestamp=datetime.now(),
        event_type='out'
    )
    db.session.add(event)
    db.session.commit()
    
    # update daily summary
    today = date.today()
    attendance = Attendance.query.filter_by(user_id=current_user.id, date=today).first()
    if not attendance:
        attendance = Attendance(
            user_id=current_user.id,
            check_out_time=event.timestamp,
            date=today,
            status='present'
        )
        db.session.add(attendance)
    else:
        if not attendance.check_out_time or event.timestamp > attendance.check_out_time:
            attendance.check_out_time = event.timestamp
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Check-out recorded',
        'time': event.timestamp.strftime('%H:%M:%S')
    })

# ===================== ADMIN ROUTES =====================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))
    
    today = date.today()
    total_users = User.query.count()
    present_today = Attendance.query.filter(
        Attendance.date == today,
        Attendance.status == 'present'
    ).count()
    absent_today = total_users - present_today
    
    recent_attendance = Attendance.query.order_by(Attendance.created_at.desc()).limit(20).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         present_today=present_today,
                         absent_today=absent_today,
                         recent_attendance=recent_attendance)

@app.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    """List all users"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/<int:user_id>/attendance', methods=['GET'])
@login_required
def admin_user_attendance(user_id):
    """View user's attendance"""
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get attendance for last 90 days
    ninety_days_ago = date.today() - timedelta(days=90)
    records = Attendance.query.filter(
        Attendance.user_id == user_id,
        Attendance.date >= ninety_days_ago
    ).order_by(Attendance.date.desc()).all()
    
    return render_template('admin_user_attendance.html', user=user, records=records)

@app.route('/admin/attendance-report', methods=['GET'])
@login_required
def admin_attendance_report():
    """Attendance report"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))
    
    users = User.query.all()
    today = date.today()
    
    report_data = []
    for user in users:
        present = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.status == 'present'
        ).count()
        
        absent = Attendance.query.filter(
            Attendance.user_id == user.id,
            Attendance.status == 'absent'
        ).count()
        
        report_data.append({
            'user': user,
            'present': present,
            'absent': absent
        })
    
    return render_template('admin_attendance_report.html', report_data=report_data)

@app.route('/admin/add-user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    """Add new user"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        employee_id = data.get('employee_id')
        department = data.get('department')
        
        if not all([username, email, password, employee_id, department]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        if User.query.filter_by(employee_id=employee_id).first():
            return jsonify({'error': 'Employee ID already exists'}), 400
        
        user = User(
            username=username,
            email=email,
            employee_id=employee_id,
            department=department,
            admin_id=current_user.id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'User added successfully'})
        else:
            return redirect(url_for('admin_users'))
    
    return render_template('admin_add_user.html')


@app.route('/admin/add-admin', methods=['GET', 'POST'])
@login_required
def admin_add_admin():
    """Create another admin account"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([username, email, password]):
            return render_template('admin_add_admin.html', error='All fields are required')
        
        if Admin.query.filter_by(username=username).first():
            return render_template('admin_add_admin.html', error='Username already exists')
        
        if Admin.query.filter_by(email=email).first():
            return render_template('admin_add_admin.html', error='Email already exists')
        
        new_admin = Admin(username=username, email=email)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_add_admin.html')


@app.route('/admin/export-users')
@login_required
def admin_export_users():
    """Export user list as CSV"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))
    
    users = User.query.all()
    
    def generate():
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow(['Username','Email','Employee ID','Department','Joined'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        for u in users:
            writer.writerow([
                u.username,
                u.email,
                u.employee_id,
                u.department,
                u.created_at.strftime('%Y-%m-%d')
            ])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
    
    return Response(generate(), mimetype='text/csv',
                    headers={
                        'Content-Disposition':'attachment;filename=users.csv'
                    })


@app.route('/admin/export-attendance')
@login_required
def admin_export_attendance():
    """Export attendance report as CSV"""
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))
    
    records = Attendance.query.order_by(Attendance.date.asc()).all()
    
    def generate():
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow(['Username','Employee ID','Date','Check-In','Check-Out','Status','Notes'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        for r in records:
            writer.writerow([
                r.user.username,
                r.user.employee_id,
                r.date.strftime('%Y-%m-%d'),
                r.check_in_time.strftime('%H:%M:%S') if r.check_in_time else '',
                r.check_out_time.strftime('%H:%M:%S') if r.check_out_time else '',
                r.status,
                r.notes or ''
            ])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
    
    return Response(generate(), mimetype='text/csv',
                    headers={
                        'Content-Disposition':'attachment;filename=attendance.csv'
                    })

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Delete user"""
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@app.route('/admin/attendance/mark', methods=['POST'])
@login_required
def admin_mark_attendance():
    """Mark attendance for user"""
    if not isinstance(current_user, Admin):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_id = data.get('user_id')
    status = data.get('status')
    date_str = data.get('date')
    
    if not all([user_id, status, date_str]):
        return jsonify({'error': 'Missing fields'}), 400
    
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    attendance = Attendance.query.filter_by(
        user_id=user_id,
        date=attendance_date
    ).first()
    
    if not attendance:
        attendance = Attendance(
            user_id=user_id,
            date=attendance_date,
            check_in_time=datetime.now(),
            status=status
        )
        db.session.add(attendance)
    else:
        attendance.status = status
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Attendance marked successfully'})

# ===================== ERROR HANDLERS =====================

@app.route('/user/upload-photo', methods=['POST'])
@login_required
def upload_photo():
    """Allow user to upload or capture a photo"""
    if not isinstance(current_user, User):
        return jsonify({'error': 'Unauthorized'}), 401
    file = request.files.get('photo')
    if not file or file.filename == '':
        flash('No photo selected for upload')
        return redirect(url_for('user_dashboard'))

    # simple extension whitelist
    allowed_ext = {'png', 'jpg', 'jpeg', 'gif'}
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_ext:
        flash('Unsupported file type. Please upload an image.')
        return redirect(url_for('user_dashboard'))

    # ensure uploads folder exists (created at startup as well)
    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    unique_name = f'user_{current_user.id}_{int(datetime.utcnow().timestamp())}.{ext}'
    path = os.path.join(upload_dir, unique_name)
    try:
        file.save(path)
    except Exception as e:
        flash('Failed to save photo: ' + str(e))
        return redirect(url_for('user_dashboard'))

    current_user.photo = f'uploads/{unique_name}'
    db.session.commit()
    flash('Photo uploaded successfully')
    return redirect(url_for('user_dashboard'))

def safe_float(val: str | None, default: float = 0.0) -> float:
    """Convert a string to float, returning ``default`` on failure.

    ``val`` can be ``None`` or an empty string; the function will not raise
    exceptions.
    """
    try:
        if val is None or val == '':
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


@app.route('/admin/payroll', methods=['GET', 'POST'])
@login_required
def admin_payroll():
    """Generate simple payroll based on attendance events

    Supports filtering by month and optionally a single user.  On POST the
    form may supply a separate rate for each user (name pattern ``rate_<id>``)
    which will be used when computing that user's payment. A global ``rate``
    parameter still exists as a fallback.
    """
    if not isinstance(current_user, Admin):
        return redirect(url_for('index'))

    # determine period and selected user id from either query string or form
    if request.method == 'POST':
        period = request.form.get('month') or date.today().strftime('%Y-%m')
        # form returns empty string if not chosen
        selected_uid = request.form.get('user_id')
        try:
            selected_uid = int(selected_uid) if selected_uid else None
        except (ValueError, TypeError):
            selected_uid = None
    else:
        period = request.args.get('month') or date.today().strftime('%Y-%m')
        selected_uid_raw = request.args.get('user_id')
        try:
            selected_uid = int(selected_uid_raw) if selected_uid_raw else None
        except (ValueError, TypeError):
            selected_uid = None

    # validate period format
    try:
        year, mon = map(int, period.split('-'))
        if mon < 1 or mon > 12:
            period = date.today().strftime('%Y-%m')
            year, mon = map(int, period.split('-'))
    except (ValueError, IndexError):
        period = date.today().strftime('%Y-%m')
        year, mon = map(int, period.split('-'))
    start_date = date(year, mon, 1)
    if mon == 12:
        end_date = date(year+1, 1, 1)
    else:
        end_date = date(year, mon+1, 1)

    # build base user list for computation and for dropdown
    if selected_uid:
        user_obj = User.query.get(selected_uid)
        users = [user_obj] if user_obj else []
    else:
        users = User.query.all()

    # global fallback rate
    if request.method == 'POST':
        base_rate = safe_float(request.form.get('rate'))
    else:
        base_rate = safe_float(request.args.get('rate'))

    payroll_data = []
    for u in users:
        # compute attendance hours primarily from events
        events = AttendanceEvent.query.filter(
            AttendanceEvent.user_id == u.id,
            AttendanceEvent.timestamp >= datetime.combine(start_date, datetime.min.time()),
            AttendanceEvent.timestamp < datetime.combine(end_date, datetime.min.time())
        ).order_by(AttendanceEvent.timestamp.asc()).all()
        total_seconds = 0
        if events:
            last_in = None
            for e in events:
                if e.event_type == 'in':
                    if last_in is None:
                        last_in = e.timestamp
                elif e.event_type == 'out' and last_in is not None:
                    total_seconds += (e.timestamp - last_in).total_seconds()
                    last_in = None
        else:
            # no event data; fall back to summary attendance records (e.g., seeded by init_db)
            records = Attendance.query.filter(
                Attendance.user_id == u.id,
                Attendance.date >= start_date,
                Attendance.date < end_date
            ).all()
            for r in records:
                if r.check_in_time and r.check_out_time:
                    total_seconds += (r.check_out_time - r.check_in_time).total_seconds()
        hours = total_seconds / 3600
        full_days = int(hours // 8)
        half_days = int((hours % 8) // 4)

        # per-user rate override (POST form takes precedence but GET args are also respected)
        rate_for_user = base_rate
        key = f'rate_{u.id}'
        if request.method == 'POST' and key in request.form:
            rate_for_user = safe_float(request.form.get(key), rate_for_user)
        elif request.method == 'GET' and request.args.get(key) is not None:
            rate_for_user = safe_float(request.args.get(key), rate_for_user)

        payroll_data.append({
            'user': u,
            'hours': hours,
            'full_days': full_days,
            'half_days': half_days,
            'rate': rate_for_user,
            'payment': hours * rate_for_user
        })

    return render_template(
        'admin_payroll.html',
        payroll_data=payroll_data,
        period=period,
        rate=base_rate,
        users=User.query.all(),
        selected_uid=selected_uid
    )

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # bind to all interfaces so other devices can access using IP
    app.run(debug=True, host='0.0.0.0')
