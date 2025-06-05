import json
import logging
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from nltk.corpus import wordnet as wn
from textblob import TextBlob

# Configure persistent logger
gen_logger = logging.getLogger("gesture_pipeline")
logging.basicConfig(
    filename="gesture_debug.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Constants for lexemes, gestures, and modes
FACE_LEXEMES = [
    "HAPPINESS",
    "SMILE",
    "SADNESS",
    "FEAR",
    "ANGER",
    "DISGUST",
    "FROWN",
]
GESTURE_LIST = ["hello", "handDown", "handUp", "me", "you"]
HEAD_MOVES = [
    "nod", "shake", "wobble", "forward", "backward", "up", "down",
    "left", "right", "tiltr", "tiltl", "up_right", "up_left",
    "down_right", "down_left",
]
MODES = ["RIGHT_HAND", "LEFT_HAND", "BOTH_HANDS"]


def load_gesture_db(path: str) -> Dict[str, Any]:
    """
    Load a JSON gesture library from disk.
    """
    file = Path(path)
    data = file.read_text(encoding="utf-8")
    return json.loads(data)


def get_semantic_tag(word: str) -> str:
    """
    Return the semantic lexname tag for a word (or empty if none).
    """
    synsets = wn.synsets(word)
    return synsets[0].lexname().lower() if synsets else ""


def get_emotion_context(word: str) -> List[str]:
    """
    Map a word's sentiment polarity to emotion lexemes.
    """
    polarity = TextBlob(word).sentiment.polarity
    if polarity > 0.5:
        return ["HAPPINESS", "SMILE"]
    if polarity > 0.1:
        return ["SMILE"]
    if polarity < -0.5:
        return ["ANGER", "DISGUST"]
    if polarity < -0.1:
        return ["SADNESS", "FROWN"]
    return []

def find_gesture_candidates(text: str, max_gestures: int = 5) -> List[str]:
    """
    Score words by relevance and select top candidates for gesturing.
    Improved: Broader inclusion of verbs and nouns, with adjusted sentiment thresholds.
    """
    blob = TextBlob(text)
    scores: Dict[str, int] = {}

    # BOOST: se la frase è lunga, forziamo 'handup', 'handdown' e 'me'
    boost_targets = {"handup", "handdown", "me"}
    word_count = len(text.split())

    if word_count > 12:
        for bt in boost_targets:
            scores[bt] = 10  # priorità molto alta
    elif word_count > 7:
        for bt in boost_targets:
            scores[bt] = 6  # priorità moderata

    for word, tag in blob.tags:
        token = word.lower().strip(".,!?'" )
        sem = get_semantic_tag(token)
        polarity = TextBlob(token).sentiment.polarity
        score = 0

        # Pronouns strongly suggest gesturing
        if token in {"i", "you", "me", "myself"}:
            score += 3
        # Verbs generally involve actions worth gesturing
        if tag.startswith("VB"):
            score += 2
            # Additional boost for communication verbs
            if "communication" in sem:
                score += 2
        # Nouns can indicate objects or locations
        if tag.startswith("NN"):
            score += 1
            if "location" in sem:
                score += 2
        # Adjectives reveal emotional tone
        if tag.startswith("JJ") and abs(polarity) > 0.1:
            score += 2
        # Moderate sentiment words
        if abs(polarity) > 0.3:
            score += 1
        # Strong sentiment emphasis
        if abs(polarity) > 0.6:
            score += 1

        if score > 0:
            scores[token] = max(scores.get(token, 0), score)

    # Sort by descending score and return top tokens
    sorted_tokens = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [tok for tok, _ in sorted_tokens[:max_gestures]]


def emphasize_words(text: str, gestures: List[str]) -> str:
    """
    Wrap candidate gesture words in markup for later processing.
    """
    def mark(token: str) -> str:
        clean = token.strip(".,!?'").lower()
        return f"*{token}*" if clean in gestures else token
    return ' '.join(mark(tok) for tok in text.split())


def tokenize_and_mark(text: str) -> List[Tuple[str, bool]]:
    """
    Extract tokens and flag those wrapped in *markers*.
    """
    raw = re.findall(r"\*?[\w',.?!]+\*?", text)
    return [
        (tok.strip('*'), tok.startswith('*') and tok.endswith('*'))
        for tok in raw
    ]


def attach_punctuation(tokens: List[str]) -> List[str]:
    """
    Ensure punctuation tokens attach to preceding words.
    """
    merged: List[str] = []
    for tok in tokens:
        if tok in {'.', ',', '!', '?'} and merged:
            merged[-1] += tok
        else:
            merged.append(tok)
    return merged


def assign_time_markers(parsed: List[Tuple[str, bool]]) -> Tuple[List[str], int]:
    """
    Insert <mark> tags around gesture words for BML timing.

    Returns:
        markers: list of text segments (with marks)
        last_index: number of marked words
    """
    markers: List[str] = []
    idx = 0
    for word, is_marked in parsed:
        if is_marked:
            markers.append(f'<mark name="tm{idx}"/> {word}')
            idx += 1
        else:
            markers.append(word)

    # closing marker for end of speech
    markers.append(f'<mark name="tm{idx}"/>')
    return attach_punctuation(markers), idx


def match_gesture(word: str) -> Optional[Dict[str, Any]]:
    """
    Match a word against the gesture database by context.
    """
    contexts = {get_semantic_tag(word)} | set(get_emotion_context(word))
    for cat, group in GESTURE_DB.items():
        for lex, data in group.items():
            if contexts & set(data.get("contexts", [])):
                return {
                    "type": cat,
                    "lexeme": lex,
                    "mode": random.choice(MODES) if cat == "hand" else None,
                }
    return None


def fallback_gesture(word: str) -> Optional[Dict[str, Any]]:
    """
    Provide a basic gesture when no match is found.
    """
    sem = get_semantic_tag(word)
    emo = get_emotion_context(word)

    if "location" in sem:
        # default pointing
        return {"type": "pointing", "lexeme": None, "mode": None, "target": "plate"}
    if "communication" in sem:
        return {"type": "gesture", "lexeme": random.choice(GESTURE_LIST), "mode": random.choice(MODES)}
    if emo:
        lex = emo[0].upper()
        lexeme = lex if lex in FACE_LEXEMES else "NONE"
        return {"type": "face", "lexeme": lexeme, "mode": None}
    return None


def generate_gestures(words: List[str]) -> List[Dict[str, Any]]:
    """
    Build BML gesture entries for marked words.
    """
    entries: List[Dict[str, Any]] = []
    for i, word in enumerate(words):
        gesture = match_gesture(word) or fallback_gesture(word)
        if gesture:
            start_tag = f"s1:tm{i}"
            entries.append({
                "id": f"g{i}",
                **gesture,
                "amount": "1",
                "start": start_tag,
                "end": "start+1",
            })
    return entries

from nltk.tokenize import sent_tokenize
import random

def render_bml(
    xml_id: str,
    markers: List[str],
    gestures: List[Dict[str, Any]],
    last_idx: int,
    full_text: str,
) -> str:
    """
    Create a BML XML string combining posture, gaze, gestures, and speech.
    """
    polarity = TextBlob(full_text).sentiment.polarity
    lines: List[str] = [
        '<?xml version="1.0" encoding="utf-8" ?>',
        f'<bml xmlns="http://www.bml-initiative.org/bml/bml-1.0" '
        'xmlns:ext="http://www.bml-initiative.org/bml/coreextensions-1.0"',
        f'  id="{xml_id}" characterId="Audrey" composition="APPEND">',
    ]

    # Determine posture blocks
    posture_blocks = []

    if polarity < -0.1:
        # Use a single 'armCrossed' posture for negative sentiment
        posture_blocks.append(
            f'  <posture id="pos1" start="0" end="s1:tm{last_idx}+1">\n'
            f'    <stance type="armCrossed"/>\n'
            f'    <target name="User" facing="FRONT"/>\n'
            f'  </posture>'
        )
    else:
        # Posture rotation
        posture_variants = ["akimboLeft", "akimboRight", "akimbo"]
        random.shuffle(posture_variants)

        # Always add the first posture at the beginning
        random_length = random.randint(2, 4)
        lex = posture_variants[0]
        posture_blocks.append(
            f'  <posture id="pos1" start="0" end="start+{random_length}">\n'
            f'    <stance type="{lex}"/>\n'
            f'    <target name="User" facing="FRONT"/>\n'
            f'  </posture>'
        )

        # Add more if text is long
        char_len = len(full_text)
        if char_len >= 300:
            n_additional = 1 if char_len < 500 else 2  # Max 2 extra, for a total of 3
            n_additional = min(n_additional, 2)

            step = max(1, last_idx // (n_additional + 1))
            for i in range(n_additional):
                start_tm = f"s1:tm{min((i + 1) * step, last_idx)}"
                random_length = random.randint(2, 4)
                lex = posture_variants[(i + 1) % len(posture_variants)]
                posture_blocks.append(
                    f'  <posture id="pos{i+2}" start="{start_tm}" end="start+{random_length}">\n'
                    f'    <stance type="{lex}"/>\n'
                    f'    <target name="User" facing="FRONT"/>\n'
                    f'  </posture>'
                )

    # Add posture blocks
    lines += posture_blocks

    # Add gaze
    lines.append(f'  <gaze id="g0" start="0" end="s1:tm{last_idx}+1" target="Camera"/>')

    # Add gestures
    counts = {"face": 0, "head": 0, "gesture": 0, "pointing": 0}
    for g in gestures:
        gtype = g["type"]
        counts[gtype] += 1
        gid = f"{gtype[0]}{counts[gtype]}"
        if gtype == "face":
            lines.append(
                f'  <faceLexeme id="{gid}" lexeme="{g["lexeme"]}" '
                f'amount="1" start="{g["start"]}" end="{g["end"]}"/>'
            )
        elif gtype == "gesture":
            lines.append(
                f'  <gesture id="{gid}" lexeme="{g["lexeme"]}" '
                f'mode="{g.get("mode", "RIGHT_HAND")}" amount="1" '
                f'start="{g["start"]}" end="{g["end"]}"/>'
            )
        elif gtype == "pointing":
            lines.append(
                f'  <pointing id="{gid}" target="{g.get("target", "plate")}" '
                f'start="{g["start"]}" end="{g["end"]}"/>'
            )
        elif gtype == "head":
            lines.append(
                f'  <head id="{gid}" lexeme="{g["lexeme"]}" '
                f'start="{g["start"]}" end="{g["end"]}"/>'
            )

    # Add speech block
    lines += [
        '  <speech id="s1" start="0">',
        '    <description priority="2" type="application/ssml+xml">',
        '      <speak>',
        f'        {" ".join(markers)}',
        '      </speak>',
        '    </description>',
        '  </speech>',
        '</bml>',
    ]
    return "\n".join(lines)

def pipeline(text: str, max_gestures: int = 5) -> str:
    """
    Full end-to-end pipeline: from raw input to BML output.
    """
    # 1. Identify gesture-worthy words
    candidates = find_gesture_candidates(text, max_gestures)
    gen_logger.info(f"Gesture candidates: {candidates}")

    # 2. Mark and parse text
    marked_text = emphasize_words(text, candidates)
    parsed = tokenize_and_mark(marked_text)

    # 3. Insert timing markers
    markers, last_idx = assign_time_markers(parsed)
    words_to_gesture = [word for word, marked in parsed if marked]

    # 4. Generate gesture entries
    gestures = generate_gestures(words_to_gesture)

    # 5. Render final BML
    return render_bml("bml1", markers, gestures, last_idx, text)


# Load gesture DB once at import
gestures_path = "gestures_library_improved.json"
GESTURE_DB = load_gesture_db(gestures_path)


if __name__ == "__main__":
    sample_text = "Hello, how are you? My name is Audrey, I'm a conversational agent.Nice to meet you! What are you eating today?."
    print(pipeline(sample_text))
