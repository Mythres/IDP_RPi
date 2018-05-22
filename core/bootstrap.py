import argparse
import importlib
import os
import sys

def bootstrap_interface():
    interface_mods = dict()
    interface_mods_help = ""
    counter = 1

    for dir_entry in os.scandir("./interfaces"):
        if dir_entry.is_dir() and "__" not in dir_entry.name:
            mod_name = dir_entry.path.split('/')[-1]
            interface_mods[mod_name] = importlib.import_module("interfaces." + mod_name + "." + mod_name)
            interface_mods_help += (str(counter) + ". " + mod_name + "\n")
            counter += 1
    
    parser = argparse.ArgumentParser()
    parser.add_argument("interface", help="Please choose an interface to use: " + interface_mods_help)
    args = parser.parse_args()
    if args.interface in interface_mods:
        return interface_mods[args.interface]
    else:
        sys.exit("Invalid interface specified.\nPlease choose an interface:\n" + interface_mods_help)

def bootstrap_assignments():
    assignment_mods = dict()

    for dir_entry in os.scandir("./assignments"):
        if dir_entry.is_dir() and "__" not in dir_entry.name:
            mod_name = dir_entry.path.split('/')[-1]
            assignment_mods[mod_name] = importlib.import_module("assignments." + mod_name + "." + mod_name)

    return assignment_mods

def bootstrap_drivers():
    driver_mods = dict()

    for dir_entry in os.scandir("./drivers"):
        if dir_entry.is_dir() and "__" not in dir_entry.name:
            mod_name = dir_entry.path.split('/')[-1]
            driver_mods[mod_name] = importlib.import_module("drivers." + mod_name + "." + mod_name)

    return driver_mods