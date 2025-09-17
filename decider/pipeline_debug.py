import json
import logging
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from nltk.corpus import wordnet as wn
from textblob import TextBlob

# Logger setup
gen_logger = logging.getLogger("gesture_pipeline")
logging.basicConfig(filename="gesture_debug.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

FACE_LEXEMES = ["HAPPINESS", "SMILE", "SADNESS", "FEAR", "ANGER", "DISGUST", "FROWN"]
HEAD_LIST = ["nod", "shake", "up", "down", "tilt_left", "tilt_right", "left", "right"]
GESTURE_LIST = ["hello", "handDown", "handUp", "me", "you"]
MODES = ["RIGHT_HAND", "LEFT_HAND"]

def get_semantic_tag(word: str) -> str:
    synsets = wn.synsets(word)
    return synsets[0].lexname().lower() if synsets else ""

def get_emotion_context(word: str) -> List[str]:
    polarity = TextBlob(word).sentiment.polarity
    if polarity > 0.5: return ["HAPPINESS", "SMILE"]
    if polarity > 0.1: return ["SMILE"]
    if polarity < -0.5: return ["ANGER", "DISGUST"]
    if polarity < -0.1: return ["SADNESS", "FROWN"]
    return []

def find_gesture_candidates(text: str, max_gestures: int = 5) -> List[str]:
    blob = TextBlob(text)
    scores: Dict[str, int] = {}

    tokens = list(blob.tags)
    word_count = len(tokens)

    # Scala dinamica più contenuta: +1 ogni 15 parole
    scaled_max = min(8, max_gestures + word_count // 10)


    for word, tag in tokens:
        token = word.lower().strip(".,!?'" )
        sem = get_semantic_tag(token)
        polarity = TextBlob(token).sentiment.polarity
        score = 0

        # print(f"[TOK] '{token}' POS={tag}, Pol={polarity:.2f}, Sem='{sem}'")

        if token in {"i", "you", "me", "myself"}:
            score += 1
        if tag.startswith("VB"):
            score += 2
        if "communication" in sem:
            score += 2
        if tag.startswith("NN"):
            score += 1
        if "location" in sem:
            score += 1
        if tag.startswith("JJ") and abs(polarity) > 0.1:
            score += 2
        if abs(polarity) > 0.3:
            score += 1
        if abs(polarity) > 0.6:
            score += 1

        if score > 0:
            scores[token] = max(scores.get(token, 0), score)

    sorted_tokens = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_tokens = [tok for tok, _ in sorted_tokens[:scaled_max]]

    return top_tokens


def emphasize_words(text: str, gestures: List[str]) -> str:
    def mark(token: str) -> str:
        clean = token.strip(".,!?'").lower()
        return f"*{token}*" if clean in gestures else token
    return ' '.join(mark(tok) for tok in text.split())

def tokenize_and_mark(text: str) -> List[Tuple[str, bool]]:
    raw = re.findall(r"\*?[\w',.?!]+\*?", text)
    return [(tok.strip('*'), tok.startswith('*') and tok.endswith('*')) for tok in raw]

def attach_punctuation(tokens: List[str]) -> List[str]:
    merged: List[str] = []
    for tok in tokens:
        if tok in {'.', ',', '!', '?'} and merged: merged[-1] += tok
        else: merged.append(tok)
    return merged

def assign_time_markers(parsed: List[Tuple[str, bool]]) -> Tuple[List[str], int]:
    markers: List[str] = []
    idx = 0
    for word, is_marked in parsed:
        if is_marked:
            markers.append(f'<mark name="tm{idx}"/> {word}')
            idx += 1
        else:
            markers.append(word)
    markers.append(f'<mark name="tm{idx}"/>')
    return attach_punctuation(markers), idx

def fallback_gesture(word: str) -> Optional[Dict[str, Any]]:
    sem = get_semantic_tag(word)
    emo = get_emotion_context(word)
    
    if word.lower() in {"me", "you"}:
        return {"type": "gesture", "lexeme": word.lower(), "mode": "RIGHT_HAND"}
    if "location" in sem: #<head id="h2" lexeme="NOD" start="s1:tm6+1" end ="s1:tm7" repetition="1"/>
        return {"type": "head", "lexeme": random.choice(HEAD_LIST)}
    if "communication" in sem:
        return {"type": "gesture", "lexeme": random.choice(GESTURE_LIST), "mode": random.choice(MODES)}
    if emo:
        lex = emo[0].upper()
        lexeme = lex if lex in FACE_LEXEMES else "NONE"
        return {"type": "face", "lexeme": lexeme, "mode": None}
    return None

def generate_gestures(words: List[str], last_idx: int) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for i, word in enumerate(words):
        gesture = fallback_gesture(word)
        if gesture:
            print(f"[GESTURE] {word} → {gesture}")
            start_tag = f"s1:tm{i}"
            entries.append({
                "id": f"g{i}",
                **gesture,
                "amount": "1",
                "start": start_tag,
                "end": "start+1",
            })
        else:
            print(f"[NO MATCH] {word} → fallback or skipped")

    return entries

def render_bml(xml_id: str, markers: List[str], gestures: List[Dict[str, Any]], last_idx: int, full_text: str) -> str:
    polarity = TextBlob(full_text).sentiment.polarity
    lines: List[str] = [
        '<?xml version="1.0" encoding="utf-8" ?>',
        f'<bml xmlns="http://www.bml-initiative.org/bml/bml-1.0" xmlns:ext="http://www.bml-initiative.org/bml/coreextensions-1.0"',
        f'  id="{xml_id}" characterId="Audrey" composition="APPEND">',
    ]
    posture_blocks = []
    if polarity < -0.1:
        posture_blocks.append(f'  <posture id="pos1" start="0" end="s1:tm{last_idx}+1"><stance type="armCrossed"/><target name="User" facing="FRONT"/></posture>')
    else:
        posture_variants = ["akimboLeft", "akimboRight", "akimbo"]
        random.shuffle(posture_variants)
        random_length = random.randint(2, 4)
        lex = posture_variants[0]
        posture_blocks.append(f'  <posture id="pos1" start="0" end="start+{random_length}"><stance type="{lex}"/><target name="User" facing="FRONT"/></posture>')
        if len(full_text) >= 300:
            n_additional = 1 if len(full_text) < 500 else 2
            step = max(1, last_idx // (n_additional + 1))
            for i in range(n_additional):
                start_tm = f"s1:tm{min((i + 1) * step, last_idx)}"
                random_length = random.randint(2, 4)
                lex = posture_variants[(i + 1) % len(posture_variants)]
                posture_blocks.append(f'  <posture id="pos{i+2}" start="{start_tm}" end="start+{random_length}"><stance type="{lex}"/><target name="User" facing="FRONT"/></posture>')
    lines += posture_blocks
    lines.append(f'  <gaze id="g0" start="0" end="s1:tm{last_idx}+1" target="Camera"/>')
    counts = {"face": 0, "head": 0, "gesture": 0, "pointing": 0}
    for g in gestures:
        gtype = g["type"]
        counts[gtype] += 1
        gid = f"{gtype[0]}{counts[gtype]}"
        
        if gtype == "face":
            lines.append(f'  <faceLexeme id="{gid}" lexeme="{g["lexeme"]}" amount="1" start="{g["start"]}" end="{g["end"]}"/>')
        elif gtype == "gesture":
            lines.append(f'  <gesture id="{gid}" lexeme="{g["lexeme"]}" mode="{g.get("mode", "RIGHT_HAND")}" amount="1" start="{g["start"]}" end="{g["end"]}"/>')
        elif gtype == "pointing":
            lines.append(f'  <pointing id="{gid}" target="{g.get("target", "plate")}" start="{g["start"]}" end="{g["end"]}"/>')
        elif gtype == "head":
            lines.append(f'  <head id="{gid}" lexeme="{g["lexeme"]}" start="{g["start"]}" end="{g["end"]}" repetition="1"/>')

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
    candidates = find_gesture_candidates(text, max_gestures)
    print(f"[CANDIDATES] {candidates}")
    gen_logger.info(f"Gesture candidates: {candidates}")
    marked_text = emphasize_words(text, candidates)
    print(f"[MARKED] {marked_text}")
    parsed = tokenize_and_mark(marked_text)
    markers, last_idx = assign_time_markers(parsed)
    words_to_gesture = [word.strip(".,!?").lower() for word, marked in parsed if marked]
    print(f"[GESTURE TOKENS] {words_to_gesture}")
    gestures = generate_gestures(words_to_gesture, last_idx)
    bml = render_bml("bml1", markers, gestures, last_idx, text)
    print(f"[BML LEN] {len(bml)} chars, {len(gestures)} gestures\n")
    return bml

if __name__ == "__main__":
    short_test_sentences = [
        "I'm thrilled to talk with you today! You always make me smile. It's going to be a great session, full of ideas.",
        "I felt so disappointed and angry after the meeting yesterday. It was hard to concentrate and my mood dropped quickly.",
        "Could you explain this problem to me? I really need your help before the deadline tomorrow morning.",
        "She placed the book on the table and walked away in silence, ignoring everything happening around her.",
        "It was a wonderful surprise, but something about it felt wrong and made me hesitate to respond immediately."
    ]

    long_test_sentences = [
        "I'm extremely happy to finally have the opportunity to talk with you about everything that's been going on lately. Your advice has always helped me reflect and gain perspective, especially when things get confusing or emotionally intense. Being able to share openly is such a relief, and I really appreciate your support every time we talk.",
        "Yesterday's presentation didn't go as planned, and honestly, I felt deeply disappointed and even a bit ashamed of the way I handled the questions. I kept thinking about how I could have responded better, and the frustration built up as I reviewed the feedback. But now I want to take this as a learning opportunity and make sure I do better next time.",
        "Could you explain the process we followed during the last brainstorming session, especially the way we evaluated each idea? I think I missed a few important points, and I’d like to clarify them before we move forward. It’s crucial for me to understand every detail so I can contribute meaningfully during tomorrow’s meeting.",
        "She walked into the room quietly, placed her notes on the table, and looked around without saying a word. Everyone was watching, but she ignored their gazes and started presenting confidently, as if nothing had happened. The silence that followed was intense, and I could tell people were both impressed and confused by her demeanor.",
        "It was such a pleasant surprise to see everyone smiling and laughing again after the difficult week we had. The atmosphere felt lighter, and the sense of togetherness really made a difference. Even though some problems are still unresolved, having that joyful moment helped me regain a bit of hope and motivation to keep pushing forward."
    ]

    output_dir = Path("test")
    output_dir.mkdir(exist_ok=True)

    # Process short sentences
    for idx, sentence in enumerate(short_test_sentences):
        print(f"\n=== Short Test {idx+1} ===")
        bml = pipeline(sentence)
        output_path = output_dir / f"short_bml_{idx+1}.xml"
        with output_path.open("w", encoding="utf-8") as f:
            f.write(bml)
        print(f"[SAVED] {output_path}")

    # Process long sentences
    for idx, sentence in enumerate(long_test_sentences):
        print(f"\n=== Long Test {idx+1} ===")
        bml = pipeline(sentence)
        output_path = output_dir / f"long_bml_{idx+1}.xml"
        with output_path.open("w", encoding="utf-8") as f:
            f.write(bml)
        print(f"[SAVED] {output_path}")
