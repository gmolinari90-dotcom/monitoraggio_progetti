
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px

st.set_page_config(page_title='Dashboard Monitoraggio Progetti', layout='wide')
st.title('📊 DASHBOARD MONITORAGGIO PROGETTI')

# Logo
try:
    logo = Image.open("assets/logo.png")
    st.image(logo, width=150)
except:
    st.warning("Logo non trovato nella cartella assets.")

# Login utente
utente = st.text_input("🔐 Inserisci il tuo nome utente").upper()

# Accessi
accessi_utenti = {
    "MOLINARI": ["GESTIONALE", "RIEPILOGO", "ANALISI DEI DATI"],
    "BARBATO": ["RIEPILOGO"],
    "ANGRISANO": ["GESTIONALE", "ANALISI DEI DATI"]
}

if utente:
    sezioni = accessi_utenti.get(utente, [])
    if not sezioni:
        st.warning("Utente non autorizzato.")
    else:
        # Carica dati
        df = pd.read_excel('R.E.P.xlsx', sheet_name='DATI', engine='openpyxl', header=3)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        obbligatorie = [
            "Nome Breve", "OWNER", "PM", "Appalto", "Tipologia",
            "Importo contrattuale (al netto di progettazione, sicurezza) aggiornato all'ultimo atto ufficiale"
        ]
        formula_keywords = ["Delta", "Avanz.", "%", "Ritardo", "Durata", "Fine Lavori", "Attivazione"]
        euro_columns = [col for col in df.columns if "€" in col or "Importo" in col or "mln" in col]
        facoltative = [col for col in df.columns if any(k in col for k in formula_keywords) or "NOTE" in col or "previsione" in col or col in euro_columns]

        tab1, tab2, tab3 = st.tabs(sezioni)

        if "GESTIONALE" in sezioni:
            with tab1:
                st.subheader("🛠️ GESTIONALE")
                filtered_df = df[df['OWNER'] == utente]
                st.dataframe(filtered_df)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Modifica progetto esistente"):
                        selected = st.selectbox("Seleziona progetto", filtered_df['Nome Breve'].dropna().unique())
                        progetto = filtered_df[filtered_df['Nome Breve'] == selected].iloc[0]
                        with st.form("form_modifica"):
                            modifiche = {}
                            for k, campo in enumerate(obbligatorie + facoltative):
                                valore = progetto.get(campo, "")
                                modifiche[campo] = st.text_input(campo, value=str(valore), key=f"mod_{k}")
                            submitted = st.form_submit_button("💾 Salva modifiche")
                            if submitted:
                                idx = df[df['Nome Breve'] == selected].index[0]
                                for k, v in modifiche.items():
                                    df.at[idx, k] = v
                                st.success("✅ Progetto aggiornato!")

                with col2:
                    if st.button("➕ Inserisci nuovo progetto"):
                        with st.form("form_nuovo"):
                            nuovo = {}
                            for i, campo in enumerate(obbligatorie + facoltative):
                                nuovo[campo] = st.text_input(campo, key=f"new_{i}")
                            submitted = st.form_submit_button("💾 Salva nuovo progetto")
                            if submitted:
                                df = pd.concat([df, pd.DataFrame([nuovo])], ignore_index=True)
                                st.success("✅ Nuovo progetto salvato!")

        if "RIEPILOGO" in sezioni:
            with tab2:
                st.subheader("📋 RIEPILOGO COMPLETO")
                st.dataframe(df)

        if "ANALISI DEI DATI" in sezioni:
            with tab3:
                st.subheader("📊 ANALISI DEI DATI")
                if 'AREA GEOGRAFICA' in df.columns:
                    area_counts = df['AREA GEOGRAFICA'].value_counts().reset_index()
                    area_counts.columns = ['AREA GEOGRAFICA', 'Numero Progetti']
                    fig = px.bar(area_counts, x='AREA GEOGRAFICA', y='Numero Progetti', title='Distribuzione Progetti per Area Geografica')
                    st.plotly_chart(fig)
                else:
                    st.warning("Colonna 'AREA GEOGRAFICA' non trovata nei dati.")
    