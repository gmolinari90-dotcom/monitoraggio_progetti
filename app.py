import streamlit as st
import pandas as pd

# Carica i dati
df = pd.read_excel('data/R.E.P.xlsx', sheet_name='DATI', engine='openpyxl', header=3)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Campi obbligatori
obbligatorie = [
    "Nome Breve", "OWNER", "PM", "Appalto", "Tipologia",
    "Importo contrattuale (al netto di progettazione, sicurezza) aggiornato all'ultimo atto ufficiale"
]

# Campi facoltativi
formula_keywords = ["Delta", "Avanz.", "%", "Ritardo", "Durata", "Importo SIL", "Fine Lavori", "Attivazione"]
facoltative = [col for col in df.columns if any(k in col for k in formula_keywords) or "NOTE" in col or "previsione" in col]

st.set_page_config(page_title='Monitoraggio Progetti', layout='wide')
st.title("📊 Dashboard Monitoraggio Progetti")

# Login utente
utente = st.text_input("🔐 Inserisci il tuo nome utente").strip().upper()

if utente:
    filtered_df = df[df['OWNER'].astype(str).str.upper() == utente]
    st.subheader(f"Progetti associati a: {utente}")
    st.dataframe(filtered_df)

    st.markdown("---")
    st.subheader("➕ Inserisci nuovo progetto")

    mostra_form = st.checkbox("Mostra campi da compilare")

    if mostra_form:
        with st.form("form_nuovo_progetto"):
            nuovo = {}
            st.markdown("### Campi obbligatori")
            for campo in obbligatorie:
                nuovo[campo] = st.text_input(f"{campo}")

            st.markdown("### Campi facoltativi")
            for campo in facoltative:
                nuovo[campo] = st.text_input(f"{campo}")

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
            for campo in obbligatorie + facoltative:
                valore = progetto.get(campo, "")
                modifiche[campo] = st.text_input(f"{campo}", value=str(valore))
            submitted = st.form_submit_button("🔄 Aggiorna progetto")
            if submitted:
                idx = df[(df['OWNER'].astype(str).str.upper() == utente) & (df['Nome Breve'] == selected)].index[0]
                for k, v in modifiche.items():
                    df.at[idx, k] = v
                st.success("✅ Progetto aggiornato!")
