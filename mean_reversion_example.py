import pandas as pd
import time
import multiprocessing as mp

# local imports
from backtester import engine, tester
from backtester import api_interface as api

ticker['TP'] = (ticker['Close'] + ticker['Low'] + ticker['High'])/3
ticker['std'] = ticker['TP'].rolling(20).std(ddof=0)
ticker['MA-TP'] = ticker['TP'].rolling(20).mean()
ticker['BOLU'] = ticker['MA-TP'] + 2*ticker['std']
ticker['BOLD'] = ticker['MA-TP'] - 2*ticker['std']

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

def preprocessData(list_of_stocks):
    list_of_stocks_processed = []
    for stock in list_of_stocks:
        df = pd.read_csv("data/" + stock + ".csv", parse_dates=[0])
        df['TP'] = (df['Close'] + df['Low'] + df['High'])/3 # Calculate Typical Price
        df['std'] = df['TP'].rolling(20).std(ddof=0) # Calculate Standard Deviation
        df['MA-TP'] = df['TP'].rolling(20).mean() # Calculate Moving Average of Typical Price
        df['BOLU'] = df['MA-TP'] + 2*df['std'] # Calculate Upper Bollinger Band
        df['BOLD'] = df['MA-TP'] - 2*df['std'] # Calculate Lower Bollinger Band
        df.to_csv("data/" + stock + "_Processed.csv", index=False) # Save to CSV
        list_of_stocks_processed.append(stock + "_Processed")
    return list_of_stocks_processed

if __name__ == "__main__":
    # list_of_stocks = ["TSLA_2020-03-01_2022-01-20_1min"] 
    list_of_stocks = ["TSLA_2021-12-21_2022-01-20_60min", "TSLA_2021-12-21_2022-01-20_60min", "TSLA_2021-12-21_2022-01-20_60min"] # List of stock data csv's to be tested, located in "data/" folder 
    preprocessData(list_of_stocks) # Preprocess the data
    starttime = time.time() # Start timer
    results = tester.testArr(list_of_stocks, logic) # Run backtest on list of stocks using the logic function

    print(results) # Print results
    df = pd.DataFrame(list(results),columns=["Buy and Hold","Strategy","Longs","Sells","Shorts","Covers","Stdev_Strategy","Stdev_Hold","Coin"]) # Create dataframe of results
    df.to_csv("resultsoftesting.csv",index =False) # Save results to csv
    # print('That took {} seconds'.format(time.time() - starttime)) # Print time taken to run backtest