from flask import Flask, render_template, request, redirect, url_for, session, g
import json
import mysql.connector
from mysql.connector import Error
import datetime
from flask_cors import CORS
from multiprocessing import Pool
from mysql.connector.pooling import MySQLConnectionPool
from flask_mysqlpool import MySQLPool

app = Flask(__name__)
CORS(app)
app.secret_key = 'the generator people'

# connection = None

# try:
#     app.config['MYSQL_HOST'] = 'localhost'
#     app.config['MYSQL_PORT'] = 3308
#     app.config['MYSQL_USER'] = 'leaveportal'
#     app.config['MYSQL_PASS'] = ''
#     app.config['MYSQL_DB'] = 'leaveportal'
#     app.config['MYSQL_POOL_NAME'] = 'mysql_pool'
#     app.config['MYSQL_POOL_SIZE'] = 31
#     app.config['MYSQL_AUTOCOMMIT'] = True
#
#
#
#
#
# except Error as e:
#     print("Error while connecting to MySQL", e)
#
# db = MySQLPool(app)


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
        connection = g.pool.get_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM login_info WHERE staff_id = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # print(account)
        cursor.close()
        # If account exists in accounts table in out database
        if account:
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
    connection = g.pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    username = session['username']
    print(username)
    cursor.execute("select * from personal_data where staff_number = '" + str(username) + "'")
    data = cursor.fetchone()
    # cursor.close()
    print(data)
    cursor.execute(
        "with X as (select leave_type_id , count(status) total, start_date from history where status='approved' and Staff_id = '" + str(
            username) + "' and year(start_date) = year(now()) group by leave_type_id ) select coalesce(x.total,0) total, a.*, b.* FROM role_leave_days a,leave_types b left join x on b.id=x.leave_type_id where a.leave_id=b.id and a.level='" + str(
            data['level']) + "' and b.gender like '%" + str(data['gender']) + "%'")
    leave_data = cursor.fetchall()
    print('this is it', leave_data)
    cursor.execute("select * from leave_history where staff_id='" + str(username) + "'")
    history = cursor.fetchall()
    print(history)
    cursor.close()
    return render_template('leave.html', data=data, username=username, leave_data=leave_data, history=history)


@app.route('/test')
def test():
    user_id = session['id']
    # print('useris', user_id)
    # connection = g.pool.get_connection()
    # cursor = connection.cursor(dictionary=True)
    # cursor.execute(
    #     "select first_name ,middle_name ,last_name ,staff_number from personal_data pd where line_manager ='" + str(
    #         user_id) + "'")
    # dr = cursor.fetchall()
    # # print('DR is:',dr)
    # drjson = json.dumps(dr, sort_keys=True,
    #                     indent=1,
    #                     default=default
    #                     )
    # # print('this json', drjson)
    # cursor.execute("select * from personal_data_history where lm='" + str(user_id) + "'")
    # dd = cursor.fetchall()
    # print('DD is:',dd)
    # ddjson = json.dumps(dd, sort_keys=True,
    #                     indent=1,
    #                     default=default
    #                     )
    # print('this json', ddjson)
    return render_template('c.html')


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


@app.route('/names')
def get_dr_names():
    print('fetching names of drs')
    user_id = 3
    connection =app.config['pool'].get_connection()
    cursor =  connection.cursor(dictionary=True)
    cursor.execute("""select concat(first_name, " " ,middle_name, " " ,last_name) name ,staff_number id from personal_data pd where line_manager ='""" + str(user_id) + "'")
    dr = cursor.fetchall()
    json_dr = json.dumps(dr, sort_keys=True,
                         indent=1,
                         default=default
                         )
    print('json dr', json_dr)
    cursor.close()
    return json_dr


@app.route('/events')
def get_events():
    user_id = 3
    connection =app.config['pool'].get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("select id,comment text,start_date start,end_date end,Staff_id as resource from personal_data_history where lm='" + str(user_id) + "'")
    dd = cursor.fetchall()
    json_dd = json.dumps(dd,
                         indent=1,
                         default=default
                         )
    print('json dd', json_dd)
    cursor.close()
    return json_dd


@app.route('/annual')
def annual():
    return render_template('test.html')


@app.before_first_request
def db_conn():
    print("Creating db pool")
    g.pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name='ourPool',
        pool_size=10,
        host='localhost',
        database='leaveportal',
        user='root',
        password='', port='3308'
    )
    app.config['pool'] = g.pool


if __name__ == '__main__':

    app.run(port=5000, debug=True)
