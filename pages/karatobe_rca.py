from apps import karatobe_navigation as navigation
from apps import footer
from dash import register_page, dcc, html, callback, Output, Input, clientside_callback
import dash_bootstrap_components as dbc
import pandas as pd
# from skimage import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask_login import current_user


register_page(__name__, path='/karatobe/rca')


'''Data-------------------------------------------'''
df_tops_new = pd.read_csv('./assets/karatobe/tops_short.csv', encoding="cp1251")

border = {"border":"1px black solid"}
config = {
    'displayModeBar': True,
    'displaylogo': False,
    # 'doubleClick': 'reset',
    # 'doubleClickDelay': 100,
    # 'edits': {'legendPosition': True, 'titleText': True},
    'scrollZoom': True,
    'modeBarButtonsToRemove': [
        'zoom2d',
        # 'pan2d',
        'select2d',
        'lasso2d',
        'zoomIn2d',
        'zoomOut2d',
        'autoScale2d',
        # 'resetScale2d'

    ],
}


'''Containers-------------------------------------------'''
plots = dbc.Container([
    dbc.Col([
        dcc.Dropdown(id="rca-well-selection", options=['333', '338', 'КН-2', 'КН-3', 'КН-4'], value='КН-2', clearable=False)], width={"size": 2, "offset": 5}),
    dbc.Col([
        dcc.Loading(type="default",
                    children=dcc.Graph(
                        id='rca-plot',
                        config=config)
                    )
    ], width={"size": 10, "offset": 1}, style=border)
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
            dcc.Interval(id='interval_pg_rca', interval=86400000 * 7, n_intervals=0),
            dcc.Store(id='screen_rca', storage_type='memory'),
            navigation.navbar,
            plots,
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
clientside_callback(
    """
    function(n_intervals) {
        var w = window.innerWidth;
        var h = window.innerHeight;
        return {'height': h, 'width': w};
    }
    """,
    Output('screen_rca', 'data'),
    Input('interval_pg_rca', 'n_intervals')
)


@callback(
    Output('rca-plot', 'figure'),
    Input('rca-well-selection', 'value'),
    Input('screen_rca', 'data')
)
def core(well, screen):
    min = 600
    max = 800

    # https://stackoverflow.com/questions/65056691/plotly-how-to-show-more-than-2-x-axes-titles-ranges-on-the-same-subplot
    core_plot = make_subplots(rows=1, cols=6, column_widths=[5, 5, 5, 5, 5, 3], horizontal_spacing=0.015, shared_yaxes=True)

    '''Well Logs'''
    try:
        log = pd.read_csv(f"./assets/karatobe/{well}/log.csv")
        core_plot.add_trace(
            go.Scatter(x=log.GR, y=log.DEPT, name='GR', showlegend=False, mode='none', line_color='brown',
                       fill='tozerox', fillcolor='brown', xaxis="x1", yaxis="y1"))
        core_plot.add_trace(
            go.Scatter(x0=200, dx=0, y=log.DEPT, name=None, showlegend=False, fill='tonextx', mode='none',
                       fillcolor='yellow', xaxis="x1", yaxis="y1"))
        core_plot.add_trace(
            go.Scatter(x=log.HCAL, y=log.DEPT, name='CALI', showlegend=False, mode='lines', line_color='blue',
                       xaxis="x11", yaxis="y1"))

        core_plot.add_trace(
            go.Scatter(x=log.RHOZ, y=log.DEPT, name='DENS', showlegend=False, mode='lines', line_color="red",
                       xaxis="x2", yaxis="y2"))
        core_plot.add_trace(
            go.Scatter(x=log.TNPH, y=log.DEPT, name='NPOR', showlegend=False, mode='lines', line_color="blue",
                       xaxis="x12", yaxis="y2"))

        core_plot.add_trace(
            go.Scatter(x=log['RLA1'], y=log.DEPT, name='RLA1', showlegend=False, mode='lines', line_color="black",
                       xaxis="x3", yaxis="y3"))
        core_plot.add_trace(
            go.Scatter(x=log['RLA5'], y=log.DEPT, name='RLA5', showlegend=False, mode='lines', line_color="purple",
                       xaxis="x3", yaxis="y3"))
    except Exception as error:
        print("An exception occurred with Log Data:", error)

    '''CORE'''
    try:
        core = pd.read_csv(f"./assets/karatobe/{well}/core.csv")
        min = core.Depth.min()
        max = core.Depth.max()
        min = min - (max - min)/10
        max = max + (max - min)/10

        core_plot.add_trace(
            go.Scatter(
                x=core["GD"], y=core["Depth"], name='Grain Density', showlegend=True,
                mode='markers', marker_color="red", marker_symbol="x-dot",
                xaxis="x2", yaxis="y2"))
        core_plot.add_trace(
            go.Scatter(
                x=core["Porosity"], y=core["Depth"], name='Porosity', showlegend=True,
                mode='markers', marker_color="blue", marker_symbol="x-dot",
                xaxis="x12", yaxis="y2"))
        core_plot.add_trace(
            go.Scatter(
                x=core["SW"], y=core["Depth"], name='Sw', showlegend=True,
                mode='markers', marker_color="blue",
                xaxis="x4", yaxis="y4"))
        core_plot.add_trace(
            go.Scatter(
                x=core["Kg"], y=core["Depth"], name='Permeability', showlegend=True,
                mode='markers', marker_color="black",
                xaxis="x5", yaxis="y5"))
    except Exception as error:
        print("An exception occurred with Core Data:", error)

    '''Core Image'''
    # try:
    #     img = io.imread(f"./assets/karatobe/{well}/654_662.09.png")
    #     core_plot.add_trace(
    #         go.Image(
    #             z=img,
    #             dx=0.0007413177, dy=0.0007413177,
    #             x0=0, y0=654,
    #             xaxis="x6", yaxis="y6"
    #         ))
    # except Exception as error:
    #     print("An exception occurred with Core Image:", error)

    '''Well Tops'''
    try:
        df_top_new = df_tops_new[df_tops_new['well'] == well]

        for col in range(1, 6):
            for top in df_top_new.columns[1:]:
                if df_top_new.iloc[0][top] > 0:
                    core_plot.add_hline(y=df_top_new.iloc[0][top], line_dash="dot", line_color="indigo", col=col, annotation_text=top, annotation_position="top right")
    except Exception as error:
        print("An exception occurred with Top Data:", error)

    '''Update Layout'''
    if True:
        core_plot.update_layout(
            xaxis1=dict(
                title={'font': {'color': 'brown', 'size': 12}, 'text': 'GR'},
                anchor='y1',
                # side='top',
                range=[0, 200],
                tickfont={'color': 'brown', 'size': 12},
            ),
            xaxis11=dict(
                title={'font': {'color': 'blue', 'size': 12}, 'text': 'CALI'},
                anchor='free',
                overlaying='x1',
                side='right',
                range=[200, 300],
                tickfont={'color': 'blue', 'size': 12},
                showgrid=False,
                tickmode='linear',
                tick0=200,
                dtick=20
            ),
            xaxis2=dict(
                title={'font': {'color': 'red', 'size': 12}, 'text': 'DENS'},
                anchor='y2',
                # side='top',
                range=[1.95, 2.95],
                tickfont={'color': 'red', 'size': 12},
                tickmode='linear',
                tick0=1.95,
                dtick=0.25
            ),
            xaxis12=dict(
                title={'font': {'color': 'blue', 'size': 12}, 'text': 'NPOR'},
                anchor='free',
                overlaying='x2',
                side='right',
                range=[0.45, -0.15],
                tickfont={'color': 'blue', 'size': 12},
                showgrid=False,
                tickmode='linear',
                tick0=0.45,
                dtick=0.15
            ),
            xaxis3=dict(
                title={'font': {'color': 'purple', 'size': 12}, 'text': 'Resistivity'},
                anchor='y3',
                # side='top',
                range=[0, 2],
                type="log",
                tickfont={'color': 'purple', 'size': 12},
            ),
            xaxis4=dict(
                title={'font': {'color': 'blue', 'size': 12}, 'text': 'Sw'},
                anchor='y4',
                # side='top',
                range=[0, 100],
                tickfont={'color': 'blue', 'size': 12},
            ),
            xaxis5=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'Проницаемость по газу, мД'},
                anchor='y5',
                # side='top',
                range=[-2, 4],
                type="log",
                tickfont={'color': 'black', 'size': 12},
            ),
            yaxis1=dict(domain=[0.08, 1]),
            yaxis2=dict(domain=[0.08, 1]),
            yaxis3=dict(domain=[0.08, 1]),
            yaxis4=dict(domain=[0.08, 1]),
            yaxis5=dict(domain=[0.08, 1]),
            title_text=f"<b>{well}</b>", title_x=0.5, title_font=dict(size=16),
            margin=dict(l=60, r=20, t=60, b=20),
            paper_bgcolor="white",
            hovermode='y',
            autosize=True,
            height=(screen['height']-150),
        );

        core_plot.update_yaxes(title_text="Глубина", range=[max, min], row=1, col=1)
        core_plot.update_annotations(font_size=12)

    return core_plot