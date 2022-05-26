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
    
    query = "SELECT * FROM USER WHERE lower(email_user) = lower(%s)"
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
    print(validation)
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
    query = "INSERT INTO USER VALUES(%s,%s,%s,0,%s,%s,10,300,0,'',%s,'')"
    query_data = (email,name,password,now,now,verify_token)
    try: 
        db.execute_query(query,query_data)
        #send email
        verification_link = app.config['CLIENT_LINK']+"/email-verification/"+verify_token
        helper.send_email_verification(email,verification_link)
        return jsonify({"message": "Register success!"}),201
    except:
        db.execute_query(query,query_data)
        # db.execute_query(query,query_data)
        # verification_link = app.config['CLIENT_LINK']+"/email-verification/"+verify_token
        # helper.send_email_verification(email,verification_link)
        return jsonify({"message": "Register Failed!"}),400

def verify_email(verify_token):
    query = "SELECT * FROM USER WHERE verify_token = %s"
    query_data = [verify_token]
    try:
        user = db.execute_sql(query,query_data)
        if len(user) <= 0:
            return jsonify({"message": "Error!"}),500
        else:
            now = helper.get_current_time()
            query = "UPDATE user SET verification = 1, updated_At = %s WHERE verify_token = %s"
            query_data = (now,verify_token)
            try:
                db.execute_query(query,query_data)
                print(app.config['FRONT_LINK'] )
                return redirect(app.config['FRONT_LINK'], code=302)
                # return jsonify({"message": "Email has been verified!"}),200
            except:
                # return redirect(app.config['FRONT_LINK'], code=200)
                return jsonify({"message": "Email verification failed!"}),500
    except:
        return jsonify({"message": "Error!"}),500
    

def login (data):
    if data == {}:
        return jsonify({"message": "Form still empty"}),400
    if data.get('inputEmail') == {}:
        return jsonify({"message": "Field email must not be empty"}),400
    if data.get('inputPassword') == {}:
        return jsonify({"message": "Field password must not be empty"}),400
    query = "SELECT * FROM USER WHERE lower(email_user) = lower(%s)"
    query_data = [data['inputEmail']]
    try: 
        user = db.execute_sql(query,query_data)
        # print(len(user))
        if len(user) <= 0:
            # print("adf")
            return jsonify({"message": "Please Register!"}),400
        else:
            # print(data.get('inputPassword'))
            # print(user[0][2])
            password = helper.verify_password(data.get('inputPassword'),user[0][2])
            if password:
                #check plan expired
                now_date = helper.get_current_time().date()
                if  user[0][3] == 1:
                    if  now_date > user[0][11]:
                        query = "UPDATE USER SET tipe_user = 0, expired = %s, api_hit = 0, limit_teks = 300 WHERE email_user = %s"
                        query_data = [None,user[0][0]]
                        try:
                            db.execute_query(query,query_data)
                        except:
                            return None
                if user[0][8] == 0:
                    out = jsonify({'message': "Please verify your account"})
                    return out,400
                else:
                    token = jwt.encode({
                        'email' : data.get('inputEmail'),
                        'exp' : datetime.utcnow() + timedelta(minutes = 180)
                    },app.config['SECRET_KEY'])
                    now = helper.get_current_time()
                    query = "UPDATE USER set token = %s, updated_at=%s where lower(email_user) = lower(%s)"
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

def minusData(email, api_hit, expired):
    now_date = helper.get_current_time().date()
    if expired != "":
        if  now_date > expired:
            query = "UPDATE USER SET tipe_user = 0, expired = %s, api_hit = %s, limit_teks = 300 WHERE email_user = %s"
            query_data = [None,api_hit-1,email]
        else:
            query = "UPDATE USER SET api_hit = %s WHERE email_user = %s"
            query_data = [api_hit-1,email]
    else:
        query = "UPDATE USER SET api_hit = %s WHERE email_user = %s"
        query_data = [api_hit-1,email]
    try:
        db.execute_query(query,query_data)
    except:
        return None

def cekTokenDev(token,teks):
    query = "SELECT * FROM USER WHERE verify_token = %s"
    query_data = [token]
    try: 
        user = db.execute_sql(query,query_data)
        if len(user) > 0:
            now_date = helper.get_current_time().date()
            if int(user[0][6]) > 0 and len(teks) <= int(user[0][7]) and now_date <= user[0][11] and user[0][3] == 1:
                minusData(user[0][0],int(user[0][6]),user[0][11])
                return "premium"
            elif int(user[0][6]) > 0 and len(teks) <= int(user[0][7]) and now_date <= user[0][11] and user[0][3] == 0:
                minusData(user[0][0],int(user[0][6]),user[0][11])
                return "free"
            else:
                print(len(teks))
                return jsonify({"message": "Failed! Please Check Your Account Api Hit, expired and limit teks"}),400
        else: 
            return jsonify({"message": "user not found"}),404
    except:
        return jsonify({"message": "Failed User!"}),400

def getAll(offset):
    query = "SELECT * FROM USER order by email_user limit 10 offset %s"
    query_data = [int(offset)]
    try: 
        user = db.execute_sql(query,query_data)
        return jsonify({"user": user}),200
    except:
        return jsonify({"message": "Failed!"}),400

def getUserbyEmail(data):
    query = "SELECT email_user, nama_user, tipe_user, api_hit, verify_token, expired FROM USER WHERE email_user = %s"
    query_data = [data['email']]
    try: 
        user = db.execute_sql(query,query_data)
        return jsonify({"user" : user}),200
    except:
        return jsonify({"message": "Failed!"}),400

def getUserbyEmail2(data):
    query = "SELECT email_user, nama_user, tipe_user, api_hit, verify_token, expired FROM USER WHERE email_user = %s"
    query_data = [data['email']]
    try: 
        user = db.execute_sql(query,query_data)
        return user
    except:
        return jsonify({"message": "Failed!"}),400

def getUserbyToken(token):
    query = "SELECT email_user,nama_user FROM USER WHERE token = %s"
    query_data = [token]
    try: 
        user = db.execute_sql(query,query_data)
        if len(user)==0:
            return None
        return token
    except:
        return None

def updateUser(data):
    query = "UPDATE USER set nama_user = %s, password_user =%s, updated_at = %s where email_user = %s"
    #get data
    email = data['email']
    password = data['password']
    name = data['name']
    now = helper.get_current_time()
    password = helper.is_password( password )
    if not password:
        return jsonify({"message": "Password Invalid"}),400
    else:
        password = helper.hash_password(password) #hashing password

        query_data = [name,password,now,email]
        try: 
            db.execute_query(query,query_data)
            return jsonify({"message": "Update Success!"}),200
        except:
            return jsonify({"message": "Update Failed!"}),400

# pagination
def pagination():
    query = "SELECT count(*) FROM user"
    query_data = []
    try: 
        jum_user = db.execute_sql(query)
        if len(jum_user) > 0:
            return jsonify({"pagination": jum_user[0]}),200
        else:
            return jsonify({"pagination": 0}),200
    except:
        return jsonify({"message": "Error"}),400