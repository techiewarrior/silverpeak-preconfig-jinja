from dotenv import load_dotenv
import csv
from jinja2 import Template, FileSystemLoader, Environment, PackageLoader, select_autoescape
import yaml
import time
import colored
from colored import stylize

# Silver Peak Orchestrator Connectors
from orchhelp import OrchHelper
import post_yaml_to_orch

# For SFTP Transfer of Switch Config
import os

# Console text highlight color parameters
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")

# Load environment variables
load_dotenv()

# Set Orchestrator login from .env
orch = OrchHelper(str(os.getenv('ORCH_IP_ADDRESS')))
orch.user = os.getenv('ORCH_USERNAME')
orch.password = os.getenv('ORCH_PASSWORD')

# Retrieve Jinja2 template for generating EdgeConnect Preconfig YAML file
env = Environment(loader=FileSystemLoader("templates"))
ec_template_file = "ec_preconfig_template.jinja2"
ec_template = env.get_template(ec_template_file)
print("Using " + stylize(ec_template_file,blue_text) + " for EdgeConnect jinja template")

# Local directory for configuration outputs
local_config_directory = "preconfig_outputs/"

if not os.path.exists(local_config_directory):
    os.makedirs(local_config_directory)


# Enter source CSV file for config generation data
correct_file = "n"

while correct_file != "y":
    filename = input("Please enter source csv filename: ")
    print("Using " + stylize(filename,green_text) + " for configuration source data")
    correct_file = input("Do you want to proceed with that source file?(y/n, q to quit): ")
    if correct_file == "q":
        exit()
    else:
        pass

# Default autoApply to False
autoApply = False

# Check if user wants to upload preconfigs to Orchestrator
upload_to_orch = input("Do you want to upload the generated Preconfigs to Orchestrator?(y/n, other to quit): ")
if upload_to_orch == "y":
    # Check if user wants to auto-approve appliances matching uploaded preconfigs
    auto_approve_check = input("Do you want to auto-approve discovered appliances matching the preconfigs?(y/n, other to quit): ")
    if auto_approve_check == "y":
        autoApply = True
    elif auto_approve_check == "n":
        autoApply = False
    else:
        exit()
elif upload_to_orch == "n":
    pass
else:
    exit()


# Connect to Orchestrator
orch.login()

with open(filename, encoding='utf-8-sig') as csvfile:
    csv_dict = csv.DictReader(csvfile)

    # Set initial row number for row identification
    row_number = 1

    # Track hosts added for Orchestrator approval
    silverpeak_hostname_list = []

    # For each row/site in configuration file, generate Silver Peak and Aruba configurations
    for row in csv_dict:

        # Render EdgeConnect YAML Preconfig File from Jinja template
        if row['hostname'] != "":
            print("Rendering EdgeConnect template for " + stylize(row['hostname'],blue_text) + " from row " + str(row_number))

            silverpeak_hostname_list.append(row['hostname'])

            preconfig = ec_template.render(
            hostname=row['hostname'],
            group=row['group'],
            site=row['site'],
            networkRole=row['networkRole'],
            region=row['region'],
            address=row['address'],
            address2=row['address2'],
            city=row['city'],
            state=row['state'],
            zipCode=row['zipCode'],
            country=row['country'],
            name=row['name'],
            email=row['email'],
            phoneNumber=row['phoneNumber'],

            template_group_1=row['template_group_1'],
            template_group_2=row['template_group_2'],
            template_group_3=row['template_group_3'],
            template_group_4=row['template_group_4'],

            overlay_1=row['overlay_1'],
            overlay_2=row['overlay_2'],
            overlay_3=row['overlay_3'],
            overlay_4=row['overlay_4'],
            overlay_5=row['overlay_5'],
            overlay_6=row['overlay_6'],
            overlay_7=row['overlay_7'],

            totalOutboundBandwidth=row['totalOutboundBandwidth'],
            totalInboundBandwidth=row['totalInboundBandwidth'],
            outboundMaxBandwidth=row['outboundMaxBandwidth'],

            LAN_INT1_NAME=row['lan_interface_1_name'],
            LAN_INT1_DESC=row['lan_interface_1_desc'],
            LAN_INT1_IPMASK=row['lan_interface_1_ipmask'],
            LAN_INT1_NEXTHOP=row['lan_interface_1_nexthop'],
            LAN_INT1_SEGMENT=row['lan_interface_1_segment'],
            LAN_INT1_ZONE=row['lan_interface_1_zone'],

            LAN_INT2_NAME=row['lan_interface_2_name'],
            LAN_INT2_DESC=row['lan_interface_2_desc'],
            LAN_INT2_IPMASK=row['lan_interface_2_ipmask'],
            LAN_INT2_NEXTHOP=row['lan_interface_2_nexthop'],
            LAN_INT2_SEGMENT=row['lan_interface_2_segment'],
            LAN_INT2_ZONE=row['lan_interface_2_zone'],

            LAN_INT3_NAME=row['lan_interface_3_name'],
            LAN_INT3_DESC=row['lan_interface_3_desc'],
            LAN_INT3_IPMASK=row['lan_interface_3_ipmask'],
            LAN_INT3_NEXTHOP=row['lan_interface_3_nexthop'],
            LAN_INT3_SEGMENT=row['lan_interface_3_segment'],
            LAN_INT3_ZONE=row['lan_interface_3_zone'],

            WAN_INT1_NAME=row['wan_interface_1_name'],
            WAN_INT1_DESC=row['wan_interface_1_desc'],
            WAN_INT1_LABEL=row['wan_interface_1_label'],
            WAN_INT1_OUTBOUND_MAX=row['wan_interface_1_max_outbound_bw'],
            WAN_INT1_INBOUND_MAX=row['wan_interface_1_max_inbound_bw'],
            WAN_INT1_IPMASK=row['wan_interface_1_ipmask'],
            WAN_INT1_NEXTHOP=row['wan_interface_1_nexthop'],
            WAN_INT1_FIREWALL_MODE=row['wan_interface_1_firewall_mode'],
            WAN_INT1_NAT=row['wan_interface_1_behind_nat'],
            WAN_INT1_ZONE=row['wan_interface_1_zone'],
            CONFIGURE_DHCP=row['configure_dhcp'],

            DHCP_RELAY_SERVER_1=row['dhcp_relay_server_1'],
            DHCP_RELAY_SERVER_2=row['dhcp_relay_server_2'],

            DHCP_INT1_NAME=row['dhcp_interface_1'],
            DHCP_INT1_TYPE=row['dhcp_interface_1_type'],
            DHCP_INT1_NETWORK=row['dhcp_interface_1_network'],
            DHCP_INT1_START_ADDRESS=row['dhcp_interface_1_srv_start_address'],
            DHCP_INT1_END_ADDRESS=row['dhcp_interface_1_srv_end_address'],
            DHCP_INT1_GATEWAY=row['dhcp_interface_1_srv_gateway'],
            DHCP_INT1_DNS_SERVER_1=row['dhcp_interface_1_srv_dns1'],
            DHCP_INT1_DNS_SERVER_2=row['dhcp_interface_1_srv_dns2'],
            DHCP_INT1_NTP_SERVER_1=row['dhcp_interface_1_srv_ntp'],
            DHCP_INT1_OPTION1=row['dhcp_interface_1_srv_opt1'],
            DHCP_INT1_OPTION1_VALUE=row['dhcp_interface_1_srv_opt1value'],
            DHCP_INT1_OPTION2=row['dhcp_interface_1_srv_opt2'],
            DHCP_INT1_OPTION2_VALUE=row['dhcp_interface_1_srv_opt2value'],

            DHCP_INT2_NAME=row['dhcp_interface_2'],
            DHCP_INT2_TYPE=row['dhcp_interface_2_type'],
            DHCP_INT2_NETWORK=row['dhcp_interface_2_network'],
            DHCP_INT2_START_ADDRESS=row['dhcp_interface_2_srv_start_address'],
            DHCP_INT2_END_ADDRESS=row['dhcp_interface_2_srv_end_address'],
            DHCP_INT2_GATEWAY=row['dhcp_interface_2_srv_gateway'],
            DHCP_INT2_DNS_SERVER_1=row['dhcp_interface_2_srv_dns1'],
            DHCP_INT2_DNS_SERVER_2=row['dhcp_interface_2_srv_dns2'],
            DHCP_INT2_NTP_SERVER_1=row['dhcp_interface_2_srv_ntp'],
            DHCP_INT2_OPTION1=row['dhcp_interface_2_srv_opt1'],
            DHCP_INT2_OPTION1_VALUE=row['dhcp_interface_2_srv_opt1value'],
            DHCP_INT2_OPTION2=row['dhcp_interface_2_srv_opt2'],
            DHCP_INT2_OPTION2_VALUE=row['dhcp_interface_2_srv_opt2value'],

            DHCP_INT3_NAME=row['dhcp_interface_3'],
            DHCP_INT3_TYPE=row['dhcp_interface_3_type'],
            DHCP_INT3_NETWORK=row['dhcp_interface_3_network'],
            DHCP_INT3_START_ADDRESS=row['dhcp_interface_3_srv_start_address'],
            DHCP_INT3_END_ADDRESS=row['dhcp_interface_3_srv_end_address'],
            DHCP_INT3_GATEWAY=row['dhcp_interface_3_srv_gateway'],
            DHCP_INT3_DNS_SERVER_1=row['dhcp_interface_3_srv_dns1'],
            DHCP_INT3_DNS_SERVER_2=row['dhcp_interface_3_srv_dns2'],
            DHCP_INT3_NTP_SERVER_1=row['dhcp_interface_3_srv_ntp'],
            DHCP_INT3_OPTION1=row['dhcp_interface_3_srv_opt1'],
            DHCP_INT3_OPTION1_VALUE=row['dhcp_interface_3_srv_opt1value'],
            DHCP_INT3_OPTION2=row['dhcp_interface_3_srv_opt2'],
            DHCP_INT3_OPTION2_VALUE=row['dhcp_interface_3_srv_opt2value'],

            DHCP_MAX_LEASE=row['dhcp_max_lease'],
            DHCP_DEFAULT_LEASE=row['dhcp_default_lease'],

            LICENSE_BANDWIDTH=row['license_bandwidth'],
            LICENSE_BOOST=row['license_boost'],

            static_route_1_subnet=row['static_route_1_subnet'],
            static_route_1_nexthop=row['static_route_1_nexthop'],
            static_route_1_interface=row['static_route_1_interface'],
            static_route_1_metric=row['static_route_1_metric'],
            static_route_1_advertise=row['static_route_1_advertise'],
            static_route_1_comment=row['static_route_1_comment'],

            silverpeak_bgp_asn=row['silverpeak_bgp_asn'],
            silverpeak_bgp_id=row['silverpeak_bgp_id'],
            switch_bgp_ip=row['switch_bgp_ip'],
            switch_bgp_asn=row['switch_bgp_asn'],
            )

            output_filename = row['hostname'] + "_preconfig.yml"

            with open(local_config_directory + output_filename, 'w') as preconfig_file:
                write_data = preconfig_file.write(preconfig)

            # If option was chosen, upload preconfig to Orchestrator with selected auto-approve settings
            if upload_to_orch == "y":
                post_yaml_to_orch.post(orch, row['hostname'], row['serial_number'], yaml.dump(yaml.load(preconfig,Loader=yaml.SafeLoader), default_flow_style=False), autoApply)
                print("Posted EC Preconfig " + stylize(row['hostname'],blue_text))
            else:
                pass

            row_number = row_number + 1

        else:
            print("No hostname for Silver Peak EdgeConnect from row " + stylize(row_number,red_text) + ": no preconfig created")
            
            row_number = row_number + 1


# If auto-apply option was chosen, also approve any matching appliances in denied discovered list
if autoApply == True:

    # Retrieve all denied discovered appliances from Orchestrator
    all_denied_appliances = orch.get_all_denied_appliances().json()

    # Retrieve all preconfigs from Orchestrator
    all_preconfigs = orch.get_all_preconfig().json()

    # Dict of Denied Appliances to approve with discovered_id and preconfig_id to apply
    approve_dict = {}

    # For each EdgeConnect host in the source csv
    # check against all preconfigs for matching tag
    # and check against all discovered denied appliances with the same tag that are reachable
    for host in silverpeak_hostname_list:
        for preconfig in all_preconfigs:
            for appliance in all_denied_appliances:
                if (host == preconfig['name'] == appliance['applianceInfo']['site'] and appliance['applianceInfo']['reachabilityStatus'] == 1):
                    approve_dict[host] = {'discovered_id':appliance['id'],'preconfig_id':preconfig['id']}
                else:
                    pass

    # Approve and apply corresponding preconfig for each of the matched appliances
    # This simulates the functionality of 'auto-approve' with previously denied/deleted devices
    for appliance in approve_dict:
        orch.approve_and_apply_preconfig(approve_dict[appliance]['preconfig_id'],approve_dict[appliance]['discovered_id'])

else:
    pass

# Logout from Orchestrator
orch.logout()