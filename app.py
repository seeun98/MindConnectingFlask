from flask import Flask, render_template, request, jsonify, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from pymongo import MongoClient

from datetime import datetime
from forms import UserCreateForm, UserLoginForm, ProfessorOfficeForm, CommunicateForm

import config

client = MongoClient('localhost', 27017)
db = client.mindConnecting

app = Flask(__name__)
app.config.from_object(config)


@app.route("/")
def home():
    return redirect(url_for('schedule_index'))


@app.route("/professor/addStatus", methods=['GET', 'POST'])
def professor_office_form():
    form = ProfessorOfficeForm()
    if request.method == 'POST':
        professor = db.member.find_one({'name': form.name.data, 'is_student': 'Professor'})
        if professor:
            info = {
                'name': form.name.data,
                'status': form.status.data
            }
            db.professorStatus.delete_many({'name': info['name']})
            db.professorStatus.insert_one(info)
            return redirect(url_for('home'))
        else:
            flash("이름이 교수님 데이터베이스에 없습니다.")

    return render_template("professorOfficeForm.html", form=form)


@app.route("/schedule", methods=['GET'])
def schedule_index():
    schedule_list = list(db.schedule.find({},
                                          {'_id': 0,
                                           'subject': 1,
                                           'professor': 1,
                                           'time_location': 1,
                                           'code': 1}))
    professor_status_list = list(db.professorStatus.find({}, {'_id': 0}))
    professor_status_dict = {item.get('name'): item.get('status')
                             for item in professor_status_list}

    color_dict = {
        '재실': 'success',  # 초록
        '퇴근': 'danger',  # 빨강
        '연구중': 'warning',  # 노랑
        '휴식중': 'secondary',  # 회색
    }

    print(professor_status_dict)
    for sc in schedule_list:
        sc['status'] = professor_status_dict.get(sc['professor'], None)
        sc['color'] = color_dict.get(sc['status'], '')
    # 재실 데이터가져오기
    # 재실 데이터 vs 스케쥴 리스트 데이터비
    # 비교 후, 해당하는 교수님 데이터에 새로운 key 값 추가하기
    print(schedule_list)
    return render_template("professorIndex.html", schedule_list=schedule_list)


# -----------------------------------------------------------------------------------------------------------------
# auth 인증


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = UserLoginForm()

    if request.method == 'POST':
        error = None
        user = db.member.find_one({'id': form.userid.data})
        print(user)
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user['password'], form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        flash(error)

    return render_template('login.html', form=form)


@app.route("/joinus", methods=['GET', 'POST'])
def joinus():
    form = UserCreateForm()
    if request.method == 'POST':
        user = db.member.find_one({'id': form.userid.data})
        if not user:
            user = {
                'id': form.userid.data,
                'password': generate_password_hash(form.password1.data),
                'name': form.name.data,
                'email': form.email.data,
                'is_student': form.is_student.data,
                'department': form.department.data
            }
            print(user)
            db.member.insert_one(user)
            return redirect(url_for('login'))
        else:
            flash('이미 존재하는 사용자입니다.')

    return render_template('joinus.html', form=form)


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.member.find_one({'id': user_id})['name']


@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('home'))


# -----------------------------------------------------------------------------------------------------------------
# 게시판 창구


@app.route("/communicate/<code>", methods=['GET', 'POST'])
def communicate_page(code):
    form = CommunicateForm()
    if request.method == 'POST':
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        info = {
            'code': code,
            'title': form.title.data,
            'content': form.content.data,
            'timestamp': timestamp
        }

        db.communicate.insert_one(info)

    communicate_list = list(db.communicate.find({'code': code}, {'_id': 0}))
    return render_template('communicate.html', communicate_list=communicate_list, form=form)


@app.route("/review_page/<code>/<communicate_id>", methods=['GET'])
def review_page(code, communicate_id):
    return render_template("communicateRE.html", code=code, communicate_id=communicate_id)


# 댓글 구성요소
# id, communicate_id, content
# 댓글 한 요소 들고 오기
@app.route("/review_page/<code>/<communicate_id>/element", methods=['GET'])
def element(code, communicate_id):
    element_list = list(db.communicate.find({'code': code, 'communicate_id': communicate_id}, {'_id': 0}))
    print(element_list)
    return jsonify({'result': 'success', 'items': element_list})


# 댓글 불러오기
@app.route("/review_page/<code>/<communicate_id>/comments", methods=['GET'])
def review_page_comments_list(communicate_id, comment_id, content):
    comments_list = list(
        db.comment.find({'communicate_id': communicate_id, 'comment_id': comment_id, 'content': content}))
    return jsonify({'result': 'success', 'items': comments_list})


# 댓글 등록 누를때 댓글 데이터베이스에 저장하기
@app.route("/comment", methods=['POST'])
def comment_page_post():
    code = request.form['code']
    communicate_id = request.form['communicate_id']
    content = request.form['content']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    info = {
        'communicate_id': communicate_id,
        'code': code,
        'content': content,
        'timestamp': timestamp
    }

    db.communicateComment.insert_one(info)
    return jsonify({'result': 'success'})


# 댓글 등록 누를때 댓글 데이터베이스에 저장하기
@app.route("/comment/<communicate_id>", methods=['GET'])
def comment_page_get(communicate_id):
    # print(communicate_id)
    found_comments = list(db.communicateComment.find({'code': communicate_id}, {'_id': 0}))
    # print(found_comments)
    return jsonify({'result': 'success', 'items': found_comments})


@app.route("/search_post", methods=['POST'])
def search_post():
    select_option = request.form['select_option']
    what = request.form['what']

    print(select_option)
    print(what)
    result = None
    if select_option == 'sbjNm':
        result = db.schedule.find_one({'subject': what})
    elif select_option == 'profNm':
        result = db.schedule.find_one({'professor': what})

    print(result)
    if result is None:
        return jsonify({'result': 'fail', 'msg': '검색 실패'})
    else:
        return jsonify({'result': 'success', 'msg': '검색 성공', 'item': result})


@app.route("/select_subject", methods=['GET', 'POST'])
def select_subject():
    if request.method == 'GET':
        # timeT = getTimeTable()
        print("ㅏㅏㅏ")
        # print(timeT)
        return render_template('select_subject.html')
    else:
        # select = request.form['select']
        # search = request.form['search']
        #
        # select_search = {
        #     'select': select,
        #     'search': search
        # }

        all_subject = list(db.schedule.find({}))

        print("엥...")
        print(all_subject[0]['subject'])
        return render_template('select_subject.html')  # return 값 수정필요


if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)
