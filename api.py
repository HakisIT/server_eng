from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask, Response, request, json, redirect, url_for, render_template, jsonify
from flask_restful import Api, Resource
import mysql.connector
from flask_cors import CORS
import random
import json
import hashlib

HOST = '192.168.1.35'
PORT = 9999

app = Flask(__name__)

CORS(app)
api = Api()

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12312q',
    port='3306',
    database='english_words',
)
mycursor = mydb.cursor()


def selection_id(word_id):
    sql_select_query = """SELECT * FROM main WHERE id = %s"""
    mycursor.execute(sql_select_query, (word_id,))
    word1 = mycursor.fetchall()
    dct = {word1[0][0]:[word1[0][1], word1[0][2], word1[0][3]]}
    return Response(str(dct), content_type='text/html; charset=utf-8')


def select_main():
    mycursor = mydb.cursor()
    mycursor.execute('SELECT id FROM main')
    words = mycursor.fetchall()
    id_lst = []
    for i in words:
        id_lst.append(i[0])
    return id_lst


def selection_word():
    sql_select_query = "SELECT english FROM main"
    mycursor.execute(sql_select_query)
    words = mycursor.fetchall()
    wrd = []
    for i in words:
        wrd.append(i[0][:-1])
    return wrd

def user_info():
    sql_select_query = "SELECT * FROM user_info"
    mycursor.execute(sql_select_query)
    users = mycursor.fetchall()
    user_info = {}
    for i in users:
        user_info.update({i[0]:[i[1], i[2], i[3]]})
    return user_info

def users_list():
    sql_select_query = "SELECT user_name FROM user_info"
    mycursor.execute(sql_select_query)
    users = mycursor.fetchall()
    users_lst = []
    for i in users:
        users_lst.append(i[0])
    return users_lst

def validate_word(data):
    # check is digit in data
    if any(char.isdigit() for char in data['english']) or any(char.isdigit() for char in data['russian']) or any(char.isdigit() for char in data['czech']):
        print('number validate')
        return False

    if data['english'] == '' or data['russian'] == '' or data['czech'] == '':
        print('empty validate')
        return False
    return True


def add_new_word(rcv_data):
    print('rcv_data', rcv_data)

    if validate_word(rcv_data) == True:
        sql_insert_query = """INSERT INTO main (english, russian, chech) 
                                    VALUES (%s, %s, %s)"""
        tuple1 = (rcv_data['english'], rcv_data['russian'], rcv_data['czech'])
        mycursor.execute(sql_insert_query, tuple1)
        mydb.commit()
        return True
    else:
        return False
    

def validate_regist(data):    
    if data['user'] not in users_list():
        if data['user'] == '' or data['password'] == '' or data['email'] == '':
            return 'Fill in all the blanks'
        else:
            return True
        

def validate_autoriz(data):
    if data['user'] in users_list():
        if data['user'] == '' or data['password'] == '':
            return 'Fill in all the blanks'
        else:
            return True


def hash_password(data):
    data_json = json.dumps(data)
    return hashlib.sha256(data_json.encode('utf-8')).hexdigest()


def add_new_user(rcv_data):
    if hash_password(rcv_data) != '' and validate_regist(rcv_data) == True:
        hash_pass = hash_password(rcv_data['password'])
        sql_insert_query = """INSERT INTO user_info (user_name, password, email) 
                                    VALUES (%s, %s, %s)"""
        tuple1 = (rcv_data['user'], hash_pass, rcv_data['email'])
        mycursor.execute(sql_insert_query, tuple1)
        mydb.commit()
        return True
    
    elif validate_regist(rcv_data) == 'Fill in all the blanks':
        return 'Fill in all the blanks'
    else:
        return False


def login(rcv_data):
    if hash_password(rcv_data) != '' and validate_autoriz(rcv_data) == True:
        
        return True
    
    elif validate_autoriz(rcv_data) == 'Fill in all the blanks':
        return 'Fill in all the blanks'
    else:
        return False

# class Main(Resource):
#     def get(self, word_id):
#         return selection_id(word_id)

@app.route('/search/<word>')
def search_text(word):
    if word in selection_word():
        return {'data': 'success'}
    else:
        return 'page not found'
    

@app.route('/words/<int:word_id>')
def get(word_id):
    return selection_id(word_id)


@app.route('/add', methods=['POST'])
def process_data():
    if request.method=='POST':
        if request.data:
            rcv_data = json.loads(request.data.decode(encoding='utf-8'))

            if add_new_word(rcv_data) == True:
                return jsonify({'data': 'success'})
            else:
                return jsonify({'data': {'success': 'fail'}})
            

@app.route('/registration', methods=['POST'])
def regist():
    if request.data:
        rcv_data = json.loads(request.data.decode(encoding='utf-8'))
        print('POST rcv_data', rcv_data)

        if add_new_user(rcv_data) == True:
            return jsonify('Success registation !')
        
        elif add_new_user(rcv_data) == 'Fill in all the blanks':
            return jsonify('Fill in all the blanks')
        
        else:
            return jsonify('This user already exists')
            
@app.route('/authorization', methods=['POST'])
def autoriz():
    if request.data:
        rcv_data = json.loads(request.data.decode(encoding='utf-8'))

        if add_new_user(rcv_data) == True:
            return jsonify('Success authorization !')
        
        elif add_new_user(rcv_data) == 'Fill in all the blanks':
            return jsonify('Fill in all the blanks')
        
        else:
            return jsonify('This user does not exist')


@app.route('/<usr>')
def user(usr):
    return f"<h1>{'Success add '+ usr}</h1>"


@app.route('/random')
def random_id():
    rnd_id = random.choice(select_main())
    return selection_id(rnd_id)



if __name__ == '__main__':
    app.run(debug=True, port=9999, host="192.168.1.35")