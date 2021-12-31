from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from flask.wrappers import Response
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from uuid import uuid4
import jwt
import hashlib
import re
import os


client = MongoClient('mongodb+srv://test:sparta@cluster0.qjo3f.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbwesta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/media/"

SECRET_KEY = 'SPARTA'


def valid_token():
    token_receive = request.cookies.get('wetoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return "로그인 시간이 만료되었습니다"
    except jwt.exceptions.DecodeError:
        return "로그인 정보가 존재하지 않습니다."


def email_check(email):
    return bool(db.users.find_one({'email': email}))


# @app.route('/mypage', methods=['GET','POST'])
# def profile_img():
#     valid = valid_token()
#     if type(valid) == dict:
#         if request.method == 'GET':
#             return render_template('mypage.html')
#         else:
#             file = request.files['file']
#             img_name = uuid4().hex
#             file.save('./static/media/profile_img/' + img_name)
#             img_id = '../static/media/profile_img/' + img_name
#             db.users.update_one({'email':valid['id']}, {'$profile_img':img_id})
#             return jsonify({'result':'success'})
#     else:
#         return redirect(url_for('login'))


@app.route('/')
def main():
    valid = valid_token()
    if type(valid) == dict:
        feeds = list(db.feeds.find({}, {'_id':False, 'email':False}))
        feeds.reverse()
        return render_template('index.html', feeds=feeds)
    else:
        return redirect(url_for('login'))


@app.route('/api/feeds', methods=['POST'])
def upload_feed():
    valid = valid_token()
    file = request.files['file']
    img_name = uuid4().hex
    desc = request.form['desc']
    target = db.users.find_one({'email':valid['id']})
    profile_img = '../static/img/westagram-logo.jpg'

    file.save('./static/media/feeds/' + img_name)
    img_id = '../static/media/feeds/' + img_name

    doc = {'image_id': img_id, 'desc':desc, 'nickname':target['nickname'], 'profile_img':profile_img}
    db.feeds.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        # 회원가입 화면 이동
        return render_template('join.html')
    else:
        email = request.form['email']
        name = request.form['name']
        nickname = request.form['nickname']
        temp_password = request.form['password']
        password = hashlib.sha256(temp_password.encode('utf-8')).hexdigest()

        #이메일 유효성 검사
        if (re.search('[^a-zA-Z0-9-_.@]+', email) is not None
                or not (9 < len(email) < 26)):
            return jsonify({'result': 'error', 'msg': '휴대폰번호 또는 이메일의 형식을 확인해주세요. 영문과, 숫자, 일부 특수문자(.-_) 사용 가능. 10~25자 길이'})
        # 비밀번호 유효성 검사
        elif (re.search('[^a-zA-Z0-9!@#$%^&*]+', temp_password) is not None or
              not (7 < len(temp_password) < 21) or
              re.search('[0-9]+', temp_password) is None or
              re.search('[a-zA-Z]+', temp_password) is None):
            return jsonify({'result': 'error', 'msg': '비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 일부 특수문자(!@#$%^&*) 사용 가능. 8~20자 길이'})
        # 빈칸 검사
        elif not (email and name and nickname and temp_password):
            return jsonify({'result': 'error', 'msg': '빈칸을 입력해주세요.'})
        # 중복 이메일 검사
        elif email_check(email):
            return jsonify({'result': 'error', 'msg': '가입된 내역이 있습니다.'})
        doc = {'email':email, 'name':name, 'nickname':nickname, 'password':password}

        db.users.insert_one(doc)

        return jsonify({'result':'success', 'msg':'회원 가입을 축하드립니다!'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # 이미 토큰을 가지고 있는 상태에서 login으로 돌아오는 경우 메인으로 강제 귀환
        valid = valid_token()
        if type(valid) == dict:
            return redirect(url_for('main'))
        else:
            return render_template('login.html')
    else:
        email = request.form['email']
        temp_password = request.form['password']
        password = hashlib.sha256(temp_password.encode('utf-8')).hexdigest()

        temp_user = db.users.find_one({'email': email, 'password': password})

        if temp_user is not None:
            payload = {
                'id': email,
                'exp': datetime.utcnow() + timedelta(seconds=60 * 60)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            return jsonify({'result': 'success', 'token': token})
        else:
            return Response(status=401)


@app.route('/login', methods=['POST'])
def logout():
    return jsonify({'result': 'success'})




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)