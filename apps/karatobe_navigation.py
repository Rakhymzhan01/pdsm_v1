import dash
from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc


navbar = dbc.Navbar(
    dbc.Container(
        [

            dbc.Row([
                dbc.Col([
                    html.Img(src=dash.get_asset_url('logo.png'), height="40px"),
                    dbc.NavbarBrand("Каратюбе", className="ms-2 brandName")
                ], width={"size":"auto"})
            ], align="center", className="g-0"),

            dbc.Row([
                dbc.Col([dbc.NavbarToggler(id="karatobe_toggler_left", n_clicks=0)])
            ]), # keep links to the left

            dbc.Row([
                dbc.Col([
                    dbc.Collapse(
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink("Дом", href="/karatobe/home", className="navLink")),
                            dbc.NavItem(dbc.NavLink("Сводка", href="/karatobe/dash", className="navLink")),
                            dbc.NavItem(dbc.NavLink("Анализ", href="/karatobe/analysis", className="navLink")),
                            dbc.NavItem(dbc.NavLink("Конструктор", href="/karatobe/construction", className="navLink")),
                            dbc.NavItem(dbc.NavLink("Подсчетный план", href="/karatobe/map", className="navLink")),
                            dbc.NavItem(dbc.NavLink("Тест", href="/karatobe/test", className="navLink")),
                            dbc.NavItem(dbc.NavLink("Гант", href="/karatobe/gantt", className="navLink")),
                            dbc.NavItem(dbc.DropdownMenu(
                                children=[
                                    dbc.DropdownMenuItem("База Скважин", href="/karatobe/wells", className="navLink"),
                                    dbc.DropdownMenuItem("База Добычи", href="/karatobe/data", className="navLink"),
                                    dbc.DropdownMenuItem("База PVT", href="/karatobe/pvt", className="navLink"),
                                    dbc.DropdownMenuItem("База КРС/ПРС", href="/karatobe/wo", className="navLink"),
                                    dbc.DropdownMenuItem("База Перфорации", href="/karatobe/perf", className="navLink"),
                                    dbc.DropdownMenuItem("База Конструкции", href="/karatobe/comp", className="navLink"),
                                    dbc.DropdownMenuItem("База Отбивок", href="/karatobe/top", className="navLink"),
                                ],
                                nav=True,
                                in_navbar=True,
                                label="База",
                                className="navLink"
                            )),
                            dbc.NavItem(dbc.DropdownMenu(
                                children=[
                                    dbc.DropdownMenuItem("Анализ ГИС", href="/quanti", className="navLink"),
                                    dbc.DropdownMenuItem("XPT", href="/karatobe/xpt", className="navLink"),
                                    dbc.DropdownMenuItem("СтИК", href="/karatobe/rca", className="navLink"),
                                    dbc.DropdownMenuItem("СпИК", href="/karatobe/scal", className="navLink"),
                                ],
                                nav=True,
                                in_navbar=True,
                                label="Инструменты",
                                className="navLink"
                            ))
                        ]),
                        id="karatobe_collapse_left",
                        is_open=False,
                        navbar=True
                    )
                ])], align="center", className="g-0"),

            dbc.Row([
                dbc.Col([dbc.NavbarToggler(id="karatobe_toggler_right", n_clicks=0)])
            ]), # keep links to the left

            dbc.Row([
                dbc.Col([
                    dbc.Collapse(
                        dbc.Nav([
                                dbc.NavItem(dbc.NavLink("Активы", href="/", className="navbar-nav ml-auto mr-3 navLink")),
                                dbc.NavItem(dbc.NavLink("Аккаунт", href="/account", className="navbar-nav ml-auto mr-3 navLink")),
                                dbc.NavItem(dbc.NavLink("Выход", href="/logout", className="navbar-nav ml-auto mr-3 navLink"))
                            ]),
                        id="karatobe_collapse_right",
                        is_open=False,
                        navbar=True
                    )
                ])], align="center", className="g-0")

        ], fluid=True),
    sticky="top",
    color="LightSteelBlue",
    style={"margin-bottom": "10px"}
)


@callback(
    Output('karatobe_collapse_right', 'is_open'),
    Input('karatobe_toggler_right', 'n_clicks'),
    State('karatobe_collapse_right', 'is_open')
)
def toggle_navbar_collapse_right(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output('karatobe_collapse_left', 'is_open'),
    Input('karatobe_toggler_left', 'n_clicks'),
    State('karatobe_collapse_left', 'is_open')
)
def toggle_navbar_collapse_left(n, is_open):
    if n:
        return not is_open
    return is_open