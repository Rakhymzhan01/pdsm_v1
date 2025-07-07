import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


# period = '3y'
# interval = '1d'
#
# oil_price_data = yf.download(tickers='CL=F', period=period, interval=interval)
# oil_price_data['KZDate'] = oil_price_data.index + pd.Timedelta(hours=9)
#
# currency_exchange_data = yf.download(tickers='KZT=X', period=period, interval=interval)
# currency_exchange_data['KZDate'] = currency_exchange_data.index + pd.Timedelta(hours=9)
#
# fig = make_subplots(
#     rows=2, cols=1, subplot_titles=("<b>Цена нефти Brent,</b> <i>$</i>", "<b>Курс доллара,</b> <i>₸</i>"),
#     horizontal_spacing=0.01, shared_xaxes=True
# )
#
# fig.add_trace(
#     go.Candlestick(
#         x=oil_price_data.KZDate,
#         open=oil_price_data['Open']['CL=F'],
#         high=oil_price_data['High']['CL=F'],
#         low=oil_price_data['Low']['CL=F'],
#         close=oil_price_data['Close']['CL=F']
#     ), row=1, col=1)
#
# fig.add_trace(
#     go.Candlestick(
#         x=currency_exchange_data.KZDate,
#         open=currency_exchange_data['Open']['KZT=X'],
#         high=currency_exchange_data['High']['KZT=X'],
#         low=currency_exchange_data['Low']['KZT=X'],
#         close=currency_exchange_data['Close']['KZT=X']
#     ), row=2, col=1)
#
# fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])],  # hide weekends
#                  rangeslider_visible=False)
#
# fig.update_layout(
#     # xaxis_rangeslider_visible=False,
#     margin=dict(l=0, r=0, t=25, b=0),
#     height=600,
#     template='plotly_white',
#     showlegend=False,
# )

fig = make_subplots(
    rows=2, cols=1, subplot_titles=("<b>Цена нефти Brent,</b> <i>$</i>", "<b>Курс доллара,</b> <i>₸</i>"),
    horizontal_spacing=0.01, shared_xaxes=True
)