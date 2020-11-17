from dotenv import load_dotenv
import csv
import colored
from colored import stylize
import shutil

# ESXi VM on/off functions
from ztp_demo_esxi import esxiHelper

# Silver Peak Orchestrator Connectors
from orchhelp import OrchHelper

# For SFTP Transfer of Switch Config
import os
import paramiko

# To clear startup configuration on ACX
from netmiko import ConnectHandler
import time

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

# Set TFTP login from .env
tftp_server = str(os.getenv('TFTP_IP_ADDRESS'))
sftp_user = os.getenv('TFTP_USERNAME')
sftp_pass = os.getenv('TFTP_PASSWORD')

# Set ESXi login from .env
esxi = esxiHelper(str(os.getenv('ESXI_IP_ADDRESS')), )
esxi.user = os.getenv('ESXI_USERNAME')
esxi.password = os.getenv('ESXI_PASSWORD')

correct_file = "n"

while correct_file != "y":
    filename = input("Please enter source csv filename for cleanup: ")
    #filename = "ztp_demo_data.csv"
    print("Using " + stylize(filename,green_text) + " for configuration source data")
    correct_file = input("Do you want to proceed with that source file?(y/n, q to quit): ")
    if correct_file == "q":
        exit()
    else:
        pass

# Connect to Orchestrator
orch.login()

# Connect to TFTP SERVER
ssh = paramiko.SSHClient() 
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(tftp_server, username=sftp_user, password=sftp_pass)
sftp = ssh.open_sftp()
print(tftp_server + ": SFTP login success")

with open(filename, encoding='utf-8-sig') as csvfile:
    csv_dict = csv.DictReader(csvfile)

    all_preconfigs = orch.get_all_preconfig().json()
    all_switch_configs = sftp.listdir("/srv/tftp/")
    preconfigs_to_delete = []
    switch_configs_to_delete = []
    switches_to_erase = []
    silverpeak_hostname_list = []

    for row in csv_dict: 
        silverpeak_hostname_list.append(row['hostname'])
        for preconfig in all_preconfigs:
            if preconfig['name'] == row['hostname']:
                preconfigs_to_delete.append(preconfig['id'])
            else:
                pass
        for switch_config in all_switch_configs:
            if switch_config == row['switch_hostname']+".cfg":
                if switch_config not in switch_configs_to_delete:
                    switch_configs_to_delete.append(switch_config)
            else:
                pass
        if row['switch_mgmt_ipmask'] != "":
            switch_ip = row['switch_mgmt_ipmask'][:-3]
            if switch_ip not in switches_to_erase:
                switches_to_erase.append(switch_ip)

print("The following Preconfigs are queued for deletion:")
width = 10
print('\n'.join(''.join(str(preconfigs_to_delete[i:i+width])) for i in range(0, len(preconfigs_to_delete), width)))

print("Do you want to proceed to delete these preconfig files from Orchestrator?(y/n):")
proceed = input()
if (proceed == "y" or proceed == "Y"):
    for preconfigId in preconfigs_to_delete:
        orch.delete_preconfig(str(preconfigId))
        print("Deleted preconfig id:" + str(preconfigId))
    print(stylize("All requested preconfig files have been deleted from Orchestrator",green_text))
else:
    print(stylize("Deletion cancelled, no preconfigs deleted from Orchestrator",red_text))


print("The following switch configurations are queued for deletion:")
width = 3
print('\n'.join(''.join(str(switch_configs_to_delete[i:i+width])) for i in range(0, len(switch_configs_to_delete), width)))

print("Do you want to proceed to delete these switch configuration files from server?(y/n):")
proceed = input()
if (proceed == "y" or proceed == "Y"):
    for switch_config in switch_configs_to_delete:
        sftp.remove("/srv/tftp/"+switch_config)
        print("Deleted switch configuration:" + switch_config)
    print(stylize("All requested switch configuration files have been deleted from server",green_text))
else:
    print(stylize("Deletion cancelled, no switch configurations deleted from server",red_text))


print("The following switches are queued to be erased:")
width = 3
print('\n'.join(''.join(str(switches_to_erase[i:i+width])) for i in range(0, len(switches_to_erase), width)))

print("Do you want to proceed to erase the startup configurations from these switches?(y/n):")
proceed = input()
if (proceed == "y" or proceed == "Y"):
    for switch_ip in switches_to_erase:

        aruba_sw = {
        'device_type': 'hp_procurve',
        'ip': switch_ip,
        'username': 'admin',
        'password': 'Speak-123',
        }

        print("Connecting to " + stylize(switch_ip, green_text))

        net_connect = ConnectHandler(**aruba_sw)

        output = net_connect.send_command_timing('erase startup-config')
        if 'checkpoint' in output:
            output += net_connect.send_command_timing('y\n')
        elif 'exist' in output:
            print ('Switch {0} startup-config has already been erased'.format(switch_ip))
        else:
            pass
        net_connect.disconnect()

        print("Erased switch startup configuration at " + switch_ip)


    print(stylize("All requested switches have been erased",green_text))
else:
    print(stylize("Erase cancelled, no switch configurations erased",red_text))


# Shutdown switches
esxi.acx_switch_power_off()

# Get Device Keys from demo Appliances
appliance_nepk_ids = []
all_appliances = orch.get_all_appliances().json()
for appliance in all_appliances:
    if appliance['hostName'] in silverpeak_hostname_list:
        appliance_nepk_ids.append(appliance['nePk'])

# Remove ztp demo appliances from Orch
for nePk in appliance_nepk_ids:
    orch.delete_appliance_for_rediscovery(nePk)

# Logout from Orchestrator
orch.logout()

# Remove local configuration files
local_config_directory = "ztp_config_outputs/"

shutil.rmtree(local_config_directory)
