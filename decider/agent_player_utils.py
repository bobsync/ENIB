# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 16:59:17 2024

@author: Maxime
"""

import re

class VirtualAgentControl():
    def __init__(self, udp_client):
        self.udp_client = udp_client
        self.bml_id = 0
        self.bml_topic = 'BML_COMMAND'
        self.start_BML = """<bml xmlns="http://www.bml-initiative.org/bml/bml-1.0" xmlns:ext="http://www.bml-initiative.org/bml/coreextensions-1.0" id="14" characterId="Audrey" composition="MERGE">
                    """     
        self.end_BML = """</bml>"""
        
    def add_bml_wrap(self, msg):
        """Adds the bml tags : <bml...> msg </bml>"""
        return self.start_BML + msg + self.end_BML
    
    def send_bml_item(self, bml_item):
        bml = self.add_bml_wrap(bml_item)
        fixed_bml = self.fix_bml_ids(bml)
        self.udp_client.send(f'{self.bml_topic}:{fixed_bml}')
        self.bml_id+=1
        
    def send_bml_items(self, bml_items):
        bml = self.add_bml_wrap("\n".join(bml_items))
        fixed_bml = self.fix_bml_ids(bml)
        self.udp_client.send(f'{self.bml_topic}:{fixed_bml}')
    
    def send_bml(self, bml):
        self.udp_client.send(f'{self.bml_topic}:{bml}')
        self.bml_id+=1
        
        
    def fix_bml_ids(self, text):
        # Define the regex pattern to find id=""
        pattern = r'id=".*?"'
        
        # Function to replace the matched pattern with the current id and increment the id
        def replacement(match):
            result = f'id="{self.bml_id}"'
            self.bml_id += 1
            return result
        
        # Use re.sub with a function to perform the replacement
        modified_text = re.sub(pattern, replacement, text)
        
        return modified_text
        
    def speak_BML(self, text, priority):
        ret = ""
        ret += f"""<speech id="{self.bml_id}" start="0">
                	  <description priority="{priority}" type="application/ssml+xml">
            			  <speak>
               """
        ret += text
        ret += """
                         </speak>
                      </description>
                  </speech>
               """
        return ret
    
    # <speak>
    #     <prosody volume="x-soft" rate="x-slow" range="x-low">
    #       je parle doucement !
    #     </prosody>
    #     <prosody volume="x-loud" rate="x-fast" range="x-high">
    #       Je parle bien plus fort !
    #     </prosody>
    # </speak>
    
    def speak(self, text, priority=0):
        bml = self.add_bml_wrap(self.speak_BML(text, priority))
        self.send_bml(bml)
        
    
    def gaze_object_BML(self, target, duration):
        ret = ""
        ret += f"""<gaze id = "{self.bml_id}" start = "0" stroke="{duration}" target = "{target}" />
               """
        return ret
    
    def gaze_object(self, target, duration=2):
        bml = self.add_bml_wrap(self.gaze_object_BML(target, duration))
        self.send_bml(bml)
        
    
    def gaze_shift_object_BML(self, target):
        ret = ""
        ret += f"""<gazedirectionshift id = "{self.bml_id}" start = "0" target = "{target}" />
               """
        return ret
    
    def gaze_shift_object(self, target):
        bml = self.add_bml_wrap(self.gaze_shift_object_BML(target))
        self.send_bml(bml)
        
        
    def head_roll_BML(self, roll_angle_deg):
        amount = abs(roll_angle_deg/15) #the amount is not exact
        lexeme = 'tilt_right' if roll_angle_deg > 0 else 'tilt_left'
        ret = ""
        ret += f"""<head id = "{self.bml_id}" lexeme = "{lexeme}" amount = "{amount}" />
                """
        return ret
    
    def head_roll(self, roll_angle_deg):
        bml = self.add_bml_wrap(self.head_roll_BML(roll_angle_deg))
        self.send_bml(bml)
        
    
    def head_pitch_BML(self, pitch_angle_deg):
        pitch_angle_deg = max(-20, min(30, pitch_angle_deg)) #doesn't work if angle too low
        amount = abs(pitch_angle_deg/20)
        print(f"{pitch_angle_deg=} {amount=}")
        lexeme = 'down' if pitch_angle_deg > 0 else 'up'
        ret = ""
        ret += f"""<head id = "{self.bml_id}" lexeme = "{lexeme}" amount = "{amount}" />
                """
        return ret
    
    def head_pitch(self, pitch_angle_deg):
        bml = self.add_bml_wrap(self.head_pitch_BML(pitch_angle_deg))
        self.send_bml(bml)
    
    def point_object_BML(self, target, duration):
        ret = ""
        ret += f"""<pointing id = "{self.bml_id}" start = "0" stroke="{duration}" target = "{target}"/>
               """
        return ret
    
    def point_object(self, target, duration=2):
        bml = self.add_bml_wrap(self.point_object_BML(target, duration))
        self.send_bml(bml)
    

class AgentPlayerControl():
    def __init__(self, udp_client):
        self.subscribes = []
        self.udp_client = udp_client
        self.agent = VirtualAgentControl(self.udp_client)
        self.command_topic = "AGENT_PLAYER_COMMAND"
        
        

    def move_object_str(self, target, pos, rotation):
        round_dec = 4
        x, y, z = pos['x'], pos['y'], pos['z']
        x, y, z = round(x, round_dec), round(y, round_dec), round(z, round_dec)
        
        if rotation is not None:
            if 'x' in rotation:
                rot_x, rot_y, rot_z = rotation['x'], rotation['y'], rotation['z']
            elif 'pitch' in rotation:
                rot_x, rot_y, rot_z = rotation['pitch'], rotation['yaw'], rotation['roll']
            
            rot_x, rot_y, rot_z = round(rot_x, round_dec), round(rot_y, round_dec), round(rot_z, round_dec)
            res = f"{self.command_topic}:move_object:{target}:{x},{y},{z},{rot_x},{rot_y},{rot_z}"
        else:
            res = f"{self.command_topic}:move_object:{target}:{x},{y},{z}"
        
        return res
    
    def move_object(self, target, pos, rotation=None):
        self.udp_client.send(self.move_object_str(target, pos, rotation))
        #time.sleep(0.01)
