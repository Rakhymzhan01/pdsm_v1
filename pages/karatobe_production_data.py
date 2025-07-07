from apps import karatobe_navigation as navigation
from apps import footer
from dash import register_page, dcc, html, callback, Output, Input, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.types import Date, Text, Float
from flask_login import current_user
import psycopg2

# https://towardsdatascience.com/set-up-heroku-postgresql-for-your-app-in-python-7dad9ceb0f92

register_page(__name__, path='/karatobe/data')


'''Data-------------------------------------------------'''
engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")


'''Containers-------------------------------------------'''
container = dbc.Container([
    html.Br(),
    dbc.Col([
        dbc.Row([
            # Latest Date Notification
            html.Div(id='karatobe_prod_data_date'),
        ], justify="center"),
        dbc.Row([
            dcc.Loading(children=html.Div(id='karatobe_postgres_datatable')),
            html.Br(),
            dbc.Col([
                html.Button('Добавить', id='karatobe_editing_rows_button', n_clicks=0),
                html.Button('Сохранить', id='karatobe_save_to_postgres', n_clicks=0),
                html.Button('Скачать', id='karatobe_save_button', n_clicks=0),
            ]),
            dcc.Download(id="karatobe_download"),
            # Create notification when saving to DataBase
            html.Div(id='karatobe_prod_data_notification'),
        ], justify="center"),
    ], width={"size": 10, "offset": 1})
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
            dcc.Interval(id='karatobe_interval_prod_data', interval=86400000*7, n_intervals=0),
            container,
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
    Output('karatobe_prod_data_date', 'children'),
    Output('karatobe_postgres_datatable', 'children'),
    Input('karatobe_interval_prod_data', 'n_intervals')
)
def populate_datatable(n_intervals):
    columns = ['Дата[m/d/yyyy]', 'Скв', 'Горизонт', 'Обороты Насоса', 'Ндин. м', 'Трубное Давление',
               'Затрубное Давление', 'Время. час', 'Qж. м3/сут', 'Qн. м3/сут', 'Qв. м3/сут', 'Qн. тн/сут', 'Qз. м3/сут']
    empty_row = [{i: '' for i in columns}]

    con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres",
                           password="akzhol2030")
    cur = con.cursor()
    query = 'SELECT MAX("Date") FROM prod'
    cur.execute(query)
    last_date = cur.fetchall()[0][0]
    con.close()

    if current_user.username in ["Aman", "YNarimanov", "BBeregenov"]:
        df = pd.read_sql_table("prod", con=engine)
        return [
            html.H1(f"Данные по добыче загружены до: {last_date}",
                    style={'color': 'red', 'font-weight': 'bold', 'font-size': 'large'}),
            dash_table.DataTable(
                id='karatobe_our_table',
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": True}
                    for i in df.columns
                ],
                data=df.to_dict('records'),
                editable=True,  # allow editing of data inside all cells
                filter_action="native",  # allow filtering of data by user ('native') or not ('none')
                sort_action="native",  # enables data to be sorted per-column by user or not ('none')
                sort_mode="single",  # sort across 'multi' or 'single' columns
                column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                row_selectable="multi",  # allow users to select 'multi' or 'single' rows
                row_deletable=True,  # choose if user can delete a row (True) or not (False)
                selected_columns=[],  # ids of columns that user selects
                selected_rows=[],  # indices of rows that user selects
                page_action="native",  # all data is passed to the table up-front or not ('none')
                page_current=0,  # page number that user is on
                page_size=20,  # number of rows visible per page
                style_cell={
                    'minWidth': 35, 'maxWidth': 95, 'width': 35
                },  # ensure adequate header width when text is shorter than cell's text
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['Date', 'well', 'Horizon']
                ],  # align text columns to left. By default they are aligned to right
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                }  # overflow cells' content into multiple lines
            ),
        ]
    else:
        return [
            html.H1(f"Данные по добыче загружены до: {last_date}",
                           style={'color': 'red', 'font-weight': 'bold', 'font-size': 'large'}),
            dash_table.DataTable(
                id='karatobe_our_table',
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": True}
                    for i in columns
                ],
                data=empty_row,
                editable=True,  # allow editing of data inside all cells
                filter_action="native",  # allow filtering of data by user ('native') or not ('none')
                sort_action="native",  # enables data to be sorted per-column by user or not ('none')
                sort_mode="single",  # sort across 'multi' or 'single' columns
                column_selectable="multi",  # allow users to select 'multi' or 'single' columns
                row_selectable="multi",  # allow users to select 'multi' or 'single' rows
                row_deletable=True,  # choose if user can delete a row (True) or not (False)
                selected_columns=[],  # ids of columns that user selects
                selected_rows=[],  # indices of rows that user selects
                page_action="native",  # all data is passed to the table up-front or not ('none')
                page_current=0,  # page number that user is on
                page_size=30,  # number of rows visible per page
                style_cell={
                    'minWidth': 30, 'maxWidth': 120, 'width': 30, 'fontSize': 13
                },  # ensure adequate header width when text is shorter than cell's text
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['Дата', 'Скв', 'Горизонт']
                ],  # align text columns to left. By default they are aligned to right
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
                }  # overflow cells' content into multiple lines
            ),
        ]

@callback(
    Output('karatobe_our_table', 'data'),
    Input('karatobe_editing_rows_button', 'n_clicks'),
    [State('karatobe_our_table', 'data'), State('karatobe_our_table', 'columns')]
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

# @callback(
#     Output('our-table', 'columns'),
#     [Input('adding-columns-button', 'n_clicks')],
#     [State('adding-rows-name', 'value'),
#      State('our-table', 'columns')],
# )
# def add_column(n_clicks, value, existing_columns):
#     print(existing_columns)
#     if n_clicks > 0:
#         existing_columns.append({
#             'name': value, 'id': value,
#             'renamable': True, 'deletable': True
#         })
#     print(existing_columns)
#     return existing_columns

@callback(
    Output('karatobe_prod_data_notification', 'children'),
    Input('karatobe_save_to_postgres', 'n_clicks'),
    State('karatobe_our_table', 'data')
)
def df_to_postgres(n_clicks, dataset):
    if n_clicks > 0:
        if current_user.username in ["Aman", "BBeregenov"]:
            df = pd.DataFrame(dataset)
            df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
            df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
            df.replace(',', '.', regex=True, inplace=True)
            dtype = {'Date': Date,
                     'well': Text(), 'Horizon': Text(),
                     'Pump': Float(25), 'H_m': Float(25),
                     'Ptr_atm': Float(25), 'Pztr_atm': Float(25), 'Time_hr': Float(25), 'Ql_m3': Float(25),
                     'Qo_m3': Float(25), 'Qw_m3': Float(25), 'Qo_ton': Float(25), 'Qi_m3': Float(25)}
            df.to_sql(name="prod", con=engine, if_exists="replace", index=False, dtype=dtype)
            return [
                html.Plaintext("Изменения сохранены.",
                               style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
            ]
        else:
            df = pd.DataFrame(dataset)
            df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
            df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
            df.replace(',', '.', regex=True, inplace=True)
            df['Дата[m/d/yyyy]'] = pd.to_datetime(df['Дата[m/d/yyyy]'], format="%m/%d/%Y")
            df.rename(columns={
                "Дата[m/d/yyyy]": "Date",
                "Скв": "well",
                "Горизонт": "Horizon",
                "Обороты Насоса": "Pump",
                "Ндин. м": "H_m",
                "Трубное Давление": "Ptr_atm",
                "Затрубное Давление": "Pztr_atm",
                "Время. час": "Time_hr",
                "Qж. м3/сут": "Ql_m3",
                "Qн. м3/сут": "Qo_m3",
                "Qв. м3/сут": "Qw_m3",
                "Qн. тн/сут": "Qo_ton",
                "Qз. м3/сут": "Qi_m3"
            }, inplace=True)

            dtype = {'Date': Date,
                     'well': Text(), 'Horizon': Text(),
                     'Pump': Float(25), 'H_m': Float(25),
                     'Ptr_atm': Float(25), 'Pztr_atm': Float(25), 'Time_hr': Float(25), 'Ql_m3': Float(25),
                     'Qo_m3': Float(25), 'Qw_m3': Float(25), 'Qo_ton': Float(25), 'Qi_m3': Float(25)}
            df.to_sql(name="prod", con=engine, if_exists="append", index=False, dtype=dtype)
            return [
                html.Plaintext("Изменения сохранены.",
                               style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
            ]


@callback(
    Output("karatobe_download", "data"),
    Input("karatobe_save_button", "n_clicks"),
    State("karatobe_our_table", "data")
)
def download_as_csv(n_clicks, table_data):
    # https://www.dash-extensions.com/components/download
    if n_clicks > 0:
        con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres",
                               password="akzhol2030")
        cur = con.cursor()
        cur.execute('SELECT * FROM prod')
        df_prod = cur.fetchall()
        prod_columns = ['Дата', 'Скв', 'Горизонт', 'Обороты Насоса', 'Ндин. м', 'Трубное Давление',
                   'Затрубное Давление', 'Время. час', 'Qж. м3/сут', 'Qн. м3/сут', 'Qв. м3/сут', 'Qн. тн/сут',
                   'Qз. м3/сут']
        df_prod = pd.DataFrame(df_prod, columns=prod_columns)
        con.close()

        def to_xlsx(bytes_io):
            xslx_writer = pd.ExcelWriter(bytes_io, engine="xlsxwriter")  # requires the xlsxwriter package
            df_prod.to_excel(xslx_writer, index=False, sheet_name="суточная")
            xslx_writer.close()

        return dcc.send_bytes(to_xlsx, "История добычи м.Каратобе.xlsx")

