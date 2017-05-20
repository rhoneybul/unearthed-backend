from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import json
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
	return jsonify({"Greeting": 'Hello Hackathon'})

"""
ROUTES FOR ALL NODES
"""

## GET request to return all nodes

@app.route("/nodes", methods=['GET'])
def getNodes():
	with open('json/pump.json', 'rb') as f:
		data = json.load(f)["Nodes"]
	return jsonify({"Nodes": data})

## POST request to add a new node 

@app.route("/nodes", methods=['POST'])
def createNodes():
	with open("json/pump.json", "rb") as f:
		data = json.load(f)['Nodes']
	ids = []
	for node in data:
		ids.append(node['id'])
	maxid = np.max(ids)
	id = maxid+1
	newNode = {
		"id": id,
		"type": request.json["type"]
	}
	
	data.append(newNode)
	nodesDict = {
		"Nodes": data
	}
	with open("json/pump.json", "w") as f:
		json.dump(nodesDict, f, indent=2)
	return jsonify({"newNode": newNode})

"""
ROUTES FOR A PARTICULAR NODE
"""
## GET REQUEST FOR A PARTICULAR NODE
@app.route("/<string:node>", methods=['GET'])
def getNode(node):
	with open('json/pump.json', 'rb') as f:
		data = json.load(f)["Nodes"]
	nodeDict = [d for d in data if int(d['id']) == int(node)]
	if len(nodeDict) == 0:
		return jsonify({"Error": "Cannot Find Node"})
	else:
		nodeDict = nodeDict[0]
		return jsonify({"Node": nodeDict})

## UPDATE NODE

@app.route("/<string:node>", methods=['PUT'])
def updateNode(node):
	with open('json/pump.json', 'rb') as f:
		data = json.load(f)["Nodes"]
	toUpdate = [d for d in data if int(d['id']) == int(node)]
	if len(toUpdate) == 0:
		return jsonify({"Error": "Cannot find Node"})
	else:
		newDict = [d for d in data if int(d['id']) != int(node)]
		toUpdate = toUpdate[0]
		toUpdate["isLocked"] = request.json["isLocked"]
		newDict.append(toUpdate)
		nodesDict = {
			"Nodes": newDict
		}
		with open("json/pump.json", "w") as f:
			json.dump(nodesDict, f, indent=2)
		return jsonify({"updatedNode": toUpdate})	

## DELETE NODE

@app.route("/<string:node>", methods=["DELETE"])
def deleteNode(node):
	with open('json/pump.json', 'rb') as f:
		data = json.load(f)["Nodes"]
	newDict = [d for d in data if int(d['id']) != int(node)]
	nodesDict = {
		"Nodes": newDict
	}
	## For nodes dict, need to iterate through and remove 
	## from any connections array 
	for dd in newDict:
		dd["connections"] = [conn for conn in dd["connections"] if int(conn) != int(node)] 
		print dd["connections"]
	with open('json/pump.json', 'w') as f:
		json.dump(nodesDict, f, indent=2)
	return jsonify({"newDict": newDict})

"""
ROUTES FOR OBTAINING ISOLATION REGIME
"""

@app.route("/<string:node>/isolate", methods=['GET'])
def isolateNode(node):
	with open("json/pump.json", "rb") as f:
		data = json.load(f)["Nodes"]
	nodeToIsolate = {}
	for nodes in data:
		if int(nodes['id']) == int(node):
			nodeToIsolate = nodes
	if len(nodeToIsolate.keys()) == 0:
		return jsonify({"Error": "Cannot Find Node"})
	else:
		return jsonify({"Node": nodeToIsolate})

"""
ROUTES FOR GETTING / CREATING CONNECTION
"""



"""
=================
SOUTH32 comments;
=================

- valves will move place next to the valve
- things will get covered over time
- crowdsourcing is positive... taps into exisitng workforce
- need to make it easy - user interface needs to be simple
- connections is difficult. Entering the relationships is important... Verification is importatnt.

==============
BACKEND SCHEMA
==============

route ("/:node/isolate") [GET]
	returns the nodes reuquired to isolate the particular ':node'

\/ route /nodes [POST]
	posts a new node into the data structure

\/ route /nodes [GET]
	gets all nodes in the network

\/ route /:node [GET]
	get a particular node

route /:node [UPDATE]
	updates the values for a particular node

route /connection/:id1/:id2 [UPDATE]
	updates a particular connection

route /connection/:id1/:id2 [POST]
	posts a new connection between id1 and id2

route /connection/:id1/:id2 [DELETE]
	if verified, remove a verification
	if no verificaiton remove verification

route /connection/:node [DELETE]
	if verified remove the verification
	if no verification remove the node, 
	and subsequently all connections associated with that node.

route /connection/:id1/:id2 [GET]
	confirmation of the connection
	if connections exists:
		then display : connection exists between id1 and id2, and the verificaiton status
	else:
		renders form for post request, and can create the connection
"""

if __name__ == "__main__":
	app.run()