from apps import karatobe_navigation as navigation
from apps import footer
from dash import dcc, html, callback, Output, Input, register_page, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
from flask_login import current_user


register_page(__name__, path='/karatobe/dash')


'''Data-------------------------------------------------'''
df_faults = pd.read_csv('./assets/karatobe/Faults.csv')
border = {"border": "1px black solid"}
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
        'autoScale2d',
        'resetScale2d'
    ]
}


'''Containers-------------------------------------------'''
plots = dbc.Container([
    dbc.Col([
        dbc.Row([
            # Bubble Map
            dbc.Col(children=dcc.Loading(type="default",
                                         children=dcc.Graph(id='bubble-cum-fig', className="h-100",
                                                            config=config)
                                         ), xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, style=border),
            # Heat Map
            dbc.Col(children=dcc.Loading(type="default",
                                         children=dcc.Graph(id='heat-plot-fig', className="h-100",
                                                            config=config)
                                         ), xs=12, sm=12, md=8, lg=8, xl=8, xxl=8, style=border)
        ], align="center"),
        dbc.Row([
            # Prediction CheckBox
            dbc.Col(
                [
                    # dcc.Checklist(id='forecast', options=['План'], labelStyle={'display': 'inline-block'}),
                    dcc.Checklist(
                        id='forecast',
                        options=[
                            {
                                "label": [
                                    html.Img(src="/assets/karatobe/forecast.png", height=50),
                                    # html.Span("План", style={"font-size": 15, "padding-left": 10}),
                                ],
                                "value": "План",
                            },
                        ],
                        className="text-center mt-2 mb-2",
                        labelStyle={"display": "flex", "align-items": "center"},
                    )
                ],
                # style=border,
                width={"size": 4, "offset": 4}
            )
        ], align="center"),
        dbc.Row([
            # Line Plot
            dbc.Col(dcc.Loading(type="default",
                                children=dcc.Graph(id='line-fig', className="h-100",
                                                   config=config)
                                ), style=border),
        ], align="center")
    ], align="center")
], fluid=True)


'''Layout-----------------------------------------------'''
def layout():
    if not current_user.is_authenticated:
        return html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col([
                    "Пожалуйста, ", dcc.Link("войдите", href="/"), ", чтобы продолжить"
                ], width={"size": 6, "offset": 3})
            ], align="center")
        ])
    elif current_user.user_level.split('_')[0] in ["master", "all", "karatobe"]:
        return html.Div([
            dcc.Interval(id='interval_pg_dashboard', interval=86400000 * 7, n_intervals=0),
            dcc.Store(id='prod_data_dashboard', storage_type='memory'),
            dcc.Store(id='inj_data_dashboard', storage_type='memory'),
            dcc.Store(id='screen_dashboard', storage_type='memory'),
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
    Output('screen_dashboard', 'data'),
    Input('interval_pg_dashboard', 'n_intervals')
)


@callback(
    Output('prod_data_dashboard', 'data'),
    Output('inj_data_dashboard', 'data'),
    Output('bubble-cum-fig', 'figure'),
    Output('heat-plot-fig', 'figure'),
    Input('screen_dashboard', 'data')
)
def get_prod_well_data_dashboard(screen):
    con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
    cur = con.cursor()

    """Get Prod Data"""
    if True:
        query = 'SELECT "Date", "well", "Horizon", "Ql_m3", "Qw_m3", "Qo_ton", "Qi_m3"  FROM prod'
        cur.execute(query)
        df_prod = cur.fetchall()
        prod_columns = ['Дата', 'Скв', 'Объект', 'Qж. м3/сут', 'Qв. м3/сут', 'Qн. тн/сут', 'Qпр. м3/сут']
        df_prod = pd.DataFrame(df_prod, columns=prod_columns)

        df_prod['Дата'] = pd.to_datetime(df_prod['Дата'], format="%Y-%m-%d")
        string_columns = ['Скв', 'Объект']
        df_prod[string_columns] = df_prod[string_columns].astype(str)
        float_columns = ['Qж. м3/сут', 'Qв. м3/сут', 'Qн. тн/сут', 'Qпр. м3/сут']
        df_prod[float_columns] = df_prod[float_columns].astype(float)
        df_prod.sort_values(by='Дата', inplace=True)
        df_prod['Обв. %'] = 100 * df_prod['Qв. м3/сут'].div(df_prod['Qж. м3/сут']).replace(np.inf, 0)
        df_prod[['Обв. %']] = df_prod[['Обв. %']].round(1)
        df_prod.sort_values(by='Дата', inplace=True)

    """Get Wells Data"""
    if True:
        cur.execute('SELECT * FROM wells')
        df_wells = cur.fetchall()
        wells_column = ['Скв', 'x', 'y', 'lat', 'lon', 'hor', 'year']
        df_wells = pd.DataFrame(df_wells, columns=wells_column)
        float_columns = ['x', 'y', 'lat', 'lon']
        df_wells[float_columns] = df_wells[float_columns].astype(float)

    con.close()

    """Cumulative Bubble Map"""
    if True:
        """Cumulative Bubble Map"""
        if True:
            df_prod_bubble = df_prod[['Скв', 'Qж. м3/сут', 'Qв. м3/сут', 'Qпр. м3/сут']]
            df_prod_bubble = df_prod_bubble.groupby(['Скв']).sum()
            df_prod_bubble['Обв. %'] = 100 * df_prod_bubble['Qв. м3/сут'].div(df_prod_bubble['Qж. м3/сут']).replace(np.inf,
                                                                                                                    0)
            df_prod_bubble.reset_index()
            df_prod_bubble.rename(columns={"Qж. м3/сут": 'Qж. м3', "Qв. м3/сут": 'Qв. м3', "Qпр. м3/сут": 'Qпр. м3'},
                                  inplace=True)
            df_prod_bubble[['Обв. %', 'Qж. м3', 'Qв. м3', 'Qпр. м3']] = df_prod_bubble[
                ['Обв. %', 'Qж. м3', 'Qв. м3', 'Qпр. м3']].round(1)
            df_prod_bubble = pd.merge(df_prod_bubble, df_wells, on='Скв', how='inner')
            bubble_cum = go.Figure()
            bubble_cum.add_trace(go.Scatter(name='Нефть', x=df_prod_bubble["x"], y=df_prod_bubble["y"],
                                            mode='markers',
                                            marker=dict(color='green', size=df_prod_bubble["Qж. м3"], sizemode='area',
                                                        sizeref=2. * max(df_prod_bubble["Qж. м3"]) / (30. ** 2)),
                                            showlegend=False,
                                            hovertemplate=
                                            '<b>Скважина</b>: <i>%{text}</i><br>' +
                                            '<b>Qж. м3</b>: <i>%{marker.size}</i><br>' +
                                            '<b>Обв. %</b>: <i>%{customdata}</i><br>',
                                            text=df_prod_bubble["Скв"],
                                            customdata=df_prod_bubble["Обв. %"],
                                            ))
            bubble_cum.add_trace(go.Scatter(name='Вода', x=df_prod_bubble["x"], y=df_prod_bubble["y"],
                                            mode='markers',
                                            marker=dict(color='blue', size=df_prod_bubble["Qв. м3"], sizemode='area',
                                                        sizeref=2. * max(df_prod_bubble["Qж. м3"]) / (30. ** 2)),
                                            showlegend=False,
                                            hoverinfo='none',
                                            ))
            bubble_cum.add_trace(go.Scatter(name='Закачка', x=df_prod_bubble["x"], y=df_prod_bubble["y"],
                                            mode='markers',
                                            marker=dict(color='olive', size=df_prod_bubble["Qпр. м3"], sizemode='area',
                                                        sizeref=2. * max(df_prod_bubble["Qпр. м3"]) / (30. ** 2)),
                                            showlegend=False,
                                            hoverinfo='none',
                                            hovertemplate=
                                            '<b>Скважина</b>: <i>%{text}</i><br>' +
                                            '<b>Qпр. м3</b>: <i>%{marker.size}</i><br>',
                                            text=df_prod_bubble["Скв"]
                                            ))

        """Faults"""
        if True:
            for pol in df_faults['polygon'].unique():
                df_fault = df_faults[df_faults['polygon'] == pol]
                bubble_cum.add_trace(go.Scatter(x=df_fault["x"], y=df_fault["y"],
                                                 mode='lines',
                                                 line=dict(color='firebrick', width=1),
                                                 showlegend=False,
                                                 hoverinfo='none'
                                                 ))

        """Well Anotation"""
        if True:
            for horizon in sorted(df_wells['hor'].unique()):
                if horizon == 'Консв':
                    df_short = df_wells[df_wells['hor'] == horizon]
                    bubble_cum.add_trace(go.Scatter(name=horizon, x=df_short["x"], y=df_short["y"],
                                                    legendrank=4,
                                                    visible='legendonly',
                                                    mode='markers+text',
                                                    marker_symbol='x',
                                                    marker_color='black',
                                                    hoverinfo='none',
                                                    text=df_short["Скв"],
                                                    textposition="top center",
                                                    textfont=dict(family="sans serif", size=16, color="black"),
                                                    ))
                elif horizon == 'Бурен':
                    df_short = df_wells[df_wells['hor'] == horizon]
                    bubble_cum.add_trace(go.Scatter(name=horizon, x=df_short["x"], y=df_short["y"],
                                                    legendrank=3,
                                                    mode='markers+text',
                                                    marker_symbol='circle',
                                                    marker_color='red',
                                                    hoverinfo='none',
                                                    text=df_short["Скв"],
                                                    textposition="top center",
                                                    textfont=dict(family="sans serif", size=16, color="red"),
                                                    ))
                elif horizon in ['J1-IV', 'V-J2', 'P&T', 'P2-I']:
                    df_short = df_wells[df_wells['hor'] == horizon]
                    bubble_cum.add_trace(go.Scatter(name=horizon, x=df_short["x"], y=df_short["y"],
                                                    legendrank=1,
                                                    mode='text',
                                                    hoverinfo='none',
                                                    text=df_short["Скв"],
                                                    textposition="top center",
                                                    textfont=dict(family="sans serif", size=16, color="crimson"),
                                                    ))
                else:
                    df_short = df_wells[df_wells['hor'] == horizon]
                    bubble_cum.add_trace(go.Scatter(name=horizon, x=df_short["x"], y=df_short["y"],
                                                    legendrank=1,
                                                    visible='legendonly',
                                                    mode='text',
                                                    hoverinfo='none',
                                                    text=df_short["Скв"],
                                                    textposition="top center",
                                                    textfont=dict(family="sans serif", size=16, color="orange"),
                                                    ))

        """Layout"""
        if True:
            bubble_cum.update_layout(title_text="<b>Карта Накопленных Отборов</b>", title_x=0.5, title_font=dict(size=16),
                                     yaxis_title=None, xaxis_title=None,
                                     yaxis_range=[5306000, 5309500], xaxis_range=[465000, 468000],
                                     margin=dict(l=0, r=0, t=40, b=0),
                                     paper_bgcolor="white",
                                     plot_bgcolor="white",
                                     legend=dict(
                                         orientation="h",
                                         itemwidth=70,
                                         yanchor="bottom",
                                         y=0.02,
                                         xanchor="right",
                                         x=1
                                     ),
                                     hovermode='closest',
                                     autosize=False,
                                     height=int((screen['height'] - 50) / 2.25)
                                     )
            bubble_cum.update_yaxes(showticklabels=False, showgrid=False)
            bubble_cum.update_xaxes(showticklabels=False, showgrid=False)

    """HeatPlot"""
    if True:
        df_prod_heat = df_prod[['Дата', 'Скв', 'Qн. тн/сут']]
        df_prod_heat = df_prod_heat.pivot_table(index='Скв', columns='Дата', values='Qн. тн/сут', aggfunc='sum')
        df_prod_heat.replace(0, np.nan, inplace=True)
        df_prod_heat.dropna(axis=0, how="all", inplace=True)
        df_prod_heat.sort_values(df_prod_heat.columns[-1], ascending=False, inplace=True)

        heatmap = px.imshow(df_prod_heat, range_color=[0, 50], labels=dict(x=None, y=None, color="Qн. тн/сут"),
                            # color_continuous_scale="RdBu_r", color_continuous_midpoint=30
                            )
        heatmap.update_layout(title_text="<b>Тепловая карта Скважин</b>", title_x=0.5, title_font=dict(size=16),
                              yaxis=dict(tickfont=dict(size=10)),
                              margin=dict(l=10, r=10, t=40, b=20),
                              paper_bgcolor="white",
                              # width=750,
                              height=int((screen['height'] - 50) / 2.25),
                              xaxis_title=None,
                              yaxis_title=None
                              )
        heatmap.update_xaxes(
            tickfont=dict(size=12),
            ticks="outside",
            dtick="M1",
            tickformat="%b\n%Y",
        )

    """Data for Line Plot"""
    df_prod_field = df_prod[['Дата', 'Скв', 'Qж. м3/сут', 'Qн. тн/сут', 'Qв. м3/сут']]
    df_prod_field = df_prod_field[df_prod_field["Qж. м3/сут"] > 0]
    df_prod_field = df_prod_field.groupby(['Дата']).agg(
        {'Скв': 'count', 'Qж. м3/сут': 'sum', 'Qн. тн/сут': 'sum', 'Qв. м3/сут': 'sum'})
    df_prod_field.reset_index(inplace=True)
    df_prod_field['Обв. %'] = 100 * df_prod_field['Qв. м3/сут'].div(df_prod_field['Qж. м3/сут']).replace(np.inf, 0)
    df_prod_field[['Обв. %', 'Qн. тн/сут', 'Qж. м3/сут']] = df_prod_field[
        ['Обв. %', 'Qн. тн/сут', 'Qж. м3/сут']].round(1)

    df_inj_field = df_prod[['Дата', 'Скв', 'Qпр. м3/сут']].copy()
    df_inj_field = df_inj_field[df_inj_field["Qпр. м3/сут"] > 0]
    df_inj_field = df_inj_field.groupby(['Дата']).agg({'Скв': 'count', 'Qпр. м3/сут': 'sum'})
    df_inj_field.reset_index(inplace=True)

    return [df_prod_field.to_dict('records'), df_inj_field.to_dict('records'), bubble_cum, heatmap]


@callback(

    Output('line-fig', 'figure'),
    Input('prod_data_dashboard', 'data'),
    Input('inj_data_dashboard', 'data'),
    Input('forecast', 'value'),
    Input('screen_dashboard', 'data')
)
def update_dashboard_plots(production, injection, forecast, screen):
    df_prod_field = pd.DataFrame(production)
    df_prod_field['Дата'] = pd.to_datetime(df_prod_field['Дата'])

    df_inj_field = pd.DataFrame(injection)
    df_inj_field['Дата'] = pd.to_datetime(df_inj_field['Дата'])

    line = go.Figure()

    '''Add Prod Data'''
    if True:
        line.add_trace(
            go.Scatter(
                x=df_prod_field['Дата'],
                y=df_prod_field['Qн. тн/сут'],
                mode='lines',
                name='Qн. тн/сут',
                line=dict(color='darkgreen', width=4)
            ),

        )
        line.add_trace(
            go.Scatter(
                x=df_prod_field['Дата'],
                y=df_prod_field['Qж. м3/сут'],
                mode='lines',
                name='Qж. м3/сут',
                line=dict(color='black', width=4),
                visible='legendonly'
            )
        )
        line.add_trace(
            go.Scatter(
                x=df_inj_field['Дата'],
                y=df_inj_field['Qпр. м3/сут'],
                mode='lines',
                name='Qпр. м3/сут',
                line=dict(color='olive', width=4),
                visible='legendonly'
            )
        )
        line.add_trace(
            go.Scatter(
                x=df_prod_field['Дата'],
                y=df_prod_field['Обв. %'],
                mode='lines',
                name='Обв. %',
                line=dict(color='blue', width=4),
                yaxis="y2"
            )
        )
        line.add_trace(
            go.Bar(
                x=df_prod_field['Дата'],
                y=df_prod_field['Скв'],
                name='Кол.скв.',
                opacity=0.4,
                marker_color='crimson',
                text=df_prod_field['Скв'],
                textfont=dict(size=12, color="black"),
                yaxis="y2"
            )
        )

        if forecast:
            line.add_trace(go.Scatter(
                x=[datetime.date(2023, i, 15) for i in range(1, 13)],
                y=[332, 344, 335, 376, 372, 367, 398, 406, 415, 394, 394, 379],
                mode='markers+lines',
                name='I-вариант - с бурением',
                line=dict(color='lightgreen', width=4, dash='dash'),
                visible='legendonly'
            ))
            line.add_trace(go.Scatter(
                x=[datetime.date(2023, i, 15) for i in range(1, 13)],
                y=[323, 307, 281, 308, 310, 322, 334, 339, 330, 315, 328, 305],
                mode='markers+lines',
                name='115 тыс.т/год',
                line=dict(color='darkgreen', width=4, dash='dash'),
                visible='legendonly'
            ))
            line.add_trace(go.Scatter(
                x=[datetime.date(i, 12, 31) for i in range(2023, 2046)],
                y=[398.9, 517.6, 732.1, 662.2, 564.8, 485, 426.5, 382, 342, 306.6, 274.2, 243.4, 213.1, 181.6, 152.3,
                   123.3, 100.8, 77.1, 62.8, 54.1, 48.3, 42.8, 38.3],
                mode='markers+lines',
                name='План',
                line=dict(color='darkgreen', width=4, dash='dash')
            ))
            range_ = [min(df_prod_field['Дата']) - datetime.timedelta(days=1), datetime.date(2045, 12, 31)]
        else:
            range_ = [min(df_prod_field['Дата']) - datetime.timedelta(days=1),
                      max(df_prod_field['Дата']) + datetime.timedelta(days=1)]

    '''Update Layout'''
    if True:
        line.update_layout(
            title=dict(text="<b>История Добычи м. Каратюбе</b>", x=0.5, font_size=16),
            margin=dict(l=80, r=60, t=40, b=20),
            paper_bgcolor="white",
            plot_bgcolor="white",
            height=int((screen['height'] - 50) / 2.25),
            autosize=True,
            xaxis=dict(
                anchor='y',
                range=range_,
                tickfont=dict(size=14),
                ticks="outside",
                tickformatstops=[
                    dict(dtickrange=[None, "M1"], value="%e\n%b, %Y"),
                    dict(dtickrange=["M1", "M12"], value="%b\n%Y"),
                    dict(dtickrange=["M12", None], value="%Y")
                ]
            ),
            yaxis=dict(
                anchor="x",
                range=[0, 2000],
                title=dict(
                    text="<b>Qт/сут; Qж/сут; Qпр/сут</b>",
                    font=dict(size=14, color="black")
                ),
                tickfont=dict(size=14, color="black")),
            yaxis2=dict(
                anchor="x",
                overlaying="y",
                side="right",
                range=[0, 100],
                showgrid=False,
                title=dict(
                    text="<b>Обв.% / Кол.скв</b>",
                    font=dict(size=14, color="black")
                ),
                tickfont=dict(size=14, color="black")),
        )

    return line
