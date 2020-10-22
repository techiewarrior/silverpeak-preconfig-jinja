# Zero Touch Provisioning Demo with Silver Peak and Aruba

### Demo Script:
##### ztp-demo.py

- Takes in CSV file with data for Silver Peak Edge Connects and ArubaOS-CX switches
- Builds configs and stages to Orchestrator for auto-approve or automatically approves if in denied-discovered list
- Powers on switches after a delay for the Edge Connects to come online
- Switches ZTP config via DHCP TFTP option from Edge Connects

### Clean up script:
##### ztp-full-reset.py

- Removes preconfigs from Orchestrator
- Removes switch configs from TFTP Server
- Erases startup config of ArubaOS-CX switches
- Powers down switches
- Removes Edge Connects in Orchestrator for rediscovery



#### INSTALL NOTES:
1. Using a custom orchhelp.py from SPOpenSource for additional functions to Orchestrator

2. copy post_yaml_to_orch.py to local directory from SPOpenSource

3. Create .env file with appropriate values - modeled in dotenv.txt
  - Silver Peak Orchestrator
  - TFTP Server (configs will be posted via SFTP, Switches will retrieve via TFTP)
  - ESXi Server (Where the ArubaOS-CX virtual switches reside for power-on/off if containing ACX in hostname)

4. pip3 install -r requirements.txt

