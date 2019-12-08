import redis
from pymongo import MongoClient
from flask import Flask, request
from logging.config import dictConfig
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# from os import path
# log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.config')
# logging.config.fileConfig(log_file_path)

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "aydar": generate_password_hash("user"),
    "ravil": generate_password_hash("admin")
}


cache = redis.Redis(host='redis', port=6379)

db_client = MongoClient('mongodb://root:password@mongo')
db = db_client.server_storage
storage = db.storage

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.route('/put', methods=['POST', 'PUT'], endpoint="put")
@auth.login_required
def put():
    response = {}
    app.logger.debug('put for key')
    storage.find_one_and_update(
        {"key": request.values.get("key")}, {"$set": {"key": request.values.get("key"), "value": request.values.get("value")}}, upsert=True)
    return response, 200


@app.route('/get', methods=['GET'], endpoint="get")
@auth.login_required
def get():
    response = {
        'from-cache': False
    }
    response_code = 200
    cached_ans = None
    if not request.values.get('no-cache'):
        cached_ans = cache.get(request.values.get('key'))
        app.logger.debug('get for key')

    if request.values.get('no-cache') or not cached_ans:
        app.logger.warning('no data in cache for key') # not in cache

        storage_ans = storage.find_one({"key": request.values.get("key")})
        app.logger.debug('get for key')
        if storage_ans:
           response["value"] = storage_ans['value']
           response_code=200
           if not request.values.get('no-cache'):
               cache.set(request.values.get("key"), str(response['value']))
        else:
            app.logger.error('no data in database for key')
            response_code = 404
    else:
        if type(cached_ans) is bytes:
            cached_ans = cached_ans.decode('utf-8')
        response['value'] = cached_ans
        response['from-cache'] = True

    return response, response_code


@app.route('/delete', methods=['DELETE'], endpoint="delete")
@auth.login_required
def delete():
    response = {}
    response_code = 200
    deleted_count = storage.delete_one({"key": request.values.get("key")}).deleted_count
    app.logger.debug('delete for key')
    if not deleted_count:
        response_code = 204
    return response, response_code


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=65432)