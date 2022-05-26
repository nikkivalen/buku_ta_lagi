from logging import error
from server import jsonify
from server import db
from server import helper
from decimal import * #for rupiah format

# pagination
def pagination():
    query = "SELECT count(*) FROM premium"
    try: 
        jum_user = db.execute_sql(query)
        if len(jum_user) > 0:
            return jsonify({"pagination": jum_user[0]}),200
        else:
            return jsonify({"pagination": 0}),200
    except:
        return jsonify({"message": "Error"}),400

# getPremium
def getPlan(offset):
    query = "SELECT * FROM PREMIUM order by status desc limit 10 offset %s"
    query_data = [int(offset)]
    try: 
        plan = db.execute_sql(query,query_data)
        return jsonify({"plan":  plan}),200
    except:
        return jsonify({"message": "Failed!"}),400

def getPlanById(id):
    query = "SELECT * FROM PREMIUM where id_premium = %s"
    query_data = [id]
    try: 
        plan = db.execute_sql(query,query_data)
        return jsonify({"plan":  plan}),200
    except:
        return jsonify({"message": "Failed!"}),400

# insert premium
def addPremium (data):
    now = helper.get_current_time()
    tampilan = helper.transform_to_rupiah_format(Decimal(str(data['price'])+".00"))
    query = "INSERT INTO PREMIUM VALUES ('', %s, %s, %s, %s, %s, 1, %s, %s, %s,%s)"
    query_data = [data['jenis'],data['validity'],data['price'],data['keterangan'],tampilan,data['api_hit'],data['limit'],now,now]
    try:
        db.execute_query(query,query_data)
        return jsonify({"message" : "Insert success"}),201
    except:
        return jsonify({"message" : "Failed"}),400

# delete premium
def deletePremium (id):
    stat = 0
    query = "SELECT * FROM PREMIUM where id_premium = %s"
    print(id)
    plan = db.execute_sql(query,[id])
    
    if (plan[0][6] == 0): 
        stat = 1
    print(stat)
    now = helper.get_current_time()
    query = "UPDATE PREMIUM set status = %s, updated_at = %s where id_premium = %s"
    query_data = [stat,now,id]
    try:
        db.execute_query(query,query_data)
        if stat == 0:
            return jsonify({"message" : "Deactivation success"}),200
        return jsonify({"message" : "Activation success"}),200
    except:
        return jsonify({"message" : "Failed"}),400

# update premium
def updatePremium (data,id):
    now = helper.get_current_time()
    tampilan = helper.transform_to_rupiah_format(Decimal(str(data['price'])+".00"))
    query = "UPDATE PREMIUM set jenis_premium = %s, validity = %s, price = %s, keterangan = %s, tampilan = %s, api_hit = %s, limit_teks = %s , updated_at = %s where id_premium = %s"
    query_data = [data['jenis'],data['validity'],data['price'],data['keterangan'],tampilan,data['api_hit'],data['limit'],now,id]
    try:
        db.execute_query(query,query_data)
        return jsonify({"message" : "Update success"}),200
    except:
        db.execute_query(query,query_data)
        return jsonify({"message" : "Failed"}),400