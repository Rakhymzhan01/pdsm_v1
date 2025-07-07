from apps import karatobe_navigation as navigation
from apps import footer
import pandas as pd
from dash import dcc, html, callback, Output, Input, clientside_callback, register_page, ClientsideFunction
import dash_bootstrap_components as dbc
import psycopg2, datetime
from flask_login import current_user
import dash
from dash import html, dcc
import plotly.graph_objects as go


register_page(__name__, path='/karatobe/test', name="ZingChart")


# plots = dbc.Container([
#     dbc.Row([
#         dcc.Interval(id='interval_pg_bubble_pie', interval=86400000 * 7, n_intervals=0),
#         html.Div(id="zingchart", style={"height": "1200px", "width": "2600px"}),
#         dcc.Store(id="chart-data", data={
#                 "values": [],
#                 "names": [],
#                 "series": []
#             })
#     ], justify="center")
# ], fluid=True)
#
#
# '''Layout-----------------------------------------------'''
# def layout():
#     if not current_user.is_authenticated:
#         return html.Div([
#             html.Br(),
#             dbc.Row([
#                 dbc.Col([
#                     "Please ", dcc.Link("login", href="/"), " to continue"
#                 ], width={"size": 6, "offset": 3})
#             ], align="center")
#         ])
#     elif current_user.user_level.split('_')[0] in ["master", "all", "karatobe"]:
#         return html.Div([
#             navigation.navbar,
#             plots,
#             footer.footer
#         ])
#     else:
#         return html.Div([
#             html.Br(),
#             dbc.Row([
#                 dbc.Col([
#                     "Вы не авторизованы для просмотра этой страницы. Пожалуйста, ", dcc.Link("войдите", href="/"), " другой учетной записью."
#                 ], width={"size": 6, "offset": 3})
#             ], align="center")
#         ])
#
#
# '''Callbacks--------------------------------------------'''
# clientside_callback(
#     """
#     function(n_intervals) {
#         var w = window.innerWidth;
#         var h = window.innerHeight-70;
#         return {"height": h, "width": w};
#     }
#     """,
#     Output('zingchart', 'style'),
#     Input('interval_pg_bubble_pie', 'n_intervals')
# )
#
#
#
# @callback(
#     Output("chart-data", "data"),
#     Input('zingchart', 'style')
# )
# def update_chart(n_intervals):
#     """Data"""
#     if True:
#         con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
#         cur = con.cursor()
#
#         """Get Prod Data for Last Day"""
#         if True:
#             cur.execute('SELECT "well", "Horizon", "Qo_m3", "Qw_m3", "Qi_m3" FROM prod WHERE DATE("Date") = (SELECT DATE(MAX("Date")) FROM prod)')
#             df_prod = cur.fetchall()
#             prod_columns = ['Скв', 'Объект', 'Qн. м3/сут', 'Qв. м3/сут', 'Qпр. м3/сут']
#             df_prod = pd.DataFrame(df_prod, columns=prod_columns)
#             float_columns = ['Qн. м3/сут', 'Qв. м3/сут', 'Qпр. м3/сут']
#             df_prod[float_columns] = df_prod[float_columns].astype(float)
#
#
#         """Get Wells Coordinate Data"""
#         if True:
#             cur.execute('SELECT * FROM wells')
#             df_wells = cur.fetchall()
#             wells_column = ['Скв', 'x', 'y', 'lat', 'lon', 'hor', 'year']
#             df_wells = pd.DataFrame(df_wells, columns=wells_column)
#             float_columns = ['x', 'y', 'lat', 'lon']
#             df_wells[float_columns] = df_wells[float_columns].astype(float)
#
#         con.close()
#
#         """Data Preparation"""
#         if True:
#             df_prod.fillna(0, inplace=True)
#             df_prod['J1_oil'] = 0
#             df_prod['J1_wat'] = 0
#             df_prod['J1_inj'] = 0
#             df_prod['J2_oil'] = 0
#             df_prod['J2_wat'] = 0
#             df_prod['J2_inj'] = 0
#             df_prod['PT_oil'] = 0
#             df_prod['PT_wat'] = 0
#             df_prod['PT_inj'] = 0
#             df_prod.loc[df_prod['Объект'].str.contains("J1"), 'J1_oil'] = df_prod['Qн. м3/сут']
#             df_prod.loc[df_prod['Объект'].str.contains("J1"), 'J1_wat'] = df_prod['Qв. м3/сут']
#             df_prod.loc[df_prod['Объект'].str.contains("J1"), 'J1_inj'] = df_prod['Qпр. м3/сут']
#
#             df_prod.loc[df_prod['Объект'].str.contains("J2"), 'J2_oil'] = df_prod['Qн. м3/сут']
#             df_prod.loc[df_prod['Объект'].str.contains("J2"), 'J2_wat'] = df_prod['Qв. м3/сут']
#             df_prod.loc[df_prod['Объект'].str.contains("J2"), 'J2_inj'] = df_prod['Qпр. м3/сут']
#
#             df_prod.loc[df_prod['Объект'].str.contains("T1|P2"), 'PT_oil'] = df_prod['Qн. м3/сут']
#             df_prod.loc[df_prod['Объект'].str.contains("T1|P2"), 'PT_wat'] = df_prod['Qв. м3/сут']
#             df_prod.loc[df_prod['Объект'].str.contains("T1|P2"), 'PT_inj'] = df_prod['Qпр. м3/сут']
#
#             df_prod['bubble_size'] = df_prod['J1_oil'] + df_prod['J1_wat'] + df_prod['J1_inj'] + \
#                                      df_prod['J2_oil'] + df_prod['J2_wat'] + df_prod['J2_inj'] + \
#                                      df_prod['PT_oil'] + df_prod['PT_wat'] + df_prod['PT_inj']
#
#             df_prod_bubble = pd.merge(df_prod, df_wells, on='Скв', how='outer')
#
#     new_data = {
#         "values": [],
#         "names": [],
#         "series": []
#     }
#
#     for index, row in df_prod_bubble.iterrows():
#         new_data['values'].append([row['lon'], row['lat'], row['bubble_size']])
#         new_data['names'].append(row['Скв'])
#
#     new_data['series'] = [
#         {
#             "data-v": df_prod_bubble['J1_oil'],
#             "data-pie": "Нефть (нижняя юра)",
#             "marker": {"backgroundColor": 'green'},
#             "value-box": {
#                 "text": "%data-bubblename",
#                 "placement": "bottom",
#                 "font-color": "black",
#             }
#         },
#         {
#             "data-v": df_prod_bubble['J1_wat'],
#             "data-pie": "Вода (нижняя юра)",
#             "marker": {"backgroundColor": 'blue'},
#         },
#         {
#             "data-v": df_prod_bubble['J2_oil'],
#             "data-pie": "Нефть (средняя юра)",
#             "marker": {"backgroundColor": 'green'},
#         },
#         {
#             "data-v": df_prod_bubble['J2_wat'],
#             "data-pie": "Вода (средняя юра)",
#             "marker": {"backgroundColor": 'blue'},
#         },
#         {
#             "data-v": df_prod_bubble['PT_oil'],
#             "data-pie": "Нефть (пермо-триас)",
#             "marker": {"backgroundColor": 'green'},
#         },
#         {
#             "data-v": df_prod_bubble['PT_wat'],
#             "data-pie": "Вода (пермо-триас)",
#             "marker": {"backgroundColor": 'blue'},
#         },
#         {
#             "data-v": df_prod_bubble['PT_inj'],
#             "data-pie": "Закачка (пермо-триас)",
#             "marker": {"backgroundColor": 'olive'},
#         }
#     ]
#     return new_data
#
#
# clientside_callback(
#     ClientsideFunction(
#         namespace='zingCharts',
#         function_name='zingPieBubble'
#     ),
#     Output("zingchart", "children"),
#     Input("chart-data", "data")
# )


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
        'autoScale2d',
        'resetScale2d'
    ],
}
plots = dbc.Container([
    dbc.Row([
        dcc.Interval(id='interval_pg_bubble_pie', interval=86400000 * 7, n_intervals=0),
        dcc.Store(id='screen_bubble_pie', storage_type='memory'),
        html.Div(children=[
            dcc.Loading(
                type="default",
                children=dcc.Graph(
                    id='bubble_pie_plot',
                    className="h-100",
                    config=config)
            )
        ], style={"height": "1200px", "width": "2600px"})
    ], justify="center")
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
        var h = window.innerHeight-70;
        return {"height": h, "width": w};
    }
    """,
    Output('screen_bubble_pie', 'data'),
    Input('interval_pg_bubble_pie', 'n_intervals')
)


@callback(
    Output('bubble_pie_plot', 'figure'),
    Input('screen_bubble_pie', 'data')
)
def plot__bubble_pie(screen):
    """Well Data"""
    if True:
        con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")
        cur = con.cursor()

        """Get Prod Data for Last Day"""
        if True:
            cur.execute('SELECT "Date", "well", "Horizon", "Qo_m3", "Qw_m3", "Qi_m3" FROM prod WHERE DATE("Date") = (SELECT DATE(MAX("Date")) FROM prod)')
            df_prod = cur.fetchall()
            prod_columns = ['Date', 'Скв', 'Объект', 'Qн. м3/сут', 'Qв. м3/сут', 'Qпр. м3/сут']
            df_prod = pd.DataFrame(df_prod, columns=prod_columns)
            last_date = max(df_prod.Date)
            float_columns = ['Qн. м3/сут', 'Qв. м3/сут', 'Qпр. м3/сут']
            df_prod[float_columns] = df_prod[float_columns].astype(float)
            df_prod['bubble_size'] = df_prod['Qн. м3/сут'] + df_prod['Qв. м3/сут']
            df_prod.fillna(0, inplace=True)

        """Get Wells Data"""
        if True:
            cur.execute('SELECT * FROM wells')
            df_wells = cur.fetchall()
            wells_column = ['Скв', 'x', 'y', 'lat', 'lon', 'hor', 'year']
            df_wells = pd.DataFrame(df_wells, columns=wells_column)
            float_columns = ['x', 'y', 'lat', 'lon']
            df_wells[float_columns] = df_wells[float_columns].astype(float)

        con.close()

        df_prod_bubble = pd.merge(df_prod, df_wells, on='Скв', how='inner')

        fig = go.Figure()

        xaxis_range=[464500, 469000]
        yaxis_range = [5306000, 5310000]
        colors = ['green', 'lightblue', 'darkorange', 'lightgreen']

        for index, row in df_prod_bubble.iterrows():
            x_ = (row.x - min(xaxis_range)) / (max(xaxis_range) - min(xaxis_range))
            y_ = (row.y - min(yaxis_range)) / (max(yaxis_range) - min(yaxis_range))
            r = 0.02 * row['bubble_size'] / max(df_prod_bubble['bubble_size'])
            fig.add_trace(go.Pie(
                labels=['oil', 'water'],
                values=[row['Qн. м3/сут'], row['Qв. м3/сут']],
                name=f"Скв: {row['Скв']} <br> {row['Объект']}", # name=loc['name'],
                text=[f"{row['Скв']}", ""],
                domain={"x": [x_-r, x_+r], "y": [y_-r, y_+r]},  # fake domains for layout
                # hoverinfo="value+label+percent",
                # textinfo='text',
                # textfont_size=14,
                # showlegend=False
            ))


        # Add map as background image (or omit if you want pie-only layout)
        fig.update_traces(
            hoverinfo='value+label+percent+name',
            textinfo='text',
            textfont_size=12,
            textposition='outside',
            marker=dict(colors=colors, line=dict(color='#000000', width=1))
        )

    """Gornyi Otvod"""
    if True:
        df_boundaries = pd.read_csv('./assets/karatobe/Gornyi_Otvod.csv')
        for contr in df_boundaries['contract'].unique():
            if contr != "КТМ":
                df_boundary = df_boundaries[df_boundaries['contract'] == contr]
                first_row = df_boundary.iloc[0]
                df_boundary = pd.concat([df_boundary, pd.DataFrame([first_row])], ignore_index=True)
                fig.add_trace(go.Scatter(
                    x=df_boundary["x"], y=df_boundary["y"], name=str(contr),
                    mode='lines', line=dict(color='black', width=1),
                    # showlegend=False,
                    # hoverinfo='none',
                    hovertemplate='<b>%{customdata}</b>',
                    customdata=df_boundary["contract"],
                ))


    """Faults"""
    if True:
        df_faults = pd.read_csv('./assets/karatobe/Faults.csv')
        for pol in df_faults['polygon'].unique():
            df_fault = df_faults[df_faults['polygon'] == pol]
            fig.add_trace(go.Scatter(x=df_fault["x"], y=df_fault["y"],
                                             mode='lines',
                                             line=dict(color='firebrick', width=1),
                                             showlegend=False,
                                             hoverinfo='none'
                                             ))

    fig.update_layout(
        title=f"<b>Карта Текущих Отборов на <i>{last_date.strftime('%d-%B-%y')}</i></b>", title_x=0.5, title_font=dict(size=16),
        # yaxis_title=None, xaxis_title=None,
        hovermode='closest',
        autosize=True,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=screen['height'] - 100,
        xaxis={'range': [464500, 469000], 'title': None, 'fixedrange': True, 'showticklabels': False, 'showgrid': False},
        yaxis={'range': [5306000, 5310000], 'title': None, 'fixedrange': True, 'showticklabels': False, 'showgrid': False},
        # yaxis_range = [5306000, 5310000],
        # xaxis_fixedrange = True,
        # yaxis_fixedrange = True,
        legend=dict(
            orientation="h",
            itemwidth=40,
            yanchor="bottom",
            y=0.02,
            xanchor="right",
            x=0.5,
            bgcolor="rgba(0,0,0,0)"
        ),
    )


    return fig
