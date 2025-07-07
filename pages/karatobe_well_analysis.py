from apps import karatobe_navigation as navigation
from apps import footer
from dash import register_page, dcc, html, callback, Output, Input, clientside_callback, dash_table, ALL, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import lasio, datetime
from os import scandir
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from flask_login import current_user


register_page(__name__, path='/karatobe/analysis')


'''Data-------------------------------------------------'''
jurassic_middle = ['V-J2', 'J2-V']
jurassic_lower = ['IV-J1', 'J1-IV', 'IV-J2']
jurassic = jurassic_middle + jurassic_lower
perm = ["P2"]
trias = ["T1"]

border = {"border": "0px gray solid"}
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
    ],
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
    dbc.Row([
        # Select wells Columns
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    # dbc.Card(
                    #     [
                    #         dbc.CardHeader("Сред. Юра"),
                    #         dbc.CardBody(id='btns-jurassic_middle')
                    #     ]
                    # ),
                    # dbc.Card(
                    #     [
                    #         dbc.CardHeader("Нижн. Юра"),
                    #         dbc.CardBody(id='btns-jurassic_lower')
                    #     ]
                    # ),
                    dbc.Row(html.H6(children=html.B("Сред. Юра"), className="text-center mt-2 mb-2", style={"color": "Purple", "text-decoration": "None",})),
                    dbc.Row(id='btns-jurassic_middle'),
                    dbc.Row(html.H6(children=html.B("Нижн. Юра"), className="text-center mt-2 mb-2", style={"color": "Purple", "text-decoration": "None",})),
                    dbc.Row(id='btns-jurassic_lower'),
                ], width=6),
                dbc.Col([
                    # dbc.Card(
                    #     [
                    #         dbc.CardHeader("Триас"),
                    #         dbc.CardBody(id='btns-trias')
                    #     ]
                    # ),
                    # dbc.Card(
                    #     [
                    #         dbc.CardHeader("Пермь"),
                    #         dbc.CardBody(id='btns-perm')
                    #     ]
                    # ),
                    dbc.Row(html.H6(children=html.B("Триас"), className="text-center mt-2 mb-2", style={"color": "Purple", "text-decoration": "None",})),
                    dbc.Row(id='btns-trias'),
                    dbc.Row(html.H6(children=html.B("Пермь"), className="text-center mt-2 mb-2", style={"color": "Purple", "text-decoration": "None",})),
                    dbc.Row(id='btns-perm'),
                ], width=6)
            ], style={"overflow-y": "scroll", "maxHeight": "calc(100vh - 120px)"}),
        ], xs=12, sm=12, md=6, lg=2, xl=2, xxl=1),

        # Plots
        dbc.Col([
            dbc.Row([
                # Bubble Map
                dbc.Col([
                    dcc.Loading(
                        type="default",
                        children=drawFigure(
                            dcc.Graph(
                                id='bubble-cum-fig2',
                                config=config,
                                style={"height": "calc((100vh - 100px)/2)"}
                            )
                        )
                    )], xs=12, sm=12, md=5, lg=5, xl=5, xxl=5, style=border),

                # Pie Chart
                dbc.Col([
                    dcc.Loading(
                        type="default",
                        children=drawFigure(
                            dcc.Graph(
                                id='pie-chart-fig',
                                config=config,
                                style={"height": "calc((100vh - 100px)/2)"}
                            )
                        )
                        )], xs=12, sm=12, md=2, lg=2, xl=2, xxl=2, style=border),

                # WorkOver Table
                dbc.Col([
                    dcc.Loading(
                        type="default",
                        children=dbc.Card(
                            [
                                dbc.CardHeader(id="wo_tittle"),
                                dbc.CardBody(
                                    dash_table.DataTable(
                                        id='workover_table',
                                        page_action='none',
                                        # page_size=5,
                                        # style_cell={'padding': '5px'},
                                        style_header={'backgroundColor': 'white', 'fontWeight': 'bold'},
                                        style_data={'whiteSpace': 'normal', 'height': 'auto'},
                                        style_data_conditional=[
                                            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'}],
                                        style_cell={'minWidth': 30, 'maxWidth': 300, 'fontSize': 12},
                                        style_table={'maxHeight': "calc((100vh - 180px)/2)"}
                                    )
                                )
                            ]
                        )
                    )
                    ], xs=12, sm=12, md=5, lg=5, xl=5, xxl=5, style=border),
            ]),

            dbc.Row([
                # Line Plot
                dbc.Col(dcc.Loading(type="default",
                                    children=drawFigure(
                                        dcc.Graph(
                                            id='line-fig2',
                                            config=config,
                                            style={"height": "calc((100vh - 290px)/2)"}
                                        )
                                    )), xs=12, sm=12, md=12, lg=12, xl=12, xxl=12, style=border)
            ])
        ], xs=12, sm=12, md=8, lg=7, xl=7, xxl=8),

        # LOG
        dbc.Col([
            # Well Log
            dcc.Loading(
                type="default",
                children=drawFigure(
                    dcc.Graph(
                        id='log-fig2',
                        config=config,
                        style={"height": "calc(100vh - 160px)"}
                    )
                )
            )
        ], xs=12, sm=12, md=3, lg=3, xl=3, xxl=3),

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
            dcc.Interval(id='interval_pg_analysis', interval=86400000*7, n_intervals=0),
            dcc.Store(id='prod_data_analysis', storage_type='memory'),
            dcc.Store(id='selected_well_analysis', storage_type='memory'),
            dcc.Store(id='workovers_analysis', storage_type='memory'),
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
@callback(
    Output('prod_data_analysis', 'data'),

    Output('btns-jurassic_middle', 'children'),
    Output('btns-jurassic_lower', 'children'),
    Output('btns-perm', 'children'),
    Output('btns-trias', 'children'),

    Output('workovers_analysis', 'data'),

    Output('bubble-cum-fig2', 'figure'),
    Input('interval_pg_analysis', 'n_intervals')
)
def get_prod_well_data_analysis(n_intervals):

    """Data"""
    if True:
        con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
        cur = con.cursor()

        """Get Wells List for Each Horizon"""
        if True:
            query = 'SELECT DISTINCT "well", "Horizon" FROM prod;'
            cur.execute(query)
            df_well_list_per_horizon = cur.fetchall()
            df_well_list_per_horizon = pd.DataFrame(df_well_list_per_horizon, columns=['Скв', 'Объект'])

        """Get Prod Data for Last 2 Days"""
        if True:
            query = 'SELECT MAX("Date") FROM prod'
            cur.execute(query)
            last_date = cur.fetchall()[0][0]
            before_date = last_date - datetime.timedelta(1)

            cur.execute('SELECT * FROM prod WHERE "Date" BETWEEN %s and %s;', (before_date, last_date))
            # cur.execute('SELECT * FROM prod')
            df_prod = cur.fetchall()
            prod_columns = ['Дата', 'Скв', 'Объект', 'об/мин', 'Ндин. м', 'Рт. атм', 'Рз. атм', 'Время. час', 'Qж. м3/сут',
                            'Qн. м3/сут', 'Qв. м3/сут', 'Qн. тн/сут', 'Qпр. м3/сут']
            df_prod = pd.DataFrame(df_prod, columns=prod_columns)

            df_prod['Дата'] = pd.to_datetime(df_prod['Дата'])
            string_columns = ['Скв', 'Объект']
            df_prod[string_columns] = df_prod[string_columns].astype(str)
            float_columns = ['об/мин', 'Ндин. м', 'Рт. атм', 'Рз. атм', 'Время. час',
                             'Qж. м3/сут', 'Qн. м3/сут', 'Qв. м3/сут', 'Qн. тн/сут', 'Qпр. м3/сут']
            df_prod[float_columns] = df_prod[float_columns].astype(float)
            df_prod.sort_values(by='Дата', inplace=True)
            df_prod['Обв. %'] = 100 * df_prod['Qв. м3/сут'].div(df_prod['Qж. м3/сут']).replace(np.inf, 0)
            df_prod[['Обв. %']] = df_prod[['Обв. %']].round(1)

        """Get Wells Data"""
        if True:
            cur.execute('SELECT * FROM wells')
            df_wells = cur.fetchall()
            wells_column = ['Скв', 'x', 'y', 'lat', 'lon', 'hor', 'year']
            df_wells = pd.DataFrame(df_wells, columns=wells_column)
            float_columns = ['x', 'y', 'lat', 'lon']
            df_wells[float_columns] = df_wells[float_columns].astype(float)

        """Get WorkOvers Data"""
        if True:
            cur.execute("SELECT * FROM workovers")
            df_wo = cur.fetchall()
            wo_columns = ['Дата', 'Скв', 'Вид работ', 'Комментарий']
            df_wo = pd.DataFrame(df_wo, columns=wo_columns)
            df_wo['Дата'] = pd.to_datetime(df_wo['Дата'])
            df_wo.sort_values(by='Дата', inplace=True)
            df_wo['Дата'] = df_wo['Дата'].dt.strftime('%d-%b-%y')
            string_columns = ['Скв', 'Вид работ', 'Комментарий']
            df_wo[string_columns] = df_wo[string_columns].astype(str)

        con.close()

    """Buttons"""
    if True:
        last_date = df_prod['Дата'].max()

        jurassic_middle_wells_prod = sorted(
            df_well_list_per_horizon[df_well_list_per_horizon['Объект'].str.contains('|'.join(jurassic_middle), na=False)]['Скв'].unique())

        lst_jurassic_middle_wells_prod = []
        for (i, well) in enumerate(jurassic_middle_wells_prod):
            if df_wells[df_wells['Скв'] == well].iloc[0]['hor'] in ['Консв', 'Ликв']:
                btn_color = "secondary"
            else:
                try:
                    last_day_oil_rate_j = df_prod[
                        (df_prod['Скв'] == well) &
                        (df_prod['Объект'].str.contains('|'.join(jurassic_middle), na=False)) &
                        (df_prod['Дата'] == last_date)
                        ]['Qн. тн/сут'].values[0]
                    prev_day_oil_rate_j = df_prod[
                        (df_prod['Скв'] == well) &
                        (df_prod['Объект'].str.contains('|'.join(jurassic_middle), na=False)) &
                        (df_prod['Дата'] == last_date - datetime.timedelta(1))
                        ]['Qн. тн/сут'].values[0]
                    last_day_inj_rate_j = df_prod[
                        (df_prod['Скв'] == well) &
                        (df_prod['Объект'].str.contains('|'.join(jurassic_middle), na=False)) &
                        (df_prod['Дата'] == last_date)
                        ]['Qпр. м3/сут'].values[0]
                    if last_day_inj_rate_j > 0:
                        btn_color = "info"
                    elif last_day_oil_rate_j > prev_day_oil_rate_j * 0.9:
                        btn_color = "success"
                    elif not last_day_oil_rate_j > 0:
                        btn_color = "dark"
                    else:
                        btn_color = "warning"
                except:
                    btn_color = "secondary"
            lst_jurassic_middle_wells_prod.append(dbc.Button(well, id={'type': "well", 'index': well}, color=btn_color, size="sm"))
        button_group_jurassic_middle = dbc.ButtonGroup(lst_jurassic_middle_wells_prod, vertical=True)

        jurassic_lower_wells_prod = sorted(
            df_well_list_per_horizon[df_well_list_per_horizon['Объект'].str.contains('|'.join(jurassic_lower), na=False)]['Скв'].unique())
        lst_jurassic_lower_wells_prod = []
        for (i, well) in enumerate(jurassic_lower_wells_prod):
            if df_wells[df_wells['Скв'] == well].iloc[0]['hor'] in ['Консв', 'Ликв']:
                btn_color = "secondary"
            else:
                try:
                    last_day_oil_rate_j = df_prod[
                        (df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(jurassic_lower), na=False)) & (
                                    df_prod['Дата'] == last_date)][
                        'Qн. тн/сут'].values[0]
                    prev_day_oil_rate_j = \
                    df_prod[(df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(jurassic_lower), na=False)) & (
                            df_prod['Дата'] == last_date - datetime.timedelta(1))]['Qн. тн/сут'].values[0]
                    last_day_inj_rate_j = df_prod[
                        (df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(jurassic_lower), na=False)) & (
                                    df_prod['Дата'] == last_date)][
                        'Qпр. м3/сут'].values[0]
                    if last_day_inj_rate_j > 0:
                        btn_color = "info"
                    elif last_day_oil_rate_j > prev_day_oil_rate_j * 0.9:
                        btn_color = "success"
                    elif not last_day_oil_rate_j > 0:
                        btn_color = "dark"
                    else:
                        btn_color = "warning"
                except:
                    btn_color = "secondary"
            lst_jurassic_lower_wells_prod.append(
                dbc.Button(well, id={'type': "well", 'index': well}, color=btn_color, size="sm"))
        button_group_jurassic_lower = dbc.ButtonGroup(lst_jurassic_lower_wells_prod, vertical=True)

        perm_wells_prod = sorted(
            df_well_list_per_horizon[df_well_list_per_horizon['Объект'].str.contains('|'.join(perm), na=False)]['Скв'].unique())
        lst_perm = []
        for (i, well) in enumerate(perm_wells_prod):
            if df_wells[df_wells['Скв'] == well].iloc[0]['hor'] in ['Консв', 'Ликв']:
                btn_color = "secondary"
            else:
                try:
                    last_day_oil_rate_pt = df_prod[
                        (df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(perm), na=False)) & (
                                df_prod['Дата'] == last_date)]['Qн. тн/сут'].values[0]
                    previous_day_oil_rate_pt = df_prod[
                        (df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(perm), na=False)) & (
                                    df_prod['Дата'] == last_date - datetime.timedelta(1))]['Qн. тн/сут'].values[0]
                    last_day_inj_rate_pt = df_prod[
                        (df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(perm), na=False)) & (
                                df_prod['Дата'] == last_date)]['Qпр. м3/сут'].values[0]
                    if last_day_inj_rate_pt > 0:
                        btn_color = "info"
                    elif last_day_oil_rate_pt > previous_day_oil_rate_pt * 0.9:
                        btn_color = "success"
                    elif not last_day_oil_rate_pt > 0:
                        btn_color = "dark"
                    else:
                        btn_color = "warning"
                except:
                    btn_color = "secondary"
            lst_perm.append(dbc.Button(well, id={'type': "well", 'index': well}, color=btn_color, size="sm"))
        button_group_perm = dbc.ButtonGroup(lst_perm, vertical=True)

        trias_wells_prod = sorted(
            df_well_list_per_horizon[df_well_list_per_horizon['Объект'].str.contains('|'.join(trias), na=False)]['Скв'].unique())
        lst_trias = []
        for (i, well) in enumerate(trias_wells_prod):
            if df_wells[df_wells['Скв'] == well].iloc[0]['hor'] in ['Консв', 'Ликв']:
                btn_color = "secondary"
            else:
                try:
                    last_day_oil_rate_pt = df_prod[
                        (df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(trias), na=False)) & (
                                df_prod['Дата'] == last_date)]['Qн. тн/сут'].values[0]
                    previous_day_oil_rate_pt = df_prod[
                        (df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(trias), na=False)) & (
                                df_prod['Дата'] == last_date - datetime.timedelta(1))]['Qн. тн/сут'].values[0]
                    last_day_inj_rate_pt = df_prod[
                        (df_prod['Скв'] == well) & (df_prod['Объект'].str.contains('|'.join(trias), na=False)) & (
                                df_prod['Дата'] == last_date)]['Qпр. м3/сут'].values[0]
                    if last_day_inj_rate_pt > 0:
                        btn_color = "info"
                    elif last_day_oil_rate_pt > previous_day_oil_rate_pt * 0.9:
                        btn_color = "success"
                    elif not last_day_oil_rate_pt > 0:
                        btn_color = "dark"
                    else:
                        btn_color = "warning"
                except:
                    btn_color = "secondary"
            lst_trias.append(dbc.Button(well, id={'type': "well", 'index': well}, color=btn_color, size="sm"))
        button_group_trias = dbc.ButtonGroup(lst_trias, vertical=True)

    """Map"""
    if True:
        bubble_plot = go.Figure()

        """Instantenious Bubble Map"""
        if True:
            """Data Preparation"""
            if True:
                df_prod_bubble = df_prod[df_prod['Дата'] == last_date].copy()
                df_prod_bubble = pd.merge(df_prod_bubble, df_wells, on='Скв', how='inner')
                max_bubble = max(df_prod_bubble['Qж. м3/сут'])

                df_prod_bubble_liq_jurassic = df_prod_bubble[
                    (df_prod_bubble['Qж. м3/сут'] > 0) & (df_prod_bubble['Объект'].str.contains('J'))].copy()
                df_prod_bubble_wat_jurassic = df_prod_bubble[
                    (df_prod_bubble['Qв. м3/сут'] > 0) & (df_prod_bubble['Объект'].str.contains('J'))].copy()

                df_prod_bubble_liq = df_prod_bubble[
                    (df_prod_bubble['Qж. м3/сут'] > 0) & (df_prod_bubble['Объект'].str.contains('P|T'))].copy()
                df_prod_bubble_wat = df_prod_bubble[
                    (df_prod_bubble['Qв. м3/сут'] > 0) & (df_prod_bubble['Объект'].str.contains('P|T'))].copy()
                df_prod_bubble_inj = df_prod_bubble[
                    (df_prod_bubble['Qпр. м3/сут'] > 0) & (df_prod_bubble['Объект'].str.contains('P|T'))].copy()

                df_prod_bubble_bd = df_prod_bubble[(~(df_prod_bubble['Qпр. м3/сут'] > 0)) & (~(df_prod_bubble['Qв. м3/сут'] > 0))].copy()

            sizemode_ = 'area' # 'area' or 'diameter'
            sizeref_ = 0.3
            """Jurassic"""
            if True:
                bubble_plot.add_trace(
                    go.Scatter(
                        x=df_prod_bubble_liq_jurassic["x"], y=df_prod_bubble_liq_jurassic["y"],
                        mode='markers+text', name='Юра',
                        marker=dict(
                            color='green',
                            size=df_prod_bubble_liq_jurassic["Qж. м3/сут"],
                            sizemode=sizemode_,
                            sizeref=sizeref_
                        ),
                        legendgroup="jurassic", legendrank=1,
                        showlegend=True,
                        hovertemplate=
                        '<b>Скважина</b>: <i>%{text}</i><br>' +
                        '<b>Qж. м3/сут</b>: <i>%{marker.size}</i><br>' +
                        '<b>Обв. %</b>: <i>%{customdata}</i><br>',
                        text=df_prod_bubble_liq_jurassic["Скв"],
                        textposition="top center",
                        customdata=df_prod_bubble_liq_jurassic["Обв. %"],
                    )
                )
                bubble_plot.add_trace(
                    go.Scatter(
                        x=df_prod_bubble_wat_jurassic["x"], y=df_prod_bubble_wat_jurassic["y"],
                        mode='markers',
                        marker=dict(
                            color='blue',
                            size=df_prod_bubble_wat_jurassic["Qв. м3/сут"],
                            sizemode=sizemode_,
                            sizeref=sizeref_
                        ),
                        legendgroup="jurassic",
                        showlegend=False,
                        hoverinfo='none',
                    )
                )

            """Non Jurassic"""
            if True:
                bubble_plot.add_trace(
                    go.Scatter(
                        x=df_prod_bubble_liq["x"], y=df_prod_bubble_liq["y"],
                        mode='markers+text', name='Пермо-Триас',
                        marker=dict(
                            color='green',
                            size=df_prod_bubble_liq["Qж. м3/сут"],
                            sizemode=sizemode_,
                            sizeref=sizeref_
                        ),
                        legendgroup="non_jurassic", legendrank=2,
                        showlegend=True,
                        hovertemplate=
                        '<b>Скважина</b>: <i>%{text}</i><br>' +
                        '<b>Qж. м3/сут</b>: <i>%{marker.size}</i><br>' +
                        '<b>Обв. %</b>: <i>%{customdata}</i><br>',
                        text=df_prod_bubble_liq["Скв"],
                        textposition="top center",
                        customdata=df_prod_bubble_liq["Обв. %"],
                    )
                )
                bubble_plot.add_trace(
                    go.Scatter(
                        x=df_prod_bubble_wat["x"], y=df_prod_bubble_wat["y"],
                        mode='markers',
                        marker=dict(
                            color='blue',
                            size=df_prod_bubble_wat["Qв. м3/сут"],
                            sizemode=sizemode_,
                            sizeref=sizeref_
                        ),
                        legendgroup="non_jurassic",
                        showlegend=False,
                        hoverinfo='none',
                    )
                )
                bubble_plot.add_trace(
                    go.Scatter(
                        x=df_prod_bubble_inj["x"], y=df_prod_bubble_inj["y"],
                        mode='markers+text', name='Закачка',
                        marker=dict(
                            color='olive',
                            size=df_prod_bubble_inj["Qпр. м3/сут"],
                            sizemode=sizemode_,
                            sizeref=sizeref_*10
                        ),
                        legendgroup="non_jurassic",
                        showlegend=False,
                        hovertemplate=
                        '<b>Скважина</b>: <i>%{text}</i><br>' +
                        '<b>Qпр. м3/сут</b>: <i>%{marker.size}</i><br>',
                        text=df_prod_bubble_inj["Скв"],
                        textposition="top center",
                    )
                )

            """ShutIn Wells"""
            if True:
                bubble_plot.add_trace(
                    go.Scatter(
                        name="БД", x=df_prod_bubble_bd["x"], y=df_prod_bubble_bd["y"],
                        legendrank=3,
                        mode='markers+text',
                        marker_symbol='x',
                        marker_color='magenta',
                        hoverinfo='none',
                        text=df_prod_bubble_bd["Скв"],
                        textposition="top center",
                        textfont=dict(family="sans serif", size=16, color="black"),
                    )
                )


        """Well Anotation"""
        if True:
            for horizon in sorted(df_wells['hor'].unique()):
                if horizon == 'Консв':
                    df_short = df_wells[df_wells['hor'] == horizon]
                    bubble_plot.add_trace(go.Scatter(name=horizon, x=df_short["x"], y=df_short["y"],
                                                     legendrank=3,
                                                     visible='legendonly',
                                                     mode='markers+text',
                                                     marker_symbol='x',
                                                     marker_color='black',
                                                     hoverinfo='text',
                                                     text=df_short["Скв"],
                                                     textposition="top center",
                                                     textfont=dict(family="sans serif", size=16, color="black"),
                                                     ))
                elif horizon == 'Бурен':
                    df_short = df_wells[df_wells['hor'] == horizon]
                    bubble_plot.add_trace(go.Scatter(name=horizon, x=df_short["x"], y=df_short["y"],
                                                     legendrank=4,
                                                     # visible='legendonly',
                                                     mode='markers+text',
                                                     marker_symbol='circle',
                                                     marker_color='red',
                                                     hoverinfo='text',
                                                     text=df_short["Скв"],
                                                     textposition="top center",
                                                     textfont=dict(family="sans serif", size=16, color="red"),
                                                     ))
                elif horizon.startswith('202'):
                    df_short = df_wells[df_wells['hor'] == horizon]
                    bubble_plot.add_trace(go.Scatter(name=horizon, x=df_short["x"], y=df_short["y"],
                                                     legendrank=5,
                                                     visible='legendonly',
                                                     mode='markers+text',
                                                     marker_symbol='x',
                                                     marker_color='orange',
                                                     hoverinfo='none',
                                                     text=df_short["Скв"],
                                                     textposition="top center",
                                                     textfont=dict(family="sans serif", size=16, color="orange"),
                                                     ))

        """Faults"""
        if True:
            df_faults = pd.read_csv('./assets/karatobe/Faults.csv')
            for pol in df_faults['polygon'].unique():
                df_fault = df_faults[df_faults['polygon'] == pol]
                bubble_plot.add_trace(go.Scatter(x=df_fault["x"], y=df_fault["y"],
                                                 mode='lines',
                                                 line=dict(color='firebrick', width=1),
                                                 showlegend=False,
                                                 hoverinfo='none'
                                                 ))

        """Gornyi Otvod"""
        if True:
            df_boundaries = pd.read_csv('./assets/karatobe/Gornyi_Otvod.csv')
            for contr in df_boundaries['contract'].unique():
                df_boundary = df_boundaries[df_boundaries['contract'] == contr]
                first_row = df_boundary.iloc[0]
                df_boundary = pd.concat([df_boundary, pd.DataFrame([first_row])], ignore_index=True)
                bubble_plot.add_trace(go.Scatter(x=df_boundary["x"], y=df_boundary["y"], name=str(contr),
                                                 mode='lines', line=dict(color='black', width=1),
                                                 showlegend=False,
                                                 # hoverinfo='none',
                                                 hovertemplate='<b>%{customdata}</b>',
                                                 customdata=df_boundary["contract"],
                                                 ))

        """Map Layout"""
        if True:
            bubble_plot.update_layout(
                title_text=f"Добыча на <b>{last_date.strftime('%d-%B-%y')}</b>", title_x=0.5, title_font=dict(size=16),
                xaxis={'range': [464500, 469000], 'title': None, 'fixedrange': False, 'showticklabels': False,
                       'showgrid': False},
                yaxis={'range': [5306000, 5310000], 'title': None, 'fixedrange': False, 'showticklabels': False,
                       'showgrid': False},
                margin=dict(l=0, r=0, t=40, b=0),
                paper_bgcolor="white",
                plot_bgcolor="white",
                legend=dict(
                    orientation="h",
                    # itemwidth=40,
                    # yanchor="bottom",
                    y=0.02,
                    # xanchor="right",
                    x=0.1,
                    # bgcolor="rgba(0,0,0,0)",
                    font=dict(
                        size=14,
                        color="black"
                    ),
                    bgcolor="yellow",
                    bordercolor="Black",
                    borderwidth=1
                ),
                hovermode='closest',
                autosize=False,
                # height=((screen['height'] - 100) / 2),
            )

    return [
        df_prod.to_dict('records'),

        button_group_jurassic_middle,
        button_group_jurassic_lower,
        button_group_perm,
        button_group_trias,

        df_wo.to_dict('records'),
        bubble_plot
    ]


@callback(
    Output('selected_well_analysis', 'data'),
    Input('bubble-cum-fig2', 'clickData'),
    Input({'type': 'well', 'index': ALL}, 'n_clicks')
)
def selected_well(clk_data, *args):
    trigger = ctx.triggered_id
    if isinstance(trigger, dict):
        well_select = trigger['index']
    else:
        try:
            well_select = clk_data['points'][0]['text']
        except:
            well_select = "Г-29"
    return well_select


@callback(
    Output('log-fig2', 'figure'),
    Input('selected_well_analysis', 'data')
)
def update_log_analysis(well):

    con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
    cur = con.cursor()

    """Get Perf Data"""
    if True:
        cur.execute(f"SELECT * FROM perfs WHERE well='{well}' ")
        df_perf = cur.fetchall()
        perf_column = ["well", "hor", "status", "perf"]
        df_perf = pd.DataFrame(df_perf, columns=perf_column)

    """Get Completion Data"""
    if True:
        cur.execute(f"SELECT * FROM completions WHERE well='{well}' ")
        df_comp = cur.fetchall()
        comp_column = ["well", "TD", "BP", "TS", "RT", "Packer", "Fracture"]
        df_comp = pd.DataFrame(df_comp, columns=comp_column)
        df_comp[["TD", "BP", "TS", "RT"]] = df_comp[["TD", "BP", "TS", "RT"]].astype(float)

    """Get Well Top Data"""
    if True:
        cur.execute(f" SELECT * FROM tops WHERE well='{well}' ")
        df_top = cur.fetchall()
        tops_columns = ['well', 'XII_a', 'XI_1_Br', 'XI_br', 'X_Br', 'IX Br', 'VIII_K1b',
                        'VII g(J2-?)', 'J2_IIIa', 'V_J', 'V_J2_b', 'V-1', 'V2_J2', 'V3_J2',
                        'V3_b', 'J1-IV-2', 'J1-IV-1', 'T_BJ(base_IV-1)', 'T Upper Part', 'T-II',
                        'Top_P2(I-P)', 'P1k_anh', 'P1k_gal']
        df_top = pd.DataFrame(df_top, columns=tops_columns)

    con.close()

    fig = make_subplots(
        rows=1, cols=5, column_widths=[3, 5, 5, 5, 5],
        horizontal_spacing=0.03, shared_yaxes=True,
        # subplot_titles=['', 'Vsh', 'Sw', 'Por']
    )

    """Well Schematic"""
    try:
        # Casing
        if df_comp.TD[0] > 0:
            fig.add_shape(type="rect", row=1, col=1,
                          x0=0, y0=0, x1=10, y1=df_comp.TD[0],
                          line=dict(color="gray", width=4))

        # Cement
        if df_comp.BP[0] > 0:
            fig.add_shape(type="rect", row=1, col=1,
                          x0=0, y0=df_comp.TD[0], x1=10, y1=df_comp.BP[0],
                          line=dict(color="turquoise", width=1),
                          fillcolor="turquoise")

        # Tubing
        if df_comp.TS[0] > 0:
            fig.add_shape(type="rect", row=1, col=1,
                          x0=3, y0=0, x1=7, y1=df_comp.TS[0],
                          line=dict(color="slategrey", width=4),
                          fillcolor="slategrey")

        # Packer
        if df_comp.Packer[0] != None:
            packers = map(float, df_comp.Packer[0].split(";"))
            for packer in packers:
                fig.add_shape(type="rect", row=1, col=1,
                              x0=0, y0=packer-1,
                              x1=3, y1=packer+1,
                              line=dict(color="black"),
                              fillcolor="black")
                fig.add_shape(type="rect", row=1, col=1,
                              x0=7, y0=packer - 1,
                              x1=10, y1=packer + 1,
                              line=dict(color="black"),
                              fillcolor="black")

                # log.add_hrect(
                #     y0=float(packer)-1, y1=float(packer)+1, line_width=0, col=1,
                #     fillcolor="black", opacity=1)

        # Fracture
        if df_comp.Fracture[0] != None:
            for frac in df_comp.Fracture[0].split(";"):
                fig.add_trace(go.Scatter(
                    x=[5], y=[float(frac)], name='ГРП',
                    mode='markers', marker=dict(size=30, symbol="star", line=dict(width=2, color="red"), color="yellow"), hoverinfo='skip'),
                    row=1, col=1)

        # Isolated Perforations
        perfs_closed = []
        df_comp_well = df_perf[df_perf['status'] == "closed"]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_closed.extend(elem.split("; "))
        perfs_closed.sort()
        for perf in perfs_closed:
            perf_list = list(map(float, perf.split("-")))
            fig.add_shape(type="line", row=1, col=1,
                          x0=0, y0=perf_list[0], x1=0, y1=perf_list[1],
                          line=dict(color="green", width=10))
            fig.add_shape(type="line", row=1, col=1,
                          x0=10, y0=perf_list[0], x1=10, y1=perf_list[1],
                          line=dict(color="green", width=10))

        # Recommended Perforations
        perfs_recommended = []
        df_comp_well = df_perf[df_perf['status'] == "recommendation"]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_recommended.extend(elem.split("; "))
        perfs_recommended.sort()
        for perf in perfs_recommended:
            perf_list = list(map(float, perf.split("-")))
            fig.add_shape(type="line", row=1, col=1,
                          x0=0, y0=perf_list[0], x1=0, y1=perf_list[1],
                          line=dict(color="orange", width=10))
            fig.add_shape(type="line", row=1, col=1,
                          x0=10, y0=perf_list[0], x1=10, y1=perf_list[1],
                          line=dict(color="orange", width=10))

        # Active Perforations
        perfs_open = []
        df_comp_well = df_perf[df_perf['status'] == "open"]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_open.extend(elem.split("; "))
        perfs_open.sort()
        for perf in perfs_open:
                perf_list = list(map(float, perf.split("-")))
                fig.add_shape(type="line", row=1, col=1,
                              x0=0, y0=perf_list[0], x1=0, y1=perf_list[1],
                              line=dict(color="red", width=10))
                fig.add_shape(type="line", row=1, col=1,
                              x0=10, y0=perf_list[0], x1=10, y1=perf_list[1],
                              line=dict(color="red", width=10))
    except Exception as error:
        print("No Completions For this well")
        print("An exception occurred:", error)

    """Well Logs"""
    try:
        path = f"./assets/karatobe/LOGs/{well}"

        # log_tracks = [
        #     {"curves": ["GR"], "color": "darkgreen", "xaxis": "x2", "yaxis": "y2", "scale": lambda x: x * 11 if x.mean() < 10 else x, "flag": "gr_done"},
        #     {"curves": ["RHOB", "ZDNC", "ZDEN", "RHOM", "RHOZ"], "color": "red", "xaxis": "x3", "yaxis": "y3", "flag": "rhob_done"},
        #     {"curves": ["NPHI", "CNC", "TNPH", "APLC"], "color": "blue", "xaxis": "x31", "yaxis": "y3", "scale": lambda x: x * 100 if x.mean() < 1 else x, "flag": "neut_done"},
        #     {"curves": ["DDLL", "RD", "LLD", "LL3", "AT90", "RLA1", "RESISTIVITY"], "color": "blueviolet", "xaxis": "x4", "yaxis": "y4", "flag": "resdeep_done"},
        #     {"curves": ["DSLL", "RS", "LLS", "GZ3", "AT10", "RLA5"], "color": "black", "xaxis": "x4", "yaxis": "y4", "flag": "resshallow_done"},
        #     # {"curves": ["SW", "SW_AR"], "color": "aqua", "xaxis": "x5", "yaxis": "y5", "flag": "sw_done"},
        #     # Add more tracks here...
        # ]

        gr_done = False
        rhob_done = False
        neut_done = False
        resdeep_done = False
        resshallow_done = False
        sw_done = False
        for file in scandir(path):
            try:
                df = lasio.read(file.path, engine='normal').df()

                for curve in ["GR"]:
                    if curve in df.columns and not gr_done:
                        gr_done = True
                        if df[curve].dropna().mean() < 10:
                            fig.add_trace(go.Scatter(
                                x=df[curve] * 11, y=df.index, name=curve, mode="lines", line_color="darkgreen",
                                xaxis="x2", yaxis="y2"
                            ))
                        else:
                            fig.add_trace(go.Scatter(
                                x=df[curve], y=df.index, name=curve, mode="lines", line_color="darkgreen",
                                xaxis="x2", yaxis="y2"
                            ))
                        print("GR DONE")
                        break
                for curve in ["RHOB", "ZDNC", "ZDEN", "RHOM", "RHOZ"]:
                    if curve in df.columns and not rhob_done:
                        rhob_done = True
                        fig.add_trace(go.Scatter(
                            x=df[curve], y=df.index, name=curve, mode="lines", line_color="red",
                            xaxis="x3", yaxis="y3"
                        ))
                        break
                for curve in ["NPHI", "CNC", "TNPH", "APLC"]:
                    if curve in df.columns and not neut_done:
                        neut_done = True
                        if df[curve].dropna().mean() < 1:
                            fig.add_trace(go.Scatter(
                                x=df[curve] * 100, y=df.index, name=curve, mode="lines", line_color="blue",
                                xaxis="x6", yaxis="y3"
                            ))
                        else:
                            fig.add_trace(go.Scatter(
                                x=df[curve], y=df.index, name=curve, mode="lines", line_color="blue",
                                xaxis="x6", yaxis="y3"
                            ))
                        break
                for curve in ["DDLL", "RD", "LLD", "LL3", "AT90", "RLA1", "RESISTIVITY"]:
                    if curve in df.columns and not resdeep_done:
                        resdeep_done = True
                        fig.add_trace(go.Scatter(
                            x=df[curve], y=df.index, name=curve, mode="lines", line_color="blueviolet",
                            xaxis="x4", yaxis="y4"
                        ))
                        break
                for curve in ["DSLL", "RS", "LLS", "GZ3", "AT10", "RLA5"]:
                    if curve in df.columns and not resshallow_done:
                        resshallow_done = True
                        fig.add_trace(go.Scatter(
                            x=df[curve], y=df.index, name=curve, mode="lines", line_color="black",
                            xaxis="x4", yaxis="y4"
                        ))
                        break
                for curve in ["SW", "SW_AR"]:
                    if curve in df.columns and not sw_done:
                        sw_done = True
                        fig.add_trace(go.Scatter(
                            x=df[curve], y=df.index, mode="none", fill='tozerox', fillcolor="aqua",
                            xaxis="x5", yaxis="y5"
                        ))
                        fig.add_trace(go.Scatter(
                            x0=1, dx=0, y=df.index, mode="none", fill='tonextx', fillcolor="green",
                            xaxis="x5", yaxis="y5"
                        ))
                        break
            except Exception as error:
                print("An exception occurred:", error)
                pass
    except Exception as error:
        print("No Well Log For this well")
        print("An exception occurred:", error)

    """Well Tops"""
    try:
        for i in range(2, 6):
            for top in df_top.columns[9:-1]:
                if not df_top.iloc[0][top] is None:
                    fig.add_hline(
                        y=float(df_top.iloc[0][top]),
                        line_dash="dot",
                        line_color="indigo",
                        annotation_text=top,
                        annotation_position="top right",
                        col=i,
                    )
    except Exception as error:
        print("No Tops For this well")
        print("An exception occurred:", error)

    """Layout"""
    if True:
        try:
            range_=[df_comp.TD[0]+10, 600]
        except:
            range_=[1010, 300]
        fig.update_layout(
            title=dict(text=f"<b>{well}</b>", x=0.5, y=0.98, font=dict(size=16)),
            margin=dict(l=40, r=10, t=100, b=20),
            paper_bgcolor="white",
            template="plotly_white",
            autosize=True,
            # height="100vh",
            showlegend=False,
            hovermode="y",
            yaxis1=dict(
                title={'font': {'color': 'black', 'size': 16}, 'text': 'Глубина'},
                range=range_,
                tickmode='linear',
                tick0=range_[1],
                dtick=50,
                minor=dict(ticklen=5, tickcolor="black", tickmode='auto', nticks=5, showgrid=True),
                # domain=[0.05, 1]
            ),
            yaxis2=dict(
                showline=True, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            yaxis3=dict(
                showline=True, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            yaxis4=dict(
                showline=True, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            yaxis5=dict(
                showline=True, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            xaxis1=dict(
                anchor='y1',
                visible=False,
                domain=[0.0, 0.1],
            ),
            xaxis2=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'GR'},
                anchor='y2',
                side='top',
                range=[0, 200],
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='black', mirror=True,
                domain=[0.12, 0.38],
            ),
            xaxis3=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'DENS'},
                anchor='y3',
                side='top',
                range=[1.95, 2.95],
                tickfont={'color': 'black', 'size': 9},
                tickmode='linear',
                tick0=1.95,
                dtick=0.25,
                showline=True, linewidth=1, linecolor='black', mirror=True,
                domain=[0.4, 0.58],
            ),
            xaxis6=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'NPOR'},
                anchor='y3',
                overlaying='x3',
                side='right',
                range=[45, -15],
                tickfont={'color': 'black', 'size': 9},
                showgrid=False,
                tickmode='linear',
                tick0=45,
                dtick=15,
                showline=True, linewidth=1, linecolor='black', mirror=True,
                domain=[0.4, 0.58],
            ),
            xaxis4=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'Resistivity'},
                anchor='y4',
                side='top',
                range=[0, 2],
                type="log",
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='black', mirror=True,
                domain=[0.6, 0.78],
            ),
            xaxis5=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'Sw'},
                anchor='y5',
                side='top',
                range=[0, 1],
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='black', mirror=True,
                domain=[0.8, 1.0],
            ),
        )

    return fig


clientside_callback(
    """
    function(data, well) {
        filtered_data = data.filter(d => d["Скв"] == well);
        wo_tittle = "История Скважины " + well
        return [filtered_data, wo_tittle];
    }
    """,
    Output('workover_table', 'data'),
    Output('wo_tittle', 'children'),
    Input('workovers_analysis', 'data'),
    Input('selected_well_analysis', 'data'),

)


clientside_callback(
    """
    function(data, well) {
        filtered_data = data.filter(d => d["Скв"] == well);
        let x = filtered_data.map(d=> d["Qв. м3/сут"]);
        let y = filtered_data.map(d=> d["Qн. м3/сут"]);
        return {
            'data': [{
                'hoverinfo': 'label+percent',
                'insidetextorientation': 'horizontal',
                'labels': ['Qв. м3/сут', 'Qн. м3/сут'],
                'marker': {'colors': ['blue', 'green'], 'line': {'color': '#000000', 'width': 1}},
                'pull': [0.1, 0],
                'textfont': {'size': 14},
                'textinfo': 'value+percent',
                'textposition': 'inside',
                'type': 'pie',
                'values': [x.slice(-1)[0], y.slice(-1)[0]]
                }],
            'layout': {
                        'margin': {'b': 0, 'l': 0, 'r': 0, 't': 40},
                        'paper_bgcolor': 'white',
                        'autosize': 'True',
                        'template': '...',
                        'title': {'font': {'size': 16}, 'text': 'Добыча скв.: <b>' + well + '</b>', 'x': 0.5},
                        'uniformtext': {'minsize': 14, 'mode': 'hide'},
                        'xaxis': {'title': {}},
                        'yaxis': {'title': {}},
                        'legend': {'x': 0.05, 'y': 0.05, 'font_size': 16},
                      }
            }
        }
    """,
    Output('pie-chart-fig', 'figure'),
    Input('prod_data_analysis', 'data'),
    Input('selected_well_analysis', 'data')
)


"""Get Production Data"""
def get_prod_data(well):
    con = psycopg2.connect(
        host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030"
    )
    cur = con.cursor()
    cur.execute(f" SELECT * FROM prod WHERE well='{well}' ")
    df_prod = cur.fetchall()
    con.close()

    prod_columns = ['Дата', 'Скв', 'Объект', 'об/мин', 'Ндин. м', 'Рт. атм', 'Рз. атм', 'Время. час', 'Qж. м3/сут', 'Qн. м3/сут', 'Qв. м3/сут', 'Qн. тн/сут', 'Qпр. м3/сут']
    df_prod = pd.DataFrame(df_prod, columns=prod_columns)

    df_prod['Дата'] = pd.to_datetime(df_prod['Дата'], format="%Y-%m-%d")
    string_columns = ['Скв', 'Объект']
    df_prod[string_columns] = df_prod[string_columns].astype(str)
    float_columns = ['об/мин', 'Ндин. м', 'Рт. атм', 'Рз. атм', 'Время. час',
                     'Qж. м3/сут', 'Qн. м3/сут', 'Qв. м3/сут', 'Qн. тн/сут', 'Qпр. м3/сут']
    df_prod[float_columns] = df_prod[float_columns].astype(float)
    df_prod.sort_values(by='Дата', inplace=True)
    df_prod['Обв. %'] = 100 * df_prod['Qв. м3/сут'].div(df_prod['Qж. м3/сут']).replace(np.inf, 0)
    df_prod[['Обв. %']] = df_prod[['Обв. %']].round(1)

    return df_prod

"""Get WorkOver Data"""
def get_wo_data(well):
    con = psycopg2.connect(
        host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030"
    )
    cur = con.cursor()
    cur.execute(f" SELECT * FROM workovers WHERE well='{well}' ")
    df_wo = cur.fetchall()
    con.close()

    wo_columns = ['Дата', 'Скв', 'Вид работ', 'Комментарий']
    df_wo = pd.DataFrame(df_wo, columns=wo_columns)
    df_wo['Дата'] = pd.to_datetime(df_wo['Дата'], format='%Y-%m-%d')
    df_wo['Дата'] = df_wo['Дата'].dt.strftime('%d-%b-%y')
    string_columns = ['Скв', 'Вид работ', 'Комментарий']
    df_wo[string_columns] = df_wo[string_columns].astype(str)

    return df_wo

"""Plot Production"""
def plot_production(well):
    df_prod_well = get_prod_data(well)
    df_wo_well = get_wo_data(well)

    fig = go.Figure()

    '''Add Prod Data'''
    if True:
        fig.add_trace(
            go.Scatter(
                name="Qн. тн/сут",
                x=df_prod_well["Дата"], y=df_prod_well["Qн. тн/сут"],
                mode='lines', line=dict(color="darkgreen", width=3)
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Qж. м3/сут",
                x=df_prod_well["Дата"], y=df_prod_well["Qж. м3/сут"],
                mode='lines', line=dict(color="black", width=3), visible="legendonly"
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Обв. %",
                x=df_prod_well["Дата"], y=df_prod_well["Обв. %"],
                mode='lines', line=dict(color="blue", width=3)
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Ндин. м",
                x=df_prod_well["Дата"], y=df_prod_well["Ндин. м"],
                mode='lines', line=dict(color="maroon", width=3),
                yaxis="y2"
            )
        )
        fig.add_trace(
            go.Scatter(
                name="об/мин",
                x=df_prod_well["Дата"], y=df_prod_well["об/мин"],
                mode='lines', line=dict(color="orange", width=3), visible="legendonly",
                yaxis="y4"
            )
        )

    '''Add Inj Data'''
    q_inj_title = ''
    if well in ["КН-4", "338"]:
        q_inj_title = "<span style='color:olive'>Закачка воды; </span><span style='color:red'>Ртр.; </span>"
        fig.add_trace(
            go.Scatter(
                name="Qпр. м3/сут",
                x=df_prod_well["Дата"], y=df_prod_well["Qпр. м3/сут"],
                mode='lines', line=dict(color="olive", width=3), yaxis="y4"
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Рт. атм",
                x=df_prod_well["Дата"], y=df_prod_well["Рт. атм"],
                mode='lines', line=dict(color="red", width=3), yaxis="y4"
            )
        )

    '''Add WorkOver Lines'''
    for ind in df_wo_well.index:
        wo_date = datetime.datetime.strptime(df_wo_well["Дата"][ind], '%d-%b-%y').timestamp() * 1000
        fig.add_vline(
            x=wo_date,
            line=dict(width=3, dash="dot", color="red"),
            annotation_text=df_wo_well["Вид работ"][ind],
            annotation_textangle=-90,
            annotation_font_size=20,
            annotation_font_color="red"
        )

    '''Update Layout'''
    if True:
        fig.update_traces(hovertemplate=None)
        fig.update_layout(
            title=dict(text="История скважины: <b>"+well+"<b>", font_size=16, x=0.5),
            margin=dict(l=0, r=0, t=40, b=0),
            template='plotly_white',
            # height=(screen['height']-100)//2,
            hovermode="x",
            legend=dict(
                orientation="h",
                # yanchor="bottom",
                # xanchor="right"
            ),
            xaxis=dict(
                anchor='y',
                domain=[0.0, 0.95],
                tickfont=dict(size=14),
            ),
            yaxis=dict(
                title=dict(text="<span style='color:darkgreen'>Qн; </span><span style='color:black'>Qж; </span><span style='color:blue'>Обв.</span>", font=dict(size=15)),
                tickfont=dict(color="black", size=14),
                anchor="x",
                range=[0, 100]
            ),
            yaxis2=dict(
                title=dict(text="Ндин", font=dict(color="maroon", size=15)),
                tickfont=dict(color="black", size=14),
                anchor="x",
                overlaying="y",
                side="right",
                range=[1000, 0],
                showgrid=False
            ),
            yaxis4=dict(
                title=dict(text=f"{q_inj_title}<span style='color:orange'>об/мин</span>", font=dict(size=15)),
                tickfont=dict(color="black", size=14),
                anchor="free",
                overlaying="y",
                side="right",
                position=1,
                range=[0, 500],
                showgrid=False
            ),
        )

    return fig

"""Plot Injection"""
def plot_injection(well):
    df_prod_well = get_prod_data(well)
    df_wo_well = get_wo_data(well)

    fig = go.Figure()

    '''Add Inj Data'''
    if True:
        fig.add_trace(
            go.Scatter(
                name="Qпр. м3/сут",
                x=df_prod_well["Дата"], y=df_prod_well["Qпр. м3/сут"],
                mode='lines', line=dict(color="olive", width=3)
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Рт. атм",
                x=df_prod_well["Дата"], y=df_prod_well["Рт. атм"],
                mode='lines', line=dict(color="red", width=3), yaxis="y2"
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Рз. атм",
                x=df_prod_well["Дата"], y=df_prod_well["Рз. атм"],
                mode='lines', line=dict(color="red", width=3, dash='dash'), yaxis="y2"
            )
        )

    '''Add WorkOver Lines'''
    for ind in df_wo_well.index:
        wo_date = datetime.datetime.strptime(df_wo_well["Дата"][ind], '%d-%b-%y').timestamp() * 1000
        fig.add_vline(
            x=wo_date,
            line=dict(width=3, dash="dot", color="red"),
            annotation_text=df_wo_well["Вид работ"][ind],
            annotation_textangle=-90,
            annotation_font_size=20,
            annotation_font_color="red"
        )

    '''Update Layout'''
    if True:
        fig.update_layout(
            title=dict(text="Закачка скважины <b>" + well + "<b>", font_size=16, x=0.5),
            margin=dict(l=60, r=20, t=40, b=20),
            template='plotly_white',
            # height=(screen['height'] - 100) // 2,
            xaxis=dict(
                anchor='y',
                domain=[0.0, 0.95],
                tickfont=dict(size=14),
            ),
            yaxis=dict(
                title=dict(text="Закачка воды, м3/сут", font=dict(color="olive", size=15)),
                tickfont=dict(color="olive", size=14),
                anchor="x",
                range=[0, 1000]
            ),
            yaxis2=dict(
                title=dict(text="Давление, атм", font=dict(color="red", size=15)),
                tickfont=dict(color="red", size=14),
                anchor="x",
                overlaying="y",
                side="right",
                range=[0, 200],
                showgrid=False,
                position=0.9,
                tick0=0, dtick=40
            )
        )

    return fig

@callback(
    Output('line-fig2', 'figure'),
    Input('selected_well_analysis', 'data')
)
def update_line_plot(well):
    if well in ["Г-22"]:
        return plot_injection(well)
    else:
        return plot_production(well)