from apps import footer
from dash import register_page, html, dcc
import dash_bootstrap_components as dbc
from flask_login import current_user


register_page(__name__, path='/')


'''Layout-----------------------------------------------'''
def layout():
    if not current_user.is_authenticated:
        return html.Div(
            [
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H2(children="Авторизация:"),
                        html.Br(),
                        dcc.Input(placeholder="Введите имя пользователя", type="text", id="uname-box"),
                        dcc.Input(placeholder="Введите ваш пароль", type="password", id="pwd-box"),
                        html.Button(children="Войти", n_clicks=0, type="submit", id="login-button"),
                        html.Br(),
                        html.Br(),
                        html.Div(children="", id="output-state")
                    ], width={"size": 6, "offset": 3})
                ], align="center")
            ]
        )
    else:
        if current_user.username == "Aman":
            display_list = [
                dcc.Link("IC Petroleum", href="/karatobe/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("Каспий нефть", href="/airankol/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("Кристалл Менеджмент", href="/crystalmanagment/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("Оценка", href="/exploration/map", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("Free Tools", href="/guest/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("ГКЗ", href="/gkz/home", style={'font-size': 24, 'font-weight': 'bold'}),
                # html.Br(),
                # dcc.Link("Арыстановское", href="/arystan/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("Кокжиде", href="/kokzhide/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("KKK", href="/kkk/home", style={'font-size': 24, 'font-weight': 'bold'}),
            ]
        elif current_user.user_level.split('_')[0] in ["all"]:
            display_list = [
                dcc.Link("IC Petroleum", href="/karatobe/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("Каспий нефть", href="/airankol/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("Кристалл Менеджмент", href="/crystalmanagment/home", style={'font-size': 24, 'font-weight': 'bold'}),
                html.Br(),
                dcc.Link("Оценка", href="/exploration/map", style={'font-size': 24, 'font-weight': 'bold'}),
            ]
        elif current_user.user_level.split('_')[0] in ["karatobe"]:
            display_list = [
                dcc.Link("IC Petroleum", href="/karatobe/home", style={'font-size': 24, 'font-weight': 'bold'})
            ]
        elif current_user.user_level.split('_')[0] in ["airankol"]:
            display_list = [
                dcc.Link("Каспий нефть", href="/airankol/home", style={'font-size': 24, 'font-weight': 'bold'})
            ]
        elif current_user.user_level.split('_')[0] in ["crystalmanagment"]:
            display_list = [
                dcc.Link("Кристалл Менеджмент", href="/crystalmanagment/home", style={'font-size': 24, 'font-weight': 'bold'})
            ]
        return html.Div([
            html.Br(),
            dbc.Row([
                dbc.Col(display_list, width={"size": 6, "offset": 3})
            ], align="center"),
            footer.footer
        ])
