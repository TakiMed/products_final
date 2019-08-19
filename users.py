from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
import pymongo
from flask_jwt import JWT, jwt_required
#from security import identity, authenticate
import json
from config import mycolu

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
    def post(self, username): 
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