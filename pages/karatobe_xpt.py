from apps import karatobe_navigation as navigation
from apps import footer
import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask_login import current_user
import psycopg2, lasio
from os import scandir


dash.register_page(__name__, path='/karatobe/xpt')


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
        dcc.Dropdown(id="xpt-well-selection", options=['КН-2', 'КН-4', '359'], value='359', clearable=False)], width={"size": 2, "offset": 5}),
    dbc.Col([
        dcc.Loading(type="default",
                    children=dcc.Graph(
                        id='xpt-plot',
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

# Callbacks--------------------------------------------
@callback(
    Output('xpt-plot', 'figure'),
    Input('xpt-well-selection', 'value')
)
def xpt(well):
    # https://stackoverflow.com/questions/65056691/plotly-how-to-show-more-than-2-x-axes-titles-ranges-on-the-same-subplot
    xpt_plot = make_subplots(rows=1, cols=5, column_widths=[5, 5, 5, 10, 5], horizontal_spacing=0.01,
                             shared_yaxes=True)

    """Well Log"""
    try:
        path = f"./assets/karatobe/LOGs/{well}"
        for file in scandir(path):
            log = lasio.read(file.path, engine='normal').df()
            log.dropna(inplace=True)
            xpt_plot.add_trace(
                go.Scatter(x=log.GR, y=log.index, name='GR', showlegend=False, mode='none', line_color='brown',
                           fill='tozerox', fillcolor='brown', xaxis="x1", yaxis="y1"))
            xpt_plot.add_trace(
                go.Scatter(x0=200, dx=0, y=log.index, name=None, showlegend=False, fill='tonextx', mode='none',
                           fillcolor='yellow', xaxis="x1", yaxis="y1"))
            xpt_plot.add_trace(
                go.Scatter(x=log.CALI, y=log.index, name='CALI', showlegend=False, mode='lines', line_color='blue',
                           xaxis="x11", yaxis="y1"))

            xpt_plot.add_trace(
                go.Scatter(x=log.RHOZ, y=log.index, name='DENS', showlegend=False, mode='lines', line_color="red",
                           xaxis="x2", yaxis="y2"))
            xpt_plot.add_trace(
                go.Scatter(x=log.TNPH, y=log.index, name='NPOR', showlegend=False, mode='lines', line_color="blue",
                           xaxis="x12", yaxis="y2"))

            xpt_plot.add_trace(
                go.Scatter(x=log['RLA1'], y=log.index, name='RLA1', showlegend=False, mode='lines',
                           line_color="black",
                           xaxis="x3", yaxis="y3"))
            xpt_plot.add_trace(
                go.Scatter(x=log['RLA5'], y=log.index, name='RLA5', showlegend=False, mode='lines',
                           line_color="purple",
                           xaxis="x3", yaxis="y3"))
            break
    except Exception as error:
        print("An exception occurred at LAS upload, with error:", error)

    """XPT Data"""
    try:
        xpt = pd.read_csv(f"./assets/karatobe/XPTs/{well}/XPT.csv")

        xpt_valid = xpt[xpt["DD Mobility"] >= 0.6].copy()
        xpt_valid.reset_index(inplace=True)

        xpt_non_valid = xpt[xpt["DD Mobility"] < 0.6].copy()
        xpt_non_valid.reset_index(inplace=True)

        xpt_valid["DEPT_shift"] = xpt_valid["Probe MD"].diff(periods=-1)
        xpt_valid["Gradient"] = xpt_valid["Formation Pres."].diff(periods=-1) / xpt_valid["Probe MD"].diff(periods=-1) * 10.332
        xpt_valid["Gradient"] = xpt_valid["Gradient"].round(2)
        xpt_valid["P_Color"] = "green"
        xpt_valid["M_Color"] = "lime"

        for i, row in xpt_valid.iterrows():
            if row.Gradient >= 1.1 or row.Gradient < 0.1 or pd.isna(row.Gradient):
                xpt_valid.at[i, 'Gradient'] = np.NaN
                xpt_valid.at[i, 'P_Color'] = "aqua"
            if row['DD Mobility'] < 0.6 or pd.isna(row['DD Mobility']):
                xpt_valid.at[i, 'M_Color'] = "red"
                xpt_valid.at[i, 'Gradient'] = np.NaN
                xpt_valid.at[i, 'P_Color'] = "red"
            if row['DEPT_shift'] > 15:
                xpt_valid.at[i, 'Gradient'] = np.NaN

        '''XPT Plot'''
        xpt_plot.add_trace(go.Scatter(
            x=xpt_non_valid["Formation Pres."], y=xpt_non_valid["Probe MD"],
            name='XPT Pres.[атм]', legendgroup="Pres.",
            mode='markers', marker_color="red", showlegend=False,
            xaxis="x4", yaxis="y4"))
        xpt_plot.add_trace(go.Scatter(
            x=xpt_valid["Formation Pres."], y=xpt_valid["Probe MD"],
            name='XPT Pres.[атм]', legendgroup="Pres.",
            mode='markers', marker_color=xpt_valid["M_Color"],
            xaxis="x4", yaxis="y4"))

        xpt_plot.add_trace(
            go.Scatter(x=xpt["Mud Pres. Before"], y=xpt["Probe MD"], name='Mud Pres.[атм]', mode='markers',
                       marker_color="orange", marker_symbol="diamond", xaxis="x4", yaxis="y4"))

        xpt_plot.add_trace(
            go.Scatter(x=[0, 87.108], y=[0, 900], name='Hydrostatic Pres.[psi]', mode='lines', line_color="blue",
                       xaxis="x4", yaxis="y4"))

        xpt_plot.add_trace(go.Scatter(
            x=xpt_non_valid["DD Mobility"], y=xpt_non_valid["Probe MD"],
            name='Mobility[mD/cP]', legendgroup="Mob.", showlegend=False,
            mode='markers', marker_color="red",
            xaxis="x5", yaxis="y5"))
        xpt_plot.add_trace(go.Scatter(
            x=xpt_valid["DD Mobility"], y=xpt_valid["Probe MD"],
            name='Mobility[mD/cP]', legendgroup="Mob.",
            mode='markers', marker_color=xpt_valid["M_Color"],
            xaxis="x5", yaxis="y5"))
        xpt_plot.add_vrect(x0=0.01, x1=1, line_width=0, fillcolor="red", opacity=0.1, col=5)


        '''Gradient Annotation'''
        for i, gradient in enumerate(xpt_valid.Gradient[:-1]):
            if gradient > 0.95:
                xpt_plot.add_annotation(
                    x=(xpt_valid["Formation Pres."][i] + xpt_valid["Formation Pres."][i + 1]) / 2,
                    y=(xpt_valid["Probe MD"][i] + xpt_valid["Probe MD"][i + 1]) / 2,
                    text=str(gradient) + " т/м3",
                    showarrow=True,
                    font=dict(size=20, color="blue"),
                    # align="center",
                    arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#636363",
                    ax=-50, ay=0,
                    # bordercolor="#c7c7c7", borderwidth=2, borderpad=4,
                    # bgcolor="blue", opacity=0.8,
                    row=1, col=4
                )
            elif gradient > 0:
                xpt_plot.add_annotation(
                    x=(xpt_valid["Formation Pres."][i] + xpt_valid["Formation Pres."][i + 1]) / 2,
                    y=(xpt_valid["Probe MD"][i] + xpt_valid["Probe MD"][i + 1]) / 2,
                    text=str(gradient) + " т/м3",
                    showarrow=True,
                    font=dict(size=20, color="green"),
                    # align="center",
                    arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#636363",
                    ax=-50, ay=0,
                    # bordercolor="#c7c7c7", borderwidth=2, borderpad=4,
                    # bgcolor="lime", opacity=0.8,
                    row=1, col=4
                )

                # ax31.annotate(gradient, (xpt["Formation Pres."][i], xpt["Probe MD"][i]))
    except Exception as error:
        print("An exception occurred at XPT Data, with error:", error)

    """Well Top"""
    try:
        con = psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres",
                               password="akzhol2030")
        cur = con.cursor()

        cur.execute(f" SELECT * FROM tops WHERE well='{well}' ")
        top = cur.fetchall()
        tops_columns = ['well', 'XII_a', 'XI_1_Br', 'XI_br', 'X_Br', 'IX Br', 'VIII_K1b',
                        'VII g(J2-?)', 'J2_IIIa', 'V_J', 'V_J2_b', 'V-1', 'V2_J2', 'V3_J2',
                        'V3_b', 'J1-IV-2', 'J1-IV-1', 'T_BJ(base_IV-1)', 'T Upper Part', 'T-II',
                        'Top_P2(I-P)', 'P1k_anh', 'P1k_gal']
        top = pd.DataFrame(top, columns=tops_columns)

        con.close()

        for t in top.columns[1:]:
            if top.iloc[0][t] is not None:
                xpt_plot.add_hline(y=float(top.iloc[0][t]), line_dash="dot", line_color="indigo", col="all",
                                   annotation_text=t, annotation_position="top right")
    except Exception as error:
        print("An exception occurred at well top download, with error:", error)

    '''Update Layout'''
    if True:
        xpt_plot.update_layout(
            xaxis1=dict(
                title={'font': {'color': 'brown', 'size': 12}, 'text': 'GR'},
                anchor='y1',
                # side='top',
                range=[0, 200],
                tickfont={'color': 'brown', 'size': 12},
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            xaxis11=dict(
                title={'font': {'color': 'blue', 'size': 12}, 'text': 'CALI'},
                anchor='free',
                overlaying='x1',
                side='right',
                range=[200, 300],
                tickfont={'color': 'blue', 'size': 12},
                showline=True, linewidth=1, linecolor='black', mirror=True,
                showgrid=False,
                tickmode='linear',
                tick0=200,
                dtick=20,
            ),
            xaxis2=dict(
                title={'font': {'color': 'red', 'size': 12}, 'text': 'DENS'},
                anchor='y2',
                # side='top',
                range=[1.65, 2.65],
                tickfont={'color': 'red', 'size': 12},
                showline=True, linewidth=1, linecolor='black', mirror=True,
                tickmode='linear',
                tick0=1.65,
                dtick=0.25
            ),
            xaxis12=dict(
                title={'font': {'color': 'blue', 'size': 12}, 'text': 'NPOR'},
                anchor='free',
                overlaying='x2',
                side='right',
                range=[0.6, 0],
                tickfont={'color': 'blue', 'size': 12},
                showline=True, linewidth=1, linecolor='black', mirror=True,
                showgrid=False,
                tickmode='linear',
                tick0=0.6,
                dtick=0.15
            ),
            xaxis3=dict(
                title={'font': {'color': 'purple', 'size': 12}, 'text': 'Resistivity'},
                anchor='y3',
                # side='top',
                range=[-1, 2],
                type="log",
                tickfont={'color': 'purple', 'size': 12},
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            xaxis4=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'XPT Pressure [атм]'},
                anchor='y4',
                # side='top',
                range=[10, 110],
                tickfont={'color': 'black', 'size': 12},
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            xaxis5=dict(
                title={'font': {'color': 'black', 'size': 12}, 'text': 'XPT Mobility [cP/mD]'},
                anchor='y5',
                # side='top',
                range=[-2, 3],
                type="log",
                tickfont={'color': 'black', 'size': 12},
                showline=True, linewidth=1, linecolor='black', mirror=True,
            ),
            yaxis1=dict(
                title={'font': {'color': 'black', 'size': 16}, 'text': 'Глубина'},
                domain=[0.05, 1],
                range=[max(log.index), min(log.index)],
                tickmode='linear',
                tick0=max(log.index),
                dtick=50,
                minor=dict(ticklen=5, tickcolor="black", tickmode='auto', nticks=5, showgrid=True),
            ),
            yaxis2=dict(domain=[0.05, 1], showline=True, linewidth=2, linecolor='black', mirror=True),
            yaxis3=dict(domain=[0.05, 1], showline=True, linewidth=2, linecolor='black', mirror=True),
            yaxis4=dict(domain=[0.05, 1], showline=True, linewidth=2, linecolor='black', mirror=True),
            yaxis5=dict(domain=[0.05, 1], showline=True, linewidth=2, linecolor='black', mirror=True),
            title_text=f"<b>{well}</b>", title_x=0.5, title_font=dict(size=16),
            margin=dict(l=60, r=20, t=60, b=20),
            template="plotly_white",
            hovermode='y',
            autosize=True,
            height=1125
        );

        xpt_plot.update_annotations(font_size=12)

    return xpt_plot