from apps import karatobe_navigation as navigation
from apps import footer
import dash
from dash import dcc, html, callback, Output, Input, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
from sqlalchemy import create_engine
from flask_login import current_user

dash.register_page(__name__, path='/karatobe/wo')


'''Data-------------------------------------------------'''
engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")


'''Containers-------------------------------------------'''
container = dbc.Container([
    html.Br(),
    dbc.Col([
        dcc.Loading(children=html.Div(id='workover_datatable')),
        html.Br(),
        html.Button('Добавить', id='add_row_workover', n_clicks=0),
        html.Button('Сохранить', id='save_workover_table', n_clicks=0),
        html.Div(id='workover_notification', children=[]),
    ], width={"size": 10, "offset": 1})
])


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
            dcc.Interval(id='interval_wo', interval=86400000*7, n_intervals=0),
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

#---------------------------------------------------------------------
@callback(
    Output('workover_datatable', 'children'),
    Input('interval_wo', 'n_intervals')
)
def populate_datatable(n_intervals):
    df = pd.read_sql_table("workovers", con=engine)
    return [
        dash_table.DataTable(
            id='wo-table',
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": False}
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
                'minWidth': 30, 'maxWidth': 120, 'width': 15, 'fontSize': 15
            }, # ensure adequate header width when text is shorter than cell's text
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['Date', 'well']
            ], # align text columns to left. By default they are aligned to right
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto'
            } # overflow cells' content into multiple lines
        ),
    ]

@callback(
    Output('wo-table', 'data'),
    Input('add_row_workover', 'n_clicks'),
    [State('wo-table', 'data'), State('wo-table', 'columns')]
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@callback(
    Output('workover_notification', 'children'),
    Input('save_workover_table', 'n_clicks'),
    State('wo-table', 'data')
)
def df_to_postgres(n_clicks, dataset):
    if n_clicks > 0:
        df = pd.DataFrame(dataset)
        # df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
        # df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        # df.replace(',', '.', regex=True, inplace=True)
        df.to_sql("workovers", con=engine, if_exists='replace', index=False)
        return [
            html.Plaintext("Изменения сохранены.",
                           style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
        ]
