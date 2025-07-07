from apps import karatobe_navigation as navigation
from apps import footer
from functions import currency
import dash_bootstrap_components as dbc
from dash import register_page, dcc, html, callback, Output, Input

from flask_login import current_user
field = "karatobe"

register_page(__name__, path=f'/{field}/home')


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
    elif current_user.user_level.split('_')[0] in ["master", "all", field]:
        return html.Div([
            navigation.navbar,
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Markdown('## Добро пожаловать!'),
                    dcc.Markdown('Данный сайт предназначен для анализа данных месторождения _Каратюбе_.'),
                    dcc.Markdown('\n'),
                    dcc.Markdown('## Разделы'),
                    dcc.Markdown('**Дом:** Текущая домашняя страница.'),
                    dcc.Markdown('**Сводка:** Сводная информация по всему месторождению с тремя графиками:'),
                    html.Ul(children=[html.Li('Карта Накопленных отборов'),
                                      html.Li('Тепловая карта скважин'),
                                      html.Li('История Добычи')]),
                    dcc.Markdown('**Анализ:** Информационная панель для анализа по скважинам.'),
                    dcc.Markdown('**Корреляция:** Корреляция разрезов скважин.'),
                    dcc.Markdown('**Сейсмика:** Сейсмические профили по Inline / Xline.'),
                    dcc.Markdown('**Карта:** Географическое положение месторождения с пробуренными скважинами.'),
                    dcc.Markdown(
                        '**Гант:** Диаграмма Ганта  — это популярный тип столбчатых диаграмм для иллюстрации плана, графика работ по проекту.'),
                    dcc.Markdown('**База:** Производственная база данных по:'),
                    html.Ul(children=[html.Li('Добыче продукции'),
                                      html.Li('Истории геолого-технических мероприятий'),
                                      html.Li('Интервалов перфораций')]),
                    dcc.Markdown('## Нужна помощь?'),
                    html.A("Если вы хотите связаться с нами", href='aman.jymekeshov@gmail.com', target="_blank"),
                ], width={"size": 6, "offset": 1}, className="body"),
                dbc.Col([
                    dcc.Interval(id='interval_pg_home', interval=86400000 * 7, n_intervals=0),
                    dcc.Loading(
                        type="default",
                        children=dbc.Card([
                                    dbc.CardBody(dcc.Graph(id='currency_fig', config={'displayModeBar': False}))
                                ], color="secondary", inverse=False, outline=True)
                    ),
                ], width={"size": 3, "offset": 1}, className="body"),
            ]),
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
    Output('currency_fig', 'figure'),
    Input('interval_pg_home', 'n_intervals')
)
def update_page(n_intervals):
    return currency.fig