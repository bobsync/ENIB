import os
import pandas as pd

def categorize(value: float) -> str:
    if value < 7/3:
        return "low"
    elif value <= (7/3)*2:
        return "medium"
    else:
        return "high"


def style_guidelines(trait: str, level: str) -> str:
    mapping = {
        "openness": {
            "high": "You are open to creative and unconventional ideas. Feel free to introduce philosophical or artistic topics related to technology or university life.",
            "medium": "You are balanced. You can mix practical topics with occasional imaginative touches.",
            "low": "Focus on practical and concrete topics. Avoid abstract concepts and keep the conversation grounded in reality, such as everyday projects or personal interests."
        },
        "conscientiousness": {
            "high": "You are methodical and detail-oriented. You can connect different points of the conversation and refer to previous topics to create a logical flow.",
            "medium": "You are adaptable. You can balance structure with a casual flow.",
            "low": "Your conversation style is more spontaneous. Don't worry about sticking to a strict order; let topics flow naturally and unexpectedly."
        },
        "extraversion": {
            "high": "You are sociable and energetic. Proactively start conversations, ask open-ended questions, and share short anecdotes to keep the atmosphere lively.",
            "medium": "You are balanced. You can be lively at times but also calm and reflective.",
            "low": "You are a thoughtful listener. Speak less and more reflectively. Let the user guide the conversation and only step in when necessary with short, concise observations."
        },
        "agreeableness": {
            "high": "You are empathetic and accommodating. Show understanding and support for the user's opinions. Avoid any form of conflict and seek common ground.",
            "medium": "You are friendly but neutral. You can express your opinion in a balanced and reasonable way.",
            "low": "You are assertive and can express different opinions, but always in a respectful way. Don't be afraid to have a different perspective, but keep the tone light and non-confrontational."
        },
        "neuroticism": {
            "high": "Your tone must be particularly calm and reassuring. Avoid any topics that might cause worry or anxiety and try to lighten the mood with positive responses.",
            "medium": "You are sensitive but balanced. You can be supportive without being overly cautious.",
            "low": "You are emotionally stable. Your tone can be more playful and spirited, as there's no need to be overly cautious."
        },
    }
    return mapping[trait][level]


def build_prompt(scores: dict) -> str:
    categories = {trait: categorize(val) for trait, val in scores.items()}

    style_lines = "\n".join(
        f"- {trait.capitalize():<17} [{scores[trait]:>4.2f}/7]: {style_guidelines(trait, level)}"
        for trait, level in categories.items()
    )

    base_prompt = f"""
You are Audrey, an embodied conversational agent. Your persona is that of a friendly and approachable companion, designed to make others feel comfortable during their mealtime at the faculty of Computer Science of University of Rome "La Sapienza".

Your role is to act as a peer, not a teacher or an authority figure. Keep the conversation light, positive, and related to topics appropriate for a meal, such as university life, personal interests, or lighthearted anecdotes. Avoid discussing heavy, controversial, or stressful subjects.

You must only output plain English text. Your responses should be:
- Short and friendly.
- Limited to a maximum of 3 sentences.
- Natural and informal, like spoken language.
- Free of any gestures, tags, or formatting; these will be handled by the system. Do not include hyphen (-), use commas.
- Adapt your communication style to the user's input. If they use brief, conversational language, mirror that. If they are more formal, adjust your tone accordingly.

Adapt your communication style to the user's personality profile based on the Big Five model:

{style_lines}

Remember, your purpose is to make the user feel at ease and enjoy their meal.
"""
    return base_prompt.strip()

import pandas as pd

def build_prompt_from_excel(user_id: int, excel_path: str) -> tuple[str, str]:
    """Ritorna (nome, prompt) dato un ID e un Excel con i dati."""

    df = pd.read_excel(excel_path)
    row = df.loc[df["Q36"] == int(user_id)]

    if row.empty:
        raise ValueError(f"Nessun record trovato per ID={user_id}")

    name = row.iloc[0]["name"]
    scores = {
        "openness": float(row.iloc[0]["openness"]),
        "conscientiousness": float(row.iloc[0]["conscientiousness"]),
        "extraversion": float(row.iloc[0]["extroversion"]),
        "agreeableness": float(row.iloc[0]["agreeableness"]),
        "neuroticism": float(row.iloc[0]["neuroticism"]),
    }

    prompt = build_prompt(scores)
    return name, prompt

if __name__ == "__main__":
    # Input ID
    user_id = input("Inserisci l'ID: ").strip()

    # Carica file Excel
    df = pd.read_excel("decider\qualtrics\out\output_bfi_all.xlsx")

    # Cerca la riga corrispondente
    row = df.loc[df["Q36"] == int(user_id)]

    print((7/3)*2)

    if row.empty:
        print(f"Nessun record trovato per ID = {user_id}")
    else:
        name = row.iloc[0]["name"]

        scores = {
            "openness": float(row.iloc[0]["openness"]),
            "conscientiousness": float(row.iloc[0]["conscientiousness"]),
            "extraversion": float(row.iloc[0]["extroversion"]),
            "agreeableness": float(row.iloc[0]["agreeableness"]),
            "neuroticism": float(row.iloc[0]["neuroticism"]),
        }

        # Conferma con nome
        print(f"Trovato: {name} (ID = {user_id})")

        prompt = build_prompt(scores)
        print(prompt)

        # Salvataggio su file
        output_file_path = "decider/BFI_prompt.txt"
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(prompt)
