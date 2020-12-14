# Standard library imports
import argparse
import csv
import datetime
import json
import os
import time

# Third party imports
import colored
import urllib3
import yaml
from colored import stylize
from dotenv import load_dotenv
from jinja2 import (
    Environment,
    FileSystemLoader,
    PackageLoader,
    Template,
    select_autoescape,
)
from urllib3.exceptions import InsecureRequestWarning

# Local application imports
from silverpeak_python_sdk import OrchHelper

# Disable Certificate Warnings
urllib3.disable_warnings(category=InsecureRequestWarning)


def comma_separate(cs_string_list):
    # Blank List
    cs_list = []
    # Convert string to comma separated list
    cs_string_list = cs_string_list.split(",")
    # Strip leading/trailing whitespace from items
    for item in cs_string_list:
        cs_list.append(item.strip())
    return cs_list


def get_csv_file():
    # Enter source CSV file for config generation data
    correct_file = "n"

    while correct_file != "y":
        csv_filename = input("Please enter source csv filename: ")
        print(
            "Using {} for configuration source data".format(
                stylize(csv_filename, green_text)
            )
        )
        correct_file = input(
            "Do you want to proceed with that source file?(y/n, q to quit): "
        )
        if correct_file == "q":
            exit()
        else:
            pass

    return csv_filename


def prompt_for_orch_upload():
    # Check if user wants to upload preconfigs to Orchestrator
    upload_to_orch = input(
        "Upload the generated Preconfigs to Orchestrator?(y/n, other key to quit): "
    )
    if upload_to_orch == "y":
        return True
    if upload_to_orch == "n":
        return False
    else:
        exit()


def prompt_for_auto_apply(discovered_appiance_type):
    # Check if user wants to auto-approve appliances matching uploaded preconfigs
    auto_approve_check = input(
        "Do you want to auto-approve {} appliances matching the preconfigs?(y/n, other to quit): ".format(
            discovered_appiance_type
        )
    )
    if auto_approve_check == "y":
        return True
    elif auto_approve_check == "n":
        return False
    else:
        exit()


# Console text highlight color parameters
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--upload", help="Upload created preconfigs to Orchestrator", type=bool
)
parser.add_argument(
    "--autoapply", help="Mark uploadded preconfigs for auto-approve", type=bool
)
parser.add_argument(
    "--autodenied",
    help="Approve and apply preconfig to matching denied appliances",
    type=bool,
)
parser.add_argument("--csv", help="specify source csv file for preconfigs", type=str)
parser.add_argument("--jinja", help="specify source jinja2 template", type=str)
parser.add_argument("--vault", help="specify source vault URL", type=str)
parser.add_argument("--orch, -o", help="specify Orchestrator URL", type=str)
args = parser.parse_args()

# Load environment variables
load_dotenv()

# If Vault argument or Vault URL present in env
# retrieve Orch credentials from Vault
if vars(args)["vault"] is not None:
    vault_url = vars(args)["vault"]
elif os.getenv("VAULT_URL") is not None:
    vault_url = os.getenv("VAULT_URL")
elif vars(args)["orch"] is not None:
    orch = OrchHelper(vars(args)["orch"])
    orch_user = os.getenv("ORCH_USER")
    orch_pw = os.getenv("ORCH_PASSWORD")
else:
    orch = OrchHelper(str(os.getenv("ORCH_URL")))
    orch_user = os.getenv("ORCH_USER")
    orch_pw = os.getenv("ORCH_PASSWORD")


## TODO
# Get Orch credentials from VAULT


# Obtain Jinja2 template file for generating preconfig
if vars(args)["jinja"] is not None:
    ec_template_file = vars(args)["csv"]
else:
    ec_template_file = "ec_preconfig_template.jinja2"

# Retrieve Jinja2 template for generating EdgeConnect Preconfig YAML file
env = Environment(loader=FileSystemLoader("templates"))
ec_template = env.get_template(ec_template_file)
print(
    "Using {} for EdgeConnect jinja template".format(
        stylize(ec_template_file, blue_text)
    )
)

# Local directory for configuration outputs
local_config_directory = "preconfig_outputs/"
if not os.path.exists(local_config_directory):
    os.makedirs(local_config_directory)

# Obtain CSV file for generating preconfigs
if vars(args)["csv"] is not None:
    csv_filename = vars(args)["csv"]
else:
    get_csv_file()

# Check if configs should be uploaded to Orchestrator
if vars(args)["upload"] is not None:
    upload_to_orch = vars(args)["upload"]
else:
    upload_to_orch = prompt_for_orch_upload()

# If uploading to Orchestrator check if preconfigs should be marked for auto-approve
if vars(args)["autoapply"] is not None:
    auto_apply = vars(args)["autoapply"]
elif upload_to_orch == True:
    auto_apply = prompt_for_auto_apply("DISCOVERED")
else:
    pass

# If auto-apply, check if should also approve matching appliances that are currently denied
if vars(args)["autodenied"] is not None:
    auto_apply_denied = vars(args)["autodenied"]
elif auto_apply == True:
    auto_apply_denied = prompt_for_auto_apply("DENIED")
else:
    pass


# Connect to Orchestrator
orch.login(orch_user, orch_pw)

# Open CSV file
with open(csv_filename, encoding="utf-8-sig") as csvfile:
    csv_dict = csv.DictReader(csvfile)

    # Set initial row number for row identification
    row_number = 1

    # Track hosts added for Orchestrator approval
    silverpeak_hostname_list = []

    # For each row/site in configuration file, generate Silver Peak and Aruba configurations
    for row in csv_dict:

        # Render EdgeConnect YAML Preconfig File from Jinja template
        if row["hostname"] != "":
            print(
                "Rendering EdgeConnect template for {} from row {}".format(
                    stylize(row["hostname"], blue_text), str(row_number)
                )
            )

            silverpeak_hostname_list.append(row["hostname"])

            # Convert list strings to comma separated list, strips leading/trailing whitespace
            row["templateGroups"] = comma_separate(row["templateGroups"])
            row["businessIntentOverlays"] = comma_separate(
                row["businessIntentOverlays"]
            )

            # Render Jinja template
            preconfig = ec_template.render(data=row)

            # Validate preconfig via Orchestrator
            validate = orch.validate_preconfig(
                row["hostname"], row["serial_number"], preconfig, auto_apply
            )

            if validate.status_code == 200:

                # Write local YAML file
                output_filename = "{}_preconfig.yml".format(row["hostname"])

                with open(
                    local_config_directory + output_filename, "w"
                ) as preconfig_file:
                    write_data = preconfig_file.write(preconfig)

                # If option was chosen, upload preconfig to Orchestrator with selected auto-apply settings
                if upload_to_orch == True:

                    orch.create_preconfig(
                        row["hostname"],
                        row["serial_number"],
                        preconfig,
                        auto_apply,
                    )
                    print(
                        "Posted EC Preconfig {}".format(
                            stylize(row["hostname"], blue_text)
                        )
                    )
                else:
                    pass
            else:
                print("Preconfig failed validation")

            row_number = row_number + 1

        else:
            print(
                "No hostname for Silver Peak EdgeConnect from row {}: no preconfig created".format(
                    stylize(row_number, red_text)
                )
            )

            row_number = row_number + 1


# If auto-apply option was chosen, also approve any matching appliances in denied discovered list
if auto_apply_denied == True:

    # Retrieve all denied discovered appliances from Orchestrator
    all_denied_appliances = orch.get_all_denied_appliances()

    # Retrieve all preconfigs from Orchestrator
    all_preconfigs = orch.get_all_preconfig()

    # Dict of Denied Appliances to approve with discovered_id and preconfig_id to apply
    approve_dict = {}

    # For each EdgeConnect host in the source csv
    # check against all preconfigs for matching tag
    # and check against all discovered denied appliances with the same tag that are reachable
    for host in silverpeak_hostname_list:
        for preconfig in all_preconfigs:
            for appliance in all_denied_appliances:
                if (
                    host == preconfig["name"] == appliance["applianceInfo"]["site"]
                    and appliance["applianceInfo"]["reachabilityStatus"] == 1
                ):
                    approve_dict[host] = {
                        "discovered_id": appliance["id"],
                        "preconfig_id": preconfig["id"],
                    }
                else:
                    pass

    # Approve and apply corresponding preconfig for each of the matched appliances
    # This simulates the functionality of 'auto-approve' with previously denied/deleted devices
    for appliance in approve_dict:
        orch.approve_and_apply_preconfig(
            approve_dict[appliance]["preconfig_id"],
            approve_dict[appliance]["discovered_id"],
        )

else:
    pass

# Logout from Orchestrator if logged in
orch.logout()
