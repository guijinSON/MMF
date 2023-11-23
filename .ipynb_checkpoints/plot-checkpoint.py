import numpy as np
import random
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import uuid

sys_random = random.SystemRandom()

class plotly_stock():
    def __init__(self):
        self.buffer_ = []
        print("Setting up plotly gen...")

    def plot_functions(self):

        funcs_ = {
            "candlestick":[self.draw_candlestick_chart,4],
            "line":[self.draw_line_chart,1],
            "barline":[self.draw_bar_line_chart,2]
        }

        return funcs_

    def get_frequency(self):
        freq = random.choice(["1m","2m","5m","15m","30m","60m","90m","1h","1d","5d","1wk","1mo","3mo"])
        return freq

    def get_date_range(
                    self,
                    freq,
                    date_dict={
                        "1m":6,
                        "2m":59,
                        "5m":59,
                        "15m":59,
                        "30m":59,
                        "90m":59,
                        "1h":300}):
        end_date = datetime.now()
        if freq in date_dict.keys():
            start_date = end_date - timedelta(days=date_dict[freq])
            return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
        else:
            return None, end_date.strftime('%Y-%m-%d')

    def get_single_stock(self,ticker):
        ticker = yf.Ticker(ticker)
        freq = self.get_frequency()
        start_date, end_date = self.get_date_range(freq)
        if start_date is None:
            history = ticker.history(period='max',end=end_date, interval=freq)
        else:
            history = ticker.history(start=start_date, end=end_date, interval=freq)
        history.reset_index(inplace=True)
        history.rename(columns={"Date":"Datetime"},inplace=True)
        return history,freq

    def draw_candlestick_chart(self,data,ticker,freq,name):
        if freq in ["1d","5d","1wk","1mo","3mo"]:
            rb = [dict(bounds=["sat", "mon"])]
        else:
            rb = [
            dict(bounds=[17, 9], pattern="hour"), #hide hours outside of 9am-5pm
            dict(bounds=["sat", "mon"])
        ]

        fig = go.Figure(data=[go.Candlestick(x=data['Datetime'],
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'])])
        
        fig.update_layout(yaxis_title=ticker)
        fig.update_xaxes(rangebreaks=rb)
        fig.write_image(f"images/{name}.png")

    def draw_line_chart(self,data,ticker,freq,name):
        y = random.choice(["Open","High","Low","Close"])
        fig = px.line(data, x='Datetime', y=y, title=f'{ticker} {y}')
        fig.write_image(f"images/{name}.png")

    def draw_bar_line_chart(self,data,ticker,freq,name):
        if freq in ["1d","5d","1wk","1mo","3mo"]:
            rb = [dict(bounds=["sat", "mon"])]
        else:
            rb = [
            dict(bounds=[17, 9], pattern="hour"), #hide hours outside of 9am-5pm
            dict(bounds=["sat", "mon"])
        ]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Bar(
            x=data['Datetime'],
            y=data["Volume"],
            name="volume"
            )
        )

        fig.add_trace(go.Scatter(
            x=data['Datetime'],
            y=data["Close"],
            name="Close"
            ),
            secondary_y=True)
        fig.update_layout(yaxis_title=ticker)
        fig.update_xaxes(rangebreaks=rb)
        fig.write_image(f"images/{name}.png")

    def draw_lv1_chart(self,ticker,threshold=250,rs=0):
        random.seed(rs)
        # chart_type,(func,multiplier) = random.choices(list(self.plot_functions().items()))[0]
        chart_type,(func,multiplier) = sys_random.choice(list(self.plot_functions().items()))
        name = str(uuid.uuid4())
        
        threshold = threshold/multiplier
        data,freq = self.get_single_stock(ticker)
        
        start_slice = np.random.randint(0, len(data) - threshold)
        sliced = data.iloc[start_slice:int(start_slice + threshold), :]
        func(sliced,ticker,freq,name)
        
        self.buffer_.append([name, ticker, chart_type, freq, sliced.Datetime.values[0], sliced.Datetime.values[-1]])
