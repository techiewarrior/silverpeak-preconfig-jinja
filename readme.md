# Generate Silver Peak Preconfig YAML files from Jinja Templates

### Preconfig Generator:
##### silverpeak-preconfig-from-jinja.py

- Takes in CSV file with data for Silver Peak Edge Connects
- Validates YAML Preconfig on specified Orchestrator
- If valid, writes local copies of YAML Preconfig files
- *Optionally* stages Preconfigs to Orchestrator
- *Optionally* marks Preconfigs for auto-approve or automatically approves if in denied-discovered list


#### INSTALL NOTES:
1. Dependent on [silverpeak_python_sdk](https://github.com/zachcamara/silverpeak_python_sdk)

2. Create .env file with appropriate values - modeled in dotenv.txt
  - Silver Peak Orchestrator IP or FQDN
  - Silver Peak Orchestrator Username
  - Silver Peak Orchestrator Password

3. pip3 install -r requirements.txt

