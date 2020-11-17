import base64


def post(orch, hostname, serial, yaml_text, autoApply):
	# convert from a string to base64,
	# then post that b64 output as a string to Orch
	yaml_upload = yaml_to_b64string(yaml_text)
	data = {}
	data['name'] = hostname 
	data['configData'] = yaml_upload
	data['autoApply'] = autoApply
	data['tag'] = hostname
	data['serialNum'] = serial
	r = orch.post("/gms/appliance/preconfiguration/validate", data)
	if(r.status_code == 200):
		orch.post("/gms/appliance/preconfiguration/", data)
		#print("Success")
	else:
		print("Problem with upload")
		print(r.text)

def yaml_to_b64string(yaml):
    yaml_byte = yaml.encode('utf-8')
    yaml_b64 = base64.b64encode(yaml_byte)
    yaml_upload = str(yaml_b64)
    # take off the (b' ') portion
    yaml_upload = yaml_upload[2:-1]
    return yaml_upload

def b64string_to_yaml(yaml_upload):
    yaml_byte = base64.b64decode(yaml_upload)
    yaml = yaml_byte.decode('utf-8')
    yaml = bytes(yaml, 'utf-8').decode("unicode_escape")
    return yaml