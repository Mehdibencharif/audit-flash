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
import openai

# ✅ Import du chatbot
from chatbot import repondre_a_question

# CONFIGURATION GLOBALE
st.set_page_config(page_title="Formulaire Audit Flash", layout="wide")

# ==========================
# Choix de la langue
# ==========================
langue = st.radio(
    "Langue / Language",
    ("Français", "English"),
    horizontal=True
)

# Dictionnaire de traduction global
translations = {
    "fr": {
        "titre_infos": "📄 1. Informations générales",
        "texte_expander": "Cliquez ici pour remplir cette section",
        # Ajoute les autres clés ici au fur et à mesure
    },
    "en": {
        "titre_infos": "📄 1. General Information",
        "texte_expander": "Click here to fill out this section",
        # Ajoute les autres clés ici au fur et à mesure
    }
}

# Sélection de la langue
lang = "fr" if langue == "Français" else "en"

# ================================
# Assistant IA gratuit via Groq
# ================================
import os
import requests

def _get_groq_key() -> str | None:
    """Récupère la clé GROQ_API_KEY depuis l'environnement ou st.secrets,
    en tolérant GROQ_APIKEY et en nettoyant les guillemets/espaces."""
    key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_APIKEY")
    try:
        import streamlit as st
        key = key or st.secrets.get("GROQ_API_KEY") or st.secrets.get("GROQ_APIKEY")
    except Exception:
        pass
    if not key:
        return None
    # Nettoyage simple (au cas où la clé aurait été collée avec des guillemets)
    return str(key).strip().strip('"').strip("'")

def repondre_a_question(question: str, langue: str = "fr") -> str:
    """
    Répond via l'API gratuite Groq (modèle Llama 3.1 8B Instant).
    Remplace totalement l'usage d'OpenAI.
    """
    q = (question or "").strip()
    if not q:
        return "⚠️ Aucune question fournie."

    api_key = _get_groq_key()
    if not api_key:
        return ("⚠️ Clé GROQ_API_KEY manquante. Ajoute-la dans Settings → Secrets "
                "ou comme variable d’environnement.")

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
            # Renvoyer une erreur lisible
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
# Interface Streamlit (UI Chatbot) Sidebar mise en valeur
# ================================
st.markdown("""
<style>
/* élargit la barre latérale */
section[data-testid="stSidebar"] { 
  width: 420px !important; 
}
@media (max-width: 1200px){
  section[data-testid="stSidebar"] { width: 360px !important; }
}
/* bandeau titre dans la sidebar */
.chat-hero {
  background: #cddc39;            /* ta couleur primaire */
  color: #37474f;
  padding: 12px 14px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 18px;
  margin-bottom: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}
/* carte contenant question/réponse */
.chat-card {
  background: #f6f8fa;
  border: 1px solid #e3e7ea;
  border-radius: 10px;
  padding: 10px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    # Bandeau très visible
    st.markdown("<div class='chat-hero'>🤖 Assistant Audit Flash</div>", unsafe_allow_html=True)

    # Carte du chatbot
    with st.container(border=False):
        st.markdown("<div class='chat-card'>", unsafe_allow_html=True)

        user_question = st.text_area(
            "💬 Posez votre question ici :",
            key="chatbot_input",
            placeholder="Ex : C’est quoi un VFD ? Comment calculer le ROI ?",
            height=90
        )

        col_send, col_lang = st.columns([1, 1])
        with col_send:
            envoyer = st.button("📤 Envoyer", key="chatbot_button")
        with col_lang:
            st.caption("Langue : " + ("Français" if langue == "Français" else "English"))

        if envoyer:
            if user_question.strip():
                with st.spinner("💬 L’assistant réfléchit..."):
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
                st.warning("❗ Veuillez écrire une question avant d’envoyer.")

        st.markdown("</div>", unsafe_allow_html=True)  # /chat-card
# ==========================
# COULEURS ET STYLE PERSONNALISÉ
# ==========================
couleur_primaire = "#cddc39"  # Lime doux inspiré de ton branding
couleur_fond = "#f5f5f5"      # Gris clair plus doux et agréable

# Injection CSS
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
    logo_image = logo_path  # on prépare le chemin
except:
    logo_image = None

# LOGO + TITRE alignés
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

        
# MESSAGE DE BIENVENUE (multilingue)
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

# SOMMAIRE INTERACTIF (avec ancres)
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


st.markdown("<div id='infos'></div>", unsafe_allow_html=True)  # ancre cliquable
st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_infos']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_infos']):
    client_nom = st.text_input(
        translations[lang]['label_client_nom'], 
        help=translations[lang]['aide_client_nom']
    )
    site_nom = st.text_input(translations[lang]['label_site_nom'])
    adresse = st.text_input(translations[lang]['label_adresse'])
    ville = st.text_input(translations[lang]['label_ville'])
    province = st.text_input(translations[lang]['label_province'])
    code_postal = st.text_input(translations[lang]['label_code_postal'])

# ==========================
# 2. PERSONNE CONTACT
# ==========================
translations = {
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

st.markdown("<div id='contacts_remplisseur'></div>", unsafe_allow_html=True)  # ancre cliquable
st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_contacts_remplisseur']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_contacts_remplisseur']):
    # Sous-titre efficacité énergétique
    st.markdown(f"#### {translations[lang]['sous_titre_ee']}")
    contact_ee_nom = st.text_input(translations[lang]['label_contact_ee_nom'])
    contact_ee_mail = st.text_input(
        translations[lang]['label_contact_ee_mail'],
        help=translations[lang]['help_contact_ee_mail']
    )
    contact_ee_tel = st.text_input(
        translations[lang]['label_contact_ee_tel'],
        help=translations[lang]['help_contact_ee_tel']
    )
    contact_ee_ext = st.text_input(translations[lang]['label_contact_ee_ext'])

    # Sous-titre maintenance
    st.markdown(f"#### {translations[lang]['sous_titre_maint']}")
    contact_maint_nom = st.text_input(translations[lang]['label_contact_maint_nom'])
    contact_maint_mail = st.text_input(translations[lang]['label_contact_maint_mail'])
    contact_maint_tel = st.text_input(translations[lang]['label_contact_maint_tel'])
    contact_maint_ext = st.text_input(translations[lang]['label_contact_maint_ext'])

    # Sous-titre personne ayant rempli le formulaire
    st.markdown(f"#### {translations[lang]['titre_remplisseur']}")
    rempli_nom = st.text_input(translations[lang]['label_rempli_nom'])
    rempli_date = st.date_input(translations[lang]['label_rempli_date'], value=date.today())
    rempli_mail = st.text_input(translations[lang]['label_rempli_mail'])
    rempli_tel = st.text_input(translations[lang]['label_rempli_tel'])
    rempli_ext = st.text_input(translations[lang]['label_rempli_ext'])

# ==========================
# 3. DOCUMENTS À FOURNIR
# ==========================
translations = {
    "fr": {
        # ... (tes clés des autres blocs)
        "titre_documents": "📑 3. Documents à fournir avant la visite",
        "texte_expander_documents": "Cliquez ici pour remplir cette section",
        "label_facture_elec": "Factures électricité (1 à 3 ans)",
        "label_facture_combustibles": "Factures Gaz / Mazout / Propane / Bois",
        "label_facture_autres": "Autres consommables (azote, eau, CO2, etc.)",
        "label_plans_pid": "Plans d’aménagement du site et P&ID (schémas de tuyauterie et d’instrumentation)",
        "label_temps_fonctionnement": "Temps de fonctionnement de l’usine (heures/an)",
        "sous_titre_fichiers_televerses": "📂 Fichiers téléversés",
        "label_facture_elec_uploaded": "**Factures électricité :**",
        "label_facture_combustibles_uploaded": "**Factures Gaz/Mazout/Propane/Bois :**",
        "label_facture_autres_uploaded": "**Autres consommables :**",
        "label_plans_pid_uploaded": "**Plans d’aménagement du site et P&ID :**"
    },
    "en": {
        # ... (tes clés des autres blocs)
        "titre_documents": "📑 3. Documents to Provide Before the Visit",
        "texte_expander_documents": "Click here to fill out this section",
        "label_facture_elec": "Electricity bills (1 to 3 years)",
        "label_facture_combustibles": "Gas / Fuel Oil / Propane / Wood bills",
        "label_facture_autres": "Other consumables (nitrogen, water, CO2, etc.)",
        "label_plans_pid": "Site layout plans and P&ID (piping and instrumentation diagrams)",
        "label_temps_fonctionnement": "Plant operating time (hours/year)",
        "sous_titre_fichiers_televerses": "📂 Uploaded Files",
        "label_facture_elec_uploaded": "**Electricity bills:**",
        "label_facture_combustibles_uploaded": "**Gas/Fuel Oil/Propane/Wood bills:**",
        "label_facture_autres_uploaded": "**Other consumables:**",
        "label_plans_pid_uploaded": "**Site layout plans and P&ID:**"
    }
}

st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_documents']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_documents']):
    facture_elec = st.file_uploader(translations[lang]['label_facture_elec'], type="pdf", accept_multiple_files=True)
    facture_combustibles = st.file_uploader(translations[lang]['label_facture_combustibles'], type="pdf", accept_multiple_files=True)
    facture_autres = st.file_uploader(translations[lang]['label_facture_autres'], type="pdf", accept_multiple_files=True)
    plans_pid = st.file_uploader(translations[lang]['label_plans_pid'], type="pdf", accept_multiple_files=True)
    temps_fonctionnement = st.text_input(translations[lang]['label_temps_fonctionnement'])

    st.markdown(f"### {translations[lang]['sous_titre_fichiers_televerses']}")
    if facture_elec:
        st.markdown(translations[lang]['label_facture_elec_uploaded'])
        for fichier in facture_elec:
            st.write(f"➡️ {fichier.name}")

    if facture_combustibles:
        st.markdown(translations[lang]['label_facture_combustibles_uploaded'])
        for fichier in facture_combustibles:
            st.write(f"➡️ {fichier.name}")

    if facture_autres:
        st.markdown(translations[lang]['label_facture_autres_uploaded'])
        for fichier in facture_autres:
            st.write(f"➡️ {fichier.name}")

    if plans_pid:
        st.markdown(translations[lang]['label_plans_pid_uploaded'])
        for fichier in plans_pid:
            st.write(f"➡️ {fichier.name}")


# ==========================
# 4. OBJECTIF CLIENT
# ==========================
translations = {
    "fr": {
        # ... (tes autres clés)
        "titre_objectifs": "🎯 4. Objectif client",
        "texte_expander_objectifs": "Cliquez ici pour remplir cette section",
        "label_sauver_ges": "Objectif de réduction de GES (%)",
        "help_sauver_ges": "Exemple : 20",
        "label_economie_energie": "Économie d’énergie",
        "label_gain_productivite": "Productivité accrue : coûts, temps",
        "label_roi_vise": "Retour sur investissement visé",
        "label_remplacement_equipement": "Remplacement d’équipement prévu",
        "label_investissement_prevu": "Investissement prévu (montant et date)",
        "label_autres_objectifs": "Autres objectifs (description)"
    },
    "en": {
        # ... (tes autres clés)
        "titre_objectifs": "🎯 4. Client Objectives",
        "texte_expander_objectifs": "Click here to fill out this section",
        "label_sauver_ges": "GHG reduction target (%)",
        "help_sauver_ges": "Example: 20",
        "label_economie_energie": "Energy savings",
        "label_gain_productivite": "Increased productivity: costs, time",
        "label_roi_vise": "Target return on investment",
        "label_remplacement_equipement": "Planned equipment replacement",
        "label_investissement_prevu": "Planned investment (amount and date)",
        "label_autres_objectifs": "Other objectives (description)"
    }
}

st.markdown("<div id='objectifs'></div>", unsafe_allow_html=True)  # ancre cliquable
st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_objectifs']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_objectifs']):
    sauver_ges = st.text_input(
        translations[lang]['label_sauver_ges'], 
        help=translations[lang]['help_sauver_ges']
    )
    economie_energie = st.checkbox(translations[lang]['label_economie_energie'])
    gain_productivite = st.checkbox(translations[lang]['label_gain_productivite'])
    roi_vise = st.text_input(translations[lang]['label_roi_vise'])
    remplacement_equipement = st.checkbox(translations[lang]['label_remplacement_equipement'])
    investissement_prevu = st.text_input(translations[lang]['label_investissement_prevu'])
    autres_objectifs = st.text_area(translations[lang]['label_autres_objectifs'])

# ==========================
# 5. LISTE DES ÉQUIPEMENTS
# ==========================
translations = {
    "fr": {
        # ... autres clés ...
        "titre_equipements": "⚙️ 5. Liste des équipements",
        "texte_expander_equipements": "Cliquez ici pour remplir cette section",
        "sous_titre_chaudieres": "Chaudières",
        "label_nb_chaudieres": "Nombre de chaudières",
        "label_type_chaudiere": "Type de chaudière",
        "label_rendement_chaudiere": "Rendement chaudière (%)",
        "label_taille_chaudiere": "Taille de la chaudière (BHP ou BTU)",
        "label_appoint_eau": "Appoint d’eau (volume)",
        "label_micro_modulation": "Chaudière équipée de micro modulation ?",
        "label_economiseur_chaudiere": "Économiseur installé ?",  # ✅ corrigé
        "sous_titre_frigo": "Équipements frigorifiques",
        "label_nb_frigo": "Nombre de systèmes frigorifiques",
        "label_capacite_frigo": "Capacité frigorifique",
        "label_nom_frigorigenes": "Nom du frigorigène",  # ✅ corrigé
        "sous_titre_compresseur": "Compresseur d’air",
        "label_puissance_comp": "Puissance compresseur (HP)",
        "label_variation_vitesse": "Variation de vitesse compresseur",
        "sous_titre_pompes": "Pompes industrielles",
        "label_nb_pompes": "Nombre de pompes",
        "label_type_pompe": "Type de pompe (centrifuge, volumétrique, etc.)",
        "label_puissance_pompe": "Puissance pompe (kW ou HP)",
        "label_rendement_pompe": "Rendement pompe (%)",
        "label_vitesse_variable_pompe": "Variateur de vitesse pompe",
        "sous_titre_ventilation": "Systèmes de ventilation / HVAC",
        "label_nb_ventilation": "Nombre d’unités de ventilation",
        "label_type_ventilation": "Type de ventilation (naturelle, mécanique, etc.)",
        "label_puissance_ventilation": "Puissance ventilation (kWh)",
        "sous_titre_machines": "Autres machines de production",
        "label_nom_machine": "Nom de la machine",
        "label_puissance_machine": "Puissance machine (kW)",
        "label_taux_utilisation": "Taux d’utilisation machine (%)",
        "label_rendement_machine": "Rendement machine (%)",
        "label_source_energie_machine": "Source d’énergie (fossile, électricité, etc.)",
        "sous_titre_eclairage": "Systèmes d’éclairage",
        "label_type_eclairage": "Type d’éclairage (LED, fluorescent, etc.)",
        "label_puissance_totale_eclairage": "Puissance totale installée (kW)",
        "label_heures_utilisation": "Nombre d’heures d’utilisation par jour",
        "sous_titre_depoussiereur": "Dépoussiéreur",
        "label_puissance_dep_hp": "Puissance (HP)",
        "label_vfd_dep": "Variateur de vitesse (VFD)",
        "label_marque_dep": "Marque",
    },
    "en": {
        # ... autres clés ...
        "titre_equipements": "⚙️ 5. Equipment List",
        "texte_expander_equipements": "Click here to fill out this section",
        "sous_titre_chaudieres": "Boilers",
        "label_nb_chaudieres": "Number of boilers",
        "label_type_chaudiere": "Type of boiler",
        "label_rendement_chaudiere": "Boiler efficiency (%)",
        "label_taille_chaudiere": "Boiler size (BHP or BTU)",
        "label_appoint_eau": "Water make-up (volume)",
        "label_micro_modulation": "Boiler with micro modulation?",
        "label_economiseur_chaudiere": "Economizer installed?",  
        "sous_titre_frigo": "Refrigeration equipment",
        "label_nb_frigo": "Number of refrigeration systems",
        "label_capacite_frigo": "Refrigeration capacity",
        "label_nom_frigorigenes": "Refrigerant name",  
        "sous_titre_compresseur": "Air compressor",
        "label_puissance_comp": "Compressor power (HP)",
        "label_variation_vitesse": "Variable speed compressor",
        "sous_titre_pompes": "Industrial pumps",
        "label_nb_pompes": "Number of pumps",
        "label_type_pompe": "Type of pump (centrifugal, volumetric, etc.)",
        "label_puissance_pompe": "Pump power (kW or HP)",
        "label_rendement_pompe": "Pump efficiency (%)",
        "label_vitesse_variable_pompe": "Pump variable speed drive",
        "sous_titre_ventilation": "Ventilation / HVAC systems",
        "label_nb_ventilation": "Number of ventilation units",
        "label_type_ventilation": "Type of ventilation (natural, mechanical, etc.)",
        "label_puissance_ventilation": "Ventilation power (kWh)",
        "sous_titre_machines": "Other production machines",
        "label_nom_machine": "Machine name",
        "label_puissance_machine": "Machine power (kW)",
        "label_taux_utilisation": "Machine utilization rate (%)",
        "label_rendement_machine": "Machine efficiency (%)",
        "label_source_energie_machine": "Energy source (fossil, electricity, etc.)",
        "sous_titre_eclairage": "Lighting systems",
        "label_type_eclairage": "Type of lighting (LED, fluorescent, etc.)",
        "label_puissance_totale_eclairage": "Total installed power (kW)",
        "label_heures_utilisation": "Number of hours of use per day",
        "sous_titre_depoussiereur": "Dust collector",
        "label_puissance_dep_hp": "Power (HP)",
        "label_vfd_dep": "Variable Frequency Drive (VFD)",
        "label_marque_dep": "Brand",
    }
}

st.markdown(
    f"""
<div class='section-title'>
    {translations[lang]['titre_equipements']}
</div>
""",
    unsafe_allow_html=True,
)

with st.expander(translations[lang]['texte_expander_equipements']):
    # 🔥 Chaudières
    st.markdown(f"#### {translations[lang]['sous_titre_chaudieres']}")
    columns_chaudieres = [
        "Nom",
        translations[lang]['label_type_chaudiere'],
        translations[lang]['label_rendement_chaudiere'],
        translations[lang]['label_taille_chaudiere'],
        translations[lang]['label_appoint_eau'],
        translations[lang]['label_micro_modulation'],
        translations[lang]['label_economiseur_chaudiere'],
    ]
    df_chaudieres = st.data_editor(
        pd.DataFrame(columns=columns_chaudieres),
        num_rows="dynamic",
        key="chaudieres",
    )
    st.write("Aperçu des données des chaudières :")
    st.dataframe(df_chaudieres)

    # ❄️ Équipements frigorifiques
    st.markdown(f"#### {translations[lang]['sous_titre_frigo']}")
    columns_frigo = [
        "Nom",
        translations[lang]['label_capacite_frigo'],
        translations[lang]['label_nom_frigorigenes'],
    ]
    df_frigo = st.data_editor(
        pd.DataFrame(columns=columns_frigo),
        num_rows="dynamic",
        key="frigo",
    )
    st.write("Aperçu des données des équipements frigorifiques :")
    st.dataframe(df_frigo)

    # 💨 Compresseur d’air
    st.markdown(f"#### {translations[lang]['sous_titre_compresseur']}")
    columns_compresseur = [
        "Nom",
        translations[lang]['label_puissance_comp'],
        translations[lang]['label_variation_vitesse'],
    ]
    df_compresseur = st.data_editor(
        pd.DataFrame(columns=columns_compresseur),
        num_rows="dynamic",
        key="compresseur",
    )
    st.write("Aperçu des données des compresseurs d’air :")
    st.dataframe(df_compresseur)

    # 🧹 Dépoussiéreur 
    st.markdown(f"#### {translations[lang]['sous_titre_depoussiereur']}")
    columns_dep = [
        "Nom",
        translations[lang]['label_puissance_dep_hp'],
        translations[lang]['label_vfd_dep'],
        translations[lang]['label_marque_dep'],
    ]
    df_dep = st.data_editor(
        pd.DataFrame(columns=columns_dep),
        num_rows="dynamic",
        key="depoussieur",
        column_config={
            "Nom": st.column_config.TextColumn(),
            translations[lang]['label_puissance_dep_hp']: st.column_config.NumberColumn(step=0.5, min_value=0.0),
            translations[lang]['label_vfd_dep']: st.column_config.CheckboxColumn(default=False),
            translations[lang]['label_marque_dep']: st.column_config.TextColumn(),
        },
    )
    st.write("Aperçu des données des dépoussiéreurs :")
    st.dataframe(df_dep)

    # 🚰 Pompes industrielles
    st.markdown(f"#### {translations[lang]['sous_titre_pompes']}")
    columns_pompes = [
        "Nom",
        translations[lang]['label_type_pompe'],
        translations[lang]['label_puissance_pompe'],
        translations[lang]['label_rendement_pompe'],
        translations[lang]['label_vitesse_variable_pompe'],
    ]
    df_pompes = st.data_editor(
        pd.DataFrame(columns=columns_pompes),
        num_rows="dynamic",
        key="pompes",
    )
    st.write("Aperçu des données des pompes industrielles :")
    st.dataframe(df_pompes)

    # 🌬️ Ventilation / HVAC
    st.markdown(f"#### {translations[lang]['sous_titre_ventilation']}")
    columns_ventilation = [
        "Nom",
        translations[lang]['label_type_ventilation'],
        translations[lang]['label_puissance_ventilation'],
    ]
    df_ventilation = st.data_editor(
        pd.DataFrame(columns=columns_ventilation),
        num_rows="dynamic",
        key="ventilation",
    )
    st.write("Aperçu des données des systèmes de ventilation :")
    st.dataframe(df_ventilation)

    # 🛠️ Autres machines de production
    st.markdown(f"#### {translations[lang]['sous_titre_machines']}")
    columns_machines = [
        "Nom",
        translations[lang]['label_nom_machine'],
        translations[lang]['label_puissance_machine'],
        translations[lang]['label_taux_utilisation'],
        translations[lang]['label_rendement_machine'],
        translations[lang]['label_source_energie_machine'],
    ]
    df_machines = st.data_editor(
        pd.DataFrame(columns=columns_machines),
        num_rows="dynamic",
        key="machines",
    )
    st.write("Aperçu des données des autres machines de production :")
    st.dataframe(df_machines)

    # 💡 Éclairage
    st.markdown(f"#### {translations[lang]['sous_titre_eclairage']}")
    columns_eclairage = [
        "Nom",
        translations[lang]['label_type_eclairage'],
        translations[lang]['label_puissance_totale_eclairage'],
        translations[lang]['label_heures_utilisation'],
    ]
    df_eclairage = st.data_editor(
        pd.DataFrame(columns=columns_eclairage),
        num_rows="dynamic",
        key="eclairage",
    )
    st.write("Aperçu des données des systèmes d’éclairage :")
    st.dataframe(df_eclairage)

# ==========================
# 6. VOS PRIORITÉS STRATÉGIQUES
# ==========================

translations = {
    "fr": {
        "titre_priorites": "🎯 6. Vos priorités stratégiques",
        "texte_expander_priorites": "Cliquez ici pour remplir cette section",
        "intro_priorites": "Indiquez vos priorités stratégiques en attribuant une note de 0 (pas important) à 10 (très important).",
        "label_priorite_energie": "Réduction de la consommation énergétique",
        "help_priorite_energie": "Économies d’énergie globales pour votre site.",
        "label_priorite_roi": "Retour sur investissement",
        "help_priorite_roi": "Nombre d'années pour le retour sur investissement (1 an = retour rapide, 10 ans = retour lent).",
        "label_priorite_ges": "Réduction des émissions de GES",
        "help_priorite_ges": "Conformité réglementaire et impact environnemental.",
        "label_priorite_prod": "Productivité et fiabilité",
        "help_priorite_prod": "Optimisation des performances et disponibilité des équipements.",
        "label_priorite_maintenance": "Maintenance et fiabilité",
        "help_priorite_maintenance": "Facilité d’entretien et durabilité des équipements.",
        "analyse_priorites": "### 📊 Analyse de vos priorités stratégiques",
        "resultat_priorite_energie": "Réduction de la consommation énergétique",
        "resultat_priorite_roi": "Retour sur investissement",
        "resultat_priorite_ges": "Réduction des émissions de GES",
        "resultat_priorite_prod": "Productivité et fiabilité",
        "resultat_priorite_maintenance": "Maintenance et fiabilité",
        "warning_priorites": "⚠️ Veuillez indiquer vos priorités pour générer l'analyse."
    },
    "en": {
        "titre_priorites": "🎯 6. Your Strategic Priorities",
        "texte_expander_priorites": "Click here to fill out this section",
        "intro_priorites": "Indicate your strategic priorities by assigning a score from 0 (not important) to 10 (very important).",
        "label_priorite_energie": "Energy consumption reduction",
        "help_priorite_energie": "Overall energy savings for your site.",
        "label_priorite_roi": "Return on investment",
        "help_priorite_roi": "Number of years for ROI (1 year = fast payback, 10 years = slow payback).",
        "label_priorite_ges": "GHG emissions reduction",
        "help_priorite_ges": "Regulatory compliance and environmental impact.",
        "label_priorite_prod": "Productivity and reliability",
        "help_priorite_prod": "Performance optimization and equipment availability.",
        "label_priorite_maintenance": "Maintenance and reliability",
        "help_priorite_maintenance": "Ease of maintenance and equipment longevity.",
        "analyse_priorites": "### 📊 Analysis of your strategic priorities",
        "resultat_priorite_energie": "Energy consumption reduction",
        "resultat_priorite_roi": "Return on investment",
        "resultat_priorite_ges": "GHG emissions reduction",
        "resultat_priorite_prod": "Productivity and reliability",
        "resultat_priorite_maintenance": "Maintenance and reliability",
        "warning_priorites": "⚠️ Please indicate your priorities to generate the analysis."
    }
}


st.markdown("<div id='priorites'></div>", unsafe_allow_html=True)

st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_priorites']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_priorites']):
    st.markdown(translations[lang]['intro_priorites'])

    priorite_energie = st.slider(
        translations[lang]['label_priorite_energie'],
        0, 10, 5,
        help=translations[lang]['help_priorite_energie']
    )
    priorite_roi = st.slider(
        translations[lang]['label_priorite_roi'],
        1, 10, 5,
        help=translations[lang]['help_priorite_roi']
    )
    priorite_ges = st.slider(
        translations[lang]['label_priorite_ges'],
        0, 10, 5,
        help=translations[lang]['help_priorite_ges']
    )
    priorite_prod = st.slider(
        translations[lang]['label_priorite_prod'],
        0, 10, 5,
        help=translations[lang]['help_priorite_prod']
    )
    priorite_maintenance = st.slider(
        translations[lang]['label_priorite_maintenance'],
        0, 10, 5,
        help=translations[lang]['help_priorite_maintenance']
    )

    total_priorites = (
        priorite_energie +
        priorite_roi +
        priorite_ges +
        priorite_prod +
        priorite_maintenance
    )

    if total_priorites > 0:
        poids_energie = priorite_energie / total_priorites
        poids_roi = priorite_roi / total_priorites
        poids_ges = priorite_ges / total_priorites
        poids_prod = priorite_prod / total_priorites
        poids_maintenance = priorite_maintenance / total_priorites

        st.markdown(translations[lang]['analyse_priorites'])

        col1, col2 = st.columns([1, 2])  # Ajuste les proportions

        with col1:
            st.markdown(f"- {translations[lang]['resultat_priorite_energie']}: **{poids_energie:.0%}**")
            st.markdown(f"- {translations[lang]['resultat_priorite_roi']}: **{poids_roi:.0%}**")
            st.markdown(f"- {translations[lang]['resultat_priorite_ges']}: **{poids_ges:.0%}**")
            st.markdown(f"- {translations[lang]['resultat_priorite_prod']}: **{poids_prod:.0%}**")
            st.markdown(f"- {translations[lang]['resultat_priorite_maintenance']}: **{poids_maintenance:.0%}**")

        with col2:
            labels = [
                translations[lang]['resultat_priorite_energie'],
                translations[lang]['resultat_priorite_roi'],
                translations[lang]['resultat_priorite_ges'],
                translations[lang]['resultat_priorite_prod'],
                translations[lang]['resultat_priorite_maintenance']
            ]
            values = [
                poids_energie * 100,
                poids_roi * 100,
                poids_ges * 100,
                poids_prod * 100,
                poids_maintenance * 100
            ]

            fig, ax = plt.subplots(figsize=(4, 2.5))  # Taille modérée et compacte
            ax.barh(labels, values, color='#4682B4', edgecolor='black', height=0.5)
            ax.set_xlabel("Poids (%)", fontsize=8)
            ax.set_xlim(0, 100)
            ax.tick_params(axis='both', labelsize=7)
            ax.set_title(translations[lang]['titre_priorites'], fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)
    else:
        st.warning(translations[lang]['warning_priorites'])


# ==========================
# 7. SERVICES COMPLÉMENTAIRES
# ==========================
translations = {
    "fr": {
        # ... (tes autres clés)
        "titre_services": "🛠️ 7. Services complémentaires",
        "texte_expander_services": "Cliquez ici pour remplir cette section",
        "label_controle": "Contrôle et automatisation",
        "label_maintenance": "Maintenance préventive et corrective",
        "label_ventilation": "Ventilation industrielle et gestion de l’air",
        "label_autres_services": "Autres services souhaités (précisez)"
    },
    "en": {
        # ... (tes autres clés)
        "titre_services": "🛠️ 7. Additional Services",
        "texte_expander_services": "Click here to fill out this section",
        "label_controle": "Control and automation",
        "label_maintenance": "Preventive and corrective maintenance",
        "label_ventilation": "Industrial ventilation and air management",
        "label_autres_services": "Other desired services (please specify)"
    }
}

st.markdown("<div id='services'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_services']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_services']):
    controle = st.checkbox(translations[lang]['label_controle'])
    maintenance = st.checkbox(translations[lang]['label_maintenance'])
    ventilation = st.checkbox(translations[lang]['label_ventilation'])
    autres_services = st.text_area(translations[lang]['label_autres_services'])


# ==========================
# 8-PDF – génération pro & complète
# ==========================
from fpdf import FPDF
import io, re
from datetime import date
import pandas as pd

TXT = {
    "fr": {
        "titre_pdf": "📝 8. Récapitulatif et génération PDF",
        "info": ("ℹ️ Note : Cette version d’essai ne conserve pas vos données après fermeture de la page. "
                 "La version finale permettra d’enregistrer et de reprendre vos réponses."),
        "btn_generate": "📥 Générer le PDF",
        "btn_download": "📥 Télécharger le PDF",
        "err_missing": "Veuillez remplir ou corriger les champs suivants :",
        "ok_pdf": "✅ PDF généré avec succès !",
        "label_client": "Nom du client",
        "label_site": "Nom du site",
        "label_mail": "Courriel de contact EE",
        "objectifs": "Objectifs du client :",
        "services": "Services complémentaires souhaités :",
        "priorites": "Priorités stratégiques du client :",
        "equipements": "Équipements identifiés lors de l’audit :",
        "aucun_eq": "Aucun équipement saisi",
        "control": "Contrôle et automatisation",
        "maint": "Maintenance",
        "vent": "Ventilation",
    },
    "en": {
        "titre_pdf": "📝 8. Summary and PDF Generation",
        "info": ("ℹ️ Note: This trial version does not retain your data after closing the page. "
                 "A final version will allow you to save and resume later."),
        "btn_generate": "📥 Generate PDF",
        "btn_download": "📥 Download PDF",
        "err_missing": "Please fill or correct the following fields:",
        "ok_pdf": "✅ PDF successfully generated!",
        "label_client": "Client Name",
        "label_site": "Site Name",
        "label_mail": "EE Contact Email",
        "objectifs": "Client objectives:",
        "services": "Additional desired services:",
        "priorites": "Client strategic priorities:",
        "equipements": "Equipment identified during the audit:",
        "aucun_eq": "No equipment provided",
        "control": "Control & automation",
        "maint": "Maintenance",
        "vent": "Ventilation",
    }
}[lang]

st.info(TXT["info"])
st.markdown("<div id='pdf'></div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>{TXT['titre_pdf']}</div>", unsafe_allow_html=True)

# ====== OUTILS : lecture fiable des data_editor ======
def _df_depuis_editor(key: str) -> pd.DataFrame:
    """
    Récupère proprement le contenu d'un st.data_editor(key=...).
    Retourne toujours un DataFrame (éventuellement vide).
    """
    val = st.session_state.get(key, None)

    # Déjà un DataFrame
    if isinstance(val, pd.DataFrame):
        return val.copy()

    # Dict 'edited_rows' / 'added_rows'
    if isinstance(val, dict):
        rows = []
        if isinstance(val.get("added_rows"), list):
            rows.extend(val["added_rows"])
        if isinstance(val.get("edited_rows"), dict):
            rows.extend(val["edited_rows"].values())
        return pd.DataFrame(rows)

    # Liste de dicts
    if isinstance(val, list) and all(isinstance(x, dict) for x in val):
        return pd.DataFrame(val)

    return pd.DataFrame()  # vide par défaut


def _noms_depuis_editor(key: str, col_nom: str = "Nom") -> list[str]:
    """Renvoie la liste des 'Nom' saisis dans l'éditeur `key`."""
    df = _df_depuis_editor(key)
    if df.empty or col_nom not in df.columns:
        return []
    noms = (
        df[col_nom]
        .astype(str)
        .map(lambda s: s.strip())
        .loc[lambda s: s.str.len() > 0]
        .tolist()
    )
    return noms


def _depoussieurs_detaille(lang: str) -> list[str]:
    """
    Construit des lignes détaillées pour les dépoussiéreurs :
    'Nom – 12 HP – VFD: Oui/Non – Marque'
    """
    df = _df_depuis_editor("depoussieur")
    if df.empty:
        return []

    hp_label = translations[lang].get("label_puissance_dep_hp", "Puissance (HP)")
    vfd_label = translations[lang].get("label_vfd_dep", "Variateur de vitesse (VFD)")
    marque_label = translations[lang].get("label_marque_dep", "Marque")

    # colonnes manquantes -> colonnes vides
    for c in ["Nom", hp_label, vfd_label, marque_label]:
        if c not in df.columns:
            df[c] = ""

    lignes = []
    for _, r in df.iterrows():
        nom = str(r["Nom"]).strip()
        if not nom:
            continue
        hp = r[hp_label]
        vfd = r[vfd_label]
        marque = r[marque_label]

        hp_txt = f"{hp} HP" if (pd.notna(hp) and str(hp).strip() != "") else "HP n/d"
        vfd_txt = "Oui" if bool(vfd) else "Non"
        marque_txt = f" – {marque}" if isinstance(marque, str) and marque.strip() else ""
        lignes.append(f"{nom} – {hp_txt} – VFD: {vfd_txt}{marque_txt}")

    return lignes

# ====== Génération du PDF ======
def generer_pdf(
    *,
    client_nom: str,
    site_nom: str,
    sauver_ges: str,
    economie_energie: bool,
    gain_productivite: bool,
    roi_vise: str,
    investissement_prevu: str,
    autres_objectifs: str,
    priorites: dict,
    equipements: dict,
) -> bytes:
    """Construit le PDF et renvoie les bytes."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Polices (fallback sur Arial si non disponibles)
    try:
        pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        FONT_REG, FONT_B = 'DejaVu', 'DejaVu'
    except Exception:
        FONT_REG = FONT_B = 'Arial'

    # Logo optionnel
    try:
        pdf.image("Image/Logo Soteck.jpg", x=170, y=10, w=30)
    except Exception:
        pass

    # Titre + infos
    pdf.set_font(FONT_B, 'B', 16)
    pdf.cell(0, 10, "Résumé - Audit Flash", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font(FONT_REG, '', 12)
    pdf.cell(0, 8, f"Client : {client_nom}", ln=True)
    pdf.cell(0, 8, f"Site   : {site_nom}", ln=True)
    pdf.cell(0, 8, f"Date   : {date.today().strftime('%d/%m/%Y')}", ln=True)

    # Objectifs
    pdf.ln(4)
    pdf.set_font(FONT_B, 'B', 12)
    pdf.cell(0, 8, TXT["objectifs"], ln=True)
    pdf.set_font(FONT_REG, '', 12)
    pdf.cell(0, 8, f"Réduction GES : {sauver_ges}%", ln=True)
    pdf.cell(0, 8, f"Économie d’énergie : {'Oui' if economie_energie else 'Non'}", ln=True)
    pdf.cell(0, 8, f"Productivité accrue : {'Oui' if gain_productivite else 'Non'}", ln=True)
    pdf.cell(0, 8, f"ROI visé : {roi_vise}", ln=True)
    pdf.cell(0, 8, f"Investissement prévu : {investissement_prevu}", ln=True)
    if autres_objectifs:
        pdf.multi_cell(0, 8, f"Autres objectifs : {autres_objectifs}")

    # Services
    pdf.ln(3)
    pdf.set_font(FONT_B, 'B', 12)
    pdf.cell(0, 8, TXT["services"], ln=True)
    pdf.set_font(FONT_REG, '', 12)
    pdf.cell(0, 8, f"- {TXT['control']} : {'Oui' if st.session_state.get('controle') else 'Non'}", ln=True)
    pdf.cell(0, 8, f"- {TXT['maint']}   : {'Oui' if st.session_state.get('maintenance') else 'Non'}", ln=True)
    pdf.cell(0, 8, f"- {TXT['vent']}    : {'Oui' if st.session_state.get('ventilation') else 'Non'}", ln=True)

    # Priorités
    pdf.ln(3)
    pdf.set_font(FONT_B, 'B', 12)
    pdf.cell(0, 8, TXT["priorites"], ln=True)
    pdf.set_font(FONT_REG, '', 12)
    if priorites:
        for k, v in priorites.items():
            try:
                pdf.cell(0, 8, f"{k} : {float(v):.0%}", ln=True)
            except Exception:
                pdf.cell(0, 8, f"{k} : {v}", ln=True)
    else:
        pdf.cell(0, 8, "Non renseignées", ln=True)

    # Équipements
    pdf.ln(3)
    pdf.set_font(FONT_B, 'B', 12)
    pdf.cell(0, 8, TXT["equipements"], ln=True)
    pdf.set_font(FONT_REG, '', 12)
    for bloc, noms in equipements.items():
        if isinstance(noms, list) and len(noms) > 0:
            if bloc == "Dépoussiéreurs":
                pdf.cell(0, 8, f"- {bloc} :", ln=True)
                for item in noms:
                    pdf.multi_cell(0, 8, f"    • {item}")
            else:
                pdf.multi_cell(0, 8, f"- {bloc} : {', '.join(noms)}")
        else:
            pdf.cell(0, 8, f"- {bloc} : {TXT['aucun_eq']}", ln=True)

    # Bandeau bas (optionnel)
    try:
        pdf.image("Image/sous-page.jpg", x=10, y=265, w=190)
    except Exception:
        pass

    # Bytes PDF
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes


# ---- Vérification + Génération ----
st.divider()
email_regex = r"[^@]+@[^@]+\.[^@]+"

if st.button(TXT["btn_generate"]):
    missing = []
    if not client_nom: missing.append(TXT["label_client"])
    if not site_nom:   missing.append(TXT["label_site"])
    if contact_ee_mail and not re.match(email_regex, contact_ee_mail):
        missing.append(TXT["label_mail"])

    if missing:
        st.error(f"{TXT['err_missing']} {', '.join(missing)}")
    else:
        # Listes d’équipements
        equipements = {
            "Chaudières": _noms_depuis_editor("chaudieres"),
            "Systèmes frigorifiques": _noms_depuis_editor("frigo"),
            "Compresseurs": _noms_depuis_editor("compresseur"),
            "Pompes": _noms_depuis_editor("pompes"),
            "Ventilation": _noms_depuis_editor("ventilation"),
            "Machines de production": _noms_depuis_editor("machines"),
            "Éclairage": _noms_depuis_editor("eclairage"),
            "Dépoussiéreurs": _depoussieurs_detaille(lang),
        }

        # Priorités (depuis session_state si dispo)
        poids_energie      = st.session_state.get("poids_energie", 0)
        poids_roi          = st.session_state.get("poids_roi", 0)
        poids_ges          = st.session_state.get("poids_ges", 0)
        poids_prod         = st.session_state.get("poids_prod", st.session_state.get("poids_productivite", 0))
        poids_maintenance  = st.session_state.get("poids_maintenance", 0)

        priorites = {}
        total = (poids_energie + poids_roi + poids_ges + poids_prod + poids_maintenance)
        if total > 0:
            priorites = {
                "Réduction conso énergétique": poids_energie,
                "Retour sur investissement":   poids_roi,
                "Réduction émissions GES":     poids_ges,
                "Productivité & fiabilité":    poids_prod,
                "Maintenance & fiabilité":     poids_maintenance,
            }

        pdf_bytes = generer_pdf(
            client_nom=str(client_nom),
            site_nom=str(site_nom),
            sauver_ges=str(sauver_ges),
            economie_energie=bool(economie_energie),
            gain_productivite=bool(gain_productivite),
            roi_vise=str(roi_vise),
            investissement_prevu=str(investissement_prevu),
            autres_objectifs=str(autres_objectifs),
            priorites=priorites,
            equipements=equipements,
        )

        # On garde en mémoire pour l’étape e-mail
        st.session_state["pdf_bytes"] = pdf_bytes
        st.success(TXT["ok_pdf"])

# ---- Bouton de téléchargement (après génération) ----
if "pdf_bytes" in st.session_state:
    st.download_button(
        label=TXT["btn_download"],
        data=st.session_state["pdf_bytes"],
        file_name=f"audit_flash_{client_nom or 'client'}.pdf",
        mime="application/pdf",
    )

# ===========================
# 🔁 Récupération des données
# ===========================

# Champs saisis (avec valeurs par défaut sûres)
client_nom          = st.session_state.get("client_nom", "").strip()
site_nom            = st.session_state.get("site_nom", "").strip()
contact_ee_nom      = st.session_state.get("contact_ee_nom", "").strip()
contact_ee_mail     = st.session_state.get("contact_ee_mail", "").strip()
sauver_ges          = st.session_state.get("sauver_ges", "")
roi_vise            = st.session_state.get("roi_vise", "")
controle            = bool(st.session_state.get("controle", False))
maintenance         = bool(st.session_state.get("maintenance", False))
ventilation         = bool(st.session_state.get("ventilation", False))

poids_energie       = float(st.session_state.get("poids_energie", 0))
poids_roi           = float(st.session_state.get("poids_roi", 0))
poids_ges           = float(st.session_state.get("poids_ges", 0))
poids_productivite  = float(st.session_state.get("poids_productivite", 0))
poids_maintenance   = float(st.session_state.get("poids_maintenance", 0))

# Sécuriser l’existence des clés d’éditeurs
for key in ["chaudieres", "frigo", "compresseur", "pompes", "ventilation", "machines", "eclairage", "depoussieur"]:
    if key not in st.session_state or st.session_state[key] is None:
        st.session_state[key] = []

# ===========================
# 📤 EXPORT EXCEL
# ===========================

translations_excel = {
    "fr": {
        "label_client_nom": "Nom du client",
        "msg_checkbox_excel": "Exporter les données au format Excel",
        "bouton_export_excel": "📥 Télécharger Excel",
    },
    "en": {
        "label_client_nom": "Client Name",
        "msg_checkbox_excel": "Export data to Excel",
        "bouton_export_excel": "📥 Download Excel",
    }
}

if 'lang' not in locals() or lang not in translations_excel:
    lang = "fr"

if st.checkbox(translations_excel[lang]['msg_checkbox_excel']):
    data = {
        translations_excel[lang]['label_client_nom']: [client_nom or "N/A"],
        "Site": [site_nom or "N/A"],
        "GES (%)": [sauver_ges if sauver_ges != "" else "N/A"],
        "ROI visé": [roi_vise if roi_vise != "" else "N/A"],
        "Contrôle": ['Oui' if controle else 'Non'],
        "Maintenance": ['Oui' if maintenance else 'Non'],
        "Ventilation": ['Oui' if ventilation else 'Non'],
        "Poids énergie": [f"{poids_energie:.0%}"],
        "Poids ROI": [f"{poids_roi:.0%}"],
        "Poids GES": [f"{poids_ges:.0%}"],
        "Poids Productivité": [f"{poids_productivite:.0%}"],
        "Poids Maintenance": [f"{poids_maintenance:.0%}"],
    }

    df_export = pd.DataFrame(data)

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False, sheet_name="Audit Flash")

    excel_buffer.seek(0)
    st.download_button(
        label=translations_excel[lang]['bouton_export_excel'],
        data=excel_buffer,
        file_name="audit_flash.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ===========================
# 📧 Soumission (avec PDF déjà généré)
# ===========================

if st.button("Soumettre le formulaire"):
    # 1) Vérifier que le PDF existe (créé via le bouton 'Générer le PDF')
    pdf_bytes = st.session_state.get("pdf_bytes")
    if not pdf_bytes:
        st.error("⚠️ Veuillez d’abord cliquer sur **« Générer le PDF »** dans la section précédente.")
    else:
        # --- Résumé texte pour l’e-mail ---
        resume = (
            f"Bonjour,\n\n"
            f"Ci-joint le résumé de l'Audit Flash pour le client {client_nom or 'N/A'}.\n\n"
            f"Informations saisies :\n"
            f"- Site : {site_nom or 'N/A'}\n"
            f"- Contact : {contact_ee_nom or 'N/A'}\n"
            f"- Email : {contact_ee_mail or 'N/A'}\n"
            f"- Réduction GES : {sauver_ges if sauver_ges != '' else 'N/A'}%\n"
        )

        # 2) Préparer le fichier PDF joint (nom)
        pdf_filename = f"Resume_AuditFlash_{(client_nom or 'client').replace(' ', '_')}.pdf"

        # 3) (Optionnel) – Attachements des fichiers téléversés si tu les as :
        # Assure-toi que ces variables existent plus haut dans ton script :
        facture_elec = locals().get("facture_elec", [])
        facture_combustibles = locals().get("facture_combustibles", [])
        facture_autres = locals().get("facture_autres", [])
        plans_pid = locals().get("plans_pid", [])

        # 4) ENVOI PAR EMAIL (on peut l’activer plus tard si tu veux)
        try:
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587  # STARTTLS
            EMAIL_SENDER = "elmehdi.bencharif@gmail.com"
            EMAIL_PASSWORD = st.secrets["email_password"]

            # ✅ Destinataires (modifie si besoin)
            EMAIL_DESTINATAIRES = ["mbencharif@soteck.com"]
             #, "pdelorme@soteck.com"                   
            msg = EmailMessage()
            msg['Subject'] = f"Audit Flash - Client {client_nom or 'N/A'}"
            msg['From'] = EMAIL_SENDER
            msg['To'] = ", ".join(EMAIL_DESTINATAIRES)
            msg.set_content(resume)

            # Pièce jointe principale : PDF généré
            msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=pdf_filename)

            # Autres pièces jointes (si présentes)
            uploads_dir = "uploads"
            os.makedirs(uploads_dir, exist_ok=True)
            for file_group in [facture_elec, facture_combustibles, facture_autres, plans_pid]:
                for file in file_group or []:
                    try:
                        file_path = os.path.join(uploads_dir, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.read())
                        with open(file_path, "rb") as f:
                            msg.add_attachment(
                                f.read(),
                                maintype='application',
                                subtype='pdf',
                                filename=file.name
                            )
                    except Exception as e:
                        st.warning(f"⚠️ Fichier {getattr(file, 'name', 'inconnu')} non attaché : {e}")

            # Envoi
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)

            st.success("✅ Formulaire soumis et envoyé par e-mail avec succès !")

        except Exception as e:
            st.error(f"⛔ Erreur lors de l'envoi de l'e-mail : {e}")

