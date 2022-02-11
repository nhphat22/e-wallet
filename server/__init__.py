import os
from flask import Flask
from flask_cors import CORS
from server.routes import auth_blueprint


app = Flask(__name__)
CORS(app)
app.register_blueprint(auth_blueprint)

app.config.from_object('config.Config')