import streamlit as st
from datetime import date
from fpdf import FPDF
import io

# Configuration de la page
st.set_page_config(page_title="Formulaire Audit Flash", layout="wide")

# Couleurs personnalisées inspirées de la charte graphique
couleur_primaire = "#d4e157"  # Lime (comme sur la capture)
couleur_fond_section = "#f9fbe7"  # Vert très pâle pour arrière-plan
couleur_titre = "#37474f"  # Gris anthracite

# Style global
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #f9fbe7; /* Vert pâle agréable */
    }}
    .section-title {{
        background-color: #cddc39;
        color: #37474f;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 20px;
    }}
    div.stButton > button {{
        background-color: #cddc39;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    div.stButton > button:hover {{
        background-color: #afb42b;
        color: #37474f;
    }}
    .stTextInput > div > div > input {{
        background-color: white;
        color: #37474f;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
🔗 Pour en savoir plus sur nous et nos services :  
**[Soteck](https://www.soteck.com/fr)**
---
""")

# Logo et titre
logo_path = "Image/Logo Soteck.jpg"
col1, col2 = st.columns([8, 1])
with col2:
    try:
        st.image(logo_path, width=300)
    except:
        st.warning("⚠️ Logo non trouvé.")

st.markdown(f"<div class='section-title'>📋 Formulaire de prise de besoin - Audit Flash</div>", unsafe_allow_html=True)
st.markdown("""
Bienvenue dans notre formulaire interactif pour la préparation de votre audit flash énergétique.  
Veuillez remplir toutes les sections ci-dessous pour nous permettre de répondre au mieux à vos besoins.
""")

# Sections avec titres en gras et couleur
def section_header(titre):
    st.markdown(f"<div class='section-title'>{titre}</div>", unsafe_allow_html=True)

section_header("📄 Informations générales")
client_nom = st.text_input("Nom du client portail")
site_nom = st.text_input("Nom du site du client")
adresse = st.text_input("Adresse")
ville = st.text_input("Ville")
province = st.text_input("Province")
code_postal = st.text_input("Code postal")

section_header("👤 Personnes contacts")
st.markdown("#### 🔌 Efficacité énergétique")
contact_ee_nom = st.text_input("Prénom et Nom (EE)")
contact_ee_mail = st.text_input("Courriel (EE)")
contact_ee_tel = st.text_input("Téléphone (EE)")
contact_ee_ext = st.text_input("Extension (EE)")

st.markdown("#### 🛠️ Maintenance")
contact_maint_nom = st.text_input("Prénom et Nom (Maintenance)")
contact_maint_mail = st.text_input("Courriel (Maintenance)")
contact_maint_tel = st.text_input("Téléphone (Maintenance)")
contact_maint_ext = st.text_input("Extension (Maintenance)")

section_header("📑 Documents à fournir avant la visite")
facture_elec = st.file_uploader("Factures électricité (1 à 3 ans)", type="pdf", accept_multiple_files=True)
facture_combustibles = st.file_uploader("Factures Gaz / Mazout / Propane / Bois", type="pdf", accept_multiple_files=True)
facture_autres = st.file_uploader("Autres consommables (azote, eau, CO2, etc.)", type="pdf", accept_multiple_files=True)
temps_fonctionnement = st.text_input("Temps de fonctionnement de l’usine (heures/an)")

section_header("🎯 Objectifs du client")
sauver_ges = st.text_input("Objectif de réduction de GES (%)")
economie_energie = st.checkbox("Économie d’énergie")
gain_productivite = st.checkbox("Productivité accrue : coûts, temps")
roi_vise = st.text_input("Retour sur investissement visé")
remplacement_equipement = st.checkbox("Remplacement d’équipement prévu")
investissement_prevu = st.text_input("Investissement prévu (montant et date)")
autres_objectifs = st.text_area("Autres objectifs (description)")

section_header("⚙️ Liste des équipements")
# Chaudières
st.markdown("#### Chaudières")
nb_chaudieres = st.number_input("Nombre de chaudières", min_value=0, step=1)
type_chaudiere = st.text_input("Type de chaudière")
# (autres champs ici...)

section_header("📝 Remplisseur du formulaire")
rempli_nom = st.text_input("Nom du remplisseur")
rempli_date = st.date_input("Date", value=date.today())
rempli_mail = st.text_input("Courriel")
rempli_tel = st.text_input("Téléphone")
rempli_ext = st.text_input("Extension")

# Autres services proposés
section_header("🛠️ Autres services proposés")
st.markdown("Souhaitez-vous être contacté pour d'autres services que nous offrons (ex.: contrôle, maintenance, ventilation) ?")

controle = st.checkbox("Contrôle et automatisation")
maintenance = st.checkbox("Maintenance préventive et corrective")
ventilation = st.checkbox("Ventilation industrielle et gestion de l’air")
autres_services = st.text_area("Autres services souhaités (précisez)")

# Bouton de génération du PDF
if st.button("📥 Générer le PDF"):
    if not client_nom or not site_nom:
        st.error("❌ Veuillez remplir au minimum le nom du client et le site.")
    else:
        pdf = FPDF()
        pdf.add_page()
        # ... le code PDF habituel ...
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Services complémentaires souhaités:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"- Contrôle et automatisation: {'Oui' if controle else 'Non'}", ln=True)
        pdf.cell(0, 10, f"- Maintenance: {'Oui' if maintenance else 'Non'}", ln=True)
        pdf.cell(0, 10, f"- Ventilation: {'Oui' if ventilation else 'Non'}", ln=True)
        pdf.multi_cell(0, 10, f"Autres services souhaités: {autres_services}")
        # ... puis le reste ...

