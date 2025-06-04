# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 15:57:10 2024

@author: Maxime
"""

import os
import sys
import json
from subprocess import Popen, PIPE


### Utilities to locate the root folder of the modules ###
def get_modules_folder_dir():
    """Return the directory containing the available modules configuration."""
    current_dir = os.path.abspath(os.path.dirname(__file__))

    while not os.path.exists(os.path.join(current_dir, 'available_modules.json')):
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        if parent_dir == current_dir:
            print("Le fichier 'available_modules.json' n'a pas été trouvé.")
            sys.exit(1)
        current_dir = parent_dir

    return current_dir
    
modules_folder_dir = get_modules_folder_dir()
sys.path.append(modules_folder_dir)
from UDPClient import UDPClient

### Retrieve the whiteboard IP ###
ip_whiteboard_file = os.path.join(modules_folder_dir, 'IP_whiteboard.txt')
with open(ip_whiteboard_file, 'r') as txt_file:
    ip_whiteboard = txt_file.read()
    

# Setup UDP Client
udp_client = UDPClient(ip_whiteboard)
subscribes = ['COMMON']

for subscribe in subscribes:
    udp_client.send(f'Subscribe:{subscribe}')
    
    
available_modules_path = os.path.join(modules_folder_dir, 'available_modules.json')

# Open and load the JSON data
with open(available_modules_path, 'r') as file:
    available_modules = json.load(file)
    

# Function to find a module by name
def find_module(modules, module_full_name):
    for module in modules:
        if module['name'] == module_full_name:
            return module
    return None

# Function to launch a module
def launch_module(module):
    launch_path = module['launch_path']
    absolute_launch_path = os.path.join(modules_folder_dir, launch_path)
    absolute_module_path = os.path.dirname(absolute_launch_path)
    Popen(f'start {absolute_launch_path}', cwd=absolute_module_path, shell=True)

def launch_all_modules():
    for module in available_modules:
        module_name = module['name']
        module = find_module(available_modules, module_name)
        if module:
            print(f"Launching module: {module_name}")
            launch_module(module)
        else:
            print(f"Module '{module_name}' not found.")

def main():
    # Main loop
    while True:
        received_messages = udp_client.get_received_messages()
        if 'COMMON' in received_messages:
            message = received_messages['COMMON']
            if 'REQUEST_MODULE_ACTIVATION' in message:
                module_full_name = message.split(':')[1].lower()
                module = find_module(available_modules, module_full_name)
                if module:
                    print(f"Launching module: {module_full_name}")
                    launch_module(module)
                else:
                    print(f"Module '{module_full_name}' not found.")
            
            else:
                pass
            
            
if __name__ == '__main__':
    main()
        
    