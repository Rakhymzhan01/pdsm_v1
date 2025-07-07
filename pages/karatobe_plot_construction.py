from apps import karatobe_navigation as navigation
from apps import footer
from dash import register_page, dcc, html, callback, Output, Input, clientside_callback, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from flask_login import current_user


register_page(__name__, path='/karatobe/construction')


'''Data-------------------------------------------------'''
border = {"border":"1px gray solid"}
config = {
    'displayModeBar': True,
    'displaylogo': False,
    'doubleClick': 'reset',
    # 'doubleClickDelay ': 100,
    # 'edits': {'legendPosition': True, 'titleText': True},
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
}
def drawFigure(fig):
    return html.Div([
        dbc.Card(
            dbc.CardBody(
                [fig]
            )
        )
    ])


'''Containers-------------------------------------------'''
plots = dbc.Container(
    dbc.Col(
        [
            dbc.Row(
                [
                    # Number of Curves
                    dbc.Col([
                        drawFigure(
                            dcc.Dropdown(
                                id='num_curves',
                                options=[1,2,3,4],
                                clearable=False,
                                value=1,
                                placeholder="Выберите количество кривых для отображения:")
                        )
                    ]),

                    # Filters and Curve
                    dbc.Col([
                        drawFigure(dbc.Row(id='filter_selectors')),
                    ])
                ],
                justify="center"
            ),

            # Plot
            dbc.Row(
                [
                    drawFigure(
                        dcc.Loading(
                            type="default",
                            children=dcc.Graph(
                                id='constructed_plot',
                                className="h-100",
                                config=config
                            )
                        )
                    )
                ],
                justify="center"
            )

        ],
        width={"size": 10, "offset": 1}
    ),
    fluid=True
)


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
            dcc.Interval(id='interval_pg_construction', interval=86400000*7, n_intervals=0),
            dcc.Store(id='work_over_data_construction', storage_type='session'),
            dcc.Store(id='completion_data_construction', storage_type='session'),
            dcc.Store(id='screen_construction', storage_type='session'),
            navigation.navbar,
            html.Br(),
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
    Output('screen_construction', 'data'),
    Input('interval_pg_construction', 'n_intervals')
)

@callback(
    Output('filter_selectors', 'children'),
    Input('num_curves', 'value')
)
def filter_selectors(num_curves):
    filter_selectors = []
    for i in range(num_curves):
        filter_selectors.append(
            dbc.Row([
                    dcc.Dropdown(
                        id={'type': 'horizon_filter_dropdown', 'index': i},
                        options=[
                            {'label': 'Всё', 'value': 'Всё'},
                            {'label': 'Сред. Юра', 'value': 'J2'},
                            {'label': 'Нижн. Юра', 'value': 'J1'},
                            {'label': 'Пермо-Триас', 'value': 'PT'}
                         ],
                        value='Всё',
                        clearable=False)
            ])
        )
    return filter_selectors


"""Plot Production"""
def plot_production(horizon_filter_dropdown_values, screen):

    curve_counts = len(horizon_filter_dropdown_values)
    colors = {'Всё': 'darkgreen',
              'J2': 'purple',
              'J1': 'darkred',
              'PT': 'navy'}
    fig = go.Figure()

    con = psycopg2.connect(
        host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030"
    )
    cur = con.cursor()

    for i in range(curve_counts):

        horizon = horizon_filter_dropdown_values[i]

        if horizon == "Всё":
            title = "Совокупная добыча месторождения"
            cur.execute("""
                SELECT "Date", SUM("Qo_ton") AS Qo_ton, SUM("Ql_m3") AS Ql_m3, SUM("Qo_m3") AS Qo_m3, SUM("Qw_m3") AS Qw_m3
                FROM prod
                GROUP BY "Date"
                ORDER BY "Date"
            """)
        elif horizon == "PT":
            title = "Пермо-Триас"
            cur.execute("""
                select "Date", SUM("Qo_ton") AS Qo_ton, SUM("Ql_m3") AS Ql_m3, SUM("Qo_m3") AS Qo_m3, SUM("Qw_m3") AS Qw_m3
                from prod
                where "Horizon" like %s or "Horizon" like %s
                group by "Date"
                order by "Date"
            """, ("%P%", "%T%"))
        else:
            if horizon == "J1":
                title = "Нижняя Юра"
            elif horizon == "J2":
                title = "Средняя Юра"
            cur.execute("""
                select "Date", SUM("Qo_ton") AS Qo_ton, SUM("Ql_m3") AS Ql_m3, SUM("Qo_m3") AS Qo_m3, SUM("Qw_m3") AS Qw_m3
                from prod
                where "Horizon" like %s
                group by "Date"
                order by "Date"
            """, ("%"+horizon+"%", ))


        df = cur.fetchall()
        prod_columns = ['Дата', 'Qн. тн/сут', 'Qж. м3/сут', 'Qн. м3/сут', 'Qв. м3/сут']
        df = pd.DataFrame(df, columns=prod_columns)
        # df['Обв. %'] = 100 * df['Qв. м3/сут'].div(df['Qж. м3/сут']).replace(np.inf, 0)
        # df[['Обв. %']] = df[['Обв. %']].round(1)

        fig.add_trace(
            go.Scatter(
                name=title,
                x=df["Дата"], y=df["Qн. тн/сут"],
                mode='lines',
                line=dict(color=colors[horizon], width=3)
            )
        )

    fig.update_layout(
        # title=dict(text="<b>Qн. тн/сут<b>", font_size=16, x=0.5),
        # margin=dict(l=0, r=0, t=40, b=0),
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h"
        ),
        height=(screen['height'] - 350),
        hovermode="x",
        xaxis=dict(
            tickfont=dict(size=14),
            ticks="outside",
            tickformatstops=[
                dict(dtickrange=[None, "M1"], value="%e\n%b, %Y"),
                dict(dtickrange=["M1", "M12"], value="%b\n%Y"),
                dict(dtickrange=["M12", None], value="%Y")
            ]
        ),
        yaxis=dict(
            title=dict(
                text="<b>Qн. тн/сут</b>",
                font=dict(size=14, color="black")
            ),
            tickfont=dict(size=14, color="black")),
    )

    con.close()

    # '''Add Prod Data'''
    # if True:
    #     fig.add_trace(
    #         go.Scatter(
    #             name="Qн. тн/сут",
    #             x=df_prod_well["Дата"], y=df_prod_well["Qн. тн/сут"],
    #             mode='lines', line=dict(color="darkgreen", width=3)
    #         )
    #     )
    #     fig.add_trace(
    #         go.Scatter(
    #             name="Qж. м3/сут",
    #             x=df_prod_well["Дата"], y=df_prod_well["Qж. м3/сут"],
    #             mode='lines', line=dict(color="black", width=3), visible="legendonly"
    #         )
    #     )
    #     fig.add_trace(
    #         go.Scatter(
    #             name="Обв. %",
    #             x=df_prod_well["Дата"], y=df_prod_well["Обв. %"],
    #             mode='lines', line=dict(color="blue", width=3)
    #         )
    #     )
    #     fig.add_trace(
    #         go.Scatter(
    #             name="Ндин. м",
    #             x=df_prod_well["Дата"], y=df_prod_well["Ндин. м"],
    #             mode='lines', line=dict(color="maroon", width=3),
    #             yaxis="y2"
    #         )
    #     )
    #     fig.add_trace(
    #         go.Scatter(
    #             name="об/мин",
    #             x=df_prod_well["Дата"], y=df_prod_well["об/мин"],
    #             mode='lines', line=dict(color="orange", width=3), visible="legendonly",
    #             yaxis="y4"
    #         )
    #     )
    #
    # '''Update Layout'''
    # if True:
    #     fig.update_layout(
    #         title=dict(text="Добыча скважины <b>"+well+"<b>", font_size=16, x=0.5),
    #         margin=dict(l=60, r=20, t=40, b=20),
    #         template='plotly_white',
    #         height=(screen['height']-100)//2,
    #         xaxis=dict(
    #             anchor='y',
    #             domain=[0.0, 0.95],
    #             tickfont=dict(size=14),
    #         ),
    #         yaxis=dict(
    #             title=dict(text="Qн; Qж; Обводненность", font=dict(color="black", size=15)),
    #             tickfont=dict(color="black", size=14),
    #             anchor="x",
    #             range=[0, 100]
    #         ),
    #         yaxis2=dict(
    #             title=dict(text="Ндин", font=dict(color="maroon", size=15)),
    #             tickfont=dict(color="maroon", size=14),
    #             anchor="x",
    #             overlaying="y",
    #             side="right",
    #             range=[1000, 0],
    #             showgrid=False
    #         ),
    #         yaxis4=dict(
    #             title=dict(text="об/мин", font=dict(color="orange", size=15)),
    #             tickfont=dict(color="orange", size=14),
    #             anchor="free",
    #             overlaying="y",
    #             side="right",
    #             position=1,
    #             range=[0, 500],
    #             showgrid=False
    #         ),
    #     )

    return fig

@callback(
    Output('constructed_plot', 'figure'),
    Input({'type': 'horizon_filter_dropdown', 'index': ALL}, 'value'),
    Input('screen_construction', 'data')
)
def construct_plot(horizon_filter_dropdown_values, screen):
    return plot_production(horizon_filter_dropdown_values, screen)