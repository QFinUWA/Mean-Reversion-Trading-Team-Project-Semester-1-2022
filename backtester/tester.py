import pandas as pd
from backtester import engine
import multiprocessing as mp
import time
from functools import partial

# Function used to backtest each stock
# Parameters: stock - the name of the stock data csv to be tested
#             logic - the logic function to be used
def backtest_stock(stock, logic):
    lock = mp.Lock() # Lock used to prevent errors with multiprocessing
    df = pd.read_csv("data/" + stock, parse_dates=[0]) # Read the csv file into a dataframe to be tested
    backtest = engine.backtest(df) # Create a backtest object with the data from the csv
    backtest.start(1000, logic) # Start the backtest with the provided logic function
    lock.acquire()
    data = backtest.results() # Get the results of the backtest
    data.extend([stock]) # Add the stock name to the results for easy comparison
    lock.release()
    return data # Return the results

# Function used to test an array of stocks
# Parameters: arr - the array of stock data csv's to be tested
#             logic - the logic function to be used
#             cores - the number of cores to be used
def testArr(arr, logic, cores):
    pool = mp.Pool(cores) # Create a multiprocessing pool with the specified number of cores
    stocktest = partial(backtest_stock, logic=logic) # Create a partial function to be used in the pool
    results = pool.map(stocktest, iterable=arr) # Map the partial function to the pool, returning the results
    # print(results)
    return results # Return the results