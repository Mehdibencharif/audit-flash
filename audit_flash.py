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
""")


# Étape 1 : Infos générales
st.header("1. Informations générales")
nom = st.text_input("Nom complet")
entreprise = st.text_input("Nom de l'entreprise")
secteur = st.selectbox("Secteur d'activité", ["Industrie", "Tertiaire", "Agroalimentaire", "Autre"])
objectif = st.multiselect("Quels sont vos objectifs prioritaires ?", ["Réduction de consommation", "Réduction des coûts", "Réduction des GES", "Amélioration du confort", "Réduction de maintenance"])

# Étape 2 : Comparaison AHP
st.header("2. Priorisation des critères (AHP simplifié)")
st.markdown("Comparez les critères deux à deux selon leur importance pour vous.")
criteria = ["Énergie", "Coûts", "Environnement", "Confort", "Maintenance"]

pairwise = {}

for i in range(len(criteria)):
    for j in range(i + 1, len(criteria)):
        question = f"Par rapport à **{criteria[i]}** vs **{criteria[j]}**, lequel est plus important ?"
        choix = st.slider(question, 1, 9, 5, format="%d")
        pairwise[(criteria[i], criteria[j])] = choix

# Création de la matrice AHP
if st.button("Calculer les priorités"):
    size = len(criteria)
    mat = np.ones((size, size))

    for i in range(size):
        for j in range(size):
            if i != j:
                if (criteria[i], criteria[j]) in pairwise:
                    mat[i][j] = pairwise[(criteria[i], criteria[j])]
                    mat[j][i] = 1 / mat[i][j]

    # Normalisation et pondération
    column_sums = np.sum(mat, axis=0)
    normalized = mat / column_sums
    weights = np.mean(normalized, axis=1)
    df_weights = pd.DataFrame({"Critère": criteria, "Poids": weights})

    st.success("Voici la pondération de vos critères :")
    st.dataframe(df_weights)

    fig = px.pie(df_weights, names="Critère", values="Poids", title="Priorisation des critères")
    st.plotly_chart(fig)

    st.markdown("Un rapport peut être généré selon ces priorités pour vous proposer des actions ciblées dès le premier contact.")

    # Analyse et génération de résumé
    st.subheader("Résumé personnalisé des priorités")

    top_criteria = df_weights.sort_values("Poids", ascending=False).head(3)

    resume = f"""
Bonjour {nom if nom else "utilisateur"}, voici un aperçu de vos priorités :

1. **{top_criteria.iloc[0]['Critère']}** : Ce critère a été identifié comme le plus important. Nous vous proposerons des actions ciblées pour l'optimiser en priorité.
2. **{top_criteria.iloc[1]['Critère']}** : Ce critère arrive en deuxième position, et sera intégré dans les recommandations secondaires.
3. **{top_criteria.iloc[2]['Critère']}** : Ce critère complète votre trio de tête et pourra être intégré dans les solutions complémentaires.

Grâce à cette hiérarchisation, un audit ciblé pourra être planifié avec un maximum d'efficacité et de pertinence.
"""

    st.markdown(resume)

    # Bouton pour télécharger le résumé
    st.download_button(
        label="📄 Télécharger le résumé personnalisé",
        data=resume,
        file_name=f"resume_audit_flash_{nom.replace(' ', '_') if nom else 'utilisateur'}.txt",
        mime="text/plain"
    )
