from vmwc import VMWareClient

class esxiHelper:

    def __init__(self, ipaddress):
        self.host = ipaddress
        self.user = "root"
        self.password = "password"

    def ecv_power_on(self):

        with VMWareClient(self.host, self.user, self.password) as client:
            for vm in client.get_virtual_machines():
                if "ZTP" in vm.name and "ECV" in vm.name:
                    print ('powering on ',format(vm.name))
                    vm.power_on()
    
    def ecv_power_off(self):

        with VMWareClient(self.host, self.user, self.password) as client:
            for vm in client.get_virtual_machines():
                if "ZTP" in vm.name and "ECV" in vm.name:
                    print ('powering off ',format(vm.name))
                    vm.power_off()