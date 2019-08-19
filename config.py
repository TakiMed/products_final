import pymongo
import json
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#myclient.drop_database("mydatabase")
mydb=myclient["mydatabase"]
mycolu = mydb["Users"]
mycolp = mydb["Products"]