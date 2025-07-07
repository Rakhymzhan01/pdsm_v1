from apps import karatobe_navigation as navigation
from apps import footer
import dash
from dash import dcc, html, callback, Output, Input, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask_login import current_user


dash.register_page(__name__, path='/karatobe/scal')


'''Data-------------------------------------------'''
df_table = pd.read_csv('./assets/karatobe/relative_permeability_table.csv')
df_summary = pd.read_csv('./assets/karatobe/relative_permeability_summary.csv')

wells = ["All"] + df_summary.Well.unique().tolist()
horizons = ["All"] + df_summary.Horizon.unique().tolist()
plugs = ["All"] + df_summary.Plug.unique().tolist()

border = {"border":"1px black solid"}
config = {
    'displayModeBar': True,
    'displaylogo': False,
    # 'doubleClick': 'reset',
    # 'doubleClickDelay': 100,
    # 'edits': {'legendPosition': True, 'titleText': True},
    'scrollZoom': True,
    'modeBarButtonsToRemove': [
        'zoom2d',
        # 'pan2d',
        'select2d',
        'lasso2d',
        'zoomIn2d',
        'zoomOut2d',
        'autoScale2d',
        # 'resetScale2d'

    ],
}

perm_colors = {
        "darkgreen": 4,
        "green": 3,
        "forestgreen": 2,
        "limegreen": 1,
        "lime": 0
}


'''Containers-------------------------------------------'''
plots = dbc.Container([
    dbc.Col([
        dbc.Row([
            dbc.Col(html.Div([
                "Выберите скважину:",
                dcc.Dropdown(id="scal-well-selection", options=wells, value='All', clearable=False)
            ]), width=2),
            dbc.Col(html.Div([
                "Выберите горизонт:",
                dcc.Dropdown(id="scal-horizon-selection", options=horizons, value='All', clearable=False)
            ]), width=2)
        ], justify="center"),
        dbc.Row([
            dbc.Col([
                dcc.Loading(type="default",
                            children=dcc.Graph(
                                id='scal-plot',
                                config=config)
                            )
            ], width=10, style=border)
        ], justify="center")
    ], width={"size": 10, "offset": 1}),


], fluid=True)


'''Layout-----------------------------------------------'''
def layout():
    if not current_user.is_authenticated:
        return html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col([
                    "Please ", dcc.Link("login", href="/"), " to continue"
                ], width={"size": 6, "offset": 3})
            ], align="center")
        ])
    elif current_user.user_level.split('_')[0] in ["master", "all", "karatobe"]:
        return html.Div([
            dcc.Interval(id='interval_pg_scal', interval=86400000 * 7, n_intervals=0),
            dcc.Store(id='screen_scal', storage_type='memory'),
            navigation.navbar,
            plots,
            footer.footer
        ])
    else:
        return html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col([
                    "Вы не авторизованы для просмотра этой страницы. Пожалуйста, ", dcc.Link("войдите", href="/"), " другой учетной записью."
                ], width={"size": 6, "offset": 3})
            ], align="center")
        ])


'''Callbacks--------------------------------------------'''
clientside_callback(
    """
    function(n_intervals) {
        var w = window.innerWidth;
        var h = window.innerHeight;
        return {'height': h, 'width': w};
    }
    """,
    Output('screen_scal', 'data'),
    Input('interval_pg_scal', 'n_intervals')
)


@callback(
    Output('scal-plot', 'figure'),
    Input('scal-well-selection', 'value'),
    Input('scal-horizon-selection', 'value'),
    Input('screen_scal', 'data')
)
def update_wells_logs(well, horizon, screen):
    if well != "All" and horizon != "All":
        df_summary_well_horizon = df_summary[(df_summary.Well == well) & (df_summary.Horizon == horizon)].copy()
    elif well != "All" and horizon == "All":
        df_summary_well_horizon = df_summary[df_summary.Well == well].copy()
    elif well == "All" and horizon != "All":
        df_summary_well_horizon = df_summary[df_summary.Horizon == horizon].copy()
    else:
        df_summary_well_horizon = df_summary.copy()
    df_summary_well_horizon.sort_values(by=['Kl'], ascending=True, inplace=True)

    fig = go.Figure()
    for index, row in df_summary_well_horizon.iterrows():
        try:
            df_ = df_table[(df_table.Well == row.Well) & (df_table.Plug == row.Plug)]
            well = row.Well
            plug = row.Plug
            perm = round(df_summary[(df_summary.Plug == plug) & (df_summary.Well == well)]["Kl"].values[0], 1)
            depth = round(df_summary[(df_summary.Plug == plug) & (df_summary.Well == well)]["Depth"].values[0], 1)
            horizon = df_summary[(df_summary.Plug == plug) & (df_summary.Well == well)]["Horizon"].values[0]
            color, _ = min(perm_colors.items(), key=lambda x: abs(math.log(perm, 10) - x[1]))


            fig.add_trace(
                go.Scatter(
                    x=df_["Sw"],
                    y=df_["Kro"],
                    mode='lines', line=dict(color=color),
                    legendgroup=plug,
                    name=str(well) + " " + str(horizon) + " " + str(plug) + " " + str(perm) + "mD / " + str(depth) + "m"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df_["Sw"],
                    y=df_["Krw"],
                    mode='lines', line=dict(color="blue"),
                    legendgroup=plug,
                    name=plug,
                    showlegend=False,
                )
            )
        except Exception as error:
            print("An exception occurred:", error)

        fig.update_layout(title_text="Relative Permeability", title_x=0.5, font=dict(size=18), height=(screen['height']-175))
        fig.update_xaxes(title_text="Sw", range=[0, 100])
        fig.update_yaxes(title_text="Kr", range=[0, 1])

    return fig


