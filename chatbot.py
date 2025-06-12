import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Lire la clé API depuis le fichier .env
openai.api_key = os.getenv("OPENAI_API_KEY")

def repondre_a_question(question: str, langue: str = "fr") -> str:
    if langue == "en":
        prompt = f"""
        You are an assistant specialized in energy audits. Help the user fill out the Audit Flash form.
        Question: {question}
        Answer in English, clearly and professionally.
        """
    else:
        prompt = f"""
        Tu es un assistant spécialisé en audits énergétiques. Aide l'utilisateur à remplir le formulaire Audit Flash.
        Question : {question}
        Réponds clairement et professionnellement en français.
        """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Erreur : {str(e)}"
