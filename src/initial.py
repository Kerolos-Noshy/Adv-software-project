from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
repo_path = os.path.abspath(os.path.dirname(__name__))

template_dir = os.path.join(
        repo_path,  'templates'  # location of front end pages
    )

static_dir = os.path.join(
        repo_path,  'static'  # location of front end pages
    )
app = Flask(__name__,template_folder=template_dir,static_folder=static_dir)
CORS(app)    
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False