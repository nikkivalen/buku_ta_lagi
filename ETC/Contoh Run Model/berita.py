from logging import error
from server import jsonify
from server import db
from server import helper
import datetime
from server.models import ner
from server.models import history

# pagination
def pagination(kategori,search):
    query = "select count(*) from (SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score, 0 as score1 FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and lower(b.isi_berita) like %s UNION ALL SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, 0 as score, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score1 FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) != 0 and b.id_berita not in (SELECT id_berita from (SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and lower(b.isi_berita) like %s) t1) order by score desc,score1 desc, tanggal_berita desc) t2"
    query_data = [search, '%' + kategori + '%' ,'%' + search + '%',search,'%' + kategori + '%', search, search,'%' + kategori + '%','%' + search + '%' ]
    try: 
        jum_berita = db.execute_sql(query,query_data)
        if len(jum_berita) > 0:
            return jsonify({"pagination": jum_berita[0]}),200
        else:
            return jsonify({"pagination": 0}),200
    except:
        return jsonify({"message": "Error"}),400

def mypagination(search,email):
    query = "SELECT count(*) FROM BERITA b WHERE lower(b.judul_berita) like lower(%s) and b.edited_by = %s"
    query_data = ['%' + search + '%', email]
    try: 
        jum_berita = db.execute_sql(query,query_data)
        if len(jum_berita) > 0:
            return jsonify({"pagination": jum_berita[0]}),200
        else:
            return jsonify({"pagination": 0}),200
    except:
        jum_berita = db.execute_sql(query,query_data)
        return jsonify({"message": "Error"}),400

# select kategori
def selectKategori():
    query = "SELECT * from kategori"
    try: 
        kategori = db.execute_sql(query)
        return jsonify({"kategori": kategori}),200
    except:
        kategori = db.execute_sql(query)
        return jsonify({"message": "Failed!"}),400

# select berita
def selectById(data):
    query = "SELECT b.id_berita,b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.kategori_berita, b.ner  FROM BERITA b, KATEGORI k WHERE b.kategori_berita = k.id_kategori and id_berita = %s"
    query_data = [data]
    try: 
        berita = db.execute_sql(query,query_data)
        return jsonify({"berita": berita}),200
    except:
        return jsonify({"message": "Failed!"}),400


# select All berita
def selectAll(kategori, offset,search):
    query = "SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score, 0 as score1 FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and lower(b.isi_berita) like %s UNION ALL SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, 0 as score, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score1 FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) != 0 and b.id_berita not in (SELECT id_berita from (SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and lower(b.isi_berita) like %s) t1) order by score desc,score1 desc, tanggal_berita desc LIMIT 10 OFFSET %s"
    query_data = [search, '%' + kategori + '%' ,'%' + search + '%',search,'%' + kategori + '%', search, search,'%' + kategori + '%','%' + search + '%' ,int(offset)]
    try: 
        berita = db.execute_sql(query,query_data)
        
        if len(berita) > 0:
            return jsonify({"berita": berita}),200
        else:
            return jsonify({"berita": "Tidak ada berita ditemukan"}),404
    except:
        return jsonify({"message": "Failed!"}),400

def selectAllwithHistory(kategori, offset,search,email):
    query = "SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score, 0 as score1 FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and lower(b.isi_berita) like %s UNION ALL SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, 0 as score, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score1 FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) != 0 and b.id_berita not in (SELECT id_berita from (SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by, b.ner, MATCH(b.isi_berita) AGAINST (%s IN NATURAL LANGUAGE MODE) AS score FROM  BERITA b, KATEGORI k where b.kategori_berita = k.id_kategori and lower(k.nama_kategori) like %s and lower(b.isi_berita) like %s) t1) order by score desc,score1 desc, tanggal_berita desc LIMIT 10 OFFSET %s"
    query_data = [search, '%' + kategori + '%' ,'%' + search + '%',search,'%' + kategori + '%', search, search,'%' + kategori + '%','%' + search + '%' ,int(offset)]
    try: 
        berita = db.execute_sql(query,query_data)
        if search != '':

            hasil = history.addHistory(search,email)
            print(hasil)
        if len(berita) > 0:
            return jsonify({"berita": berita}),200
        else:
            return jsonify({"berita": "Tidak ada berita ditemukan"}),404
    except:
        return jsonify({"message": "Failed!"}),400

def selectBeritabyUser( offset,search,email):
    query = "SELECT b.id_berita, rpad(substring(b.judul_berita,1,100),103, '.'), b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by FROM BERITA b, KATEGORI k WHERE b.kategori_berita = k.id_kategori AND lower(judul_berita) like lower(%s) and lower(b.edited_by) = lower(%s) order by b.tanggal_berita desc LIMIT 10 OFFSET %s "
    query_data = ['%' + search + '%',email,int(offset)]
    try: 
        berita = db.execute_sql(query,query_data)
        if len(berita) > 0:
            return jsonify({"berita": berita}),200
        else:
            return jsonify({"berita": "Tidak ada berita ditemukan"}),404
    except:
        return jsonify({"message": "Failed!"}),400

#Add Berita
def addBerita(data,email):
    now = helper.get_current_time()
    list_hasil = ner.nested_ner_berita(data['isi'])
    nner = ""
    if (list_hasil is not None):
        for i in list_hasil:
            nner += i['entity'] + ":" + str(i["kata"]) + ";"
    else:
        nner = "None"
    query = "INSERT INTO BERITA VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    query_data = [data['judul'],helper.strtodate2(data['tanggal']),data['sumber'],data['tempat'],data['kategori'],data['isi'],now,now,email, nner]
    try:
        db.execute_query(query,query_data)
        return jsonify({"message" : "Insert success"}),201
    except:
        db.execute_query(query,query_data)
        return jsonify({"message" : "Failed"}),400

#update Berita
def updateBerita(data,id):
    now = helper.get_current_time()
    list_hasil = ner.nested_ner_berita(data['isi'])
    nner = ""
    if (list_hasil is not None):
        for i in list_hasil:
            nner += i['entity'] + ":" + str(i["kata"]) + ";"
    else:
        nner = "None"
    query = "UPDATE BERITA SET judul_berita = %s, tanggal_berita = %s, sumber_berita = %s, tempat_berita = %s, kategori_berita = %s, isi_berita = %s, updated_at = %s, ner = %s where id_berita = %s"
    query_data = [data['judul'],helper.strtodate2(data['tanggal']),data['sumber'],data['tempat'],data['kategori'],data['isi'],now,nner,id]
    try:
        db.execute_query(query,query_data)
        return jsonify({"message" : "Update success"}),200
    except:
        return jsonify({"message" : "Failed"}),400

#delete Berita
def deleteBerita(id):
    query = "DELETE from BERITA where id_berita = %s"
    query_data = [id]
    try:
        db.execute_query(query,query_data)
        return jsonify({"message" : "Delete success"}),200
    except:
        return jsonify({"message" : "Failed"}),400

# getBeritaAdmin
def getBeritaAdmin (email, offset):
    query = "SELECT b.id_berita, b.judul_berita, b.tanggal_berita, b.sumber_berita,b.tempat_berita, k.nama_kategori,b.isi_berita,b.crawl_at,b.updated_at, b.edited_by FROM BERITA b, KATEGORI k WHERE b.kategori_berita = k.id_kategori AND lower(b.edited_by) = lower(%s) LIMIT 10 OFFSET %s"
    query_data = [email,int(offset)]
    try: 
        berita = db.execute_sql(query,query_data)
        if len(berita) > 0:
            return jsonify({"berita": berita}),200
        else:
            return jsonify({"berita": "Tidak ada berita ditemukan"}),404
    except:
        berita = db.execute_sql(query,query_data)
        return jsonify({"message": "Failed!"}),400


def updateNER(data, id):
    query = "UPDATE BERITA SET ner = %s where id_berita = %s"
    query_data = [data['ner'], id]
    try:
        db.execute_query(query,query_data)
        return jsonify({"message" : "Update success"}),200
    except:
        return jsonify({"message" : "Failed"}),400
