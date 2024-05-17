from flask import Blueprint, jsonify, request, session, redirect, url_for
from .models import db, AdminData, EmpData, Leaves, ProjectList, Project, Events, TagList
from flask_mail import Message
from flask_mail import Mail
import random
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('admin.index'))
@main.route('/auth/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        admin = AdminData.query.filter_by(username=username).first()
        if admin and admin.password == password:
            session['logged_in'] = True
            session['username'] = username
            return jsonify({'loginStatus': True}), 200
        else:
            return jsonify({'loginStatus': False, 'Error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/auth/login', methods=['POST'])
def employee_login():
    try:
        data = request.json
        empid = data.get('empid')
        password = data.get('password')

        user = EmpData.query.filter_by(empid=empid).first()
        if user and user.password == password:
            session['logged_in'] = True
            session['empid'] = empid
            return jsonify({'loginStatus': True}), 200
        else:
            return jsonify({'loginStatus': False, 'Error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/auth/add_employee', methods=['POST'])
def addEmp():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    empid = data.get('employee_id')
    password = data.get('password')
    salary = data.get('salary')
    category = data.get('category_id')
    profile_image = request.files['image'].read()

    new_emp = EmpData(name=name, email=email, empid=empid, password=password, salary=salary, category=category, profile_image=profile_image)
    db.session.add(new_emp)
    db.session.commit()

    return jsonify({'message': 'Employee added successfully'}), 200

@main.route('/auth/employee', methods=['GET', 'POST'])
def get_employee_data():
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'error': 'Not logged in'}), 401

    # Get the logged-in employee's data from the database
    empid = session['empid']
    user = EmpData.query.filter_by(empid=empid).first()
    if not user:
        return jsonify({'error': 'Employee not found'}), 404

    return jsonify({
        'name': user.name,
        'email': user.email,
        'password': user.password,
        'profileImage': user.get_profile_image_base64()
    }), 200

@main.route('/auth/employees', methods=['GET', 'POST'])
def get_employees():
    employees = EmpData.query.all()
    employee_list = []
    for employee in employees:
        employee_dict = {
            'name': employee.name,
            'email': employee.email,
            'employee_id': employee.empid,
            'salary': employee.salary,
            'category': employee.category
        }
        employee_list.mainend(employee_dict)
        db.session.commit()
    return jsonify({'Status': True, 'Result': employee_list}), 200

@main.route('/auth/update_employee', methods=['POST'])
def update_employee():
    data = request.json
    empid = session.get('empid')
    if not empid:
        return jsonify({'error': 'Employee not logged in'}), 401

    user = EmpData.query.filter_by(empid=empid).first()
    if not user:
        return jsonify({'error': 'Employee not found'}), 404

    # Update email if provided
    new_email = data.get('email')
    if new_email:
        user.email = new_email
        print('Email Updated Successfully')

    # Update password if provided
    new_password = data.get('password')
    if new_password:
        user.password = new_password
        print('Password Updated Successfully')

    db.session.commit()
    return jsonify({'message': 'Employee updated successfully'}), 200

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/auth/upload_profile', methods=['POST'])
def upload_profile_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Convert the file data to bytes
        file_data = file.read()

        # Save the file data to the database
        user = EmpData.query.filter_by(empid=session['empid']).first()
        user.profile_image = file_data
        db.session.commit()

        return jsonify({'message': 'Profile image uploaded successfully'}), 200

    return jsonify({'error': 'File format not allowed'}), 400

@main.route('/auth/leave', methods=['GET', 'POST'])
def add_leave():
    data = request.json
    name = data.get('name')
    empid = data.get('employeeId')
    reason = data.get('reason')
    numberOfDays = data.get('numberOfDays')

    fromDate = datetime.strptime(data.get('fromDate'), '%Y-%m-%d')
    toDate = datetime.strptime(data.get('toDate'), '%Y-%m-%d')

    # Create a new Leave instance and add it to the database
    new_leave = Leaves(name=name, empid=empid, reason=reason, numberOfDays=numberOfDays, fromDate=fromDate, toDate=toDate)
    db.session.add(new_leave)
    db.session.commit()

    return jsonify({'message': 'Leave added successfully'}), 200

@main.route('/auth/add_projects', methods=['GET', 'POST'])
def add_project():
    data = request.json
    project_name = data.get('name')

    # Check if the project already exists
    existing_project = ProjectList.query.filter_by(name=project_name).first()
    if existing_project:
        return jsonify({'error': 'Project already exists'}), 400

    # If the project doesn't exist, add it to the database
    new_project = ProjectList(name=project_name)
    db.session.add(new_project)
    db.session.commit()

    return jsonify({'message': 'Project added successfully'}), 201

# Route to add an event
@main.route('/auth/add_event', methods=['POST'])
def add_event():
    try:
        data = request.json
        title = data.get('title')
        start = datetime.fromisoformat(data.get('start'))
        end = datetime.fromisoformat(data.get('end'))
        all_day = data.get('allDay')
        print(title, start, end, all_day)
        new_event = Events(title=title, start=start, end=end, all_day=all_day)
        db.session.add(new_event)
        db.session.commit()

        return jsonify({'message': 'Event added successfully', 'id': new_event.id}), 200
    except Exception as e:
        print(f"Error adding event: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/auth/update_event/<int:event_id>', methods=['POST'])
def update_event(event_id):
    data = request.json
    title = data.get('title')
    start = datetime.fromisoformat(data.get('start'))
    end = datetime.fromisoformat(data.get('end'))

    event = Events.query.get(event_id)
    if event:
        event.title = title
        event.start = start
        event.end = end
        db.session.commit()
        return jsonify({'message': 'Event updated successfully'}), 200
    else:
        return jsonify({'error': 'Event not found'}), 404

@main.route('/auth/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Events.query.get(event_id)
    if event:
        event.delete_event()
        return jsonify({'message': 'Event deleted successfully'}), 200
    else:
        return jsonify({'error': 'Event not found'}), 404

# Route to fetch all events
@main.route('/auth/get_events', methods=['GET'])
def get_events():
    events = Events.query.all()
    events_data = [event.to_dict() for event in events]
    return jsonify(events_data), 200

'''
@main.route('/auth/add_project_data', methods=['POST'])
def add_project_data():
    task = request.json.get('task')
    projectName = request.json.get('projectName')
    tags = request.json.get('tags')
    timeElapsed = request.json.get('timeElapsed')
    
    # Create a new Project instance and add it to the database
    new_project = Project(task=task, projectName=projectName, tags=tags, timeElapsed=timeElapsed)
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({'message': 'Project data added successfully!'}), 201
'''
@main.route('/auth/add_project_data', methods=['POST'])
def add_project_data():
    data = request.json
    projectName = data.get('projectName')
    task = data.get('task')  # Updated to 'description'
    tags = ','.join(data.get('tags'))  # Convert list of tags to comma-separated string
    timeElapsed = data.get('timeElapsed')
    
    # Create a new Project instance and add it to the database
    new_project = Project(projectName=projectName, task=task, tags=tags, timeElapsed=timeElapsed)
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({'message': 'Project data added successfully!'}), 201

@main.route('/auth/projects', methods=['GET', 'POST'])  # Allow both GET and POST requests
def handle_projects():
    if request.method == 'GET':
        projects = Project.query.all()
        projects_data = [project.to_dict() for project in projects]
        return jsonify(projects_data), 200
    elif request.method == 'POST':
        data = request.json
        if not data.get('projectName').strip():
            return jsonify({'error': 'Project name is required!'}), 400

        new_project = Project(projectName=data.get('projectName'), tag=data.get('tag'), timeElapsed=data.get('timeElapsed'))
        db.session.add(new_project)
        db.session.commit()

        return jsonify({'message': 'Project added successfully!'}), 201

@main.route('/auth/project_list', methods=['GET'])
def get_project_list():
    # Query the database to fetch all project names
    projects = ProjectList.query.all()
    # Extract project names and return as JSON response
    project_names = [project.name for project in projects]
    return jsonify(project_names)

@main.route('/auth/tag_list', methods=['GET'])
def get_tag_list():
    tags = TagList.query.all()
    tags_list = [{'id': tag.id, 'tag': tag.tag} for tag in tags]
    return jsonify({'tags': tags_list})

@main.route('/auth/add_tag', methods=['POST'])
def add_tag():
    data = request.json
    tag_name = data.get('tag')

    # Check if the tag already exists
    existing_tag = TagList.query.filter_by(tag=tag_name).first()
    if existing_tag:
        return jsonify({'error': 'Tag already exists'}), 400

    # If the tag doesn't exist, add it to the database
    new_tag = TagList(tag=tag_name)
    db.session.add(new_tag)
    db.session.commit()

    return jsonify({'message': 'Tag added successfully'}), 201
@main.route('/auth/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    user = EmpData.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    otp = random.randint(100000, 999999)  # Generate OTP
    session['otp'] = otp
    session['email'] = email

    # Here you would normally send the OTP to the user's email or phone number
    # Send OTP via email
    msg = Message('Password Reset OTP', sender='rushi', recipients=[email])
    msg.body = f'Your OTP for password reset is: {otp}'
    mail.send(msg)

    # For simplicity, we'll just return the OTP in the response
    return jsonify({'message': 'OTP sent successfully', 'otp': otp}), 200


@main.route('/auth/resetpassword', methods=['GET', 'POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('password')

    session['otp'] = otp
    session['email'] = email
    # Verify the OTP
    session_otp = session.get('otp')
    session_email = session.get('email')

    if (not session_email) or (not session_otp) or (session_email != email) or (int(session_otp) != int(otp)):
        return jsonify({'error': 'Invalid or expired OTP'}), 401

    # Find the user by email
    user = EmpData.query.filter_by(email=email).first()
    if not user:
        print('User not found')
        return jsonify({'error': 'User not found'}), 404

    # Update the user's password
    user.password = new_password
    db.session.commit()
    return jsonify({'message': 'Password reset successful'}), 200


