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
from nlp import pipeline  # Converte risposte LLM in BML
import xml.etree.ElementTree as ET  # Per parsing di file XML

# === CONFIGURAZIONE ===

MODULE_FULL_NAME = "DECIDER/CONVERSATION_GESTURE"  # Nome identificativo del modulo
ICEBREAKER_FOLDER = "icebreakers"  # Cartella dei BML per inattività
STARTUP_BML_FILE = "startup.xml"  # BML iniziale al boot
PROMPT_FILE = "prompt_bml_plain.txt"  # Prompt iniziale per il LLM
INACTIVITY_TIMEOUT = 50  # Timeout inattività in secondi

# Stato globale
used_icebreakers: set[str] = set()
last_user_interaction_time: float = time.time()

# Moduli richiesti per iniziare l'interazione
REQUIRED_MODULES = {
    "LARGE_LANGUAGE_MODEL/LLAMA3_ONLINE_GROQ",
    "SPEECH/REALTIME_WHISPER",
    "DECIDER/CONVERSATION_GESTURE"
}

# Tipi di messaggi a cui ci si iscrive
SUBSCRIPTIONS = [
    'USER_FULL_SENTENCE_PERCEPTION',
    'USER_CONTEXT_PERCEPTION',
    'AUDIO_FEATURES_PERCEPTION',
    'LLM_RESPONSE',
    'COMMON',
    'AGENT_PLAYER_STATUS'
]

# === INIZIALIZZAZIONE ===

# Iscrizione ai tipi di messaggi necessari
for subscribe in SUBSCRIPTIONS:
    udp_client.send(f"Subscribe:{subscribe}")

# Caricamento prompt di sistema per il LLM
with io.open(PROMPT_FILE, mode="r", encoding="utf-8") as f:
    system_prompt_content = f.read()
    system_prompt_reminder_content = f.read()

system_prompt_message = {'role': 'system', 'content': system_prompt_content}
system_prompt_reminder_message = {'role': 'system', 'content': system_prompt_reminder_content}

# Caricamento del BML di avvio
with open(STARTUP_BML_FILE, "r", encoding="utf-8") as f:
    startup_bml = f.read()

# Inizializzazione del controller dell'agente
agent_player = AgentPlayerControl(udp_client)

# === VARIABILI DI STATO ===

activated_modules = set()
conversation_history = []
user_context = {"activity": "other", "gaze": "front"}
agent_interaction = True
startup_message_sent = False
used_icebreakers = set()
last_user_interaction_time = time.time()
goodbye_triggered = False

# === FUNZIONI ===

def handle_goodbye_sequence():
    print("[INFO] Frase di addio rilevata. Attendo fine del parlato di Audrey...")
    while True:
        received_messages = udp_client.get_received_messages()
        if (agent_status := received_messages.get('AGENT_PLAYER_STATUS')):
            if "Audrey:speech off" in agent_status:
                print("[INFO] Audrey ha terminato di parlare. Interazione conclusa.")
                break
        time.sleep(0.1)

def check_all_modules_activated(message: str) -> bool:
    """Traccia i moduli attivati e verifica se tutti quelli richiesti sono attivi."""
    if 'MODULE_SUCCESSFULLY_ACTIVATED' in message:
        module_name = message.split(':')[1]
        activated_modules.add(module_name)
        print(f"[INFO] Modulo attivato: {module_name}")
    return REQUIRED_MODULES.issubset(activated_modules)

def process_user_sentence(sentence: str):
    """Gestisce una nuova frase dell'utente."""
    global last_user_interaction_time, agent_interaction, goodbye_triggered

    print("User -", sentence)

    goodbye_triggered = check_goodbye(sentence)

    agent_interaction, agent_response = maybe_update_agent_interaction(sentence, agent_interaction)
    if agent_response:
        agent_player.agent.speak(agent_response)
        return

    if agent_interaction:
        conversation_history.append({'role': 'user', 'content': sentence})
        llm_query_prompt = json.dumps(
            [system_prompt_message] + conversation_history[-8:] + [system_prompt_reminder_message]
        )
        udp_client.send(f'LLM_QUERY:{llm_query_prompt}')

def process_llm_response(response: str):
    """Converte la risposta del LLM in BML e la invia all'agente."""
    print("LLM Response received:", response)
    bml = pipeline(response)

    with open("output_bml.xml", "w", encoding="utf-8") as f:
        f.write(bml)

    agent_player.agent.send_bml(bml)
    conversation_history.append({'role': 'assistant', 'content': response})

def send_startup_message():
    """Invia il messaggio BML di avvio dell'agente."""
    global startup_message_sent
    print("[INFO] Tutti i moduli attivati. Invio messaggio di avvio.")
    time.sleep(3)
    agent_player.agent.send_bml(startup_bml)
    startup_message_sent = True

def reset_inactivity_timer():
    """Aggiorna il timestamp dell'ultima interazione utente."""
    global last_user_interaction_time
    last_user_interaction_time = time.time()

def get_unused_icebreaker() -> tuple[str, str] | None:
    """Restituisce un BML icebreaker non ancora usato."""
    files = [f for f in os.listdir(ICEBREAKER_FOLDER) if f.endswith(".xml")]
    unused_files = list(set(files) - used_icebreakers)
    if not unused_files:
        return None

    chosen_filename = random.choice(unused_files)
    used_icebreakers.add(chosen_filename)

    full_path = os.path.join(ICEBREAKER_FOLDER, chosen_filename)
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    return full_path, content

def estrai_frase_da_bml(xml_path: str) -> str:
    """Estrae il testo parlato da un file BML ignorando i tag."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    speak_elem = next(
        (el for el in root.iter() if el.tag.endswith('speak')),
        None
    )

    if speak_elem is None:
        return ""

    frase = "".join(speak_elem.itertext()).strip()
    return frase

def handle_inactivity():
    """Invia un icebreaker se l'utente è inattivo da troppo tempo."""
    global last_user_interaction_time
    if time.time() - last_user_interaction_time > INACTIVITY_TIMEOUT:
        result = get_unused_icebreaker()
        if result:
            xml_path, icebreaker_bml = result
            print(f"[INFO] Inattività rilevata (> {INACTIVITY_TIMEOUT}s). Invio icebreaker.")
            agent_player.agent.send_bml(icebreaker_bml)

            speak_text = estrai_frase_da_bml(xml_path)
            conversation_history.append({
                'role': 'assistant',
                'content': speak_text
            })
            reset_inactivity_timer()

# === CICLO PRINCIPALE ===

udp_client.send(f'COMMON:MODULE_SUCCESSFULLY_ACTIVATED:{MODULE_FULL_NAME}')

while True:
    received_messages = udp_client.get_received_messages()

    if (message := received_messages.get('COMMON')):
        if 'REQUEST_MODULE_DEACTIVATION' in message:
            request_module_full_name = message.split(':')[1]
            if MODULE_FULL_NAME == request_module_full_name:
                break

        if check_all_modules_activated(message) and not startup_message_sent:
            send_startup_message()

    if startup_message_sent:
        handle_inactivity()

        if (agent_status := received_messages.get('AGENT_PLAYER_STATUS')):
            print("[DEBUG] AGENT_PLAYER_STATUS message:", agent_status)
            if "Audrey:speech off" in agent_status:
                print("AUDREY ENDED SPEECH")
                reset_inactivity_timer()

        if (context_data := received_messages.get('USER_CONTEXT_PERCEPTION')):
            try:
                user_context.update(json.loads(context_data))
                print("[USER CONTEXT UPDATED]", user_context)
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
