import streamlit as st
from datetime import date
from fpdf import FPDF
import io
import re
import pandas as pd

# CONFIGURATION GLOBALE
st.set_page_config(page_title="Formulaire Audit Flash", layout="wide")

# COULEURS ET STYLE PERSONNALISÉ
couleur_primaire = "#cddc39"  # Lime doux inspiré de ton branding
couleur_fond = "#f9fbe7"      # Vert très pâle et agréable

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
        font-size: 20px;
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
col1, col2 = st.columns([8, 1])
with col2:
    try:
        st.image(logo_path, width=500)
    except:
        st.warning("⚠️ Logo non trouvé.")

# TITRE PRINCIPAL
st.markdown(f"<div class='section-title'>📋 Formulaire de prise de besoin - Audit Flash</div>", unsafe_allow_html=True)

# MESSAGE DE BIENVENUE
st.markdown("""
Bienvenue dans notre formulaire interactif de prise de besoin pour l'audit flash énergétique.  
Veuillez remplir toutes les sections ci-dessous pour que nous puissions préparer votre audit de manière efficace.

---
🔗 Pour en savoir plus sur nous et nos services visiter notre site :  
**[Soteck](https://www.soteck.com/fr)**
---
""")

# SOMMAIRE INTERACTIF (avec ancres)
st.markdown("""
### 📑 Sommaire :
- [1. Informations générales](#infos)
- [2. Personnes contacts](#contacts)
- [3. Documents à fournir](#docs)
- [4. Objectifs du client](#objectifs)
- [5. Liste des équipements](#equipements)
- [6. Services complémentaires](#services)
- [7. Récapitulatif et génération PDF](#pdf)
""", unsafe_allow_html=True)

# ==========================
# 1. INFORMATIONS GÉNÉRALES
# ==========================
st.markdown("<div id='infos'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📄 1. Informations générales</div>", unsafe_allow_html=True)
client_nom = st.text_input("Nom du client portail *", help="Ex: Soteck Clauger")
site_nom = st.text_input("Nom du site du client *")
adresse = st.text_input("Adresse")
ville = st.text_input("Ville")
province = st.text_input("Province")
code_postal = st.text_input("Code postal")

# ==========================
# 2. PERSONNES CONTACTS
# ==========================
st.markdown("<div id='contacts'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>👤 2. Personnes contacts</div>", unsafe_allow_html=True)
st.markdown("#### 🔌 Efficacité énergétique")
contact_ee_nom = st.text_input("Prénom et Nom (EE)")
contact_ee_mail = st.text_input("Courriel (EE)", help="Format : exemple@domaine.com")
contact_ee_tel = st.text_input("Téléphone (EE)", help="10 chiffres recommandés")
contact_ee_ext = st.text_input("Extension (EE)")

st.markdown("#### 🛠️ Maintenance")
contact_maint_nom = st.text_input("Prénom et Nom (Maintenance)")
contact_maint_mail = st.text_input("Courriel (Maintenance)")
contact_maint_tel = st.text_input("Téléphone (Maintenance)")
contact_maint_ext = st.text_input("Extension (Maintenance)")

# ==========================
# 3. DOCUMENTS À FOURNIR
# ==========================
st.markdown("<div id='docs'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📑 3. Documents à fournir avant la visite</div>", unsafe_allow_html=True)
facture_elec = st.file_uploader("Factures électricité (1 à 3 ans)", type="pdf", accept_multiple_files=True)
facture_combustibles = st.file_uploader("Factures Gaz / Mazout / Propane / Bois", type="pdf", accept_multiple_files=True)
facture_autres = st.file_uploader("Autres consommables (azote, eau, CO2, etc.)", type="pdf", accept_multiple_files=True)
temps_fonctionnement = st.text_input("Temps de fonctionnement de l’usine (heures/an)")

# ==========================
# 4. OBJECTIFS DU CLIENT
# ==========================
st.markdown("<div id='objectifs'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🎯 4. Objectifs du client</div>", unsafe_allow_html=True)
sauver_ges = st.text_input("Objectif de réduction de GES (%)", help="Exemple : 20")
economie_energie = st.checkbox("Économie d’énergie")
gain_productivite = st.checkbox("Productivité accrue : coûts, temps")
roi_vise = st.text_input("Retour sur investissement visé")
remplacement_equipement = st.checkbox("Remplacement d’équipement prévu")
investissement_prevu = st.text_input("Investissement prévu (montant et date)")
autres_objectifs = st.text_area("Autres objectifs (description)")

# ==========================
# 5. LISTE DES ÉQUIPEMENTS
# ==========================
st.markdown("<div id='equipements'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>⚙️ 5. Liste des équipements</div>", unsafe_allow_html=True)
st.markdown("#### Chaudières")
nb_chaudieres = st.number_input("Nombre de chaudières", min_value=0, step=1)
type_chaudiere = st.text_input("Type de chaudière")
rendement_chaudiere = st.text_input("Rendement (%)")

st.markdown("#### Équipements frigorifiques")
nb_frigo = st.number_input("Nombre de systèmes frigorifiques", min_value=0, step=1)
capacite_frigo = st.text_input("Capacité frigorifique")

st.markdown("#### Compresseur d’air")
puissance_comp = st.text_input("Puissance (HP)")
variation_vitesse = st.radio("Variation de vitesse", ["Oui", "Non"])

# ==========================
# 6. SERVICES COMPLÉMENTAIRES
# ==========================
st.markdown("<div id='services'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🛠️ 6. Services complémentaires</div>", unsafe_allow_html=True)
controle = st.checkbox("Contrôle et automatisation")
maintenance = st.checkbox("Maintenance préventive et corrective")
ventilation = st.checkbox("Ventilation industrielle et gestion de l’air")
autres_services = st.text_area("Autres services souhaités (précisez)")

# ==========================
# 7. RÉCAPITULATIF ET GÉNÉRATION PDF
# ==========================
st.markdown("<div id='pdf'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📝 7. Récapitulatif et génération PDF</div>", unsafe_allow_html=True)

if st.button("📥 Générer le PDF"):
    erreurs = []
    if not client_nom:
        erreurs.append("Nom du client portail")
    if not site_nom:
        erreurs.append("Nom du site du client")
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if contact_ee_mail and not re.match(email_regex, contact_ee_mail):
        erreurs.append("Courriel (EE) invalide")

    if erreurs:
        st.error(f"Veuillez remplir ou corriger les champs suivants : {', '.join(erreurs)}")
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

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Objectifs du client:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Réduction GES: {sauver_ges}%", ln=True)
        pdf.cell(0, 10, f"Économie énergie: {'Oui' if economie_energie else 'Non'}", ln=True)
        pdf.cell(0, 10, f"Productivité accrue: {'Oui' if gain_productivite else 'Non'}", ln=True)
        pdf.cell(0, 10, f"ROI visé: {roi_vise}", ln=True)
        pdf.cell(0, 10, f"Investissement prévu: {investissement_prevu}", ln=True)
        pdf.multi_cell(0, 10, f"Autres objectifs: {autres_objectifs}")

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Services complémentaires souhaités:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"- Contrôle et automatisation: {'Oui' if controle else 'Non'}", ln=True)
        pdf.cell(0, 10, f"- Maintenance: {'Oui' if maintenance else 'Non'}", ln=True)
        pdf.cell(0, 10, f"- Ventilation: {'Oui' if ventilation else 'Non'}", ln=True)
        pdf.multi_cell(0, 10, f"Autres services: {autres_services}")

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

# BONUS : EXPORT EXCEL
if st.checkbox("Exporter les données au format Excel"):
    data = {
        "Client": [client_nom],
        "Site": [site_nom],
        "GES": [sauver_ges],
        "ROI": [roi_vise],
        "Contrôle": ['Oui' if controle else 'Non'],
        "Maintenance": ['Oui' if maintenance else 'Non'],
        "Ventilation": ['Oui' if ventilation else 'Non'],
    }
    df = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    st.download_button(
        label="📥 Télécharger Excel",
        data=excel_buffer,
        file_name="audit_flash.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
