from Data import *

# Récupération des données prétraitées
try:
    with open("Data/new_dataframe.txt", "rb") as f:
        pick = pickle.Unpickler(f)
        df_covid = pick.load()
except Exception as e:
    print("Pickle File Error:",e)
   
# Initialisation de l'application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Récupérons la liste des pays
pays = df_covid["countryName"].unique().tolist()

# Créons une liste contenant les mois de l'année
mois = ["Janvier", "Fevrier", "Mars"] + ["" for i in range(8)] + ["Décembre"]

# Récupérons la première date ou la date minimale
first_date = df_covid[["Jour", "month", "Année"]].head(1)

# Récupérons la dernière date ou la date maximale
last_date = df_covid[["Jour", "month", "Année"]].tail(1)

# Ajout de la barre de navigation
sidebar = dbc.Card(
    dbc.CardBody([
        html.H2("Covid-19 Navbar",
                className="display-4"),
        html.Hr(),
        html.P(
            "Choisissez une page",
            className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Nombre de cas",
                            href="/",
                            active="exact"),
                dbc.NavLink("Nombre de morts",
                            href="/page-1",
                            active="exact"),
                dbc.NavLink("Cas par mois",
                            href="/page-2",
                            active="exact"),
                dbc.NavLink("Morts par mois",
                            href="/page-3",
                            active="exact"),
                dbc.NavLink("Nouveaux cas par jour",
                            href="/page-4",
                            active="exact"),
                dbc.NavLink("Cumul des cas par mois",
                            href="/page-5",
                            active="exact"),
                dbc.NavLink("Cumul des morts par mois",
                            href="/page-6",
                            active="exact"),
                dbc.NavLink("Morts par jour",
                            href="/page-7",
                            active="exact"),
                dbc.NavLink("Top des pays - cas",
                            href="/page-8",
                            active="exact"),
                dbc.NavLink("Top des pays - morts",
                            href="/page-9",
                            active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ]),
    color="light",
    className="h-100",
    style={
            "width": "19rem",
            "position": "fixed",
            "overflow-y": "auto"
        }
)

# Définition de la squelette principale du contenu
content = dbc.Container(
    [
        html.Div(
            dcc.DatePickerRange(
                id = "date-picker",
                calendar_orientation="horizontal",
                day_size=39,
                end_date_placeholder_text="Dernière date",
                start_date_placeholder_text="Première date",
                with_portal=True,
                first_day_of_week=0,
                reopen_calendar_on_clear=True,
                is_RTL=False,
                clearable=True,
                number_of_months_shown=1,
                min_date_allowed=dt(
                    int(first_date["Année"]),
                    int(first_date["month"]),
                    int(first_date["Jour"])
                ),
                max_date_allowed=dt(
                    int(last_date["Année"]),
                    int(last_date["month"]),
                    int(last_date["Jour"])    
                ),
                initial_visible_month=dt(
                    2020, 
                    1,
                    1
                ),
                start_date=dt(
                    int(first_date["Année"]),
                    int(first_date["month"]),
                    int(first_date["Jour"])
                ).date(),
                end_date=dt(
                    int(last_date["Année"]),
                    int(last_date["month"]),
                    int(last_date["Jour"])
                ).date(),
                display_format="MMM Do, YY",
                month_format="MMMM, YYYY",
                minimum_nights=4,
                persistence=True,
                persisted_props=["start_date", "end_date"],
                persistence_type="session",
                updatemode="singledate",
                className="shadow-lg"
            ),
            style={"text-align": "right","margin": "1rem"}
        ),
        dcc.Dropdown(
            id = "pays",
            options=[{"label" : p, "value" : p} for p in pays],
            value = "Canada",
            className="form-control",
            placeholder="Choisissez un pays", 
            multi=True
        ),
        html.Div(
            id = "slider-top",
            className="text-center",
            children = [
                html.Label("Choisissez le nombre de pays dans le top"),
                dcc.Slider(
                    id = "choose-number",
                    value = 10,
                    # className="form-control",
                    min = 5,
                    max = 100,
                    marks={i: str(i) for i in range(5, 100+1, 5)}
                )
            ],
            style={"display": "none"}
        ),
        dbc.Card(
            dbc.CardBody(
                id = "principal-content"
            ),
            style={
                "margin-top": "2rem"
            }
        )
    ],
)

# Réunissons le location, la barre de navigation et le contenu dans le layout
app.layout = dbc.Container(
    [
        dcc.Location(id = "url"),
        dbc.Row(
            [
                dbc.Col(
                    sidebar,
                    width=2
                ),
                dbc.Col(
                    content,
                    width=9, 
                    style = {"margin-left": "19rem"}
                )
            ]
        )
    ],
    fluid=True
) 

######
@contextmanager
def change(path):
    try:
        f = open(path, "w")
        base = sys.stdout
        sys.stdout = f
        yield
    finally:
        sys.stdout = base
######

# Définition d'un callback pour ajouter ou supprimer un slider
@app.callback(
    [
        # Output(component_id="slider-top", component_property="children"),
        Output(component_id="slider-top", component_property="style")
    ],
    [Input(component_id="url", component_property="pathname")]
)
def add_slider(pathname):
    '''Cette fonction renvoie une marge pour le slider et le rend visible si les utilisateur 
    accéde à la page 8 ou 9, sinon elle rend invisible le slider
    Args:
        pathname(str): contient le chemin d'accés 
    Returns:
        style du slider
    '''
    if pathname == "/page-8" or pathname == "/page-9":
        return [
            {"margin": "1rem"}
        ]
    return [
            {"display": "none"}
        ]

# Définition des callbacks pour la résolution des questions
@app.callback(
    Output(component_id="principal-content", component_property="children"),
    [
        Input(component_id="url", component_property="pathname"),
        Input(component_id="date-picker", component_property="start_date"),
        Input(component_id="date-picker", component_property="end_date"),
        Input(component_id="pays", component_property="value"),
        Input(component_id="choose-number", component_property="value")
    ]
)
def add_response(pathname, start_date, end_date, pays, top):
    ''' Fonction qui renvoie une réponse à une question selon le pathname donné en entrée.
    Args:
        pathname(str): Contient le chemin d'accés 
        start_date(str): La date de départ
        end_date(str): La date de fin
        pays(str ou list): Contient le pays ou les pays qui est/sont recherchés dans le dataset
        top(int): Définit le numéro du top des pays à afficher dans les pages 8 et 9
    '''
    if pays:
        
        # Filtrage des données par dates et par pays avant de retourner les résultats
        # en fonction du pathname
        if not type(pays) is list:
            pays = [pays] 
        df = df_covid.loc[start_date:end_date]
        df = df[df["countryName"].isin(pays)]
        
        if pathname == "/":
            # Calcul du nombre total de cas enregistré
            total_cas = df["Cas"].sum()
            
            # Création d'un div qui va afficher le nombre total de cas
            div = html.Div(
                [
                    html.Label("Nombre total de cas"),
                    html.P(total_cas, className="display-5")
                ],
                className="text-center"
            )
            
            # Retournons le résultat
            return div
        
        elif pathname == "/page-1":
            # Calcul du nombre total de morts enregistré
            total_morts = df["Morts"].sum()
            
            # Création d'un div qui va afficher le nombre total de morts
            div = html.Div(
                [
                    html.Label("Nombre total de morts"),
                    html.P(total_morts, className="display-5")
                ],
                className="text-center"
            )
            
            # Retournons le résultat
            return div
        
        elif pathname == "/page-2": 
            pass
            # Ré-echantillonnage du dataset par mois puis calcul du nombre de cas par mois
            
            # Création d'une colonne qui va contenir les mois en chaine de caractères grâce
            # à l'attribut month de datetime et à la liste créée en début de script
            
            # Création d'un bar chart du nombre de cas par mois
        
            # Changeons le titre de l'axe des ordonnées    
            
            # Placons le titre de la figure au milieu
            
            # Retournons le résultat
        
        elif pathname == "/page-3":
            pass
            # Ré-echantillonnage du dataset par mois puis calcul du nombre de morts par mois
            
            # Création d'une colonne qui va contenir les mois en chaine de caractères grâce
            # à l'attribut month de datetime et à la liste créée en début de script
            
            # Création d'un bar chart du nombre de morts par mois
            
            # Changeons le titre de l'axe des ordonnées    
            
            # Placons le titre de la figure au milieu
            
            # Retournons le résultat 
        
        elif pathname == "/page-4":
            pass
            # Ré-echantillonnage du dataset par jour puis calcul du nombre de morts par mois
            # Cela n'est pas nécessaire mais c'est pour la précision du traitement que l'on veut 
            # effectuer
            
            # Création d'un line chart ou courbe du nombre de cas par jour
            
            # Changeons le titre de l'axe des ordonnées    
            
            # Placons le titre de la figure au milieu
            
            # Retournons le résultat 
        
        elif pathname == "/page-5":
            pass
            # Ré-echantillonnage du dataset par mois puis calcul de la somme des cas par mois
            
            # Cumul des cas et affectation à la colonne Cas
            
            # Création d'une colonne qui va contenir les mois en chaine de caractères grace
            # à l'attribut month de datetime et à la liste créée en début de script
            
            # Création d'un line chart ou courbe de la somme cumulée du nombre de cas par mois
            
            # Changeons le titre de l'axe des ordonnées    
            
            # Placons le titre de la figure au milieu
            
            # Retournons le résultat 
        
        elif pathname == "/page-6":
            pass
            # Ré-echantillonnage du dataset par mois puis calcul de la somme des morts par mois
            
            # Cumul des morts et affectation à la colonne Morts
            
            # Création d'une colonne qui va contenir les mois en chaine de caractères grace
            # à l'attribut month de datetime et à la liste créée en début de script
            
            # Création d'un line chart ou courbe de la somme cumulée du nombre de morts par mois
            
            # Changeons le titre de l'axe des ordonnées    
            
            # Placons le titre de la figure au milieu
            
            # Retournons le résultat 
        
        elif pathname == "/page-7":
            pass            
            # Ré-echantillonnage du dataset par jour puis détermination du nombre de morts par jour
            # Cela n'est pas nécessaire mais c'est pour la précision de ce que l'on veut traiter
            
            # Création d'un line chart ou courbe du nombre de morts par jour
            
            # Changeons le titre de l'axe des ordonnées    
            
            # Placons le titre de la figure au milieu
            
            # Retournons le résultat 
        
        elif pathname == "/page-8":
            pass 
            # Détermination du nombre de cas par pays (as_index mis à false nous permet de garder la
            # variable countryName sous forme de colonne)
            
            # Trions les nombres de cas par ordre décroissant
            
            # Prenons le top des pays avec le plus de cas
            
            # Création d'un tableau de données stylisé contenant les colonnes pays et nombre de cas
            
            # Retournons le résultat
        elif pathname == "/page-9":
            pass
            # Détermination du nombre de morts par pays (as_index mis à false nous permet de garder la
            # variable countryName sous forme de colonne)
            
            # Trions les nombres de morts par ordre décroissant
            
            # Prenons le top des pays avec le plus de morts
            
            # Création d'un tableau de données stylisé contenant les colonnes pays et nombre de morts
            
            # Retournons le résultat
        
    # S'il y a un problème alors faisont en sort que la page ne change pas d'aspect   
    raise dash.exceptions.PreventUpdate

# Activons l'application sur le port 4000 
if __name__ == "__main__":
    app.run_server(
        port=4000,
        debug=True
    )