from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
import pymongo
from flask_jwt import JWT, jwt_required
from .security import identity, authenticate
from .config import mycolp
import json

class Product(Resource):
    @jwt_required()
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
    def put(self,name):
        try:
            request_data = request.get_json()
            product = list(mycolp.find({"name": name}))
            parser = reqparse.RequestParser()
            is_required = False
            if not product:
                is_required = True
            else:
                product = product[0]
            parser.add_argument("name", type=str, required=is_required)
            parser.add_argument("description", type=str, required=is_required)
            parser.add_argument("quantity", type=int, required=is_required)
            parser.add_argument("price", type=int, required=is_required)
            parser.add_argument("user", type=str, required=is_required)
            request_data = parser.parse_args()
            
            new_product = {
                "name":request_data["name"] if request_data["name"] else product["name"],
                "description":request_data["description"] if request_data["description"] else product["description"],
                "quantity":request_data["quantity"] if request_data["quantity"] else product["quantity"],
                "price":request_data["price"] if request_data["price"] else product["price"],
                "user":request_data["user"] if request_data["user"] else product["user"],
            }
            
            if not product:
                mycolp.insert_one(new_product)
                return dumps(new_product), 201
            else:
                mycolp.update_one({"name": name}, {"$set": new_product})
                return {"message": "Updated"}, 200
        except Exception as e:
            return {"error": str(e)}, 400
    
    #@jwt_required()
    def delete(self,name):
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