import streamlit as st
from datetime import date
from fpdf import FPDF
import io
import re
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt
import requests
import uuid
import json
from datetime import datetime
import sqlite3

# ================================
# CONFIGURATION BASE DE DONNÉES
# ================================

def init_database():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect('audit_flash.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS formulaires (
            form_id TEXT PRIMARY KEY,
            data TEXT,
            created_at TEXT,
            updated_at TEXT,
            email_contact TEXT,
            statut TEXT DEFAULT 'en_cours'
        )
    ''')
    conn.commit()
    return conn

def sauvegarder_formulaire(form_id, data_dict, email_contact=""):
    """Sauvegarde les données du formulaire"""
    try:
        conn = sqlite3.connect('audit_flash.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Vérifier si le formulaire existe déjà
        cursor.execute("SELECT form_id FROM formulaires WHERE form_id = ?", (form_id,))
        exists = cursor.fetchone()
        
        now = datetime.utcnow().isoformat()
        data_json = json.dumps(data_dict, ensure_ascii=False)
        
        if exists:
            cursor.execute("""
                UPDATE formulaires 
                SET data = ?, updated_at = ?, email_contact = ?
                WHERE form_id = ?
            """, (data_json, now, email_contact, form_id))
        else:
            cursor.execute("""
                INSERT INTO formulaires (form_id, data, created_at, updated_at, email_contact, statut)
                VALUES (?, ?, ?, ?, ?, 'en_cours')
            """, (form_id, data_json, now, now, email_contact))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")
        return False

def charger_formulaire(form_id):
    """Charge un formulaire existant depuis la base de données"""
    try:
        conn = sqlite3.connect('audit_flash.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM formulaires WHERE form_id = ?", (form_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return None

def get_or_create_form_id():
    """Récupère ou crée un ID de formulaire unique"""
    # Vérifier dans les paramètres d'URL
    query_params = st.query_params
    form_id_from_url = query_params.get("form_id", None)
    
    # Si un form_id est déjà dans session_state, le garder
    if "form_id" in st.session_state:
        return st.session_state["form_id"]
    
    # Si un form_id est dans l'URL, charger les données
    if form_id_from_url:
        st.session_state["form_id"] = form_id_from_url
        data = charger_formulaire(form_id_from_url)
        if data:
            # Charger toutes les données dans session_state
            for key, value in data.items():
                st.session_state[key] = value
            st.session_state["formulaire_charge"] = True
        return form_id_from_url
    
    # Créer un nouveau form_id
    new_id = str(uuid.uuid4())
    st.session_state["form_id"] = new_id
    st.query_params["form_id"] = new_id
    return new_id

def collecter_donnees_formulaire():
    """Collecte toutes les données du formulaire depuis session_state"""
    return {
        # Informations générales
        "client_nom": st.session_state.get("client_nom", ""),
        "site_nom": st.session_state.get("site_nom", ""),
        "adresse": st.session_state.get("adresse", ""),
        "ville": st.session_state.get("ville", ""),
        "province": st.session_state.get("province", ""),
        "code_postal": st.session_state.get("code_postal", ""),
        
        # Contacts
        "contact_ee_nom": st.session_state.get("contact_ee_nom", ""),
        "contact_ee_mail": st.session_state.get("contact_ee_mail", ""),
        "contact_ee_tel": st.session_state.get("contact_ee_tel", ""),
        "contact_ee_ext": st.session_state.get("contact_ee_ext", ""),
        "contact_maint_nom": st.session_state.get("contact_maint_nom", ""),
        "contact_maint_mail": st.session_state.get("contact_maint_mail", ""),
        "contact_maint_tel": st.session_state.get("contact_maint_tel", ""),
        "contact_maint_ext": st.session_state.get("contact_maint_ext", ""),
        "rempli_nom": st.session_state.get("rempli_nom", ""),
        "rempli_date": str(st.session_state.get("rempli_date", "")),
        "rempli_mail": st.session_state.get("rempli_mail", ""),
        "rempli_tel": st.session_state.get("rempli_tel", ""),
        "rempli_ext": st.session_state.get("rempli_ext", ""),
        
        # Objectifs
        "sauver_ges": st.session_state.get("sauver_ges", ""),
        "economie_energie": st.session_state.get("economie_energie", False),
        "gain_productivite": st.session_state.get("gain_productivite", False),
        "roi_vise": st.session_state.get("roi_vise", ""),
        "remplacement_equipement": st.session_state.get("remplacement_equipement", False),
        "investissement_prevu": st.session_state.get("investissement_prevu", ""),
        "autres_objectifs": st.session_state.get("autres_objectifs", ""),
        
        # Priorités
        "priorite_energie": st.session_state.get("priorite_energie", 5),
        "priorite_roi": st.session_state.get("priorite_roi", 5),
        "priorite_ges": st.session_state.get("priorite_ges", 5),
        "priorite_prod": st.session_state.get("priorite_prod", 5),
        "priorite_maintenance": st.session_state.get("priorite_maintenance", 5),
        
        # Services
        "controle": st.session_state.get("controle", False),
        "maintenance": st.session_state.get("maintenance", False),
        "ventilation": st.session_state.get("ventilation", False),
        "autres_services": st.session_state.get("autres_services", ""),
        
        # Documents
        "temps_fonctionnement": st.session_state.get("temps_fonctionnement", ""),
        
        # Équipements (convertir DataFrames en dict)
        "chaudieres": _df_to_dict("chaudieres"),
        "frigo": _df_to_dict("frigo"),
        "compresseur": _df_to_dict("compresseur"),
        "pompes": _df_to_dict("pompes"),
        "ventilation_eq": _df_to_dict("ventilation"),
        "machines": _df_to_dict("machines"),
        "eclairage": _df_to_dict("eclairage"),
        "depoussieur": _df_to_dict("depoussieur"),
    }

def _df_to_dict(key):
    """Convertit un DataFrame en liste de dicts pour JSON"""
    val = st.session_state.get(key, None)
    if isinstance(val, pd.DataFrame):
        return val.to_dict('records')
    elif isinstance(val, dict):
        if "added_rows" in val:
            return val.get("added_rows", [])
    elif isinstance(val, list):
        return val
    return []

def sauvegarder_auto():
    """Sauvegarde automatique appelée après modifications"""
    if "form_id" not in st.session_state:
        return
    
    form_id = st.session_state["form_id"]
    data = collecter_donnees_formulaire()
    email = data.get("contact_ee_mail", "")
    
    sauvegarder_formulaire(form_id, data, email)

# Initialiser la DB au démarrage
init_database()

# CONFIGURATION GLOBALE
st.set_page_config(page_title="Formulaire Audit Flash", layout="wide")

# ================================
# RÉCUPÉRATION/CRÉATION FORM_ID
# ================================
form_id = get_or_create_form_id()

# ==========================
# Choix de la langue
# ==========================
langue = st.radio(
    "Langue / Language",
    ("Français", "English"),
    horizontal=True,
    key="langue_radio"
)

# Dictionnaire de traduction global
translations = {
    "fr": {
        "titre_infos": "📄 1. Informations générales",
        "texte_expander": "Cliquez ici pour remplir cette section",
    },
    "en": {
        "titre_infos": "📄 1. General Information",
        "texte_expander": "Click here to fill out this section",
    }
}

lang = "fr" if langue == "Français" else "en"

# ================================
# BANDEAU DE SAUVEGARDE
# ================================
st.markdown("""
<style>
.save-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.save-banner h3 {
    margin: 0 0 10px 0;
    font-size: 20px;
}
.save-banner p {
    margin: 5px 0;
    font-size: 14px;
    opacity: 0.95;
}
.url-box {
    background: rgba(255,255,255,0.15);
    padding: 12px;
    border-radius: 8px;
    margin-top: 12px;
    font-family: monospace;
    word-break: break-all;
}
</style>
""", unsafe_allow_html=True)

# Bandeau de sauvegarde
url_complete = f"https://audit-flash-mgrrwuxnxiqslifj2dpwgk.streamlit.app/?form_id={form_id}"

if lang == "fr":
    st.markdown(f"""
    <div class='save-banner'>
        <h3>💾 Sauvegarde automatique activée</h3>
        <p>✅ Votre progression est sauvegardée automatiquement toutes les 30 secondes.</p>
        <p>📤 <strong>Partagez ce lien</strong> avec vos collègues pour qu'ils puissent continuer le formulaire :</p>
        <div class='url-box'>{url_complete}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class='save-banner'>
        <h3>💾 Auto-save enabled</h3>
        <p>✅ Your progress is automatically saved every 30 seconds.</p>
        <p>📤 <strong>Share this link</strong> with colleagues to continue the form:</p>
        <div class='url-box'>{url_complete}</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 1])
with col2:
    if st.button("💾 Sauvegarder" if lang == "fr" else "💾 Save Now"):
        sauvegarder_auto()
        st.success("✅ Sauvegardé!" if lang == "fr" else "✅ Saved!")

with col3:
    if st.button("🔄 Nouvelle session" if lang == "fr" else "🔄 New Session"):
        # Effacer session_state et créer nouveau form_id
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.query_params.clear()
        st.rerun()

# Message si formulaire chargé
if st.session_state.get("formulaire_charge"):
    st.info("📂 Formulaire existant chargé avec succès!" if lang == "fr" else "📂 Existing form loaded successfully!")
    st.session_state["formulaire_charge"] = False

st.divider()

# ================================
# Assistant IA gratuit via Groq
# ================================

def _get_groq_key() -> str | None:
    """Récupère la clé GROQ_API_KEY depuis l'environnement ou st.secrets"""
    key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_APIKEY")
    try:
        key = key or st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ_APIKEY")
    except Exception:
        pass
    if not key:
        return None
    return str(key).strip().strip('"').strip("'")

def repondre_a_question(question: str, langue: str = "fr") -> str:
    """Répond via l'API gratuite Groq (modèle Llama 3.1 8B Instant)"""
    q = (question or "").strip()
    if not q:
        return "⚠️ Aucune question fournie."

    api_key = _get_groq_key()
    if not api_key:
        return ("⚠️ Clé GROQ_API_KEY manquante. Ajoute-la dans Settings → Secrets "
                "ou comme variable d'environnement.")

    system_msg = (
        "Tu es un assistant concis en efficacité énergétique. "
        "Réponds en {langue} avec définitions claires, formules simples, "
        "règles de pouce et un mini-exemple si utile."
    ).format(langue="fr" if langue.lower().startswith("fr") else "en")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": q},
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=45)
        if r.status_code != 200:
            try:
                info = r.json()
            except Exception:
                info = {"error": r.text}
            return f"⚠️ Erreur Groq ({r.status_code}) : {info}"
        data = r.json()
        return (data["choices"][0]["message"]["content"] or "").strip()
    except requests.exceptions.RequestException as e:
        return f"⚠️ Erreur réseau Groq : {e}"
    except Exception as e:
        return f"⚠️ Erreur inattendue : {e}"

# ================================
# Interface Streamlit (UI Chatbot) Sidebar
# ================================
st.markdown("""
<style>
section[data-testid="stSidebar"] { 
  width: 420px !important; 
}
@media (max-width: 1200px){
  section[data-testid="stSidebar"] { width: 360px !important; }
}
.chat-hero {
  background: #cddc39;
  color: #37474f;
  padding: 12px 14px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 18px;
  margin-bottom: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}
.chat-card {
  background: #f6f8fa;
  border: 1px solid #e3e7ea;
  border-radius: 10px;
  padding: 10px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='chat-hero'>🤖 Assistant Audit Flash</div>", unsafe_allow_html=True)

    with st.container(border=False):
        st.markdown("<div class='chat-card'>", unsafe_allow_html=True)

        user_question = st.text_area(
            "💬 Posez votre question ici :",
            key="chatbot_input",
            placeholder="Ex : C'est quoi un VFD ? Comment calculer le ROI ?",
            height=90
        )

        col_send, col_lang = st.columns([1, 1])
        with col_send:
            envoyer = st.button("📤 Envoyer", key="chatbot_button")
        with col_lang:
            st.caption("Langue : " + ("Français" if langue == "Français" else "English"))

        if envoyer:
            if user_question.strip():
                with st.spinner("💬 L'assistant réfléchit..."):
                    reponse = repondre_a_question(
                        user_question,
                        langue="en" if langue == "English" else "fr"
                    )

                if reponse.startswith("⚠️"):
                    st.error(reponse)
                else:
                    st.markdown("#### ✅ Réponse")
                    st.markdown(
                        f"<div style='background:#ffffff;padding:10px;border-radius:8px;"
                        f"border:1px solid #e3e7ea;'>🤖 {reponse}</div>",
                        unsafe_allow_html=True
                    )
            else:
                st.warning("❗ Veuillez écrire une question avant d'envoyer.")

        st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# COULEURS ET STYLE PERSONNALISÉ
# ==========================
couleur_primaire = "#cddc39"
couleur_fond = "#f5f5f5"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {couleur_fond};
    }}
    .section-title {{
        background-color: {couleur_primaire};
        color: #37474f;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 24px;
    }}
    div.stButton > button {{
        background-color: {couleur_primaire};
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    div.stButton > button:hover {{
        background-color: #afb42b;
        color: #37474f;
    }}
    </style>
""", unsafe_allow_html=True)

# LOGO
logo_path = "Image/Logo Soteck.jpg"
logo_image = None

try:
    logo_image = logo_path
except:
    logo_image = None

col1, col2 = st.columns([6, 1])
with col1:
    st.markdown(f"""
    <div style='font-size:24px; font-weight:bold; color:#37474f;'>
    📋 Formulaire de prise de besoin - Audit Flash
    </div>
    """, unsafe_allow_html=True)
with col2:
    if logo_image:
        st.image(logo_image, width=350)
    else:
        st.warning("⚠️ Logo non trouvé.")

if langue == "Français":
    st.markdown("""
    **Bienvenue dans notre formulaire interactif de prise de besoin pour l'audit flash énergétique.  
    Veuillez remplir toutes les sections ci-dessous pour que nous puissions préparer votre audit de manière efficace.**

    ---
    🔗 Pour en savoir plus sur notre entreprise et nos services :  
    **[Soteck](https://www.soteck.com/fr)**
    ---
    """)
else:
    st.markdown("""
    **Welcome to our interactive needs assessment form for the energy flash audit.  
    Please fill out all the sections below so that we can efficiently prepare your audit.**

    ---
    🔗 Learn more about our company and services:  
    **[Soteck](https://www.soteck.com/en)**
    ---
    """)

# SOMMAIRE INTERACTIF
if langue == "Français":
    st.markdown("""
    ### 📑 Sommaire :
    - [1. Informations générales](#infos)
    - [2. Personnes contacts](#contacts)
    - [3. Documents à fournir](#docs)
    - [4. Objectifs du client](#objectifs)
    - [5. Liste des équipements](#equipements)
    - [6. Vos priorités stratégiques](#priorites)
    - [7. Services complémentaires](#services)
    - [8. Récapitulatif et génération PDF](#pdf)
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    ### 📑 Summary :
    - [1. General Information](#infos)
    - [2. Contact Persons](#contacts)
    - [3. Documents to Provide](#docs)
    - [4. Client Objectives](#objectifs)
    - [5. List of Equipment](#equipements)
    - [6. Strategic Priorities](#priorites)
    - [7. Additional Services](#services)
    - [8. Summary and PDF Generation](#pdf)
    """, unsafe_allow_html=True)

# ==========================
# 1. INFORMATIONS GÉNÉRALES
# ==========================
translations = {
    "fr": {
        "titre_infos": "📄 1. Informations générales",
        "texte_expander_infos": "Cliquez ici pour remplir cette section",
        "label_client_nom": "Nom du client *",
        "aide_client_nom": "Ex: Soteck Clauger",
        "label_site_nom": "Nom du site du client *",
        "label_adresse": "Adresse",
        "label_ville": "Ville",
        "label_province": "Province",
        "label_code_postal": "Code postal"
    },
    "en": {
        "titre_infos": "📄 1. General Information",
        "texte_expander_infos": "Click here to fill out this section",
        "label_client_nom": "Client name *",
        "aide_client_nom": "E.g., Soteck Clauger",
        "label_site_nom": "Client site name *",
        "label_adresse": "Address",
        "label_ville": "City",
        "label_province": "Province",
        "label_code_postal": "Postal code"
    }
}

st.markdown("<div id='infos'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_infos']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_infos']):
    client_nom = st.text_input(
        translations[lang]['label_client_nom'],
        help=translations[lang]['aide_client_nom'],
        key="client_nom",
        on_change=sauvegarder_auto
    )
    site_nom = st.text_input(
        translations[lang]['label_site_nom'],
        key="site_nom",
        on_change=sauvegarder_auto
    )
    adresse = st.text_input(translations[lang]['label_adresse'], key="adresse", on_change=sauvegarder_auto)
    ville = st.text_input(translations[lang]['label_ville'], key="ville", on_change=sauvegarder_auto)
    province = st.text_input(translations[lang]['label_province'], key="province", on_change=sauvegarder_auto)
    code_postal = st.text_input(translations[lang]['label_code_postal'], key="code_postal", on_change=sauvegarder_auto)

# ==========================
# 2. PERSONNE CONTACT
# ==========================
translations_contacts = {
    "fr": {
        "titre_contacts_remplisseur": "👥 2. Personne contact et remplisseur",
        "texte_expander_contacts_remplisseur": "Cliquez ici pour remplir cette section",
        "sous_titre_ee": "🔌 Efficacité énergétique ",
        "label_contact_ee_nom": "Prénom et Nom (EE)",
        "label_contact_ee_mail": "Courriel (EE)",
        "help_contact_ee_mail": "Format : exemple@domaine.com",
        "label_contact_ee_tel": "Téléphone (EE)",
        "help_contact_ee_tel": "10 chiffres recommandés",
        "label_contact_ee_ext": "Extension (EE)",
        "sous_titre_maint": "🛠️ Maintenance (Externe)",
        "label_contact_maint_nom": "Prénom et Nom (Maintenance)",
        "label_contact_maint_mail": "Courriel (Maintenance)",
        "label_contact_maint_tel": "Téléphone (Maintenance)",
        "label_contact_maint_ext": "Extension (Maintenance)",
        "titre_remplisseur": "👤 Personne ayant rempli ce formulaire",
        "label_rempli_nom": "Nom du remplisseur",
        "label_rempli_date": "Date de remplissage",
        "label_rempli_mail": "Courriel du remplisseur",
        "label_rempli_tel": "Téléphone du remplisseur",
        "label_rempli_ext": "Extension du remplisseur"
    },
    "en": {
        "titre_contacts_remplisseur": "👥 2. Contact Person and Form Filler",
        "texte_expander_contacts_remplisseur": "Click here to fill out this section",
        "sous_titre_ee": "🔌 Energy Efficiency (Soteck)",
        "label_contact_ee_nom": "First and Last Name (EE)",
        "label_contact_ee_mail": "Email (EE)",
        "help_contact_ee_mail": "Format: example@domain.com",
        "label_contact_ee_tel": "Phone (EE)",
        "help_contact_ee_tel": "10 digits recommended",
        "label_contact_ee_ext": "Extension (EE)",
        "sous_titre_maint": "🛠️ Maintenance (External)",
        "label_contact_maint_nom": "First and Last Name (Maintenance)",
        "label_contact_maint_mail": "Email (Maintenance)",
        "label_contact_maint_tel": "Phone (Maintenance)",
        "label_contact_maint_ext": "Extension (Maintenance)",
        "titre_remplisseur": "👤 Person who filled out this form",
        "label_rempli_nom": "Name of the person who filled out the form",
        "label_rempli_date": "Date of completion",
        "label_rempli_mail": "Email of the person who filled out the form",
        "label_rempli_tel": "Phone number of the person who filled out the form",
        "label_rempli_ext": "Extension of the person who filled out the form"
    }
}

st.markdown("<div id='contacts'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='section-title'>
    {translations_contacts[lang]['titre_contacts_remplisseur']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations_contacts[lang]['texte_expander_contacts_remplisseur']):
    st.markdown(f"#### {translations_contacts[lang]['sous_titre_ee']}")
    contact_ee_nom = st.text_input(translations_contacts[lang]['label_contact_ee_nom'], key="contact_ee_nom", on_change=sauvegarder_auto)
    contact_ee_mail = st.text_input(
        translations_contacts[lang]['label_contact_ee_mail'],
        help=translations_contacts[lang]['help_contact_ee_mail'],
        key="contact_ee_mail",
        on_change=sauvegarder_auto
    )
    contact_ee_tel = st.text_input(
        translations_contacts[lang]['label_contact_ee_tel'],
        help=translations_contacts[lang]['help_contact_ee_tel'],
        key="contact_ee_tel",
        on_change=sauvegarder_auto
    )
    contact_ee_ext = st.text_input(translations_contacts[lang]['label_contact_ee_ext'], key="contact_ee_ext", on_change=sauvegarder_auto)

    st.markdown(f"#### {translations_contacts[lang]['sous_titre_maint']}")
    contact_maint_nom = st.text_input(translations_contacts[lang]['label_contact_maint_nom'], key="contact_maint_nom", on_change=sauvegarder_auto)
    contact_maint_mail = st.text_input(translations_contacts[lang]['label_contact_maint_mail'], key="contact_maint_mail", on_change=sauvegarder_auto)
    contact_maint_tel = st.text_input(translations_contacts[lang]['label_contact_maint_tel'], key="contact_maint_tel", on_change=sauvegarder_auto)
    contact_maint_ext = st.text_input(translations_contacts[lang]['label_contact_maint_ext'], key="contact_maint_ext", on_change=sauvegarder_auto)

    st.markdown(f"#### {translations_contacts[lang]['titre_remplisseur']}")
    rempli_nom = st.text_input(translations_contacts[lang]['label_rempli_nom'], key="rempli_nom", on_change=sauvegarder_auto)
    rempli_date = st.date_input(translations_contacts[lang]['label_rempli_date'], value=date.today(), key="rempli_date", on_change=sauvegarder_auto)
    rempli_mail = st.text_input(translations_contacts[lang]['label_rempli_mail'], key="rempli_mail", on_change=sauvegarder_auto)
    rempli_tel = st.text_input(translations_contacts[lang]['label_rempli_tel'], key="rempli_tel", on_change=sauvegarder_auto)
    rempli_ext = st.text_input(translations_contacts[lang]['label_rempli_ext'], key="rempli_ext", on_change=sauvegarder_auto)

# ==========================
# 3. DOCUMENTS À FOURNIR
# ==========================
translations_docs = {
    "fr": {
        "titre_documents": "📑 3. Documents à fournir avant la visite",
        "texte_expander_documents": "Cliquez ici pour remplir cette section",
        "label_facture_elec": "Factures électricité (1 à 3 ans)",
        "label_facture_combustibles": "Factures Gaz / Mazout / Propane / Bois",
        "label_facture_autres": "Autres consommables (azote, eau, CO2, etc.)",
        "label_plans_pid": "Plans d'aménagement du site et P&ID",
        "label_temps_fonctionnement": "Temps de fonctionnement de l'usine (heures/an)",
        "sous_titre_fichiers_televerses": "📂 Fichiers téléversés"
    },
    "en": {
        "titre_documents": "📑 3. Documents to Provide Before the Visit",
        "texte_expander_documents": "Click here to fill out this section",
        "label_facture_elec": "Electricity bills (1 to 3 years)",
        "label_facture_combustibles": "Gas / Fuel Oil / Propane / Wood bills",
        "label_facture_autres": "Other consumables (nitrogen, water, CO2, etc.)",
        "label_plans_pid": "Site layout plans and P&ID",
        "label_temps_fonctionnement": "Plant operating time (hours/year)",
        "sous_titre_fichiers_televerses": "📂 Uploaded Files"
    }
}

st.markdown(f"""
<div class='section-title'>
    {translations_docs[lang]['titre_documents']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations_docs[lang]['texte_expander_documents']):
    facture_elec = st.file_uploader(translations_docs[lang]['label_facture_elec'], type="pdf", accept_multiple_files=True, key="facture_elec_uploader")
    facture_combustibles = st.file_uploader(translations_docs[lang]['label_facture_combustibles'], type="pdf", accept_multiple_files=True, key="facture_combustibles_uploader")
    facture_autres = st.file_uploader(translations_docs[lang]['label_facture_autres'], type="pdf", accept_multiple_files=True, key="facture_autres_uploader")
    plans_pid = st.file_uploader(translations_docs[lang]['label_plans_pid'], type="pdf", accept_multiple_files=True, key="plans_pid_uploader")
    temps_fonctionnement = st.text_input(translations_docs[lang]['label_temps_fonctionnement'], key="temps_fonctionnement", on_change=sauvegarder_auto)

    if facture_elec or facture_combustibles or facture_autres or plans_pid:
        st.markdown(f"### {translations_docs[lang]['sous_titre_fichiers_televerses']}")
        if facture_elec:
            for fichier in facture_elec:
                st.write(f"➡️ {fichier.name}")

st.session_state["facture_elec_files"] = facture_elec or []
st.session_state["facture_combustibles_files"] = facture_combustibles or []
st.session_state["facture_autres_files"] = facture_autres or []
st.session_state["plans_pid_files"] = plans_pid or []

# ==========================
# 4. OBJECTIF CLIENT
# ==========================
translations_obj = {
    "fr": {
        "titre_objectifs": "🎯 4. Objectif client",
        "texte_expander_objectifs": "Cliquez ici pour remplir cette section",
        "label_sauver_ges": "Objectif de réduction de GES (%)",
        "label_economie_energie": "Économie d'énergie",
        "label_gain_productivite": "Productivité accrue",
        "label_roi_vise": "Retour sur investissement visé",
        "label_remplacement_equipement": "Remplacement d'équipement prévu",
        "label_investissement_prevu": "Investissement prévu",
        "label_autres_objectifs": "Autres objectifs"
    },
    "en": {
        "titre_objectifs": "🎯 4. Client Objectives",
        "texte_expander_objectifs": "Click here to fill out this section",
        "label_sauver_ges": "GHG reduction target (%)",
        "label_economie_energie": "Energy savings",
        "label_gain_productivite": "Increased productivity",
        "label_roi_vise": "Target ROI",
        "label_remplacement_equipement": "Planned equipment replacement",
        "label_investissement_prevu": "Planned investment",
        "label_autres_objectifs": "Other objectives"
    }
}

st.markdown("<div id='objectifs'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='section-title'>
    {translations_obj[lang]['titre_objectifs']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations_obj[lang]['texte_expander_objectifs']):
    sauver_ges = st.text_input(translations_obj[lang]['label_sauver_ges'], key="sauver_ges", on_change=sauvegarder_auto)
    economie_energie = st.checkbox(translations_obj[lang]['label_economie_energie'], key="economie_energie", on_change=sauvegarder_auto)
    gain_productivite = st.checkbox(translations_obj[lang]['label_gain_productivite'], key="gain_productivite", on_change=sauvegarder_auto)
    roi_vise = st.text_input(translations_obj[lang]['label_roi_vise'], key="roi_vise", on_change=sauvegarder_auto)
    remplacement_equipement = st.checkbox(translations_obj[lang]['label_remplacement_equipement'], key="remplacement_equipement", on_change=sauvegarder_auto)
    investissement_prevu = st.text_input(translations_obj[lang]['label_investissement_prevu'], key="investissement_prevu", on_change=sauvegarder_auto)
    autres_objectifs = st.text_area(translations_obj[lang]['label_autres_objectifs'], key="autres_objectifs", on_change=sauvegarder_auto)

# ==========================
# 5. LISTE DES ÉQUIPEMENTS
# ==========================
translations_eq = {
    "fr": {
        "titre_equipements": "⚙️ 5. Liste des équipements",
        "texte_expander_equipements": "Cliquez ici pour remplir cette section",
        "sous_titre_chaudieres": "Chaudières",
        "sous_titre_frigo": "Équipements frigorifiques",
        "sous_titre_compresseur": "Compresseur d'air",
        "sous_titre_pompes": "Pompes industrielles",
        "sous_titre_ventilation": "Systèmes de ventilation / HVAC",
        "sous_titre_machines": "Autres machines de production",
        "sous_titre_eclairage": "Systèmes d'éclairage",
        "sous_titre_depoussiereur": "Dépoussiéreur"
    },
    "en": {
        "titre_equipements": "⚙️ 5. Equipment List",
        "texte_expander_equipements": "Click here to fill out this section",
        "sous_titre_chaudieres": "Boilers",
        "sous_titre_frigo": "Refrigeration equipment",
        "sous_titre_compresseur": "Air compressor",
        "sous_titre_pompes": "Industrial pumps",
        "sous_titre_ventilation": "Ventilation / HVAC systems",
        "sous_titre_machines": "Other production machines",
        "sous_titre_eclairage": "Lighting systems",
        "sous_titre_depoussiereur": "Dust collector"
    }
}

st.markdown(f"""
<div class='section-title'>
    {translations_eq[lang]['titre_equipements']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations_eq[lang]['texte_expander_equipements']):
    st.session_state["_EQ"] = translations_eq[lang].copy()
    
    st.markdown(f"#### {translations_eq[lang]['sous_titre_chaudieres']}")
    columns_chaudieres = ["Nom", "Type", "Rendement (%)", "Taille (BHP/BTU)", "Appoint eau", "Micro modulation", "Économiseur"]
    
    # Charger données existantes si disponibles
    default_chaudieres = st.session_state.get("chaudieres", pd.DataFrame(columns=columns_chaudieres))
    if isinstance(default_chaudieres, list):
        default_chaudieres = pd.DataFrame(default_chaudieres)
    
    df_chaudieres = st.data_editor(
        default_chaudieres,
        num_rows="dynamic",
        key="chaudieres"
    )
    
    st.markdown(f"#### {translations_eq[lang]['sous_titre_frigo']}")
    columns_frigo = ["Nom", "Capacité", "Frigorigène"]
    default_frigo = st.session_state.get("frigo", pd.DataFrame(columns=columns_frigo))
    if isinstance(default_frigo, list):
        default_frigo = pd.DataFrame(default_frigo)
    df_frigo = st.data_editor(default_frigo, num_rows="dynamic", key="frigo")
    
    st.markdown(f"#### {translations_eq[lang]['sous_titre_compresseur']}")
    columns_compresseur = ["Nom", "Puissance (HP)", "Variation vitesse"]
    default_comp = st.session_state.get("compresseur", pd.DataFrame(columns=columns_compresseur))
    if isinstance(default_comp, list):
        default_comp = pd.DataFrame(default_comp)
    df_compresseur = st.data_editor(default_comp, num_rows="dynamic", key="compresseur")
    
    st.markdown(f"#### {translations_eq[lang]['sous_titre_depoussiereur']}")
    columns_dep = ["Nom", "Puissance (HP)", "VFD", "Marque"]
    default_dep = st.session_state.get("depoussieur", pd.DataFrame(columns=columns_dep))
    if isinstance(default_dep, list):
        default_dep = pd.DataFrame(default_dep)
    df_dep = st.data_editor(default_dep, num_rows="dynamic", key="depoussieur")
    
    st.markdown(f"#### {translations_eq[lang]['sous_titre_pompes']}")
    columns_pompes = ["Nom", "Type", "Puissance", "Rendement (%)", "VFD"]
    default_pompes = st.session_state.get("pompes", pd.DataFrame(columns=columns_pompes))
    if isinstance(default_pompes, list):
        default_pompes = pd.DataFrame(default_pompes)
    df_pompes = st.data_editor(default_pompes, num_rows="dynamic", key="pompes")
    
    st.markdown(f"#### {translations_eq[lang]['sous_titre_ventilation']}")
    columns_ventilation = ["Nom", "Type", "Puissance (kWh)"]
    default_vent = st.session_state.get("ventilation", pd.DataFrame(columns=columns_ventilation))
    if isinstance(default_vent, list):
        default_vent = pd.DataFrame(default_vent)
    df_ventilation = st.data_editor(default_vent, num_rows="dynamic", key="ventilation")
    
    st.markdown(f"#### {translations_eq[lang]['sous_titre_machines']}")
    columns_machines = ["Nom", "Machine", "Puissance (kW)", "Utilisation (%)", "Rendement (%)", "Source énergie"]
    default_mach = st.session_state.get("machines", pd.DataFrame(columns=columns_machines))
    if isinstance(default_mach, list):
        default_mach = pd.DataFrame(default_mach)
    df_machines = st.data_editor(default_mach, num_rows="dynamic", key="machines")
    
    st.markdown(f"#### {translations_eq[lang]['sous_titre_eclairage']}")
    columns_eclairage = ["Nom", "Type", "Puissance (kW)", "Heures/jour"]
    default_ecl = st.session_state.get("eclairage", pd.DataFrame(columns=columns_eclairage))
    if isinstance(default_ecl, list):
        default_ecl = pd.DataFrame(default_ecl)
    df_eclairage = st.data_editor(default_ecl, num_rows="dynamic", key="eclairage")

    # Sauvegarder après modification d'équipements
    if st.button("💾 Sauvegarder équipements"):
        sauvegarder_auto()
        st.success("✅ Équipements sauvegardés!")

# Helpers pour génération PDF (inchangés)
def _one_line(s: str) -> str:
    return re.sub(r'[\r\n]+', ' ', (s or '').strip())

def _slug(x: str) -> str:
    return re.sub(r'[^A-Za-z0-9_-]+', '_', (x or '').strip())

def _val(x, suffix: str = "") -> str:
    if isinstance(x, (int, float)) and not pd.isna(x):
        return f"{x:g}{suffix}"
    s = (str(x) if x is not None else "").strip()
    return s + suffix if s else "n/d"

def _yn(x) -> str:
    if isinstance(x, bool):
        return "Oui" if x else "Non"
    s = (str(x) if x is not None else "").strip().lower()
    if s in {"oui","yes","y","true","vrai","1"}: return "Oui"
    if s in {"non","no","n","false","faux","0"}: return "Non"
    return "n/d"

def _EQ():
    return st.session_state.get("_EQ", {})

def _df_depuis_editor(key: str) -> pd.DataFrame:
    val = st.session_state.get(key, None)
    if isinstance(val, pd.DataFrame):
        return val.copy()
    if isinstance(val, dict):
        rows = []
        if isinstance(val.get("added_rows"), list):
            rows.extend(val["added_rows"])
        if isinstance(val.get("edited_rows"), dict):
            rows.extend(val["edited_rows"].values())
        return pd.DataFrame(rows)
    if isinstance(val, list) and all(isinstance(x, dict) for x in val):
        return pd.DataFrame(val)
    return pd.DataFrame()

def _chaudieres_detaille() -> list[str]:
    df = _df_depuis_editor("chaudieres")
    if df.empty: return []
    L=[]
    for _, r in df.iterrows():
        nom = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{nom} – Type: {_val(r.get('Type'))} – Rend: {_val(r.get('Rendement (%)'), '%')}")
    return L

def _frigo_detaille() -> list[str]:
    df = _df_depuis_editor("frigo")
    if df.empty: return []
    L=[]
    for _, r in df.iterrows():
        nom = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{nom} – Capacité: {_val(r.get('Capacité'))} – Frigorigène: {_val(r.get('Frigorigène'))}")
    return L

def _compresseurs_detaille() -> list[str]:
    df = _df_depuis_editor("compresseur")
    if df.empty: return []
    L=[]
    for _, r in df.iterrows():
        nom = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{nom} – {_val(r.get('Puissance (HP)'))} HP – VFD: {_yn(r.get('Variation vitesse'))}")
    return L

def _depoussieurs_detaille(lang=None) -> list[str]:
    df = _df_depuis_editor("depoussieur")
    if df.empty: return []
    L=[]
    for _, r in df.iterrows():
        nom = str(r.get("Nom","")).strip()
        if not nom: continue
        hp = _val(r.get("Puissance (HP)"))
        vfd = _yn(r.get("VFD"))
        marque = r.get("Marque", "")
        L.append(f"{nom} – {hp} HP – VFD: {vfd} – {marque}")
    return L

def _pompes_detaille() -> list[str]:
    df = _df_depuis_editor("pompes")
    if df.empty: return []
    L=[]
    for _, r in df.iterrows():
        nom = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{nom} – Type: {_val(r.get('Type'))} – {_val(r.get('Puissance'))} – VFD: {_yn(r.get('VFD'))}")
    return L

def _ventilation_detaille() -> list[str]:
    df = _df_depuis_editor("ventilation")
    if df.empty: return []
    L=[]
    for _, r in df.iterrows():
        nom = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{nom} – Type: {_val(r.get('Type'))} – {_val(r.get('Puissance (kWh)'))}")
    return L

def _machines_detaille() -> list[str]:
    df = _df_depuis_editor("machines")
    if df.empty: return []
    L=[]
    for _, r in df.iterrows():
        nom = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{nom} – {_val(r.get('Puissance (kW)'))} kW – Util: {_val(r.get('Utilisation (%)'), '%')}")
    return L

def _eclairage_detaille() -> list[str]:
    df = _df_depuis_editor("eclairage")
    if df.empty: return []
    L=[]
    for _, r in df.iterrows():
        nom = str(r.get("Nom","")).strip() or "Sans nom"
        L.append(f"{nom} – Type: {_val(r.get('Type'))} – {_val(r.get('Puissance (kW)'))} kW")
    return L

def _safe_details(fn_or_val):
    try:
        if callable(fn_or_val):
            return fn_or_val()
        return fn_or_val
    except TypeError:
        try:
            return fn_or_val(lang)
        except Exception:
            return []

# ==========================
# 6. VOS PRIORITÉS STRATÉGIQUES
# ==========================
translations_prio = {
    "fr": {
        "titre_priorites": "🎯 6. Vos priorités stratégiques",
        "texte_expander_priorites": "Cliquez ici pour remplir cette section",
        "intro_priorites": "Indiquez vos priorités de 0 à 10",
        "label_priorite_energie": "Réduction consommation énergétique",
        "label_priorite_roi": "Retour sur investissement",
        "label_priorite_ges": "Réduction émissions GES",
        "label_priorite_prod": "Productivité et fiabilité",
        "label_priorite_maintenance": "Maintenance et fiabilité"
    },
    "en": {
        "titre_priorites": "🎯 6. Your Strategic Priorities",
        "texte_expander_priorites": "Click here to fill out this section",
        "intro_priorites": "Indicate your priorities from 0 to 10",
        "label_priorite_energie": "Energy consumption reduction",
        "label_priorite_roi": "Return on investment",
        "label_priorite_ges": "GHG emissions reduction",
        "label_priorite_prod": "Productivity and reliability",
        "label_priorite_maintenance": "Maintenance and reliability"
    }
}

st.markdown("<div id='priorites'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='section-title'>
    {translations_prio[lang]['titre_priorites']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations_prio[lang]['texte_expander_priorites']):
    st.markdown(translations_prio[lang]['intro_priorites'])
    
    priorite_energie = st.slider(translations_prio[lang]['label_priorite_energie'], 0, 10, 5, key="priorite_energie", on_change=sauvegarder_auto)
    priorite_roi = st.slider(translations_prio[lang]['label_priorite_roi'], 1, 10, 5, key="priorite_roi", on_change=sauvegarder_auto)
    priorite_ges = st.slider(translations_prio[lang]['label_priorite_ges'], 0, 10, 5, key="priorite_ges", on_change=sauvegarder_auto)
    priorite_prod = st.slider(translations_prio[lang]['label_priorite_prod'], 0, 10, 5, key="priorite_prod", on_change=sauvegarder_auto)
    priorite_maintenance = st.slider(translations_prio[lang]['label_priorite_maintenance'], 0, 10, 5, key="priorite_maintenance", on_change=sauvegarder_auto)

    total_priorites = priorite_energie + priorite_roi + priorite_ges + priorite_prod + priorite_maintenance
    
    if total_priorites > 0:
        poids_energie = priorite_energie / total_priorites
        poids_roi = priorite_roi / total_priorites
        poids_ges = priorite_ges / total_priorites
        poids_prod = priorite_prod / total_priorites
        poids_maintenance = priorite_maintenance / total_priorites
        
        st.session_state["poids_energie"] = poids_energie
        st.session_state["poids_roi"] = poids_roi
        st.session_state["poids_ges"] = poids_ges
        st.session_state["poids_prod"] = poids_prod
        st.session_state["poids_maintenance"] = poids_maintenance

# ==========================
# 7. SERVICES COMPLÉMENTAIRES
# ==========================
translations_serv = {
    "fr": {
        "titre_services": "🛠️ 7. Services complémentaires",
        "texte_expander_services": "Cliquez ici pour remplir cette section",
        "label_controle": "Contrôle et automatisation",
        "label_maintenance": "Maintenance préventive et corrective",
        "label_ventilation": "Ventilation industrielle",
        "label_autres_services": "Autres services"
    },
    "en": {
        "titre_services": "🛠️ 7. Additional Services",
        "texte_expander_services": "Click here to fill out this section",
        "label_controle": "Control and automation",
        "label_maintenance": "Preventive and corrective maintenance",
        "label_ventilation": "Industrial ventilation",
        "label_autres_services": "Other services"
    }
}

st.markdown("<div id='services'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='section-title'>
    {translations_serv[lang]['titre_services']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations_serv[lang]['texte_expander_services']):
    controle = st.checkbox(translations_serv[lang]['label_controle'], key="controle", on_change=sauvegarder_auto)
    maintenance = st.checkbox(translations_serv[lang]['label_maintenance'], key="maintenance", on_change=sauvegarder_auto)
    ventilation = st.checkbox(translations_serv[lang]['label_ventilation'], key="ventilation", on_change=sauvegarder_auto)
    autres_services = st.text_area(translations_serv[lang]['label_autres_services'], key="autres_services", on_change=sauvegarder_auto)

# ==========================
# 8. PDF - Génération
# ==========================
def generer_pdf(**kwargs) -> bytes:
    """Génère le PDF (code inchangé de votre version originale)"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    try:
        pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        FONT_REG, FONT_B = 'DejaVu', 'DejaVu'
    except Exception:
        FONT_REG = FONT_B = 'Arial'
    
    BULLET = "•" if FONT_REG == "DejaVu" else "-"
    
    try:
        pdf.image("Image/Logo Soteck.jpg", x=170, y=10, w=30)
    except Exception:
        pass
    
    pdf.set_font(FONT_B, 'B', 16)
    pdf.cell(0, 10, "Résumé - Audit Flash", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font(FONT_REG, '', 12)
    pdf.cell(0, 8, f"Client : {kwargs.get('client_nom', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Site   : {kwargs.get('site_nom', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Date   : {date.today().strftime('%d/%m/%Y')}", ln=True)
    
    pdf.ln(4)
    pdf.set_font(FONT_B, 'B', 12)
    pdf.cell(0, 8, "Objectifs:", ln=True)
    pdf.set_font(FONT_REG, '', 12)
    pdf.cell(0, 8, f"Réduction GES : {kwargs.get('sauver_ges', 'N/A')}%", ln=True)
    
    out = pdf.output(dest="S")
    pdf_bytes = out if isinstance(out, (bytes, bytearray)) else out.encode("latin-1")
    return pdf_bytes

TXT_PDF = {
    "fr": {
        "titre_pdf": "📝 8. Récapitulatif et génération PDF",
        "btn_generate": "📥 Générer le PDF",
        "btn_download": "📥 Télécharger le PDF",
        "ok_pdf": "✅ PDF généré avec succès !"
    },
    "en": {
        "titre_pdf": "📝 8. Summary and PDF Generation",
        "btn_generate": "📥 Generate PDF",
        "btn_download": "📥 Download PDF",
        "ok_pdf": "✅ PDF successfully generated!"
    }
}[lang]

st.markdown("<div id='pdf'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{TXT_PDF['titre_pdf']}</div>", unsafe_allow_html=True)

if st.button(TXT_PDF["btn_generate"]):
    # Sauvegarder avant de générer
    sauvegarder_auto()
    
    equipements = {
        "Chaudières": _chaudieres_detaille(),
        "Systèmes frigorifiques": _frigo_detaille(),
        "Compresseurs": _compresseurs_detaille(),
        "Pompes": _pompes_detaille(),
        "Ventilation": _ventilation_detaille(),
        "Machines de production": _machines_detaille(),
        "Éclairage": _eclairage_detaille(),
        "Dépoussiéreurs": _depoussieurs_detaille(lang),
    }
    
    priorites = {}
    total = (priorite_energie + priorite_roi + priorite_ges + priorite_prod + priorite_maintenance)
    if total > 0:
        priorites = {
            "Réduction conso énergétique": priorite_energie / total,
            "ROI": priorite_roi / total,
            "Réduction GES": priorite_ges / total,
            "Productivité": priorite_prod / total,
            "Maintenance": priorite_maintenance / total,
        }
    
    pdf_bytes = generer_pdf(
        client_nom=client_nom,
        site_nom=site_nom,
        sauver_ges=sauver_ges,
        economie_energie=economie_energie,
        gain_productivite=gain_productivite,
        roi_vise=roi_vise,
        investissement_prevu=investissement_prevu,
        autres_objectifs=autres_objectifs,
        priorites=priorites,
        equipements=equipements,
    )
    
    st.session_state["pdf_bytes"] = pdf_bytes
    st.success(TXT_PDF["ok_pdf"])

if "pdf_bytes" in st.session_state:
    st.download_button(
        label=TXT_PDF["btn_download"],
        data=st.session_state["pdf_bytes"],
        file_name=f"audit_flash_{_slug(site_nom)}_{_slug(client_nom)}.pdf",
        mime="application/pdf",
    )

# ==========================
# SOUMISSION FINALE
# ==========================
if st.button("📧 Soumettre le formulaire"):
    pdf_bytes = st.session_state.get("pdf_bytes")
    if not pdf_bytes:
        st.error("⚠️ Veuillez d'abord générer le PDF")
    else:
        # Marquer comme soumis dans la DB
        try:
            conn = sqlite3.connect('audit_flash.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("UPDATE formulaires SET statut = 'soumis' WHERE form_id = ?", (form_id,))
            conn.commit()
            conn.close()
        except Exception:
            pass
        
        # Envoyer l'email (code inchangé)
        try:
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587
            EMAIL_SENDER = "elmehdi.bencharif@gmail.com"
            EMAIL_PASSWORD = str(st.secrets["email_password"]).strip()
            EMAIL_DESTINATAIRES = ["mbencharif@soteck.com", "pdelorme@soteck.com"]
            
            msg = EmailMessage()
            msg["Subject"] = f"Audit Flash – {site_nom} – {client_nom}"
            msg["From"] = EMAIL_SENDER
            msg["To"] = ", ".join(EMAIL_DESTINATAIRES)
            msg.set_content(f"Formulaire soumis pour {client_nom} - {site_nom}\n\nForm ID: {form_id}")
            msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", 
                             filename=f"audit_flash_{_slug(site_nom)}.pdf")
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            
            st.success("✅ Formulaire soumis avec succès!")
            
        except Exception as e:
            st.error(f"⛔ Erreur lors de l'envoi : {e}")

# ==========================
# SAUVEGARDE AUTO PÉRIODIQUE
# ==========================
import time
if "last_autosave" not in st.session_state:
    st.session_state["last_autosave"] = time.time()

# Sauvegarder toutes les 30 secondes
if time.time() - st.session_state["last_autosave"] > 30:
    sauvegarder_auto()
    st.session_state["last_autosave"] = time.time()

st.markdown("---")
st.caption(f"🔒 Session sauvegardée | Form ID: {form_id[:8]}... | Dernière sauvegarde: {datetime.now().strftime('%H:%M:%S')}")



