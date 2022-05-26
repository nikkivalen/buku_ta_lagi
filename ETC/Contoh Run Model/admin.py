from logging import error
from server import jsonify
from server import db,app
from server import helper
from flask import redirect
import jwt
from datetime import datetime, timedelta

def validation_register(data):
    # there is data empty
    if data == {}:
        return "Form still empty"
    if data.get('inputName') == {}:
        return "Field name must not be empty"
    if data.get('inputPassword') == {}:
        return "Field password must not be empty"
    if data.get('inputEmail') == {}:
        return "Field email must not be empty"

    # email
    email = helper.is_email(data.get('inputEmail'))
    if not email:
        return "Email is not valid"
    
    query = "SELECT * FROM ADMIN WHERE lower(email_admin) = lower(%s)"
    query_data = [data.get('inputEmail')]
    try:
        result = db.execute_sql(query,query_data)
        if result: 
            return "Email has already used!"
    except:
        return 'Internal Server Error'

    # password
    password = helper.is_password( data.get('inputPassword'))
    if not password:
        return "Password must be 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character"

    return ''

def insert(data):
    validation = validation_register(data)
    if validation != '':
        return jsonify({"message": validation}),400

    #get data
    email = data.get('inputEmail')
    password = data.get('inputPassword')
    name = data.get('inputName')
    now = helper.get_current_time()
    password = helper.hash_password(password) #hashing password
    verify_token = helper.get_verification_token()
    print(name)
    query = "INSERT INTO ADMIN VALUES(%s,%s,%s,1,%s,1,%s,%s)"
    query_data = (email,password,name,None,now,now)
    try: 
        db.execute_query(query,query_data)
        return jsonify({"message": "Register success!"}),201
    except:
        db.execute_query(query,query_data)
        return jsonify({"message": "Register Failed!"}),400


def login (data):
    if data == {}:
        return jsonify({"message": "Form still empty"}),400
    if data.get('inputEmail') == {}:
        return jsonify({"message": "Field email must not be empty"}),400
    if data.get('inputPassword') == {}:
        return jsonify({"message": "Field password must not be empty"}),400
    query = "SELECT * FROM ADMIN WHERE lower(email_admin) = lower(%s)"
    query_data = [data['inputEmail']]
    try: 
        user = db.execute_sql(query,query_data)
        # print(len(user))
        if len(user) <= 0:
            # print("adf")
            return jsonify({"message": "Please Register!"}),400
        else:
            password = True
            if user[0][3] == 1:
                password = helper.verify_password(data.get('inputPassword'),user[0][1])
            if password:
                token = jwt.encode({
                    'email' : data.get('inputEmail'),
                    'tipe' : user[0][3],
                    'exp' : datetime.utcnow() + timedelta(minutes = 180)
                },app.config['SECRET_KEY'])
                now = helper.get_current_time()
                query = "UPDATE ADMIN set token = %s, updated_at=%s where lower(email_admin) = lower(%s)"
                query_data = (token,now,data['inputEmail'])
                try: 
                    db.execute_query(query,query_data)
                    out = jsonify({'token': token})
                    return out,200
                except:
                    # db.execute_query(query,query_data)
                    return jsonify({"message": "Login Failed!"}),400
            else:
                return jsonify({"message": "Wrong Password!"}),400
    except:
        return jsonify({"message": "Internal Server Error!"}),500

# pagination
def pagination():
    query = "SELECT count(*) FROM admin"
    try: 
        jum_user = db.execute_sql(query)
        if len(jum_user) > 0:
            return jsonify({"pagination": jum_user[0]}),200
        else:
            return jsonify({"pagination": 0}),200
    except:
        return jsonify({"message": "Error"}),400

def getAllAdmin(offset):
    query = "SELECT * FROM ADMIN WHERE status_admin = 1 and tipe_admin = 1 limit 10 offset %s "
    query_data = [int(offset)]
    try:
        result = db.execute_sql(query,query_data)
        return jsonify({"user": result}),200
    except:
        return jsonify({"message": "Login Failed!"}),400
    
def getAdmin(email):
    query = "SELECT * FROM ADMIN WHERE status_admin = 1 and lower(email_admin) = lower(%s)"
    query_data = [email]
    try:
        result = db.execute_sql(query,query_data)
        return jsonify({"user": result}),200
    except:
        return jsonify({"message": "Login Failed!"}),400

def getUserbyToken(token):
    query = "SELECT * FROM ADMIN WHERE token = %s"
    query_data = [token]
    try: 
        user = db.execute_sql(query,query_data)
        if len(user)==0:
            return None
        return token
    except:
        return None

def deleteAdmin(email):
    query = "UPDATE ADMIN SET status_admin = 0 where lower(email_admin) = lower(%s)"
    query_data = [email]
    try: 
        user = db.execute_query(query,query_data)
        return jsonify({"message": "Delete Success!"}),200
    except:
        return jsonify({"message": "Delete Failed!"}),400