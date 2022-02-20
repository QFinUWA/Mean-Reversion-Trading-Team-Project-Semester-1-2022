import pandas as pd
import API_Interface as api
import time
import multiprocessing as mp

# local imports
from backtester import engine

# read in data preserving dates
df = pd.read_csv("data/USDT_LTC.csv", parse_dates=[0])
# df = api.get_intraday_extended('AAPL', 'all', '', '60min', True, False)
# df = api.get_intraday_extended('TSLA', 'year1month2', 'year1month1', '60min', True, False)
# api.get_intraday_extended('TSLA', 'all', 'year1month1', '1min', True, True)
# df = pd.read_csv("data/TSLA_2021-12-21_2022-01-20_1min.csv")

# df = pd.read_csv("data/AAPL_2020-03-01_2022-01-20_60min.csv")

# globals
training_period = 2

#backtesting
backtest = engine.backtest(df) #IMPORTANT

'''Algorithm function, lookback is a data frame parsed to function continuously until end of initial dataframe is reached.'''
def logic(account, lookback):
    try:
        today = len(lookback)-1
        if(today > training_period): 
            price_moving_average = lookback['close'].rolling(window=training_period).mean()[today]  # update PMA
            volumn_moving_average = lookback['volume'].rolling(window=training_period).mean()[today]  # update VMA

            if(lookback['close'][today] < price_moving_average):
                if(lookback['volume'][today] > volumn_moving_average):
                    if(account.buying_power > 0):
                        account.enter_position('long', account.buying_power, lookback['close'][today])
            else:
                if(lookback['close'][today] > price_moving_average):
                    if(lookback['volume'][today] < volumn_moving_average):
                        for position in account.positions:
                                account.close_position(position, 1, lookback['close'][today]) 
    except Exception as e:
        print(e)
        pass  # Handles lookback errors in beginning of dataset

list_of_coins = ["USDT_DOGE","USDT_BTC","USDT_ETH","USDT_LTC","USDT_XRP"]

lock = mp.Lock()
def backtest_stock(results,stock,logic):
    df = pd.read_csv("data/" + stock + ".csv", parse_dates=[0])
    backtest = engine.backtest(df)
    backtest.start(1000, logic)
    lock.acquire()
    data = backtest.results()
    data.extend([stock]) #coinname
    results.append(data)
    lock.release()

def wait_process_done(f, wait_time=0.001):
    # Monitor the status of another process 
    if not f.is_alive():
        time.sleep(1)
    print('foo is done.')

# if __name__ == '__main__':
#     p = Process(target=foo, args=('foo',))
#     p.start()
#     wait_process_done(p)

if __name__ == "__main__":

    # backtest.start(100, logic)
    # backtest.results()
    # backtest.chart()
    # backtest.plotlyplotting()
    # plotlyplotting.chart()
    manager = mp.Manager()
    results = manager.list()
    processes = []
    starttime = time.time()
    for coin in list_of_coins:
        p = mp.Process(target=backtest_stock, args=(results,coin,logic))
        processes.append(p)
        p.start()
    for process in processes:
        processes.remove(process)
        process.join()
        

    df = pd.DataFrame(list(results),columns=["Buy and Hold","Strategy","Longs","Sells","Shorts","Covers","Stdev_Strategy","Stdev_Hold","Coin"])
    df.to_csv("resultsbugtest.csv",index =False)
    print('That took {} seconds'.format(time.time() - starttime))