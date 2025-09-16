# -*- coding: utf-8 -*-
"""
Main conversation and gesture coordination module for the agent "Audrey".
Handles user interaction, LLM queries, BML generation, and inactivity behavior.
@author: Maxime
"""

import os
import random
import time
import io
import json
from setup_udp_client import udp_client  # Gestione della comunicazione via UDP
from agent_player_utils import AgentPlayerControl  # Controllo del comportamento dell'agente
from conversation_utils import maybe_update_agent_interaction, check_goodbye  # Logica per risposte rapide dell'agente
from pipeline_debug import pipeline  # Converte risposte LLM in BML
import xml.etree.ElementTree as ET  # Per parsing di file XML

# === CONFIGURAZIONE ===

MODULE_FULL_NAME = "DECIDER/CONVERSATION_GESTURE"
ICEBREAKER_FOLDER = "icebreakers"
STARTUP_BML_FILE = "startup.xml"
PROMPT_FILE = "BFI_prompt.txt"
INACTIVITY_TIMEOUT = 25
GAZE_SHIFT_INTERVAL = random.randint(5, 10)
POST_SPEAK_DELAY = 5  # Tempo di attesa dopo il parlato prima di un gaze shift

# Stato globale
used_icebreakers: set[str] = set()
last_user_interaction_time: float = time.time()
last_gaze_shift_time = time.time()
last_speech_end_time = 0.0

REQUIRED_MODULES = {
    "LARGE_LANGUAGE_MODEL/LLAMA3_ONLINE_GROQ",
    "SPEECH/REALTIME_WHISPER",
    "DECIDER/CONVERSATION_GESTURE",
    "WEBCAM/GAZE_DETECTION"
}

SUBSCRIPTIONS = [
    'USER_FULL_SENTENCE_PERCEPTION',
    'USER_CONTEXT_PERCEPTION',
    'AUDIO_FEATURES_PERCEPTION',
    'LLM_RESPONSE',
    'COMMON',
    'AGENT_PLAYER_STATUS'
]

for subscribe in SUBSCRIPTIONS:
    udp_client.send(f"Subscribe:{subscribe}")

with io.open(PROMPT_FILE, mode="r", encoding="utf-8") as f:
    system_prompt_content = f.read()
    system_prompt_reminder_content = system_prompt_content  # fix: non doppio f.read()

system_prompt_message = {'role': 'system', 'content': system_prompt_content}
system_prompt_reminder_message = {'role': 'system', 'content': system_prompt_reminder_content}

with open(STARTUP_BML_FILE, "r", encoding="utf-8") as f:
    startup_bml = f.read()

agent_player = AgentPlayerControl(udp_client)

# === VARIABILI DI STATO ===

activated_modules = set()
conversation_history = []
user_context = {"activity": "other", "gaze": "front"}
agent_interaction = True
startup_message_sent = False
startup_sent_time = None
used_icebreakers = set()
last_user_interaction_time = time.time()
goodbye_triggered = False
speaking = False
close_all = True
icebreaker_pending = False

# === FUNZIONI ===

current_icebreaker = None  # (group_name, variant_index)

def discard_current_icebreaker_group():
    """Scarta l'intero gruppo corrente di icebreaker dopo risposta utente."""
    global current_icebreaker
    if current_icebreaker:
        group_name, _ = current_icebreaker
        used_icebreakers.add(group_name)
        print(f"[INFO] Gruppo icebreaker '{group_name}' scartato dopo risposta utente.")
        current_icebreaker = None

def get_next_icebreaker_variant():
    global current_icebreaker

    if current_icebreaker is None:
        available_groups = [d for d in os.listdir(ICEBREAKER_FOLDER) if os.path.isdir(os.path.join(ICEBREAKER_FOLDER, d))]
        unused_groups = list(set(available_groups) - used_icebreakers)
        if not unused_groups:
            print("[DEBUG] Nessun gruppo icebreaker disponibile.")
            return None

        chosen_group = random.choice(unused_groups)
        used_icebreakers.add(chosen_group)
        current_icebreaker = (chosen_group, 0)

    group_name, index = current_icebreaker
    group_path = os.path.join(ICEBREAKER_FOLDER, group_name)
    next_file = os.path.join(group_path, f"{index + 1}.xml")

    if os.path.exists(next_file):
        current_icebreaker = (group_name, index + 1)
        with open(next_file, "r", encoding="utf-8") as f:
            return next_file, f.read()
    else:
        print(f"[DEBUG] Fine varianti per il gruppo {group_name}")
        current_icebreaker = None
        return None

def handle_goodbye_sequence():
    print("[INFO] Frase di addio rilevata. Attendo fine del parlato di Audrey...")
    while True:
        received_messages = udp_client.get_received_messages()
        if (agent_status := received_messages.get('AGENT_PLAYER_STATUS')):
            if "Audrey:speech off" in agent_status:
                print("[INFO] Audrey ha terminato di parlare. Interazione conclusa.")
                if close_all:
                    udp_client.send("COMMON:BROADCAST_REQUEST_SHUTDOWN") # per terminare tutto
                break
        time.sleep(0.1)

def check_all_modules_activated(message: str) -> bool:
    if 'MODULE_SUCCESSFULLY_ACTIVATED' in message:
        module_name = message.split(':')[-1]
        activated_modules.add(module_name)
        print(f"[INFO] Modulo attivato: {module_name}")
    return REQUIRED_MODULES.issubset(activated_modules)

def process_user_sentence(sentence: str):
    global last_user_interaction_time, agent_interaction, goodbye_triggered, speaking

    reset_inactivity_timer()
    print("[USER]", sentence)

    # 👇 Se era attivo un icebreaker, scartiamo il gruppo
    if current_icebreaker:
        discard_current_icebreaker_group()

    goodbye_triggered = check_goodbye(sentence)

    agent_interaction, agent_response = maybe_update_agent_interaction(sentence, agent_interaction)
    if agent_response:
        speaking = True
        print("[DEBUG] Risposta automatica: speaking=True")
        agent_player.agent.speak(agent_response)
        return

    if agent_interaction:
        conversation_history.append({'role': 'user', 'content': sentence})
        llm_query_prompt = json.dumps(
            [system_prompt_message] + conversation_history[-8:] + [system_prompt_reminder_message]
        )
        print("[DEBUG] Invio prompt al LLM")
        udp_client.send(f'LLM_QUERY:{llm_query_prompt}')

def process_llm_response(response: str):
    global speaking
    print("[LLM RESPONSE]", response)
    bml = pipeline(response)
    print("[DEBUG] BML generato:", bml)

    speaking = "<speak" in bml or "<speech" in bml
    print(f"[DEBUG] speaking impostato a {speaking} in base al contenuto del BML")

    with open("output_bml.xml", "w", encoding="utf-8") as f:
        f.write(bml)

    agent_player.agent.send_bml(bml)
    conversation_history.append({'role': 'assistant', 'content': response})

def send_startup_message():
    global startup_message_sent, startup_sent_time
    print("[INFO] Tutti i moduli attivati. Invio messaggio di avvio.")
    time.sleep(3)
    agent_player.agent.send_bml(startup_bml)
    startup_message_sent = True
    startup_sent_time = time.time()

def reset_inactivity_timer():
    global last_user_interaction_time
    last_user_interaction_time = time.time()
    print("[DEBUG] Inactivity timer resettato")

def estrai_frase_da_bml(xml_path: str) -> str:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    speak_elem = next((el for el in root.iter() if el.tag.endswith('speak')), None)
    if speak_elem is None:
        return ""

    frase = "".join(speak_elem.itertext()).strip()
    return frase

def handle_inactivity():
    global last_user_interaction_time, speaking, icebreaker_pending
    if startup_sent_time is None:
        return

    if time.time() - startup_sent_time < 20:
        return

    if time.time() - last_user_interaction_time > INACTIVITY_TIMEOUT and not speaking:
        if user_context.get("gaze", "").lower() == "down":
            if not icebreaker_pending:
                print("[DEBUG] Icebreaker posticipato: utente guarda in basso")
            icebreaker_pending = True
            return


        print("[DEBUG] Condizione di inattività soddisfatta. Verifica icebreaker...")
        result = get_next_icebreaker_variant()
        if result:
            xml_path, icebreaker_bml = result
            print(f"[INFO] Inattività rilevata (> {INACTIVITY_TIMEOUT}s). Invio icebreaker.")
            agent_player.agent.send_bml(icebreaker_bml)
            speaking = True

            speak_text = estrai_frase_da_bml(xml_path)
            conversation_history.append({
                'role': 'assistant',
                'content': speak_text
            })
            reset_inactivity_timer()
            icebreaker_pending = False

def send_random_gaze_bml():
    directions = ["left", "right", "up", "down", "upright", "upleft"]
    chosen_target = random.choice(directions)
    duration = round(random.uniform(1,2), 2)

    print(f"[DEBUG] Tentativo gaze shift - speaking={speaking}")

    bml = f"""
    <bml xmlns="http://www.bml-initiative.org/bml/bml-1.0" id="gazeShift" characterId="Audrey" composition="MERGE">
        <gaze id="g0" start="0" end="start+{duration}" target="{chosen_target}"/>
    </bml>
    """

    agent_player.agent.send_bml(bml)
    print(f"[GAZE SHIFT] Audrey guarda verso {chosen_target} per {duration} secondi.")

# === AVVIO ===

udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_ACTIVATED:{MODULE_FULL_NAME}')

while not startup_message_sent:
    received_messages = udp_client.get_received_messages()
    if (message := received_messages.get('COMMON')):
        if 'REQUEST_MODULE_DEACTIVATION' in message:
            request_module_full_name = message.split(':')[1]
            if MODULE_FULL_NAME == request_module_full_name:
                udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_DEACTIVATED:{MODULE_FULL_NAME}')
                udp_client.close()
                exit()

        if check_all_modules_activated(message) and not startup_message_sent:
            send_startup_message()

# === LOOP PRINCIPALE ===

while True:
    received_messages = udp_client.get_received_messages()
    now = time.time()

    if (message := received_messages.get('COMMON')):
        if 'REQUEST_MODULE_DEACTIVATION' in message:
            request_module_full_name = message.split(':')[1]
            if MODULE_FULL_NAME == request_module_full_name:
                break

    if startup_sent_time and now - startup_sent_time >= 10:
        handle_inactivity()

        if (
            now - last_gaze_shift_time > GAZE_SHIFT_INTERVAL
            and not speaking
            and now - last_speech_end_time > POST_SPEAK_DELAY
        ):
            send_random_gaze_bml()
            last_gaze_shift_time = now
            GAZE_SHIFT_INTERVAL = random.randint(7, 12)

    if (agent_status := received_messages.get('AGENT_PLAYER_STATUS')):
        print("[DEBUG] AGENT_PLAYER_STATUS message:", agent_status)
        if "Audrey:speech off" in agent_status:
            print("AUDREY ENDED SPEECH")
            reset_inactivity_timer()
            speaking = False
            last_speech_end_time = time.time()
            print("[DEBUG] speaking=False per fine parlato")

    if (context_data := received_messages.get('USER_CONTEXT_PERCEPTION')):
        try:
            old_gaze = user_context.get("gaze")
            user_context.update(json.loads(context_data))
            print("[USER CONTEXT UPDATED]", user_context)

            if icebreaker_pending and user_context.get("gaze", "").lower() != "down":
                print("[DEBUG] Icebreaker ritardato ora inviato: utente non guarda più in basso")
                handle_inactivity()

        except json.JSONDecodeError:
            print("[ERROR] Malformed USER_CONTEXT_PERCEPTION data.")

    if (user_full_sentence := received_messages.get('USER_FULL_SENTENCE_PERCEPTION')):
        process_user_sentence(user_full_sentence)

    if (llm_response := received_messages.get('LLM_RESPONSE')):
        process_llm_response(llm_response)

        if goodbye_triggered:
            handle_goodbye_sequence()
            break

# === CHIUSURA ===

udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_DEACTIVATED:{MODULE_FULL_NAME}')
udp_client.close()
