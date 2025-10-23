import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
from config_streamlit import obbligatorie, facoltative, accessi_utenti

# Logo
logo = Image.open("assets/logo.png")
st.image(logo, width=150)

# Carica dati
file_path = 'data/R.E.P.xlsx'
df = pd.read_excel(file_path, sheet_name='DATI', engine='openpyxl', header=3)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

st.set_page_config(page_title='Dashboard Progetti', layout='wide')
st.title("📊 Dashboard Monitoraggio Progetti")

# Login utente
utente = st.text_input("🔐 Inserisci il tuo nome utente")

if utente:
    sezioni = accessi_utenti.get(utente, [])
    scelta = st.sidebar.radio("📁 Seleziona sezione", sezioni)

    if scelta == "GESTIONALE":
        st.subheader("🛠️ GESTIONALE - Inserimento e modifica progetti")
        filtered_df = df[df['OWNER'] == utente]
        st.dataframe(filtered_df)

        with st.form("form_gestione"):
            nuovo = {}
            st.markdown("### Campi obbligatori")
            for i, campo in enumerate(obbligatorie):
                nuovo[campo] = st.text_input(campo, key=f"gest_ob_{i}")
            st.markdown("### Campi facoltativi")
            for j, campo in enumerate(facoltative):
                nuovo[campo] = st.text_input(campo, key=f"gest_fac_{j}")
            submitted = st.form_submit_button("💾 Salva progetto")
            if submitted:
                df = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
                st.success("✅ Progetto salvato!")

    elif scelta == "RIEPILOGO":
        st.subheader("📋 RIEPILOGO COMPLETO")
        st.dataframe(df)
        selected = st.selectbox("Seleziona progetto da modificare", df['Nome Breve'].dropna().unique())
        progetto = df[df['Nome Breve'] == selected].iloc[0]
        with st.form("form_riepilogo"):
            modifiche = {}
            for k, campo in enumerate(obbligatorie + facoltative):
                valore = progetto.get(campo, "")
                modifiche[campo] = st.text_input(campo, value=str(valore), key=f"riep_{k}")
            submitted = st.form_submit_button("🔄 Aggiorna progetto")
            if submitted:
                idx = df[df['Nome Breve'] == selected].index[0]
                for k, v in modifiche.items():
                    df.at[idx, k] = v
                st.success("✅ Progetto aggiornato!")

    elif scelta == "ANALISI DEI DATI":
        st.subheader("📊 ANALISI DEI DATI")
        if '% Avanz. Economico Effettivo' in df.columns:
            fig = px.bar(df, x='Nome Breve', y='% Avanz. Economico Effettivo', title='Avanzamento Economico')
            st.plotly_chart(fig)
        else:
            st.warning("Colonna '% Avanz. Economico Effettivo' non trovata nei dati.")
