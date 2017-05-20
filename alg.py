import json

with open('json/pump.json') as data_file:    
    	data = json.load(data_file)

def algFindIso(node):
	for i in data["Nodes"]:
		if i["id"] == node:
			

if __name__=="__main__":
    algFindIso(0)

	
	
