import mysql.connector
import db

connection = None


def find_all(username):
    query = "select p1.*,concat(p2.first_name ,' ',p2.middle_name , ' ', p2.last_name ) line_manager_name,p2.email line_manager_email from personal_data p1 left join personal_data p2 on p1.line_manager = p2.id where p1.staff_number = '" + str(username) + "'"
    return db.get_one(connection, query)


def history(username,status):
    query = "select * from leave_history where staff_id= '" + str(username) + "'" "and status='" + str(status)+ "'"
    return db.get_many(connection, query)


def all_data(username,level,gender):
    query =  "with X as (select leave_type_id , count(status) total, start_date from history where status='approved' and Staff_id = '" + str(
            username) + "' and year(start_date) = year(now()) group by leave_type_id ) select coalesce(x.total,0) total, a.*, b.* FROM role_leave_days a,leave_types b left join x on b.id=x.leave_type_id where a.leave_id=b.id and a.level='" + str(
            level) + "' and b.gender like '%" + str(gender) + "%'"
    return db.get_many(connection, query)


def all_data2(username,level,gender,leave_type_id):
    query = "with X as (select leave_type_id , count(status) total, start_date from history where status='approved' and Staff_id = '" + str(
            username) + "' and year(start_date) = year(now()) group by leave_type_id ) select coalesce(x.total,0) total, a.*, b.* FROM role_leave_days a,leave_types b left join x on b.id=x.leave_type_id where a.leave_id=b.id and a.level='" + str(
            level) + "' and b.gender like '%" + str(gender) + "%' and leave_id='"+leave_type_id+"'"
    return db.get_one(connection, query)


def leave_history(username):
    query = "select * from leave_history where staff_id='" + str(username) + "'"
    return db.get_many(connection, query)


def dr_names(user_id):
    query = """select concat(first_name, " " ,middle_name, " " ,last_name) name ,staff_number id from personal_data pd where line_manager ='""" + str(user_id) + "'"
    return db.get_many(connection, query)


def approve_reject(status, id, comment):
    query ="update history set status='%s',  Approved_Rejected_date = now(), managers_comment='%s' where id= %s" % (status,  comment, id)
    db.insert(connection,query)
    query = "select p.*, p2.email line_manager_email, h.Approved_Rejected_date, h.Status, h.start_date ,h.end_date from personal_data p, history h, personal_data p2 where p.staff_number = h.staff_id and h.id = %s and p2.id = p.line_manager" % id
    return db.get_one(connection,query)


def pending( line_manager_id):
    query= "select * from leave_history lh where line_manager = '%s'  and status='pending'"% line_manager_id
    return db.get_many(connection, query)


def approved_pending_leave(staff_id, leave_type_id):
    query ="select * from approved_pending_leave_view  where Staff_id = '%s' and leave_id = %s"% (staff_id, leave_type_id )
    return db.get_one(connection,query)


def approved_pending_info(staff_id,id):
    query ="select * from approved_pending_leave_view  where Staff_id = '%s' and level ='%s'"% (staff_id,id)
    print('my approved_pending_info is', query)
    return db.get_many(connection,query)


def get_leave_types(gender, level):
    query = "select * from leave_days_types  where gender like '%" + str(gender) + "%' and level = '" + str(level) + "'"
    print('my leave type days is',query )
    return db.get_many(connection, query)


def get_leave_total_duration(leave_type_id):
    query = "select duration from leave_days_types  where leave_id = '" + str(leave_type_id) + "'"
    return db.get_one(connection, query)


def line_manager_approved( line_manager_id):
    query= "select * from leave_history lh where line_manager = '%s'  and status='approved' and year(start_date) = year(now())"% line_manager_id
    return db.get_many(connection, query)


def all_approved( ):
    query= "select * from leave_history lh where status='approved' and year(start_date) = year(now())"
    return db.get_many(connection, query)

def enofyear():
    query = "calculate_carry_forward_leave_days"
    return db.call_proc(connection, query)

def carried_froward_days(staff_id):
    query= "select * from carried_forward_leave_days cfld where staff_id =%s"% staff_id
    return db.get_one(connection, query)

def get_holidays():
    query = "select * from holidays"
    return db.get_many(connection, query)

def get_leave_holidays(start_date, end_date):
    query = "select * from holidays where date between '%s' and '%s'" % (start_date, end_date)
    return db.get_many(connection, query)


def get_password(staff_id):
    query = "select * from login_info where staff_id=%s"% staff_id
    return db.get_one(connection, query)

def new_password(password, staff_id):
    query = "update login_info set Password='%s' where staff_id='%s'"% (password.decode('ascii'),staff_id)
    db.insert(connection,query)

def all_staff():
    query = "select p1.*,concat(p2.first_name ,' ',p2.middle_name , ' ', p2.last_name ) line_manager_name,p2.email line_manager_email from personal_data p1 left join personal_data p2 on p1.line_manager = p2.id "
    return db.get_many(connection, query)


def holiday():
    query = "select * from holidays"
    return db.get_many(connection, query)

def admleave():
    query = "select * from leave_types"
    return db.get_many(connection, query)

def lmid():
    query = "select * from personal_data where role in (2,3)"
    return db.get_many(connection, query)

def role():
    query = "select * from role"
    return db.get_many(connection, query)


def view_holidays(id):
    query = "select * from holidays where id=%s"% id
    return db.get_one(connection, query)

def update_leave_types(id):
    query = "select * from leave_types where id=%s"% id
    return db.get_one(connection, query)


def remove_holiday(id):
    query = "delete from holidays where id=%s"% id
    return db.get_one(connection, query)


def department():
    query = "select * from departments"
    return db.get_many(connection, query)

def station():
    query = "select * from station"
    return db.get_many(connection, query)


def get_stations(id):
    query = "select * from station where id=%s"% id
    return db.get_one(connection, query)


def role_leave():
    query = "select lt.name, lt.gender, r.role_name, rld.duration, rld.carry_forward, rld.days_carry_forward, rld.id, rld.role_id from role_leave_days rld left join leave_types lt on rld.leave_id = lt.id left join `role` r on r.id = rld.role_id "
    return db.get_many(connection, query)

def get_role_leave_days(id):
    query ="select * from role_leave_days where id=%s"% id
    return db.get_one(connection, query)


def remove_leave(id):
    query = "delete from leave_types where id=%s"% id
    return db.get_one(connection, query)

def remove_role_leave_days(id):
    query ="delete  from role_leave_days where id=%s"% id
    return db.get_one(connection, query)

def get_department(id):
    query = "select * from departments where id=%s"% id
    return db.get_one(connection, query)

def get_personal_email(staff_id):
    query = " select email from personal_data where staff_number=%s"% staff_id
    return db.get_one(connection,query)

def get_role(id):
    query = "select * from role where id=%s"% id
    return db.get_one(connection, query)


def get_office():
    query = "select * from station"
    return db.get_many(connection, query)


def get_departments():
    query = "select * from departments"
    return db.get_many(connection, query)

def get_leave_id(leave):
    query = "Select id from leave_types where name='%s'"% leave
    return db.get_one(connection, query)

def get_count_staff():
    query = "select count(first_name) staffno from personal_data pd"
    return db.get_one(connection, query)

def get_count_role():
    query = "select count(role_name) role from role "
    return db.get_one(connection, query)

def get_count_station():
    query = "select count(name) station from station"
    return db.get_one(connection, query)

def get_count_holiday():
    query = "select count(nameofholiday) holiday from holidays"
    return db.get_one(connection, query)

def staff_all():
    query = "select * from personal_data"
    return db.get_many(connection,query)


def new_login(staff_id, password, email):
    query = "insert into login_info  (staff_id, password, email) values ('%s','%s','%s')"%  (staff_id,password.decode('ascii'),email)
    db.insert(connection,query)

def remaining(lm_id):
    query = "select * from approved_pending_leave_lm_view where line_manager =%s"% lm_id
    return db.get_many(connection,query)

def all_leave():
    query = "select * from leave_days_types"
    return db.get_many(connection,query)

def all_leave_types():
    query = "select * from leave_types"
    return db.get_many(connection,query)


def get_drs(lm):
    query = " select * from personal_data where line_manager = %s" % lm
    return db.get_many(connection, query)