import streamlit as st
from datetime import date
from fpdf import FPDF
import io

# Configuration de la page
st.set_page_config(page_title="Formulaire Audit Flash", layout="wide")

# Accueil
st.markdown("""
# 📋 Formulaire de prise de besoin - Audit Flash

Bienvenue dans notre formulaire interactif pour la préparation de votre audit flash énergétique.  
Veuillez remplir toutes les sections ci-dessous pour nous permettre de répondre au mieux à vos besoins.
---
🔗 Pour en savoir plus : [Soteck](https://www.soteck.com/fr)
""")

# Logo
logo_path = "Image/Logo Soteck.jpg"
col1, col2 = st.columns([8, 1])
with col2:
    try:
        st.image(logo_path, width=100)
    except:
        st.warning("⚠️ Logo non trouvé.")

# Style personnalisé
st.markdown("""
    <style>
    .stApp {
        background-color: #f1f8e9;
    }
    div.stButton > button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #1b5e20;
        color: #a5d6a7;
    }
    h1, h2, h3 {
        color: #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# =====================
# Formulaire structuré
# =====================

with st.expander("📄 Informations générales"):
    client_nom = st.text_input("Nom du client portail", placeholder="Ex: Soteck Clauger")
    site_nom = st.text_input("Nom du site du client")
    adresse = st.text_input("Adresse")
    ville = st.text_input("Ville")
    province = st.text_input("Province")
    code_postal = st.text_input("Code postal")

with st.expander("👤 Personnes contacts"):
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

with st.expander("📑 Documents à fournir avant la visite"):
    facture_elec = st.file_uploader("Factures électricité (1 à 3 ans)", type="pdf", accept_multiple_files=True)
    facture_combustibles = st.file_uploader("Factures Gaz / Mazout / Propane / Bois", type="pdf", accept_multiple_files=True)
    facture_autres = st.file_uploader("Autres consommables (azote, eau, CO2, etc.)", type="pdf", accept_multiple_files=True)
    temps_fonctionnement = st.text_input("Temps de fonctionnement de l’usine (heures/an)")

with st.expander("🎯 Objectifs du client"):
    sauver_ges = st.text_input("Objectif de réduction de GES (%)")
    economie_energie = st.checkbox("Économie d’énergie")
    gain_productivite = st.checkbox("Productivité accrue : coûts, temps")
    roi_vise = st.text_input("Retour sur investissement visé")
    remplacement_equipement = st.checkbox("Remplacement d’équipement prévu")
    investissement_prevu = st.text_input("Investissement prévu (montant et date)")
    autres_objectifs = st.text_area("Autres objectifs (description)")

with st.expander("⚙️ Liste des équipements"):
    st.markdown("#### Chaudières")
    nb_chaudieres = st.number_input("Nombre de chaudières", min_value=0, step=1)
    type_chaudiere = st.text_input("Type de chaudière")
    taille_chaudiere = st.text_input("Taille")
    combustible_chaudiere = st.text_input("Combustible utilisé")
    rendement_chaudiere = st.text_input("Rendement (%)")
    appoint_eau = st.text_input("Appoint d’eau")

    st.markdown("#### Équipements frigorifiques")
    nb_frigo = st.number_input("Nombre de systèmes frigorifiques", min_value=0, step=1)
    capacite_frigo = st.text_input("Capacité frigorifique")
    fluide_frigo = st.text_input("Fluide frigorigène")
    temp_froid = st.text_input("Température d’usage")
    condensation = st.text_input("Type de condensation")

    st.markdown("#### Compresseur d’air")
    puissance_comp = st.text_input("Puissance (HP)")
    refroidissement_comp = st.text_input("Refroidissement")
    variation_vitesse = st.radio("Variation de vitesse", ["Oui", "Non"])

    st.markdown("#### Autres équipements aux combustibles")
    capacite_autres = st.text_input("Capacité")
    autres_infos = st.text_area("Autres informations")

with st.expander("📝 Remplisseur du formulaire"):
    rempli_nom = st.text_input("Nom du remplisseur")
    rempli_date = st.date_input("Date", value=date.today())
    rempli_mail = st.text_input("Courriel")
    rempli_tel = st.text_input("Téléphone")
    rempli_ext = st.text_input("Extension")

# =====================
# Vérification et génération PDF
# =====================

if st.button("📥 Générer le PDF"):
    if not client_nom or not site_nom:
        st.error("❌ Veuillez remplir au minimum le nom du client et le site.")
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
        pdf.cell(0, 10, f"Date du formulaire: {rempli_date.strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(5)

        # Objectifs
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Objectifs du client:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Réduction GES: {sauver_ges}%", ln=True)
        pdf.cell(0, 10, f"Économie énergie: {'Oui' if economie_energie else 'Non'}", ln=True)
        pdf.cell(0, 10, f"Productivité accrue: {'Oui' if gain_productivite else 'Non'}", ln=True)
        pdf.cell(0, 10, f"ROI visé: {roi_vise}", ln=True)
        pdf.cell(0, 10, f"Investissement prévu: {investissement_prevu}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, "Autres objectifs:", ln=True)
        pdf.multi_cell(0, 10, autres_objectifs)

        # Équipements
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Équipements:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Chaudières: {nb_chaudieres} ({type_chaudiere})", ln=True)
        pdf.cell(0, 10, f"Frigorifiques: {nb_frigo} ({capacite_frigo})", ln=True)
        pdf.cell(0, 10, f"Compresseur: {puissance_comp} HP, Vitesse variable: {variation_vitesse}", ln=True)
        pdf.cell(0, 10, f"Autres équipements: {capacite_autres}", ln=True)
        pdf.ln(5)

        # Documents téléchargés
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Documents téléchargés:", ln=True)
        pdf.set_font("Arial", '', 12)

        def list_files(files, titre):
            if files:
                pdf.cell(0, 10, f"{titre}:", ln=True)
                for f in files:
                    pdf.cell(0, 10, f"  - {f.name}", ln=True)
            else:
                pdf.cell(0, 10, f"{titre}: Aucun", ln=True)

        list_files(facture_elec, "Factures électricité")
        list_files(facture_combustibles, "Factures combustibles")
        list_files(facture_autres, "Autres consommables")

        # Création du fichier PDF
        pdf_buffer = io.BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_buffer.write(pdf_bytes)
        pdf_buffer.seek(0)

        st.download_button(
            label="📥 Télécharger le PDF",
            data=pdf_buffer,
            file_name="audit_flash.pdf",
            mime="application/pdf"
        )

        st.success("✅ PDF généré avec succès !")
