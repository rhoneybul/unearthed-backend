from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import json
import numpy as np

app = Flask(__name__)
CORS(app)

DATA_FN = 'json/isolation.json'

def getNodeWithId(nodes, nodeId):
	node = [n for n in nodes if int(n["id"]) == nodeId]
	if len(node) == 0:
		return None
	return node[0]

@app.route("/")
def index():
	return jsonify({"Greeting": 'Hello Hackathon'})

"""
ROUTES FOR ALL NODES
"""

## GET request to return all nodes

@app.route("/nodes", methods=["GET"])
def getNodes():
	with open(DATA_FN, "r") as f:
		nodes = json.load(f)["nodes"]
	return jsonify({"nodes": nodes})

## POST request to add a new node

@app.route("/nodes", methods=["POST"])
def createNodes():
	with open(DATA_FN, "r") as f:
		nodes = json.load(f)["nodes"]
	ids = []
	for node in nodes:
		ids.append(node["id"])
	newid = np.max(ids) + 1
	newNode = {
		"id": newid,
		"type": request.json["type"]
	}
	nodes.append(newNode)
	with open(DATA_FN, "w") as f:
		json.dump({"nodes": nodes}, f, indent=2)
	return jsonify({"newNode": newNode})

"""
ROUTES FOR A PARTICULAR NODE
"""
## GET REQUEST FOR A PARTICULAR NODE
@app.route("/<int:nodeId>", methods=["GET"])
def getNode(nodeId):
	with open(DATA_FN, "r") as f:
		nodes = json.load(f)["nodes"]
	nodeDict = getNodeWithId(nodes, nodeId)
	if nodeDict == None:
		return jsonify({"Error": "Cannot find node."})
	else:
		return jsonify({"node": nodeDict})

## UPDATE NODE

@app.route("/<int:nodeId>", methods=['PUT'])
def updateNode(nodeId):
	with open(v, "r") as f:
		nodes = json.load(f)["nodes"]
	toUpdate = getNodeWithId(nodes, nodeId)
	if toUpdate == None:
		return jsonify({"Error": "Cannot find node."})
	else:
		newDict = [d for d in nodes if int(d["id"]) != nodeId]
		toUpdate["isLocked"] = request.json["isLocked"]
		newDict.append(toUpdate)
		nodesDict = {
			"nodes": newDict
		}
		with open(DATA_FN, "w") as f:
			json.dump(nodesDict, f, indent=2)
		return jsonify({"updatedNode": toUpdate})	

## DELETE NODE

@app.route("/<int:nodeId>", methods=["DELETE"])
def deleteNode(nodeId):
	with open(DATA_FN, "r") as f:
		nodes = json.load(f)["nodes"]
	newDict = [d for d in nodes if int(d["id"]) != nodeId]
	nodesDict = {
		"Nodes": newDict
	}
	for dd in newDict:
		dd["connections"] = [conn for conn in dd["connections"] if int(conn) != nodeId]
		print dd["connections"]
	with open(DATA_FN, "w") as f:
		json.dump(nodesDict, f, indent=2)
	return jsonify({"newDict": newDict})

"""
ROUTES FOR OBTAINING ISOLATION REGIME
"""

@app.route("/<int:nodeId>/isolate", methods=["GET"])
def isolateNode(nodeId):
	with open(DATA_FN, "r") as f:
		nodes = json.load(f)["nodes"]
	nodeToIsolate = getNodeWithId(nodes, nodeId)
	if nodeToIsolate == None:
		return jsonify({"Error": "Cannot find node."})
	else:
		nodesToIsolate = []
		queue = [nodeToIsolate["id"]]
		visited = {}
		while len(queue) > 0:
			cur = queue[0]
			queue = queue[1:]
			if visited[cur] == True:
				continue
			curNode = getNodeWithId(nodes, cur)
			visited[cur] = True
			if curNode["type"] == "Isolation valve":
				nodesToIsolate.append(cur)
			else:
				for conn in curNode["connections"]:
					queue.append(conn)
		return jsonify(nodesToIsolate)

"""
ROUTES FOR GETTING / CREATING CONNECTION
"""

@app.route("/connections/<int:nodeId>", methods=["GET"])
def getConnections(nodeId):
	with open(DATA_FN, "r") as f:
		nodes = json.load(f)["nodes"]
	nodeData = [d for d in nodes if int(d["id"]) == nodeId]
	if len(nodeData) == 0:
		return jsonify({"Error": "Cannot find node."})
	else:
		nodeData = nodeData[0]
		connections = nodeData["connections"]
		if len(connections) == 0:
			return jsonify({"Error": "No Connections."})
		else:
			connDict = []
			for conn in connections:
				connDict.append([d for d in nodes if int(d["id"]) == int(conn)][0])
			return jsonify({"Connections": connDict})

@app.route("/connections", methods=["POST"])
def addConnection():
	node1 = request.json['1']
	node2 = request.json['2']
	with open(DATA_FN, "r") as f:
		nodes = json.load(f)["nodes"]
	firstNode = [d for d in nodes if int(d["id"]) == int(node1)]
	secondNode = [d for d in nodes if int(d["id"]) == int(node2)]
	if len(firstNode) == 0 or len(secondNode) == 0:
		return jsonify({"Error": "Cannot find node."})
	else:
		firstNode = firstNode[0]
		secondNode = secondNode[0]
		newDict = [d for d in nodes if int(d["id"]) != int(node1) and int(d["id"]) != int(node2)]
		## Test if the connection already exists
		if int(node1) in secondNode["connections"] or int(node2) in firstNode["connections"]:
			return jsonify({"Error": "Connection already exists."})
		else:
			secondNode["connections"].append(int(node1))
			firstNode["connections"].append(int(node2))
			newDict.append(secondNode)
			newDict.append(firstNode)
			newDict = {
				"nodes": newDict
			}
			updatedNodes = [firstNode, secondNode]
			with open(DATA_FN, "w") as f:
				json.dump(newDict, f, indent=2)
			return jsonify({"updatedNodes": updatedNodes})

@app.route("/connections/<string:node1>/<string:node2>", methods=['DELETE'])
def deleteConnection(node1, node2):
	with open(DATA_FN, "r") as f:
		nodes = json.load(f)["nodes"]
	firstNode = [d for d in nodes if int(d["id"]) == int(node1)]
	secondNode = [d for d in nodes if int(d["id"]) == int(node2)]
	if len(firstNode) == 0 or len(secondNode) == 0:
		return jsonify({"Error": "Cannot find node."})
	else:
		firstNode = firstNode[0]
		secondNode = secondNode[0]
		newDict = [d for d in nodes if int(d["id"]) != int(node1) and int(d["id"]) != int(node2)]
		if int(node1) in secondNode["connections"] or int(node2) in firstNode["connections"]:
			secondNode['connections'].remove(int(node1))
			firstNode['connections'].remove(int(node2))
			newDict.append(secondNode)
			newDict.append(firstNode)
			updatedNodes = [firstNode, secondNode]
			updatedDict = {
				"nodes": newDict
			}
			with open(DATA_FN, "w") as f:
				json.dump(updatedDict, f, indent=2)
			return jsonify({"updatedNodes": updatedNodes})
		else:
			return jsonify({"Error": "Connection does not exist."})

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
"""

if __name__ == "__main__":
	app.run()
