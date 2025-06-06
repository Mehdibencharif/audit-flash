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

# COULEURS ET STYLE PERSONNALISÉ
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

        
# MESSAGE DE BIENVENUE
st.markdown("""
**Bienvenue dans notre formulaire interactif de prise de besoin pour l'audit flash énergétique.  
Veuillez remplir toutes les sections ci-dessous pour que nous puissions préparer votre audit de manière efficace.**

---
🔗 Pour en savoir plus sur notre entreprise et nos services :  
**[Soteck](https://www.soteck.com/fr)**
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
        "label_client_nom": "Nom du client portail *",
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
        "label_client_nom": "Client portal name *",
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
        "sous_titre_ee": "🔌 Efficacité énergétique (Soteck)",
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
        "sous_titre_frigo": "Équipements frigorifiques",
        "label_nb_frigo": "Nombre de systèmes frigorifiques",
        "label_capacite_frigo": "Capacité frigorifique",
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
        "label_heures_utilisation": "Nombre d’heures d’utilisation par jour"
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
        "sous_titre_frigo": "Refrigeration equipment",
        "label_nb_frigo": "Number of refrigeration systems",
        "label_capacite_frigo": "Refrigeration capacity",
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
        "label_heures_utilisation": "Number of hours of use per day"
    }
}

st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_equipements']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_equipements']):
    # 🔥 Section Chaudières
    st.markdown(f"#### {translations[lang]['sous_titre_chaudieres']}")
    columns_chaudieres = [
        translations[lang]['label_type_chaudiere'],
        translations[lang]['label_rendement_chaudiere'],
        translations[lang]['label_taille_chaudiere'],
        translations[lang]['label_appoint_eau'],
        translations[lang]['label_micro_modulation']
    ]
    df_chaudieres = st.data_editor(
        pd.DataFrame(columns=columns_chaudieres),
        num_rows="dynamic",
        key="chaudieres"
    )
    st.write("Aperçu des données des chaudières :")
    st.dataframe(df_chaudieres)

    # ❄️ Section Équipements frigorifiques
    st.markdown(f"#### {translations[lang]['sous_titre_frigo']}")
    columns_frigo = [
        translations[lang]['label_capacite_frigo']
    ]
    df_frigo = st.data_editor(
        pd.DataFrame(columns=columns_frigo),
        num_rows="dynamic",
        key="frigo"
    )
    st.write("Aperçu des données des équipements frigorifiques :")
    st.dataframe(df_frigo)

    # 💨 Section Compresseur d’air
    st.markdown(f"#### {translations[lang]['sous_titre_compresseur']}")
    columns_compresseur = [
        translations[lang]['label_puissance_comp'],
        translations[lang]['label_variation_vitesse']
    ]
    df_compresseur = st.data_editor(
        pd.DataFrame(columns=columns_compresseur),
        num_rows="dynamic",
        key="compresseur"
    )
    st.write("Aperçu des données des compresseurs d’air :")
    st.dataframe(df_compresseur)

    # 🚰 Section Pompes industrielles
    st.markdown(f"#### {translations[lang]['sous_titre_pompes']}")
    columns_pompes = [
        translations[lang]['label_type_pompe'],
        translations[lang]['label_puissance_pompe'],
        translations[lang]['label_rendement_pompe'],
        translations[lang]['label_vitesse_variable_pompe']
    ]
    df_pompes = st.data_editor(
        pd.DataFrame(columns=columns_pompes),
        num_rows="dynamic",
        key="pompes"
    )
    st.write("Aperçu des données des pompes industrielles :")
    st.dataframe(df_pompes)

    # 🌬️ Section Ventilation
    st.markdown(f"#### {translations[lang]['sous_titre_ventilation']}")
    columns_ventilation = [
        translations[lang]['label_type_ventilation'],
        translations[lang]['label_puissance_ventilation']
    ]
    df_ventilation = st.data_editor(
        pd.DataFrame(columns=columns_ventilation),
        num_rows="dynamic",
        key="ventilation"
    )
    st.write("Aperçu des données des systèmes de ventilation :")
    st.dataframe(df_ventilation)

    # 🛠️ Section Autres machines de production
    st.markdown(f"#### {translations[lang]['sous_titre_machines']}")
    columns_machines = [
        translations[lang]['label_nom_machine'],
        translations[lang]['label_puissance_machine'],
        translations[lang]['label_taux_utilisation'],
        translations[lang]['label_rendement_machine'],
        translations[lang]['label_source_energie_machine']
    ]
    df_machines = st.data_editor(
        pd.DataFrame(columns=columns_machines),
        num_rows="dynamic",
        key="machines"
    )
    st.write("Aperçu des données des autres machines de production :")
    st.dataframe(df_machines)

    # 💡 Section Éclairage
    st.markdown(f"#### {translations[lang]['sous_titre_eclairage']}")
    columns_eclairage = [
        translations[lang]['label_type_eclairage'],
        translations[lang]['label_puissance_totale_eclairage'],
        translations[lang]['label_heures_utilisation']
    ]
    df_eclairage = st.data_editor(
        pd.DataFrame(columns=columns_eclairage),
        num_rows="dynamic",
        key="eclairage"
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
# 8. RÉCAPITULATIF ET GÉNÉRATION PDF
# ==========================
translations = {
    "fr": {
        # ... autres clés ...
        "titre_pdf": "📝 8. Récapitulatif et génération PDF",
        "texte_info_pdf": "ℹ️ Note : Cette version d’essai ne conserve pas vos données après fermeture de la page. Une version finale permettra d’enregistrer et de reprendre vos réponses ultérieurement.",
        "bouton_generer_pdf": "📥 Générer le PDF",
        "msg_erreur_champs": "Veuillez remplir ou corriger les champs suivants :",
        "msg_succes_pdf": "✅ PDF généré avec succès !",
        "bouton_telecharger_pdf": "📥 Télécharger le PDF",
        "label_client_nom": "Nom du client",
        "label_site_nom": "Nom du site",
        "label_contact_ee_mail": "Courriel de contact EE"
    },
    "en": {
        # ... autres clés ...
        "titre_pdf": "📝 8. Summary and PDF Generation",
        "texte_info_pdf": "ℹ️ Note: This trial version does not retain your data after closing the page. A final version will allow you to save and resume your answers later.",
        "bouton_generer_pdf": "📥 Generate PDF",
        "msg_erreur_champs": "Please fill or correct the following fields:",
        "msg_succes_pdf": "✅ PDF successfully generated!",
        "bouton_telecharger_pdf": "📥 Download PDF",
        "label_client_nom": "Client Name",
        "label_site_nom": "Site Name",
        "label_contact_ee_mail": "EE Contact Email"
    }
}


st.info(translations[lang]['texte_info_pdf'])

st.markdown("<div id='pdf'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_pdf']}
</div>
""", unsafe_allow_html=True)

if st.button(translations[lang]['bouton_generer_pdf']):
    erreurs = []
    if not client_nom:
        erreurs.append(translations[lang]['label_client_nom'])
    if not site_nom:
        erreurs.append(translations[lang]['label_site_nom'])
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if contact_ee_mail and not re.match(email_regex, contact_ee_mail):
        erreurs.append(translations[lang]['label_contact_ee_mail'])

    if erreurs:
        st.error(f"{translations[lang]['msg_erreur_champs']} {', '.join(erreurs)}")
    else:
        pdf = FPDF()
        pdf.add_page()
        try:
            pdf.image(logo_path, x=160, y=10, w=30)
        except:
            pass

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Résumé - Audit Flash", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", '', 12)

        pdf.cell(0, 10, f"Client: {client_nom}", ln=True)
        pdf.cell(0, 10, f"Site: {site_nom}", ln=True)
        pdf.cell(0, 10, f"Date: {date.today().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(5)

        # Objectifs du client
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Objectifs du client:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Réduction GES: {sauver_ges}%", ln=True)
        pdf.cell(0, 10, f"Économie énergie: {'Oui' if economie_energie else 'Non'}", ln=True)
        pdf.cell(0, 10, f"Productivité accrue: {'Oui' if gain_productivite else 'Non'}", ln=True)
        pdf.cell(0, 10, f"ROI visé: {roi_vise}", ln=True)
        pdf.cell(0, 10, f"Investissement prévu: {investissement_prevu}", ln=True)
        pdf.multi_cell(0, 10, f"Autres objectifs: {autres_objectifs}")

        # Services complémentaires
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Services complémentaires souhaités:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"- Contrôle et automatisation: {'Oui' if controle else 'Non'}", ln=True)
        pdf.cell(0, 10, f"- Maintenance: {'Oui' if maintenance else 'Non'}", ln=True)
        pdf.cell(0, 10, f"- Ventilation: {'Oui' if ventilation else 'Non'}", ln=True)
        pdf.multi_cell(0, 10, f"Autres services: {autres_services}")

        # Priorités stratégiques
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Priorités stratégiques du client:", ln=True)
        pdf.set_font("Arial", '', 12)
        if total_priorites > 0:
            pdf.cell(0, 10, f"Réduction consommation énergétique : {poids_energie:.0%}", ln=True)
            pdf.cell(0, 10, f"Retour sur investissement : {poids_roi:.0%}", ln=True)
            pdf.cell(0, 10, f"Réduction émissions GES : {poids_ges:.0%}", ln=True)
            pdf.cell(0, 10, f"Productivité et fiabilité : {poids_prod:.0%}", ln=True)
            pdf.cell(0, 10, f"Maintenance et fiabilité : {poids_maintenance:.0%}", ln=True)
        else:
            pdf.cell(0, 10, "Les priorités stratégiques n'ont pas été renseignées.", ln=True)

        pdf_buffer = io.BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_buffer.write(pdf_bytes)
        pdf_buffer.seek(0)

        st.download_button(
            label=translations[lang]['bouton_telecharger_pdf'],
            data=pdf_buffer,
            file_name="audit_flash.pdf",
            mime="application/pdf"
        )
        st.success(translations[lang]['msg_succes_pdf'])

# BONUS : EXPORT EXCEL
# ==========================
translations = {
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

# Vérifie que la langue est définie et existe
if 'lang' not in locals() or lang not in translations:
    lang = "fr"  # Valeur par défaut

# Initialisation de la liste erreurs
erreurs = []

if st.checkbox(translations[lang]['msg_checkbox_excel']):
    data = {
        translations[lang]['label_client_nom']: [client_nom],
        "Site": [site_nom],
        "GES": [sauver_ges],
        "ROI": [roi_vise],
        "Contrôle": ['Oui' if controle else 'Non'],
        "Maintenance": ['Oui' if maintenance else 'Non'],
        "Ventilation": ['Oui' if ventilation else 'Non'],
    }
    df_export = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False)
    excel_buffer.seek(0)
    st.download_button(
        label=translations[lang]['bouton_export_excel'],
        data=excel_buffer,
        file_name="audit_flash.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Ajout d'erreur simulée (juste pour tester la ligne incriminée)
label_client = translations[lang].get('label_client_nom', 'Nom du client')
erreurs.append(label_client)

#========================
# Soumission par courriel
#========================

# Adresse e-mail destinataire fixe
EMAIL_DESTINATAIRE = "mbencharif@soteck.com"

if st.button("Soumettre le formulaire"):
    # Exemple résumé texte
    resume = f"""
    Bonjour,

    Ci-joint le résumé de l'Audit Flash pour le client {client_nom}.

    Informations saisies :
    - Site : {site_nom}
    - Contact : {contact_ee_nom}
    - Email : {contact_ee_mail}
    - Réduction GES : {sauver_ges}%
 
    """

    # Générer le PDF si souhaité
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Résumé Audit Flash - {client_nom}", ln=True, align='C')
    pdf.multi_cell(0, 10, resume)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_filename = f"Resume_AuditFlash_{client_nom}.pdf"

    # Envoyer l'e-mail
    try:
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        EMAIL_SENDER = "elmehdi.bencharif@gmail.com"  # Ton adresse Gmail
        EMAIL_PASSWORD = "ljbirfbvgvbvsfgj"  # Ton mot de passe d'application Gmail

        msg = EmailMessage()
        msg['Subject'] = f"Audit Flash - Client {client_nom}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_DESTINATAIRE
        msg.set_content(resume)

        # Attacher le résumé PDF
        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=pdf_filename)

        # Attacher les fichiers téléversés
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        for file_group in [facture_elec, facture_combustibles, facture_autres, plans_pid]:
            if file_group:
                for file in file_group:
                    file_path = os.path.join(uploads_dir, file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.read())
                    with open(file_path, "rb") as f:
                        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=file.name)

        # Envoi via SMTP Gmail
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        st.success("Formulaire soumis et envoyé par e-mail avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'e-mail : {e}")




