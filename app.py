from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import json
import mysql.connector
import os
import datetime
from datetime import date
from flask_cors import CORS
import modal
import random
import string
from multiprocessing import Pool
from mysql.connector.pooling import MySQLConnectionPool
import mail
import util
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'C:\\Users\\Perry\\PycharmProjects\\leave\\static\\image'

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)
app.secret_key = 'the generator people'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])




@app.route('/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        connection = app.config['pool'].get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM login_info WHERE staff_id ='%s'"% username)

        # Fetch one record and return result
        account = cursor.fetchone()
        valid_password = False
        if account:
            valid_password = bcrypt.check_password_hash(account[2], password)

        cursor.close()
        connection.close()
        # If account exists in accounts table in out database
        if valid_password:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # Redirect to home page
            print('Logged in successfully!')
            return redirect('/dashboard')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    username = session['username']
    print('username is',username)

    holiday = modal.get_holidays()
    print("all hoildays", holiday)

    data = modal.find_all(username)
    print('data needed is', data)

    line_manager_id = data['id']
    print(line_manager_id)

    leave_data = modal.approved_pending_info(username, data['role'])
    leave_types = modal.get_leave_types(data['gender'], data['role'])
    print('leave types: ', leave_types)

    print('this is it', leave_data)

    # days_left = modal.carried_froward_days(username)
    # print(days_left)
    history = modal.leave_history(username)
    for i in leave_types:
        found = False
        for j in leave_data:
            if i['leave_id'] == j['leave_id']:
                found = True
                break
        if not found:
            leave_data.append({'total': 0, 'Staff_id': username, 'leave_id': i['leave_id'], 'duration': i['duration'], 'name': i['name']})
    print('leave data is now : ', leave_data)

    print(history)

    pending =modal.pending(line_manager_id)
    approved = []

    if data['role'] == 2:
        approved = modal.line_manager_approved(line_manager_id)
    elif data['role'] ==3:
        approved = modal.all_approved()

    id=data['id']
    leave_data2 = modal.remaining(id)
    leave_types2 = modal.all_leave_types()
    all_leaves = modal.all_leave()

    all_info = []
    headers = ['Name']
    for j in leave_types2:
        headers.append(j['name'] + " total")
        headers.append(j['name'] + " used")
    drs = modal.get_drs(id)

    for i in drs:
        one_info = [i['first_name']  + " " + i['middle_name'] + " " + i['last_name']]
        for j in leave_types2:
            # one_info[j['name'] + ' total'] = get_leave_total(leave_data2, j['id'], i['staff_number'], 'duration')
            print (i['gender'], j['gender'])
            one_info.append(get_leave_duration(all_leaves, i['role'], j['id'], i['gender']))
            one_info.append(get_leave_total(leave_data2, j['id'], i['staff_number'], 'total'))
        all_info.append(one_info)


    return render_template('leave.html', leave_types=leave_types, data=data, username=username, leave_data=leave_data, history=history, pending=pending, pending_count=len(pending), approved=approved, holiday=holiday, all_info=all_info, headers=headers)


def get_leave_duration(data, role, leave_id, gender):
    duration = 0
    for i in  data:
        print('searching ', i, 'for', role, leave_id)
        if str(i['level']) == str(role) and str(i['leave_id']) == str(leave_id) and gender in str(i['gender']):
            duration = i['duration']
            break
    return duration

def get_leave_total(data, leave_id, staff_no, type):
    val = 0
    for i in data:
        # print("Value is ", val, 'searching', i, 'for ', staff_no, leave_id, (i['leave_id'] == leave_id), (str(i['Staff_id'] == staff_no)))
        if i['leave_id'] == leave_id and str(i['Staff_id']) == str(staff_no):
            val = i[type]

            break

    return val


#222222
#222222

@app.route('/remaining_leave')
def remaining_leave():
    username = session['username']
    data = modal.find_all(username)
    id = 4
    print('data needed is', data)
    leave_data = modal.remaining(id)
    leave_types = modal.all_leave()
    print('leave types: ', leave_types)

    print('this is it', leave_data)

    all_info = []
    drs = modal.get_drs(id)

    for i in drs:
        one_info = {'name': i['first_name']}
        for j in leave_types:
            one_info[j['name'] + ' total'] = get_leave_total(leave_data, j['id'], i['staff_number'], 'duration')
            one_info[j['name'] + ' used'] = get_leave_total(leave_data, j['id'],i['staff_number'], 'total')
        all_info.append(one_info)

    print(all_info, 'all info')

    # for i in leave_types:
    #     found = False
    #     for j in leave_data:
    #         if i['leave_id'] == j['leave_id']:
    #             break
    #     if not found:
    #         leave_data.append({'total': 0, 'Staff_id': username, 'leave_id': i['leave_id'], 'duration': i['duration'],
    #                            'name': i['name']})
    print('leave data is now : ', leave_data)



@app.route('/test')
def test():
    user_id = session['id']
    print('useris', user_id)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "select first_name ,middle_name ,last_name ,staff_number from personal_data pd where line_manager ='" + str(
            user_id) + "'")
    dr = cursor.fetchall()

    drjson = json.dumps(dr, sort_keys=True,
                        indent=1,
                        default=default
                        )

    cursor.execute("select * from personal_data_history where lm='" + str(user_id) + "'")
    dd = cursor.fetchall()

    ddjson = json.dumps(dd, sort_keys=True,
                        indent=1,
                        default=default
                        )

    return render_template('c.html')


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


@app.route('/names')
def get_dr_names():
    print('fetching names of drs in app2')
    user_id = 3

    dr = modal.dr_names(str(user_id))
    json_dr = json.dumps(dr, sort_keys=True,
                         indent=1,
                         default=default
                         )
    print('json dr', json_dr)

    return json_dr





@app.route('/annual')
def annual():
    return redirect('leave1.html')


@app.route('/admin')
def admin():
    return render_template('admin_leave.html')



@app.route('/request_leave', methods=['POST'])
def request_leave():

    username = session['username']

    start = request.form['startdate']

    end = request.form['endate']
    leave_type_id = request.form['leave_type_id']
    comment = request.form['Comment']

    data1 = modal.find_all(username)
    print('data1 is', data1)


    print(data1['level'])
    print(data1['gender'])
    print(leave_type_id)

    data3 = modal.approved_pending_leave(username,leave_type_id)
    print(data3)
    line_m = data1['line_manager']
    s_id = data1['staff_number']

    if data3:
        datar = int(data3['duration']) - int(data3['total'])
    else:
        #user has not applied for for any leave of this type so he has all the days left. Get the total days
        total_duration = modal.get_leave_total_duration(leave_type_id)
        datar = total_duration['duration']
        print('fetched total duration from another src', datar)
    start1 = datetime.datetime.strptime(start, '%Y-%m-%d')
    ends1 = datetime.datetime.strptime(end, '%Y-%m-%d')

    holidays = modal.get_leave_holidays(start1, ends1)
    holiday_count = len(holidays)

    weekdays = util.workdays(start1,ends1)
    requested_leave_days = len(weekdays) - holiday_count
    # print(data2)
    print('this is requested_leave_days', requested_leave_days)
    print('this is datar', datar)

    if requested_leave_days <= datar:
        connection = app.config['pool'].get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "insert into history (start_date ,end_date ,comment ,leave_type_id, requested_date , status, line_manager, staff_id, requested_leave_days) values ('%s','%s','%s','%s' ,now(),'pending','%s','%s', '%s')"% (start, end,comment, leave_type_id, line_m, s_id, requested_leave_days)

        cursor.execute(query)
        cursor.close()
        connection.close()
        subject = "Leave Request"
        message = "hello %s, %s has applied for %s leave days. regards, leave planner"%(data1['line_manager_name'],data1['last_name'],requested_leave_days)
        mail.send_mail([data1['line_manager_email']], message, subject, [data1['email']])
        flash("LEAVE APPLICATION SUCCESSFUL")
        return redirect('/dashboard')
    else:
        flash("SORRY! YOU DO NOT HAVE THAT NUMBER OF DAYS REMAINING")
        return redirect('/dashboard')



@app.route('/approve_reject', methods = ['POST'])
def approve_reject():
    print("this is approve reject")
    id = request.form['id']
    status = request.form['status']
    comment = request.form['comment']
    result = modal.approve_reject(status,id, comment)
    email = result['email']
    line_manager_email = result['line_manager_email']
    subject = "Leave %s" % status
    if result['Status'] == 'approved':
        message = "hello, %s, your leave request with start date as ,%s, and end date as , %s has been approved by your line manager with the reason as %s " % (result['last_name'], result['start_date'],result['end_date'], comment)

    else:
        message = "hello, %s, your leave request with start date as ,%s, and end date as , %s has been rejected by your line manager with the reason as %s " % (result['last_name'], result['start_date'],result['end_date'], comment)
    mail.send_mail([email], message, subject,[line_manager_email])


    return redirect('/dashboard#linemanagermodal')


@app.route('/endofyear')
def endofyear():
    modal.enofyear()
    return 'ok'


@app.route('/home1')
def home1():
    return render_template('annual.html')


@app.route('/changepassword', methods=['POST'])
def changepassword():
    c_password = request.form['current_password']
    n_password = request.form['new_password']
    cf_password = request.form['confirm_password']
    username = session['username']
    p_word = modal.get_password(username)
    print (p_word)
    message= ""
    if bcrypt.check_password_hash(p_word['Password'], c_password):
        if n_password == cf_password:
            pw_hash = bcrypt.generate_password_hash(cf_password)
            query = modal.new_password(pw_hash,username)
            print(query)
            message = "Password changed successfully"
        else:
            message = "New password and confirmed passwords do not match"
    else:
        message = "Password incorrect"
    return redirect('/dashboard')


@app.route('/resetpassword', methods=['POST'])
def resetpassword():
    staff_id = request.form['pass_reset']
    pwd = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(8))
    pw_hash = bcrypt.generate_password_hash(pwd)
    modal.new_password(pw_hash, staff_id)
    # //todo send mail with ***pwd*** as the new password
    email = modal.get_personal_email(staff_id)
    print('email is', email)
    subject = 'Password Reset'
    message = "Your password has been reset. Your new password is '%s'" % pwd
    mail.send_mail([email['email']], message, subject,None)

    return redirect('admleave')


@app.route('/staff_info')
def staff_info():
    info = modal.all_staff()
    lm = modal.lmid()
    rl = modal.role()
    dp = modal.get_departments()
    st = modal.get_office()
    print('managers are', lm)
    print('staff info is', info)
    print('roles are', rl)
    print('dp are', dp)
    print('st are', st)
    return render_template('admin_staff_info.html', info=info, lm=lm, rl=rl, st=st, dp=dp)


@app.route('/holidays')
def holidays():
    query = modal.holiday()
    holiday = query
    print('holiday info is', holiday)
    return render_template('holidays.html', holiday=holiday)


@app.route('/admleave')
def admleave():
    leave_type = modal.admleave()
    role_leave = modal.role_leave()
    role = modal.role()
    print('leave_type info is', leave_type)
    print('role_leave info is', role_leave)
    return render_template('admin_leave.html', leave_type=leave_type, role_leave=role_leave, role=role)


@app.route('/admdash')
def admdash():
    staff_count = modal.get_count_staff()
    role = modal.get_count_role()
    office = modal.get_count_station()
    holidays = modal.get_count_holiday()
    staff = modal.staff_all()
    print('staff  is',staff)
    print('staff count is',staff_count)
    print('role count is',role)
    print('holidays count is',holidays)
    print('office count is', office)
    return render_template('admin_dash.html', staff=staff, office=office, role=role, holidays=holidays, staff_count=staff_count)


@app.route('/updateleavetype', methods=['POST'])
def updateleavetype():
    name = request.form['leave_name']
    gender = request.form['gender']
    id = request.form['id']
    query ="update leave_types set name='%s', gender='%s' where id='%s'"% (name,gender,id)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    print('update is ', query)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('admleave')



@app.route('/remove_leave', methods=['POST'])
def remove_leave():
    print('id is', request.form)
    nid = request.form['id']
    query = modal.remove_leave(nid)

    print('deleted is ', query)

    return redirect('admleave')



@app.route('/update_role_leave_days', methods=['POST'])
def update_role_leave_days():
    role = request.form['role']
    duration = request.form['duration']
    carryf = request.form['carryf']
    carryd = request.form['carryd']
    id = request.form['id']
    query = "update role_leave_days set role_id='%s', duration='%s', carry_forward='%s', days_carry_forward='%s' where id='%s'" % (role,duration, carryf, carryd, id )
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    print('leave_type is ', query)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('admleave')


@app.route('/remove_role_leave_days', methods=['POST'])
def remove_role_leave_days():
    print('id is', request.form)
    nid = request.form['id']
    query = modal.remove_role_leave_days(nid)

    print('deleted is ', query)

    return redirect('admleave')


@app.route('/view/<username>')
def view(username):
    details = modal.find_all(username)
    print('view details',details)
    userdata = json.dumps(details, sort_keys=True,
                        indent=1,
                        default=default
                        )
    return userdata


@app.route('/view_holidays/<id>')
def view_holidays(id):
    details = modal.view_holidays(id)
    print('holiday view details',details)
    userdata = json.dumps(details, sort_keys=True,
                        indent=1,
                        default=default
                        )
    return userdata


@app.route('/get_leave_types/<id>')
def update_leave_types(id):
    details = modal.update_leave_types(id)
    print('leave view details',details)
    userdata = json.dumps(details, sort_keys=True,
                        indent=1,
                        default=default
                        )
    return userdata


@app.route('/get_department/<id>')
def update_department(id):
    details = modal.get_department(id)
    print('department is',details)
    userdata = json.dumps(details, sort_keys=True,
                        indent=1,
                        default=default
                        )
    return userdata


@app.route('/get_role/<id>')
def update_role(id):
    details = modal.get_role(id)
    print('role is',details)
    userdata = json.dumps(details, sort_keys=True,
                        indent=1,
                        default=default
                        )
    return userdata


@app.route('/get_station/<id>')
def get_station(id):
    details = modal.get_stations(id)
    print('stations',details)
    userdata = json.dumps(details, sort_keys=True,
                        indent=1,
                        default=default
                        )
    return userdata


@app.route('/get_role_leave_days/<id>')
def get_role_leave_days(id):
    details = modal.get_role_leave_days(id)
    print('leave view details',details)
    userdata = json.dumps(details, sort_keys=True,
                        indent=1,
                        default=default
                        )
    return userdata


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/update_department', methods=['POST'])
def update_departments():
    name = request.form['department_name']
    id = request.form['id']
    query = "update departments set name='%s' where id='%s'"% (name,id)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    print('update_department is ', query)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('departments')


@app.route('/update_roles', methods=['POST'])
def update_roles():
    name = request.form['role_name']
    id = request.form['id']
    query = "update role set role_name='%s' where id='%s'"% (name,id)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    print('update_role is ', query)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('departments')


@app.route('/update_station', methods=['POST'])
def update_station():
    name = request.form['station_name']
    id = request.form['id']
    query = "update station set name='%s' where id='%s'"% (name,id)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    print('update_role is ', query)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('departments')


@app.route('/updateuser', methods=['POST'])
def updateuser():
    print('updating user')
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    n_first = request.form['first_name']
    n_middle = request.form['middle_name']
    n_last = request.form['last_name']
    n_gender = request.form['gender2']
    n_email = request.form['email']
    n_phone = request.form['phone']
    n_department = request.form['department']
    n_isadmin = request.form['isadmin2']
    n_line_manager = request.form['line_manager2']
    n_station = request.form['station']
    n_position = request.form['position']
    n_staffn = request.form['staff_number']
    n_role = request.form['role2']
    n_id = request.form['id']

    # if 'file' not in request.files:
    #     flash('No file part')
    #     return redirect(request.url)

    # if file.filename == '':
    #     flash('No file selected for uploading')
    #     return redirect(request.url)
    query = "update personal_data set first_name='%s', middle_name='%s', last_name='%s', gender='%s',email='%s', phone_number='%s', department='%s', isadmin='%s', line_manager='%s', station='%s', position='%s', staff_number='%s', role='%s' where id ='%s' " % (
    n_first, n_middle, n_last, n_gender, n_email, n_phone, n_department, n_isadmin, n_line_manager, n_station, n_position,
    n_staffn, n_role, n_id)

    if 'file-input' in request.files and request.files['file-input'].filename != '':
        file = request.files['file-input']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            n_pix = filename
            query = "update personal_data set first_name='%s', middle_name='%s', last_name='%s', gender='%s',email='%s', phone_number='%s', department='%s', isadmin='%s', line_manager='%s', station='%s', role='%s', staff_number='%s', profile_pix='%s'  where id ='%s' " % (
            n_first, n_middle, n_last, n_gender, n_email, n_phone, n_department, n_isadmin, n_line_manager, n_station,
            n_role, n_staffn, n_pix, n_id)

        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            # return redirect(request.url)
    print('update is ', query)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('staff_info')


@app.route('/updateholiday', methods=['POST'])
def updateholiday():
    n_name = request.form['holiday_name']
    n_date = request.form['holiday_date']
    n_id = request.form['id']
    query ="update holidays set nameofholiday='%s', date='%s' where id='%s'" % (n_name,n_date,n_id)
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    print('update is ', query)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('holidays')


@app.route('/remove_holiday', methods=['POST'])
def remove_holiday():
    print('id is', request.form)
    nid = request.form['id']
    query = modal.remove_holiday(nid)

    print('deleted is ', query)

    return redirect('holidays')


@app.route('/remove_department', methods=['POST'])
def remove_department():
    print('id is', request.form)
    nid = request.form['id']
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "delete  from departments where id=%s" % nid
    cursor.execute(query)
    cursor.close()
    connection.close()

    print('deleted department is ', query)

    return redirect('departments')


@app.route('/remove_role', methods=['POST'])
def remove_role():
    print('id is', request.form)
    id = request.form['id']
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    query ="delete  from role where id=%s"% id
    cursor.execute(query)
    cursor.close()
    connection.close()
    print('deleted role is ', query)

    return redirect('departments')


@app.route('/remove_office', methods=['POST'])
def remove_office():
    print('id is', request.form)
    id = request.form['id']
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "delete  from station where id=%s"% id
    cursor.execute(query)
    cursor.close()
    connection.close()

    print('deleted office is ', query)

    return redirect('departments')


@app.route('/departments')
def dept():
    department = modal.department()
    print('dept is ', department)
    station = modal.station()
    print('station is ', station)
    role = modal.role()
    print('role is ', role)
    return render_template('department.html', department=department, station=station,role=role)


@app.route('/new_holiday', methods=['POST'])
def new_holiday():
    name = request.form['holiday_name']
    date = request.form ['holiday_date']
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "insert into holidays set nameofholiday='%s', date='%s'"% (name,date)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('holidays')


@app.route('/newuser', methods=['POST'])
def newuser():
    print('updating user')
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    n_first = request.form['first_name']
    n_middle = request.form['middle_name']
    n_last = request.form['last_name']
    n_gender = request.form['gender2']
    n_email = request.form['email']
    n_phone = request.form['phone']
    n_department = request.form['department']
    n_isadmin = request.form['isadmin2']
    n_line_manager = request.form['line_manager2']
    n_station = request.form['station']
    n_position = request.form['position']
    n_staffn = request.form['staff_number']
    n_role = request.form['role2']
    n_pix =''


    # staff_id = request.form['pass_reset']
    pwd = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(8))
    pw_hash = bcrypt.generate_password_hash(pwd)
    modal.new_login(n_staffn, pw_hash, n_email)
    # //todo send mail with ***pwd*** as the new password
    # email = modal.get_personal_email(n_staffn)
    # print('email is', email)
    subject = 'Leave Portal Password'
    message = "Your password to the leave portal is '%s'" % pwd
    mail.send_mail([n_email], message, subject,None)


    if 'file-input' in request.files and request.files['file-input'].filename != '':
        file = request.files['file-input']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            n_pix = filename


        else:
            flash('Profile picture with types are txt, pdf, png, jpg, jpeg, gif is needed')
            # return redirect(request.url)
    query = "insert into personal_data set first_name='%s', middle_name='%s', last_name='%s', gender='%s',email='%s', phone_number='%s', department='%s', isadmin='%s', line_manager='%s', station='%s', role='%s',position='%s', staff_number='%s', profile_pix='%s'" % (
        n_first, n_middle, n_last, n_gender, n_email, n_phone, n_department, n_isadmin, n_line_manager, n_station,
        n_role, n_position, n_staffn, n_pix)

    print('inserted user is ', query)
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('staff_info')


@app.route('/new_leave_days', methods=['POST'])
def new_leave_days():
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    leave = request.form['leave']
    gender = request.form['carryg']
    role = request.form['role']
    duration = request.form['duration']
    carryf = request.form['carryf']
    carryd = request.form['carryd']
    query1 = "insert into role_leave_days set leave_id='%s', role_id='%s', duration='%s', carry_forward='%s', days_carry_forward='%s'"% (leave,role, duration,carryf,carryd)
    print('new leave is ', query1)
    cursor.execute(query1)
    cursor.close()
    connection.close()
    return redirect('admleave')


@app.route('/new_leave', methods=['POST'])
def new_leave():
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    leave = request.form['leave']
    gender = request.form['carryg']
    query1 = "insert into leave_types set name='%s', gender='%s'"% (leave,gender)
    print('new leave is ', query1)
    cursor.execute(query1)
    cursor.close()
    connection.close()
    return redirect('admleave')


@app.route('/new_department', methods=['POST'])
def new_department():
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    name = request.form['name']
    query = "insert into departments set name='%s'"% name
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('departments')


@app.route('/new_role', methods=['POST'])
def new_role():
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    name = request.form['name']
    query = "insert into role set role_name='%s'"% name
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('departments')


@app.route('/new_office', methods=['POST'])
def new_office():
    connection = app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    name = request.form['name']
    query = "insert into station set name='%s'"% name
    cursor.execute(query)
    cursor.close()
    connection.close()
    return redirect('departments')


@app.before_first_request
def db_conn():
    print("Creating db pool")
    g.pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name='ourPool',
        pool_size=32,
        host='localhost',
        database='leaveportal',
        user='root',
        password='', port='3308'
    )
    app.config['pool'] = g.pool
    modal.connection = app



if __name__ == '__main__':
    app.config.update(mail.mail_settings)
    mail.init(app)
    app.run(port=5000, debug=True)
