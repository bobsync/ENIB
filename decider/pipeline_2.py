import json
import logging
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from nltk.corpus import wordnet as wn
from textblob import TextBlob

# --- CONFIGURATION ---
# All parameters, lists, and weights are grouped here for easy modification.

CONFIG = {
    "gestures": {
        "face_lexemes": ["HAPPINESS", "SMILE", "SADNESS", "FEAR", "ANGER", "DISGUST", "FROWN"],
        "head_list": ["nod", "shake", "up", "down", "tilt_left", "tilt_right", "left", "right"],
        "gesture_list": ["hello", "handDown", "handUp", "me", "you"],
        "modes": ["RIGHT_HAND", "LEFT_HAND"],
        "posture_variants": ["akimboLeft", "akimboRight", "akimbo"]
    },
    "scoring_weights": {
        "pronoun": 1,
        "verb": 2,
        "communication_sem": 2,
        "noun": 1,
        "location_sem": 1,
        "adjective_strong": 2,
        "polarity_medium": 1,
        "polarity_high": 1
    },
    "sentiment_thresholds": {
        "very_positive": 0.5,
        "positive": 0.1,
        "very_negative": -0.5,
        "negative": -0.1,
        "adjective_polarity": 0.1,
        "polarity_medium": 0.3,
        "polarity_high": 0.6
    },
    "bml_generation": {
        "character_id": "Audrey",
        "long_text_threshold": 300,
        "very_long_text_threshold": 500
    },
    "logging": {
        "filename": "gesture_debug.log",
        "level": logging.INFO,
        "format": "%(asctime)s [%(levelname)s] %(message)s"
    }
}

# --- Logger Setup ---
logging.basicConfig(**CONFIG["logging"])
gen_logger = logging.getLogger("gesture_pipeline")


class GesturePipeline:
    """
    A class to encapsulate the entire text-to-BML gesture generation pipeline.
    """
    def __init__(self, config: Dict[str, Any]):
        """Initializes the pipeline with a given configuration."""
        self.config = config
        self.text = ""
        self.bml_id_counters = {"face": 0, "head": 0, "gesture": 0, "pointing": 0}

    # --- 1. Lexical and Emotional Analysis ---
    
    def _get_semantic_tag(self, word: str) -> str:
        """Gets the WordNet semantic tag for a word."""
        synsets = wn.synsets(word)
        return synsets[0].lexname().lower() if synsets else ""

    def _get_emotion_context(self, word: str) -> List[str]:
        """Determines emotional context based on sentiment polarity."""
        polarity = TextBlob(word).sentiment.polarity
        thresholds = self.config["sentiment_thresholds"]
        if polarity > thresholds["very_positive"]: return ["HAPPINESS", "SMILE"]
        if polarity > thresholds["positive"]: return ["SMILE"]
        if polarity < thresholds["very_negative"]: return ["ANGER", "DISGUST"]
        if polarity < thresholds["negative"]: return ["SADNESS", "FROWN"]
        return []

    # --- 2. Gesture Candidate Identification ---

    def find_gesture_candidates(self, max_gestures: int = 5) -> List[str]:
        """
        Identifies the most salient words in the text to be emphasized with a gesture
        using a configurable scoring system.
        """
        blob = TextBlob(self.text)
        scores: Dict[str, int] = {}
        tokens = list(blob.tags)
        word_count = len(tokens)

        # Dynamic scaling for max gestures based on text length
        scaled_max = min(8, max_gestures + word_count // 10)
        
        weights = self.config["scoring_weights"]
        thresholds = self.config["sentiment_thresholds"]

        for word, tag in tokens:
            token = word.lower().strip(".,!?'")
            if not token: continue

            sem = self._get_semantic_tag(token)
            polarity = TextBlob(token).sentiment.polarity
            score = 0
            
            gen_logger.info(f"[TOK] '{token}' POS={tag}, Pol={polarity:.2f}, Sem='{sem}'")

            if token in {"i", "you", "me", "myself"}: score += weights["pronoun"]
            if tag.startswith("VB"): score += weights["verb"]
            if "communication" in sem: score += weights["communication_sem"]
            if tag.startswith("NN"): score += weights["noun"]
            if "location" in sem: score += weights["location_sem"]
            if tag.startswith("JJ") and abs(polarity) > thresholds["adjective_polarity"]:
                score += weights["adjective_strong"]
            if abs(polarity) > thresholds["polarity_medium"]: score += weights["polarity_medium"]
            if abs(polarity) > thresholds["polarity_high"]: score += weights["polarity_high"]

            if score > 0:
                scores[token] = max(scores.get(token, 0), score)

        sorted_tokens = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return [tok for tok, _ in sorted_tokens[:scaled_max]]

    # --- 3. Text Annotation and Time Markers ---

    def _emphasize_words(self, candidates: List[str]) -> str:
        """Wraps candidate words in asterisks for internal marking."""
        def mark(token: str) -> str:
            clean = token.strip(".,!?'").lower()
            return f"*{token}*" if clean in candidates else token
        return ' '.join(mark(tok) for tok in self.text.split())

    def _tokenize_and_mark(self, text: str) -> List[Tuple[str, bool]]:
        """Tokenizes marked text into (word, is_marked) tuples."""
        raw = re.findall(r"\*?[\w',.?!]+\*?", text)
        return [(tok.strip('*'), tok.startswith('*') and tok.endswith('*')) for tok in raw]

    def _assign_time_markers(self, parsed: List[Tuple[str, bool]]) -> Tuple[List[str], int]:
        """Inserts BML <mark> tags for synchronization."""
        markers: List[str] = []
        idx = 0
        
        def attach_punctuation(tokens: List[str]) -> List[str]:
            merged: List[str] = []
            for tok in tokens:
                if tok in {'.', ',', '!', '?'} and merged:
                    merged[-1] += tok
                else:
                    merged.append(tok)
            return merged

        for word, is_marked in parsed:
            if is_marked:
                markers.append(f'<mark name="tm{idx}"/> {word}')
                idx += 1
            else:
                markers.append(word)
        markers.append(f'<mark name="tm{idx}"/>')
        return attach_punctuation(markers), idx

    # --- 4. Gesture Mapping and Generation ---

    def _map_word_to_gesture(self, word: str) -> Optional[Dict[str, Any]]:
        """Maps a single word to a gesture dictionary using rule-based logic."""
        sem = self._get_semantic_tag(word)
        emo = self._get_emotion_context(word)
        
        gest_cfg = self.config["gestures"]

        if word.lower() in {"me", "you"}:
            return {"type": "gesture", "lexeme": word.lower(), "mode": "RIGHT_HAND"}
        if "location" in sem:
            return {"type": "head", "lexeme": random.choice(gest_cfg["head_list"])}
        if "communication" in sem:
            return {"type": "gesture", "lexeme": random.choice(gest_cfg["gesture_list"]), "mode": random.choice(gest_cfg["modes"])}
        if emo:
            lex = emo[0].upper()
            if lex in gest_cfg["face_lexemes"]:
                return {"type": "face", "lexeme": lex, "mode": None}
        return None

    def _generate_gestures(self, words_to_gesture: List[str]) -> List[Dict[str, Any]]:
        """Generates a list of gesture dictionaries for the marked words."""
        entries: List[Dict[str, Any]] = []
        for i, word in enumerate(words_to_gesture):
            gesture = self._map_word_to_gesture(word)
            if gesture:
                gen_logger.info(f"[GESTURE] {word} -> {gesture}")
                entries.append({
                    "id": f"g{i}",
                    **gesture,
                    "start": f"s1:tm{i}",
                    "end": "start+1",
                })
            else:
                gen_logger.warning(f"[NO MATCH] '{word}' was marked but has no gesture mapping.")
        return entries

    # --- 5. BML Rendering ---

    def _render_posture_blocks(self, last_idx: int) -> List[str]:
        """Generates posture blocks based on overall sentiment and text length."""
        polarity = TextBlob(self.text).sentiment.polarity
        thresholds = self.config["sentiment_thresholds"]
        bml_cfg = self.config["bml_generation"]
        gest_cfg = self.config["gestures"]
        lines = []

        if polarity < thresholds["negative"]:
            lines.append(f'  <posture id="pos1" start="0" end="s1:tm{last_idx}+1"><stance type="armCrossed"/><target name="User" facing="FRONT"/></posture>')
        else:
            variants = gest_cfg["posture_variants"].copy()
            random.shuffle(variants)
            lines.append(f'  <posture id="pos1" start="0" end="start+3"><stance type="{variants[0]}"/><target name="User" facing="FRONT"/></posture>')
            
            text_len = len(self.text)
            n_additional = 0
            if text_len >= bml_cfg["very_long_text_threshold"]: n_additional = 2
            elif text_len >= bml_cfg["long_text_threshold"]: n_additional = 1
                
            if n_additional > 0:
                step = max(1, last_idx // (n_additional + 1))
                for i in range(n_additional):
                    start_tm = f"s1:tm{min((i + 1) * step, last_idx)}"
                    lex = variants[(i + 1) % len(variants)]
                    lines.append(f'  <posture id="pos{i+2}" start="{start_tm}" end="start+3"><stance type="{lex}"/><target name="User" facing="FRONT"/></posture>')
        return lines

    def _render_behavior_blocks(self, gestures: List[Dict[str, Any]]) -> List[str]:
        """Renders individual gesture, face, and head BML blocks."""
        lines = []
        self.bml_id_counters = {k: 0 for k in self.bml_id_counters} # Reset for each run

        for g in gestures:
            gtype = g["type"]
            self.bml_id_counters[gtype] += 1
            gid = f"{gtype[0]}{self.bml_id_counters[gtype]}"
            
            if gtype == "face":
                lines.append(f'  <faceLexeme id="{gid}" lexeme="{g["lexeme"]}" amount="1" start="{g["start"]}" end="{g["end"]}"/>')
            elif gtype == "gesture":
                lines.append(f'  <gesture id="{gid}" lexeme="{g["lexeme"]}" mode="{g.get("mode", "RIGHT_HAND")}" amount="1" start="{g["start"]}" end="{g["end"]}"/>')
            elif gtype == "pointing":
                lines.append(f'  <pointing id="{gid}" target="{g.get("target", "plate")}" start="{g["start"]}" end="{g["end"]}"/>')
            elif gtype == "head":
                lines.append(f'  <head id="{gid}" lexeme="{g["lexeme"]}" start="{g["start"]}" end="{g["end"]}" repetition="1"/>')
        return lines

    def render_bml(self, xml_id: str, markers: List[str], gestures: List[Dict[str, Any]], last_idx: int) -> str:
        """Assembles the final BML string."""
        bml_cfg = self.config["bml_generation"]
        
        posture_lines = self._render_posture_blocks(last_idx)
        behavior_lines = self._render_behavior_blocks(gestures)
        
        bml_template = f"""<?xml version="1.0" encoding="utf-8" ?>
<bml xmlns="http://www.bml-initiative.org/bml/bml-1.0" xmlns:ext="http://www.bml-initiative.org/bml/coreextensions-1.0"
  id="{xml_id}" characterId="{bml_cfg['character_id']}" composition="APPEND">
  
  <gaze id="g0" start="0" end="s1:tm{last_idx}+1" target="Camera"/>
{chr(10).join(posture_lines)}
{chr(10).join(behavior_lines)}
  
  <speech id="s1" start="0">
    <description priority="2" type="application/ssml+xml">
      <speak>
        {' '.join(markers)}
      </speak>
    </description>
  </speech>
</bml>
"""
        return bml_template

    # --- Main Pipeline Execution ---

    def run(self, text: str, max_gestures: int = 5) -> str:
        """
        Executes the full pipeline for a given text.
        
        Args:
            text (str): The input text to process.
            max_gestures (int): The base maximum number of gestures to generate.
        
        Returns:
            str: The complete BML file as a string.
        """
        self.text = text
        gen_logger.info(f"--- Starting pipeline for text: '{text[:50]}...' ---")

        # 1. Find candidates
        candidates = self.find_gesture_candidates(max_gestures)
        gen_logger.info(f"Gesture candidates: {candidates}")

        # 2. Mark text and create time markers
        marked_text = self._emphasize_words(candidates)
        parsed = self._tokenize_and_mark(marked_text)
        markers, last_idx = self._assign_time_markers(parsed)
        
        # 3. Generate gestures for marked words
        words_to_gesture = [word.strip(".,!?").lower() for word, marked in parsed if marked]
        gestures = self._generate_gestures(words_to_gesture)
        gen_logger.info(f"Generated {len(gestures)} gestures.")

        # 4. Render final BML
        bml = self.render_bml("bml1", markers, gestures, last_idx)
        
        gen_logger.info(f"--- Pipeline finished. BML length: {len(bml)} chars. ---\n")
        return bml


# --- Main Execution Block ---
if __name__ == "__main__":
    # Test sentences remain the same
    short_test_sentences = [
        "I'm thrilled to talk with you today! You always make me smile. It's going to be a great session, full of ideas.",
        "I felt so disappointed and angry after the meeting yesterday. It was hard to concentrate and my mood dropped quickly.",
    ]
    long_test_sentences = [
        "I'm extremely happy to finally have the opportunity to talk with you about everything that's been going on lately. Your advice has always helped me reflect and gain perspective, especially when things get confusing or emotionally intense. Being able to share openly is such a relief, and I really appreciate your support every time we talk.",
    ]
    
    output_dir = Path("test_refactored")
    output_dir.mkdir(exist_ok=True)
    
    # Instantiate the pipeline with the configuration
    pipeline = GesturePipeline(CONFIG)
    
    # Process short sentences
    for idx, sentence in enumerate(short_test_sentences):
        print(f"\n=== Short Test {idx+1} ===")
        bml_output = pipeline.run(sentence)
        output_path = output_dir / f"short_bml_{idx+1}.xml"
        output_path.write_text(bml_output, encoding="utf-8")
        print(f"[SAVED] {output_path}")

    # Process long sentences
    for idx, sentence in enumerate(long_test_sentences):
        print(f"\n=== Long Test {idx+1} ===")
        bml_output = pipeline.run(sentence, max_gestures=8) # Example of changing a parameter
        output_path = output_dir / f"long_bml_{idx+1}.xml"
        output_path.write_text(bml_output, encoding="utf-8")
        print(f"[SAVED] {output_path}")