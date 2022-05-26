from server import jsonify
from server import db
from server import helper
from server import app
import jwt

#midtrans
from server import core

# pagination
def pagination(email):
    query = "SELECT count(*) FROM transaction where lower(email_user) = lower(%s)"
    query_data = [email]
    try: 
        jum_user = db.execute_sql(query,query_data)
        if len(jum_user) > 0:
            return jsonify({"pagination": jum_user[0]}),200
        else:
            return jsonify({"pagination": 0}),200
    except:
        return jsonify({"message": "Error"}),400

def getPlan():
    query = "SELECT * FROM PREMIUM where status=1"
    try: 
        plan = db.execute_sql(query)
        return jsonify({"plan":  plan}),200
    except:
        return jsonify({"message": "Failed!"}),400

def getTransaction(data):
    query = "SELECT t.id_transaksi, t.tanggal_transaksi, p.jenis_premium, t.nomor_kartu, t.jumlah_uang FROM transaction t, premium p where t.id_premium = p.id_premium and t.email_user =%s order by  t.tanggal_transaksi desc"
    query_data = [data['email']]
    try: 
        transaksi = db.execute_sql(query,query_data)
        return jsonify({"transaksi": transaksi}),200
    except:
        return jsonify({"message": "Get Data Failed!"}),400

def getTransaction(data, offset):
    if (offset == -1):
        query = "SELECT t.id_transaksi, t.tanggal_transaksi, p.jenis_premium, t.nomor_kartu, t.jumlah_uang FROM transaction t, premium p where t.id_premium = p.id_premium and t.email_user =%s order by  t.tanggal_transaksi desc"
        query_data = [data['email']]
    else :
        query = "SELECT t.id_transaksi, t.tanggal_transaksi, p.jenis_premium, t.nomor_kartu, t.jumlah_uang FROM transaction t, premium p where t.id_premium = p.id_premium and t.email_user =%s order by  t.tanggal_transaksi desc limit 10 offset %s"
        query_data = [data, int(offset)]
    try: 
        transaksi = db.execute_sql(query,query_data)
        return jsonify({"transaksi": transaksi}),200
    except:
        return jsonify({"message": "Get Data Failed!"}),400

def subscribe(user,data):
    query = "SELECT * FROM PREMIUM WHERE id_premium = %s"
    query_data = [data['id_plan']]
    print(data)
    try: 
        plan = db.execute_sql(query,query_data)
    except:
        return jsonify({"message": "Failed!"}),400
    # get card token
    card_token_params = {
        'card_number': data['card_number'],
        'card_exp_month': data['card_exp_month'],
        'card_exp_year': data['card_exp_year'],
        'card_cvv': data['card_cvv'],
        'client_key': core.api_config.client_key
    }

    cc_token = None
    try:
        card_token_response = core.card_token(card_token_params)
        cc_token = card_token_response['token_id']
    except:
        return jsonify({'message': 'Credit card invalid!'}),400

    #charge with card token
    order_id = helper.get_uuid()
    now = helper.get_current_time()
    expired_date = helper.get_exp_time(plan[0][2])
    price = plan[0][3]
    card_charge_params = {
        "payment_type": "credit_card",
        "transaction_details": {
            "gross_amount": price,
            "order_id": order_id,
        },
        "credit_card":{
            "token_id": cc_token
        },
        "item_details": [{
            "id": data['id_plan'],
            "name": plan[0][1],
            "quantity": 1,
            "price": price,
        }],
        "customer_details": {
            "name": user[0][1],
            "email": user[0][0]
        }
    }

    # charge transaction
    try:
        charge_response = core.charge(card_charge_params)
        if charge_response['status_code'] == '200':
            #add payment history
            query = "INSERT INTO transaction VALUES(%s,%s,%s,%s,%s,%s,%s)"
            query_data = (order_id,now,data['id_plan'],user[0][0],data['card_number'],price,expired_date)
            db.execute_query(query,query_data)

            #update user plan
            query = "UPDATE USER SET tipe_user = 1, expired = %s, api_hit = %s, limit_teks = %s, updated_at = %s WHERE email_user = %s"
            query_data = (expired_date,int(user[0][3])+int(plan[0][7]), int(plan[0][8]),now,user[0][0])
            db.execute_query(query,query_data)

            #send invoice email to user
            helper.send_email_invoice(user[0][0],plan[0],order_id,expired_date,user[0])
        else:
            raise ValueError()

        return jsonify({"message": "Payment successful!","data":card_charge_params}),200
    except:
        return jsonify({'message': 'Payment failed!'}),500

def getLaporan():
    query = "SELECT count(*), convert(sum(jumlah_uang),char), month(tanggal_transaksi) FROM `transaction` WHERE year(tanggal_transaksi) = year(CURDATE()) group by month(tanggal_transaksi) order by month(tanggal_transaksi)"
    try: 
        plan = db.execute_sql(query)
        return jsonify({"laporan": plan}),200
    except:
        return jsonify({"message": "Failed!"}),400

def getLaporan2():
    query = "SELECT count(*), convert(sum(jumlah_uang),char), month(tanggal_transaksi) FROM `transaction` WHERE year(tanggal_transaksi) = year(CURDATE())-1 group by month(tanggal_transaksi)"
    try: 
        plan = db.execute_sql(query)
        return jsonify({"laporan": plan}),200
    except:
        return jsonify({"message": "Failed!"}),400
    