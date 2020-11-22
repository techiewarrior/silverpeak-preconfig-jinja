import os
import csv
import re

with open("./templates/ec_preconfig_template.jinja2", encoding='utf-8-sig') as jinjaTemplate:
    # Read contents into string
    data = jinjaTemplate.read()
    # Regex find all jinja dictionary variables in dict['varName'] format
    matches = re.findall("\['(.*?)'\]", data, re.DOTALL)
    # Remove duplicates from list
    varList = []
    for i in matches: 
        if i not in varList: 
            varList.append(i) 

# Local directory for configuration outputs
local_config_directory = "preconfig_outputs/"

if not os.path.exists(local_config_directory):
    os.makedirs(local_config_directory)

# Create CSV file with all possible variable headers
filename = local_config_directory + "preconfig_template.csv"
with open(filename, 'w') as csvfile:
    # using csv.writer method from CSV package 
    write = csv.writer(csvfile) 
    # write variables as header list of CSV file      
    write.writerow(varList)