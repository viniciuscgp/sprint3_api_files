from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger
import os 
from dotenv import load_dotenv
from flask_cors import CORS

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "title": 'Clean IDE - Files API',
    "description": 'This API is part of an MVP made for the 3rd Sprint of the PUC-RJ Fullstack Developer postgraduate course',
    "termsOfService": 'Termos de Serviço',
    "contact": {
        "email": "vinians2006@yahoo.com.br"
    },
    "license": {
        "name": "Licença",
        "url": ""
    },
}

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'DkidAddxx@@@333dddSASS'

db = SQLAlchemy(app)
ma = Marshmallow(app)
SECRET_KEY = os.getenv("SECRET_KEY")

swagger = Swagger(app=app, config=swagger_config)

from controller import *

if __name__ == '__main__':
    load_dotenv()
    port = int(os.getenv("PORT", 5001))    
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=port, debug=True)
