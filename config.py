import pymongo
import json
#myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#myclient.drop_database("mydatabase")
myclient = pymongo.MongoClient("mongodb+srv://takiMed:993yzDmfks7S1FSo@cluster0.aif7q.mongodb.net/productsDatabase?retryWrites=true&w=majority")
mydb=myclient["mydatabase"]
mycolu = mydb["Users"]
mycolp = mydb["Products"]