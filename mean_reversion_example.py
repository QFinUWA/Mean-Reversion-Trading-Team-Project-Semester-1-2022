import pandas as pd
import time
import multiprocessing as mp

# local imports
from backtester import engine, tester
from backtester import API_Interface as api

training_period = 20 # 20 for demo
standard_deviations = 3.5 # 3.5 for demo

def logic(account, lookback): # Logic function to be used for each time interval in backtest 
    
    try:
        today = len(lookback)-1
        if(today > training_period):
            if(lookback['close'][today] < lookback['BOLD'][today]): # If current price is below lower Bollinger Band, enter a long position
                for position in account.positions: # Close all current positions
                    account.close_position(position, 1, lookback['close'][today])
                if(account.buying_power > 0):
                    account.enter_position('long', account.buying_power, lookback['close'][today]) # Enter a long position
            if(lookback['close'][today] > lookback['BOLU'][today]): # If today's price is above the upper Bollinger Band, enter a short position
                for position in account.positions: # Close all current positions
                    account.close_position(position, 1, lookback['close'][today])
                if(account.buying_power > 0):
                    account.enter_position('short', account.buying_power, lookback['close'][today]) # Enter a short position
    except Exception as e:
        print(e)
        pass  # Handles lookback errors in beginning of dataset

def preprocess_data(list_of_stocks):
    list_of_stocks_processed = []
    for stock in list_of_stocks:
        df = pd.read_csv("data/" + stock + ".csv", parse_dates=[0])
        df['TP'] = (df['close'] + df['low'] + df['high'])/3 # Calculate Typical Price
        df['std'] = df['close'].rolling(training_period).std(ddof=0) # Calculate Standard Deviation
        df['MA-TP'] = df['TP'].rolling(training_period).mean() # Calculate Moving Average of Typical Price
        df['BOLU'] = df['MA-TP'] + standard_deviations*df['std'] # Calculate Upper Bollinger Band
        df['BOLD'] = df['MA-TP'] - standard_deviations*df['std'] # Calculate Lower Bollinger Band
        df.to_csv("data/" + stock + "_Processed.csv", index=False) # Save to CSV
        list_of_stocks_processed.append(stock + "_Processed")
    return list_of_stocks_processed

if __name__ == "__main__":
    # list_of_stocks = ["TSLA_2020-03-01_2022-01-20_1min"] 
    list_of_stocks = ["TSLA_2020-03-09_2022-01-28_15min", "AAPL_2020-03-24_2022-02-12_15min"] # List of stock data csv's to be tested, located in "data/" folder 
    list_of_stocks_proccessed = preprocess_data(list_of_stocks) # Preprocess the data
    starttime = time.time() # Start timer
    results = tester.test_array(list_of_stocks_proccessed, logic, chart=True) # Run backtest on list of stocks using the logic function

    print("training period " + str(training_period))
    print("standard deviations " + str(standard_deviations))
    print(results) # Print results
    df = pd.DataFrame(list(results), columns=["Buy and Hold","Strategy","Longs","Sells","Shorts","Covers","Stdev_Strategy","Stdev_Hold","Coin"]) # Create dataframe of results
    df.to_csv("resultsoftesting.csv", index=False) # Save results to csv
    # print('That took {} seconds'.format(time.time() - starttime)) # Print time taken to run backtest