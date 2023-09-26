from flask import request, jsonify, redirect, make_response
from app import app, db, SECRET_KEY
from models import Files
from schemas import FilesSchema, FilesListSchema
from flasgger.utils import swag_from
from functools import wraps
import jwt
 

file_schema = FilesSchema()
files_schema = FilesSchema(many=True)
files_list_schema = FilesListSchema(many=True)


def decode_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(decoded)
        return decoded
    except Exception as e:
        print(e)
        return None  # token expirado
    
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token()
        if not token:
            return jsonify({"error": "Missing token"}), 402
        user_data = decode_jwt(token)
        if not user_data:
            return jsonify({"error": "Invalid or expired token"}), 403
        return f(*args, **kwargs)
    return decorated    

# TODAS AS ROTAS
# --------------------------------------------------------------------------
@app.before_request
def before_request_func():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'content-type')
        response.headers.add('Access-Control-Allow-Headers', 'authorization')
        return response


# ROUTE / 
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return redirect("/apidocs")


# ROUTE /files (GET)  GET all files owned by that user
# --------------------------------------------------------------------------
@app.route('/files', methods=['GET'])
@swag_from('docs/get_files.yml')
@requires_auth
def get_files():
    token = get_token()
    user_data = decode_jwt(token)
    user_id = user_data.get('user_id')
    
    files = Files.query.filter_by(user_id=user_id).all()
    return jsonify(files_list_schema.dump(files))


# ROUTE /files (POST) ADD A NEW FILE TO THAT USER
# --------------------------------------------------------------------------
@app.route('/files', methods=['POST'])
@swag_from('docs/post_file.yml')
@requires_auth
def post_file():
    token = get_token()
    data = request.get_json()
    user_data = decode_jwt(token)
    user_id = user_data.get('user_id')

    # Verifica se o arquivo já existe
    existing_file = Files.query.filter_by(user_id=user_id, file_name=data['file_name']).first()

    if existing_file:
        # Atualiza o arquivo existente
        existing_file.file_content = data['file_content']
        existing_file.tags = data['tags']
        file_to_commit = existing_file
    else:
        # Cria um novo arquivo
        new_file = Files(
            user_id=user_id,
            file_name=data['file_name'],
            file_content=data['file_content'],
            tags=data['tags']
        )
        db.session.add(new_file)
        file_to_commit = new_file

    try:
        db.session.commit()
        return file_schema.jsonify(file_to_commit)
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Error processing the file."}), 400


# ROUTE /users/nn (PUT) UPDATE THE FILE DATA
# --------------------------------------------------------------------------
@app.route('/files/<int:file_id>', methods=['PUT'])
@swag_from('docs/put_file.yml')
@requires_auth
def update_file(file_id):
    data = request.get_json()
    token = get_token()
    user_data = decode_jwt(token)
    user_id = user_data.get('user_id')

    file = Files.query.get(file_id)
    if file and file.user_id == user_id:
        file.file_name = data.get('file_name', file.file_name)
        file.file_content = data.get('file_content', file.file_content)
        file.tags = data.get('tags', file.tags)
        db.session.commit()
        return jsonify(files_schema.dump(file))
    else:
        return jsonify({'error': 'File not found or unauthorized'}), 404


# ROUTE /file/<id> (GET) FIND A USER SPECIFIC FILE
# --------------------------------------------------------------------------
@app.route('/file/<int:file_id>', methods=['GET'])
@swag_from('docs/get_file.yml')
@requires_auth
def get_file_by_id(file_id):
    token = get_token()
    user_data = decode_jwt(token)
    user_id = user_data.get('user_id')

    file = Files.query.filter_by(user_id=user_id, id=file_id).first()
    if file:
        return jsonify(file.serialize())
    else:
        return jsonify({'error': 'File not found'}), 404

    
# ROUTE /users/<id> (DELETE) DEL USER BY ID
# --------------------------------------------------------------------------
@app.route('/files', methods=['DELETE'])
@swag_from('docs/delete_file.yml')
@requires_auth
def delete_file():
    token = get_token()
    user_data = decode_jwt(token)
    user_id = user_data.get('user_id')
    file_name = request.args.get('file_name')

    file = Files.query.filter_by(user_id=user_id, file_name=file_name).first()
    if file:
        db.session.delete(file)
        db.session.commit()
        return jsonify({'message': 'File deleted successfully'})
    else:
        return jsonify({'error': 'File not found'}), 404
    
    
def get_token():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split('Bearer ')[1]
    else:
        token = None    
    return token    