#
# sp_orchhelper.py - basic Orchestrator helper class that includes functions to facilitate login, logout, and issue REST GET/POST/DELETE/PUT calls over a session
# 
# Your use of this Software is pursuant to the Silver Peak Disclaimer (see the README file for this repository)
# 
# Last update: Jul 2020
# 

import requests

#optional python module for supporting hidden password entry. See getpass.getpass() function.
import getpass 


class OrchHelper:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.url_prefix = "https://" + url + "/gms/rest"
        self.session = requests.Session()
        self.headers = {}
        self.apiSrcId = "?source=menu_rest_apis_id"  #for API calls w/ just source as query param
        self.apiSrcId2 = "&source=menu_rest_apis_id" #for API calls w/ multiple query params
        self.supportedAuthModes = ["local","radius","tacacs"] #remote authentication modes supported via this helper module
        self.authMode = "local"   # change this to the desired auth mode before invoking login() function.
        #requests.packages.urllib3.disable_warnings() #disable certificate warning messages 

########## login ##########

    def login (self):
        # basic login function without multi-factor authentication
        # NOTE: if the userId is using RBAC, they must have R/O or R/W access to the REST API functionality to access the APIs
        # Returns True if login succeeds, False if exception raised or failure to login

        if self.authMode not in self.supportedAuthModes:
            print("{0}: authentication mode not supported".format(self.authMode))
            return False
        
        try:
            response = self.post("/authentication/login",
                                 {"user": self.user, "password": self.password, "loginType": self.supportedAuthModes.index(self.authMode)})
            if response.status_code == 200:
                print ("{0}: Orchestrator login success".format(self.url))
                # get and set X-XSRF-TOKEN
                for cookie in response.cookies:
                    if cookie.name == "orchCsrfToken":
                        self.headers["X-XSRF-TOKEN"] = cookie.value
                return True
            else:
                print ("{0}: Orchestrator login failed: {1}".format(self.url, response.text))
                return False
        except:
            print("{0}: Exception - unable to connect to Orchestrator".format(self.url))
            return False

    def mfa_login (self, mfacode):
        # alternative login function for multi-factor authentication
        # mfacode is integer value that is provided by Orchestrator after providing initial userid and passwd
        # To use mfa_login, first request the mfacode using send_mfa(). An MFA code will be sent depending on how the user is configured.
        # Then call this function with the provided MFA code.
        #
        # NOTE: if the userId is using RBAC, they must have R/O or R/W access to the REST API functionality to access the APIs
        # Returns True if login succeeds, False if exception raised or failure to login
        
        try:
            response = self.post("/authentication/login", {"user": self.user, "password": self.password, "token": int(mfacode)})
            if response.status_code == 200:
                print ("{0}: Orchestrator MFA login success".format(self.url))
                # get and set X-XSRF-TOKEN
                for cookie in response.cookies:
                    if cookie.name == "orchCsrfToken":
                        self.headers["X-XSRF-TOKEN"] = cookie.value
                return True
            else:
                print ("{0}: Orchestrator MFA login failed: {1}".format(self.url, response.text))
                return False
        except:
            print("{0}: Exception - unable to connect to Orchestrator".format(self.url))
            return False
             
    def send_mfa(self):
        # send request to Orchestrator to issue MFA token to user
        # returns True on success, False on failure or exception
        try:
            response = self.post("/authentication/loginToken",{"user": self.user, "password": self.password, "TempCode": True})
        except:
            print("Exception - unable to submit token request")
            return False
        return True if response.status_code in [200,204] else False
        
    def logout(self):
        try:
            response = self.get("/authentication/logout")
            if response.status_code == 200:
                print ("{0}: Orchestrator logout success".format(self.url))
            else:
                print ("{0}: Orchestrator logout failed: {1}".format(self.url, response.text))
        except:
            print("{0}: Exception - unable to logout of Orchestrator".format(self.url))


    #def get_login_status(self):
        # GET /authentication/loginStatus
        # Get the current authentication status of the HTTP session

    #def validate_password():
        # POST /authentication/password/validation
        # Authenticate user's password only, but doesn't mark user's status as login

    #def check_mfa_type():
        # POST /authentication/userAuthType
        # Check the two factor authentication methods the user requires to login

    #def check_mfa_type_active():
        # POST /authentication/userAuthTypeToken
        # Check the two factor authentication methods the user has active using a reset password token

    #def oauth_login():
        # GET /authentication/oauth/redirect
        # Login to Orchestrator using Oauth server

    #def oauth_state():
        # GET /authentication/oauth/stateToken
        # Returns the Oauth state token needed to login

    #def jwt_login():
        # GET /authentication/jwt
        # Used to login via JWT authentication

    #def saml_login():
        # POST /authentication/saml2/consume
        # Use to authenticate via SAML

    #def saml_logout():
        # GET /authentication/saml2/logout
        # Logout of Orchestrator via SAML


########## gmsLicense ##########

    #def get_gms_license():
       # GET /gmsLicense
       # Get current license key and information

    #def set_gms_license():
        # POST /gmsLicense
        # Set Orchestrator license key

    #def validate_gms_license():
        # GET /gmsLicense/validation
        # Validate a new license key

########## appliance ##########

    def get_all_appliances(self):
        # GET operation to retrive all in-use appliances
        # JSON response is a list object
        response = self.get("/appliance")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve appliances from Orch at {0}".format(self.url))
            return False

    #def delete_appliance():
        # DELETE /appliance/{nePk}
        # Delete an appliance from network.

    #def get_appliances_queued_for_deletion():
        # GET /appliance/queuedForDeletion
        # Lists appliances ( appliance primary keys) that are queued on the Orchestrator for deletion.

    def delete_appliance_for_rediscovery(self, nePk):
        # DELETE operation to delete specific appliance for rediscovery
        response = self.delete("/appliance/deleteForDiscovery/" + nePk)
        if response.status_code == 200:
            return True
        else:
            print("Failed to delete appliance id:{0} from Orch at {1}".format(nePk,self.url))
            return False

    #def modify_appliance():
        # POST /appliance/{nePk}
        # Modify an appliance's IP address, username, password, networkRole, and webProtocol.

    #def change_appliance_group():
        # POST /appliance/changeGroup/{groupPk}
        # Change one or more appliances' group

    #def get_appliance_info():
        # GET /appliance/{nePk}
        # Get appliance information

    #def get_all_discovered():
        # GET /appliance/discovered
        # Returns the all discovered appliances

    #def get_all_approved():
        # GET /appliance/approved
        # Get the all approved appliances

    def get_all_denied_appliances(self):
        # GET operation to retrive all discovered denied appliances
        response = self.get("/appliance/denied")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve discovered denied appliances from Orch at {0}".format(self.url))
            return False

    #def add_and_approve_discovered_appliances():
        # POST /appliance/discovered/approve/{key}
        # Add and approve discovered appliances

    #def add_discovered_appliances():
        # POST /appliance/discovered/add/{key}
        # Add discovered appliances to Orchestrator

    #def deny_appliance():
        # POST /appliance/discovered/deny/{id}
        # Deny discovered appliances.

    #def update_discovered_appliances():
        # PUT /appliance/discovered/update
        # Trigger discovered appliances update

    #def change_appliance_credentials():
        # POST /appliance/changePassword/{nePk}/{username}
        # Change a user's password on appliance.

    #def appliance_get_api():
        # GET /appliance/rest/{nePk}/{url : (.*)}
        # To communicate with appliance GET APIs directly.

    #def appliance_post_api():
        # POST /appliance/rest/{nePk}/{url : (.*)}
        # To communicate with appliance POST APIs directly.

    #def get_appliance_stats_config():
        # GET /appliance/statsConfig
        # To get stats config which will be synchronized to appliances.

    #def modify_appliance_stats_config():
        # POST /appliance/statsConfig
        # To modify stats config which will be synchronized to appliances.

    #def default_appliance_stats_config():
        # GET /appliance/statsConfig/default
        # To get default stats config which will be synchronized to appliances.

    #def get_appliance_dns_cache_config():
        # GET /appliance/dnsCache/config/{neId}?cached={cached}
        # Gets DNS Cache configurations


########## group ##########
########## grnode ##########
########## aggregateStats ##########
########## timeseriesStats ##########
########## realtimeStats ##########
########## template ##########

    def get_all_template_groups(self):
        # GET operation to retrieve all template groups
        response = self.get("/template/templateGroups")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve template groups from Orch at {0}".format(self.url))
            return False

    def get_template_group(self, templateGroup):
        # GET operation to retrieve template group contents
        templateGroup.replace(" ", "%20")
        response = self.get("/template/templateGroups/" + templateGroup)
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve template group {0} from Orch at {1}".format(templateGroup, self.url))
            return False
    
    def post_template_group(self, templateGroup, templateGroupBody):
        # POST operation to update existing template group
        templateGroup.replace(" ", "%20")
        response = self.post("/template/templateGroups/" + templateGroup, templateGroupBody)
        if response.status_code == 200:
            return True
        else:
            print (response.status_code)
            print("Failed to create or update template group {0} from Orch at {1}".format(templateGroup,self.url))
            return False

    def select_templates_for_template_group(self, templateGroup, selectedTemplates):
        # POST operation to select templates for existing template group
        templateGroup.replace(" ", "%20")
        response = self.post("/template/templateSelection/" + templateGroup, selectedTemplates)
        if response.status_code == 200:
            return True
        else:
            print("Failed to select templates {0} for template group {1} from Orch at {2}".format(selectedTemplates,templateGroup,self.url))
            return False

    
    def create_template_group(self, templateGroupBody):
        # POST operation to create new template group
        response = self.post("/template/templateCreate", templateGroupBody)
        if response.status_code == 200:
            return True
        elif response.status_code == 204:
            print("Created a !!EMPTY!! template group {0} with no selected templates from Orch at {1}".format(templateGroupBody['name'],self.url))
            return True
        else:
            print (response.status_code)
            print("Failed to create template group {0} from Orch at {1}".format(templateGroupBody['name'],self.url))
            return False

########## linkIntegrity ##########
########## routePolicy ##########
########## optimizationPolicy ##########
########## qosPolicy ##########
########## natPolicy ##########
########## acls ##########
########## shaper ##########
########## inboundShaper ##########
########## flow ##########
########## reachability ##########
########## tcpdump ##########
########## debugFiles ##########
########## logging ##########
########## appliancesSoftwareVersions ##########
########## wccp ##########
########## alarm ##########
########## netFlow ##########
########## gmsBackup ##########
########## gmsConfig ##########
########## tca ##########
########## applianceBackup ##########
########## interfaceState ##########
########## subnets ##########
########## saasOptimization ##########
########## vrrp ##########
########## spPortal ##########
########## saveChanges ##########
########## authentication ##########
########## disks ##########
########## userAccount ##########
########## activeSessions ##########
########## hostName ##########
########## maps ##########
########## dns ##########
########## networkMemory ##########
########## user ##########
########## ssl ##########
########## sslSubstituteCert ##########
########## sslCACertificate ##########
########## fileCreation ##########
########## applianceUpgrade ##########
########## scheduledJobs2 ##########
########## gmsServer ##########
########## releases ##########
########## application ##########
########## applicationGroup ##########
########## appSystemStateInfo ##########
########## appSystemDeployInfo ##########
########## networkRoleAndSite ##########
########## banners ##########
########## bridgeInterfaceState ##########
########## broadcastCli ##########

    def broadcast_cli(self, appliance_list, cli_commands):
        # POST operation to send broadcast CLI commands to list of appliances
        response = self.post("/broadcastCli",{"neList": appliance_list, "cmdList": cli_commands})
        if response.status_code == 200:
            return True
        else:
            print("Failed to perform broadcast cli on the appliances {0} from Orch at {1}".format(appliance_list,self.url))
            return False

########## bypass ##########
########## gmsRegistration ##########
########## gmsSMTP ##########
########## cache ##########
########## applianceResync ##########
########## snmp ##########
########## tunnelsConfiguration ##########
########## bondedTunnelsConfiguration ##########
########## thirdPartyTunnelsConfiguration ##########
########## gmsRemoteAuth ##########
########## upgradeAppliances ##########
########## discovery ##########
########## applianceWizard ##########
########## appliancePreconfig ##########

    def get_all_preconfig(self):
        # GET operation to retrieve list of preconfigs
        # JSON response is a list object
        response = self.get("/gms/appliance/preconfiguration?filter=metadata")
        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve preconfig metadata from Orch at {0}".format(self.url))
            return False

    def delete_preconfig(self, preconfigId):
        # DELETE operation to delete specific preconfig by preconfig id number (preconfigId)
        response = self.delete("/gms/appliance/preconfiguration/" + preconfigId)
        if response.status_code == 200:
            return True
        else:
            print("Failed to delete preconfig id:{0} from Orch at {1}".format(preconfigId,self.url))
            return False

    def approve_and_apply_preconfig(self, preconfigId, discovered_id):
        # POST operation to approve a discovered appliance and apply specific preconfig (preconfigId)
        response = self.empty_post("/gms/appliance/preconfiguration/{0}/apply/discovered/{1}".format(preconfigId,discovered_id))
        if response.status_code == 200:
            return True
        else:
            print("Failed to approve appliance (discovery id:{0}) and apply preconfiguration (preconfigId:{1}) discovered denied appliances from Orch at {2}".format(discovered_id,preconfigId,self.url))
            return False

    def apply_preconfig_to_existing(self, preconfigId, nePk):
        # POST operation to apply preconfig to an existing managed appliance
        response = self.empty_post("/gms/appliance/preconfiguration/{0}/apply/{1}".format(preconfigId,nePk))
        if response.status_code == 200:
            return True
        else:
            print("Failed to apply preconfig (id: {0}) to appliance (nePk:{1}) from Orch at {2}".format(preconfigId,nePk,self.url))
            return False    

########## thirdPartyLicenses ##########
########## license ##########
########## scheduleTimezone ##########
########## topologyConfig ##########
########## dynamicTopologyConfig ##########
########## session ##########
########## interfaceLabels ##########
########## overlays ##########
########## portProfiles ##########
########## actionLog ##########
########## overlayAssociation ##########
########## dhcpConfig ##########
########## applianceExtraInfo ##########
########## overlayManagerProperties ##########
########## menuTypeConfig ##########
########## tunnelGroups ##########
########## tunnelGroupAssociation ##########
########## gmsHttpsUpload ##########
########## location ##########
########## deployment ##########
########## vxoaHostname ##########
########## tunnelsConfig ##########
########## dnsInfo ##########
########## health ##########
########## advancedProperties ##########
########## applianceRebootHistory ##########
########## peerPriority ##########
########## wanNextHopHealth ##########
########## sessionTimeout ##########
########## IdleTime ##########
########## applianceCrashHistory ##########
########## services ##########
########## internalSubnets ##########
########## ipAllowList ##########
########## applicationDefinition ##########
########## haGroups ##########
########## avcMode ##########
########## ikeless ##########
########## gmsStatsCollection ##########
########## dbPartition ##########
########## adminDistance ##########
########## portForwarding ##########
########## bgp ##########
########## uiUsageStats ##########
########## restRequestTimeStats ##########
########## ospf ##########
########## remoteLogReceiver ##########
########## rmaWizard ##########
########## pauseOrchestration ##########
########## zones ##########
########## securityMaps ##########
########## brandCustomization ##########
########## builtInPolicies ##########
########## restApiConfig ##########
########## exception ##########
########## regions ##########
########## thirdPartyServices ##########
########## multicast ##########
########## nat ##########
########## rbacApplianceAccessGroup ##########
########## rbacAssignment ##########
########## rbacRole ##########
########## loopback ##########
########## loopbackOrch ##########
########## vti ##########
########## maintenanceMode ##########
########## gmsNotification ##########
########## dnsProxy ##########
########## customApplianceTags ##########
########## vrf ##########
########## securitySettings ##########
########## shell ##########
########## mgmtServices ##########
########## vrfSnatMaps ##########
########## vrfDnatMaps ##########
########## statsRetention ##########
########## apiKey ##########

    def post(self, url, data):
        apiSrcStr = self.apiSrcId if ("?" not in url) else self.apiSrcId2
        return self.session.post(self.url_prefix + url + apiSrcStr, json=data, verify=False, timeout=120, headers=self.headers)

    def get(self, url):
        apiSrcStr = self.apiSrcId if ("?" not in url) else self.apiSrcId2
        return self.session.get(self.url_prefix + url + apiSrcStr, verify=False, timeout=120, headers=self.headers)

    def delete(self, url):
        apiSrcStr = self.apiSrcId if ("?" not in url) else self.apiSrcId2
        return self.session.delete(self.url_prefix + url + apiSrcStr, verify=False, timeout=120, headers=self.headers)

    def put(self, url, data):
        apiSrcStr = self.apiSrcId if ("?" not in url) else self.apiSrcId2
        return self.session.put(self.url_prefix + url + apiSrcStr, json=data, verify=False, timeout=120, headers=self.headers)

# sample test code - only applies if this module is run as main
# this tests:
#   instantiation of an OrchHelper class
#   basic login capability, using local authentication
#   retrieval of the managed appliances
#   logout operation
# This code can be left in here when importing this class into other modules

if __name__ == "__main__":
    url = "" # enterURL of your orchestrator (without https:// prefix)
    user =  input("UserId: ")
    pwd = getpass.getpass("Password: ")
    o = OrchHelper(url, user, pwd)

    o.authMode = "local"  #not required as local is the default
    o.login()
    
    # for MFA login:
    #    o.send_mfa()
    #    mfa = input("Enter MFA code: ")
    #    o.mfa_login(mfa)
    
    appliances = o.get_all_appliances()
    print("Total appliances: ",len(appliances))
    
    o.logout()
    
