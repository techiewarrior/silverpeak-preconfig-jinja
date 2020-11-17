from vmwc import VMWareClient

class esxiHelper:

    def __init__(self, ipaddress):
        self.host = ipaddress
        self.user = "root"
        self.password = "password"

    def acx_switch_reboot(self):

        with VMWareClient(self.host, self.user, self.password) as client:
            for vm in client.get_virtual_machines():
                if "ACX" in vm.name:
                    print ('rebooting',format(vm.name))
                    vm.reboot()

    def acx_switch_power_on(self):

        with VMWareClient(self.host, self.user, self.password) as client:
            for vm in client.get_virtual_machines():
                if "ACX" in vm.name:
                    print ('powering on ',format(vm.name))
                    vm.power_on()
    
    def acx_switch_power_off(self):

        with VMWareClient(self.host, self.user, self.password) as client:
            for vm in client.get_virtual_machines():
                if "ACX" in vm.name:
                    print ('powering off ',format(vm.name))
                    vm.power_off()