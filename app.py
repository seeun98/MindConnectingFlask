from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime



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
        #         #여기의 class_id를 가져온다.
        #         #class_id에 맞는 professorCommunicate 페이지로 보내준다.
    return render_template("index.html")

# #professorCommunicate_list
# #시간표 누를 시 -> 그 class_id에 해당하는 메인페이지인(교수님 공지 게시판)이 나온다
# @app.route("/professorCommunicatelist/<class_id>", methods=['GET'])
# def professorCommunicatelist_get(class_id):
#     professorCommunicate_list = list(db.professorQuestion.find({'class_id': class_id},{'_id': 0}))
#     print(professorCommunicate_list)
#     return jsonify({'result':'success', 'items': professorCommunicate_list})
#
#
# @app.route("/professorCommunicate/<class_id>", methods=['GET'])
# def professorCommunicate(class_id):
#     return render_template("professorCommunicatelist.html", class_id=class_id)
#
# @app.route("/QuestionFrom", methods=['GET'])
# def QuestionForm():
#     return render_template("professorCommunicateQuestionForm.html")




#-----------------------------------------------------------------------------------------------------------------
#게시판 창구

@app.route("/communicate/<class_id>", methods=['GET'])
def communicate_page(class_id):
    return render_template('communicate.html', class_id=class_id)

@app.route("/communicate/<class_id>/list", methods=['GET'])
def communicate_list_get(class_id):
    communicate_list = list(db.communicate.find({'class_id': class_id}, {'_id': 0}))

    return jsonify({'result': 'success', 'items': communicate_list})



@app.route("/communicate", methods=['POST'])
def communicate_post():
    class_id = request.form['class_id']
    title = request.form['title']
    content = request.form['content']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    communicateInfo = {
        'class_id': class_id,
        'title' : title,
        'content' : content,
        'timestamp': timestamp
    }

    db.communicate.insert_one(communicateInfo)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)