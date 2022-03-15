import bokeh.plotting
import pandas as pd
import numpy as np
import warnings
import time
import statistics

# Local imorts
from backtester import account, help_funcs

class backtest():
    """An object representing a backtesting simulation."""
    def __init__(self, data):
        """Initate the backtest.

        :param data: An HLOCV+ pandas dataframe with a datetime index
        :type data: pandas.DataFrame

        :return: A bactesting simulation
        :rtype: backtest
        """  
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas dataframe")
        missing = set(['high', 'low', 'open', 'close', 'volume'])-set(data.columns)
        if len(missing) > 0:
            msg = "Missing {0} column(s), dataframe must be HLOCV+".format(list(missing))
            warnings.warn(msg)

        self.data = data

    def start(self, initial_capital, logic):
        """Start backtest.

        :param initial_capital: Starting capital to fund account
        :type initial_capital: float
        :param logic: A function that will be applied to each lookback period of the data
        :type logic: function

        :return: A bactesting simulation
        :rtype: backtest
        """
        # self.tracker = []
        self.account = account.Account(initial_capital)
        
        # Enter backtest ---------------------------------------------  
        starttime = time.time()
        
        # for (index,date,low,high,open,close,volume) in self.data.itertuples(): # Itertuples is faster than iterrows
        for index, today in self.data.iterrows():
            
            # equity = self.account.total_value(close)
            date = today["date"]
            equity = self.account.total_value(today['close'])

            # Update account variables
            self.account.date = date
            self.account.equity.append(equity)

            # Execute trading logic
            lookback = self.data[0:index+1]

            logic(self.account, lookback)

            # Cleanup empty positions
            self.account.purge_positions()

        print("Backtest completed in {0} seconds".format(time.time() - starttime))
            
        # ------------------------------------------------------------

    def results(self):   
        """Print results"""           
        print("-------------- Results ----------------\n")
        being_price = self.data.iloc[0]['open']
        final_price = self.data.iloc[-1]['close']

        pc1 = help_funcs.percent_change(being_price, final_price)
        print("Buy and Hold : {0}%".format(round(pc1*100, 2)))
        print("Net Profit   : {0}".format(round(help_funcs.profit(self.account.initial_capital, pc1), 2)))
        
        pc2 = help_funcs.percent_change(self.account.initial_capital, self.account.total_value(final_price))
        print("Strategy     : {0}%".format(round(pc2*100, 2)))
        print("Net Profit   : {0}".format(round(help_funcs.profit(self.account.initial_capital, pc2), 2)))

        longs  = len([t for t in self.account.opened_trades if t.type_ == 'long'])
        sells  = len([t for t in self.account.closed_trades if t.type_ == 'long'])
        shorts = len([t for t in self.account.opened_trades if t.type_ == 'short'])
        covers = len([t for t in self.account.closed_trades if t.type_ == 'short'])

        print("Longs        : {0}".format(longs))
        print("Sells        : {0}".format(sells))
        print("Shorts       : {0}".format(shorts))
        print("Covers       : {0}".format(covers))
        print("--------------------")
        print("Total Trades : {0}".format(longs + sells + shorts + covers))
        print("\n---------------------------------------")
        return [round(pc1*100, 2),round(pc2*100, 2),longs,sells,shorts,covers,statistics.stdev(self.account.equity),statistics.stdev([price*self.account.initial_capital/self.data.iloc[0]['open'] for price in self.data['open']]), ]
    
    def chart(self, show_trades=False, title="Equity Curve"):
        """Chart results.

        :param show_trades: Show trades on plot
        :type show_trades: bool
        :param title: Plot title
        :type title: str
        """
        bokeh.plotting.output_file("results/" + title + ".html", title=title)
        p = bokeh.plotting.figure(x_axis_type="datetime", plot_width=1000, plot_height=400, title=title)
        p.grid.grid_line_alpha = 0.3
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Equity'
        shares = self.account.initial_capital/self.data.iloc[0]['open']
        base_equity = [price*shares for price in self.data['open']]     
        p.line(self.data['date'], base_equity, color='#CAD8DE', legend_label='Buy and Hold')
        p.line(self.data['date'], self.account.equity, color='#49516F', legend_label='Strategy')
        p.legend.location = "top_left"

        if show_trades:
            for trade in self.account.opened_trades:
                try:
                    x = time.mktime(trade.date.timetuple())*1000
                    y = self.account.equity[np.where(self.data['date'] == trade.date.strftime("%Y-%m-%d"))[0][0]]
                    if trade.type_ == 'long': p.circle(x, y, size=6, color='green', alpha=0.5)
                    elif trade.type_ == 'short': p.circle(x, y, size=6, color='red', alpha=0.5)
                except Exception as e:
                    print(e)
                    pass

            for trade in self.account.closed_trades:
                try:
                    x = time.mktime(trade.date.timetuple())*1000
                    y = self.account.equity[np.where(self.data['date'] == trade.date.strftime("%Y-%m-%d"))[0][0]]
                    if trade.type_ == 'long': p.circle(x, y, size=6, color='blue', alpha=0.5)
                    elif trade.type_ == 'short': p.circle(x, y, size=6, color='orange', alpha=0.5)
                except:
                    pass
        bokeh.plotting.show(p)
    
    def plotlyplotting(self, show_trades=False, title="Equity Curve"):

        import plotly.express as px

        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
        fig.show()