import streamlit as st
import pandas as pd
from PIL import Image

# Carica il logo
logo = Image.open("assets/logo.png")
st.image(logo, width=150)

# Carica i dati
df = pd.read_excel('data/R.E.P.xlsx', sheet_name='DATI', engine='openpyxl', header=3)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Campi obbligatori
obbligatorie = [
    "Nome Breve", "OWNER", "PM", "Appalto", "Tipologia",
    "Importo contrattuale (al netto di progettazione, sicurezza) aggiornato all'ultimo atto ufficiale"
]

# Campi facoltativi
formula_keywords = ["Delta", "Avanz.", "%", "Ritardo", "Durata", "Fine Lavori", "Attivazione"]
facoltative = [col for col in df.columns if any(k in col for k in formula_keywords) or "NOTE" in col or "previsione" in col or "€" in col or "Importo" in col or "mln" in col]

st.set_page_config(page_title="Monitoraggio Progetti", layout="wide")
st.title("📊 Dashboard Monitoraggio Progetti")

# Login utente
utente = st.text_input("🔐 Inserisci il tuo nome utente")

if utente:
    filtered_df = df[df['OWNER'] == utente]
    st.subheader(f"Progetti associati a: {utente}")
    st.dataframe(filtered_df)

    st.markdown("---")
    st.subheader("➕ Inserisci nuovo progetto")

    mostra_form = st.checkbox("Mostra campi da compilare")

    if mostra_form:
        with st.form("form_nuovo_progetto"):
            nuovo = {}
            st.markdown("### Campi obbligatori")
            for i, campo in enumerate(obbligatorie):
                nuovo[campo] = st.text_input(f"{campo}", key=f"new_{i}")

            st.markdown("### Campi facoltativi")
            for j, campo in enumerate(facoltative):
                nuovo[campo] = st.text_input(f"{campo}", key=f"new_f_{j}")

            submitted = st.form_submit_button("💾 Salva nuovo progetto")
            if submitted:
                df = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
                st.success("✅ Nuovo progetto salvato!")

    st.markdown("---")
    st.subheader("🛠️ Modifica progetto esistente")

    appalti = filtered_df['Nome Breve'].dropna().unique().tolist()
    selected = st.selectbox("Seleziona un progetto da modificare", appalti)

    if selected:
        progetto = filtered_df[filtered_df['Nome Breve'] == selected].iloc[0]
        with st.form("form_modifica"):
            modifiche = {}
            for k, campo in enumerate(obbligatorie + facoltative):
                valore = progetto.get(campo, "")
                modifiche[campo] = st.text_input(f"{campo}", value=str(valore), key=f"mod_{k}")
            submitted = st.form_submit_button("🔄 Aggiorna progetto")
            if submitted:
                idx = df[(df['OWNER'] == utente) & (df['Nome Breve'] == selected)].index[0]
                for k, v in modifiche.items():
                    df.at[idx, k] = v
                st.success("✅ Progetto aggiornato!")
