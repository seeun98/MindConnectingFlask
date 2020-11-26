from flask import Flask, render_template, request
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.mindConnecting
app = Flask(__name__)


def getAllSchedules():
    all_schedule = [x for x in list(db.schedule.find({}, {'_id': 0, 'code': 1, 'subject': 1, 'professor': 1}))]
    return all_schedule

# 수정필요
def getSpecificSchedules():
    specific_schedule = [x for x in list(db.schedule.find({"subject": "데이터베이스"}))]
    return specific_schedule
