from apps import karatobe_navigation as navigation
from apps import footer
from dash import register_page, dcc, html, callback, Output, Input, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import lasio, datetime, math
from os import scandir

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from flask_login import current_user


register_page(__name__, path='/karatobe/corr')


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


'''Containers-------------------------------------------'''
plots = dbc.Container(
    dbc.Col([
        # Select Wells
        dbc.Row([
            dbc.Col([dcc.Dropdown(id="well1_dropdown", options=[], value='338', clearable=False)]),
            dbc.Col(html.Div(id='distance_wells', className='text-center')),
            dbc.Col([dcc.Dropdown(id="well2_dropdown", options=[], value='Г-31', clearable=False)])
        ], className="g-0"),
        # Well Log
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    type="default",
                    children=dcc.Graph(
                        id='well_log',
                        className="h-100",
                        config=config
                    )
                ),
                xs=12, sm=12, md=12, lg=12, xl=12, xxl=12, style=border
            ),
        ]),
        # Line Plots
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    type="default",
                    children=dcc.Graph(
                        id='well1-line',
                        className="h-100",
                        config=config
                    )
                ),
                xs=12, sm=12, md=6, lg=6, xl=6, xxl=6, style=border
            ),
            dbc.Col(
                dcc.Loading(
                    type="default",
                    children=dcc.Graph(
                        id='well2-line',
                        className="h-100",
                        config=config
                    )
                ),
                xs=12, sm=12, md=6, lg=6, xl=6, xxl=6, style=border
            ),
        ]),
    ], width={"size": 10, "offset": 1}), fluid=True)


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
            dcc.Interval(id='interval_pg_correlation', interval=86400000*7, n_intervals=0),
            # dcc.Store(id='prod_data_correlation', storage_type='session'),
            # dcc.Store(id='wells_correlation', storage_type='session'),
            # dcc.Store(id='perforations_correlation', storage_type='memory'),
            # dcc.Store(id='completions_correlation', storage_type='memory'),
            dcc.Store(id='screen_correlation', storage_type='session'),
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
    Output('screen_correlation', 'data'),
    Input('interval_pg_correlation', 'n_intervals')
)


@callback(
    Output('well1_dropdown', 'options'),
    Output('well2_dropdown', 'options'),
    Input('interval_pg_correlation', 'n_intervals')
)
def get_well_list(n_intervals):
    con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
    cur = con.cursor()

    """Get Wells List with Logs"""
    # if True:
    #     query = 'SELECT DISTINCT "well" FROM elan;'
    #     cur.execute(query)
    #     wells = cur.fetchall()
    #     options = [i[0] for i in wells]

    """Get Wells List"""
    if True:
        query = 'SELECT DISTINCT "Well" FROM wells'
        cur.execute(query)
        wells = cur.fetchall()
        options = [i[0] for i in wells]

    con.close()
    return options, options


@callback(
    Output('distance_wells', 'children'),
    Input('well1_dropdown', 'value'),
    Input('well2_dropdown', 'value')
)
def distance(well1, well2):
    if well1 and well2:
        con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
        cur = con.cursor()
        cur.execute('SELECT * FROM wells')
        df_wells = cur.fetchall()
        wells_column = ['well', 'x', 'y', 'lat', 'lon', 'hor', 'year']
        df_wells = pd.DataFrame(df_wells, columns=wells_column)
        float_columns = ['x', 'y', 'lat', 'lon']
        df_wells[float_columns] = df_wells[float_columns].astype(float)

        well1_x = df_wells.loc[df_wells['well'] == well1, 'lat'].iloc[0]
        well1_y = df_wells.loc[df_wells['well'] == well1, 'lon'].iloc[0]
        well2_x = df_wells.loc[df_wells['well'] == well2, 'lat'].iloc[0]
        well2_y = df_wells.loc[df_wells['well'] == well2, 'lon'].iloc[0]
        R = 6371000
        φ1 = well1_x * math.pi / 180
        φ2 = well2_x * math.pi / 180
        Δφ = (well2_x - well1_x) * math.pi / 180
        Δλ = (well2_y - well1_y) * math.pi / 180
        a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) * math.sin(Δλ / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = int(R * c)
        return f'Расстояние между скважинами: {d} м.'

    return 'Выберите две скважины.'


# @callback(
#     Output('perforations_correlation', 'data'),
#     Output('completions_correlation', 'data'),
#     Input('interval_pg_correlation', 'n_intervals')
# )
# def get_perf_comp_data(n_intervals):
#     con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
#     cur = con.cursor()
#
#     cur.execute('SELECT * FROM perfs')
#     df_perf = cur.fetchall()
#     perf_column = ["well", "hor", "status", "perf"]
#     df_perf = pd.DataFrame(df_perf, columns=perf_column)
#
#     cur.execute('SELECT * FROM completions')
#     df_comp = cur.fetchall()
#     comp_column = ["well", "TD", "BP", "TS", "RT", "Packer", "Fracture"]
#     df_comp = pd.DataFrame(df_comp, columns=comp_column)
#     df_comp[["TD", "BP", "TS", "RT", "Packer"]] = df_comp[["TD", "BP", "TS", "RT", "Packer"]].astype(float)
#     con.close()
#
#     return [df_perf.to_dict('records'), df_comp.to_dict('records')]


@callback(
    Output('well_log', 'figure'),
    Input('well1_dropdown', 'value'),
    Input('well2_dropdown', 'value'),
    Input('screen_correlation', 'data')
)
def update_log_correlation(well1_select, well2_select, screen):
    # Get Data
    if True:
        con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
        cur = con.cursor()

        # elan_columns = ["DEPT", "Well", "VSH", "SW", "PORO"]
        # cur.execute(f" SELECT * FROM elan WHERE well='{well1_select}' ")
        # df_elan_well1 = cur.fetchall()
        # df_elan_well1 = pd.DataFrame(df_elan_well1, columns=elan_columns)
        # cur.execute(f" SELECT * FROM elan WHERE well='{well2_select}' ")
        # df_elan_well2 = cur.fetchall()
        # df_elan_well2 = pd.DataFrame(df_elan_well2, columns=elan_columns)



        tops_columns = ['well', 'XII_a', 'XI_1_Br', 'XI_br', 'X_Br', 'IX Br', 'VIII_K1b',
                        'VII g(J2-?)', 'J2_IIIa', 'V_J', 'V_J2_b', 'V-1', 'V2_J2', 'V3_J2',
                        'V3_b', 'J1-IV-2', 'J1-IV-1', 'T_BJ(base_IV-1)', 'T Upper Part', 'T-II',
                        'Top_P2(I-P)', 'P1k_anh', 'P1k_gal']
        cur.execute(f" SELECT * FROM tops WHERE well='{well1_select}' ")
        df_top_well1 = cur.fetchall()
        df_top_well1 = pd.DataFrame(df_top_well1, columns=tops_columns)

        cur.execute(f" SELECT * FROM tops WHERE well='{well2_select}' ")
        df_top_well2 = cur.fetchall()
        df_top_well2 = pd.DataFrame(df_top_well2, columns=tops_columns)

        perf_column = ["well", "hor", "status", "perf"]
        cur.execute('SELECT * FROM perfs')
        df_perf = cur.fetchall()
        df_perf = pd.DataFrame(df_perf, columns=perf_column)

        comp_column = ["well", "TD", "BP", "TS", "RT", "Packer", "Fracture"]
        cur.execute('SELECT * FROM completions')
        df_comp = cur.fetchall()
        df_comp = pd.DataFrame(df_comp, columns=comp_column)
        df_comp[["TD", "BP", "TS", "RT"]] = df_comp[["TD", "BP", "TS", "RT"]].astype(float)

        wells_comp = df_comp.set_index('well').T.to_dict('list')
        well1_rt = wells_comp[well1_select][3]
        well2_rt = wells_comp[well2_select][3]

        con.close()

    log = make_subplots(rows=1, cols=11,
                        column_widths=[3, 5, 5, 5, 5, 2, 3, 5, 5, 5, 5], horizontal_spacing=0.005,
                        shared_yaxes=True,
                        # subplot_titles=['', 'VSH', 'PORO', 'SW', '', '', 'VSH', 'PORO', 'SW']
                        )

    # Well1 Schematic
    try:
        """Cement"""
        # log.add_shape(type="rect", row=1, col=1,
        #               x0=0, y0=wells_comp[well1_select][0]-well1_rt, x1=10, y1=wells_comp[well1_select][1]-well1_rt,
        #               line=dict(color="turquoise", width=1),
        #               fillcolor="turquoise")
        """Casing"""
        log.add_shape(type="rect", row=1, col=1,
                      x0=2, y0=0, x1=8, y1=wells_comp[well1_select][0]-well1_rt,
                      line=dict(color="gray", width=4))
        """Tubing"""
        # log.add_shape(type="rect", row=1, col=1,
        #               x0=3, y0=0, x1=7, y1=wells_comp[well1_select][2]-well1_rt,
        #               line=dict(color="slategrey", width=4),
        #               fillcolor="slategrey")
        """Packer"""
        # if wells_comp[well1_select][4] > 0:
        #     log.add_hrect(
        #         y0=wells_comp[well1_select][4] - 1-well1_rt, y1=wells_comp[well1_select][4] + 1-well1_rt, line_width=0, col=1,
        #         fillcolor="black", opacity=1)

        """Isolated Perforations"""
        perfs_closed = []
        df_comp_well = df_perf[(df_perf['well'] == well1_select) & (df_perf['status'] == "closed")]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_closed.extend(elem.split("; "))
        perfs_closed.sort()
        for perf in perfs_closed:
            perf_list = list(map(float, perf.split("-")))
            log.add_shape(type="line", row=1, col=1,
                          x0=2, y0=perf_list[0]-well1_rt, x1=2, y1=perf_list[1]-well1_rt,
                          line=dict(color="green", width=10))
            log.add_shape(type="line", row=1, col=1,
                          x0=8, y0=perf_list[0]-well1_rt, x1=8, y1=perf_list[1]-well1_rt,
                          line=dict(color="green", width=10))

        """Recommended Perforations"""
        perfs_recommended = []
        df_comp_well = df_perf[(df_perf['well'] == well1_select) & (df_perf['status'] == "recommendation")]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_recommended.extend(elem.split("; "))
        perfs_recommended.sort()
        for perf in perfs_recommended:
            perf_list = list(map(float, perf.split("-")))
            log.add_shape(type="line", row=1, col=1,
                          x0=2, y0=perf_list[0]-well1_rt, x1=2, y1=perf_list[1]-well1_rt,
                          line=dict(color="orange", width=10))
            log.add_shape(type="line", row=1, col=1,
                          x0=8, y0=perf_list[0]-well1_rt, x1=8, y1=perf_list[1]-well1_rt,
                          line=dict(color="orange", width=10))

        """Active Perforations"""
        perfs_open = []
        df_comp_well = df_perf[(df_perf['well'] == well1_select) & (df_perf['status'] == "open")]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_open.extend(elem.split("; "))
        perfs_open.sort()
        for perf in perfs_open:
                perf_list = list(map(float, perf.split("-")))
                log.add_shape(type="line", row=1, col=1,
                              x0=2, y0=perf_list[0] - well1_rt, x1=2, y1=perf_list[1] - well1_rt,
                              line=dict(color="red", width=10))
                log.add_shape(type="line", row=1, col=1,
                              x0=8, y0=perf_list[0] - well1_rt, x1=8, y1=perf_list[1] - well1_rt,
                              line=dict(color="red", width=10))
    except:
        print("No Well Schematic Data for Well1")

    # Well2 Schematic
    try:
        """Cement"""
        # log.add_shape(type="rect", row=1, col=6,
        #               x0=0, y0=wells_comp[well2_select][0]-well2_rt, x1=10, y1=wells_comp[well2_select][1]-well2_rt,
        #               line=dict(color="turquoise", width=1),
        #               fillcolor="turquoise")
        """Casing"""
        log.add_shape(type="rect", row=1, col=7,
                      x0=2, y0=0, x1=8, y1=wells_comp[well2_select][0]-well2_rt,
                      line=dict(color="gray", width=4))
        """Tubing"""
        # log.add_shape(type="rect", row=1, col=6,
        #               x0=3, y0=0, x1=7, y1=wells_comp[well2_select][2]-well2_rt,
        #               line=dict(color="slategrey", width=4),
        #               fillcolor="slategrey")
        """Packer"""
        # if wells_comp[well2_select][4] > 0:
        #     log.add_hrect(
        #         y0=wells_comp[well2_select][4] - 1-well2_rt, y1=wells_comp[well2_select][4] + 1-well2_rt, line_width=0, col=6,
        #         fillcolor="black", opacity=1)

        # Isolated Perforations
        perfs_closed = []
        df_comp_well = df_perf[(df_perf['well'] == well2_select) & (df_perf['status'] == "closed")]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_closed.extend(elem.split("; "))
        perfs_closed.sort()
        for perf in perfs_closed:
            perf_list = list(map(float, perf.split("-")))
            log.add_shape(type="line", row=1, col=7,
                          x0=2, y0=perf_list[0]-well2_rt, x1=2, y1=perf_list[1]-well2_rt,
                          line=dict(color="green", width=10))
            log.add_shape(type="line", row=1, col=7,
                          x0=8, y0=perf_list[0]-well2_rt, x1=8, y1=perf_list[1]-well2_rt,
                          line=dict(color="green", width=10))

        # Recommended Perforations
        perfs_recommended = []
        df_comp_well = df_perf[(df_perf['well'] == well2_select) & (df_perf['status'] == "recommendation")]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_recommended.extend(elem.split("; "))
        perfs_recommended.sort()
        for perf in perfs_recommended:
                perf_list = list(map(float, perf.split("-")))
                log.add_shape(type="line", row=1, col=7,
                              x0=2, y0=perf_list[0]-well2_rt, x1=2, y1=perf_list[1]-well2_rt,
                              line=dict(color="orange", width=10))
                log.add_shape(type="line", row=1, col=7,
                              x0=8, y0=perf_list[0]-well2_rt, x1=8, y1=perf_list[1]-well2_rt,
                              line=dict(color="orange", width=10))

        # Active Perforations
        perfs_open = []
        df_comp_well = df_perf[(df_perf['well'] == well2_select) & (df_perf['status'] == "open")]
        for elem in df_comp_well['perf'].tolist():
            if elem != "NA":
                perfs_open.extend(elem.split("; "))
        perfs_open.sort()
        for perf in perfs_open:
                    perf_list = list(map(float, perf.split("-")))
                    log.add_shape(type="line", row=1, col=7,
                                  x0=2, y0=perf_list[0] - well2_rt, x1=2, y1=perf_list[1] - well2_rt,
                                  line=dict(color="red", width=10))
                    log.add_shape(type="line", row=1, col=7,
                                  x0=8, y0=perf_list[0] - well2_rt, x1=8, y1=perf_list[1] - well2_rt,
                                  line=dict(color="red", width=10))
    except:
        print("No Well Schematic Data for Well2")

    colors = ['brown', 'orange', 'aqua']

    # Well1 Logs
    try:
        # for count, curve in enumerate(['VSH', 'PORO', 'SW']):
        #     log.add_trace(
        #         go.Scatter(
        #             x=df_elan_well1[curve], y=df_elan_well1.DEPT-well1_rt,
        #             name=curve, legendgroup=curve,
        #             mode="none",
        #             # line=dict(color=colors[count])
        #             fill='tozerox',
        #             fillcolor=colors[count],
        #         ), row=1, col=2 + count)

        path = f"./assets/karatobe/LOGs/{well1_select}"
        for file in scandir(path):
            try:
                df = lasio.read(file.path, engine='normal').df()
                # df.dropna(inplace=True)
                for curve in ["GR"]:
                    if curve in df.columns:
                        if df[curve].mean() < 20:
                            log.add_trace(go.Scatter(
                                x=df[curve] * 11 + 4, y=df.index-well1_rt, name=curve, mode="lines", line_color="darkgreen",
                                xaxis="x2", yaxis="y2"
                            ))
                        else:
                            log.add_trace(go.Scatter(
                                x=df[curve], y=df.index-well1_rt, name=curve, mode="lines", line_color="darkgreen",
                                xaxis="x2", yaxis="y2"
                            ))
                        break
                for curve in ["RHOB", "ZDNC", "ZDEN", "RHOM", "RHOZ"]:
                    if curve in df.columns:
                        log.add_trace(go.Scatter(
                            x=df[curve], y=df.index-well1_rt, name=curve, mode="lines", line_color="red",
                            xaxis="x3", yaxis="y3"
                        ))
                        break
                for curve in ["NPHI", "CNC", "TNPH", "APLC"]:
                    if curve in df.columns:
                        if df[curve].mean() < 1:
                            log.add_trace(go.Scatter(
                                x=df[curve] * 100, y=df.index-well1_rt, name=curve, mode="lines", line_color="blue",
                                xaxis="x31", yaxis="y3"
                            ))
                        else:
                            log.add_trace(go.Scatter(
                                x=df[curve], y=df.index-well1_rt, name=curve, mode="lines", line_color="blue",
                                xaxis="x31", yaxis="y3"
                            ))
                        break
                for curve in ["DDLL", "RD", "LLD", "LL3", "AT90", "RLA1"]:
                    if curve in df.columns:
                        log.add_trace(go.Scatter(
                            x=df[curve], y=df.index-well1_rt, name=curve, mode="lines", line_color="blueviolet",
                            xaxis="x4", yaxis="y4"
                        ))
                        break
                for curve in ["DSLL", "RS", "LLS", "GZ3", "AT10", "RLA5"]:
                    if curve in df.columns:
                        log.add_trace(go.Scatter(
                            x=df[curve], y=df.index-well1_rt, name=curve, mode="lines", line_color="black",
                            xaxis="x4", yaxis="y4"
                        ))
                        break
                for curve in ["SW", "SW_AR"]:
                    if curve in df.columns:
                        log.add_trace(go.Scatter(
                            x=df[curve], y=df.index-well1_rt, mode="none", fill='tozerox', fillcolor="aqua",
                            xaxis="x5", yaxis="y5"
                        ))
                        log.add_trace(go.Scatter(
                            x0=1, dx=0, y=df.index-well1_rt, mode="none", fill='tonextx', fillcolor="green",
                            xaxis="x5", yaxis="y5"
                        ))
                        break
            except:
                pass
    except:
        print("No Well Log Data for Well1")

    # Well2 Logs
    try:
        # for count, curve in enumerate(['VSH', 'PORO', 'SW']):
        #     log.add_trace(
        #         go.Scatter(
        #             x=df_elan_well2[curve], y=df_elan_well2.DEPT-well2_rt,
        #             name=curve, legendgroup=curve,
        #             mode="none",
        #             # line=dict(color=colors[count]),
        #             fill='tozerox',
        #             fillcolor=colors[count],
        #             showlegend=False
        #         ), row=1, col=7 + count)

        path = f"./assets/karatobe/LOGs/{well2_select}"
        for file in scandir(path):
            print(well2_select)
            print(f'RT = {well2_rt}')
            try:
                df = lasio.read(file.path, engine='normal').df()
                # df.dropna(inplace=True)
                print(df.head())
                for curve in ["GR"]:
                    if curve in df.columns:
                        if df[curve].mean() < 20:
                            log.add_trace(go.Scatter(
                                x=df[curve] * 11 + 4, y=df.index-well2_rt, name=curve, mode="lines", line_color="darkgreen",
                                xaxis="x8", yaxis="y8"
                            ))
                        else:
                            log.add_trace(go.Scatter(
                                x=df[curve], y=df.index-well2_rt, name=curve, mode="lines", line_color="darkgreen",
                                xaxis="x8", yaxis="y8"
                            ))
                        break
                for curve in ["RHOB", "ZDNC", "ZDEN", "RHOM", "RHOZ"]:
                    if curve in df.columns:
                        log.add_trace(go.Scatter(
                            x=df[curve], y=df.index-well2_rt, name=curve, mode="lines", line_color="red",
                            xaxis="x9", yaxis="y9"
                        ))
                        break
                for curve in ["NPHI", "CNC", "TNPH", "APLC"]:
                    if curve in df.columns:
                        print(f'{curve} mean = {df[curve].mean()}')
                        print(df.describe())
                        if df[curve].mean() < 1:
                            log.add_trace(go.Scatter(
                                x=df[curve] * 100, y=df.index-well2_rt, name=curve, mode="lines", line_color="blue",
                                xaxis="x91", yaxis="y9"
                            ))
                        else:
                            log.add_trace(go.Scatter(
                                x=df[curve], y=df.index-well2_rt, name=curve, mode="lines", line_color="blue",
                                xaxis="x91", yaxis="y9"
                            ))
                        break
                for curve in ["DDLL", "RD", "LLD", "LL3", "AT90", "RLA5"]:
                    if curve in df.columns:
                        log.add_trace(go.Scatter(
                            x=df[curve], y=df.index-well2_rt, name=curve, mode="lines", line_color="blueviolet",
                            xaxis="x10", yaxis="y10"
                        ))
                        break
                for curve in ["DSLL", "RS", "LLS", "GZ3", "AT10", "RLA1"]:
                    if curve in df.columns:
                        log.add_trace(go.Scatter(
                            x=df[curve], y=df.index-well2_rt, name=curve, mode="lines", line_color="black",
                            xaxis="x10", yaxis="y10"
                        ))
                        break
                for curve in ["SW", "SW_AR"]:
                    if curve in df.columns:
                        log.add_trace(go.Scatter(
                            x=df[curve], y=df.index-well2_rt, mode="none", fill='tozerox', fillcolor="aqua",
                            xaxis="x11", yaxis="y11"
                        ))
                        log.add_trace(go.Scatter(
                            x0=1, dx=0, y=df.index-well2_rt, mode="none", fill='tonextx', fillcolor="green",
                            xaxis="x11", yaxis="y11"
                        ))
                        break
            except Exception as error:
                print("An exception occurred:", error)
                pass
    except:
        print("No Well Log Data for Well2")

    # Well1 Tops
    try:
        for i in range(2, 6):
            for top in df_top_well1.columns[15:]:
                if not df_top_well1.iloc[0][top] is None:
                    log.add_hline(
                        y=float(df_top_well1.iloc[0][top])-well1_rt,
                        line_dash="dot", line_color="indigo",
                        col=i, annotation_text=top, annotation_position="top right"
                    )
    except:
        print("No Well Top Data for Well1")

    # Well2 Tops
    try:
        for i in range(8, 12):
            for top in df_top_well2.columns[15:]:
                if not df_top_well2.iloc[0][top] is None:
                    log.add_hline(
                        y=float(df_top_well2.iloc[0][top])-well2_rt,
                        line_dash="dot", line_color="indigo",
                        col=i, annotation_text=top, annotation_position="top right"
                    )
    except:
        print("No Well Top Data for Well2")

    """Layout"""
    if True:
        log.update_layout(
            title_text=f"ГИС: <b>{well1_select} / {well2_select}</b>", title_x=0.5, title_font=dict(size=16),
            margin=dict(l=60, r=20, t=80, b=20),
            # template='plotly_white',
            autosize=True,
            height=(screen['height']-150)*0.6,
            showlegend=False,
            hovermode="y",
            yaxis1=dict(
                title={'font': {'color': 'black', 'size': 16}, 'text': 'Абсолютная Глубина'},
                range=[900, 400],
                tickmode='linear',
                tick0=400,
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
            yaxis6=dict(
                showline=False, linewidth=2, linecolor='black', mirror=False,
                # domain=[0.05, 1]
            ),
            yaxis7=dict(
                showline=False, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            yaxis8=dict(
                showline=True, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            yaxis9=dict(
                showline=True, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            yaxis10=dict(
                showline=True, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            yaxis11=dict(
                showline=True, linewidth=2, linecolor='black', mirror=True,
                # domain=[0.05, 1]
            ),
            xaxis1=dict(
                anchor='y1',
                range=[0, 10],
                visible=False
            ),
            xaxis2=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'GR'},
                anchor='y2',
                side='top',
                range=[0, 200],
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='black', mirror=True,
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
            ),
            xaxis31=dict(
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
            ),
            xaxis4=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'Resistivity'},
                anchor='y4',
                side='top',
                range=[0, 2],
                type="log",
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            xaxis5=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'Sw'},
                anchor='y5',
                side='top',
                range=[0, 1],
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='aqua', mirror=True,
            ),
            xaxis6=dict(
                anchor='y6',
                visible=False
            ),
            xaxis7=dict(
                anchor='y7',
                range=[0, 10],
                visible=False
            ),
            xaxis8=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'GR'},
                anchor='y8',
                side='top',
                range=[0, 200],
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            xaxis9=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'DENS'},
                anchor='y9',
                side='top',
                range=[1.95, 2.95],
                tickfont={'color': 'black', 'size': 9},
                tickmode='linear',
                tick0=1.95,
                dtick=0.25,
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            xaxis91=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'NPOR'},
                anchor='y9',
                overlaying='x9',
                side='right',
                range=[45, -15],
                tickfont={'color': 'black', 'size': 9},
                showgrid=False,
                tickmode='linear',
                tick0=45,
                dtick=15,
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            xaxis10=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'Resistivity'},
                anchor='y10',
                side='top',
                range=[0, 2],
                type="log",
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            xaxis11=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'Sw'},
                anchor='y11',
                side='top',
                range=[0, 1],
                tickfont={'color': 'black', 'size': 9},
                showline=True, linewidth=1, linecolor='aqua', mirror=True,
            ),
        )
        # log.update_yaxes(title_text="Абсолютная Глубина", range=[750, 400], row=1, col=1)
        # log.update_xaxes(visible=False, row=1, col=1)
        # log.update_xaxes(visible=False, range=[0, 1], row=1, col=2)
        # log.update_xaxes(visible=False, range=[0, 1], row=1, col=3)
        # log.update_xaxes(visible=False, range=[0, 1], row=1, col=4)
        # log.update_yaxes(showticklabels=True, showgrid=False, row=1, col=1)
        #
        # log.update_xaxes(visible=False, row=1, col=6)
        # log.update_xaxes(visible=False, range=[0, 1], row=1, col=7)
        # log.update_xaxes(visible=False, range=[0, 1], row=1, col=8)
        # log.update_xaxes(visible=False, range=[0, 1], row=1, col=9)
        # log.update_yaxes(showticklabels=False, showgrid=False, row=1, col=6)

    return log


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
    df_wo['Дата'] = pd.to_datetime(df_wo['Дата'])
    df_wo['Дата'] = df_wo['Дата'].dt.strftime('%d-%b-%y')
    string_columns = ['Скв', 'Вид работ', 'Комментарий']
    df_wo[string_columns] = df_wo[string_columns].astype(str)

    return df_wo

"""Plot Production"""
def plot_production(well, screen):
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
            title=dict(text="Добыча скважины <b>"+well+"<b>", font_size=16, x=0.5),
            margin=dict(l=60, r=20, t=40, b=20),
            template='plotly_white',
            height=(screen['height']-150)*0.4,
            xaxis=dict(
                anchor='y',
                domain=[0.0, 0.95],
                tickfont=dict(size=14),
            ),
            yaxis=dict(
                title=dict(text="Qн; Qж; Обводненность", font=dict(color="black", size=15)),
                tickfont=dict(color="black", size=14),
                anchor="x",
                range=[0, 100]
            ),
            yaxis2=dict(
                title=dict(text="Ндин", font=dict(color="maroon", size=15)),
                tickfont=dict(color="maroon", size=14),
                anchor="x",
                overlaying="y",
                side="right",
                range=[1000, 0],
                showgrid=False
            ),
            yaxis4=dict(
                title=dict(text="об/мин", font=dict(color="orange", size=15)),
                tickfont=dict(color="orange", size=14),
                anchor="free",
                overlaying="y",
                side="right",
                position=1,
                range=[0, 500],
                showgrid=False
            ),
        )

    return fig


@callback(
    Output('well1-line', 'figure'),
    Output('well2-line', 'figure'),
    Input('well1_dropdown', 'value'),
    Input('well2_dropdown', 'value'),
    Input('screen_correlation', 'data')
)
def update_line_plots(well1_select, well2_select, screen):
    well1_fig = plot_production(well1_select, screen)
    well2_fig = plot_production(well2_select, screen)

    return well1_fig, well2_fig

# clientside_callback(
#     """
#     function(data, well1, well2, screen) {
#         filtered_data = data.filter(d => d["Скв"] == well1);
#         well1_fig = {
#             'data': [
#                       {
#                         'x': filtered_data.map(d=> d["Дата"]),
#                         'y': filtered_data.map(d=> d["Qн. тн/сут"]),
#                         'line': {'color': 'darkgreen', 'width': 2},
#                         'name': "Qн. тн/сут",
#                         'mode': "lines",
#                      },
#                      {
#                         'x': filtered_data.map(d=> d["Дата"]),
#                         'y': filtered_data.map(d=> d["Обв. %"]),
#                         'line': {'color': 'blue', 'width': 2},
#                         'name': "Обв. %",
#                         'mode': "lines",
#                         'xaxis': "x",
#                         'yaxis': "y2"
#                      },
#                      {
#                         'x': filtered_data.map(d=> d["Дата"]),
#                         'y': filtered_data.map(d=> d["Ндин. м"]),
#                         'line': {'color': 'maroon', 'dash': 'dash', 'width': 2},
#                         'mode': 'lines',
#                         'name': 'Ндин. м',
#                         'xaxis': "x",
#                         'yaxis': "y4"
#                      },
#                      {
#                         'x': filtered_data.map(d=> d["Дата"]),
#                         'y': filtered_data.map(d=> d["об/мин"]),
#                         'line': {'color': 'black', 'dash': 'dash', 'width': 2},
#                         'mode': 'lines',
#                         'name': 'об/мин',
#                         'xaxis': "x",
#                         'yaxis': "y8"
#                      }
#                     ],
#             'layout': {
#                     'margin': {'b': 20, 'l': 80, 'r': 10, 't': 40},
#                     'paper_bgcolor': 'white',
#                     'template': '...',
#                     'height': (screen.height-200)/2,
#                     'title': {'font': {'size': 16}, 'text': 'Добыча скважины: <b>' + well1 + '</b>', 'x': 0.5},
#                     'xaxis': {
#                         'anchor': 'y',
#                         'domain': [0.0, 0.75],
#                         'tickfont': {'size': 12}
#                             },
#                    'yaxis': {
#                         'anchor': 'x',
#                         'domain': [0.0, 1.0],
#                         'range': [0, 100],
#                         'tickfont': {'color': 'darkgreen', 'size': 12},
#                         'title': {'font': {'color': 'darkgreen', 'size': 12}, 'text': 'Дебит нефти, тон/сут'}
#                             },
#                    'yaxis2': {
#                         'anchor': 'x',
#                         'overlaying': 'y',
#                         'range': [0, 100],
#                         'showgrid': 0,
#                         'side': 'right',
#                         'tickfont': {'color': 'blue', 'size': 12},
#                         'title': {'font': {'color': 'blue', 'size': 12}, 'text': 'Обводненность, %'}
#                             },
#                    'yaxis4': {
#                         'anchor': 'free',
#                         'overlaying': 'y',
#                         'position': 0.85,
#                         'range': [1000, 0],
#                         'showgrid': 0,
#                         'side': 'right',
#                         'tickfont': {'color': 'maroon', 'size': 12},
#                         'title': {'font': {'color': 'maroon', 'size': 12}, 'text': 'Ндин. м'}
#                             },
#                    'yaxis8': {
#                         'anchor': 'free',
#                         'overlaying': 'y',
#                         'position': 0.95,
#                         'range': [0, 500],
#                         'showgrid': 0,
#                         'side': 'right',
#                         'tickfont': {'color': 'black', 'size': 12},
#                         'title': {'font': {'color': 'black', 'size': 12}, 'text': 'об/мин'}
#                             }
#                      }
#             };
#         filtered_data = data.filter(d => d["Скв"] == well2);
#         well2_fig = {
#             'data': [
#                       {
#                         'x': filtered_data.map(d=> d["Дата"]),
#                         'y': filtered_data.map(d=> d["Qн. тн/сут"]),
#                         'line': {'color': 'darkgreen', 'width': 2},
#                         'name': "Qн. тн/сут",
#                         'mode': "lines",
#                      },
#                      {
#                         'x': filtered_data.map(d=> d["Дата"]),
#                         'y': filtered_data.map(d=> d["Обв. %"]),
#                         'line': {'color': 'blue', 'width': 2},
#                         'name': "Обв. %",
#                         'mode': "lines",
#                         'xaxis': "x",
#                         'yaxis': "y2"
#                      },
#                      {
#                         'x': filtered_data.map(d=> d["Дата"]),
#                         'y': filtered_data.map(d=> d["Ндин. м"]),
#                         'line': {'color': 'maroon', 'dash': 'dash', 'width': 2},
#                         'mode': 'lines',
#                         'name': 'Ндин. м',
#                         'xaxis': "x",
#                         'yaxis': "y4"
#                      },
#                      {
#                         'x': filtered_data.map(d=> d["Дата"]),
#                         'y': filtered_data.map(d=> d["об/мин"]),
#                         'line': {'color': 'black', 'dash': 'dash', 'width': 2},
#                         'mode': 'lines',
#                         'name': 'об/мин',
#                         'xaxis': "x",
#                         'yaxis': "y8"
#                      }
#                     ],
#             'layout': {
#                     'margin': {'b': 20, 'l': 80, 'r': 10, 't': 40},
#                     'paper_bgcolor': 'white',
#                     'template': '...',
#                     'height': (screen.height-200)/2,
#                     'title': {'font': {'size': 16}, 'text': 'Добыча скважины: <b>' + well2 + '</b>', 'x': 0.5},
#                     'xaxis': {
#                         'anchor': 'y',
#                         'domain': [0.0, 0.75],
#                         'tickfont': {'size': 12}
#                             },
#                    'yaxis': {
#                         'anchor': 'x',
#                         'domain': [0.0, 1.0],
#                         'range': [0, 100],
#                         'tickfont': {'color': 'darkgreen', 'size': 12},
#                         'title': {'font': {'color': 'darkgreen', 'size': 12}, 'text': 'Дебит нефти, тон/сут'}
#                             },
#                    'yaxis2': {
#                         'anchor': 'x',
#                         'overlaying': 'y',
#                         'range': [0, 100],
#                         'showgrid': 0,
#                         'side': 'right',
#                         'tickfont': {'color': 'blue', 'size': 12},
#                         'title': {'font': {'color': 'blue', 'size': 12}, 'text': 'Обводненность, %'}
#                             },
#                    'yaxis4': {
#                         'anchor': 'free',
#                         'overlaying': 'y',
#                         'position': 0.85,
#                         'range': [1000, 0],
#                         'showgrid': 0,
#                         'side': 'right',
#                         'tickfont': {'color': 'maroon', 'size': 12},
#                         'title': {'font': {'color': 'maroon', 'size': 12}, 'text': 'Ндин. м'}
#                             },
#                    'yaxis8': {
#                         'anchor': 'free',
#                         'overlaying': 'y',
#                         'position': 0.95,
#                         'range': [0, 500],
#                         'showgrid': 0,
#                         'side': 'right',
#                         'tickfont': {'color': 'black', 'size': 12},
#                         'title': {'font': {'color': 'black', 'size': 12}, 'text': 'об/мин'}
#                             }
#                      }
#             };
#         return [well1_fig, well2_fig];
#     }
#     """,
#     Output('well1-line', 'figure'),
#     Output('well2-line', 'figure'),
#     Input('prod_data_correlation', 'data'),
#     Input('well1_dropdown', 'value'),
#     Input('well2_dropdown', 'value'),
#     Input('screen_correlation', 'data')
# )