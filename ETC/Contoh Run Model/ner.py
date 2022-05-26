from logging import error
from typing import Mapping
from server import jsonify
from server import db,app
from server import helper
from server.models import test
from flask import redirect
import jwt
import numpy as np
from datetime import datetime, timedelta
import os
import time

# path_config = 'D:/SEMESTER_6/TA\website/nested_ner/server/server/models/config'

def getFile(tipe):
    dir_name = 'D:/SEMESTER_6/TA\website/nested_ner/server/model/'
    # Get list of all files only in the given directory
    list_of_files = filter( lambda x: os.path.isfile(os.path.join(dir_name, x)),
                            os.listdir(dir_name) )
    # Sort list of files based on last modification time in ascending order
    list_of_files = sorted( list_of_files,
                            key = lambda x: os.path.getmtime(os.path.join(dir_name, x)), reverse=True
                            )
    # Iterate over sorted list of files and print file path 
    # along with last modification time of file 
    for file_name in list_of_files:
        file_path = os.path.join(dir_name, file_name)
        timestamp_str = time.strftime(  '%m/%d/%Y :: %H:%M:%S',
                                    time.gmtime(os.path.getmtime(file_path))) 
        print(timestamp_str, ' -->', file_name)
    if tipe == 1:
        return jsonify({"file": list_of_files}),200
    else: 
        return list_of_files

def submit(file_baru): 
    dir_name = 'D:/SEMESTER_6/TA\website/nested_ner/server/model/'
    file = getFile(0)
    try:
        if (file_baru in file):

            for file_name in file:
                if '#' in file_name:
                    nama_baru = file_name[0:14]
                    old_file = os.path.join(dir_name, file_name)
                    new_file = os.path.join(dir_name, nama_baru)
            os.rename(old_file, new_file)
            old_file = os.path.join(dir_name, file_baru)
            new_file = os.path.join(dir_name, file_baru + "#") 
            os.rename(old_file, new_file)
            return jsonify({"message": "Change Model Success"}),200
        else:
            return jsonify({"message": "Change Model Error"}),400
    except:
        return jsonify({"message": "Change Model Error"}),400 

def getMapping(file_model):
    dir_name = 'D:/SEMESTER_6/TA\website/nested_ner/server/evaluation/'
    # Get list of all files only in the given directory
    list_of_files = filter( lambda x: os.path.isfile(os.path.join(dir_name, x)),
                            os.listdir(dir_name) )
    # Sort list of files based on last modification time in ascending order
    list_of_files = sorted( list_of_files,
                            key = lambda x: os.path.getmtime(os.path.join(dir_name, x)), reverse=True
                            )
    # Iterate over sorted list of files and print file path 
    # along with last modification time of file 
    for file_name in list_of_files:
        file_path = os.path.join(dir_name, file_name)
        timestamp_str = time.strftime(  '%m/%d/%Y :: %H:%M:%S',
                                    time.gmtime(os.path.getmtime(file_path))) 
        print(timestamp_str, ' -->', file_name)    
    tanggal = file_model[6:14]
    mapping = ""
    for file_name in list_of_files:
        if tanggal in file_name:
            mapping = dir_name+file_name
    if mapping != "":
        return mapping
    else:
        return "error"

def getConfig(file_model):
    dir_name = 'D:/SEMESTER_6/TA\website/nested_ner/server/server/models/config/'
    # Get list of all files only in the given directory
    list_of_files = filter( lambda x: os.path.isfile(os.path.join(dir_name, x)),
                            os.listdir(dir_name) )
    # Sort list of files based on last modification time in ascending order
    list_of_files = sorted( list_of_files,
                            key = lambda x: os.path.getmtime(os.path.join(dir_name, x)), reverse=True
                            )
    # Iterate over sorted list of files and print file path 
    # along with last modification time of file 
    for file_name in list_of_files:
        file_path = os.path.join(dir_name, file_name)
        timestamp_str = time.strftime(  '%m/%d/%Y :: %H:%M:%S',
                                    time.gmtime(os.path.getmtime(file_path))) 
        print(timestamp_str, ' -->', file_name)    
    tanggal = file_model[6:14]
    config = ""
    for file_name in list_of_files:
        if tanggal in file_name:
            config = dir_name+file_name
    if config != "":
        return config
    else:
        return "error"

def nested_ner_berita(sentences):
    dir_name = 'D:/SEMESTER_6/TA\website/nested_ner/server/model/'
    file = getFile(0)
    path_model = ""
    path_mapping = ""
    path_config = ""
    try:
        for file_name in file:
            if '#' in file_name:
                path_model = os.path.join(dir_name, file_name)
                path_mapping = getMapping(file_name)
                path_config = getConfig(file_name)
        
        if path_model != "" and path_mapping != 'error':
            list_hasil = test.main(path_config, path_model, path_mapping, sentences)
            
            list_hasil = sorted(list_hasil, key =lambda kv:(len(kv['kata'])))
            seen_titles = set()
            new_list = []
            for obj in list_hasil:
                if obj['kata'] not in seen_titles:
                    new_list.append(obj)
                    seen_titles.add(obj['kata'])
            return new_list
    except: 
        return None

def nested_ner(sentences,tipe):
    dir_name = 'D:/SEMESTER_6/TA\website/nested_ner/server/model/'
    file = getFile(0)
    path_model = ""
    path_mapping = ""
    path_config = ""
    try:
        for file_name in file:
            if '#' in file_name:
                path_model = os.path.join(dir_name, file_name)
                path_mapping = getMapping(file_name)
                path_config = getConfig(file_name)
        
        if path_model != "" and path_mapping != 'error':
            list_hasil = test.main(path_config, path_model, path_mapping, sentences)
            list_hasil = sorted(list_hasil, key =lambda kv:(len(kv['kata'])))
            message = ""
            if (tipe =="free"):
                message = "Upgrade Your Account Now !"
            elif (tipe=="premium"): 
                message = "Thanks for Upgrading Your Account !"
            seen_titles = set()
            new_list = []
            for obj in list_hasil:
                if obj['kata'] not in seen_titles:
                    new_list.append(obj)
                    seen_titles.add(obj['kata'])
            return jsonify({"list_hasil": new_list, "message": message}),200
        else:
            return jsonify({"message": "Model Not Found"}),404
    except: 
        # list_hasil = test.main(path_config, path_model, path_mapping, sentences)
        # print(sorted(list_hasil, key =lambda kv:(len(kv['kata'])))) 
        return jsonify({"message": "Process Nested NER Error"}),400 

def nested_ner_brat(sentences):
    dir_name = 'D:/SEMESTER_6/TA\website/nested_ner/server/model/'
    save_path_txt = 'D:/SEMESTER_6/TA/brat_new/brat-master/data/hasil_tes/output.txt'
    save_path_ann = 'D:/SEMESTER_6/TA/brat_new/brat-master/data/hasil_tes/output.ann'
    file = getFile(0)
    path_model = ""
    path_mapping = ""
    path_config = ""
    try:
        for file_name in file:
            if '#' in file_name:
                path_model = os.path.join(dir_name, file_name)
                path_mapping = getMapping(file_name)
                path_config = getConfig(file_name)
        
        if path_model != "" and path_mapping != 'error':
            sentences = np.char.replace(sentences, '.', ' ' + '.')
            sentences = str(sentences).split(" ")
            sentences = ' '.join(filter(None, sentences))
            list_hasil = test.main(path_config, path_model, path_mapping, str(sentences),1)
            file1 = open(save_path_txt, "w")
            file1.write(str(sentences))
            file1.close()
            file2 = open(save_path_ann, "w")
            angka = 0
            for i in list_hasil:
                index = "T" + str(angka)
                entity = i["entity"] + " " + str(i["index_awal"]) + " " + str(i["index_akhir"])
                file2.write(f'{index}\t{entity}\t{i["kata"]}\n')
                angka = angka + 1
            file2.close()
            
            return jsonify({"message": list_hasil}),200 
    except: 

        sentences = np.char.replace(sentences, '.', ' ' + '.')
        sentences = str(sentences).split(" ")
        sentences = ' '.join(filter(None, sentences))
        list_hasil = test.main(path_config, path_model, path_mapping, str(sentences),1)
        file1 = open(save_path_txt, "w")
        file1.write(str(sentences))
        file1.close()
        file2 = open(save_path_ann, "w")
        angka = 0
        for i in list_hasil:
            index = "T" + str(angka)
            entity = i["entity"] + " " + str(i["index_awal"]) + " " + str(i["index_akhir"])
            file2.write(f'{index}\t{entity}\t{i["kata"]}\n')
            angka = angka + 1
        file2.close()
        
        return jsonify({"message": "Process Nested NER Error"}),400 

def nested_nersearch(sentences,tipe):
    dir_name = 'D:/SEMESTER_6/TA\website/nested_ner/server/model/'
    file = getFile(0)
    path_model = ""
    path_mapping = ""
    path_config = ""
    try:
        for file_name in file:
            if '#' in file_name:
                path_model = os.path.join(dir_name, file_name)
                path_mapping = getMapping(file_name)
                path_config = getConfig(file_name)
        
        if path_model != "" and path_mapping != 'error':
            list_hasil = test.main(path_config, path_model, path_mapping, sentences)
            message = ""
            if (tipe =="free"):
                message = "Upgrade Your Account Now !"
            elif (tipe=="premium"): 
                message = "Thanks for Upgrading Your Account !"
            seen_titles = set()
            new_list = []
            for obj in list_hasil:
                if obj['kata'] not in seen_titles and obj['kata'] != sentences:
                    new_list.append(obj)
                    seen_titles.add(obj['kata'])
            return jsonify({"list_hasil": new_list, "message": message}),200
        else:
            return jsonify({"message": "Model Not Found"}),404
    except:
        return jsonify({"message": "Process Nested NER Error"}),400 