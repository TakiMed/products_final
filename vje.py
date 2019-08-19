from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
import pymongo
import bson
from bson.objectid import ObjectId
from flask_jwt import JWT, jwt_required
from security import identity, authenticate
import csv
from config import mydb,mycolp,mycolu
import json
from users import User,UserList
from products import Product,ProductList
from flask.json import JSONEncoder
from bson import json_util
from group import profit
from mailing import to_csv, mailing

#json Encoder jer nije htio da mi salje id, Typerror:Object of type ObjectId is not JSON serializable
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj): return json_util.default(obj)

vvproducts={
      "$jsonSchema": {
            "bsonType": "object",
            #dodati usera kad dragana napravi, ne znam kako sliku
            "properties": {
                "name": {
                    "bsonType": "string",
                    "minLength": 3,
                    "maxLength": 30
                },          
                "description": {
                    "bsonType": "string",
                    "minLength": 0,
                    "maxLength": 150
            },
                "price": {
                    "bsonType":"number",
                    "minimum":1,
                    "maximum":1000
            },            
                "quantity": {
                    "bsonType":"number",
                    "minimum":1,
                    "maximum":10
            },
                "user":{
                    "bsonType":"string"
                }
      }
    }
}
#SAD RADIM BEZ VALIDACIJE PA CU JE DODATI NAKNADNO
vvusers={
      "$jsonSchema": {
          "bsonType": "object",
          "required": [ "username", "password", "email"],
          "properties": {
            "username": {
               "bsonType": "string",
               "description": "must be a string and is required",
               "minLength": 3,
               "maxLength": 20
            },
            "password": {
               "bsonType": "string",
               "minLength":5,
               "maxLength":25
            },
            "email": {
               "bsonType": "string",
               "description": "must be a number and is required",
               "minLength":5,
               "maxLength":35
            },
            "role": {
               "bsonType": "number",
               "enum": [0,1],
               #"default": 0,
               #definisati da moze 0 ili 1
               "description": "must be a number and is required"
            },
            "product":{
                "bsonType":"array"
            } 
      }
    }
}
if not "Products" in mydb.list_collection_names():
    mycolp=mydb.create_collection("Products",validator=vvproducts)
    mycolp.create_index("name", unique=True)
else:
    mycolp = mydb["Products"]

if not "Users" in mydb.list_collection_names():
    mycolu = mydb.create_collection("Users",validator=vvusers)
    mycolu.create_index("username", unique=True)
else:
    mycolu = mydb["Users"]
#dodaj ADMINA ZBOG MAIL
admin=mycolu.find_one({"role":1})
if not admin:
    admin={"username":"admin","password":"admin123","email":"testninalogdts@gmail.com","role":1,"product":[]}
    mycolu.insert_one(admin)

app = Flask(__name__)
api = Api(app)
jwt = JWT(app, authenticate, identity)
app.secret_key = "neki_string_koji_ne_smije_da_bude_public"
app.config['DEBUG']=True
app.config['TESTING']=False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']='testninalogdts@gmail.com'
app.config['MAIL_PASSWORD']='TESTtest123.'
app.config['MAIL_DEFAULT_SENDER']='testninalogdts@gmail.com'
app.config['MAIL_MAX_EMAILS']=None
app.config['MAIL_ASCII_ATTACHMENTS']=False
mail=Mail(app)

app.json_encoder = CustomJSONEncoder
api.add_resource(Product, "/product/<string:name>")
api.add_resource(ProductList, "/products")

api.add_resource(User, "/user/<string:username>")
api.add_resource(UserList, "/userlist")

@app.route('/product_inc/<name>',methods=["POST"])
def product_inc(name):
    product=mycolp.find_one({"name":name})
    if (product["quantity"]<=9):
        incremented=product["quantity"]+1
        newvalues = { "$set": { "quantity": incremented } }
        mycolp.update_one(product, newvalues)
        return "Quantity in stock  " + str(product["quantity"]) + "  pcs  "+ product["name"] 
    else:
        return "You have exceeded the product quantity limit :  " + str(product["quantity"]) + "  pcs."

@app.route('/product_dec/<name>',methods=["POST"])
def product_dec(name):
    product=mycolp.find_one({"name":name})
    if (product["quantity"]>0):
        decremented=product["quantity"]-1
        newvalues = { "$set": { "quantity": decremented } }
        mycolp.update_one(product, newvalues)
        return "Quantity in stock  " + str(mycolp.find_one({"name":name})["quantity"]) + "  pcs  "+ product["name"] 
    else:
        return "You have exceeded the product quantity limit :  " + str(product["quantity"]) + "  pcs."

@app.route('/product_num/<name>',methods=["GET"])
#@jwt_required()
def product_num(name):
    product=mycolp.find_one({"name":name})
    return "Quantity in stock  " + str(product["quantity"]) + "  pcs  "+ product["name"]

@app.route('/product_id/<string:id>',methods=["GET","DELETE","PUT"])
def product_id(id):
    if request.method=="GET":
        product=mycolp.find_one({'_id':bson.ObjectId(oid=str(id))})
        return jsonify(product)
    elif request.method=="DELETE":
        try:
            product=mycolp.find_one_and_delete({'_id':bson.ObjectId(oid=str(id))})
            return "Product deleted."
        except Exception as e:
                return dumps({"error": str(e)})
    elif request.method=="PUT":
        try:
            product=list(mycolp.find({'_id':bson.ObjectId(oid=str(id))}))
            if not product:
                new_product = {
                '_id':bson.ObjectId(oid=str(id)),
                "name": request.args.get("name",product_id),                
                "description": request.args.get("description",""),                
                "price": request.args.get("price",1),
                "quantity": request.args.get("quantity",1),
                "user": request.args.get("user","")
            }   
                if new_product["price"]:
                    new_product["price"]=int(new_product["price"])
                if new_product["quantity"]:
                    new_product["quantity"]=int(new_product["quantity"])
                mycolp.insert_one(new_product)
                user=mycolu.find_one({"username":new_product["user"]})
                user["product"].append(id)
                mycolu.update_one({"username":new_product["user"]},{"$set":{"product":user["product"]}})
                mailing(new_product,admin)
                return dumps(new_product), 201
            else:
                product=product[0]
                new_product = {
                '_id':bson.ObjectId(oid=str(id)),
                "name": request.args.get("name",product["name"]),                
                "description": request.args.get("description",product["description"]),                
                "price": request.args.get("price",product["price"]),
                "quantity": request.args.get("quantity",product["quantity"]),
                "user": request.args.get("user",product["user"])
            }
                if new_product["price"]:
                    new_product["price"]=int(new_product["price"])
                if new_product["quantity"]:
                    new_product["quantity"]=int(new_product["quantity"])
                mycolp.update_one({'_id':bson.ObjectId(oid=str(id))}, {"$set": new_product})
                return "Product :  " + product["name"]+ "  updated.", 200
        except Exception as e:
                return dumps({"error": str(e)})
    else:
        return dumps({"error":"Wrong request."})

@app.route('/product_group')
def product_group():
    if request.method == 'GET':
        offset=int(request.args.get('offset', ''))
        limit=int(request.args.get('limit', ''))
        products=mycolp.find().skip(offset).limit(limit)
        output=[]
        for i in products:
            output.append(i)
        return jsonify({"result":output})
#STAVITI SAMO DA KAD KORISNIK DODAJE, BRISE I STAVLJA ID DA SE TO ISTO DEAVA U LISTI

@app.route('/add_product',methods=["GET","PUT","POST","DELETE"])
def add_product():
    username=request.args.get('username','')
    product_id=request.args.get('id','')
    user=mycolu.find_one({"username":username})
    products_id_list=user["product"]
    if request.method=='POST':
        #PRVO PROVJERAVAM DA LI JE TAJ PROIZVOD VEC KREIRAN OD STRANE NEKOG DRUGOG USERA
        for product in mycolp.find():
            if product['_id']==bson.ObjectId(oid=str(product_id)):
                return "Product with this id already created by user:  " + product["user"]
        if product_id not in products_id_list:
            try:
                products_id_list.append(product_id)
                new_product={
                '_id':bson.ObjectId(oid=str(product_id)),
                'user':username,
                "name": request.args.get("name",product_id),                
                "description": request.args.get("description",""),                
                "price": request.args.get("price",2),
                "quantity": request.args.get("quantity",2)}
                if new_product["price"]!=1:
                    new_product["price"]=int(new_product["price"])
                if new_product["quantity"]!=1:
                    new_product["quantity"]=int(new_product["quantity"])
                dumps(new_product)
                mycolp.insert_one(new_product)
                return new_product
                #mailing(new_product,admin)
                #mycolu.update_one({'username':username},{"$set":{"product":products_id_list}})
                #return "Added  : " + product_id + "  to user : " + user["username"] + "  and updated in Users and Products."
            except Exception as e:
                return dumps({"error": str(e)})
    elif request.method=='DELETE':
        if product_id in products_id_list:
            try:
                products_id_list.delete(product_id)
                mycolp.find_one_and_delete({'_id':bson.ObjectId(oid=str(product_id))})
                mycolu.update_one({'username':username},{"$set":{"product":products_id_list}})
                return "Deleted  : " + product_id + "  from user : " + user["username"] + "  and updated in Users and Products."
            except Exception as e:
                return dumps({"error": str(e)})
        else:
            return "Product_id not created by this user"
    elif request.method=='GET':
        return "Current product_id list for user "+ user["username"] + "  :"+ str(products_id_list)
        #UPDATE SAM VEC ODRADILA KROY POST, ISTI JE KOD, OVO JE SAMO PRO FORME STAVLJENO!
    elif request.method=='PUT':
        mycolu.update_one({'username':username},{"$set":{"product":products_id_list}})
        return "Product_id list for user  " + user["username"] +  "  updated. Current list:  " + str(user["product"])

@app.route('/max_profit/<string:username>')
def max_profit(username):
    return "Maximum possible profit from products created by user is :"+ str(profit(username))
    

app.run(port=33507, debug=True)