import re

def parse_marked_text(text):
    """Returns list of (word, is_marked)"""
    tokens = re.findall(r'\*?[a-zA-Z0-9\',.?!]+(?:\s[a-zA-Z0-9\',.?!]+)?\*?', text)
    result = []
    for token in tokens:
        if token.startswith("*") and token.endswith("*"):
            word = token.strip("*")
            result.append((word, True))
        else:
            result.append((token, False))
    return result

def attach_punctuation_to_previous(tokens):
    result = []
    for token in tokens:
        if token[0] in [".", ",", "!", "?"]: # se il primo elemento del token è una punteggiatura
            if result:
                result[-1] += token  # attacca la punteggiatura al token precedente
        else:
            result.append(token)
    return result


def assign_time_markers(words):
    result = []
    marker_index = 0
    for word, is_emphasized in words:
        if is_emphasized:
            result.append(f'<mark name="tm{marker_index}"/> {word}')
            marker_index += 1
        else:
            result.append(word)

    result.append(f'<mark name="tm{marker_index}"/>') # last marker
    return attach_punctuation_to_previous(result)

#################################################################################

GESTURE_MAP = {
    "hello": ("hello", "RIGHT_HAND"),
    "me": ("me", "RIGHT_HAND"),
    "you": ("you", "LEFT_HAND"),
    "happy": ("welldone", "RIGHT_HAND"),
    "Rome": ("handUp", "LEFT_HAND"),
    "project": ("handDown", "RIGHT_HAND"),
    "talk": ("handUp", "RIGHT_HAND"),
    "yes": ("nod", None),
    "no": ("shake", None),
}

def map_gestures(emphasized_words):
    gestures = []
    for i, word in enumerate(emphasized_words):
        word_lower = word.lower()
        if word_lower in GESTURE_MAP:
            lexeme, mode = GESTURE_MAP[word_lower]
            gesture = {
                "id": f"ges{i}",
                "lexeme": lexeme,
                "mode": mode,
                "start": f"s1:tm{i}",
                "end": f"start+1"
            }
            gestures.append(gesture)
    return gestures

#################################################################################

def generate_bml(xml_id, speech_text, markers, gestures):
    marker_text = ' '.join(markers)
    last_marker = f"tm{len([m for m in markers if 'mark name' in m]) - 1}"

    bml = f"""<?xml version="1.0" encoding="utf-8" ?> 
<bml xmlns="http://www.bml-initiative.org/bml/bml-1.0" xmlns:ext="http://www.bml-initiative.org/bml/coreextensions-1.0" 
id="{xml_id}" characterId="Audrey" composition="APPEND">

  <gaze id="g0" start="0" end="s1:{last_marker}+1" target="Camera"/>
"""

    for g in gestures:
        if g["lexeme"] in ["nod", "shake"]:  # head movement
            bml += f'  <head id="{g["id"]}" lexeme="{g["lexeme"].upper()}" start="{g["start"]}" end="{g["end"]}"/>\n'
        else:
            bml += f'  <gesture id="{g["id"]}" lexeme="{g["lexeme"]}" mode="{g["mode"]}" start="{g["start"]}" end="{g["end"]}"/>\n'

    bml += f"""
  <speech id="s1" start="0">
    <description priority="2" type="application/ssml+xml">
      <speak>
        {marker_text}
      </speak>
    </description>
  </speech>

</bml>"""
    return bml

text = "I'm *happy* to be in *Rome*, working on this *project* with *you*."

def pipeline(text):

    parsed = parse_marked_text(text)
    marked = assign_time_markers(parsed)
    emph_words = [w for w, mark in parsed if mark]
    gestures = map_gestures(emph_words)
    bml = generate_bml("bml1", text, marked, gestures)

    print(parsed)
    print(marked)
    print(emph_words)
    print(gestures)
    print(bml)

    return bml

pipeline(text)