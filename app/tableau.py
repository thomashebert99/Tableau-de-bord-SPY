from dash import Dash, html, dcc, callback, Input, Output, State, MATCH, ALL, ctx, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback_context
from plotly.graph_objs import Figure
import json
import os
import sys
import subprocess

current_directory = os.path.dirname(__file__)
scripts_path = os.path.join(current_directory, 'data', 'Scripts')
sys.path.append(scripts_path)

from DataProcessing import process_statements
from calculate_graphs import analyze_student_data, calculate_competence_scores, calculate_competence_scores_perso, calculate_progression

# Chemin du fichier CSV pour stocker les données
csv_file = 'favoris.csv'

def initial_data_processing():
    # Vérifier si le fichier CSV existe
    if os.path.exists(csv_file):
        # Charger et traiter les données
        df = pd.read_csv(csv_file)
        for student_id in df['ID']:
            script_path = os.path.join(current_directory, 'data', 'Scripts', 'requestData.py')
            subprocess.run(['python', script_path, student_id])
            process_statements(student_id)

def delete_element_from_csv(element_id, csv_path):
    try:
        # Lecture du fichier CSV
        df = pd.read_csv(csv_path)

        # Suppression de la ligne correspondant à l'ID spécifié
        df = df[df['ID'] != element_id]

        # Enregistrement du DataFrame modifié dans le fichier CSV
        df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression : {e}")
        return False


def create_grouped_barplot():
    df = calculate_competence_scores()

    scenarios = df['scenario'].tolist()

    fig = go.Figure(data=[
        go.Bar(name='Conditions', x=scenarios, y=df['conditions'].tolist()),
        go.Bar(name='Conditions max', x=scenarios, y=df['conditions max'].tolist(),
               marker=dict(color='rgba(0,0,0,0)', line=dict(color='blue'))),
        go.Bar(name='Boucles', x=scenarios, y=df['boucles'].tolist()),
        go.Bar(name='Boucles max', x=scenarios, y=df['boucles max'].tolist(),
               marker=dict(color='rgba(0,0,0,0)', line=dict(color='red'))),
    ])
    # Change the bar mode
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    return fig

# Initialiser la liste des éléments à partir du fichier CSV
def init_sidebar_list():
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        return [{"label": f"{row['ID']} - {row['Prénom']} {row['Nom']}", "value": row['Index']}
                for index, row in df.iterrows()]
    return [{"label": "Aucun élève enregistré", "value": "none"}]

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "SPY Tableau de bord"

model_scenarios = pd.read_csv('data/Models/modelProcessing.csv')
scenarios_list = model_scenarios['scenario'].unique().tolist()

app.layout = html.Div(
    children=[
        html.Div(id='page-load', style={'display': 'none'}),
        html.Div(
            children=[
                html.Img(
                    src="/assets/images/LogoSPY.png",
                    className="header-logo"
                ),
                html.H1(
                    children="Tableau de bord", className="header-title"
                )
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.H2("Liste des élèves"),
                                html.Button("+", id="open-modal-button", className="add-button")
                            ],
                            className="sidebar-header"
                        ),
                        dcc.Store(id='sidebar-store', data=init_sidebar_list()),  # Stock pour la liste des éléments
                        html.Ul(id="element-list", className="sidebar-list")
                    ],
                    className="sidebar" 
                ),
                html.Div(
                    children=[
                        html.Div(
                            className='circles-container',
                            children=[
                                html.H2("Scénarios terminés", className="container-title"),
                                html.Div(
                                    className='circle-graph-container',
                                    children=[
                                        dcc.Graph(id="graph")
                                    ]
                                ),
                                html.Div(
                                    className='circle-dropdown-container',
                                    children=[
                                        html.P("Scénario:"),
                                        dcc.Dropdown(
                                            id="values",
                                            options=scenarios_list,
                                            value="0 - tutoriel",
                                            clearable=False,
                                            style={"width": "100%"}
                                        ),
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className='barplot-grouped-container',
                            children=[
                                html.H2("Acquisition des compétences", className="container-title", id="barplot-title"),
                                dcc.Graph(id='unique-graph-id', figure=create_grouped_barplot())
                            ],
                            style={'width': '100%'}
                        )
                    ],
                    className="content-graphs"
                )
            ],
            className="content"
        ),
        dbc.Modal([
            dbc.ModalHeader("Ajouter un élève"),
            dbc.ModalBody([
                dbc.Input(id="input-id", placeholder="ID"),
                dbc.Input(id="input-first-name", placeholder="Prénom"),
                dbc.Input(id="input-last-name", placeholder="Nom")
            ]),
            dbc.ModalFooter([
                dbc.Button("Accepter", id="accept-button", className="ms-auto", n_clicks=0),
            ])
        ], id="add-modal", is_open=False
        ),
        dbc.Modal([
            dbc.ModalHeader([
                html.H4(id="details-modal-title", style={"display": "inline-block"}),
                dbc.Button("Supprimer", id="delete-button", className="ms-auto", style={"display": "inline-block", "background-color": "red"})
            ]),
            dbc.ModalBody([
                html.Div([
                    html.H2("Progression des niveaux", className="container-title"),
                    # Container pour les progress bars
                    html.Div(id="progress-container", style={"height": "300px", "overflowY": "scroll"}),

                    # Dropdown pour sélectionner le scénario
                    html.P("Scénario:"),
                    dcc.Dropdown(
                        id="progress-dropdown",
                        options=scenarios_list,
                        value="0 - tutoriel",
                        clearable=False
                    ),
                ], style = {'padding-bottom': '50px'}),
                html.Div(
                    className='barplot-grouped-container-details',
                    children=[
                        html.H2("Acquisition des compétences", className="container-title", id="barplot-title_perso"),
                        dcc.Graph(id='barplot_perso')
                    ],
                    style={'width': '100%'}
                ),
            ]),
        ],
            id="details-modal",
            is_open=False,  # Le modal est fermé par défaut
            size="xl",
            scrollable=True,
        ),
        dbc.Modal([
            dbc.ModalHeader("Confirmer la suppression"),
            dbc.ModalBody("Voulez-vous vraiment supprimer cet élément ?"),
            dbc.ModalFooter([
                dbc.Button("Oui", id="confirm-delete-button", className="ms-auto", style={"background-color": "blue"}),
                dbc.Button("Non", id="cancel-delete-button", className="ms-auto", style={"background-color": "red"})
        ])
        ], 
        id="confirm-delete-modal", is_open=False, backdrop=False),
        dcc.Store(id='details-modal-store', data={'is_open': False}),
        dcc.Store(id='selected-student-id', data=None),
        html.Div(id='invisible-output', style={'display': 'none'}),
    ],
    className="container"
)

@app.callback(
    Output("graph", "figure"),
    Input("values", "value"),
)
def generate_chart(values):
    labels = ["a terminé","n'a pas terminé"]
    df = analyze_student_data()
    row = df.loc[df['scenario'] == values]
    if not row.empty:
        values_pie = row.iloc[0, 1:].tolist()
    else:
        values_pie = []
    # fig = px.pie(df, values=values, names=names, hole=0.3)
    fig = go.Figure(data=[go.Pie(labels=labels, values=values_pie, hole=.3)])
    fig.update_traces(textinfo='percent+label')
    # Ajuster la mise en page pour une plus petite taille de conteneur
    fig.update_layout(
        autosize=True,
        showlegend=False,
        margin=dict(
            t=0,  # Enlève la marge en haut
            b=0,  # Enlève la marge en bas
            l=0,  # Enlève la marge à gauche
            r=0   # Enlève la marge à droite
        )
    )
    return fig

    
# Callback pour ouvrir/fermer la fenêtre modale
@app.callback(
    Output("add-modal", "is_open"),
    [Input("open-modal-button", "n_clicks"), Input("accept-button", "n_clicks")],
    [State("add-modal", "is_open")])
def toggle_modal(open_clicks, accept_clicks, is_open):
    if open_clicks or accept_clicks:
        return not is_open
    return is_open


# Callback pour initialiser la liste des éléments dans la sidebar
@app.callback(
    Output("element-list", "children"),
    Input('sidebar-store', 'data')
)
def update_element_list(data):
    if not data or data[0]["value"] == "none":
        return [html.Li("Aucun élève enregistré", style={"cursor": "default"})]  # Curseur par défaut
    else:
        return [html.Li(
                    d["label"],
                    id={"type": "sidebar-element", "index": d["value"]},
                    style={"cursor": "pointer"}
                ) for d in data]

@app.callback(
    Output("sidebar-store", "data"),
    Input("accept-button", "n_clicks"),
    [State("input-id", "value"), State("input-first-name", "value"),
     State("input-last-name", "value"), State("sidebar-store", "data")],
    prevent_initial_call=True
)
def add_new_element(n_clicks, input_id, input_first_name, input_last_name, data):
    if n_clicks:
        new_data = {"ID": input_id, "Prénom": input_first_name, "Nom": input_last_name}

        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            # Ajout de l'index unique
            new_index = df.index.max() + 1 if not df.empty else 0
        else:
            df = pd.DataFrame(columns=['Index', 'ID', 'Prénom', 'Nom'])
            new_index = 0

        new_data = {"Index": new_index, **new_data}
        new_row = {"label": f"{input_id} - {input_first_name} {input_last_name}", "value": new_index}

        # Créer un DataFrame à partir de new_data et le concaténer
        new_df = pd.DataFrame([new_data])
        df = pd.concat([df, new_df], ignore_index=True)

        df.to_csv(csv_file, index=False)

        if data[0]["value"] == "none":
            return [new_row]
        else:
            return data + [new_row]


@app.callback(
    [Output("details-modal", "is_open"), Output("details-modal-title", "children")],
    [Input({"type": "sidebar-element", "index": ALL}, "n_clicks"), Input("details-modal-store", "data")],
    [State("sidebar-store", "data"), State("details-modal", "is_open")]
)
def open_details_modal(n_clicks, modal_store_data, data, is_open):
    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Gestion de l'ouverture via les éléments de la sidebar
    if triggered_id.startswith('{"index":'):
        button_id = json.loads(triggered_id)
        index = button_id["index"]

        if n_clicks[index] is not None and n_clicks[index] > 0:
            label = data[index]["label"]
            return True, label

    # Gestion de la fermeture via le store
    if triggered_id == "details-modal-store" and not modal_store_data['is_open']:
        return False, ""

    return is_open, no_update


@app.callback(
    [Output("confirm-delete-modal", "is_open"), Output("details-modal-store", "data")],
    [Input("delete-button", "n_clicks"), Input("cancel-delete-button", "n_clicks"), Input("confirm-delete-button", "n_clicks")],
    [State("confirm-delete-modal", "is_open")],
)
def toggle_confirm_modal(delete_clicks, cancel_clicks, confirm_clicks, is_open):
    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "delete-button":
        return True, no_update  # Ouvrir le modal de confirmation
    elif triggered_id == "cancel-delete-button":
        return False, no_update  # Fermer le modal de confirmation sans autres actions
    elif triggered_id == "confirm-delete-button":
        return False, {'is_open': False}  # Fermer les deux modals
    return is_open, no_update  # Conserver l'état actuel dans les autres cas

@app.callback(
    Output('invisible-output', 'children'),
    [Input('accept-button', 'n_clicks')],
    [State('input-id', 'value')],  # Remplacez 'input-id' par l'ID de votre élément Input pour l'ID
    prevent_initial_call=True
)
def on_accept_button_click(n_clicks, input_id):
    if n_clicks is not None and input_id is not None:
        # Construire le chemin relatif vers requestData.py
        script_path = os.path.join(os.path.dirname(__file__), 'data', 'Scripts', 'requestData.py')

        # Exécuter le script requestData.py avec l'ID comme argument
        subprocess.run(['python', script_path, input_id])

        # Appeler la fonction process_statements avec le même ID
        process_statements(input_id)

        return "Traitement terminé pour l'ID: " + input_id

    return no_update

@app.callback(
    [Output("input-id", "value"),
     Output("input-first-name", "value"),
     Output("input-last-name", "value")],
    [Input("add-modal", "is_open")],
    [State("input-id", "value"),
     State("input-first-name", "value"),
     State("input-last-name", "value")],
    prevent_initial_call=True
)
def reset_modal_inputs(is_open, id_val, first_name_val, last_name_val):
    if not is_open:
        # Réinitialiser les valeurs lorsque le modal est fermé
        return "", "", ""
    return id_val, first_name_val, last_name_val

# Callback pour stocker l'ID de l'élève sélectionné lorsqu'un élément de la sidebar est cliqué
@app.callback(
    Output('selected-student-id', 'data'),
    [Input({'type': 'sidebar-element', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def store_selected_student_id(n_clicks):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    index = json.loads(triggered_id)['index']
    df = pd.read_csv(csv_file)
    if 0 <= index < len(df):
        return df.loc[index, 'ID']
    return None

# Callback pour créer le graphe histogramme groupé pour l'élève sélectionné
@app.callback(
    Output('barplot_perso', 'figure'),
    [Input('selected-student-id', 'data')],
    prevent_initial_call=True
)
def create_grouped_barplot_perso(student_id):
    if student_id is not None:
        df = calculate_competence_scores_perso(student_id)
        scenarios = df['scenario'].tolist()

        fig = go.Figure(data=[
            go.Bar(name='Conditions', x=scenarios, y=df['conditions'].tolist()),
            go.Bar(name='Conditions max', x=scenarios, y=df['conditions max'].tolist(),
                   marker=dict(color='rgba(0,0,0,0)', line=dict(color='blue'))),
            go.Bar(name='Boucles', x=scenarios, y=df['boucles'].tolist()),
            go.Bar(name='Boucles max', x=scenarios, y=df['boucles max'].tolist(),
                   marker=dict(color='rgba(0,0,0,0)', line=dict(color='red'))),
        ])
        # Change the bar mode
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        return fig
    return go.Figure()

# Callback pour mettre à jour les progress bars en fonction du scénario sélectionné
@app.callback(
    Output("progress-container", "children"),
    [Input("progress-dropdown", "value"), Input('selected-student-id', 'data')],
    prevent_initial_call=True
)
def update_progress_container(selected_scenario, student_id):
    if student_id is not None:
        df = calculate_progression(student_id)
        filtered_df = df[df['scenario'] == selected_scenario]

        progress_bars = []
        for index, row in filtered_df.iterrows():
            niveau = row['niveau']
            progression = row['progression']

            # Calculer le nombre d'étoiles
            if progression >= 100:
                stars = '★ ★ ★'
            elif progression >= 66:
                stars = '★ ★'
            elif progression >= 33:
                stars = '★'
            else:
                stars = "non complété"

            label = f"{niveau} : {stars}"

            # Créer un conteneur pour la barre de progression et le label
            progress_bar_container = html.Div([
                dbc.Progress(value=progression, color="success", style={"height": "30px"}),
                html.Div(label, style={
                    "position": "absolute",
                    "width": "100%",
                    "text-align": "center",
                    "font-weight": "bold",
                    "color": "black",
                    "top": "50%", # Centrer verticalement dans la barre
                    "transform": "translateY(-50%)", # Ajustement pour le centrage vertical
                    "padding": "5px"
                })
            ], style={"position": "relative", "margin": "auto", "width": "75%", "margin-bottom": "20px"})

            progress_bars.append(progress_bar_container)

        return progress_bars

@app.callback(
    Output('page-load', 'children'),
    Input('page-load', 'children')
)
def page_load_callback(_):
    initial_data_processing()
    return ""

if __name__ == "__main__":
    app.run_server(debug=True)