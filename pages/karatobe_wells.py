from apps import karatobe_navigation as navigation
from apps import footer
import dash
from dash import dcc, html, callback, Output, Input, dash_table, State
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
from flask_login import current_user


dash.register_page(__name__, path='/karatobe/wells')


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
            dcc.Interval(id='interval_wells', interval=86400000*7, n_intervals=0),
            html.Br(),
            dbc.Col([
                dcc.Loading(children=html.Div(id='wells_datatable')),
                html.Br(),
                html.Button('Добавить', id='add_well', n_clicks=0),
                html.Button('Сохранить', id='save_wells_table', n_clicks=0),
                # Create notification when saving to excel
                html.Div(id='wells_notification', children=[])
            ], width={"size": 6, "offset": 3}),
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

#---------------------------------------------------------------------
engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")

@callback(
    Output('wells_datatable', 'children'),
    Input('interval_wells', 'n_intervals')
)
def populate_wells_datatable(n_intervals):
    df_wells = pd.read_sql_table("wells", con=engine)
    return [
        dash_table.DataTable(
            id='wells-table',
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": True}
                for i in df_wells.columns
            ],
            # columns=[
            #     {'id': 'Well', 'name': 'Well', 'deletable': False, 'selectable': True, 'hideable': True},
            #     {'id': 'X', 'name': 'X', 'deletable': False, 'selectable': True, 'hideable': True},
            #     {'id': 'Y', 'name': 'Y', 'deletable': False, 'selectable': True, 'hideable': True},
            #     {'id': 'Lat', 'name': 'Lat', 'deletable': False, 'selectable': True, 'hideable': True},
            #     {'id': 'Lon', 'name': 'Lon'},
            #     {'id': 'Object', 'name': 'Object', 'deletable': False, 'selectable': True, 'hideable': True, 'presentation': 'dropdown'},
            # ],
            data=df_wells.to_dict('records'),
            editable=True,  # allow editing of data inside all cells
            filter_action="native",  # allow filtering of data by user ('native') or not ('none')
            sort_action="native",  # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",  # sort across 'multi' or 'single' columns
            # column_selectable="multi",  # allow users to select 'multi' or 'single' columns
            # row_selectable="multi",  # allow users to select 'multi' or 'single' rows
            row_deletable=True,  # choose if user can delete a row (True) or not (False)
            # selected_columns=[],  # ids of columns that user selects
            # selected_rows=[],  # indices of rows that user selects
            page_action='none',  # all data is passed to the table up-front or not ('none')
            # page_current=0,  # page number that user is on
            # page_size=30,  # number of rows visible per page
            style_cell={'minWidth': 95, 'maxWidth': 95, 'width': 95, 'textAlign': 'center'},
            style_data={'whiteSpace': 'normal', 'height': 'auto'}, # overflow cells' content into multiple lines
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'}],
            style_table={'height': '700px', 'overflowY': 'auto'},
            # dropdown={
            #     'Object': {
            #         'options': [
            #             {'label': i, 'value': i}
            #             for i in ["J1-IV", "P&T", "V-J2", "Бурен", "Консв", "Ликвид"]
            #         ]
            #     }
            # }
        ),
    ]

@callback(
    Output('wells-table', 'data'),
    Input('add_well', 'n_clicks'),
    [State('wells-table', 'data'), State('wells-table', 'columns')]
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@callback(
    Output('wells_notification', 'children'),
    Input('save_wells_table', 'n_clicks'),
    State('wells-table', 'data')
)
def df_to_postgres(n_clicks, dataset):
    if n_clicks > 0:
        df = pd.DataFrame(dataset)
        df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df.replace(',', '.', regex=True, inplace=True)
        df.to_sql("wells", con=engine, if_exists='replace', index=False)
        return [
            html.Plaintext("Изменения сохранены.",
                           style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
        ]