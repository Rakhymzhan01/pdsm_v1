from apps import karatobe_navigation as navigation
from apps import footer
from dash import register_page, dcc, html, callback, Output, Input, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from flask_login import current_user
import plotly.express as px

# https://towardsdatascience.com/set-up-heroku-postgresql-for-your-app-in-python-7dad9ceb0f92

register_page(__name__, path='/karatobe/pvt')


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
options = ['Давление (атм)', 'Температура (С)', 'Давление насыщения (атм)', 'Газовый фактор (м3/т)', 'Плотность нефти (г/cм3)', 'Объемный коэффициент (Во)',
       'Вязкость (сП)']



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
            dcc.Interval(id='interval_pvt', interval=86400000*7, n_intervals=0),
            html.Br(),
            # html.Div([
            #         dcc.Input(
            #             id='adding-rows-name',
            #             placeholder='Enter a column name...',
            #             value='',
            #             style={'padding': 10}
            #         ),
            #         html.Button('Add Column', id='adding-columns-button', n_clicks=0)
            #     ], style={'height': 50}),
            dbc.Col([
                dbc.Row([
                    dcc.Loading(children=html.Div(id='postgres_pvttable')),
                    html.Br(),
                    dbc.Col([
                        html.Button('Добавить', id='editing-rows-button', n_clicks=0),
                        html.Button('Сохранить', id='save_to_postgres', n_clicks=0),
                    ]),
                    # Create notification when saving to excel
                    html.Div(id='pvt_notification', children=[]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([dcc.Dropdown(id="x_dropdown", options=options, value='Температура (С)', clearable=False)]),
                    dbc.Col([dcc.Dropdown(id="y_dropdown", options=options, value='Вязкость (сП)', clearable=False)]),
                    dbc.Col([dcc.Dropdown(id="size_dropdown", options=options, value='Плотность нефти (г/cм3)', clearable=False)]),
                ]),
                html.Br(),
                dbc.Row([
                    dcc.Loading(
                        type="default",
                        children=dcc.Graph(
                            id='pvt_plot',
                            className="h-100",
                            config=config
                        )
                    ),
                ]),
            ], width={"size": 10, "offset": 1}),
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

'''---------------------------------------------------------------------'''
@callback(
    Output('postgres_pvttable', 'children'),
    Output('pvt_plot', 'figure'),
    Input('interval_pvt', 'n_intervals'),
    Input('x_dropdown', 'value'),
    Input('y_dropdown', 'value'),
    Input('size_dropdown', 'value')
)
def populate_datatable(n_intervals, x_dropdown, y_dropdown, size_dropdown):
    engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")
    df_pvt = pd.read_sql_table("pvt", con=engine)
    # df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
    # df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    # df.replace(',', '.', regex=True, inplace=True)

    fig = px.scatter(
        df_pvt,
        x=x_dropdown,
        y=y_dropdown,
        color="Горизонт",
        size=size_dropdown,
        text="Скважина",
        hover_data=["Скважина"]
    )
    return [
        dash_table.DataTable(
            id='pvt-table',
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": False}
                for i in df_pvt.columns
            ],
            data=df_pvt.to_dict('records'),
            editable=True,  # allow editing of data inside all cells
            filter_action="native",  # allow filtering of data by user ('native') or not ('none')
            sort_action="native",  # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",  # sort across 'multi' or 'single' columns
            column_selectable=False,  # allow users to select 'multi' or 'single' columns
            row_selectable="multi",  # allow users to select 'multi' or 'single' rows
            row_deletable=True,  # choose if user can delete a row (True) or not (False)
            selected_columns=[],  # ids of columns that user selects
            selected_rows=[],  # indices of rows that user selects
            page_action="native",  # all data is passed to the table up-front or not ('none')
            page_current=0,  # page number that user is on
            page_size=15,  # number of rows visible per page
            style_cell={
                'minWidth': 40, 'maxWidth': 160, 'width': 40
            }, # ensure adequate header width when text is shorter than cell's text
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['Скважина', 'Интервал отбора', 'Горизонт']
            ], # align text columns to left. By default they are aligned to right
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto'
            } # overflow cells' content into multiple lines
        ),
        fig
    ]

@callback(
    Output('pvt-table', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    [State('pvt-table', 'data'), State('pvt-table', 'columns')]
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
    Output('pvt_notification', 'children'),
    Input('save_to_postgres', 'n_clicks'),
    State('pvt-table', 'data')
)
def df_to_postgres(n_clicks, dataset):
    if n_clicks > 0:
        engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")
        df = pd.DataFrame(dataset)
        df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df.replace(',', '.', regex=True, inplace=True)
        df.to_sql("pvt", con=engine, if_exists='replace', index=False)
        return [
            html.Plaintext("Изменения сохранены.",
                           style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
        ]


# @callback(
#     Output('pvt_plot', 'figure'),
#     Input('interval_pvt', 'n_intervals'),
#     State('pvt-table', 'data'),
#     Input('x_dropdown', 'value'),
#     Input('y_dropdown', 'value'),
#     Input('size_dropdown', 'value')
# )
# def populate_datatable(n_intervals, dataset, x, y, size):
#     df_pvt = pd.DataFrame(dataset)
#     print(df_pvt.head())
#     fig = px.scatter(
#         df_pvt,
#         x=x,
#         y=y,
#         color="Горизонт",
#         size=size,
#         hover_data=["Скважина"]
#     )
#     return fig