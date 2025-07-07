from apps import karatobe_navigation as navigation
from apps import footer
from dash import register_page, dcc, html, callback, Output, Input, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from flask_login import current_user
# https://towardsdatascience.com/set-up-heroku-postgresql-for-your-app-in-python-7dad9ceb0f92


register_page(__name__, path='/karatobe/top')


'''Data-------------------------------------------------'''
engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")


'''Containers-------------------------------------------'''
container = dbc.Container([
    html.Br(),
    dbc.Col([
        # html.Div([
            #         dcc.Input(
            #             id='karatobe_top_add_col_name',
            #             placeholder='Enter a column name...',
            #             value='',
            #             style={'padding': 10}
            #         ),
            #         html.Button('Add Column', id='karatobe_top_add_col_btn', n_clicks=0)
            #     ], style={'height': 50}),
        dcc.Loading(children=html.Div(id='karatobe_top_postgres_datatable')),
        html.Br(),
        html.Button('Добавить', id='karatobe_top_add_row_btn', n_clicks=0),
        html.Button('Сохранить', id='karatobe_top_save_to_postgres', n_clicks=0),

        # Create notification when saving to excel
        html.Div(id='karatobe_top_placeholder'),
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
            dcc.Interval(id='karatobe_top_interval_pg', interval=86400000*7, n_intervals=0),
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
    Output('karatobe_top_postgres_datatable', 'children'),
    Input('karatobe_top_interval_pg', 'n_intervals')
)
def populate_datatable(n_intervals):
    df = pd.read_sql_table("tops", con=engine)
    # df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
    # df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    # df.replace(',', '.', regex=True, inplace=True)
    return [
        dash_table.DataTable(
            id='karatobe_top_table',
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
            page_size=30,  # number of rows visible per page
            style_cell={
                'minWidth': 45, 'maxWidth': 145, 'width': 45, 'fontSize': 13
            }, # ensure adequate header width when text is shorter than cell's text
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['well']
            ], # align text columns to left. By default they are aligned to right
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto'
            } # overflow cells' content into multiple lines
        ),
    ]

@callback(
    Output('karatobe_top_table', 'data'),
    Input('karatobe_top_add_row_btn', 'n_clicks'),
    [State('karatobe_top_table', 'data'), State('karatobe_top_table', 'columns')]
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
    Output('karatobe_top_placeholder', 'children'),
    Input('karatobe_top_save_to_postgres', 'n_clicks'),
    State('karatobe_top_table', 'data')
)
def df_to_postgres(n_clicks, dataset):
    if n_clicks > 0:
        df = pd.DataFrame(dataset)
        df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df.replace(',', '.', regex=True, inplace=True)
        df.to_sql("tops", con=engine, if_exists='replace', index=False)
        return [
            html.Plaintext("Изменения сохранены.",
                           style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
        ]

