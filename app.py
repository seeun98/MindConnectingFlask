from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import uuid

client = MongoClient('localhost', 27017)
db = client.mindConnecting

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        id = request.form['id']
        pw = request.form['password']

        memberInformation = {
            'id' : id,
            'password' : pw
        }

        #db의 아이디,비밀번호와 입력된 정보가 맞는지 확인




        return jsonify({'result':'success', 'msg' : 'login success'})

@app.route("/joinus", methods=['GET', 'POST'])
def joinus():
    if request.method == 'GET':
        return render_template('joinus.html')
    else:
        id = request.form['id']
        pw = request.form['password']
        email = request.form['email']
        is_student = request.form['is_student']
        department = request.form['department']

        information = {
            'id' : id,
            'password' : pw,
            'email' : email,
            'is_student' : is_student,
            'department' : department
        }
        print(information)
        db.member.insert_one(information)
        return render_template('login.html')




@app.route("/index", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/index", methods=['POST'])
def indexPost():
        # name = request.form['name']
        #
        # scheduleList = list(db.schedule.find({}))
        #
        #
        # for i in scheduleList:
        #     if name == scheduleList[i]['subject']:
        #         print(name)
        #         #여기의 code를 가져온다.
        #         #code에 맞는 professorCommunicate 페이지로 보내준다.
    return render_template("index.html")

# #professorCommunicate_list
# #시간표 누를 시 -> 그 code에 해당하는 메인페이지인(교수님 공지 게시판)이 나온다
# @app.route("/professorCommunicatelist/<code>", methods=['GET'])
# def professorCommunicatelist_get(code):
#     professorCommunicate_list = list(db.professorQuestion.find({'code': code},{'_id': 0}))
#     print(professorCommunicate_list)
#     return jsonify({'result':'success', 'items': professorCommunicate_list})
#
#
# @app.route("/professorCommunicate/<code>", methods=['GET'])
# def professorCommunicate(code):
#     return render_template("professorCommunicatelist.html", code=code)
#
# @app.route("/QuestionFrom", methods=['GET'])
# def QuestionForm():
#     return render_template("professorCommunicateQuestionForm.html")




#-----------------------------------------------------------------------------------------------------------------
#게시판 창구

@app.route("/communicate/<code>", methods=['GET'])
def communicate_page(code):
    return render_template('communicate.html', code=code)

@app.route("/communicate/<code>/list", methods=['GET'])
def communicate_list_get(code):
    communicate_list = list(db.communicate.find({'code': code}, {'_id': 0}))

    return jsonify({'result': 'success', 'items': communicate_list})


@app.route("/communicate", methods=['POST'])
def communicate_post():
    id = uuid.uuid4().hex
    code = request.form['code']
    title = request.form['title']
    content = request.form['content']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    communicateInfo = {
        'id': id,
        'code': code,
        'title' : title,
        'content' : content,
        'timestamp': timestamp
    }

    db.communicate.insert_one(communicateInfo)
    return jsonify({'result': 'success'})


@app.route("/review_page/<code>/<communicate_id>", methods=['GET'])
def review_page(code, communicate_id):
    return render_template("communicateRE.html", code = code, communicate_id = communicate_id)

# 댓글 구성요소
# id, communicate_id, content
#댓글 불러오기
@app.route("/review_page/<code>/<communicate_id>/comments", methods=['GET'])
def review_page_comments_list(communicate_id, comment_id, content):
    comment_list = list(db.comment.find({'communicate_id' : communicate_id, 'comment_id' : comment_id, 'content' : content}))
    return jsonify({'result': 'success', 'items': comments_list })

#댓글 등록 누를때 댓글 데이터베이스에 저장하기
@app.route("/comment", methods=['POST'])
def comment_page_post():
    comment_id = uuid.uuid4().hex
    code = request.form['code']
    communicate_id = request.form['communicate_id']
    content = request.form['content']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    communicateCommentInfo ={
        'comment_id' : comment_id,
        'communicate_id' : communicate_id,
        'code' : code,
        'content' : content,
        'timestamp' : timestamp
    }

    db.communicateComment.insert_one(communicateCommentInfo)
    return jsonify({'result': 'success'})

#댓글 등록 누를때 댓글 데이터베이스에 저장하기
@app.route("/comment/<communicate_id>", methods=['GET'])
def comment_page_get(communicate_id):
    found_comments = list(db.communicateComment.find({'communicate_id': communicate_id}, {'_id': False}))
    return jsonify({'result': 'success', 'items': found_comments})

#------댓글 페이지--------------
#게시글 하나 눌렀을때 -> 그 게시글에 대한 댓글 페이지로 넘어감
#1. 그 게시글에 대한 페이지 보여주기
#2. 댓글등록 누르면 디비에 저장 후 페이지 새로고침
#@app.route("/communicate/<code>/REcomments", methods="POST")
#def communicateREcomments():


if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)