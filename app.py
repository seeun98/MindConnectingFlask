from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import flask_admin
import uuid
from flask_admin.contrib.pymongo import ModelView

client = MongoClient('localhost', 27017)
db = client.mindConnecting

app = Flask(__name__)
#set optional bootwatch theme

@app.route("/")
def home():
    return render_template('index.html')

# @app.route("/professorIndex", methods=['GET'])
# def professorHome():
#     return render_template("professorIndex.html")

@app.route("/professorOfficeForm", methods=['GET'])
def professorOfficeForm():
    return render_template("professorOfficeForm.html")

@app.route("/professorStatus", methods=['POST'])
def professorStatus():
    name = request.form['name']
    status1 = request.form['status1']
    status2 = request.form['status2']
    status3 = request.form['status3']
    status4 = request.form['status4']

    professorStatusInfo = {
        'name' : name,
        'status1' : status1,
        'status2' : status2,
        'status3' : status3,
        'status4' : status4

    }
    db.professorStatus.insert_one(professorStatusInfo)
    return jsonify({'result':'success','msg':'교수님 상태 입력 성공'})

@app.route("/login", methods=['GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')



@app.route("/login_post", methods=['POST'])
def login_post():
    ids = request.form['id']
    pws = request.form['password']

    loginInfo = db.member.find_one({'id': ids, 'password' : pws}, {'is_student' : 1, '_id':0})
    print(loginInfo)
    if loginInfo is None:
        return jsonify({'result':'fail','msg':'로그인 실패'})
    else:
        return jsonify({'result':'success','msg':'로그인 성공','item':loginInfo})


@app.route("/joinus", methods=['GET', 'POST'])
def joinus():
    if request.method == 'GET':
        return render_template('joinus.html')
    else:
        id = request.form['id']
        pw = request.form['password']
        name = request.form['name']
        email = request.form['email']
        is_student = request.form['is_student']
        department = request.form['department']

        information = {
            'id' : id,
            'password' : pw,
            'name' : name,
            'email' : email,
            'is_student' : is_student,
            'department' : department
        }
        print(information)
        db.member.insert_one(information)
        return render_template('login.html')



@app.route("/professorIndexList", methods=['GET'])
def index_get():
    return render_template("professorIndex.html")

@app.route("/professorIndex", methods=['GET'])
def schedule_list():
    schedules_list = [x for x in list(db.schedule.find({},{'_id':0, 'subject':1, 'professor':1, 'time_location':1, 'code':1}))]
    # print(schedules_list)
    professor_status_list = [x for x in list(db.professorStatus.find({},{'_id':0}))]
    for psl in professor_status_list:
        # psl은 교수님 재실 상태 데이터
        for sc in schedules_list:
            if psl.get('name') == sc.get('professor'):
                sc['status1'] = psl.get('status1')
                sc['status2'] = psl.get('status2')
                sc['status3'] = psl.get('status3')
                sc['status4'] = psl.get('status4')

    # 재실 데이터가져오기
    # 재실 데이터 vs 스케쥴 리스트 데이터비
    # 비교 후, 해당하는 교수님 데이터에 새로운 key값 추가하기
    return jsonify({'result': 'success', 'items': schedules_list})

@app.route("/index", methods=['POST'])
def indexPost():
    return render_template("index.html")


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
# 댓글 한 요소 들고 오기

@app.route("/review_page/<code>/<communicate_id>/element", methods=['GET'])
def element(code, communicate_id):
    element_list = list(db.communicate.find({'code': code, 'communicate_id' : communicate_id},{'_id':0}))
    print(element_list)
    return jsonify({'result' : 'success', 'items' : element_list})

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
    # print(communicate_id)
    found_comments = list(db.communicateComment.find({'code': communicate_id},{'_id':0}))
    # print(found_comments)
    return jsonify({'result': 'success', 'items': found_comments})





if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)