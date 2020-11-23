# Generate Silver Peak Preconfig YAML files from Jinja Templates


### CSV Generator:
##### create_preconfig_csv.py

- Takes in jinja2 template and creates headers for all unique variables in 'preconfig_template.csv'
- Use this CSV with values for the Preconfig Generator script
- Not all variables are mandatory for preconfig
- There is an example CSV file with values included 'example.csv'

### Preconfig Generator:
##### silverpeak-preconfig-from-jinja.py

- Takes in CSV file with data for Silver Peak Edge Connects
- Builds YAML configs and stores locally
- *Optionally* stages preconfigs to Orchestrator
- *Optionally* marks preconfigs for auto-approve or automatically approves if in denied-discovered list



#### INSTALL NOTES:
1. This uses a custom orchhelp.py from SPOpenSource for additional functions to Orchestrator

2. Create .env file with appropriate values - modeled in dotenv.txt
  - Silver Peak Orchestrator IP or FQDN
  - Silver Peak Orchestrator Username
  - Silver Peak Orchestrator Password

3. pip3 install -r requirements.txt

