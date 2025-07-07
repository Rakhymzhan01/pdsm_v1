from dash import html, register_page
import dash_bootstrap_components as dbc

register_page(__name__)

layout = html.Div(children=[
        dbc.Button("Вернутся на главную", size="lg", id="home_btn_404", href="/"),
], className="bg")


