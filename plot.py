import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
import numpy as np
import random
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import uuid
from functools import wraps


sys_random = random.SystemRandom()
US_BUSINESS_DAYS = CustomBusinessDay(calendar=USFederalHolidayCalendar())


def _validate(func):
    @wraps(func)
    def wrapper(self, data, ticker, freq, name, **kwargs):
        business_days = pd.bdate_range(data.Datetime.min().date(), data.Datetime.max().date(), freq=US_BUSINESS_DAYS)
        days_in_data = data.Datetime.dt.date.drop_duplicates()

        diff = business_days.difference(days_in_data)

        if not diff.empty:
            raise ValueError('There may be missing dates given periods')

    return wrapper


def _format(func):
    @wraps(func)
    def wrapper(self, data, ticker, freq, name, **kwargs):                
        num_xaxis_point = np.random.randint(5, 10)

        num_yyyymm = data.Datetime.dt.strftime('%Y-%m').nunique()
        num_yyyy = data.Datetime.dt.strftime('%Y').nunique()

        if num_yyyy > 5:
            format = self.format.get('yyyy')
        elif num_yyyymm > 5:
            _format = np.random.choice(['bbyyy', 'yyyybb', 'yyyy-mm']).item()
            format = self.format.get(_format)
        else:
            _format = np.random.choice(['y-m-dh-m', 'hmbdy']).item()
            format = self.format.get(_format)

        return func(self, data, ticker, freq, name, num_xaxis_point=num_xaxis_point, format=format)
    return wrapper


class plotly_stock():
    def __init__(self):
        self.buffer_ = []
        print("Setting up plotly gen...")

        self.format = {
            'y-m-dh-m': '%Y-%m-%d %H:%M',
            'hmbdy': '%H:%M %b %d, %Y',
            'bbyyyy': '%b %Y',
            'yyyy-mm': '%Y-%m',
            'yyyymm': '%Y %m',
            'yyyy': '%Y',
        }

    def __call__(self, ticker, threshold=250, rs=0, **kwargs):
        try:
            self.draw_lv1_chart(ticker, threshold=threshold, rs=rs, **kwargs)
        except ValueError:
            self.draw_lv1_chart(ticker, threshold=threshold//2, rs=rs, **kwargs)
        except:
            print('Unknown Error')

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

    @_validate
    @_format
    def draw_candlestick_chart(self,data,ticker,freq,name, **kwargs):
        fig = go.Figure(data=[go.Candlestick(x=data['Datetime'],
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'])])

        if (xaxis_index_step := int(len(data)/kwargs.get('num_xaxis_point'))) < 1:
            xaxis_index_step = 1
        fig.update_layout(
            yaxis_title=ticker,
            xaxis_type='category',
            xaxis=dict(
                tickmode='array',
                tickvals=data.index[::xaxis_index_step].values,
                ticktext=data.Datetime.dt.strftime(kwargs.get('format'))[::xaxis_index_step].values,
            ),
        )
        fig.write_image(f"images/{name}.png")

    @_validate
    @_format
    def draw_line_chart(self,data,ticker,freq,name, **kwargs):
        y = random.choice(["Open","High","Low","Close"])
        fig = px.line(data, x='Datetime', y=y, title=f'{ticker} {y}')

        if (xaxis_index_step := int(len(data)/kwargs.get('num_xaxis_point'))) < 1:
            xaxis_index_step = 1
        fig.update_layout(
            xaxis_type='category',
            xaxis=dict(
                tickmode='array',
                tickvals=data.index[::xaxis_index_step].values,
                ticktext=data.Datetime.dt.strftime(kwargs.get('format'))[::xaxis_index_step].values,
            )
        )
        fig.write_image(f"images/{name}.png")

    @_validate
    @_format
    def draw_bar_line_chart(self,data,ticker,freq,name, **kwargs):
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

        if (xaxis_index_step := int(len(data)/kwargs.get('num_xaxis_point'))) < 1:
            xaxis_index_step = 1
        fig.update_layout(
            xaxis_type='category',
            xaxis=dict(
                tickmode='array',
                tickvals=data.index[::xaxis_index_step].values,
                ticktext=data.Datetime.dt.strftime(kwargs.get('format'))[::xaxis_index_step].values,
            ),
            yaxis_title=ticker,
            )
        fig.write_image(f"images/{name}.png")

    def draw_lv1_chart(self,ticker,threshold=250,rs=0):
        random.seed(rs)

        chart_type,(func,multiplier) = sys_random.choice(list(self.plot_functions().items()))
        name = str(uuid.uuid4())

        threshold = threshold/multiplier
        data,freq = self.get_single_stock(ticker)

        start_slice = np.random.randint(0, len(data) - threshold)
        sliced = data.iloc[start_slice:int(start_slice + threshold), :].reset_index(drop=True)

        func(sliced,ticker,freq,name)

        self.buffer_.append([name, ticker, chart_type, freq, sliced.Datetime.values[0], sliced.Datetime.values[-1]])
