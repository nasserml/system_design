import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config['MONGO_URI'] = 'mongodb://host.minikube.internal:27017/videos'

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

@server.route('login', methods=['POST'])
def login():
    """
    Logs in a user and returns a token if successful, or an error message if unsuccessful.

    Parameters:
    None

    Returns:
    str: The authentication token if the login is successful.
    str: The error message if the login is unsuccessful.
    """
    token, err = access.login(request)
    
    if not err:
        return token
    else:
        return err


@server.route('upload', methods=['POST'])
def upload():
    """
    Uploads a file to the server.

    Returns:
        - If the request is authorized and contains exactly one file, returns 'success' with a status code of 200.
        - If the request is not authorized, returns 'not authorized' with a status code of 401.
        - If the request does not contain exactly one file, returns 'exactly 1 file required' with a status code of 400.
    """
    access, err = validate.token(request)
    
    access = json.loads(access)
    
    if access['admin']:
        if len(request.files) > 1 or len(request.files) < 1 :
            return 'exactly 1 file required', 400
        
        
        for _,f in request.files.items():
            err = util.upload(f, fs, channel, access)
            
            if err:
                return err
            
        return 'success', 200
        
    else:
        return 'not authorized', 401



@server.route('/download', method=['GET'])
def download():
    pass

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=8080)