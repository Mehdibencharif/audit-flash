import streamlit as st

st.set_page_config(page_title="Audit Flash - Prise de Besoin", layout="centered")

st.title("📝 Formulaire de Prise de Besoin Audit Flash")

# Infos client
nom_client = st.text_input("Nom du client portail (exemple : Soteck Clauger)")
site_client = st.text_input("Nom du site du client (exemple : Soteck Clauger entrepôt)")
adresse = st.text_input("Adresse")
ville = st.text_input("Ville")
province = st.text_input("Province")
code_postal = st.text_input("Code postal")

# Contact efficacité énergétique
st.header("Contact Efficacité énergétique")
nom_contact_ee = st.text_input("Prénom et Nom")
email_contact_ee = st.text_input("Courriel")
tel_contact_ee = st.text_input("Téléphone")
ext_contact_ee = st.text_input("Extension")

# Contact maintenance
st.header("Contact Maintenance")
nom_contact_maint = st.text_input("Prénom et Nom")
email_contact_maint = st.text_input("Courriel")
tel_contact_maint = st.text_input("Téléphone")
ext_contact_maint = st.text_input("Extension")

# Bouton soumission
if st.button("Soumettre le formulaire"):
    st.success(f"Merci {nom_client}, votre formulaire a bien été reçu ! Nous vous recontacterons rapidement.")
