from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
import pymongo
#from flask_jwt import JWT, jwt_required
#from security import identity, authenticate
from config import mycolp
import json

class Product(Resource):
    def get(self, name):
        try:
            product = list(mycolp.find({"name": name}))
            if product:
                return dumps(product), 200
            else:
                return {"message": "Product with this name not found."}, 404
        except Exception as e:
            return {"error": str(e)}, 400

    #@jwt_required()
    def post(self, name): 
        try:
            request_data = request.get_json()
            print(request_data["name"])
            print(request_data["description"])
            new_product = {
                "name": request_data["name"],                
                "description": request_data["description"],                
                "price": request_data["price"],
                "quantity": request_data["quantity"],
                "user":request_data["user"]
            }
            print(new_product)
            mycolp.insert(new_product)
            return dumps(new_product), 201
        except Exception as e:
            return {"error": str(e)}, 400
    
    #@jwt_required()
    def delete(self, name):
        try:
            product = mycolp.find_one_and_delete({"name": name})
            if product:
                return {"message": "Product deleted."}, 200
            else:
                return {"message": "Product with this name not found."}, 404
        except Exception as e:
            return {"error": str(e)}, 400
class ProductList(Resource):
    def get(self):
        try:
            products = list(mycolp.find())
            if products:
                return dumps(products), 200
            else:
                return {"message": "No Products found."}, 404
        except Exception as e:
            return dumps({"error": str(e)})