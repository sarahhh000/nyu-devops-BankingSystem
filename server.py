# Copyright 2016 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import redis
from flask import Flask, Response, jsonify, request, json

# Get bindings from the environment
port = os.getenv('PORT', '5000')
hostname = os.getenv('HOSTNAME', '127.0.0.1')
redis_port = os.getenv('REDIS_PORT', '6379')

# Pet Model for demo
pets = {'fido': {'name': 'fido', 'kind': 'dog'}, 'kitty': {'name': 'kitty', 'kind': 'cat'}}

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return jsonify(name='Bank System REST API Service', version='1.0', url='/accounts'), HTTP_200_OK

######################################################################
# TODO LIST ALL ACCOUNTS
# LIST ALL ACCOUNTS WITH A CERTAIN NAME: /accounts?name=john
######################################################################
@app.route('/accounts', methods=['GET'])
def list_accounts():
    name = request.args.get('name')
    if name:
        message = []
        for key in redis_server.keys():
            account = redis_server.hgetall(key)
            if account.has_key('name'):
                if account.get('name')==name:
                    message.append(account)
                    rc = HTTP_200_OK
        if message:
            return reply(message, rc)
        message = { 'error' : 'Account under name: %s was not found' % name }
        rc = HTTP_404_NOT_FOUND
        return reply(message, rc)


######################################################################
# RETRIEVE AN ACCOUNT WITH ID
######################################################################
@app.route('/accounts/<id>', methods=['GET'])
def get_account_by_id(id):
    for account in redis_server.keys():
        if account == ('id:'+id):
            message = redis_server.hgetall(account)
            rc = HTTP_200_OK
            return reply(message, rc)

    message = { 'error' : 'Account id: %s was not found' % id }
    rc = HTTP_404_NOT_FOUND
    return reply(message, rc)


######################################################################
# ADD A NEW PET
######################################################################
@app.route('/pets', methods=['POST'])
def create_pet():
    payload = json.loads(request.data)
    if is_valid(payload):
        id = payload['name']
        if pets.has_key(id):
            message = { 'error' : 'Pet %s already exists' % id }
            rc = HTTP_409_CONFLICT
        else:
            pets[id] = {'name': payload['name'], 'kind': payload['kind']}
            message = pets[id]
            rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST

    return reply(message, rc)

######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route('/pets/<id>', methods=['PUT'])
def update_pet(id):
    payload = json.loads(request.data)
    if pets.has_key(id):
        pets[id] = {'name': payload['name'], 'kind': payload['kind']}
        message = pets[id]
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Pet %s was not found' % id }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)

######################################################################
# DELETE A PET
######################################################################
@app.route('/pets/<id>', methods=['DELETE'])
def delete_pet(id):
    del pets[id];
    return '', HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def reply(message, rc):
    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

def is_valid(data):
    valid = False
    try:
        name = data['name']
        kind = data['kind']
        valid = True
    except KeyError as err:
        app.logger.error('Missing value error: %s', err)
    return valid

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    # Get bindings from the environment
    port = os.getenv('PORT', '5000')
    redis_server = redis.Redis(host=hostname, port=int(redis_port))
    app.run(host='0.0.0.0', port=int(port), debug=True)

    # intialization
    # TODO data structure is as follows. At last will need to comment all the following code

    # this will erase all the previous data
    # redis_server.flushall()

    # 'id:1' and 'id:2' is the key, which is global unique
    redis_server.hset('id:1',  'id', '1')
    redis_server.hset('id:1',  'name', 'john')
    redis_server.hset('id:1',  'balance', 100)
    redis_server.hset('id:1',  'active', 1)

    redis_server.hset('id:2',  'id', '2')
    redis_server.hset('id:2',  'name', 'james')
    redis_server.hset('id:2',  'balance', 200)
    redis_server.hset('id:2',  'active', 0)

    redis_server.hset('id:3',  'id', '3')
    redis_server.hset('id:3',  'name', 'john')
    redis_server.hset('id:3',  'balance', 10000)
    redis_server.hset('id:3',  'active', 1)