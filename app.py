from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
	return jsonify({'Greeting': 'Hello Hackathon'})

if __name__ == "__main__":
	app.run()