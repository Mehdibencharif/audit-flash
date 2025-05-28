import streamlit as st
from datetime import date
from fpdf import FPDF
import io

st.set_page_config(page_title="Formulaire Audit Flash", layout="wide")
st.markdown("## FORMULAIRE DE PRISE DE BESOIN - AUDIT FLASH")

# --- Informations client ---
st.markdown("### Informations générales")
client_nom = st.text_input("Nom du client portail (exemple : Soteck Clauger)", key="client_nom")
site_nom = st.text_input("Nom du site du client", key="site_nom")
adresse = st.text_input("Adresse", key="adresse")
ville = st.text_input("Ville", key="ville")
province = st.text_input("Province", key="province")
code_postal = st.text_input("Code postal", key="code_postal")

# --- Contact efficacité énergétique ---
st.markdown("### Personne contact - Efficacité énergétique")
contact_ee_nom = st.text_input("Prénom et Nom", key="ee_nom")
contact_ee_mail = st.text_input("Courriel", key="ee_mail")
contact_ee_tel = st.text_input("Téléphone", key="ee_tel")
contact_ee_ext = st.text_input("Extension", key="ee_ext")

# --- Contact maintenance ---
st.markdown("### Personne contact - Maintenance")
contact_maint_nom = st.text_input("Prénom et Nom", key="maint_nom")
contact_maint_mail = st.text_input("Courriel", key="maint_mail")
contact_maint_tel = st.text_input("Téléphone", key="maint_tel")
contact_maint_ext = st.text_input("Extension", key="maint_ext")

# --- Documents indispensables ---
st.markdown("### Indispensable avant la visite")
facture_elec = st.file_uploader("Facture électricité 1 à 3 ans (PDF)", type="pdf", accept_multiple_files=True)
facture_combustibles = st.file_uploader("Facture Gaz / Mazout / Propane / Bois (PDF)", type="pdf", accept_multiple_files=True)
facture_autres = st.file_uploader("Facture autres consommables (azote, eau, CO2 …)", type="pdf", accept_multiple_files=True)
temps_fonctionnement = st.text_input("Temps de fonctionnement de l’usine", key="temps_fonctionnement")

# --- Objectifs du client ---
st.markdown("### Objectifs du client")
sauver_ges = st.text_input("Objectif de réduction de GES (%)", key="ges")
economie_energie = st.checkbox("Effectuer de l’économie d’énergie")
gain_productivite = st.checkbox("Gagner en productivité : coûts, temps")
roi_vise = st.text_input("Retour sur investissement visé", key="roi")
remplacement_equipement = st.checkbox("Remplacer un équipement")
investissement_prevu = st.text_input("Investissement prévu ? Date et montant", key="investissement")
autres_objectifs = st.text_area("Autre : décrire", key="autres_objectifs")

# --- Liste des équipements ---
st.markdown("### Liste des équipements en place")

# Chaudières
st.markdown("#### Chaudières")
nb_chaudieres = st.number_input("Nombre", min_value=0, step=1, key="nb_chaudieres")
type_chaudiere = st.text_input("Type", key="type_chaudiere")
taille_chaudiere = st.text_input("Taille", key="taille_chaudiere")
combustible_chaudiere = st.text_input("Combustible", key="combustible_chaudiere")
rendement_chaudiere = st.text_input("Rendement (%)", key="rendement_chaudiere")
appoint_eau = st.text_input("Appoint d’eau", key="appoint_eau")

# Froid
st.markdown("#### Équipements frigorifiques")
nb_frigo = st.number_input("Nombre de systèmes", min_value=0, step=1, key="nb_frigo")
capacite_frigo = st.text_input("Capacité", key="capacite_frigo")
fluide_frigo = st.text_input("Fluide frigorigène", key="fluide_frigo")
temp_froid = st.text_input("Température d’usage froid", key="temp_froid")
condensation = st.text_input("Type de condensation", key="condensation")

# Air comprimé
st.markdown("#### Compresseur d’air")
puissance_comp = st.text_input("Puissance (HP)", key="puissance_comp")
refroidissement_comp = st.text_input("Type de refroidissement", key="refroidissement_comp")
variation_vitesse = st.radio("Variation de vitesse", ["Oui", "Non"], key="variation_vitesse")

# Autres équipements
st.markdown("#### Autres équipements aux combustibles")
capacite_autres = st.text_input("Capacité", key="capacite_autres")
autres_infos = st.text_area("Autres informations supplémentaires", key="autres_infos")

# --- Remplisseur du formulaire ---
st.markdown("### Personne ayant rempli ce formulaire")
rempli_nom = st.text_input("Prénom et Nom", key="rempli_nom")
rempli_date = st.date_input("Date", value=date.today(), key="rempli_date")
rempli_mail = st.text_input("Courriel", key="rempli_mail")
rempli_tel = st.text_input("Téléphone", key="rempli_tel")
rempli_ext = st.text_input("Extension", key="rempli_ext")

# --- Génération du PDF ---
if st.button("📄 Générer le PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def write_line(label, value):
        if value:
            pdf.multi_cell(0, 10, f"{label}: {value}")

    write_line("Client", client_nom)
    write_line("Site", site_nom)
    write_line("Adresse", adresse)
    write_line("Ville", ville)
    write_line("Province", province)
    write_line("Code postal", code_postal)

    write_line("\nContact EE", f"{contact_ee_nom}, {contact_ee_mail}, {contact_ee_tel} ext {contact_ee_ext}")
    write_line("Contact Maintenance", f"{contact_maint_nom}, {contact_maint_mail}, {contact_maint_tel} ext {contact_maint_ext}")

    write_line("\nTemps de fonctionnement", temps_fonctionnement)
    write_line("Objectif GES", sauver_ges)
    write_line("Économie d'énergie", "Oui" if economie_energie else "Non")
    write_line("Productivité", "Oui" if gain_productivite else "Non")
    write_line("ROI visé", roi_vise)
    write_line("Remplacement équipement", "Oui" if remplacement_equipement else "Non")
    write_line("Investissement prévu", investissement_prevu)
    write_line("Autres objectifs", autres_objectifs)

    write_line("\nCHAUDIÈRES", f"{nb_chaudieres} - {type_chaudiere}, {taille_chaudiere}, {combustible_chaudiere}, {rendement_chaudiere}, {appoint_eau}")
    write_line("FRIGORIFIQUES", f"{nb_frigo} - {capacite_frigo}, {fluide_frigo}, {temp_froid}, {condensation}")
    write_line("AIR COMPRIMÉ", f"{puissance_comp}, {refroidissement_comp}, VSD: {variation_vitesse}")
    write_line("AUTRES", f"{capacite_autres} - {autres_infos}")

    write_line("\nRempli par", f"{rempli_nom}, {rempli_mail}, {rempli_tel} ext {rempli_ext}")
    write_line("Date", str(rempli_date))

    # Création du fichier PDF en mémoire
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    st.success("✅ PDF généré avec succès !")

    st.download_button(
        label="📥 Télécharger le PDF",
        data=pdf_buffer,
        file_name="audit_flash.pdf",
        mime="application/pdf"
    )
