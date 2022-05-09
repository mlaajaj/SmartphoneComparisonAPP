### Core Pkgs

import streamlit as st
import pandas as pd 
from streamlit_echarts import st_echarts

def main():

    df = pd.read_csv('smartphones.csv')
    marque1 = df['marque'].sort_values().unique()
    marque2 = df['marque'].sort_values().unique()

    st.title("Smartphone Comparison APP")
    st.write("Made by Mohamed LAAJAJ")
    st.write("")
    st.write("")

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

    def get_int(x):
        x =  int(x.split('%')[0])
        return x


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
                    "name": "预算 vs 开销（Budget vs spending）",
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
        data = data.T.rename(columns={data.T.columns[0]:s2, data.T.columns[1]:s1})
        st.dataframe(data)

if __name__ == "__main__":
    main()
