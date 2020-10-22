import requests
import json

class OrchHelper:

    def __init__(self, ipaddress):
        self.ipaddress = ipaddress
        self.url_prefix = "https://" + ipaddress + ":443/gms/rest"
        self.session = requests.Session()
        self.data = {}
        self.user = "admin"
        self.password = "admin" 
        
    def login(self):
        try:
            response = self.post("/authentication/login", {"user": self.user, "password": self.password})
            if response.status_code == 200:
                print("{0}: Orch login success".format(self.ipaddress))
                return True
            else:
                print("{0}: Orch login failed: {1}".format(self.ipaddress, response.text))
                return False
        except:
            print("{0}: Unable to connect to Orch appliance".format(self.ipaddress))
            return False

    def logout(self):
        response = self.get("/authentication/logout")
        if response.status_code == 200:
            print("{0}: Orch logout success".format(self.ipaddress))
        else:
            print("{0}: Orch logout failed: {1}".format(self.ipaddress, response.text))
        pass


########## NEW NOT IN PUBLIC SOURCE ########

    def get_all_preconfig(self):
        # GET operation to retrieve list of preconfigs
        # JSON response is a list object
        response = self.get("/gms/appliance/preconfiguration?filter=metadata")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve preconfig metadata from Orch at {0}".format(self.ipaddress))
            return False

    def delete_preconfig(self, preconfigId):
        # DELETE operation to delete specific preconfig by preconfig id number (preconfigId)
        response = self.delete("/gms/appliance/preconfiguration/" + preconfigId)
        if response.status_code == 200:
            return True
        else:
            print("Failed to delete preconfig id:{0} from Orch at {1}".format(preconfigId,self.ipaddress))
            return False

    def delete_appliance_for_rediscovery(self, nePk):
        # DELETE operation to delete specific appliance for rediscovery
        response = self.delete("/appliance/deleteForDiscovery/" + nePk)
        if response.status_code == 200:
            return True
        else:
            print("Failed to delete appliance id:{0} from Orch at {1}".format(preconfigId,self.ipaddress))
            return False

    def get_all_denied_appliances(self):
        # GET operation to retrive all discovered denied appliances
        response = self.get("/appliance/denied")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve discovered denied appliances from Orch at {0}".format(self.ipaddress))
            return False

    def get_all_appliances(self):
        # GET operation to retrive all in-use appliances
        response = self.get("/appliance")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve appliances from Orch at {0}".format(self.ipaddress))
            return False

    def approve_and_apply_preconfig(self, preconfigId, discovered_id):
        # POST operation to approve a discovered appliance and apply specific preconfig (preconfigId)
        response = self.empty_post("/gms/appliance/preconfiguration/{0}/apply/discovered/{1}".format(preconfigId,discovered_id))
        if response.status_code == 200:
            return True
        else:
            print("Failed to approve appliance (discovery id:{0}) and apply preconfiguration (preconfigId:{1}) discovered denied appliances from Orch at {2}".format(discovered_id,preconfigId,self.ipaddress))
            return False

    def apply_preconfig_to_existing(self, preconfigId, nePk):
        # POST operation to apply preconfig to an existing managed appliance
        response = self.empty_post("/gms/appliance/preconfiguration/{0}/apply/{1}".format(preconfigId,nePk))
        if response.status_code == 200:
            return True
        else:
            print("Failed to apply preconfig (id: {0}) to appliance (nePk:{1}) from Orch at {2}".format(preconfigId,nePk,self.ipaddress))
            return False    

    def broadcast_cli(self, appliance_list, cli_commands):
        # POST operation to send broadcast CLI commands to list of appliances
        response = self.post("/broadcastCli",{"neList": appliance_list, "cmdList": cli_commands})
        if response.status_code == 200:
            return True
        else:
            print("Failed to perform broadcast cli on the appliances {0} from Orch at {1}".format(appliance_list,self.ipaddress))
            return False



        
    def post(self, url, data):
        requests.packages.urllib3.disable_warnings()
        response = self.session.post(self.url_prefix + url, json=data, timeout=120, verify=False)
        return response
        
    def empty_post(self, url):
        requests.packages.urllib3.disable_warnings()
        response = self.session.post(self.url_prefix + url, timeout=120, verify=False)
        return response
        
    def put(self, url, data):
        requests.packages.urllib3.disable_warnings()
        response = self.session.put(self.url_prefix + url, json=data, timeout=120, verify=False)
        return response

    def get(self, url):
        requests.packages.urllib3.disable_warnings()
        response = self.session.get(self.url_prefix + url, timeout=120, verify=False)
        return response

    def delete(self, url):
        requests.packages.urllib3.disable_warnings()
        response = self.session.delete(self.url_prefix + url, timeout=120, verify=False)
        return response
        

