import streamlit as st
import pandas as pd
import plotly.express as px

# Funzione per caricare i dati
@st.cache_data
def load_data():
    df = pd.read_excel('data/R.E.P.xlsx', sheet_name='DATI', engine='openpyxl', header=3)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    columns = [
        'Nome Breve', 'OWNER', 'PM', 'Importo SIL Mensile Effettivo',
        'Importo SIL Cumulato effettivo', '% Avanz. Economico Effettivo',
        'Delta % Avanzamento ', 'RITARDO TOTALE CLB - CP', 'NOTE'
    ]
    return df[columns].copy()

# Caricamento dati
df = load_data()

# Titolo dashboard
st.title("Dashboard Monitoraggio Progetti")

# Login utente
utente = st.text_input("Inserisci il tuo nome utente")

if utente:
    filtered_df = df[df['OWNER'] == utente]
    st.subheader(f"Progetti associati a: {utente}")
    st.dataframe(filtered_df)

    # Grafico avanzamento economico
    fig = px.bar(
        filtered_df,
        x='Nome Breve',
        y='% Avanz. Economico Effettivo',
        title="Avanzamento Economico Effettivo",
        text='% Avanz. Economico Effettivo'
    )
    st.plotly_chart(fig)

    # Form per aggiunta/modifica
    st.subheader("Modifica o aggiungi un progetto")
    nome_breve = st.text_input("Nome Breve")
    pm = st.text_input("PM")
    sil_mensile = st.number_input("Importo SIL Mensile Effettivo", value=0.0)
    sil_cumulato = st.number_input("Importo SIL Cumulato effettivo", value=0.0)
    avanzamento = st.number_input("% Avanz. Economico Effettivo", value=0.0)
    delta = st.number_input("Delta % Avanzamento", value=0.0)
    ritardo = st.number_input("RITARDO TOTALE CLB - CP", value=0.0)
    nota = st.text_area("NOTE")

    if st.button("Salva progetto"):
        nuova_riga = {
            'Nome Breve': nome_breve,
            'OWNER': utente,
            'PM': pm,
            'Importo SIL Mensile Effettivo': sil_mensile,
            'Importo SIL Cumulato effettivo': sil_cumulato,
            '% Avanz. Economico Effettivo': avanzamento,
            'Delta % Avanzamento ': delta,
            'RITARDO TOTALE CLB - CP': ritardo,
            'NOTE': nota
        }
        df = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
        st.success("Progetto salvato correttamente!")
        st.dataframe(df[df['OWNER'] == utente])
``
