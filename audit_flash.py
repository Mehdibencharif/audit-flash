import streamlit as st
from datetime import date

st.set_page_config(page_title="Formulaire Audit Flash", layout="wide")
st.markdown("## FORMULAIRE DE PRISE DE BESOIN - AUDIT FLASH")

# --- Informations client ---
st.markdown("### Informations générales")
client_nom = st.text_input("Nom du client portail (exemple : Soteck Clauger)", key="client_nom")
site_nom = st.text_input("Nom du site du client (exemple : Soteck Clauger entrepôt)", key="site_nom")
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
temps_fonctionnement = st.text_input("Temps de fonctionnement de l’usine (ex: 24/24h, 5/7j)", key="temps_fonctionnement")

# --- Objectifs du client ---
st.markdown("### Objectifs du client")
sauver_ges = st.text_input("Objectif de réduction de GES (%)", key="ges")
economie_energie = st.checkbox("Effectuer de l’économie d’énergie")
gain_productivite = st.checkbox("Gagner en productivité : coûts, temps")
roi_vise = st.text_input("Retour sur investissement visé (en mois ou %)", key="roi")
remplacement_equipement = st.checkbox("Remplacer un équipement")
investissement_prevu = st.text_input("Investissement prévu ? Date et montant", key="investissement")
autres_objectifs = st.text_area("Autre : décrire", key="autres_objectifs")

# --- Liste des équipements ---
st.markdown("### Liste des équipements en place")
# Chaudières
st.markdown("#### Chaudières")
nb_chaudieres = st.number_input("Nombre", min_value=0, step=1, key="nb_chaudieres")
type_chaudiere = st.text_input("Type (vapeur, eau chaude, huile …)", key="type_chaudiere")
taille_chaudiere = st.text_input("Taille (BHP ou btu …)", key="taille_chaudiere")
combustible_chaudiere = st.text_input("Combustible", key="combustible_chaudiere")
rendement_chaudiere = st.text_input("Rendement (%)", key="rendement_chaudiere")
appoint_eau = st.text_input("Appoint d’eau en volume", key="appoint_eau")

# Froid
st.markdown("#### Équipements frigorifiques")
nb_frigo = st.number_input("Nombre de systèmes", min_value=0, step=1, key="nb_frigo")
capacite_frigo = st.text_input("Capacité par système (Tr, kW…)", key="capacite_frigo")
fluide_frigo = st.text_input("Fluide frigorigène par système", key="fluide_frigo")
temp_froid = st.text_input("Température d’usage froid", key="temp_froid")
condensation = st.text_input("Type de condensation (eau, air…)", key="condensation")

# Air comprimé
st.markdown("#### Compresseur d’air")
puissance_comp = st.text_input("Puissance (HP)", key="puissance_comp")
refroidissement_comp = st.text_input("Type de refroidissement (air, eau)", key="refroidissement_comp")
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
