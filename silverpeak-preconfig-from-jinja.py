# Standard library imports
import csv
import datetime
import json
import os
import time
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import yaml

# Third party imports
import colored
from colored import stylize
from dotenv import load_dotenv
from jinja2 import Template, FileSystemLoader, Environment, PackageLoader, select_autoescape

# Local application imports
from sp_orchhelper import OrchHelper
import post_yaml_to_orch


def comma_separate(cs_string_list):
    # Blank List
    cs_list = []
    # Convert string to comma separated list
    cs_string_list = cs_string_list.split(",")
    # Strip leading/trailing whitespace from items
    for item in cs_string_list:
        cs_list.append(item.strip())
    return cs_list

# Disable Certificate Warnings
urllib3.disable_warnings(category=InsecureRequestWarning)

# Console text highlight color parameters
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")

# Load environment variables
load_dotenv()

# Set Orchestrator login from .env
orch = OrchHelper(str(os.getenv('ORCH_URL')), os.getenv('ORCH_USER'), os.getenv('ORCH_PASSWORD'))


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
    # Connect to Orchestrator
    orch.login()

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

            # Convert list strings to comma separated list, strips leading/trailing whitespace
            row['templateGroups'] = comma_separate(row['templateGroups'])
            row['businessIntentOverlays'] = comma_separate(row['businessIntentOverlays'])

            # Render Jinja template
            preconfig = ec_template.render(data=row)

            # Write local YAML file
            output_filename = row['hostname'] + "_preconfig.yml"

            with open(local_config_directory + output_filename, 'w') as preconfig_file:
                write_data = preconfig_file.write(preconfig)

            # If option was chosen, upload preconfig to Orchestrator with selected auto-apply settings
            if upload_to_orch == "y":
                #post_yaml_to_orch.post(orch, row['hostname'], row['serial_number'], yaml.dump(yaml.load(preconfig,Loader=yaml.SafeLoader), default_flow_style=False), autoApply)
                post_yaml_to_orch.post(orch, row['hostname'], row['serial_number'], preconfig, autoApply)
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

# Logout from Orchestrator if logged in
if upload_to_orch == "y":
    orch.logout()
else:
    pass