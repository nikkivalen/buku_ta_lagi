from logging import error
from server import jsonify
from server import db
from server import helper

# select history
def selectByEmail(data):
    query = "SELECT * FROM HISTORY WHERE email_user = %s order by date desc, keyword limit 10 "
    query_data = [data['email']]
    try: 
        history = db.execute_sql(query,query_data)
        return jsonify({"history": history}),200
    except:
        return jsonify({"message": "Failed!"}),400

# del history
def clearHistory(data):
    query = "DELETE FROM HISTORY where email_user = %s"
    query_data = [data['email']]
    try: 
        history = db.execute_query(query,query_data)
        return jsonify({"message": "History Deleted"}),200
    except:
        return jsonify({"message": "Failed!"}),400

# add history
def addHistory (keyword,email):
    query = "SELECT * FROM HISTORY where email_user = %s and keyword = %s"
    query_data = [email,keyword]
    now = helper.get_current_time()
    try: 
        history = db.execute_sql(query,query_data)
        
        if len(history) == 0:
            
            query = "INSERT INTO HISTORY VALUES ('',%s,%s,%s)"
            query_data = [email,keyword,now]
            try:
                db.execute_query(query,query_data)
                return jsonify({"message": "History Added"}),200
            except:
                return jsonify({"message": "Internal Server Error"}),400
        else:
            
            query = "UPDATE HISTORY SET date = %s where id_history = %s"
            query_data = [now,history[0][0]]
            try:
                db.execute_query(query,query_data)
                return jsonify({"message": "History Added"}),200
            except:
                return jsonify({"message": "Internal Server Error"}),400
    except:
        
        return jsonify({"message": "Failed!"}),400