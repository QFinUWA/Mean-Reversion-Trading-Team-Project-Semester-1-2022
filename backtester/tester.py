from turtle import back
import pandas as pd
from backtester import engine
import multiprocessing as mp
import time
from functools import partial

# Function used to backtest each stock
# Parameters: stock - the name of the stock data csv to be tested
#             logic - the logic function to be used
def backtest_stock(results, stock, logic):
    lock = mp.Lock() # Lock used to prevent errors with multiprocessing
    df = pd.read_csv("data/" + stock + ".csv", parse_dates=[0]) # Read the csv file into a dataframe to be tested
    backtest = engine.backtest(df) # Create a backtest object with the data from the csv
    backtest.start(1000, logic) # Start the backtest with the provided logic function
    lock.acquire()
    data = backtest.results() # Get the results of the backtest
    data.extend([stock]) # Add the stock name to the results for easy comparison
    results.append(data) # Add the results to the list of results
    lock.release()
    return data # Return the results

# Function used to test an array of stocks
# Parameters: arr - the array of stock data csv's to be tested
#             logic - the logic function to be used

def testArr(arr, logic):
    manager = mp.Manager() # Create a multiprocessing manager
    results = manager.list() # Create a list to store the results
    processes = [] 
    for stock in arr: # For each stock in the array
        p = mp.Process(target=backtest_stock, args=(results, stock, logic)) # Create a process to backtest each stock
        processes.append(p) # Add the process to the list of processes
        p.start() # Start the process
    for process in processes: 
        process.join() # Wait for the process to finish
        processes.remove(process) # Remove the process from the list of processes

    return results # Return the results