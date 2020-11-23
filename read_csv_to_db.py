import csv
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.mindConnecting

with open('data.csv', 'r', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    for row_data in rdr:
        db.schedule.insert_one(row_data)
