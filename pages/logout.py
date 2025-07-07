import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import logout_user, current_user

dash.register_page(__name__)


def layout():
    if current_user.is_authenticated:
        logout_user()
    return html.Div(
        [
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div(html.H2("Вы вышли из системы – пожалуйста, войдите")),
                    html.Br(),
                    dcc.Link("Войти", href="/", style={'font-size': 24, 'font-weight': 'bold'}),
                ], width={"size": 6, "offset": 3})
            ], align="center")
        ]
    )