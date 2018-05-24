import core.bootstrap as bootstrap

class DriverLoader:
    def __init__(self):
        self.drivers = bootstrap.bootstrap_drivers()
    
    def get_driver(self, key):
        return self.drivers[key]

driver_loader = None

def load():
    global driver_loader
    driver_loader = DriverLoader()

def get_driver(key):
    driver_loader.get_driver(key)
