from apps import karatobe_navigation as navigation
from apps import footer
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
import plotly.express as px
from flask_login import current_user

dash.register_page(__name__, path='/karatobe/gantt')


'''Data-------------------------------------------------'''
df_gantt = pd.read_csv('./assets/karatobe/gantt.csv')

gantt_chart = px.timeline(data_frame=df_gantt,
                          x_start="Start", x_end="Finish", y="ВИД РАБОТ", color="Resource",
                          range_x=[datetime.datetime(2022, 7, 1), datetime.datetime(2024, 1, 1)],
                          )
gantt_chart.add_vline(x=datetime.datetime.now(), line_width=3, line_color="black", line_dash="dash")
gantt_chart.update_layout(title_text='План график планируемых работ по месторождению', title_x=0.5, showlegend=False)
gantt_chart.update_yaxes(autorange="reversed")


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
        html.Br(),
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='gantt-chart',
                    config={'displayModeBar': False},
                    figure=gantt_chart),
                width={"size": 10, "offset": 1}
            )
        ),
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