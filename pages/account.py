from dash import dcc, html, register_page
import dash_bootstrap_components as dbc

from apps import footer

from flask_login import current_user


register_page(__name__, path='/account')


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

    return html.Div([
        dcc.Interval(id='interval_pg_account', interval=86400000 * 7, n_intervals=0),
        html.Br(),
        dbc.Col([
            html.H2("Информация об аккаунте"),
            html.Br(),
            html.Br(),
            html.H4("Пользователь: " + current_user.username),
            html.Br(),
            html.H4("Хотите изменить пароль?"),
            dbc.Form([
                html.Div([
                        dbc.Label("Введите новый пароль", html_for="example-email"),
                        dbc.Input(
                            type="password",
                            id="password",
                            placeholder="Введите новый пароль")
                    ], className="mb-3"),
                html.Div([
                        dbc.Label("Подтвердите новый пароль", html_for="example-password"),
                        dbc.Input(
                            type="password",
                            id="re-enter-password",
                            placeholder="Подтвердите новый пароль",
                        )
                    ], className="mb-3"),
                dbc.Button(children="ИЗМЕНИТЬ", id="change_button", color="warning")
            ]),
            html.Div(id='password_changed_placeholder') # Create notification when saving to DataBase
        ], width={"size":6, "offset":1}, className="body"),

        footer.footer
    ])
