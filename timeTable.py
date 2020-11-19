from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.mindConnecting
def getTimeTable():
    all_subject = list(db.schedule.find({}))

    print(all_subject[0])
    return all_subject
# print(all_subject[0]['subject'])