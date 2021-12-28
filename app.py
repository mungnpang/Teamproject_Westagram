from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.qjo3f.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbwesta

app = Flask(__name__)


@app.route('/')
def main():
    return render_template("index.html")

@app.route('/join')
def join():
    return render_template("join.html")

@app.route('/join', methods=['POST'])
def join_post():
    email = request.form['email']
    name = request.form['name']
    nickname = request.form['nickname']
    password = request.form['password']

    doc = {'email':email, 'name':name, 'nickname':nickname, 'password':password}

    db.users.insert_one(doc)

    return jsonify({'result':'success', 'msg':'가입 성공'})


@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/login', methods= ['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']

    temp_user = db.users.find_one({'email':email, 'password':password})
    if temp_user is not None:


    return jsonify({'result':'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)