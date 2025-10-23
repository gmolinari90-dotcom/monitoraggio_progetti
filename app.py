
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
        df = pd.read_excel('data/R.E.P.xlsx', sheet_name='DATI', engine='openpyxl', header=3)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        obbligatorie = [
            "Nome Breve", "OWNER", "PM", "Appalto", "Tipologia",
            "Importo contrattuale (al netto di progettazione, sicurezza) aggiornato all'ultimo atto ufficiale"
        ]
        formula_keywords = ["Delta", "Avanz.", "%", "Ritardo", "Durata", "Fine Lavori", "Attivazione"]
        euro_columns = [col for col in df.columns if "€" in col or "Importo" in col or "mln" in col]
        facoltative = [col for col in df.columns if any(k in col for k in formula_keywords) or "NOTE" in col or "previsione" in col or col in euro_columns]

        # Visualizzazione schede come bottoni affiancati
        st.markdown("### Seleziona sezione")
        cols = st.columns(len(sezioni))
        scelta = st.session_state.get("scelta", sezioni[0])
        for i, sezione in enumerate(sezioni):
            if cols[i].button(sezione):
                st.session_state["scelta"] = sezione
                scelta = sezione

        if scelta == "GESTIONALE":
            st.subheader("🛠️ GESTIONALE")
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
            if 'AREA GEOGRAFICA' in df.columns:
                area_counts = df['AREA GEOGRAFICA'].value_counts().reset_index()
                area_counts.columns = ['AREA GEOGRAFICA', 'Numero Progetti']
                fig = px.bar(area_counts, x='AREA GEOGRAFICA', y='Numero Progetti', title='Distribuzione Progetti per Area Geografica')
                st.plotly_chart(fig)
            else:
                st.warning("Colonna 'AREA GEOGRAFICA' non trovata nei dati.")
    