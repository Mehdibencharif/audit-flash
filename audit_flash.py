import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Audit Flash Interactif", layout="centered")
st.title("\U0001F4A1 Audit Flash Énergétique")
st.markdown("""
Bienvenue dans l'outil interactif d'audit flash énergétique. Ce formulaire vous permettra de prioriser vos critères à l'aide de la méthode **TOPSIS**, afin de recevoir un résumé personnalisé.
""")
st.markdown("""
---
🔗 Pour en savoir plus sur notre entreprise et nos services, visitez notre site :  
**[Soteck](https://www.soteck.com/fr)**
---
""")

# Étape 1 : Infos générales
st.header("1. Informations générales")
nom = st.text_input("Nom complet")
entreprise = st.text_input("Nom de l'entreprise")
secteur = st.selectbox("Secteur d'activité", ["Industrie", "Tertiaire", "Agroalimentaire", "Autre"])
objectif = st.multiselect("Quels sont vos objectifs prioritaires ?", ["Réduction de consommation", "Réduction des coûts", "Réduction des GES", "Amélioration du confort", "Réduction de maintenance"])

# Étape 2 : Pondération simplifiée pour TOPSIS
st.header("2. Pondération des critères (TOPSIS simplifié)")
criteria = ["Énergie", "Coûts", "Environnement", "Confort", "Maintenance"]
weights = []

st.markdown("Attribuez un poids (1 à 10) à chaque critère selon son importance pour vous.")
for crit in criteria:
    weight = st.slider(f"Poids pour {crit}", 1, 10, 5, format="%d")
    weights.append(weight)

# Si bouton cliqué
if st.button("Calculer les priorités avec TOPSIS"):
    df_weights = pd.DataFrame({"Critère": criteria, "Poids": weights})
    df_weights["Poids normalisé"] = df_weights["Poids"] / df_weights["Poids"].sum()

    st.success("Voici la pondération normalisée de vos critères :")
    st.dataframe(df_weights)

    fig = px.pie(df_weights, names="Critère", values="Poids normalisé", title="Priorisation des critères")
    st.plotly_chart(fig)

    st.markdown("Un rapport peut être généré selon ces priorités pour vous proposer des actions ciblées dès le premier contact.")

    # Analyse et résumé personnalisé
    st.subheader("Résumé personnalisé des priorités")
    top_criteria = df_weights.sort_values("Poids normalisé", ascending=False).head(3)

    resume = f"""
Bonjour {nom if nom else "utilisateur"}, voici un aperçu de vos priorités (méthode TOPSIS simplifiée) :

1. **{top_criteria.iloc[0]['Critère']}** : Ce critère est prioritaire. Nous vous proposerons des actions ciblées pour l'optimiser en priorité.
2. **{top_criteria.iloc[1]['Critère']}** : Ce critère arrive en deuxième position, et sera intégré dans les recommandations secondaires.
3. **{top_criteria.iloc[2]['Critère']}** : Ce critère complète votre trio de tête et pourra être intégré dans les solutions complémentaires.

Grâce à cette hiérarchisation, un audit ciblé pourra être planifié avec un maximum d'efficacité et de pertinence.
"""
    st.markdown(resume)

    # Section récapitulative dynamique
    st.subheader("📝 Récapitulatif du formulaire")
    st.write(f"**Nom** : {nom}")
    st.write(f"**Entreprise** : {entreprise}")
    st.write(f"**Secteur** : {secteur}")
    st.write(f"**Objectifs sélectionnés** : {', '.join(objectif)}")

    # Export des données
    st.subheader("📊 Télécharger vos priorités et informations")
    data_export = {
        "Nom": [nom],
        "Entreprise": [entreprise],
        "Secteur": [secteur],
        "Objectifs": [', '.join(objectif)]
    }
    for crit, wgt, norm in zip(df_weights["Critère"], df_weights["Poids"], df_weights["Poids normalisé"]):
        data_export[f"{crit} (poids)"] = [wgt]
        data_export[f"{crit} (normalisé)"] = [norm]

    df_export = pd.DataFrame(data_export)
    csv = df_export.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button(
        label="📥 Télécharger le résumé (.csv)",
        data=csv,
        file_name=f"resume_audit_flash_{nom.replace(' ', '_') if nom else 'utilisateur'}.csv",
        mime="text/csv"
    )
