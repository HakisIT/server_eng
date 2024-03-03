from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask, Response, request, json, redirect, url_for, render_template, jsonify
from flask_restful import Api, Resource
import mysql.connector
from flask_cors import CORS
import requests
import json

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

def selection_word():
    sql_select_query = "SELECT english FROM main"
    mycursor.execute(sql_select_query)
    words = mycursor.fetchall()
    wrd = []
    for i in words:
        wrd.append(i[0][:-1])
    return wrd

def validate(data):
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

    if validate(rcv_data) == True:
        sql_insert_query = """INSERT INTO main (english, russian, chech) 
                                    VALUES (%s, %s, %s)"""
        tuple1 = (rcv_data['english'], rcv_data['russian'], rcv_data['czech'])
        mycursor.execute(sql_insert_query, tuple1)
        mydb.commit()
        return True
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
            print('POST rcv_data', rcv_data)
            data_success = {'data': 'success'}
            data_fail = {'data': {'success': 'fail'}}

            if add_new_word(rcv_data) == True:
                print("true", data_success)
                return jsonify(data_success)
            else:
                print("false", data_fail)
                return jsonify(data_fail)
            
    # else:
    #     return render_template('index.html')

@app.route('/<usr>')
def user(usr):
    return f"<h1>{'Success add '+ usr}</h1>"


if __name__ == '__main__':
    app.run(debug=True, port=9999, host="192.168.1.35")
