#---------------- LES PACKAGES ------------------------------

import streamlit as st
import pandas as pd 
from streamlit_echarts import st_echarts
from skcriteria import Data, MIN, MAX
from skcriteria.madm import simple
from st_aggrid import AgGrid

#---------------- FONCTIONS ------------------------------

def get_int(x):
    x =  int(x.split('%')[0])
    return x

def transform(x): # Convertit nos pourcentages en nombre
    try:
        x = str(x).strip()
        x = x.split('%')[0]
        x = x.split()[1]
        x = int(x)
    except:
        return x

def transform_price(x): # Convertit nos prix en nombre
    try:
        x = int(str(x).split()[0])
        return x
    except:
        return None

def valeur_list(lst): # Retourn une liste avec avec 'min' ou 'max' en fonction de la colonne (utilisée dans le cadre de notre fonction ranking)
    v = []
    for element in lst:
        if element!='price':
            v.append('max')
        else:
            v.append('min')
    return v 

def ranking(criteres, montants): # Notre fonction de ranking qui retourne un dataframe répondant aux critères de l'utilisateur. Prends en entrée les critères et le filtre des prix
    cols = ['marque','modele']
    cols.extend(criteres)
    cols.append('price')
    criteres = cols[2:]

    # Creation de notre dataframe temporaire

    temp_df = df[cols]

    for element in criteres:
        if element !='price':
            temp_df[element] = temp_df[element].apply(lambda x:transform(x))
        else:
            temp_df[element] = temp_df[element].apply(lambda x:transform_price(x))

    temp_df = temp_df[(temp_df['price']>int(montants[0])) & (temp_df['price']<int(montants[1]))]

    criteria_data = Data(
        temp_df[criteres],          # pandas dataframe
        valeur_list(criteres),      # min ou max pour chaque colonne
        anames = temp_df['modele'], # nom des smarphones (ici ce sont les modèles)
        cnames = criteres,          # attributs/nom des colonnes
        )

    # Somme pondérée des critères (tous les critères ont le même poids : 1)
    dm = simple.WeightedSum(mnorm="sum")
    dec = dm.decide(criteria_data)
    temp_df['rank'] = dec.rank_

    # On retourne notre dataframe avec les 10 meilleurs résultats
    return temp_df.sort_values('rank')[:10].reset_index(drop=True)


#-------------------------------------------------------------------------------

#-----------------------  APPLICATION  ------------------------------------------

df = pd.read_csv('/Users/laajajmohamed/Documents/smartphones.csv')
marque1 = df['marque'].sort_values().unique()
marque2 = df['marque'].sort_values().unique()

st.title("Smartphone Comparison APP")
st.markdown("**Fait par Mohamed LAAJAJ**")
st.write("""Toutes les données ont été obtenues à partir du site 'Notebookcheck.net'.  
Pour plus d'informations : https://github.com/mlaajaj/PortfolioProjects/blob/main/Smartphones_scrap.ipynb""") 

st.markdown("---")

st.header('Filtres')

# Menu

menu = ['Comparer les smartphones', 'Quel smartphones choisir ?']
choice = st.sidebar.selectbox('Menu', menu)

# Choix 1 
if choice==menu[0]:
    col1, col2 = st.columns(2)
    with col1:
        m1 = st.selectbox("Marque 1", marque1)
        smarphone = df[df['marque']==m1]['modele'].sort_values().unique()
        s1 = st.selectbox("Smartphone 1", smarphone)
    with col2:
        m2 = st.selectbox("Marque 2", [n for n in marque1 if n!=m1])
        smarphone2 = df[df['marque']==m2]['modele'].sort_values().unique()
        s2 = st.selectbox("Smartphone 2", smarphone2)

    critere = st.multiselect("Quels critères ?", sorted(df.columns.to_list()[2:15]))

    lst = []
    for n in critere:
        d = {'name':n, 'max':'100'}
        lst.append(d)

    values1 = df[df['modele']==s1][critere].values.tolist()[0]
    values2 = df[df['modele']==s2][critere].values.tolist()[0]

    if st.button('Comparer !'):

        st.header('Comparaison')
        option = {
            "title": {"text": " "},
            "tooltip": {
                "trigger": 'item'
            },
            "legend": {"data": [str(s1), str(s2)]},
            "radar": {
                "indicator": lst
            },
            "series": [
                {
                    "name": "",
                    "type": "radar",
                        "tooltip": {
                    "trigger": 'item'},
                    "data": [
                        {
                            "value": [get_int(v) for v in values1],
                            "name": s1,
                        },
                        {
                            "value": [get_int(v) for v in values2],
                            "name": s2,
                        },
                    ],
                }
            ],
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",

                        }
                },
        }            

        st_echarts(option, height="600px")

        st.header('Informations techniques')
        smartphones = [s1, s2]
        cols = ['marque']
        cols.extend(df.columns[16:len(df.columns)])
        data = df[df['modele'].isin(smartphones)][cols]
        data = data.T.rename(columns={data.T.columns[1]:s2, data.T.columns[0]:s1})
        st.dataframe(data)


# Choix 2 - Utilisation d'un else car nous avons que deux choix 
else:
    st.subheader('Zone de filtres')
    criteres = st.multiselect("Quels critères ?", sorted(df.columns.to_list()[2:15]))
    st.write('')
    prix = st.slider('Choisissez une fourchette de prix', 100.0, 1000.0, (300.0, 600.0))
    bt = st.button('Lancer la recherche !')
    st.markdown('---')
    if bt:
        st.subheader('Top 10 des meilleurs résultats selon vos critères !')
        AgGrid(ranking(criteres,prix))
