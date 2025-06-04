import streamlit as st
from datetime import date
from fpdf import FPDF
import io
import re
import pandas as pd

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
    - [8. Personne ayant rempli le formulaire](#remplisseur)
    - [9. Récapitulatif et génération PDF](#pdf)
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
    - [8. Person Completing the Form](#remplisseur)
    - [9. Summary and PDF Generation](#pdf)
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
        "titre_infos": "📄 1. Informations générales",
        "texte_expander_infos": "Cliquez ici pour remplir cette section",
        # ... (tes clés du bloc 1)
        "titre_contacts": "👤 2. Personne contact",
        "texte_expander_contacts": "Cliquez ici pour remplir cette section",
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
        "label_contact_maint_ext": "Extension (Maintenance)"
    },
    "en": {
        "titre_infos": "📄 1. General Information",
        "texte_expander_infos": "Click here to fill out this section",
        # ... (tes clés du bloc 1)
        "titre_contacts": "👤 2. Contact Person",
        "texte_expander_contacts": "Click here to fill out this section",
        "sous_titre_ee": "🔌 Energy Efficiency ",
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
        "label_contact_maint_ext": "Extension (Maintenance)"
    }
}


st.markdown("<div id='contacts'></div>", unsafe_allow_html=True)  # ancre cliquable
st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_contacts']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_contacts']):
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

    st.markdown(f"#### {translations[lang]['sous_titre_maint']}")
    contact_maint_nom = st.text_input(translations[lang]['label_contact_maint_nom'])
    contact_maint_mail = st.text_input(translations[lang]['label_contact_maint_mail'])
    contact_maint_tel = st.text_input(translations[lang]['label_contact_maint_tel'])
    contact_maint_ext = st.text_input(translations[lang]['label_contact_maint_ext'])


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
st.markdown("<div id='equipements'></div>", unsafe_allow_html=True)  # ancre cliquable
st.markdown(f"""
<div class='section-title'>
    ⚙️ 5. Liste des équipements
</div>
""", unsafe_allow_html=True)

with st.expander("Cliquez ici pour remplir cette section"):
    st.markdown("#### Chaudières")
    nb_chaudieres = st.number_input("Nombre de chaudières", min_value=0, step=1)
    type_chaudiere = st.text_input("Type de chaudière")
    rendement_chaudiere = st.text_input("Rendement chaudière (%)")
    taille_chaudiere = st.text_input("Taille de la chaudière (BHP ou BTU)")
    appoint_eau = st.text_input("Appoint d’eau (volume)")
    micro_modulation = st.radio("Chaudière équipée de micro modulation ?", ["Oui", "Non"])

    st.markdown("#### Équipements frigorifiques")
    nb_frigo = st.number_input("Nombre de systèmes frigorifiques", min_value=0, step=1)
    capacite_frigo = st.text_input("Capacité frigorifique")

    st.markdown("#### Compresseur d’air")
    puissance_comp = st.text_input("Puissance compresseur (HP)")
    variation_vitesse = st.radio("Variation de vitesse compresseur", ["Oui", "Non"])

    st.markdown("#### Pompes industrielles")
    nb_pompes = st.number_input("Nombre de pompes", min_value=0, step=1)
    type_pompe = st.text_input("Type de pompe (centrifuge, volumétrique, etc.)")
    puissance_pompe = st.text_input("Puissance pompe (kW ou HP)")
    rendement_pompe = st.text_input("Rendement pompe (%)")
    vitesse_variable_pompe = st.radio("Variateur de vitesse pompe", ["Oui", "Non"])

    st.markdown("#### Systèmes d’éclairage")
    type_eclairage = st.text_input("Type d’éclairage (LED, fluorescent, etc.)")
    puissance_totale_eclairage = st.text_input("Puissance totale installée (kW)")
    heures_utilisation = st.text_input("Nombre d’heures d’utilisation par jour")

    st.markdown("#### Systèmes de ventilation / HVAC")
    nb_ventilation = st.number_input("Nombre d’unités de ventilation", min_value=0, step=1)
    type_ventilation = st.text_input("Type de ventilation (naturelle, mécanique, etc.)")
    puissance_ventilation = st.text_input("Puissance ventilation (kWh)")

    st.markdown("#### Autres machines de production")
    nom_machine = st.text_input("Nom de la machine")
    puissance_machine = st.text_input("Puissance machine (kW)")
    taux_utilisation = st.text_input("Taux d’utilisation machine (%)")
    rendement_machine = st.text_input("Rendement machine (%)")


# ==========================
# 6. VOS PRIORITÉS STRATÉGIQUES
# ==========================
translations = {
    "fr": {
        # ... (tes autres clés)
        "titre_priorites": "🎯 6. Vos priorités stratégiques",
        "texte_expander_priorites": "Cliquez ici pour remplir cette section",
        "intro_priorites": "Indiquez vos priorités stratégiques en attribuant une note de 0 (pas important) à 10 (très important).",
        "label_priorite_energie": "Réduction de la consommation énergétique",
        "help_priorite_energie": "Économies d’énergie globales pour votre site.",
        "label_priorite_roi": "Retour sur investissement",
        "help_priorite_roi": "Amortissement du projet et gains financiers.",
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
        # ... (tes autres clés)
        "titre_priorites": "🎯 6. Your Strategic Priorities",
        "texte_expander_priorites": "Click here to fill out this section",
        "intro_priorites": "Indicate your strategic priorities by assigning a score from 0 (not important) to 10 (very important).",
        "label_priorite_energie": "Energy consumption reduction",
        "help_priorite_energie": "Overall energy savings for your site.",
        "label_priorite_roi": "Return on investment",
        "help_priorite_roi": "Project payback and financial gains.",
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
        translations[lang]['label_priorite_energie'], 0, 10, 5,
        help=translations[lang]['help_priorite_energie']
    )
    priorite_roi = st.slider(
        translations[lang]['label_priorite_roi'], 0, 10, 5,
        help=translations[lang]['help_priorite_roi']
    )
    priorite_ges = st.slider(
        translations[lang]['label_priorite_ges'], 0, 10, 5,
        help=translations[lang]['help_priorite_ges']
    )
    priorite_prod = st.slider(
        translations[lang]['label_priorite_prod'], 0, 10, 5,
        help=translations[lang]['help_priorite_prod']
    )
    priorite_maintenance = st.slider(
        translations[lang]['label_priorite_maintenance'], 0, 10, 5,
        help=translations[lang]['help_priorite_maintenance']
    )

    total_priorites = (priorite_energie + priorite_roi + priorite_ges + priorite_prod + priorite_maintenance)
    if total_priorites > 0:
        poids_energie = priorite_energie / total_priorites
        poids_roi = priorite_roi / total_priorites
        poids_ges = priorite_ges / total_priorites
        poids_prod = priorite_prod / total_priorites
        poids_maintenance = priorite_maintenance / total_priorites

        st.markdown(translations[lang]['analyse_priorites'])
        st.markdown(f"- {translations[lang]['resultat_priorite_energie']}: **{poids_energie:.0%}**")
        st.markdown(f"- {translations[lang]['resultat_priorite_roi']}: **{poids_roi:.0%}**")
        st.markdown(f"- {translations[lang]['resultat_priorite_ges']}: **{poids_ges:.0%}**")
        st.markdown(f"- {translations[lang]['resultat_priorite_prod']}: **{poids_prod:.0%}**")
        st.markdown(f"- {translations[lang]['resultat_priorite_maintenance']}: **{poids_maintenance:.0%}**")

        import matplotlib.pyplot as plt
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

        col1, col2 = st.columns([2, 5])
        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.barh(labels, values, color=couleur_primaire)
            ax.set_xlabel("Poids (%)", fontsize=8)
            ax.set_xlim(0, 100)
            ax.set_title(translations[lang]['titre_priorites'], fontsize=9)
            ax.tick_params(axis='both', labelsize=7)
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
# 8. PERSONNE AYANT REMPLI LE FORMULAIRE
# ==========================
translations = {
    "fr": {
        # ... autres clés
        "titre_remplisseur": "👤 8. Personne ayant rempli ce formulaire",
        "texte_expander_remplisseur": "Cliquez ici pour remplir cette section",
        "label_rempli_nom": "Nom du remplisseur",
        "label_rempli_date": "Date de remplissage",
        "label_rempli_mail": "Courriel du remplisseur",
        "label_rempli_tel": "Téléphone du remplisseur",
        "label_rempli_ext": "Extension du remplisseur"
    },
    "en": {
        # ... autres clés
        "titre_remplisseur": "👤 8. Form filled by",
        "texte_expander_remplisseur": "Click here to fill out this section",
        "label_rempli_nom": "Name of the person who filled out the form",
        "label_rempli_date": "Date of completion",
        "label_rempli_mail": "Email of the person who filled out the form",
        "label_rempli_tel": "Phone number of the person who filled out the form",
        "label_rempli_ext": "Extension of the person who filled out the form"
    }
}


st.markdown("<div id='remplisseur'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='section-title'>
    {translations[lang]['titre_remplisseur']}
</div>
""", unsafe_allow_html=True)

with st.expander(translations[lang]['texte_expander_remplisseur']):
    rempli_nom = st.text_input(translations[lang]['label_rempli_nom'])
    rempli_date = st.date_input(translations[lang]['label_rempli_date'], value=date.today())
    rempli_mail = st.text_input(translations[lang]['label_rempli_mail'])
    rempli_tel = st.text_input(translations[lang]['label_rempli_tel'])
    rempli_ext = st.text_input(translations[lang]['label_rempli_ext'])

# ==========================
# 9. RÉCAPITULATIF ET GÉNÉRATION PDF
# ==========================
translations = {
    "fr": {
        # ... autres clés
        "titre_pdf": "📝 9. Récapitulatif et génération PDF",
        "texte_info_pdf": "ℹ️ Note : Cette version d’essai ne conserve pas vos données après fermeture de la page. Une version finale permettra d’enregistrer et de reprendre vos réponses ultérieurement.",
        "bouton_generer_pdf": "📥 Générer le PDF",
        "msg_erreur_champs": "Veuillez remplir ou corriger les champs suivants :",
        "msg_succes_pdf": "✅ PDF généré avec succès !",
        "bouton_telecharger_pdf": "📥 Télécharger le PDF"
    },
    "en": {
        # ... autres clés
        "titre_pdf": "📝 9. Summary and PDF Generation",
        "texte_info_pdf": "ℹ️ Note: This trial version does not retain your data after closing the page. A final version will allow you to save and resume your answers later.",
        "bouton_generer_pdf": "📥 Generate PDF",
        "msg_erreur_champs": "Please fill or correct the following fields:",
        "msg_succes_pdf": "✅ PDF successfully generated!",
        "bouton_telecharger_pdf": "📥 Download PDF"
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
translations = {
    "fr": {
        # ... autres clés
        "bouton_export_excel": "📥 Télécharger Excel",
        "msg_checkbox_excel": "Exporter les données au format Excel"
    },
    "en": {
        # ... autres clés
        "bouton_export_excel": "📥 Download Excel",
        "msg_checkbox_excel": "Export data to Excel format"
    }
}

if st.checkbox(translations[lang]['msg_checkbox_excel']):
    data = {
        "Client": [client_nom],
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
