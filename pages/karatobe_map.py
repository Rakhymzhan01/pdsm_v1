from apps import karatobe_navigation as navigation
from apps import footer
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, callback, Output, Input, clientside_callback, register_page
import dash_bootstrap_components as dbc
import psycopg2
from flask_login import current_user

register_page(__name__, path='/karatobe/map')


'''Data-------------------------------------------------'''


border = {"border": "1px gray solid"}
config = {
    'displayModeBar': True,
    'displaylogo': False,
    'doubleClick': 'reset',
    # 'doubleClickDelay ': 100,
    # 'edits': {'legendPosition': True, 'titleText': True},
    'scrollZoom': True,
    'modeBarButtonsToRemove': [
        'zoom2d',
        # 'pan2d',
        'select2d',
        'zoomIn2d',
        'zoomOut2d',
        # 'autoScale2d',
        'resetScale2d',
        'lasso'
    ],
}


'''Containers-------------------------------------------'''
plots = dbc.Container(
    dbc.Col([
        dbc.Row([
            dcc.RadioItems(
                id='map_selector',
                options=['MapBox', 'XII a', 'XI1 br', 'XI br', 'X br', 'IX br', 'VIII br', 'VII g', 'VI-J2', 'V-J2', 'V1-J2', 'V2-J2', 'V3-J2', 'IV-J1', 'T1-III', 'T1-II', 'I-P2'],
                value='MapBox',
                labelStyle={"margin-left": "20px", "margin-right": "20px"},
                style={'color': 'MediumTurqoise', 'font-size': 20},
                inline=True
            )
        ], justify="center"),
        dbc.Row([
            dcc.Loading(
                type="default",
                children=dcc.Graph(
                    id='fig_map',
                    className="h-100",
                    config=config,
                    style=border
                )
            )
        ], justify="center")
    ]), fluid=True)


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
            dcc.Interval(id='interval_pg_map', interval=86400000*7, n_intervals=0),
            dcc.Store(id='wells_map', storage_type='memory'),
            dcc.Store(id='screen_map', storage_type='memory'),
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
    Output('screen_map', 'data'),
    Input('interval_pg_map', 'n_intervals')
)


@callback(
    Output('wells_map', 'data'),
    Input('interval_pg_map', 'n_intervals')
)
def get_well_data_map(n_intervals):
    con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
    cur = con.cursor()

    """Get Wells Data"""
    if True:
        cur.execute('SELECT * FROM wells')
        df_wells = cur.fetchall()
        wells_column = ['Скв', 'x', 'y', 'lat', 'lon', 'hor', 'year']
        df_wells = pd.DataFrame(df_wells, columns=wells_column)
        float_columns = ['x', 'y', 'lat', 'lon']
        df_wells[float_columns] = df_wells[float_columns].astype(float)

    con.close()
    return df_wells.to_dict('records')


@callback(
    Output('fig_map', 'figure'),
    Input('wells_map', 'data'),
    Input('map_selector', 'value'),
    Input('screen_map', 'data')
)
def plot_map(wells, map_selector, screen):
    df_wells = pd.DataFrame(wells)
    df_boundaries = pd.read_csv('./assets/karatobe/Gornyi_Otvod.csv')

    if map_selector == "MapBox":
        data = []
        try:
            for fld in df_boundaries['contract'].unique():
                df_boundary = df_boundaries[df_boundaries['contract'] == fld]
                first_row = df_boundary.iloc[0]
                df_boundary = pd.concat([df_boundary, pd.DataFrame([first_row])], ignore_index=True)
                if fld == "КТМ":
                    field_color = 'lime'
                else:
                    field_color = 'red'
                dictionary = {
                    'name': fld,
                    'type': "scattermapbox",
                    'mode': "lines",
                    'lat': df_boundary["lat"],
                    'lon': df_boundary["lon"],
                    'line': {'color': field_color, 'width': 3},
                    'hovertemplate': fld,
                }
                data.append(dictionary)
        except Exception as error:
            print("An exception occurred:", error)

        well_colors = ['black', 'yellow', 'orange', 'bisque', 'red', 'snow']
        try:
            for index, hor in enumerate(df_wells['hor'].unique()):
                df_well = df_wells[df_wells['hor'] == hor]
                wells = {
                    'name': hor,
                    'type': "scattermapbox",
                    'mode': "markers+text",
                    'lat': df_well['lat'],
                    'lon': df_well['lon'],
                    'text': df_well['Скв'],
                    'hovertemplate': df_well['Скв'],
                    'textposition': "bottom",
                    'textfont': {'size': 16, 'color': well_colors[index]},
                    'marker': {'size': 10, 'color': well_colors[index]},
                }
                data.append(wells)
        except:
            pass

        layout = {
            'height': (screen['height'] - 170),
            'mapbox': {
                'accesstoken': 'pk.eyJ1IjoiYW1hbjIwMzAiLCJhIjoiY200dGpleDc4MDllZzJrc2Ixd2MxNDYyNiJ9.F99xmm3ea5x_A77MAakFow',
                'center': {'lat': 47.925, 'lon': 56.55},
                'domain': {'x': [0.0, 1.0], 'y': [0.0, 1.0]},
                'style': 'satellite-streets',
                'zoom': 14},
            'legend': {'title': {'text': 'Участок'}, 'yanchor': 'top', 'y': 0.95},
            'margin': {'b': 0, 'l': 0, 'r': 0, 't': 0},
        }

        fig = {'data': data, 'layout': layout}

        return fig

    fig = go.Figure()

    """Well Anotation"""
    if True:
        for year in df_wells['year'].unique():
            df_short = df_wells[(df_wells['year'] == year) & (df_wells['hor'] != "Консв")]
            fig.add_trace(go.Scatter(name=year,
                                     x=df_short["x"], y=df_short["y"],
                                     mode='markers+text',
                                     marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')),
                                     hoverinfo='none',
                                     text=df_short["Скв"],
                                     textposition="top center",
                                     textfont=dict(family="sans serif", size=16, color="black"),
                                     ))

        df_short = df_wells[df_wells['hor'] == "Консв"]
        fig.add_trace(go.Scatter(name="В Консерваций",
                                 x=df_short["x"], y=df_short["y"],
                                 mode='markers+text',
                                 visible='legendonly',
                                 marker=dict(size=12, symbol='x', color='magenta', line=dict(width=2, color='DarkSlateGrey')),
                                 hoverinfo='none',
                                 text=df_short["Скв"],
                                 textposition="top center",
                                 textfont=dict(family="sans serif", size=16, color="black"),
                                 ))

    """Gornyi Otvod"""
    if True:
        for contr in df_boundaries['contract'].unique():
            if contr != "КТМ":
                df_boundary = df_boundaries[df_boundaries['contract'] == contr]
                first_row = df_boundary.iloc[0]
                df_boundary = pd.concat([df_boundary, pd.DataFrame([first_row])], ignore_index=True)
                fig.add_trace(go.Scatter(x=df_boundary["x"], y=df_boundary["y"], name=str(contr),
                                                 mode='lines', line=dict(color='black', width=1),
                                                 # showlegend=False,
                                                 # hoverinfo='none',
                                                 hovertemplate='<b>%{customdata}</b>',
                                                 customdata=df_boundary["contract"],
                                                 ))

    """Add images"""
    if map_selector:
        fig.add_layout_image(
            dict(
                source=f"../assets/karatobe/reserve_maps/{map_selector}.jpg",
                xref="x",
                yref="y",
                x=464882.06,
                y=5309469.65,
                sizex=3541.04,
                sizey=2980.71,
                sizing="stretch",
                opacity=0.75,
                layer="below"
            )
        )

    """Add Logo"""
    if True:
        fig.add_layout_image(
            dict(
                source="../assets/north.png",
                xref="paper", yref="paper",
                x=0.04, y=0.86,
                sizex=0.1, sizey=0.1,
                xanchor="right", yanchor="bottom",
                layer="above"
            )
        )

    """Map Layout"""
    if True:
        showgrid = True
        fig.update_layout(
            title=dict(
                text=f"<b>Подсчетный план {map_selector}, <i>м.Каратобе</i></b>",
                x=0.5,
                font=dict(size=16),
            ),
            xaxis=dict(
                title=None,
                range=[464500, 469000],
                showticklabels=True,
                showgrid=showgrid
            ),
            yaxis=dict(
                title=None,
                range=[5306000, 5310000],
                showticklabels=True,
                showgrid=showgrid,
                scaleanchor="x",
                scaleratio=1
            ),
            legend=dict(
                font_size=20,
                itemwidth=40,
                yanchor="bottom",
                y=0.1,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0)"
            ),
            hovermode='closest',
            autosize=True,
            height=(screen['height'] - 170),
            template="plotly_white",
            margin=dict(l=0, r=0, t=40, b=0),
            # margin=dict(r=20, l=300, b=75, t=125),
        )

    return fig


