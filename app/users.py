from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
import pymongo
from flask_jwt import JWT, jwt_required
#from security import identity, authenticate
import json
from .config import mycolu

class User(Resource):   
    def get(self, username):
        try:
            user = list(mycolu.find({"username":username}))
            if user:
                return dumps(user), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400

    #@jwt_required()
    def post(self): 
        try:
            request_data = request.get_json()
            new_user = {
                "username": request_data["username"],
                "password": request_data["password"],
                "email": request_data["email"],
                "role": request_data["role"],
                "product": request_data["product"]
            }
            mycolu.insert_one(new_user)
            return dumps(new_user), 201
        except Exception as e:
            return {"error": str(e)}, 400
    def put(self,username):
        try:
            request_data = request.get_json()
            user = list(mycolu.find({"username": username}))
            parser = reqparse.RequestParser()
            is_required = False
            if not user:
                is_required = True
            else:
                user = user[0]
            parser.add_argument("username", type=str, required=is_required)
            parser.add_argument("email", type=str, required=is_required)
            parser.add_argument("password", type=str, required=is_required)
            parser.add_argument("role", type=int, required=is_required)
            parser.add_argument("product", type=list, required=is_required)
            request_data = parser.parse_args()
            
            new_user = {
                "username":request_data["username"] if request_data["username"] else user["username"],
                "password":request_data["password"] if request_data["password"] else user["password"],
                "email":request_data["email"] if request_data["email"] else user["email"],
                "role":request_data["role"] if request_data["role"] else user["role"],
                "product":request_data["product"] if request_data["product"] else user["product"],
            }
            
            if not user:
                mycolu.insert_one(new_user)
                return dumps(new_user), 201
            else:
                mycolu.update_one({"username": username}, {"$set": new_user})
                return {"message": "Updated"}, 200

        except Exception as e:
            return {"error": str(e)}, 400
    
    #@jwt_required()
    def delete(self, username):
        try:
            user = mycolu.find_one_and_delete({"username": username})
            if user:
                return {"message": "User deleted."}, 200
            else:
                return {"message": "User with this name not found."}, 404
        except Exception as e:
            return {"error": str(e)}, 400

class UserList(Resource):
    def get(self):
        try:
            users = list(mycolu.find())
            if users:
                return dumps(users), 200
            else:
                return None, 404
        except Exception as e:
            return dumps({"error": str(e)})