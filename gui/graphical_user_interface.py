# -*- coding: utf-8 -*-
'''
Created on Thu Jun 13 18:09:41 2024

@author: Maxime
'''

import os
import sys
import json
import time
import customtkinter

### To import UDPCLient ###
def get_modules_folder_dir():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    
    while not os.path.exists(os.path.join(current_dir, 'Modules')):
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        if current_dir == os.path.abspath(os.sep):
            print("Le dossier 'Modules' n'a pas été trouvé.")
            sys.exit(1)
    
    return os.path.join(current_dir, 'Modules')
    
modules_folder_dir = get_modules_folder_dir()
sys.path.append(modules_folder_dir)
from UDPClient import UDPClient

### To have the whiteboard ip ###
ip_witeboard_file = os.path.join(modules_folder_dir, 'IP_whiteboard.txt')
with open(ip_witeboard_file, 'r') as txt_file:
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
      

customtkinter.set_appearance_mode('System')  # Modes: 'System' (standard), 'Dark', 'Light'
customtkinter.set_default_color_theme('blue')  # Themes: 'blue' (standard), 'green', 'dark-blue'


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title('Graphical User Interface')
        self.geometry(f'{800}x{400}')
        self.grid_columnconfigure(0, weight=1, uniform='column')
        self.grid_rowconfigure((0,1,2,3,4,5), weight=1, uniform='row')
        
        self.modules_activation_state = {}
        self.module_state_colors = {'activation_requested' : '#94d59d',
                                    'activation_failed' : '#df0404',
                                    'activated' : '#008400',
                                    'deactivation_requested' : '#ffa8a8',
                                    'deactivation_failed' : '#2986cc',
                                    'deactivated' : '#2986cc'}
                                      
        self.modules_request_activation_time = {}
        self.module_buttons = {}

        self.create_buttons()
        self.after(20, self.update)
        
    def create_buttons(self):
        """ Creates buttons on the interface using the available_modules.json file """
        modules_by_type = {}
        
        # Parse the available_modules to group by module type
        for module in available_modules:
            module_full_name = module['name']
            if '/' in module_full_name:
                module_type, module_name = module_full_name.split('/', 1)
            else:
                module_type, module_name = module_full_name, module_full_name
                
            if module_type not in modules_by_type:
                modules_by_type[module_type] = []
            modules_by_type[module_type].append((module_name, module['launch_path']))
        
        row = 0
        #each module type is a row, and each module name is a column
        for module_type, modules in modules_by_type.items():
            # Add a label for the module type
            label = customtkinter.CTkLabel(self, text=module_type, anchor='w')
            label.grid(row=row, column=0, padx=20, pady=10, sticky='w')
            
            col = 1
            for module_name, launch_path in modules:
                button = customtkinter.CTkButton(
                    self,
                    text=module_name,
                    command=lambda mt=module_type, mn=module_name: self.click_change_module_state(mt, mn)
                )
                button.grid(row=row, column=col, padx=10, pady=10)
                module_init_state = 'deactivated'
                self.modules_activation_state[(module_type, module_name)] = module_init_state
                color = self.module_state_colors[module_init_state]
                button.configure(fg_color=color, hover_color=color)
                self.module_buttons[(module_type, module_name)] = button
                col += 1
            
            row += 1

    def click_change_module_state(self, module_type, module_name):
        """ Is activated when the button of a module is clicked """
        module_full_name = f'{module_type}/{module_name}'
        current_module_state = self.modules_activation_state[(module_type, module_name)]
        new_module_state = current_module_state
        if current_module_state == 'deactivated':
            print(f'Request activation of module: {module_full_name}')
            udp_client.send(f'COMMON:REQUEST_MODULE_ACTIVATION:{module_full_name.upper()}')
            new_module_state = 'activation_requested'
            
            
        elif current_module_state == 'activated':
            print(f'Request deactivation of module: {module_full_name}')
            udp_client.send(f'COMMON:REQUEST_MODULE_DEACTIVATION:{module_full_name.upper()}')
            new_module_state = 'deactivation_requested'
        
        else:
            print(f'Current module state : {current_module_state}')
            
        self.modules_activation_state[(module_type, module_name)] = new_module_state
        self.change_button_color(module_type,
                                 module_name,
                                 self.module_state_colors[new_module_state])
        
        
    def change_button_color(self, module_type, module_name, color):
        button = self.module_buttons.get((module_type, module_name))
        button.configure(fg_color=color, hover_color=color)
        
            
    
    def update(self):
        """ Function executed every 20ms that checks the received messages """
        received_messages = udp_client.get_received_messages()
        if 'COMMON' in received_messages:
            message = received_messages['COMMON']
            if 'MODULE_SUCCESSFULLY_ACTIVATED' in message:
                new_module_state = 'activated' 
                module_full_name = message.split(':')[1].lower()
                module_type, module_name = module_full_name.split('/', 1)
                self.modules_activation_state[(module_type, module_name)] = new_module_state
                self.change_button_color(module_type,
                                         module_name,
                                         self.module_state_colors[new_module_state])
                
            
            elif 'MODULE_SUCCESSFULLY_DEACTIVATED' in message:
                new_module_state = 'deactivated'
                module_full_name = message.split(':')[1].lower()
                module_type, module_name = module_full_name.split('/', 1)
                self.modules_activation_state[(module_type, module_name)] = new_module_state
                self.change_button_color(module_type,
                                         module_name,
                                         self.module_state_colors[new_module_state])
                
        
        self.after(20, self.update)
        

if __name__ == '__main__':
    app = App()
    app.attributes('-topmost', True) #so the window always stays on top
    app.mainloop()
        
    