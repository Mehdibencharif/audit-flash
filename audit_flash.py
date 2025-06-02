import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="Audit Flash - Formulaire de prise de besoin", layout="centered")
st.title("📋 Formulaire de prise de besoin - Audit Flash")

st.markdown("""
Bienvenue dans notre formulaire interactif de prise de besoin pour l'audit flash énergétique.  
Veuillez remplir toutes les sections ci-dessous pour que nous puissions préparer votre audit de manière efficace.
---
🔗 Pour en savoir plus sur notre entreprise et nos services :  
**[Soteck](https://www.soteck.com/fr)**
---
""")

# --- Formulaire comme avant (je simplifie ici pour la place) ---
client_portail = st.text_input("Nom du client portail (exemple : Soteck Clauger)")
site_client = st.text_input("Nom du site du client (exemple : Soteck Clauger entrepôt)")
adresse = st.text_input("Adresse")
ville = st.text_input("Ville")
province = st.text_input("Province")
code_postal = st.text_input("Code postal")
# (et tous les autres champs... à recopier)

# --- Validation et résumé PDF ---
remplisseur_nom = st.text_input("Prénom et Nom de la personne qui a rempli ce formulaire")
remplisseur_date = st.date_input("Date")
remplisseur_email = st.text_input("Courriel")
remplisseur_tel = st.text_input("Téléphone")
remplisseur_poste = st.text_input("Extension")

if st.button("📄 Générer le résumé au format PDF"):
    resume = f"""
Formulaire de prise de besoin - Audit Flash

Informations générales
- Client portail : {client_portail}
- Site client : {site_client}
- Adresse : {adresse}, {ville}, {province}, {code_postal}

Contact Efficacité énergétique
(à compléter)

Contact Maintenance
(à compléter)

Objectifs du client
(à compléter)

Équipements en place
(à compléter)

Résumé rempli par :
- Nom : {remplisseur_nom}
- Date : {remplisseur_date}
- Courriel : {remplisseur_email}
- Téléphone : {remplisseur_tel} poste {remplisseur_poste}
    """

    # Créer le PDF avec FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in resume.split('\n'):
        pdf.multi_cell(0, 10, line)

    # Sauvegarder le PDF dans un buffer mémoire
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    st.success("✅ Résumé généré au format PDF.")
    st.download_button(
        label="📥 Télécharger le résumé PDF",
        data=pdf_buffer,
        file_name=f"resume_audit_flash_{remplisseur_nom.replace(' ', '_') if remplisseur_nom else 'utilisateur'}.pdf",
        mime="application/pdf"
    )
