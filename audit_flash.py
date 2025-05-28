import streamlit as st
from datetime import date
from fpdf import FPDF
import io

# Configuration de la page
st.set_page_config(page_title="Formulaire Audit Flash", layout="wide")

# Chemin relatif vers le logo (à placer dans un dossier 'images/')
logo_path = "Image/Logo Soteck.jpg"

# En-tête avec logo à droite
col1, col2 = st.columns([8, 1])
with col1:
    st.markdown("## FORMULAIRE DE PRISE DE BESOIN - AUDIT FLASH")
with col2:
    try:
        st.image(logo_path, width=200)
    except:
        st.warning("Logo non trouvé. Vérifie le chemin ou le dépôt GitHub.")

# Style personnalisé : interface verte
st.markdown("""
    <style>
    .stApp {
        background-color: #e6f4ea;
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
    h1, h2, h3, h4 {
        color: #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# En-tête avec logo à droite — 
# Remplace "logo.png" par le chemin ou url de ton logo
st.markdown(
    """
    <div class="header">
        <h2 class="header-title">FORMULAIRE DE PRISE DE BESOIN - AUDIT FLASH</h2>
        <div class="header-logo">
            <img src="logo.png" alt="Logo" />
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- Informations client ---
st.markdown("### Informations générales")
client_nom = st.text_input("Nom du client portail (exemple : Soteck Clauger)")
site_nom = st.text_input("Nom du site du client")
adresse = st.text_input("Adresse")
ville = st.text_input("Ville")
province = st.text_input("Province")
code_postal = st.text_input("Code postal")

# --- Contact efficacité énergétique ---
st.markdown("### Personne contact - Efficacité énergétique")
contact_ee_nom = st.text_input("Prénom et Nom (EE)")
contact_ee_mail = st.text_input("Courriel (EE)")
contact_ee_tel = st.text_input("Téléphone (EE)")
contact_ee_ext = st.text_input("Extension (EE)")

# --- Contact maintenance ---
st.markdown("### Personne contact - Maintenance")
contact_maint_nom = st.text_input("Prénom et Nom (Maintenance)")
contact_maint_mail = st.text_input("Courriel (Maintenance)")
contact_maint_tel = st.text_input("Téléphone (Maintenance)")
contact_maint_ext = st.text_input("Extension (Maintenance)")

# --- Documents indispensables ---
st.markdown("### Documents à fournir avant la visite")
facture_elec = st.file_uploader("Factures électricité (1 à 3 ans)", type="pdf", accept_multiple_files=True)
facture_combustibles = st.file_uploader("Factures Gaz / Mazout / Propane / Bois", type="pdf", accept_multiple_files=True)
facture_autres = st.file_uploader("Autres consommables (azote, eau, CO2, etc.)", type="pdf", accept_multiple_files=True)
temps_fonctionnement = st.text_input("Temps de fonctionnement de l’usine")

# --- Objectifs du client ---
st.markdown("### Objectifs du client")
sauver_ges = st.text_input("Objectif de réduction de GES (%)")
economie_energie = st.checkbox("Économie d’énergie")
gain_productivite = st.checkbox("Productivité accrue : coûts, temps")
roi_vise = st.text_input("Retour sur investissement visé")
remplacement_equipement = st.checkbox("Remplacement d’équipement prévu")
investissement_prevu = st.text_input("Investissement prévu (montant et date)")
autres_objectifs = st.text_area("Autres objectifs (description)")

# --- Liste des équipements ---
st.markdown("### Équipements en place")

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

# --- Remplisseur du formulaire ---
st.markdown("### Personne ayant rempli ce formulaire")
rempli_nom = st.text_input("Nom du remplisseur")
rempli_date = st.date_input("Date", value=date.today())
rempli_mail = st.text_input("Courriel")
rempli_tel = st.text_input("Téléphone")
rempli_ext = st.text_input("Extension")

# --- Génération du PDF ---
if st.button("Générer le PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Résumé - Audit Flash", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Client: {client_nom}", ln=True)
    pdf.cell(0, 10, f"Site: {site_nom}", ln=True)
    pdf.cell(0, 10, f"Date du formulaire: {rempli_date.strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

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

    # Création du fichier PDF en mémoire
    pdf_buffer = io.BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')  # Génère le PDF sous forme de chaîne
    pdf_buffer.write(pdf_bytes)
    pdf_buffer.seek(0)

    st.download_button(
        label="📥 Télécharger le PDF",
        data=pdf_buffer,
        file_name="audit_flash.pdf",
        mime="application/pdf"
    )

    st.success("✅ PDF généré avec succès !")
