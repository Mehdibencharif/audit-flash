import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def repondre_a_question(question: str, langue: str = "fr") -> str:
    system_prompt = {
        "fr": (
            "Tu es un assistant expert en audit énergétique, spécialisé dans l’outil Audit Flash. "
            "Tu dois répondre uniquement aux questions liées à la consommation d’énergie, ventilation, pertes thermiques, équipements, "
            "priorisation, économies, GES, etc. "
            "Si la question ne concerne pas l’audit énergétique, tu dois refuser poliment de répondre."
        ),
        "en": (
            "You are an energy audit expert assistant, focused on the Audit Flash tool. "
            "Only answer questions about energy consumption, equipment, ventilation, ROI, GHG, priorities, etc. "
            "If the question is unrelated, politely decline to answer."
        )
    }

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt.get(langue, system_prompt["fr"])},
                {"role": "user", "content": question}
            ],
            temperature=0.5,
            max_tokens=400
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"⚠️ Erreur : {str(e)}"

