import pandas as pd
import time
import multiprocessing as mp

# local imports
from backtester import engine, tester
from backtester import api_interface as api


def logic(account, lookback): # Logic function to be used for each time interval in backtest 
    training_period = 2
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


if __name__ == "__main__":
    list_of_stocks = ["TSLA_2020-03-01_2022-01-20_1min"] # List of stock data csv's to be tested, located in data/ folder
    cores = mp.cpu_count()-2 or 1 # Number of cores/processes to use for backtest, set to 2 less than your computer has, or 1 if you don't have enough cores, can be overwritten to use all cores (not recommended)
    starttime = time.time() # Start timer
    results = tester.testArr(list_of_stocks, logic, cores) # Run backtest

    print(results) # Print results
    df = pd.DataFrame(list(results),columns=["Buy and Hold","Strategy","Longs","Sells","Shorts","Covers","Stdev_Strategy","Stdev_Hold","Coin"]) # Create dataframe of results
    df.to_csv("resultsbugtest.csv",index =False) # Save results to csv
    print('That took {} seconds'.format(time.time() - starttime)) # Print time taken to run backtest