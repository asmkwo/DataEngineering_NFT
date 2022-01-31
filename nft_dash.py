import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import math
from pymongo import MongoClient
import json


# client = MongoClient("mongo")
# nft_db = client["mydatabase"]
# nft_collection = nft_db['nft']
# nft_collection.delete_many({})

# with open('nft_spider_aleatoire.json') as file:
#     nft_data = json.load(file)
#
# if isinstance(nft_data, list):
#     nft_collection.insert_many(nft_data)
# else:
#     nft_collection.insert_one(nft_data)
#
# json.dumps(nft_collection)
#importing our data
df_nft = pd.read_csv('nft_spider_aleatoire.csv')

#DATA TREATMENT

#keeping only etherum nfts
df_eth = df_nft
for i in range(len(df_nft)):
    if "ETH" in df_eth["Prix"][i]:
        df_eth = df_eth
    else:
        df_eth.drop(i, 0, inplace=True)

df_eth = df_eth.reset_index()

df_eth["Prix (ETH)"] = df_eth["Prix"].astype(str)
for i in range(len(df_eth)) :
    df_eth["Prix (ETH)"].values[i] = float(df_eth["Prix"].values[i][0:4])

#arranging data to evaluate correlation between volumes and price, for pie1 and line1 graphs
df_eth_prix = df_eth.groupby('Prix (ETH)').mean()

#only keeping data where number of subs is available
df_eth_twitter = df_eth
for i in range(len(df_eth)):
    if math.isnan(df_eth["Nombre d'abonnés"][i]) :
        df_eth_twitter.drop(i, 0, inplace = True)
df_eth_twitter = df_eth_twitter.reset_index()

#calculating the number of interactions and adding a new column in the dataframe
df_eth_twitter['Intéractions'] = df_eth_twitter.values[:,8]
for i in range(9) :
    df_eth_twitter['Intéractions'] += df_eth_twitter.values[:,i+9]
df_eth_twitter["Intéractions"] = df_eth_twitter["Intéractions"].astype(float)

df_eth_twitter_prix = df_eth_twitter.groupby('Prix (ETH)').mean()

#created to determine correlation between the volumes and other parameters
df_eth_twitter_volumes = df_eth_twitter.groupby('Volumes').mean()



#creating the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.GRID, dbc.themes.DARKLY])


app.layout = html.Div ([

    html.H1("Dashboard about nft engagement", style={'text-align' : 'center'}),

    dcc.Dropdown(id="selected_year",
        options = [
            {'label':'1985', 'value':1985},
            {'label':'1986', 'value':1986},
            {'label':'1987', 'value':1987}],

        multi=False,
        value=2000,
        style={'width':"40%"}
        ),


    html.Div(id='output_container', children=[]),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='line_prix_volumes', figure={}),
        ], width=6),
        dbc.Col([
            dcc.Graph(id='pie_volumes_prix', figure={}),
        ], width=6)

    ],justify="center"),

   # dcc.Graph(id='pie_volumes_prix', figure={}),
   # dcc.Graph(id='line_prix_volumes', figure={}),
    dcc.Graph(id='line_prix_abonnes', figure={}),
    dcc.Graph(id='line_volumes_abonnes', figure={}),
    dcc.Graph(id='line_volumes_interactions', figure={}),
    dcc.Graph(id='scatter_prix_abonnes_volumes', figure={})

])

# callbacks : connect the dash components with the plotly graph
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='pie_volumes_prix', component_property='figure'),
     Output(component_id='line_prix_volumes', component_property='figure'),
     Output(component_id='line_prix_abonnes', component_property='figure'),
     Output(component_id='line_volumes_abonnes', component_property='figure'),
     Output(component_id='line_volumes_interactions', component_property='figure'),
     Output(component_id='scatter_prix_abonnes_volumes', component_property='figure')
    ],
    [Input(component_id='selected_year', component_property='value')]
)

def update_graph(option_selected):

    container = "The year chosen by the user was : {}".format(option_selected)

#plotly Express

    container = "The year chosen by the user was : {}".format(option_selected)
    pie_volumes_prix = px.pie(
        values =  df_eth_prix["Volumes"],
        names = df_eth_prix.index,
        title = 'Répartition des volumes en fonction des prix (ETH)',
        labels = {'values':'Volumes', 'names':'Prix (ETH)'},
    )

    line_prix_volumes = px.line(
        x = df_eth_prix.index,
        y=df_eth_prix['Volumes'],
        title="Evolution du prix en fonction des volumes",
        labels={'x': 'Prix (ETH)', 'y': "Volumes"}
    )

    line_prix_abonnes = px.line(
        x=df_eth_twitter_prix.index,
        y=df_eth_twitter_prix["Nombre d'abonnés"],
        title="Evolution du prix en fonction du nombre d'abonnés",
        labels={'x': 'Prix (ETH)', 'y': "Nombre d'abonnés"}
    )

    line_volumes_abonnes = px.line(
        x=df_eth_twitter_volumes.index,
        y=df_eth_twitter_volumes["Nombre d'abonnés"],
        title="Evolution des volumes en fonction du nombre d'abonnés",
        labels={'x': 'Volumes', 'y': "Nombre d'abonnés"}
    )

    line_volumes_interactions = px.line(
        x=df_eth_twitter_volumes.index,
        y=df_eth_twitter_volumes["Intéractions"],
        title="Evolution des volumes en fonction du nombre d'intéractions",
        labels={'x': 'Volumes', 'y': "Nombre d'intéractions"}
    )

    scatter_prix_abonnes_volumes = px.scatter(
        x=df_eth_twitter_prix.index,
        y=df_eth_twitter_prix["Volumes"],
        size=df_eth_twitter_prix["Nombre d'abonnés"],
        title="Prix en fonction du nombre d'abonnés",
        labels={'x': 'Prix', 'y': 'Volumes', 'size': "Nombre d'abonnés"}
     )

    return container, pie_volumes_prix, line_prix_volumes, line_prix_abonnes, line_volumes_abonnes,line_volumes_interactions,scatter_prix_abonnes_volumes






if __name__ == '__main__':
    app.run_server(debug=True)
